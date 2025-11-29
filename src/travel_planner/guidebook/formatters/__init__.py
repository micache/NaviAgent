"""Formatters module for guidebook generation."""

from travel_planner.guidebook.formatters.base_formatter import BaseFormatter

# Lazy import to handle optional WeasyPrint dependency
try:
    from travel_planner.guidebook.formatters.pdf_formatter import EnhancedPDFFormatter
except ImportError:
    EnhancedPDFFormatter = None  # type: ignore[assignment,misc]

__all__ = ["BaseFormatter", "EnhancedPDFFormatter"]
