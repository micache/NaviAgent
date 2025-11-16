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
from agno.db import PostgresDb
from agno.memory import MemoryManager
from agno.models.openai import OpenAIChat

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import model_settings, settings
from models.schemas import WeatherAgentInput, WeatherAgentOutput
from tools.search_tool import search_tools


def create_weather_agent(
    agent_name: str = "weather",
    db: PostgresDb = None,
    user_id: str = None,
    enable_memory: bool = True,
) -> Agent:
    """
    Create a Weather Agent with structured input/output, search tools, and database support.

    Args:
        agent_name: Name of agent for model configuration (default: "weather")
        db: PostgreSQL database instance for session/memory storage
        user_id: Optional default user ID for memory management
        enable_memory: Enable user memory management (default: True)

    Returns:
        Agent configured with WeatherAgentInput and WeatherAgentOutput schemas
    """
    # Create model from centralized configuration
    model = model_settings.create_model_for_agno(agent_name)

    # Create memory manager with cheaper model if database is provided
    memory_manager = None
    if db and enable_memory:
        memory_manager = MemoryManager(
            db=db,
            model=model_settings.create_model_for_agno("memory"),
        )

    return Agent(
        name="WeatherAgent",
        model=model,
        db=db,
        user_id=user_id,
        memory_manager=memory_manager,
        add_history_to_context=True if db else False,
        num_history_runs=5,
        read_chat_history=True if db else False,
        enable_user_memories=enable_memory if db else False,
        enable_session_summaries=True if db else False,
        store_media=False,
        tools=[search_tools],
        add_datetime_to_context=True,
        instructions=[
            "You are the Weather Context Specialist for a travel planning pipeline.",
            "",
            "**Role**: Provide highly accurate weather, season, and event context that all other agents will use for planning.",
            "",
            "**Input Context**: You will receive the following structured input:",
            "  - destination: str",
            "  - departure_date: date (YYYY-MM-DD)",
            "  - duration_days: int",
            "",
            "**Internal Reasoning Steps (Your first actions)**:",
            "1. Calculate the 'end_date' (departure_date + duration_days).",
            "2. Compare the 'departure_date' to today's date to determine data type (Forecast vs. Historical).",
            "",
            "**Search & Accuracy Strategy (2-3 searches maximum)**:",
            "Your search strategy DEPENDS on the 'departure_date':",
            "",
            "1. **Analyze Departure Date (CRITICAL)**:",
            "   - **If 'departure_date' is within the next 10-14 days**: Execute a search for a specific '10-day weather forecast {destination} {departure_date}'. This is a short-term FORECAST.",
            "   - **If 'departure_date' is far in the future (15+ days away)**: Execute a search for 'average weather in {destination} in {month}' OR 'historical weather {destination} {month}'. This is a long-term AVERAGE.",
            "",
            "2. **Search for Events**:",
            "   - Search for '{destination} major festivals or events between {departure_date} and {end_date}'.",
            "",
            "**Output Requirements**:",
            "   - temperature_range: Specific range. MUST note data type. e.g., '25-32°C (Forecast)' or 'Avg. 15-20°C (Historical)'.",
            "   - season: e.g., 'Summer', 'Monsoon', 'Winter', 'Dry season', 'Peak Tourist Season', 'Shoulder Season'.",
            "   - weather_conditions: 2-3 sentences describing conditions for the *entire duration* (e.g., 'Expect sunny mornings with high chance of afternoon thunderstorms. Humidity is very high.' or 'Typically cool and overcast, with occasional light rain.')",
            "   - packing_recommendations: 5-6 specific items based *directly* on the weather (e.g., 'Light rain jacket', 'Breathable cotton shirts', 'Umbrella', 'Sunscreen SPF 50+').",
            "   - seasonal_events: Top 3-5 major festivals/events *during the travel dates*. If none, state 'No major seasonal events found'.",
            "   - weather_impact_summary: 2-3 sentences on how this weather impacts travel (e.g., 'Good for beach activities, but plan indoor options for rainy afternoons. This is peak season, so expect crowds.')",
            "",
            "**Downstream Agent Dependencies**:",
            "   - **Itinerary Agent**: Needs season/weather (rainy/sunny) to plan outdoor vs. indoor activities.",
            "   - **Advisory Agent**: Needs *specific* warnings (e.g., 'Monsoon season', 'Heatwave warning', 'Typhoon risk') for safety tips.",
            "   - **Budget Agent**: Needs 'season' (peak/off-peak/shoulder) as it directly affects hotel/flight prices.",
            "",
            "Focus on ACTIONABLE, specific info. Skip all generic advice.",
        ],
        input_schema=WeatherAgentInput,
        output_schema=WeatherAgentOutput,
        markdown=True,
        debug_mode=False,
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
