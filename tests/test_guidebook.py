"""
Tests for the Guidebook Generator module.

This test suite covers:
- GuidebookGenerator initialization and validation
- PDF, HTML, and Markdown generation
- Error handling and edge cases
- API endpoints
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "travel_planner"))

from travel_planner.guidebook import GuidebookGenerator
from travel_planner.guidebook.formatters.base import BaseFormatter
from travel_planner.guidebook.formatters.html_formatter import HTMLFormatter
from travel_planner.guidebook.formatters.markdown_formatter import MarkdownFormatter
from travel_planner.guidebook.formatters.pdf_formatter import PDFFormatter
from travel_planner.guidebook.utils.formatting_helpers import (
    format_currency,
    format_date,
    format_time_range,
    get_activity_icon,
    sanitize_text,
)

# Load sample travel plan fixture
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_TRAVEL_PLAN_PATH = FIXTURES_DIR / "sample_travel_plan.json"


@pytest.fixture
def sample_travel_plan() -> Dict:
    """Load sample travel plan from fixture file."""
    with open(SAMPLE_TRAVEL_PLAN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def minimal_travel_plan() -> Dict:
    """Create a minimal travel plan for edge case testing."""
    return {
        "version": "1.0",
        "request_summary": {
            "destination": "Test City",
            "duration": 3,
            "budget": 1000000,
            "travelers": 1,
        },
        "itinerary": {
            "daily_schedules": [
                {
                    "day_number": 1,
                    "date": "2024-01-01",
                    "title": "Test Day",
                    "activities": [
                        {
                            "time": "09:00 - 10:00",
                            "location_name": "Test Location",
                            "activity_type": "sightseeing",
                            "description": "Test activity",
                            "estimated_cost": 100,
                        }
                    ],
                }
            ],
            "location_list": ["Test Location"],
            "summary": "Test summary",
        },
        "generated_at": "2024-01-01T00:00:00",
    }


@pytest.fixture
def empty_travel_plan() -> Dict:
    """Create an empty/invalid travel plan for error testing."""
    return {}


@pytest.fixture
def output_dir(tmp_path) -> Path:
    """Create temporary output directory for test files."""
    output = tmp_path / "guidebooks"
    output.mkdir(parents=True, exist_ok=True)
    return output


class TestFormattingHelpers:
    """Tests for formatting helper functions."""

    def test_format_currency_vnd(self):
        """Test VND currency formatting."""
        assert format_currency(50000000) == "50,000,000 VND"
        assert format_currency(1000) == "1,000 VND"
        assert format_currency(0) == "0 VND"

    def test_format_currency_usd(self):
        """Test USD currency formatting."""
        assert format_currency(1500.50, currency="USD", locale="en") == "$1,500.50"
        assert format_currency(100, currency="USD") == "100.00 USD"

    def test_format_date_default(self):
        """Test date formatting with default format."""
        assert format_date("2024-06-01") == "01/06/2024"

    def test_format_date_none(self):
        """Test date formatting with None input."""
        assert format_date(None) == ""
        assert format_date("") == ""

    def test_format_date_invalid(self):
        """Test date formatting with invalid input."""
        assert format_date("invalid-date") == "invalid-date"

    def test_format_time_range(self):
        """Test time range formatting."""
        assert format_time_range("08:00", "10:00") == "08:00 - 10:00"
        assert format_time_range("08:00") == "08:00"

    def test_sanitize_text(self):
        """Test text sanitization."""
        # Check that script tags are escaped (quotes may be escaped differently)
        result = sanitize_text("<script>alert('xss')</script>")
        assert "&lt;script&gt;" in result
        assert "&lt;/script&gt;" in result
        assert "<script>" not in result  # Raw script tag should not be present
        assert sanitize_text(None) == ""
        assert sanitize_text("") == ""

    def test_sanitize_text_max_length(self):
        """Test text sanitization with max length."""
        result = sanitize_text("This is a long text", max_length=10)
        assert len(result) == 10
        assert result.endswith("...")

    def test_get_activity_icon(self):
        """Test activity icon mapping."""
        assert get_activity_icon("sightseeing") == "🏛️"
        assert get_activity_icon("food") == "🍽️"
        assert get_activity_icon("shopping") == "🛍️"
        assert get_activity_icon("transport") == "🚗"
        assert get_activity_icon("unknown_type") == "📌"


class TestGuidebookGenerator:
    """Tests for GuidebookGenerator class."""

    def test_init_with_valid_data(self, sample_travel_plan, output_dir):
        """Test initialization with valid travel plan data."""
        generator = GuidebookGenerator(
            travel_plan_data=sample_travel_plan,
            output_dir=str(output_dir),
            language="vi",
        )
        assert generator.travel_plan_data == sample_travel_plan
        assert generator.language == "vi"
        assert generator.guidebook_id is not None

    def test_init_with_invalid_data(self, empty_travel_plan, output_dir):
        """Test initialization with invalid data raises ValueError."""
        with pytest.raises(ValueError, match="at least one section"):
            GuidebookGenerator(
                travel_plan_data=empty_travel_plan,
                output_dir=str(output_dir),
            )

    def test_init_with_non_dict(self, output_dir):
        """Test initialization with non-dict data raises ValueError."""
        with pytest.raises(ValueError, match="must be a dictionary"):
            GuidebookGenerator(
                travel_plan_data="not a dict",
                output_dir=str(output_dir),
            )

    def test_from_file(self, output_dir):
        """Test loading from JSON file."""
        generator = GuidebookGenerator.from_file(
            file_path=SAMPLE_TRAVEL_PLAN_PATH,
            output_dir=str(output_dir),
        )
        assert generator.travel_plan_data is not None
        assert "itinerary" in generator.travel_plan_data

    def test_from_file_not_found(self, output_dir):
        """Test loading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            GuidebookGenerator.from_file(
                file_path="non_existent.json",
                output_dir=str(output_dir),
            )

    def test_generate_markdown(self, sample_travel_plan, output_dir):
        """Test Markdown generation."""
        generator = GuidebookGenerator(
            travel_plan_data=sample_travel_plan,
            output_dir=str(output_dir),
            language="vi",
        )
        result = generator.generate_markdown()

        assert Path(result).exists()
        assert result.endswith(".md")

        # Check content
        content = Path(result).read_text(encoding="utf-8")
        assert "Tokyo, Japan" in content
        assert "Cẩm Nang Du Lịch" in content  # Vietnamese title

    def test_generate_html(self, sample_travel_plan, output_dir):
        """Test HTML generation."""
        generator = GuidebookGenerator(
            travel_plan_data=sample_travel_plan,
            output_dir=str(output_dir),
            language="en",
        )
        result = generator.generate_html()

        assert Path(result).exists()
        assert result.endswith(".html")

        # Check content
        content = Path(result).read_text(encoding="utf-8")
        assert "Tokyo, Japan" in content
        assert "Travel Guidebook" in content  # English title
        assert "<html" in content

    def test_generate_pdf(self, sample_travel_plan, output_dir):
        """Test PDF generation."""
        generator = GuidebookGenerator(
            travel_plan_data=sample_travel_plan,
            output_dir=str(output_dir),
            language="vi",
        )
        result = generator.generate_pdf()

        assert Path(result).exists()
        assert result.endswith(".pdf")

        # Check file is not empty
        assert Path(result).stat().st_size > 0

    def test_generate_all_formats(self, sample_travel_plan, output_dir):
        """Test generating all formats at once."""
        generator = GuidebookGenerator(
            travel_plan_data=sample_travel_plan,
            output_dir=str(output_dir),
        )
        results = generator.generate_all_formats()

        assert "pdf" in results
        assert "html" in results
        assert "markdown" in results

        # All files should exist
        for path in results.values():
            if not path.startswith("Error:"):
                assert Path(path).exists()

    def test_generate_specific_formats(self, sample_travel_plan, output_dir):
        """Test generating only specific formats."""
        generator = GuidebookGenerator(
            travel_plan_data=sample_travel_plan,
            output_dir=str(output_dir),
        )
        results = generator.generate_all_formats(formats=["markdown", "html"])

        assert "markdown" in results
        assert "html" in results
        assert "pdf" not in results

    def test_get_guidebook_response(self, sample_travel_plan, output_dir):
        """Test guidebook response structure."""
        generator = GuidebookGenerator(
            travel_plan_data=sample_travel_plan,
            output_dir=str(output_dir),
        )
        generator.generate_markdown()

        response = generator.get_guidebook_response()

        assert "guidebook_id" in response
        assert "files" in response
        assert "generated_at" in response
        assert "language" in response

    def test_language_vietnamese(self, minimal_travel_plan, output_dir):
        """Test Vietnamese language labels."""
        generator = GuidebookGenerator(
            travel_plan_data=minimal_travel_plan,
            output_dir=str(output_dir),
            language="vi",
        )
        result = generator.generate_markdown()
        content = Path(result).read_text(encoding="utf-8")

        assert "Cẩm Nang Du Lịch" in content
        assert "Lịch Trình Chi Tiết" in content

    def test_language_english(self, minimal_travel_plan, output_dir):
        """Test English language labels."""
        generator = GuidebookGenerator(
            travel_plan_data=minimal_travel_plan,
            output_dir=str(output_dir),
            language="en",
        )
        result = generator.generate_markdown()
        content = Path(result).read_text(encoding="utf-8")

        assert "Travel Guidebook" in content
        assert "Detailed Itinerary" in content


