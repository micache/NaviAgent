"""Enhanced image fetcher with web search capabilities for guidebook generation."""

import base64
import logging
import re
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class ImageData:
    """Container for image data."""

    data: str  # Base64 encoded data or URL
    mime_type: str
    is_base64: bool = True
    caption: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class ImageFetcher:
    """
    Enhanced image fetcher with web search integration.
    
    Provides both placeholder images and real image search capabilities
    for destinations and locations in guidebooks.
    """

    # Default placeholder colors for different content types
    PLACEHOLDER_COLORS = {
        "hero": "#667eea",
        "location": "#764ba2",
        "map": "#4a5568",
        "food": "#f59e0b",
        "activity": "#10b981",
    }

    def __init__(
        self,
        unsplash_api_key: Optional[str] = None,
        enable_web_search: bool = True,
    ):
        """
        Initialize mageFetcher.

        Args:
            unsplash_api_key: Optional Unsplash API key for fetching images
            enable_web_search: Whether to enable web search for images
        """
        self.unsplash_api_key = unsplash_api_key
        self.enable_web_search = enable_web_search
        self._image_cache = {}

    def get_destination_hero(
        self,
        destination: str,
        search_func=None,
    ) -> ImageData:
        """
        Get hero image for destination.

        Args:
            destination: Name of the destination
            search_func: Optional function to perform web search

        Returns:
            ImageData with image URL or placeholder SVG
        """
        # Try to get real image if search is available
        if search_func and self.enable_web_search:
            image_url = self._search_destination_image(destination, search_func)
            if image_url:
                return ImageData(
                    data=image_url,
                    mime_type="image/jpeg",
                    is_base64=False,
                    caption=f"{destination} - Travel Guide",
                    width=1200,
                    height=600,
                )

        # Fallback to placeholder
        svg = self._create_hero_placeholder(destination)
        return ImageData(
            data=self._svg_to_base64(svg),
            mime_type="image/svg+xml",
            is_base64=True,
            caption=f"{destination} - Travel Guide",
        )

    def get_location_image(
        self,
        location: str,
        destination: Optional[str] = None,
        search_func=None,
    ) -> ImageData:
        """
        Get thumbnail image for a specific location.

        Args:
            location: Name of the location
            destination: Optional destination context for better search
            search_func: Optional function to perform web search

        Returns:
            ImageData with image URL or placeholder SVG
        """
        # Create cache key
        cache_key = f"{destination}_{location}" if destination else location

        # Check cache
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        # Try to get real image
        if search_func and self.enable_web_search:
            search_query = f"{location} {destination}" if destination else location
            image_url = self._search_location_image(search_query, search_func)
            if image_url:
                image_data = ImageData(
                    data=image_url,
                    mime_type="image/jpeg",
                    is_base64=False,
                    caption=location,
                    width=400,
                    height=300,
                )
                self._image_cache[cache_key] = image_data
                return image_data

        # Fallback to placeholder
        svg = self._create_location_placeholder(location)
        image_data = ImageData(
            data=self._svg_to_base64(svg),
            mime_type="image/svg+xml",
            is_base64=True,
            caption=location,
        )
        self._image_cache[cache_key] = image_data
        return image_data

    def generate_route_map(
        self,
        locations: List[str],
        destination: str = "Route Map",
    ) -> ImageData:
        """
        Generate a route map visualization.

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

    def _search_destination_image(
        self,
        destination: str,
        search_func,
    ) -> Optional[str]:
        """
        Search for destination hero image using web search.

        Args:
            destination: Destination name to search for
            search_func: Function to perform web search

        Returns:
            Image URL if found, None otherwise
        """
        try:
            # Construct search query for high-quality destination images
            query = f"{destination} travel destination photo"
            logger.debug(f"Searching images for: {query}")

            # Perform search
            results = search_func(query)

            # Extract image URLs from results
            image_url = self._extract_image_from_results(results)
            if image_url:
                logger.info(f"Found image for {destination}: {image_url}")
                return image_url

        except Exception as e:
            logger.warning(f"Failed to search image for {destination}: {e}")

        return None

    def _search_location_image(
        self,
        location: str,
        search_func,
    ) -> Optional[str]:
        """
        Search for location image using web search.

        Args:
            location: Location name to search for
            search_func: Function to perform web search

        Returns:
            Image URL if found, None otherwise
        """
        try:
            query = f"{location} landmark photo"
            logger.debug(f"Searching images for: {query}")

            results = search_func(query)
            image_url = self._extract_image_from_results(results)

            if image_url:
                logger.info(f"Found image for {location}: {image_url}")
                return image_url

        except Exception as e:
            logger.warning(f"Failed to search image for {location}: {e}")

        return None

    def _extract_image_from_results(self, results) -> Optional[str]:
        """
        Extract image URL from search results.

        Args:
            results: Search results from web search

        Returns:
            Image URL if found, None otherwise
        """
        try:
            # Handle different result formats
            if isinstance(results, dict):
                # Check for image results
                if "images" in results and results["images"]:
                    return results["images"][0].get("url")

                # Check for web results with images
                if "web" in results and "results" in results["web"]:
                    for result in results["web"]["results"][:3]:
                        if "thumbnail" in result:
                            return result["thumbnail"].get("src")
                        if "image" in result:
                            return result["image"]

            elif isinstance(results, list):
                # List of results
                for result in results[:3]:
                    if isinstance(result, dict):
                        if "thumbnail" in result:
                            return result["thumbnail"]
                        if "image" in result:
                            return result["image"]
                        if "thumbnail_url" in result:
                            return result["thumbnail_url"]

        except Exception as e:
            logger.debug(f"Error extracting image from results: {e}")

        return None

    def _is_valid_image_url(self, url: str) -> bool:
        """
        Validate if URL is a valid image URL.

        Args:
            url: URL to validate

        Returns:
            True if valid image URL, False otherwise
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False

            # Check file extension
            path = parsed.path.lower()
            image_extensions = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
            return any(path.endswith(ext) for ext in image_extensions)

        except Exception:
            return False

    def _create_hero_placeholder(self, destination: str) -> str:
        """Create a hero placeholder SVG with destination name."""
        safe_destination = self._escape_html(destination)
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600">
    <defs>
        <linearGradient id="heroGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{self.PLACEHOLDER_COLORS['hero']};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{self.PLACEHOLDER_COLORS['location']};stop-opacity:1" />
        </linearGradient>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
        </pattern>
    </defs>
    <rect width="1200" height="600" fill="url(#heroGrad)"/>
    <rect width="1200" height="600" fill="url(#grid)"/>
    <g transform="translate(600, 200)">
        <circle r="80" fill="rgba(255,255,255,0.2)"/>
        <path d="M0,-50 L12,-22 L45,-22 L18,0 L27,38 L0,18 L-27,38 L-18,0 L-45,-22 L-12,-22 Z"
              fill="white" opacity="0.9"/>
    </g>
    <text x="600" y="360" font-family="Arial, sans-serif" font-size="56" font-weight="bold"
          fill="white" text-anchor="middle">{safe_destination}</text>
    <text x="600" y="420" font-family="Arial, sans-serif" font-size="28"
          fill="rgba(255,255,255,0.8)" text-anchor="middle">Complete Travel Guide</text>
    <rect x="500" y="450" width="200" height="4" fill="rgba(255,255,255,0.5)" rx="2"/>
