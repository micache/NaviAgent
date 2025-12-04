"""Guidebook generation module for creating professional travel guidebook PDFs."""

from travel_planner.guidebook.generator import GuidebookGenerator
from travel_planner.guidebook.image_fetcher import ImageFetcher
from travel_planner.guidebook.formatters.pdf_formatter import PDFFormatter
from travel_planner.guidebook.formatters.html_formatter import HTMLFormatter
from travel_planner.guidebook.formatters.markdown_formatter import MarkdownFormatter

# Lazy import to handle optional WeasyPrint dependency
try:
    from travel_planner.guidebook.formatters.enhanced_pdf_formatter import (
        EnhancedPDFFormatter,
    )
except ImportError:
    EnhancedPDFFormatter = None  # type: ignore[assignment,misc]

__all__ = [
    "GuidebookGenerator",
    "PDFFormatter",
    "HTMLFormatter",
    "MarkdownFormatter",
    "EnhancedPDFFormatter",
    "ImageFetcher",
]
