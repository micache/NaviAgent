from __future__ import annotations

"""
Auth router: register, login, logout using Supabase auth.
"""

import os
import re
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from ..core.auth import authenticate_user
from ..core.database import get_supabase, get_supabase_service
from ..models.models import User
from ..schemas.models import LoginRequest, LogoutResponse, RegisterRequest, UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])


# localhost:8000/auth/register
@router.post("/register", response_model=UserProfile)
def register(payload: RegisterRequest) -> UserProfile:
    supabase = get_supabase()

    # 1) Create auth user
    try:
        redirect_url = os.getenv("EMAIL_REDIRECT_TO", "http://localhost:3000")
        auth_res = supabase.auth.sign_up(
            {
                "email": payload.email,
                "password": payload.password,
                "options": {"email_redirect_to": redirect_url},
            }
        )
        auth_user = getattr(auth_res, "user", None) or getattr(auth_res, "data", None)
        if not auth_user:
            raise HTTPException(status_code=400, detail="Failed to create auth user")
        user_id = auth_user["id"] if isinstance(auth_user, dict) else auth_user.id
    except Exception as exc:
        msg = str(exc)
        # Handle Supabase GoTrue throttle for sign up requests
        if "For security purposes" in msg:
            # Try to extract remaining seconds for Retry-After header
            m = re.search(r"(\d+)\s*seconds?", msg)
            retry_after = m.group(1) if m else "30"
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many sign up attempts. Please wait and retry.",
                headers={"Retry-After": retry_after},
            )
        # Common duplicate/exists cases
        if "already registered" in msg or "duplicate" in msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )
        raise HTTPException(status_code=400, detail=f"Auth sign up failed: {exc}")

    # 2) Insert profile into public.users table (id from auth.users)
    try:
        insert_data = {
            "user_id": user_id,
            "full_name": payload.full_name,
            "date_of_birth": payload.date_of_birth.isoformat() if payload.date_of_birth else None,
            "average_budget": payload.average_budget,
        }
        # Filter None values to avoid overriding defaults
        insert_data = {k: v for k, v in insert_data.items() if v is not None}
        # Use service-role key to bypass RLS for initial profile creation
        srv = get_supabase_service()
        # Use upsert to avoid duplicate errors if profile already exists
        data = (
            srv.table(User.__tablename__)
            .upsert(insert_data, on_conflict=User.user_id.key)
            .execute()
        )
        row = (data.data or [None])[0]
        return UserProfile(**row)
    except Exception as exc:
        # Best-effort cleanup: if profile creation fails, consider deleting the auth user
        raise HTTPException(status_code=400, detail=f"Create user profile failed: {exc}")


# localhost:8000/auth/login
@router.post("/login")
def login(payload: LoginRequest) -> Dict[str, Any]:
    supabase = get_supabase()
    try:
        res = supabase.auth.sign_in_with_password(
            {
                "email": payload.email,
                "password": payload.password,
            }
        )
        # supabase-py returns session and user
        session = getattr(res, "session", None) or getattr(res, "data", None)
        user = getattr(res, "user", None)
        if hasattr(session, "access_token"):
            access_token = session.access_token
        elif isinstance(session, dict):
            access_token = session.get("access_token")
        else:
            access_token = None
        if not access_token:
            raise HTTPException(status_code=400, detail="Invalid login response")
        return {
            "access_token": access_token,
            "expires_in": session.expires_in if session else None,
            "refresh_token": session.refresh_token if session else None,
            "token_type": "bearer",
            "user": getattr(user, "__dict__", user),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Login failed: {exc}")


@router.post("/logout", response_model=LogoutResponse)
def logout(auth: Dict[str, Any] = Depends(authenticate_user)) -> LogoutResponse:  # noqa: ARG001
    supabase = auth["supabase"]
    try:
        supabase.auth.sign_out()
        return LogoutResponse(success=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Logout failed: {exc}")