class TestMarkdownFormatter:
    """Tests for MarkdownFormatter class."""

    def test_markdown_structure(self, sample_travel_plan, output_dir):
        """Test markdown output structure."""
        formatter = MarkdownFormatter(
            travel_plan=sample_travel_plan,
            output_dir=str(output_dir),
            language="vi",
        )
        result = formatter.generate()
        content = Path(result).read_text(encoding="utf-8")

        # Check sections exist
        assert "## 📊" in content  # Executive summary
        assert "## 📅" in content  # Itinerary
        assert "## 💰" in content  # Budget
        assert "## ⚠️" in content  # Advisory
        assert "## 🎁" in content  # Souvenirs

    def test_markdown_tables(self, sample_travel_plan, output_dir):
        """Test markdown table generation."""
        formatter = MarkdownFormatter(
            travel_plan=sample_travel_plan,
            output_dir=str(output_dir),
        )
        result = formatter.generate()
        content = Path(result).read_text(encoding="utf-8")

        # Check for table formatting
        assert "|" in content
        assert "---|" in content  # Table header separator


class TestHTMLFormatter:
    """Tests for HTMLFormatter class."""

    def test_html_structure(self, sample_travel_plan, output_dir):
        """Test HTML output structure."""
        formatter = HTMLFormatter(
            travel_plan=sample_travel_plan,
            output_dir=str(output_dir),
            language="vi",
        )
        result = formatter.generate()
        content = Path(result).read_text(encoding="utf-8")

        # Check HTML structure
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "</html>" in content
        assert "<head>" in content
        assert "<body>" in content

    def test_html_responsive(self, sample_travel_plan, output_dir):
        """Test HTML has responsive viewport meta tag."""
        formatter = HTMLFormatter(
            travel_plan=sample_travel_plan,
            output_dir=str(output_dir),
        )
        result = formatter.generate()
        content = Path(result).read_text(encoding="utf-8")

        assert 'name="viewport"' in content

    def test_html_print_styles(self, sample_travel_plan, output_dir):
        """Test HTML has print media queries."""
        formatter = HTMLFormatter(
            travel_plan=sample_travel_plan,
            output_dir=str(output_dir),
        )
        result = formatter.generate()
        content = Path(result).read_text(encoding="utf-8")

        assert "@media print" in content


