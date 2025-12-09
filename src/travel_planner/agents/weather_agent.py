"""
Weather Agent
Provides weather forecasts, seasonal information, and event details using search tools
"""

import sys
from datetime import date, timedelta
from pathlib import Path

from agno.agent import Agent
from agno.db import PostgresDb
from agno.memory import MemoryManager

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import model_settings
from models.schemas import WeatherAgentInput, WeatherAgentOutput
from tools.external_api_tools import create_weather_tools
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

    # Create weather tools
    weather_tools = create_weather_tools()

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
        tools=[
            weather_tools,
            search_tools,
        ],  # Weather API first, then fallback to search
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
            "**Available Tools (Use in Priority Order)**:",
            "1. **Weather API Tools (CALL ONLY ONCE)**:",
            "   • get_weather_forecast(location, days, include_alerts): Real-time forecast (1-10 days)",
            "     - Returns: Daily temperature, conditions, rain chance, UV, sunrise/sunset",
            "     - Use for trips within next 10 days",
            "     - IMPORTANT: Call ONCE and use the result. DO NOT call multiple times!",
            "   • get_current_weather(location): Current conditions",
            "     - Returns: Current temp, feels like, humidity, wind, UV",
            "",
            "2. **Search Tool (FALLBACK if API fails)**:",
            "   • duckduckgo_search(query, max_results): Web search",
            "     - Use ONLY if API returns error or no data",
            "     - Query examples: '{destination} weather in {month}', '{destination} climate {month}'",
            "",
            "**Tool Selection Logic**:",
            "",
            "**Step 1: Calculate Trip Dates**",
            "   - end_date = departure_date + duration_days",
            "   - days_until_departure = departure_date - today",
            "",
            "**Step 2: Choose Tool Based on Timeline (CALL ONCE ONLY)**",
            "",
            "   A) **Trip starts within 10 days** (departure_date <= today + 10 days):",
            "      → Call ONCE: get_weather_forecast('{destination}', days=duration_days, include_alerts=True)",
            "      → This gives you EXACT forecast for departure_date through end_date",
            "      → Use the returned data to fill ALL output fields",
            "      → DO NOT call the tool again!",
            "      → If API fails/returns error → FALLBACK to duckduckgo_search() ONCE",
            "",
            "   B) **Trip starts 11+ days from now** (API forecast not available):",
            "      → Use general knowledge + duckduckgo_search() ONCE for:",
            "        - 'average weather {destination} in {month}'",
            "        - '{destination} climate {month}'",
            "        - '{destination} typical weather {season}'",
            "",
            "**Step 3: Fallback Strategy (If Needed)**",
            "   If get_weather_forecast() returns:",
            "   - 'Error' message → Use duckduckgo_search() ONCE",
            "   - 'Timeout' → Use duckduckgo_search() ONCE",
            "   - Empty/no data → Use duckduckgo_search() ONCE",
            "",
            "**CRITICAL RULE: ONE TOOL CALL PER TASK**",
            "   - Call get_weather_forecast() ONCE → Use result for all fields",
            "   - If that fails, call duckduckgo_search() ONCE → Use result",
            "   - DO NOT call same tool multiple times",
            "   - DO NOT call multiple tools if one succeeds",
            "",
            "**Output Requirements** (MUST provide all fields):",
            "   - temperature_range: Specific range + data type",
            "     Examples: '25-32°C (API Forecast)', '15-20°C (Historical Average)', '28-35°C (Seasonal Average)'",
            "   ",
            "   - season: Tourist season + climate season",
            "     Examples: 'Summer, Monsoon Season', 'Winter, Dry Season', 'Peak Tourist Season, Spring'",
            "   ",
            "   - weather_conditions: 2-3 sentences for ENTIRE duration (departure_date to end_date)",
            "     Must specify: typical conditions, rain probability, humidity level",
            "   ",
            "   - packing_recommendations: 5-6 specific items based on weather",
            "     Examples: 'Waterproof jacket', 'Sunscreen SPF 50+', 'Light breathable clothes', 'Umbrella'",
            "   ",
            "   - seasonal_events: 3-5 major events DURING travel dates (departure_date to end_date)",
            "     If none found: state 'No major seasonal events found for these dates'",
            "   ",
            "   - weather_impact_summary: 2-3 sentences on travel impact",
            "     Must cover: activity planning, clothing needs, crowd levels",
            "",
            "**Downstream Agent Dependencies**:",
            "   - **Itinerary Agent**: Needs weather (rainy/sunny) to plan outdoor vs. indoor activities",
            "   - **Advisory Agent**: Needs warnings (monsoon/typhoon/heatwave) for safety tips",
            "   - **Budget Agent**: Needs season (peak/off-peak) for pricing",
            "",
            "**Critical Rules**:",
            "Call weather API ONCE if trip is within 10 days",
            "Use the API result to fill ALL output fields",
            "DO NOT call the same tool multiple times",
            "If API fails, switch to search tool ONCE",
            "Weather forecast covers EXACT dates: departure_date to (departure_date + duration_days)",
            "Provide specific, actionable info - no generic advice",
            "",
            "=" * 80,
            "🇻🇳 VIETNAMESE OUTPUT REQUIREMENT",
            "=" * 80,
            "ALL text in your output MUST be in VIETNAMESE:",
            "  • season: Tiếng Việt (e.g., 'Mùa Đông', 'Mùa Mưa', 'Mùa Cao Điểm')",
            "  • weather_summary: Tiếng Việt",
            "  • packing_recommendations: Tiếng Việt",
            "  • seasonal_events: Tiếng Việt (event names can stay original + Vietnamese description)",
            "  • best_activities: Tiếng Việt",
            "=" * 80,
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
        destination=destination,
        departure_date=departure_date,
        duration_days=duration_days,
    )

    # Run agent with structured input
    response = await agent.arun(input=agent_input)

    # Response.content will be a WeatherAgentOutput object
    if isinstance(response.content, WeatherAgentOutput):
        print(f"[WeatherAgent] ✓ Season: {response.content.season}")
        print(
            f"[WeatherAgent] ✓ Weather summary: {response.content.weather_summary[:100]}..."
        )

        # Check if data is from API or LLM by inspecting agent's run messages
        run_response = str(
            response.model_dump() if hasattr(response, "model_dump") else response
        )
        api_success = "WeatherAPI]" in run_response and (
            "SUCCESS" in run_response or "Weather Forecast" in run_response
        )

        if api_success:
            print("   📡 DATA SOURCE: External API (WeatherAPI.com)")
        else:
            print("   🤖 DATA SOURCE: LLM Generation (API failed or not called)")

        if response.content.daily_forecasts:
            print(
                f"[WeatherAgent] ✓ Daily forecasts: {len(response.content.daily_forecasts)} days"
            )
        if response.content.seasonal_events:
            print(
                f"[WeatherAgent] ✓ Found {len(response.content.seasonal_events)} seasonal events"
            )
        if response.content.best_activities:
            print(
                f"[WeatherAgent] ✓ Best activities: {len(response.content.best_activities)} suggestions"
            )
        return response.content
    else:
        print(f"[WeatherAgent] ⚠ Unexpected response type: {type(response.content)}")
        raise ValueError(f"Expected WeatherAgentOutput, got {type(response.content)}")
