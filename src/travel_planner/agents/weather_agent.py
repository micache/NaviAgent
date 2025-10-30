"""
Weather Agent
Provides weather forecasts, seasonal information, and event details using search tools
"""

import ssl
import sys
from datetime import date, timedelta
from pathlib import Path

import certifi
import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from models.schemas import WeatherAgentInput, WeatherAgentOutput
from tools.search_tool import search_tools


def create_weather_agent(model: str = "gpt-4o-mini") -> Agent:
    """
    Create a Weather Agent with structured input/output and search tools.

    Args:
        model: OpenAI model ID to use

    Returns:
        Agent configured with WeatherAgentInput and WeatherAgentOutput schemas
    """
    # Create SSL context with certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=120.0)

    return Agent(
        name="WeatherAgent",
        model=OpenAIChat(id=model, api_key=settings.openai_api_key, http_client=http_client),
        tools=[search_tools],
        instructions=[
            "You are a weather and seasonal events specialist with access to real-time search tools.",
            "CRITICAL: Always use search tools to find current date, weather forecasts, and seasonal information.",
            "First, search for the current date and time to understand how far in advance the trip is.",
            "Search for weather forecasts for the destination during the travel period.",
            "Search for festivals, holidays, cultural events, and special occasions during the travel dates.",
            "Search for seasonal characteristics (rainy season, monsoon, peak tourist season, etc.).",
            "Provide temperature ranges in Celsius.",
            "Include precipitation chances if available from search results.",
            "Recommend appropriate clothing and items based on weather conditions.",
            "Suggest activities that are best suited for the expected weather.",
            "Mention any weather-related warnings (typhoon season, extreme heat, etc.).",
            "Be specific about dates when mentioning events or weather patterns.",
            "If exact weather forecasts are not available far in advance, provide historical/seasonal averages.",
            "Always verify information with search tools - never rely on training data alone.",
        ],
        input_schema=WeatherAgentInput,
        output_schema=WeatherAgentOutput,
        markdown=True,
        debug_mode=True,
        add_datetime_to_context=True,
        add_location_to_context=True,
    )


async def run_weather_agent(
    agent: Agent, destination: str, departure_date: date, duration_days: int
) -> WeatherAgentOutput:
    """
    Run the weather agent with structured input and output.

    Args:
        agent: The configured Weather Agent
        destination: Destination location/city
        departure_date: Departure date
        duration_days: Trip duration in days

    Returns:
        WeatherAgentOutput with weather forecasts and seasonal information
    """
    print(f"[WeatherAgent] Getting weather for {destination}")
    print(
        f"[WeatherAgent] Travel period: {departure_date} to {departure_date + timedelta(days=duration_days-1)}"
    )

    # Create structured input
    agent_input = WeatherAgentInput(
        destination=destination, departure_date=departure_date, duration_days=duration_days
    )

    # Run agent with structured input
    response = await agent.arun(input=agent_input)

    # Response.content will be a WeatherAgentOutput object
    if isinstance(response.content, WeatherAgentOutput):
        print(f"[WeatherAgent] ✓ Season: {response.content.season}")
        print(f"[WeatherAgent] ✓ Weather summary: {response.content.weather_summary[:100]}...")
        if response.content.seasonal_events:
            print(f"[WeatherAgent] ✓ Found {len(response.content.seasonal_events)} seasonal events")
        return response.content
    else:
        print(f"[WeatherAgent] ⚠ Unexpected response type: {type(response.content)}")
        raise ValueError(f"Expected WeatherAgentOutput, got {type(response.content)}")
