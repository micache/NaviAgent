"""Destination suggestion module.

This module provides tools for suggesting travel destinations based on:
- Text descriptions (suggest_from_text)
- Images (suggest_from_images)
"""

from reception.suggest_destination.suggest_from_images import (
    DuckDuckGoImagesAgent,
    GoogleVisionImagesAgent,
)
from reception.suggest_destination.suggest_from_text import (
    TextDestinationAgent,
    get_destination_suggestion,
)

__all__ = [
    "TextDestinationAgent",
    "get_destination_suggestion",
    "GoogleVisionImagesAgent",
    "DuckDuckGoImagesAgent",
]
