"""
Base formatter interface for guidebook generation.

This module provides the abstract base class that all formatters must implement.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class BaseFormatter(ABC):
    """
    Abstract base class for guidebook formatters.

    All formatters (PDF, HTML, Markdown) must inherit from this class
    and implement the required methods.
    """

    def __init__(
        self,
        travel_plan: Dict[str, Any],
        output_dir: str = "guidebooks",
        language: str = "vi",
    ):
        """
        Initialize the formatter.

        Args:
            travel_plan: Dictionary containing travel plan data.
            output_dir: Directory to save output files.
            language: Language for content (vi or en).
        """
        self.travel_plan = travel_plan
        self.output_dir = Path(output_dir)
        self.language = language

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Extract common data
        self._extract_common_data()

    def _extract_common_data(self) -> None:
        """Extract commonly used data from travel plan."""
        self.request_summary = self.travel_plan.get("request_summary", {})
        self.itinerary = self.travel_plan.get("itinerary", {})
        self.budget = self.travel_plan.get("budget", {})
        self.advisory = self.travel_plan.get("advisory", {})
        self.souvenirs = self.travel_plan.get("souvenirs", [])
        self.logistics = self.travel_plan.get("logistics", {})
        self.accommodation = self.travel_plan.get("accommodation", {})
        self.generated_at = self.travel_plan.get("generated_at", "")
        self.version = self.travel_plan.get("version", "1.0")

        # Extract destination info with fallback from multiple sources
        # Priority: request_summary -> root level -> defaults
        self.destination = (
            self.request_summary.get("destination", "") 
            or self.travel_plan.get("destination", "")
        )
        
        # For trip_duration: check multiple field names and sources
        self.trip_duration = (
            self.request_summary.get("duration") 
            or self.request_summary.get("trip_duration")
            or self.travel_plan.get("trip_duration")
            or self.travel_plan.get("duration")
            or 0
        )
        
        # For num_travelers: check multiple field names
        self.num_travelers = (
            self.request_summary.get("travelers")
            or self.request_summary.get("num_travelers") 
            or self.travel_plan.get("num_travelers")
            or self.travel_plan.get("travelers")
            or 1
        )
        
        # For budget
        self.budget_amount = (
            self.request_summary.get("budget")
            or self.travel_plan.get("budget_amount")
            or self.travel_plan.get("budget")
            or 0
        )
        
        # Convert to int if they're strings
        try:
            self.trip_duration = int(self.trip_duration) if self.trip_duration else 0
        except (ValueError, TypeError):
            self.trip_duration = 0
            
        try:
            self.num_travelers = int(self.num_travelers) if self.num_travelers else 1
        except (ValueError, TypeError):
            self.num_travelers = 1
            
        try:
            self.budget_amount = float(self.budget_amount) if self.budget_amount else 0
        except (ValueError, TypeError):
            self.budget_amount = 0

    @abstractmethod
    def generate(self, output_path: Optional[str] = None) -> str:
        """
        Generate the formatted guidebook.

        Args:
            output_path: Optional custom output path.

        Returns:
            Path to the generated file.
        """

    @abstractmethod
    def get_default_filename(self) -> str:
        """
        Get the default filename for this format.

        Returns:
            Default filename string.
        """

    def get_output_path(self, output_path: Optional[str] = None) -> Path:
        """
        Get the full output path for the file.

        Args:
            output_path: Optional custom output path.

        Returns:
            Path object for output file.
        """
        if output_path:
            return Path(output_path)
        return self.output_dir / self.get_default_filename()

    def get_labels(self) -> Dict[str, str]:
        """
        Get localized labels based on language setting.

        Returns:
            Dictionary of label keys to localized strings.
        """
        labels = {
            "vi": {
                "title": "Cẩm Nang Du Lịch",
                "executive_summary": "Tóm Tắt Chuyến Đi",
                "itinerary": "Lịch Trình Chi Tiết",
                "day": "Ngày",
                "flights": "Thông Tin Chuyến Bay",
                "accommodation": "Thông Tin Lưu Trú",
                "budget": "Phân Bổ Ngân Sách",
                "advisory": "Tư Vấn & Cảnh Báo",
                "souvenirs": "Gợi Ý Quà Tặng",
                "appendix": "Phụ Lục",
                "destination": "Điểm đến",
                "duration": "Thời gian",
                "travelers": "Số người",
                "budget_label": "Ngân sách",
                "total_cost": "Tổng chi phí",
                "status": "Trạng thái",
                "recommendations": "Đề xuất",
                "warnings": "Lưu ý",
                "visa_info": "Thông tin Visa",
                "weather_info": "Thông tin Thời tiết",
                "safety_tips": "Mẹo An toàn",
                "sim_apps": "SIM & Ứng dụng",
                "price": "Giá",
                "where_to_buy": "Nơi mua",
                "time": "Thời gian",
                "location": "Địa điểm",
                "activity": "Hoạt động",
                "cost": "Chi phí",
                "notes": "Ghi chú",
                "generated_at": "Tạo lúc",
                "table_of_contents": "Mục Lục",
                "cover_page": "Trang Bìa",
                "flight_options": "Các Lựa Chọn Bay",
                "recommended": "Đề xuất",
                "booking_tips": "Mẹo Đặt Vé",
                "amenities": "Tiện nghi",
                "area": "Khu vực",
                "rating": "Đánh giá",
                "per_night": "mỗi đêm",
                "category": "Danh mục",
                "estimated": "Ước tính",
                "breakdown": "Chi tiết",
                "selected_flight": "Chuyến Bay Đã Chọn",
                "selected_hotel": "Khách Sạn Đã Chọn",
                "emergency_contacts": "Liên Hệ Khẩn Cấp",
                "packing_list": "Danh Sách Đóng Gói",
            },
            "en": {
                "title": "Travel Guidebook",
                "executive_summary": "Trip Summary",
                "itinerary": "Detailed Itinerary",
                "day": "Day",
                "flights": "Flight Information",
                "accommodation": "Accommodation",
                "budget": "Budget Breakdown",
                "advisory": "Advisory & Warnings",
                "souvenirs": "Souvenir Suggestions",
                "appendix": "Appendix",
                "destination": "Destination",
                "duration": "Duration",
                "travelers": "Travelers",
                "budget_label": "Budget",
                "total_cost": "Total Cost",
                "status": "Status",
                "recommendations": "Recommendations",
                "warnings": "Warnings",
                "visa_info": "Visa Information",
                "weather_info": "Weather Information",
                "safety_tips": "Safety Tips",
                "sim_apps": "SIM & Apps",
                "price": "Price",
                "where_to_buy": "Where to Buy",
                "time": "Time",
                "location": "Location",
                "activity": "Activity",
                "cost": "Cost",
                "notes": "Notes",
                "generated_at": "Generated at",
                "table_of_contents": "Table of Contents",
                "cover_page": "Cover Page",
                "flight_options": "Flight Options",
                "recommended": "Recommended",
                "booking_tips": "Booking Tips",
                "amenities": "Amenities",
                "area": "Area",
                "rating": "Rating",
                "per_night": "per night",
                "category": "Category",
                "estimated": "Estimated",
                "breakdown": "Breakdown",
                "selected_flight": "Selected Flight",
                "selected_hotel": "Selected Hotel",
                "emergency_contacts": "Emergency Contacts",
                "packing_list": "Packing List",
            },
        }
        return labels.get(self.language, labels["vi"])
