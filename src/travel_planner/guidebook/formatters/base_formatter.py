"""Base formatter interface for guidebook generation."""

from abc import ABC, abstractmethod
from typing import Any


class BaseFormatter(ABC):
    """Abstract base class for guidebook formatters."""

    @abstractmethod
    def format(self, data: dict[str, Any], output_path: str) -> str:
        """Format guidebook data and save to output path.

        Args:
            data: Dictionary containing travel plan data
            output_path: Path to save the formatted output

        Returns:
            Path to the generated file
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        """Return list of supported output formats.

        Returns:
            List of supported format strings (e.g., ['pdf', 'html'])
        """
        pass