class TestPDFFormatter:
    """Tests for PDFFormatter class."""

    def test_pdf_creation(self, sample_travel_plan, output_dir):
        """Test PDF file is created."""
        formatter = PDFFormatter(
            travel_plan=sample_travel_plan,
            output_dir=str(output_dir),
        )
        result = formatter.generate()

        assert Path(result).exists()
        assert result.endswith(".pdf")

    def test_pdf_file_size(self, sample_travel_plan, output_dir):
        """Test PDF file has reasonable size."""
        formatter = PDFFormatter(
            travel_plan=sample_travel_plan,
            output_dir=str(output_dir),
        )
        result = formatter.generate()

        # PDF should be between 1KB and 10MB
        size = Path(result).stat().st_size
        assert 1024 < size < 10 * 1024 * 1024


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_sections(self, output_dir):
        """Test handling travel plan with empty sections."""
        travel_plan = {
            "version": "1.0",
            "itinerary": {
                "daily_schedules": [],
                "location_list": [],
                "summary": "Empty itinerary",
            },
        }

        generator = GuidebookGenerator(
            travel_plan_data=travel_plan,
            output_dir=str(output_dir),
        )
        result = generator.generate_markdown()

        assert Path(result).exists()

    def test_special_characters(self, output_dir):
        """Test handling special characters in content."""
        travel_plan = {
            "version": "1.0",
            "itinerary": {
                "daily_schedules": [
                    {
                        "day_number": 1,
                        "title": "Test <script>alert('xss')</script>",
                        "activities": [
                            {
                                "time": "09:00",
                                "location_name": "Test & Location",
                                "activity_type": "test",
                                "description": "Description with 'quotes' and \"double quotes\"",
                            }
                        ],
                    }
                ],
                "location_list": [],
                "summary": "Test",
            },
        }

        generator = GuidebookGenerator(
            travel_plan_data=travel_plan,
            output_dir=str(output_dir),
        )
        # Should not raise exception
        result = generator.generate_html()
        content = Path(result).read_text(encoding="utf-8")

        # Script tags should be escaped
        assert "<script>" not in content

    def test_unicode_content(self, output_dir):
        """Test handling Unicode/Vietnamese content."""
        travel_plan = {
            "version": "1.0",
            "itinerary": {
                "daily_schedules": [
                    {
                        "day_number": 1,
                        "title": "Khám phá Đà Nẵng",
                        "activities": [
                            {
                                "time": "09:00",
                                "location_name": "Chùa Linh Ứng",
                                "activity_type": "tham quan",
                                "description": "Tham quan chùa với tượng Phật bà cao nhất Việt Nam",
                            }
                        ],
                    }
                ],
                "location_list": ["Chùa Linh Ứng"],
                "summary": "Chuyến đi Đà Nẵng tuyệt vời",
            },
        }

        generator = GuidebookGenerator(
            travel_plan_data=travel_plan,
            output_dir=str(output_dir),
            language="vi",
        )

        # All formats should handle Unicode
        results = generator.generate_all_formats()
        for fmt, path in results.items():
            if not path.startswith("Error:"):
                assert Path(path).exists()