</svg>"""

    def _create_location_placeholder(self, location: str) -> str:
        """Create a location placeholder SVG."""
        safe_location = self._escape_html(location)
        color_index = hash(location) % 5
        colors = ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe"]
        color = colors[color_index]

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
    <defs>
        <linearGradient id="locGrad{color_index}" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{self.PLACEHOLDER_COLORS['location']};stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="400" height="300" fill="url(#locGrad{color_index})" rx="12"/>
    <g transform="translate(200, 110)">
        <circle r="40" fill="rgba(255,255,255,0.2)"/>
        <path d="M0,-25 C-13,-25 -25,-13 -25,0 C-25,20 0,35 0,35 C0,35 25,20 25,0 C25,-13 13,-25 0,-25"
              fill="white" opacity="0.9"/>
        <circle cx="0" cy="-3" r="8" fill="{color}"/>
    </g>
    <text x="200" y="210" font-family="Arial, sans-serif" font-size="20" font-weight="bold"
          fill="white" text-anchor="middle">{safe_location[:30]}</text>
</svg>"""

    def _create_map_placeholder(self, locations: List[str], title: str) -> str:
        """Create a route map placeholder SVG with location markers."""
        safe_title = self._escape_html(title)
        markers_svg = []

        num_locations = len(locations)
        if num_locations > 0:
            for i, loc in enumerate(locations[:8]):
                safe_loc = self._escape_html(loc[:20])
                x = 150 + (i % 4) * 200 + (i // 4) * 100
                y = 120 + (i // 4) * 160 + ((i % 2) * 40)
                marker_num = i + 1

                markers_svg.append(
                    f"""
                    <g transform="translate({x}, {y})">
                        <circle r="20" fill="#667eea" stroke="white" stroke-width="3"/>
                        <text y="7" font-family="Arial" font-size="16" font-weight="bold"
                              fill="white" text-anchor="middle">{marker_num}</text>
                        <text y="45" font-family="Arial" font-size="12"
                              fill="#333" text-anchor="middle">{safe_loc}</text>
                    </g>"""
                )

            if num_locations > 1:
                path_points = []
                for i in range(min(num_locations, 8)):
                    x = 150 + (i % 4) * 200 + (i // 4) * 100
                    y = 120 + (i // 4) * 160 + ((i % 2) * 40)
                    path_points.append(f"{x},{y}")
                path_d = "M " + " L ".join(path_points)
                markers_svg.insert(
                    0,
                    f"""<path d="{path_d}" fill="none" stroke="#667eea"
                               stroke-width="4" stroke-dasharray="10,5" opacity="0.6"/>""",
                )

        markers_content = "".join(markers_svg)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 500">
    <defs>
        <pattern id="mapGrid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#e2e8f0" stroke-width="1"/>
        </pattern>
    </defs>
    <rect width="1000" height="500" fill="#f7fafc"/>
    <rect width="1000" height="500" fill="url(#mapGrid)"/>
    <text x="500" y="50" font-family="Arial, sans-serif" font-size="24" font-weight="bold"
          fill="#2d3748" text-anchor="middle">{safe_title}</text>
    {markers_content}
    <rect x="20" y="450" width="180" height="40" fill="white" stroke="#e2e8f0" rx="6"/>
    <text x="110" y="475" font-family="Arial" font-size="14"
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
        """
        Convert ImageData to a data URI for embedding in HTML.

        Args:
            image_data: ImageData object to convert

        Returns:
            Data URI string or direct URL for use in HTML img src attribute
        """
        if image_data.is_base64:
            return f"data:{image_data.mime_type};base64,{image_data.data}"
        return image_data.data