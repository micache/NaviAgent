"""Formatters module for guidebook generation."""

from travel_planner.guidebook.formatters.base import BaseFormatter
from travel_planner.guidebook.formatters.html_formatter import HTMLFormatter
from travel_planner.guidebook.formatters.markdown_formatter import MarkdownFormatter
from travel_planner.guidebook.formatters.pdf_formatter import PDFFormatter

# Lazy import to handle optional WeasyPrint dependency
try:
    from travel_planner.guidebook.formatters.enhanced_pdf_formatter import (
        EnhancedPDFFormatter,
    )
except ImportError:
    EnhancedPDFFormatter = None  # type: ignore[assignment,misc]

__all__ = [
    "BaseFormatter",
    "PDFFormatter",
    "HTMLFormatter",
    "MarkdownFormatter",
    "EnhancedPDFFormatter",
]
