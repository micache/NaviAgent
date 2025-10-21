from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from ..core.auth import get_current_user
from ..core.database import get_supabase_authed
from ..models.models import User
from ..schemas.models import UserProfile


router = APIRouter(prefix="/users", tags=["users"])

# localhost:8000/users/me
@router.get("/me", response_model=UserProfile)
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)) -> UserProfile:
    token = current_user.get("_access_token")
    supabase = get_supabase_authed(token)

    user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user in token")

    # Query an toàn khi 0 rows (tránh .single() gây PGRST116)
    query = supabase.table(User.__tablename__).select("*").eq(User.user_id.key, user_id)

    # Nếu postgrest có maybe_single() thì dùng, không thì đọc list
    if hasattr(query, "maybe_single"):
        res = query.maybe_single().execute()
        row = getattr(res, "data", None)
    else:
        res = query.execute()
        data = getattr(res, "data", None)
        row = data[0] if isinstance(data, list) and data else None

    if not row:
        # Chưa có profile → trả về object tối thiểu thay vì lỗi 500
        return UserProfile(user_id=user_id)

    return UserProfile(**row)