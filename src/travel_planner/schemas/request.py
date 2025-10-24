"""
Request schemas for Travel Planner API
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class TravelStyle(str, Enum):
    """Travel style enum"""
    TOUR = "tour"
    SELF_GUIDED = "self_guided"


class TravelRequest(BaseModel):
    """Schema for travel planning request"""
    
    departure_point: str = Field(
        ...,
        description="Điểm khởi hành (tên thành phố hoặc sân bay)",
        min_length=1
    )
    
    destination: str = Field(
        ...,
        description="Điểm đến chính (tên thành phố hoặc quốc gia)",
        min_length=1
    )
    
    budget: float = Field(
        ...,
        description="Ngân sách dự kiến (VNĐ hoặc USD)",
        gt=0
    )
    
    num_travelers: int = Field(
        ...,
        description="Số lượng người đi",
        gt=0
    )
    
    trip_duration: int = Field(
        ...,
        description="Số ngày du lịch",
        gt=0
    )
    
    travel_style: TravelStyle = Field(
        ...,
        description="Phong cách du lịch: tour hoặc tự túc"
    )
    
    customer_notes: Optional[str] = Field(
        None,
        description="Ghi chú từ khách hàng (sở thích, yêu cầu đặc biệt, ...)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "departure_point": "Hanoi",
                "destination": "Tokyo, Japan",
                "budget": 50000000,
                "num_travelers": 2,
                "trip_duration": 7,
                "travel_style": "self_guided",
                "customer_notes": "Thích ẩm thực đường phố, muốn tham quan đền chùa và mua sắm"
            }
        }
