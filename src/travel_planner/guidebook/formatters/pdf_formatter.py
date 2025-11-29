"""Enhanced PDF formatter using WeasyPrint for professional guidebook generation."""

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader

from travel_planner.guidebook.formatters.base_formatter import BaseFormatter
from travel_planner.guidebook.image_fetcher import ImageFetcher

try:
    from weasyprint import CSS, HTML
    from weasyprint.text.fonts import FontConfiguration

    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


class EnhancedPDFFormatter(BaseFormatter):
    """Professional PDF formatter using WeasyPrint with Vietnamese font support.

    This formatter creates magazine-quality travel guidebooks with:
    - Full Vietnamese character support via Noto Sans
    - Multi-column layouts
    - Color-coded sections
    - Integrated maps and images
    - Professional typography
    """

    def __init__(self, unsplash_api_key: Optional[str] = None):
        """Initialize the PDF formatter.

        Args:
            unsplash_api_key: Optional API key for fetching real images from Unsplash
        """
        if not WEASYPRINT_AVAILABLE:
            raise ImportError(
                "WeasyPrint is required for PDF generation. "
                "Install it with: pip install weasyprint"
            )

        self.font_config = FontConfiguration()
        self.image_fetcher = ImageFetcher(unsplash_api_key=unsplash_api_key)

        # Set up Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=True)

        # Register custom filters
        self.jinja_env.filters["format_date"] = self._format_date
        self.jinja_env.filters["format_currency"] = self._format_currency

    def format(self, data: dict[str, Any], output_path: str) -> str:
        """Generate a professional PDF guidebook from travel plan data.

        Args:
            data: Dictionary containing travel plan data with keys like:
                - destination: Trip destination
                - departure_point: Starting location
                - departure_date: Trip start date
                - trip_duration: Number of days
                - num_travelers: Number of travelers
                - travel_style: Type of travel
                - customer_notes: Optional notes
                - weather: Weather information
                - logistics: Transportation details
                - accommodation: Hotel recommendations
                - itinerary: Day-by-day schedule
                - budget: Budget breakdown
                - souvenirs: Shopping recommendations
                - advisory: Travel advisory information
            output_path: Path to save the generated PDF

        Returns:
            Path to the generated PDF file
        """
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Extract and prepare data
        template_data = self._prepare_template_data(data)

        # Fetch images
        template_data["hero_image"] = self._get_hero_image(
            template_data.get("destination", "Travel")
        )
        template_data["route_map"] = self._get_route_map(template_data)
        template_data["location_images"] = self._fetch_location_images(data)

        # Render HTML template
        template = self.jinja_env.get_template("guidebook_enhanced.html")
        html_content = template.render(**template_data)

        # Load CSS
        template_dir = Path(__file__).parent.parent / "templates"
        css_path = template_dir / "guidebook_enhanced.css"

        css = CSS(filename=str(css_path), font_config=self.font_config)

        # Generate PDF
        html = HTML(string=html_content, base_url=str(template_dir))
        html.write_pdf(str(output_file), stylesheets=[css], font_config=self.font_config)

        return str(output_file)

    def get_supported_formats(self) -> list[str]:
        """Return list of supported output formats.

        Returns:
            List containing 'pdf' as the supported format
        """
        return ["pdf"]

    def _prepare_template_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Prepare and normalize data for template rendering.

        Args:
            data: Raw travel plan data

        Returns:
            Normalized data dictionary for template
        """
        # Handle different data formats (direct dict or nested structures)
        template_data = {}

        # Extract request summary if present
        request_summary = data.get("request_summary", data)

        # Basic trip information
        template_data["destination"] = request_summary.get(
            "destination", data.get("destination", "Unknown Destination")
        )
        template_data["departure_point"] = request_summary.get(
            "departure_point", data.get("departure_point", "")
        )

        # Handle date conversion
        dep_date = request_summary.get("departure_date", data.get("departure_date"))
        if isinstance(dep_date, str):
            template_data["departure_date"] = dep_date
        elif isinstance(dep_date, (date, datetime)):
            template_data["departure_date"] = dep_date.strftime("%Y-%m-%d")
        else:
            template_data["departure_date"] = str(dep_date) if dep_date else ""

        # Calculate return date
        trip_duration = request_summary.get("trip_duration", data.get("trip_duration", 7))
        template_data["trip_duration"] = trip_duration

        if isinstance(dep_date, (date, datetime)):
            return_date = dep_date + timedelta(days=trip_duration)
            template_data["return_date"] = return_date.strftime("%Y-%m-%d")
        else:
            template_data["return_date"] = ""

        template_data["num_travelers"] = request_summary.get(
            "num_travelers", data.get("num_travelers", 1)
        )
        template_data["travel_style"] = request_summary.get(
            "travel_style", data.get("travel_style", "")
        )
        template_data["customer_notes"] = request_summary.get(
            "customer_notes", data.get("customer_notes", "")
        )
        template_data["total_budget"] = request_summary.get("budget", data.get("budget", ""))

        # Section data
        template_data["weather"] = self._normalize_weather(data.get("weather"))
        template_data["logistics"] = self._normalize_logistics(data.get("logistics"))
        template_data["accommodation"] = self._normalize_accommodation(data.get("accommodation"))
        template_data["itinerary"] = self._normalize_itinerary(data.get("itinerary"))
        template_data["budget"] = self._normalize_budget(data.get("budget"))
        template_data["souvenirs"] = self._normalize_souvenirs(data.get("souvenirs"))
        template_data["advisory"] = self._normalize_advisory(data.get("advisory"))

        # Metadata
        template_data["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        return template_data

    def _normalize_weather(self, weather: Any) -> Optional[dict]:
        """Normalize weather data for template."""
        if not weather:
            return None
        if isinstance(weather, dict):
            return weather
        return {"description": str(weather)}

    def _normalize_logistics(self, logistics: Any) -> Optional[dict]:
        """Normalize logistics data for template."""
        if not logistics:
            return None
        if isinstance(logistics, dict):
            return logistics
        return {"description": str(logistics)}

    def _normalize_accommodation(self, accommodation: Any) -> Optional[dict]:
        """Normalize accommodation data for template."""
        if not accommodation:
            return None
        if isinstance(accommodation, dict):
            return accommodation
        return {"description": str(accommodation)}

    def _normalize_itinerary(self, itinerary: Any) -> Optional[dict]:
        """Normalize itinerary data for template."""
        if not itinerary:
            return None
        if isinstance(itinerary, dict):
            # Ensure days is a list
            if "days" not in itinerary and "schedule" in itinerary:
                itinerary["days"] = itinerary["schedule"]
            return itinerary
        if isinstance(itinerary, list):
            return {"days": itinerary}
        return {"description": str(itinerary)}

    def _normalize_budget(self, budget: Any) -> Optional[dict]:
        """Normalize budget data for template."""
        if not budget:
            return None
        if isinstance(budget, dict):
            return budget
        if isinstance(budget, (int, float)):
            return {"total": f"{budget:,.0f}"}
        return {"total": str(budget)}

    def _normalize_souvenirs(self, souvenirs: Any) -> Optional[dict]:
        """Normalize souvenirs data for template."""
        if not souvenirs:
            return None
        if isinstance(souvenirs, dict):
            return souvenirs
        if isinstance(souvenirs, list):
            return {"recommendations": souvenirs}
        return {"description": str(souvenirs)}

    def _normalize_advisory(self, advisory: Any) -> Optional[dict]:
        """Normalize advisory data for template."""
        if not advisory:
            return None
        if isinstance(advisory, dict):
            return advisory
        return {"description": str(advisory)}

    def _get_hero_image(self, destination: str) -> str:
        """Get hero image for the cover page.

        Args:
            destination: Name of the destination

        Returns:
            Data URI for the hero image
        """
        image_data = self.image_fetcher.get_destination_hero(destination)
        return self.image_fetcher.get_data_uri(image_data)

    def _get_route_map(self, data: dict[str, Any]) -> Optional[str]:
        """Generate route map from itinerary data.

        Args:
            data: Template data dictionary

        Returns:
            Data URI for the route map or None
        """
        # Extract locations from itinerary
        locations = []
        itinerary = data.get("itinerary")

        if itinerary and isinstance(itinerary, dict):
            days = itinerary.get("days", [])
            for day in days:
                if isinstance(day, dict):
                    # Try to extract location from day title or activities
                    if "title" in day:
                        locations.append(day["title"])
                    elif "location" in day:
                        locations.append(day["location"])
                    elif "activities" in day and day["activities"]:
                        first_activity = day["activities"][0]
                        if isinstance(first_activity, dict) and "name" in first_activity:
                            locations.append(first_activity["name"])

        # If no locations found, use destination
        if not locations:
            destination = data.get("destination", "Destination")
            locations = [destination]

        image_data = self.image_fetcher.generate_route_map(
            locations, data.get("destination", "Route Map")
        )
        return self.image_fetcher.get_data_uri(image_data)

    def _fetch_location_images(self, data: dict[str, Any]) -> dict[str, str]:
        """Fetch images for specific locations.

        Args:
            data: Travel plan data

        Returns:
            Dictionary mapping location names to data URIs
        """
        location_images = {}
        itinerary = data.get("itinerary")

        if itinerary and isinstance(itinerary, dict):
            days = itinerary.get("days", [])
            for day in days[:5]:  # Limit to first 5 days
                if isinstance(day, dict):
                    location = day.get("title") or day.get("location", "")
                    if location and location not in location_images:
                        image_data = self.image_fetcher.get_location_image(location)
                        location_images[location] = self.image_fetcher.get_data_uri(image_data)

        return location_images

    @staticmethod
    def _format_date(value: Any) -> str:
        """Format date for display.

        Args:
            value: Date value to format

        Returns:
            Formatted date string
        """
        if isinstance(value, (date, datetime)):
            return value.strftime("%B %d, %Y")
        return str(value) if value else ""

    @staticmethod
    def _format_currency(value: Any, currency: str = "VND") -> str:
        """Format currency value for display.

        Args:
            value: Numeric value to format
            currency: Currency code

        Returns:
            Formatted currency string
        """
        if isinstance(value, (int, float)):
            return f"{value:,.0f} {currency}"
        return str(value) if value else ""


def generate_guidebook_pdf(
    travel_plan_data: dict[str, Any],
    output_path: str,
    unsplash_api_key: Optional[str] = None,
) -> str:
    """Convenience function to generate a guidebook PDF.

    Args:
        travel_plan_data: Dictionary containing travel plan data
        output_path: Path to save the generated PDF
        unsplash_api_key: Optional API key for real images

    Returns:
        Path to the generated PDF file
    """
    formatter = EnhancedPDFFormatter(unsplash_api_key=unsplash_api_key)
    return formatter.format(travel_plan_data, output_path)
