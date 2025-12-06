"""
Main Guidebook Generator module.

This module provides the GuidebookGenerator class for creating
travel guidebooks in multiple formats (PDF, HTML, Markdown) from
travel plan JSON data.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from travel_planner.guidebook.formatters.html_formatter import HTMLFormatter
from travel_planner.guidebook.formatters.markdown_formatter import MarkdownFormatter
from travel_planner.guidebook.formatters.pdf_formatter import PDFFormatter

logger = logging.getLogger(__name__)


class GuidebookGenerator:
    """
    Main class for generating travel guidebooks from travel plan JSON.

    Features:
    - Load and validate travel_plan_output.json
    - Generate guidebooks in multiple formats (PDF, HTML, Markdown)
    - Customizable templates
    - Error handling and logging
    - Internationalization support (Vietnamese + English)

    Example usage:
        >>> from travel_planner.guidebook import GuidebookGenerator

        # From JSON file
        >>> generator = GuidebookGenerator.from_file("travel_plan_output.json")
        >>> files = generator.generate_all_formats()

        # From TravelPlan object
        >>> generator = GuidebookGenerator(travel_plan.dict())
        >>> pdf_path = generator.generate_pdf()
    """

    SUPPORTED_FORMATS = ["pdf", "html", "markdown", "md"]

    def __init__(
        self,
        travel_plan_data: Dict[str, Any],
        output_dir: str = "guidebooks",
        language: str = "vi",
    ):
        """
        Initialize the GuidebookGenerator.

        Args:
            travel_plan_data: Dictionary containing travel plan data.
            output_dir: Directory to save generated guidebooks.
            language: Language for content (vi or en).

        Raises:
            ValueError: If travel_plan_data is invalid.
        """
        self._validate_travel_plan(travel_plan_data)

        self.travel_plan_data = travel_plan_data
        self.output_dir = Path(output_dir)
        self.language = language
        self.guidebook_id = str(uuid.uuid4())
        self.generated_files: Dict[str, str] = {}

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"GuidebookGenerator initialized. ID: {self.guidebook_id}, "
            f"Output: {self.output_dir}, Language: {self.language}"
        )

    @classmethod
    def from_file(
        cls,
        file_path: Union[str, Path],
        output_dir: str = "guidebooks",
        language: str = "vi",
    ) -> "GuidebookGenerator":
        """
        Create a GuidebookGenerator from a JSON file.

        Args:
            file_path: Path to the travel plan JSON file.
            output_dir: Directory to save generated guidebooks.
            language: Language for content.

        Returns:
            GuidebookGenerator instance.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Travel plan file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            travel_plan_data = json.load(f)

        return cls(travel_plan_data, output_dir, language)

    def _validate_travel_plan(self, data: Dict[str, Any]) -> None:
        """
        Validate the travel plan data structure.

        Args:
            data: Travel plan data dictionary.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        if not isinstance(data, dict):
            raise ValueError("Travel plan data must be a dictionary")

        # Check for at least some content
        has_content = any(
            [
                data.get("itinerary"),
                data.get("budget"),
                data.get("advisory"),
                data.get("logistics"),
                data.get("accommodation"),
                data.get("souvenirs"),
                data.get("team_full_response"),
            ]
        )

        if not has_content:
            raise ValueError("Travel plan must contain at least one section of data")

        logger.debug("Travel plan validation passed")

    def generate_all_formats(
        self,
        formats: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        Generate guidebooks in all specified formats.

        Args:
            formats: List of formats to generate. Defaults to ["pdf", "html", "markdown"].

        Returns:
            Dictionary mapping format names to generated file paths.
    
        Example:
            >>> files = generator.generate_all_formats()
            >>> print(files)
            {'pdf': 'guidebooks/guidebook_tokyo.pdf',
             'html': 'guidebooks/guidebook_tokyo.html',
             'markdown': 'guidebooks/guidebook_tokyo.md'}
        """
        if formats is None:
            formats = ["pdf", "html", "markdown"]

        logger.info(f"Generating guidebooks in formats: {formats}")
        results = {}

        for fmt in formats:
            fmt_lower = fmt.lower()
            try:
                if fmt_lower == "pdf":
                    results["pdf"] = self.generate_pdf()
                elif fmt_lower == "html":
                    results["html"] = self.generate_html()
                elif fmt_lower in ("markdown", "md"):
                    results["markdown"] = self.generate_markdown()
                else:
                    logger.warning(f"Unsupported format: {fmt}")
            except Exception as e:
                logger.error(f"Error generating {fmt} guidebook: {e}")
                results[fmt_lower] = f"Error: {str(e)}"

        self.generated_files = {k: v for k, v in results.items() if not v.startswith("Error:")}
        return results

    def generate_pdf(self, output_path: Optional[str] = None) -> str:
        """
        Generate PDF guidebook.

        Args:
            output_path: Optional custom output path.

        Returns:
            Path to the generated PDF file.

        Raises:
            Exception: If PDF generation fails.
        """
        logger.info("Generating PDF guidebook...")

        formatter = PDFFormatter(
            travel_plan=self.travel_plan_data,
            output_dir=str(self.output_dir),
            language=self.language,
        )

        result = formatter.generate(output_path)
        self.generated_files["pdf"] = result

        logger.info(f"PDF guidebook generated: {result}")
        return result

    def generate_html(self, output_path: Optional[str] = None) -> str:
        """
        Generate HTML guidebook.

        Args:
            output_path: Optional custom output path.

        Returns:
            Path to the generated HTML file.

        Raises:
            Exception: If HTML generation fails.
        """
        logger.info("Generating HTML guidebook...")

        formatter = HTMLFormatter(
            travel_plan=self.travel_plan_data,
            output_dir=str(self.output_dir),
            language=self.language,
        )

        result = formatter.generate(output_path)
        self.generated_files["html"] = result

        logger.info(f"HTML guidebook generated: {result}")
        return result

    def generate_markdown(self, output_path: Optional[str] = None) -> str:
        """
        Generate Markdown guidebook.

        Args:
            output_path: Optional custom output path.

        Returns:
            Path to the generated Markdown file.

        Raises:
            Exception: If Markdown generation fails.
        """
        logger.info("Generating Markdown guidebook...")

        formatter = MarkdownFormatter(
            travel_plan=self.travel_plan_data,
            output_dir=str(self.output_dir),
            language=self.language,
        )

        result = formatter.generate(output_path)
        self.generated_files["markdown"] = result

        logger.info(f"Markdown guidebook generated: {result}")
        return result

    def get_guidebook_response(self) -> Dict[str, Any]:
        """
        Get a structured response with guidebook information.

        Returns:
            Dictionary containing guidebook ID, file paths, and metadata.
        """
        return {
            "guidebook_id": self.guidebook_id,
            "files": self.generated_files,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "language": self.language,
            "output_dir": str(self.output_dir),
        }
