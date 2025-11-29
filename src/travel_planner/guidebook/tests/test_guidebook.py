"""Tests for the guidebook PDF generator."""

import os
import tempfile
from datetime import date
from pathlib import Path

import pytest

from travel_planner.guidebook.image_fetcher import ImageData, ImageFetcher


class TestImageFetcher:
    """Tests for the ImageFetcher class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.fetcher = ImageFetcher()

    def test_get_destination_hero(self):
        """Test hero image generation for a destination."""
        result = self.fetcher.get_destination_hero("Paris, France")

        assert isinstance(result, ImageData)
        assert result.mime_type == "image/svg+xml"
        assert result.is_base64 is True
        assert len(result.data) > 0
        assert result.caption == "Paris, France - Travel Guide"

    def test_get_destination_hero_vietnamese(self):
        """Test hero image generation with Vietnamese characters."""
        result = self.fetcher.get_destination_hero("Châu Âu, Pháp, Anh, Đức")

        assert isinstance(result, ImageData)
        assert result.mime_type == "image/svg+xml"
        assert len(result.data) > 0
        # Verify Vietnamese characters are in caption
        assert "Châu Âu" in result.caption

    def test_get_location_image(self):
        """Test location image generation."""
        result = self.fetcher.get_location_image("Eiffel Tower")

        assert isinstance(result, ImageData)
        assert result.mime_type == "image/svg+xml"
        assert result.is_base64 is True
        assert len(result.data) > 0

    def test_generate_route_map(self):
        """Test route map generation."""
        locations = ["Paris", "Lyon", "Marseille", "Nice"]
        result = self.fetcher.generate_route_map(locations, "France Tour")

        assert isinstance(result, ImageData)
        assert result.mime_type == "image/svg+xml"
        assert "France Tour" in result.caption

    def test_generate_route_map_empty_locations(self):
        """Test route map with empty locations list."""
        result = self.fetcher.generate_route_map([], "Empty Tour")

        assert isinstance(result, ImageData)
        assert result.mime_type == "image/svg+xml"

    def test_get_data_uri(self):
        """Test data URI generation."""
        image = self.fetcher.get_destination_hero("Test")
        uri = self.fetcher.get_data_uri(image)

        assert uri.startswith("data:image/svg+xml;base64,")

    def test_html_escape(self):
        """Test HTML escaping in SVG generation."""
        # Test with potentially dangerous characters
        result = self.fetcher.get_destination_hero("<script>alert('xss')</script>")

        assert isinstance(result, ImageData)
        # The SVG should be generated without errors
        assert len(result.data) > 0


class TestEnhancedPDFFormatter:
    """Tests for the EnhancedPDFFormatter class."""

    @pytest.fixture
    def sample_travel_data(self):
        """Create sample travel plan data for testing."""
        return {
            "destination": "Châu Âu, Pháp, Anh, Đức",
            "departure_point": "Hanoi",
            "departure_date": date(2024, 6, 1),
            "trip_duration": 7,
            "num_travelers": 4,
            "travel_style": "self_guided",
            "customer_notes": "Thích quẩy, thích bar, thích ăn chơi nhảy múa",
            "weather": {
                "forecast": [
                    {"date": "June 1", "temperature": 22, "condition": "Sunny"},
                    {"date": "June 2", "temperature": 20, "condition": "Cloudy"},
                    {"date": "June 3", "temperature": 18, "condition": "Rain"},
                ],
                "seasonal_events": "Summer festivals in Paris",
                "packing_suggestions": [
                    "Light jacket",
                    "Comfortable walking shoes",
                    "Umbrella",
                ],
            },
            "logistics": {
                "flights": [
                    {
                        "airline": "Vietnam Airlines",
                        "departure_airport": "HAN",
                        "arrival_airport": "CDG",
                        "departure_city": "Hanoi",
                        "arrival_city": "Paris",
                        "departure_time": "10:00",
                        "arrival_time": "18:00",
                        "price": "15,000,000 VND",
                    }
                ],
                "local_transport": [
                    {"type": "Metro", "description": "Paris Metro system", "cost": "1.90€"},
                    {
                        "type": "Eurostar",
                        "description": "High-speed train to London",
                        "cost": "89€",
                    },
                ],
            },
            "accommodation": {
                "hotels": [
                    {
                        "name": "Hotel Le Marais",
                        "stars": 4,
                        "location": "Paris 4th Arr.",
                        "amenities": ["WiFi", "Breakfast", "Gym"],
                        "price": "2,500,000 VND/night",
                    }
                ],
                "tips": "Book early for better rates",
            },
            "itinerary": {
                "days": [
                    {
                        "day_number": 1,
                        "title": "Arrival in Paris",
                        "date": "June 1, 2024",
                        "activities": [
                            {
                                "time": "18:00",
                                "time_of_day": "evening",
                                "name": "Check-in at hotel",
                                "description": "Settle in and rest",
                            },
                            {
                                "time": "20:00",
                                "time_of_day": "evening",
                                "name": "Welcome dinner",
                                "description": "French cuisine at local bistro",
                                "cost": "50€",
                            },
                        ],
                    },
                    {
                        "day_number": 2,
                        "title": "Exploring Paris",
                        "date": "June 2, 2024",
                        "activities": [
                            {
                                "time": "09:00",
                                "time_of_day": "morning",
                                "name": "Eiffel Tower",
                                "description": "Visit the iconic tower",
                                "cost": "26€",
                                "tips": "Book tickets online to skip the queue",
                            },
                            {
                                "time": "14:00",
                                "time_of_day": "afternoon",
                                "name": "Louvre Museum",
                                "description": "World's largest art museum",
                                "cost": "17€",
                            },
                        ],
                        "meals": [
                            {
                                "type": "lunch",
                                "restaurant": "Café de Flore",
                                "cuisine": "French",
                            }
                        ],
                    },
                ],
            },
            "budget": {
                "total": "50,000,000 VND",
                "currency": "VND",
                "breakdown": [
                    {"category": "Flights", "amount": "15,000,000 VND"},
                    {"category": "Accommodation", "amount": "17,500,000 VND"},
                    {"category": "Food", "amount": "7,000,000 VND"},
                    {"category": "Activities", "amount": "5,000,000 VND"},
                    {"category": "Transport", "amount": "3,000,000 VND"},
                    {"category": "Shopping", "amount": "2,500,000 VND"},
                ],
                "saving_tips": [
                    "Use metro instead of taxis",
                    "Book attractions in advance",
                    "Eat at local markets",
                ],
            },
            "souvenirs": {
                "recommendations": [
                    {
                        "name": "French Wine",
                        "icon": "🍷",
                        "price": "20-100€",
                        "description": "Bordeaux or Burgundy",
                    },
                    {
                        "name": "Macarons",
                        "icon": "🍪",
                        "price": "15-30€",
                        "description": "From Ladurée",
                    },
                    {
                        "name": "Perfume",
                        "icon": "💐",
                        "price": "50-200€",
                        "description": "French perfume brands",
                    },
                ],
                "shopping_areas": [
                    {
                        "name": "Champs-Élysées",
                        "description": "Luxury shopping avenue",
                        "best_for": "Designer brands",
                    },
                    {
                        "name": "Le Marais",
                        "description": "Trendy boutiques",
                        "best_for": "Unique finds",
                    },
                ],
            },
            "advisory": {
                "visa": "Schengen visa required for Vietnamese citizens",
                "health": "No special vaccinations required",
                "safety": "Generally safe, watch for pickpockets in tourist areas",
                "customs": "Greet with 'Bonjour', tipping 5-10%",
                "emergency_contacts": [
                    {"service": "Police", "number": "17"},
                    {"service": "Ambulance", "number": "15"},
                    {"service": "Fire", "number": "18"},
                ],
                "useful_phrases": [
                    {"english": "Hello", "local": "Bonjour"},
                    {"english": "Thank you", "local": "Merci"},
                    {"english": "Excuse me", "local": "Excusez-moi"},
                ],
                "important_tips": [
                    "Carry your passport at all times",
                    "Most shops close on Sundays",
                    "Metro runs until midnight",
                ],
            },
        }

    def test_formatter_initialization(self):
        """Test that formatter initializes correctly."""
        try:
            from travel_planner.guidebook.formatters.pdf_formatter import (
                EnhancedPDFFormatter,
            )

            formatter = EnhancedPDFFormatter()
            assert formatter is not None
            assert formatter.get_supported_formats() == ["pdf"]
        except ImportError as e:
            pytest.skip(f"WeasyPrint not installed: {e}")

    def test_generate_pdf(self, sample_travel_data):
        """Test PDF generation with sample data."""
        try:
            from travel_planner.guidebook.formatters.pdf_formatter import (
                EnhancedPDFFormatter,
            )
        except ImportError:
            pytest.skip("WeasyPrint not installed")

        formatter = EnhancedPDFFormatter()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_guidebook.pdf")
            result = formatter.format(sample_travel_data, output_path)

            assert result == output_path
            assert os.path.exists(output_path)

            # Check file size is reasonable (not empty, not too large)
            file_size = os.path.getsize(output_path)
            assert file_size > 1000, "PDF file too small"
            assert file_size < 10_000_000, "PDF file too large (>10MB)"

    def test_generate_pdf_vietnamese_content(self, sample_travel_data):
        """Test that Vietnamese characters are properly rendered."""
        try:
            from travel_planner.guidebook.formatters.pdf_formatter import (
                EnhancedPDFFormatter,
            )
        except ImportError:
            pytest.skip("WeasyPrint not installed")

        formatter = EnhancedPDFFormatter()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_vietnamese.pdf")
            formatter.format(sample_travel_data, output_path)

            assert os.path.exists(output_path)
            # PDF should be generated without encoding errors
            file_size = os.path.getsize(output_path)
            assert file_size > 1000

    def test_generate_pdf_minimal_data(self):
        """Test PDF generation with minimal data."""
        try:
            from travel_planner.guidebook.formatters.pdf_formatter import (
                EnhancedPDFFormatter,
            )
        except ImportError:
            pytest.skip("WeasyPrint not installed")

        minimal_data = {
            "destination": "Paris",
            "departure_point": "Hanoi",
            "departure_date": "2024-06-01",
            "trip_duration": 3,
            "num_travelers": 2,
        }

        formatter = EnhancedPDFFormatter()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_minimal.pdf")
            formatter.format(minimal_data, output_path)

            assert os.path.exists(output_path)

    def test_convenience_function(self, sample_travel_data):
        """Test the convenience function for PDF generation."""
        try:
            from travel_planner.guidebook.formatters.pdf_formatter import (
                generate_guidebook_pdf,
            )
        except ImportError:
            pytest.skip("WeasyPrint not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_convenience.pdf")
            generate_guidebook_pdf(sample_travel_data, output_path)

            assert os.path.exists(output_path)


class TestTemplateRendering:
    """Tests for HTML template rendering."""

    def test_template_exists(self):
        """Test that the HTML template file exists."""
        template_dir = Path(__file__).parent.parent / "templates"
        html_template = template_dir / "guidebook_enhanced.html"
        css_template = template_dir / "guidebook_enhanced.css"

        assert html_template.exists(), f"HTML template not found at {html_template}"
        assert css_template.exists(), f"CSS template not found at {css_template}"

    def test_template_contains_vietnamese_support(self):
        """Test that CSS includes Vietnamese font support."""
        template_dir = Path(__file__).parent.parent / "templates"
        css_path = template_dir / "guidebook_enhanced.css"

        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        assert "Noto Sans" in css_content, "CSS should include Noto Sans font"

    def test_template_contains_required_sections(self):
        """Test that HTML template contains all required sections."""
        template_dir = Path(__file__).parent.parent / "templates"
        html_path = template_dir / "guidebook_enhanced.html"

        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        required_sections = [
            "cover-page",
            "section-header",
            "weather",
            "logistics",
            "accommodation",
            "itinerary",
            "budget",
            "souvenirs",
            "advisory",
        ]

        for section in required_sections:
            assert section in html_content, f"Template missing section: {section}"
