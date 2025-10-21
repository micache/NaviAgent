from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from ..core.auth import get_current_user
from ..core.database import get_supabase_authed
from ..models.models import Trip as TripModel
from ..schemas.models import Trip


router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("/", response_model=List[Trip])
def list_trips(current_user: Dict[str, Any] = Depends(get_current_user)) -> List[Trip]:
    token = current_user.get("_access_token")
    supabase = get_supabase_authed(token)
    user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user in token")

    res = (
        supabase.table(TripModel.__tablename__)
        .select("*")
        .eq(TripModel.user_id.key, user_id)
        .order(TripModel.start_date.key, desc=True)
        .order(TripModel.trip_id.key, desc=True)
        .execute()
    )
    rows = getattr(res, "data", []) or []
    return [Trip(**row) for row in rows]
