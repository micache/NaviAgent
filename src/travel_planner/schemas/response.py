"""
Response schemas for Travel Planner API
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Activity(BaseModel):
    """Schema cho một hoạt động trong lịch trình"""

    time: str = Field(..., description="Thời gian (ví dụ: '08:00 - 10:00')")
    location_name: str = Field(..., description="Tên địa điểm")
    address: Optional[str] = Field(None, description="Địa chỉ cụ thể")
    activity_type: str = Field(
        ..., description="Loại hoạt động (tham quan, ăn uống, mua sắm, di chuyển, ...)"
    )
    description: str = Field(..., description="Mô tả chi tiết hoạt động")
    estimated_cost: Optional[float] = Field(None, description="Chi phí ước tính (nếu có)")
    notes: Optional[str] = Field(None, description="Ghi chú vận hành")


class DaySchedule(BaseModel):
    """Schema cho lịch trình một ngày"""

    day_number: int = Field(..., description="Ngày thứ mấy trong chuyến đi")
    date: Optional[str] = Field(None, description="Ngày tháng (nếu có)")
    title: str = Field(..., description="Tiêu đề của ngày (ví dụ: 'Khám phá Tokyo')")
    activities: List[Activity] = Field(..., description="Danh sách hoạt động trong ngày")


class ItineraryTimeline(BaseModel):
    """Schema cho lịch trình chi tiết"""

    daily_schedules: List[DaySchedule] = Field(..., description="Lịch trình theo từng ngày")
    location_list: List[str] = Field(..., description="Danh sách tên các địa điểm chính")
    summary: Optional[str] = Field(None, description="Tóm tắt lịch trình")


class BudgetCategory(BaseModel):
    """Schema cho một danh mục chi phí"""

    category_name: str = Field(
        ..., description="Tên danh mục (Accommodation, Food, Transport, ...)"
    )
    estimated_cost: float = Field(..., description="Chi phí ước tính")
    breakdown: Optional[List[Dict[str, float]]] = Field(None, description="Chi tiết phân bổ")
    notes: Optional[str] = Field(None, description="Ghi chú về danh mục")


class BudgetBreakdown(BaseModel):
    """Schema cho chi phí dự tính"""

    categories: List[BudgetCategory] = Field(..., description="Danh sách các danh mục chi phí")
    total_estimated_cost: float = Field(..., description="Tổng chi phí ước tính")
    budget_status: str = Field(..., description="Trạng thái ngân sách (trong/vượt/dưới ngân sách)")
    recommendations: Optional[List[str]] = Field(None, description="Gợi ý tiết kiệm/điều chỉnh")


class LocationDescription(BaseModel):
    """Schema cho mô tả địa điểm"""

    location_name: str = Field(..., description="Tên địa điểm")
    description: str = Field(..., description="Mô tả ngắn gọn (2-3 câu)")
    highlights: Optional[List[str]] = Field(None, description="Điểm nổi bật")


class AdvisoryInfo(BaseModel):
    """Schema cho thông tin tư vấn và cảnh báo"""

    warnings_and_tips: List[str] = Field(..., description="Danh sách cảnh báo và lưu ý quan trọng")
    location_descriptions: List[LocationDescription] = Field(..., description="Mô tả các địa điểm")
    visa_info: Optional[str] = Field(None, description="Thông tin Visa")
    weather_info: Optional[str] = Field(None, description="Thông tin thời tiết")
    sim_and_apps: Optional[List[str]] = Field(None, description="Gợi ý SIM và ứng dụng")
    safety_tips: Optional[List[str]] = Field(None, description="Mẹo an toàn")


class SouvenirSuggestion(BaseModel):
    """Schema cho gợi ý quà tặng"""

    item_name: str = Field(..., description="Tên món quà")
    description: str = Field(..., description="Mô tả món quà")
    estimated_price: Optional[str] = Field(None, description="Giá ước tính")
    where_to_buy: Optional[str] = Field(None, description="Địa điểm mua")


class LogisticsInfo(BaseModel):
    """Schema cho thông tin hậu cần"""

    flight_info: Optional[str] = Field(None, description="Thông tin về vé máy bay")
    estimated_flight_cost: Optional[float] = Field(None, description="Chi phí vé máy bay ước tính")
    accommodation_suggestions: Optional[List[str]] = Field(
        None, description="Gợi ý khu vực đặt khách sạn"
    )
    transportation_tips: Optional[List[str]] = Field(None, description="Gợi ý di chuyển")


class TravelPlan(BaseModel):
    """Schema chính cho kế hoạch du lịch hoàn chỉnh"""

    version: str = Field(default="1.0", description="Phiên bản kế hoạch")

    # Thông tin tổng quan
    request_summary: Dict = Field(..., description="Tóm tắt yêu cầu gốc")

    # Output từ các agent
    itinerary: ItineraryTimeline = Field(..., description="Lịch trình chi tiết")
    budget: BudgetBreakdown = Field(..., description="Chi phí dự tính")
    advisory: AdvisoryInfo = Field(..., description="Tư vấn và cảnh báo")
    souvenirs: List[SouvenirSuggestion] = Field(..., description="Gợi ý quà tặng")
    logistics: LogisticsInfo = Field(..., description="Thông tin hậu cần")

    # Metadata
    generated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Thời gian tạo",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "version": "1.0",
                "request_summary": {
                    "destination": "Tokyo, Japan",
                    "duration": 7,
                    "budget": 50000000,
                    "travelers": 2,
                },
                "itinerary": {
                    "daily_schedules": [],
                    "location_list": [
                        "Senso-ji Temple",
                        "Tokyo Tower",
                        "Shibuya Crossing",
                    ],
                    "summary": "Một tuần khám phá Tokyo với sự kết hợp giữa văn hóa và hiện đại",
                },
                "budget": {
                    "categories": [],
                    "total_estimated_cost": 48000000,
                    "budget_status": "Trong ngân sách",
                },
                "advisory": {
                    "warnings_and_tips": ["Nên mua JR Pass trước khi đi"],
                    "location_descriptions": [],
                },
                "souvenirs": [],
                "logistics": {"estimated_flight_cost": 15000000},
                "generated_at": "2025-10-24T00:00:00",
            }
        }
