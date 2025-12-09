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
    estimated_cost: Optional[float] = Field(
        None, description="Chi phí ước tính (nếu có)"
    )
    notes: Optional[str] = Field(None, description="Ghi chú vận hành")


class DaySchedule(BaseModel):
    """Schema cho lịch trình một ngày"""

    day_number: int = Field(..., description="Ngày thứ mấy trong chuyến đi")
    date: Optional[str] = Field(None, description="Ngày tháng (nếu có)")
    title: str = Field(..., description="Tiêu đề của ngày (ví dụ: 'Khám phá Tokyo')")
    activities: List[Activity] = Field(
        ..., description="Danh sách hoạt động trong ngày"
    )


class SelectedFlightInfo(BaseModel):
    """Schema cho thông tin chuyến bay đã chọn trong lịch trình"""

    airline: str = Field(..., description="Hãng hàng không đã chọn")
    outbound_flight: str = Field(
        ..., description="Chuyến đi (e.g., 'VN404 - 08:00 AM')"
    )
    return_flight: str = Field(..., description="Chuyến về (e.g., 'VN405 - 14:00 PM')")
    total_cost: float = Field(
        ..., description="Tổng chi phí cho tất cả hành khách (VND)"
    )


class SelectedAccommodationInfo(BaseModel):
    """Schema cho thông tin khách sạn đã chọn trong lịch trình"""

    name: str = Field(..., description="Tên khách sạn đã chọn")
    area: str = Field(..., description="Khu vực")
    check_in: str = Field(..., description="Ngày check-in")
    check_out: str = Field(..., description="Ngày check-out")
    total_cost: float = Field(..., description="Tổng chi phí lưu trú (VND)")


class ItineraryTimeline(BaseModel):
    """Schema cho lịch trình chi tiết"""

    daily_schedules: List[DaySchedule] = Field(
        ..., description="Lịch trình theo từng ngày"
    )
    location_list: List[str] = Field(
        ..., description="Danh sách tên các địa điểm chính"
    )
    summary: Optional[str] = Field(None, description="Tóm tắt lịch trình")
    selected_flight: Optional[SelectedFlightInfo] = Field(
        None, description="Thông tin chuyến bay đã chọn cho chuyến đi"
    )
    selected_accommodation: Optional[SelectedAccommodationInfo] = Field(
        None, description="Thông tin khách sạn đã chọn cho chuyến đi"
    )


class BudgetCategory(BaseModel):
    """Schema cho một danh mục chi phí"""

    category_name: str = Field(
        ..., description="Tên danh mục (Accommodation, Food, Transport, ...)"
    )
    estimated_cost: float = Field(..., description="Chi phí ước tính")
    breakdown: Optional[List[Dict[str, float]]] = Field(
        None, description="Chi tiết phân bổ"
    )
    notes: Optional[str] = Field(None, description="Ghi chú về danh mục")


class BudgetBreakdown(BaseModel):
    """Schema cho chi phí dự tính"""

    categories: List[BudgetCategory] = Field(
        ..., description="Danh sách các danh mục chi phí"
    )
    total_estimated_cost: float = Field(..., description="Tổng chi phí ước tính")
    budget_status: str = Field(
        ..., description="Trạng thái ngân sách (trong/vượt/dưới ngân sách)"
    )
    recommendations: Optional[List[str]] = Field(
        None, description="Gợi ý tiết kiệm/điều chỉnh"
    )


class LocationDescription(BaseModel):
    """Schema cho mô tả địa điểm"""

    location_name: str = Field(..., description="Tên địa điểm")
    description: str = Field(..., description="Mô tả ngắn gọn (2-3 câu)")
    highlights: Optional[List[str]] = Field(None, description="Điểm nổi bật")


class AdvisoryInfo(BaseModel):
    """Schema cho thông tin tư vấn và cảnh báo"""

    warnings_and_tips: List[str] = Field(
        ..., description="Danh sách cảnh báo và lưu ý quan trọng"
    )
    location_descriptions: List[LocationDescription] = Field(
        ..., description="Mô tả các địa điểm"
    )
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


class FlightOption(BaseModel):
    """Schema cho thông tin chuyến bay"""

    airline: str = Field(..., description="Tên hãng hàng không")
    flight_type: str = Field(..., description="Loại bay: direct, one-stop, multi-stop")
    departure_time: str = Field(..., description="Giờ khởi hành")
    arrival_time: Optional[str] = Field(None, description="Giờ đến (nếu có)")
    duration: str = Field(..., description="Thời gian bay")
    price_per_person: float = Field(..., description="Giá vé/người (khứ hồi, VND)")
    cabin_class: str = Field(
        ..., description="Hạng ghế: Economy, Business, First Class"
    )
    benefits: List[str] = Field(
        ..., description="Quyền lợi kèm vé (hành lý, bữa ăn, ...)"
    )
    booking_platforms: List[str] = Field(..., description="Nền tảng đặt vé")
    notes: Optional[str] = Field(None, description="Ghi chú thêm")


class LogisticsInfo(BaseModel):
    """Schema cho thông tin vé máy bay"""

    flight_options: List[FlightOption] = Field(
        ..., description="Danh sách các lựa chọn chuyến bay"
    )
    recommended_flight: Optional[str] = Field(
        None, description="Chuyến bay được đề xuất"
    )
    average_price: float = Field(..., description="Giá trung bình/người (VND)")
    booking_tips: List[str] = Field(..., description="Mẹo đặt vé máy bay")
    visa_requirements: Optional[str] = Field(None, description="Yêu cầu visa")


