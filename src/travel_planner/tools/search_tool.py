"""
Internet Search Tool using DuckDuckGo Search
Provides real-time search capabilities for agents
"""

from agno.tools.duckduckgo import DuckDuckGoTools

# Create DuckDuckGo Search tools instance with configuration
search_tools = DuckDuckGoTools(
    fixed_max_results=5,        # Reduced from 10 to 5 for faster responses
    timeout=10,                 # 10 seconds timeout
)
