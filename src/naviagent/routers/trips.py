from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from ..core.auth import authenticate_user
from ..models.models import Trip as TripModel
from ..schemas.models import Trip

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("/", response_model=List[Trip])
def list_trips(auth: Dict[str, Any] = Depends(authenticate_user)) -> List[Trip]:
    user_id = auth["user_id"]
    supabase = auth["supabase"]

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
