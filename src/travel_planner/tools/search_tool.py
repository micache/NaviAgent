"""
Internet Search Tool using Google Search
Provides real-time search capabilities for agents
"""

from agno.tools.googlesearch import GoogleSearchTools

# Create Google Search tools instance with configuration
search_tools = GoogleSearchTools(
    fixed_max_results=10,  # Limit results
    fixed_language="en",  # Default to English
    timeout=10,  # 10 seconds timeout
    enable_google_search=True,
)
