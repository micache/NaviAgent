from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from ..core.auth import authenticate_user
from ..models.models import Trip as TripModel
from ..schemas.models import CreateTripRequest, Trip

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
        .order(TripModel.id.key, desc=True)
        .execute()
    )
    rows = getattr(res, "data", []) or []
    return [Trip(**row) for row in rows]


@router.post("/", response_model=Trip)
def create_trip(
    request: CreateTripRequest,
    auth: Dict[str, Any] = Depends(authenticate_user),
) -> Trip:
    """Tạo trip mới (địa điểm đã đến)."""
    user_id = auth["user_id"]
    supabase = auth["supabase"]

    trip_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    # Convert address to dict if it's a string
    address_data = request.address
    if isinstance(address_data, str):
        try:
            import json

            address_data = json.loads(address_data)
        except:
            address_data = {"name": address_data}

    data = {
        TripModel.id.key: trip_id,
        TripModel.user_id.key: user_id,
        TripModel.address.key: address_data,  # Store as JSON/dict
        TripModel.start_date.key: request.start_date.isoformat() if request.start_date else now,
        TripModel.end_date.key: request.end_date.isoformat() if request.end_date else now,
        TripModel.status.key: request.status,
    }

    res = supabase.table(TripModel.__tablename__).insert(data).execute()
    rows = getattr(res, "data", []) or []
    if not rows:
        raise HTTPException(status_code=500, detail="Failed to create trip")

    return Trip(**rows[0])
