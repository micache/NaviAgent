
from __future__ import annotations

from typing import Any, Dict, Optional
import os
import httpx

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(HTTPBearer(auto_error=False)),
) -> Dict[str, Any]:
    
    SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    """Validate bearer token with Supabase GoTrue and return the user dict."""
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="Supabase env not configured")

    token = credentials.credentials
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": SUPABASE_ANON_KEY,
                },
            )
        if resp.status_code != 200:
            # 401/403 từ Supabase → token không hợp lệ/hết hạn
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        user = resp.json()  # trả về object user có field "id"
        user["_access_token"] = token  # thêm token để dùng cho RLS
        return user
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Auth error: {exc}")