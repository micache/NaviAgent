"""
Request schemas for Travel Planner API
"""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TravelStyle(str, Enum):
    """Travel style enum"""

    TOUR = "tour"
    SELF_GUIDED = "self_guided"


class TravelRequest(BaseModel):
    """Schema for travel planning request with database support"""

    departure_point: str = Field(
        ..., description="Điểm khởi hành (tên thành phố hoặc sân bay)", min_length=1
    )

    destination: str = Field(
        ..., description="Điểm đến chính (tên thành phố hoặc quốc gia)", min_length=1
    )

    departure_date: date = Field(..., description="Ngày khởi hành (YYYY-MM-DD)")

    budget: float = Field(..., description="Ngân sách dự kiến (VNĐ hoặc USD)", gt=0)

    num_travelers: int = Field(..., description="Số lượng người đi", gt=0)

    trip_duration: int = Field(..., description="Số ngày du lịch", gt=0)

    travel_style: TravelStyle = Field(
        ..., description="Phong cách du lịch: tour hoặc tự túc"
    )

    customer_notes: Optional[str] = Field(
        None, description="Ghi chú từ khách hàng (sở thích, yêu cầu đặc biệt, ...)"
    )

    user_id: Optional[str] = Field(
        None,
        description="User ID for session tracking and memory management (optional)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "departure_point": "Hanoi",
                "destination": "Tokyo, Japan",
                "departure_date": "2025-12-15",
                "budget": 50000000,
                "num_travelers": 2,
                "trip_duration": 7,
                "travel_style": "self_guided",
                "customer_notes": "Thích ẩm thực đường phố, muốn tham quan đền chùa và mua sắm",
                "user_id": "user_12345",
            }
        }
