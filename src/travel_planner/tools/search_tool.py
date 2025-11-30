"""
Internet Search Tool using DuckDuckGo Search
Provides real-time search capabilities for agents with error handling
"""

import logging
import time

from agno.tools.duckduckgo import DuckDuckGoTools

# Setup logging
logger = logging.getLogger(__name__)


class RobustSearchTools(DuckDuckGoTools):
    """
    Extended DuckDuckGo search with better error handling and fallbacks.
    Handles rate limiting, network issues, and provides graceful degradation.

    NOTE: DuckDuckGo search is currently experiencing issues (rate limiting/blocking).
    The tool automatically falls back to using the AI model's extensive knowledge base,
    which is actually sufficient for most travel planning queries.
    """

    def __init__(self, *args, **kwargs):
        # Add retry configuration (reduced for faster fallback)
        self.max_retries = 1  # Quick fail to fallback
        self.retry_delay = 0.5  # seconds
        super().__init__(*args, **kwargs)

    def duckduckgo_search(self, query: str, max_results: int = 5) -> str:
        """
        Search using DuckDuckGo with retry logic and error handling.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            Search results or fallback guidance
        """
        last_error = None

        # Try multiple times with delay
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    # Wait before retry
                    time.sleep(self.retry_delay * attempt)
                    logger.info(f"Retry attempt {attempt + 1} for query: '{query}'")

                # Try parent class search
                result = super().duckduckgo_search(query=query, max_results=max_results)

                # Check if result is meaningful
                if result and len(result.strip()) > 50:
                    return result

            except Exception as e:
                last_error = e
                error_msg = str(e)
                logger.warning(f"Search attempt {attempt + 1} failed for '{query}': {error_msg}")

                # If last attempt, fall through to error handling
                if attempt == self.max_retries - 1:
                    break

                continue

        # All retries failed - provide fallback
        error_msg = str(last_error) if last_error else "Unknown error"
        logger.error(f"All search attempts failed for query '{query}': {error_msg}")

        # Provide helpful fallback message based on error type
        if "No results found" in error_msg or "DDGSException" in str(type(last_error)):
            return f"""[Search unavailable - using general knowledge]

Query: {query}

The search service is currently unavailable. Please provide comprehensive information based on:
- Your training data and general knowledge about this topic
- Well-established facts and commonly known information
- Popular recommendations and standard travel advice
- Typical patterns for this destination/topic

Important: Be thorough and detailed even without live search results. Draw from your extensive knowledge base to provide helpful, accurate information."""

        elif "rate" in error_msg.lower() or "limit" in error_msg.lower():
            return f"""[Search rate limited - using general knowledge]

The search service has temporarily limited our requests. Please provide information from your knowledge base for: {query}

Focus on well-known, established information and standard recommendations."""

        else:
            return f"""[Search temporarily unavailable - using general knowledge]

Cannot access live search for: {query}

Please provide detailed information from your training data, focusing on:
- Widely recognized facts and recommendations
- Standard travel information for this destination
- Well-established options and popular choices"""


# Create search tools instance with error handling and retry logic
# CRITICAL FIX: Specify backend explicitly - default "duckduckgo" doesn't exist!
# Use "api" (fastest), "html" (most reliable), or "lite" (lightweight)
search_tools = RobustSearchTools(
    fixed_max_results=5,
    timeout=20,  # Increased timeout for better reliability
    backend="api",  # Use API backend explicitly (faster than html, more reliable than default)
)