class AccommodationOption(BaseModel):
    """Schema cho thông tin khách sạn/lưu trú"""

    name: str = Field(..., description="Tên khách sạn/hostel/homestay")
    type: str = Field(
        ..., description="Loại hình (hotel, hostel, homestay, apartment, ...)"
    )
    area: str = Field(..., description="Khu vực/quận")
    price_per_night: float = Field(..., description="Giá trung bình mỗi đêm (VND)")
    rating: Optional[float] = Field(None, description="Điểm đánh giá (nếu có)")
    amenities: List[str] = Field(..., description="Tiện nghi (WiFi, Pool, Gym, ...)")
    distance_to_center: Optional[str] = Field(
        None, description="Khoảng cách đến trung tâm"
    )
    booking_platforms: List[str] = Field(
        ..., description="Nền tảng đặt phòng (Booking.com, Agoda, ...)"
    )
    notes: Optional[str] = Field(None, description="Ghi chú thêm")


class AccommodationInfo(BaseModel):
    """Schema cho thông tin khách sạn và lưu trú"""

    recommendations: List[AccommodationOption] = Field(
        ..., description="Danh sách đề xuất khách sạn/lưu trú"
    )
    best_areas: List[str] = Field(..., description="Top khu vực nên ở")
    average_price_per_night: float = Field(
        ..., description="Giá trung bình mỗi đêm cho các khách sạn đề xuất (VND)"
    )
    booking_tips: List[str] = Field(..., description="Mẹo đặt phòng")
    total_estimated_cost: float = Field(
        ..., description="Tổng chi phí lưu trú ước tính cho toàn bộ chuyến đi (VND)"
    )


class TravelPlan(BaseModel):
    """Schema chính cho kế hoạch du lịch hoàn chỉnh (Legacy - for individual agents)"""

    version: str = Field(default="1.0", description="Phiên bản kế hoạch")

    # Thông tin tổng quan
    request_summary: Optional[Dict] = Field(None, description="Tóm tắt yêu cầu gốc")

    # Output từ các agent (all optional for backward compatibility with Team mode)
    itinerary: Optional[ItineraryTimeline] = Field(
        None, description="Lịch trình chi tiết"
    )
    budget: Optional[BudgetBreakdown] = Field(None, description="Chi phí dự tính")
    advisory: Optional[AdvisoryInfo] = Field(None, description="Tư vấn và cảnh báo")
    souvenirs: Optional[List[SouvenirSuggestion]] = Field(
        None, description="Gợi ý quà tặng"
    )
    logistics: Optional[LogisticsInfo] = Field(None, description="Thông tin hậu cần")
    accommodation: Optional[AccommodationInfo] = Field(
        None, description="Thông tin khách sạn và lưu trú chi tiết"
    )

    # Metadata
    generated_at: Optional[str] = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Thời gian tạo",
    )

    # Team response (if using Agno Team)
    team_full_response: Optional[str] = Field(
        None,
        description="Full synthesized response from Travel Planning Team (when using Team mode)",
    )


class TravelPlanTeamResponse(BaseModel):
    """Schema for Travel Plan generated by Agno Team (simplified)"""

    version: str = Field(default="2.0-team", description="Team-based version")

    # Request info
    destination: str = Field(..., description="Điểm đến")
    departure_point: str = Field(..., description="Điểm xuất phát")
    departure_date: str = Field(..., description="Ngày khởi hành")
    trip_duration: int = Field(..., description="Số ngày đi")
    budget: float = Field(..., description="Ngân sách (VND)")
    num_travelers: int = Field(..., description="Số người đi")
    travel_style: str = Field(..., description="Phong cách du lịch")

    # Team synthesized response
    team_response: str = Field(
        ...,
        description="Complete travel plan synthesized by Travel Planning Team with input from 7 specialist agents",
    )

    # Metadata
    generated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Thời gian tạo",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "version": "2.0-team",
                "destination": "Tokyo, Japan",
                "departure_point": "Hanoi",
                "departure_date": "2024-06-01",
                "trip_duration": 7,
                "budget": 50000000,
                "num_travelers": 2,
                "travel_style": "self_guided",
                "team_response": "# Complete Travel Plan\n\n## Weather Forecast\n...\n\n## Flight Options\n...",
                "generated_at": "2025-10-25T00:00:00",
            }
        }

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


class GuidebookOptions(BaseModel):
    """Schema for guidebook generation options."""

    include_maps: bool = Field(
        default=False, description="Include maps in guidebook (future)"
    )
    include_qr_codes: bool = Field(
        default=False, description="Include QR codes (future)"
    )
    language: str = Field(
        default="vi", description="Language for guidebook content (vi or en)"
    )
    template: str = Field(default="default", description="Template name (default)")


class GuidebookRequest(BaseModel):
    """Schema for guidebook generation request."""

    travel_plan: Optional[TravelPlan] = Field(
        None, description="TravelPlan object for guidebook generation"
    )
    travel_plan_path: Optional[str] = Field(
        None, description="Path to travel plan JSON file"
    )
    formats: List[str] = Field(
        default=["pdf", "html", "markdown"],
        description="List of formats to generate: pdf, html, markdown",
    )
    options: Optional[GuidebookOptions] = Field(
        default_factory=GuidebookOptions,
        description="Guidebook generation options",
    )


class GuidebookResponse(BaseModel):
    """Schema for guidebook generation response."""

    guidebook_id: str = Field(..., description="Unique identifier for this guidebook")
    files: Dict[str, str] = Field(
        ..., description="Dictionary mapping format names to file paths"
    )
    generated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Generation timestamp",
    )
    language: str = Field(default="vi", description="Language used")
    output_dir: str = Field(..., description="Output directory path")
