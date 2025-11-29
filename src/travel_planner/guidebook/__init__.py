"""Guidebook generation module for creating professional travel guidebook PDFs."""

from travel_planner.guidebook.image_fetcher import ImageFetcher

# Lazy import to handle optional WeasyPrint dependency
try:
    from travel_planner.guidebook.formatters.pdf_formatter import EnhancedPDFFormatter
except ImportError:
    EnhancedPDFFormatter = None  # type: ignore[assignment,misc]

__all__ = ["EnhancedPDFFormatter", "ImageFetcher"]
