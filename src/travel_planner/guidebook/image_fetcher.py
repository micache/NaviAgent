"""Image fetcher for guidebook generation with placeholder support."""

import base64
from dataclasses import dataclass
from typing import Optional


@dataclass
class ImageData:
    """Container for image data."""

    data: str  # Base64 encoded data or URL
    mime_type: str
    is_base64: bool = True
    caption: Optional[str] = None


class ImageFetcher:
    """Fetch and generate images for guidebook.

    Provides placeholder images for destinations and locations
    when API access is not available.
    """

    # Default placeholder colors for different content types
    PLACEHOLDER_COLORS = {
        "hero": "#667eea",  # Purple gradient start
        "location": "#764ba2",  # Purple gradient end
        "map": "#4a5568",  # Gray for maps
    }

    def __init__(self, unsplash_api_key: Optional[str] = None):
        """Initialize ImageFetcher.

        Args:
            unsplash_api_key: Optional Unsplash API key for fetching real images
        """
        self.unsplash_api_key = unsplash_api_key

    def get_destination_hero(self, destination: str) -> ImageData:
        """Get hero image for destination.

        Args:
            destination: Name of the destination

        Returns:
            ImageData with placeholder SVG
        """
        svg = self._create_hero_placeholder(destination)
        return ImageData(
            data=self._svg_to_base64(svg),
            mime_type="image/svg+xml",
            is_base64=True,
            caption=f"{destination} - Travel Guide",
        )

    def get_location_image(self, location: str) -> ImageData:
        """Get thumbnail image for a specific location.

        Args:
            location: Name of the location

        Returns:
            ImageData with placeholder SVG
        """
        svg = self._create_location_placeholder(location)
        return ImageData(
            data=self._svg_to_base64(svg),
            mime_type="image/svg+xml",
            is_base64=True,
            caption=location,
        )

    def generate_route_map(self, locations: list[str], destination: str = "Route Map") -> ImageData:
        """Generate a route map visualization.

        Args:
            locations: List of location names to include in the map
            destination: Title for the map

        Returns:
            ImageData with placeholder SVG map
        """
        svg = self._create_map_placeholder(locations, destination)
        return ImageData(
            data=self._svg_to_base64(svg),
            mime_type="image/svg+xml",
            is_base64=True,
            caption=f"Route Map - {destination}",
        )

    def _create_hero_placeholder(self, destination: str) -> str:
        """Create a hero placeholder SVG with destination name."""
        # Escape HTML special characters
        safe_destination = self._escape_html(destination)
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <defs>
        <linearGradient id="heroGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{self.PLACEHOLDER_COLORS['hero']};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{self.PLACEHOLDER_COLORS['location']};stop-opacity:1" />
        </linearGradient>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
        </pattern>
    </defs>
    <rect width="800" height="400" fill="url(#heroGrad)"/>
    <rect width="800" height="400" fill="url(#grid)"/>
    <g transform="translate(400, 120)">
        <circle r="50" fill="rgba(255,255,255,0.2)"/>
        <path d="M0,-35 L8,-15 L30,-15 L12,0 L18,25 L0,12 L-18,25 L-12,0 L-30,-15 L-8,-15 Z"
              fill="white" opacity="0.9"/>
    </g>
    <text x="400" y="220" font-family="Arial, sans-serif" font-size="36" font-weight="bold"
          fill="white" text-anchor="middle">{safe_destination}</text>
    <text x="400" y="260" font-family="Arial, sans-serif" font-size="18"
          fill="rgba(255,255,255,0.8)" text-anchor="middle">Complete Travel Guide</text>
    <rect x="350" y="280" width="100" height="3" fill="rgba(255,255,255,0.5)" rx="1.5"/>
