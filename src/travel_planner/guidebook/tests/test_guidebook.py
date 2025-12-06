"""Tests for the guidebook module."""

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


class TestGuidebookGenerator:
    """Tests for the GuidebookGenerator class."""

    @pytest.fixture
    def sample_travel_data(self):
        """Create sample travel plan data for testing."""
        return {
            "request_summary": {
                "destination": "Tokyo, Japan",
                "duration": 5,
                "travelers": 2,
                "budget": 50000000,
            },
            "itinerary": {
                "summary": "A 5-day trip to Tokyo exploring culture and food",
                "location_list": ["Shibuya", "Shinjuku", "Asakusa"],
                "daily_schedules": [
                    {
                        "day_number": 1,
                        "title": "Arrival Day",
                        "date": "2024-06-01",
                        "activities": [
                            {
                                "time": "18:00",
                                "description": "Check-in at hotel",
                                "location_name": "Shinjuku",
                                "activity_type": "check-in",
                                "estimated_cost": 0,
                            },
                            {
                                "time": "20:00",
                                "description": "Welcome dinner",
                                "location_name": "Shibuya",
                                "activity_type": "food",
                                "estimated_cost": 100000,
                            },
                        ],
                    },
                ],
            },
            "budget": {
                "total_estimated_cost": 45000000,
                "budget_status": "Within Budget",
                "categories": [
                    {"category_name": "Flights", "estimated_cost": 20000000},
                    {"category_name": "Accommodation", "estimated_cost": 15000000},
                ],
                "recommendations": ["Book flights in advance"],
            },
            "advisory": {
                "warnings_and_tips": ["Check visa requirements"],
                "visa_info": "Visa-free for 90 days",
                "safety_tips": ["Japan is very safe"],
            },
            "souvenirs": [
                {
                    "item_name": "Japanese Green Tea",
                    "description": "High quality matcha",
                    "estimated_price": "2000 JPY",
                    "where_to_buy": "Uji, Kyoto",
                },
            ],
            "generated_at": "2024-05-15T10:00:00",
            "version": "1.0",
        }

    def test_generator_initialization(self, sample_travel_data):
        """Test that GuidebookGenerator initializes correctly."""
        from travel_planner.guidebook import GuidebookGenerator

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = GuidebookGenerator(
                sample_travel_data, output_dir=tmpdir, language="vi"
            )
            assert generator is not None
            assert generator.language == "vi"

    def test_generate_all_formats(self, sample_travel_data):
        """Test generating all guidebook formats."""
        from travel_planner.guidebook import GuidebookGenerator

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = GuidebookGenerator(
                sample_travel_data, output_dir=tmpdir, language="vi"
            )
            results = generator.generate_all_formats()

            assert "pdf" in results
            assert "html" in results
            assert "markdown" in results

            # All files should exist
            for fmt, path in results.items():
                assert os.path.exists(path), f"{fmt} file not generated"
                assert os.path.getsize(path) > 0, f"{fmt} file is empty"

    def test_generate_pdf(self, sample_travel_data):
        """Test PDF generation."""
        from travel_planner.guidebook import GuidebookGenerator

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = GuidebookGenerator(
                sample_travel_data, output_dir=tmpdir, language="vi"
            )
            pdf_path = generator.generate_pdf()

            assert os.path.exists(pdf_path)
            assert pdf_path.endswith(".pdf")
            assert os.path.getsize(pdf_path) > 1000  # Should be substantial

    def test_generate_html(self, sample_travel_data):
        """Test HTML generation."""
        from travel_planner.guidebook import GuidebookGenerator

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = GuidebookGenerator(
                sample_travel_data, output_dir=tmpdir, language="vi"
            )
            html_path = generator.generate_html()

            assert os.path.exists(html_path)
            assert html_path.endswith(".html")

            # Check content
            with open(html_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "Tokyo" in content
                assert "<!DOCTYPE html>" in content

    def test_generate_markdown(self, sample_travel_data):
        """Test Markdown generation."""
        from travel_planner.guidebook import GuidebookGenerator

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = GuidebookGenerator(
                sample_travel_data, output_dir=tmpdir, language="vi"
            )
            md_path = generator.generate_markdown()

            assert os.path.exists(md_path)
            assert md_path.endswith(".md")

            # Check content
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "Tokyo" in content
                assert "# " in content  # Should have headers

    def test_invalid_data_rejected(self):
        """Test that invalid data is properly rejected."""
        from travel_planner.guidebook import GuidebookGenerator

        with tempfile.TemporaryDirectory() as tmpdir:
            # Empty dict should be rejected
            with pytest.raises(ValueError):
                GuidebookGenerator({}, output_dir=tmpdir)

            # Non-dict should be rejected
            with pytest.raises(ValueError):
                GuidebookGenerator("invalid", output_dir=tmpdir)

    def test_english_language_support(self, sample_travel_data):
        """Test English language generation."""
        from travel_planner.guidebook import GuidebookGenerator

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = GuidebookGenerator(
                sample_travel_data, output_dir=tmpdir, language="en"
            )
            html_path = generator.generate_html()

            with open(html_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "Travel Guidebook" in content or "Trip Summary" in content


class TestPDFFormatter:
    """Tests for the standard PDFFormatter class."""

    @pytest.fixture
    def sample_travel_data(self):
        """Create sample travel plan data for testing."""
        return {
            "request_summary": {
                "destination": "Tokyo, Japan",
                "duration": 5,
                "travelers": 2,
                "budget": 50000000,
            },
            "itinerary": {
                "summary": "A trip to Tokyo",
                "daily_schedules": [
                    {
                        "day_number": 1,
                        "title": "Arrival",
                        "activities": [
                            {
                                "time": "18:00",
                                "description": "Check-in",
                                "location_name": "Hotel",
                            }
                        ],
                    }
                ],
            },
            "budget": {
                "total_estimated_cost": 45000000,
                "budget_status": "OK",
                "categories": [{"category_name": "Flights", "estimated_cost": 20000000}],
            },
            "generated_at": "2024-05-15",
            "version": "1.0",
        }

    def test_pdf_formatter_initialization(self, sample_travel_data):
        """Test that PDFFormatter initializes correctly."""
        from travel_planner.guidebook.formatters.pdf_formatter import PDFFormatter

        with tempfile.TemporaryDirectory() as tmpdir:
            formatter = PDFFormatter(sample_travel_data, output_dir=tmpdir)
            assert formatter is not None

    def test_pdf_formatter_generate(self, sample_travel_data):
        """Test PDFFormatter generates PDF."""
        from travel_planner.guidebook.formatters.pdf_formatter import PDFFormatter

        with tempfile.TemporaryDirectory() as tmpdir:
            formatter = PDFFormatter(sample_travel_data, output_dir=tmpdir)
            pdf_path = formatter.generate()

            assert os.path.exists(pdf_path)
            assert pdf_path.endswith(".pdf")
            assert os.path.getsize(pdf_path) > 1000


class TestHTMLFormatter:
    """Tests for the HTMLFormatter class."""

    @pytest.fixture
    def sample_travel_data(self):
        """Create sample travel plan data for testing."""
        return {
            "request_summary": {
                "destination": "Paris, France",
                "duration": 3,
                "travelers": 2,
                "budget": 30000000,
            },
            "itinerary": {
                "summary": "A trip to Paris",
                "daily_schedules": [],
            },
            "generated_at": "2024-05-15",
            "version": "1.0",
        }

    def test_html_formatter_initialization(self, sample_travel_data):
        """Test that HTMLFormatter initializes correctly."""
        from travel_planner.guidebook.formatters.html_formatter import HTMLFormatter

        with tempfile.TemporaryDirectory() as tmpdir:
            formatter = HTMLFormatter(sample_travel_data, output_dir=tmpdir)
            assert formatter is not None

    def test_html_formatter_generate(self, sample_travel_data):
        """Test HTMLFormatter generates HTML."""
        from travel_planner.guidebook.formatters.html_formatter import HTMLFormatter

        with tempfile.TemporaryDirectory() as tmpdir:
            formatter = HTMLFormatter(sample_travel_data, output_dir=tmpdir)
            html_path = formatter.generate()

            assert os.path.exists(html_path)
            assert html_path.endswith(".html")

            with open(html_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "Paris" in content


class TestMarkdownFormatter:
    """Tests for the MarkdownFormatter class."""

    @pytest.fixture
    def sample_travel_data(self):
        """Create sample travel plan data for testing."""
        return {
            "request_summary": {
                "destination": "London, UK",
                "duration": 4,
                "travelers": 1,
                "budget": 25000000,
            },
            "itinerary": {"summary": "A trip to London"},
            "generated_at": "2024-05-15",
            "version": "1.0",
        }

    def test_markdown_formatter_initialization(self, sample_travel_data):
        """Test that MarkdownFormatter initializes correctly."""
        from travel_planner.guidebook.formatters.markdown_formatter import MarkdownFormatter

        with tempfile.TemporaryDirectory() as tmpdir:
            formatter = MarkdownFormatter(sample_travel_data, output_dir=tmpdir)
            assert formatter is not None

    def test_markdown_formatter_generate(self, sample_travel_data):
        """Test MarkdownFormatter generates Markdown."""
        from travel_planner.guidebook.formatters.markdown_formatter import MarkdownFormatter

        with tempfile.TemporaryDirectory() as tmpdir:
            formatter = MarkdownFormatter(sample_travel_data, output_dir=tmpdir)
            md_path = formatter.generate()

            assert os.path.exists(md_path)
            assert md_path.endswith(".md")

            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "London" in content
                assert "#" in content  # Has markdown headers


class TestEnhancedPDFFormatter:
    """Tests for the EnhancedPDFFormatter class (WeasyPrint-based)."""

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
                ],
                "packing_suggestions": ["Light jacket", "Umbrella"],
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
                                "name": "Check-in at hotel",
                                "description": "Settle in and rest",
                            }
                        ],
                    }
                ]
            },
            "budget": {"total": "50,000,000 VND"},
        }

    def test_enhanced_formatter_initialization(self):
        """Test that EnhancedPDFFormatter initializes correctly."""
        try:
            from travel_planner.guidebook.formatters.enhanced_pdf_formatter import (
                EnhancedPDFFormatter,
            )

            formatter = EnhancedPDFFormatter()
            assert formatter is not None
            assert formatter.get_supported_formats() == ["pdf"]
        except ImportError as e:
            pytest.skip(f"WeasyPrint not installed: {e}")

    def test_enhanced_generate_pdf(self, sample_travel_data):
        """Test EnhancedPDFFormatter PDF generation with sample data."""
        try:
            from travel_planner.guidebook.formatters.enhanced_pdf_formatter import (
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
            assert os.path.getsize(output_path) > 1000


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