</svg>"""

    def _create_location_placeholder(self, location: str) -> str:
        """Create a location placeholder SVG."""
        safe_location = self._escape_html(location)
        # Generate a consistent color based on location name
        color_index = hash(location) % 5
        colors = ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe"]
        color = colors[color_index]

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 150">
    <defs>
        <linearGradient id="locGrad{color_index}" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{self.PLACEHOLDER_COLORS['location']};stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="200" height="150" fill="url(#locGrad{color_index})" rx="8"/>
    <g transform="translate(100, 55)">
        <circle r="25" fill="rgba(255,255,255,0.2)"/>
        <path d="M0,-15 C-8,-15 -15,-8 -15,0 C-15,12 0,20 0,20 C0,20 15,12 15,0 C15,-8 8,-15 0,-15"
              fill="white" opacity="0.9"/>
        <circle cx="0" cy="-2" r="5" fill="{color}"/>
    </g>
    <text x="100" y="115" font-family="Arial, sans-serif" font-size="12" font-weight="bold"
          fill="white" text-anchor="middle">{safe_location[:25]}</text>
</svg>"""

    def _create_map_placeholder(self, locations: list[str], title: str) -> str:
        """Create a route map placeholder SVG with location markers."""
        safe_title = self._escape_html(title)
        markers_svg = []

        # Generate marker positions in a route pattern
        num_locations = len(locations)
        if num_locations > 0:
            # Create a winding path through the map
            for i, loc in enumerate(locations[:8]):  # Limit to 8 markers
                safe_loc = self._escape_html(loc[:20])
                # Position markers along a curved path
                x = 100 + (i % 4) * 150 + (i // 4) * 75
                y = 80 + (i // 4) * 120 + ((i % 2) * 30)
                marker_num = i + 1

                markers_svg.append(
                    f"""
                    <g transform="translate({x}, {y})">
                        <circle r="15" fill="#667eea" stroke="white" stroke-width="2"/>
                        <text y="5" font-family="Arial" font-size="12" font-weight="bold"
                              fill="white" text-anchor="middle">{marker_num}</text>
                        <text y="30" font-family="Arial" font-size="9"
                              fill="#333" text-anchor="middle">{safe_loc}</text>
                    </g>"""
                )

            # Draw connecting lines
            if num_locations > 1:
                path_points = []
                for i in range(min(num_locations, 8)):
                    x = 100 + (i % 4) * 150 + (i // 4) * 75
                    y = 80 + (i // 4) * 120 + ((i % 2) * 30)
                    path_points.append(f"{x},{y}")
                path_d = "M " + " L ".join(path_points)
                markers_svg.insert(
                    0,
                    f"""<path d="{path_d}" fill="none" stroke="#667eea"
                               stroke-width="3" stroke-dasharray="8,4" opacity="0.6"/>""",
                )

        markers_content = "".join(markers_svg)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 350">
    <defs>
        <pattern id="mapGrid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#e2e8f0" stroke-width="1"/>
        </pattern>
    </defs>
    <rect width="700" height="350" fill="#f7fafc"/>
    <rect width="700" height="350" fill="url(#mapGrid)"/>
    <text x="350" y="30" font-family="Arial, sans-serif" font-size="16" font-weight="bold"
          fill="#2d3748" text-anchor="middle">{safe_title}</text>
    {markers_content}
    <rect x="10" y="310" width="150" height="30" fill="white" stroke="#e2e8f0" rx="4"/>
    <text x="85" y="330" font-family="Arial" font-size="10"
          fill="#718096" text-anchor="middle">📍 {num_locations} Locations</text>
</svg>"""

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters in text."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )

    def _svg_to_base64(self, svg_content: str) -> str:
        """Convert SVG content to base64 encoded string."""
        return base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")

    def get_data_uri(self, image_data: ImageData) -> str:
        """Convert ImageData to a data URI for embedding in HTML.

        Args:
            image_data: ImageData object to convert

        Returns:
            Data URI string for use in HTML img src attribute
        """
        if image_data.is_base64:
            return f"data:{image_data.mime_type};base64,{image_data.data}"
        return image_data.data
