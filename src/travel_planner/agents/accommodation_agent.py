"""
Accommodation Agent
Specialized agent for finding hotels, hostels, homestays, and other accommodations
Uses Agno's structured input/output
"""

import sys
from pathlib import Path

from agno.agent import Agent
from agno.db import PostgresDb
from agno.memory import MemoryManager

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import model_settings
from models.schemas import AccommodationAgentInput, AccommodationAgentOutput
from tools.external_api_tools import create_hotel_tools
from tools.search_tool import search_tools


def create_accommodation_agent(
    agent_name: str = "accommodation",
    db: PostgresDb = None,
    user_id: str = None,
    enable_memory: bool = True,
) -> Agent:
    """
    Create an Accommodation Agent with structured input/output and database support.

    Args:
        agent_name: Name of agent for model configuration (default: "accommodation")
        db: PostgreSQL database instance for session/memory storage
        user_id: Optional default user ID for memory management
        enable_memory: Enable user memory management (default: True)

    Returns:
        Agent configured with AccommodationAgentInput and AccommodationAgentOutput schemas
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

    # Create hotel tools
    hotel_tools = create_hotel_tools()

    return Agent(
        name="AccommodationAgent",
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
        tools=[hotel_tools, search_tools],
        add_datetime_to_context=True,
        instructions=[
            "You are the Accommodation Specialist for the travel planning pipeline.",
            "",
            "**GOAL**: Provide 4-6 diverse, realistic accommodation options based on input data and strict budget alignment.",
            "",
            "**Input Context**: You will receive:",
            "  - destination: str (e.g., 'Tokyo', 'Bangkok')",
            "  - departure_date: date (check-in date)",
            "  - duration_nights: int (number of nights)",
            "  - budget_per_night: float (allocated budget per night)",
            "  - num_travelers: int",
            "  - travel_style: str ('budget', 'luxury', 'self_guided', 'adventure')",
            "  - preferences: str (customer notes + MAY CONTAIN PRE-FETCHED API DATA)",
            "",
            "### 1. EXECUTION WORKFLOW (DATA SOURCING)",
            "Follow the steps below to start:",
            "",
            "**Priority 1: CHECK 'preferences' (Pre-fetched Data)**",
            "   - Scan `preferences` for '🔥 REAL-TIME HOTEL DATA'.",
            "   - If found: Parse text to extract hotel names, prices, ratings.",
            "   - Proceed directly to 'DATA PROCESSING & FILTERING'.",
            "",
            "**Priority 2: Call API Tools (If no pre-fetched data)**",
            "   - Calculate check-out date (check-in + duration).",
            "   - Parse raw API results.",
            "   - Proceed to 'DATA PROCESSING & FILTERING'.",
            "",
            "**Priority 3: Web Search Fallback**",
            "   - Call `duckduckgo_search` query: '{destination} hotels {travel_style} prices {year}'.",
            "   - Estimate prices based on search snippets.",
            "",
            "**Priority 4: General Knowledge Fallback (Last Resort)**",
            "   - If ALL else fails, generate realistic options based on destination knowledge.",
            "   - **CRITICAL**: Generated prices MUST try to align with `budget_per_night`.",
            "",
            "### 2. DATA PROCESSING & FILTERING (APPLY TO ALL SOURCES)",
            "**Step A: Standardization**",
            "   - Convert ALL prices to **VND** (1 USD ≈ 26,000 VND).",
            "   - Calculate `total_cost` = `price_per_night` * `duration_nights`.",
            "",
            "**Step B: BUDGET & STYLE COMPLIANCE (CRITICAL)**",
            "   - **Rule 1 (Budget)**: Filter for hotels where `price_per_night` <= `budget_per_night`.",
            "   - **Rule 2 (Tolerance)**: Include options up to **15% over budget** ONLY IF Rating >= 4.5 or Location is 'Central'."
            "   - **Rule 3 (Impossible Budget)**: If NO hotels fit the budget, return the CHEAPEST available and warn in `booking_tips`.",
            "   - **Rule 4 (Style Matching)**:",
            "       - 'luxury': Priority Rating >= 4.5, 4-5 stars.",
            "       - 'budget': Priority Low Price + Rating >= 3.8.",
            "       - 'self_guided/adventure': Priority Location (near Metro/Center).",
            "",
            "### 3. OUTPUT SCHEMA (STRICT JSON)",
            "You must return a valid JSON object matching the `AccommodationAgentOutput` schema.",
            "Important: `recommendations` is a list of `AccommodationOption` objects. The structure MUST be:",
            "",
            "{",
            '  "recommendations": [',
            "    {",
            '      "name": "String (Hotel Name)",',
            '      "type": "String (Hotel, Hostel, Resort, Homestay)",',
            '      "area": "String (Tiếng Việt - e.g. Quận 1, Gần tháp Tokyo)",',
            '      "price_per_night": 1500000, // FLOAT in VND',
            '      "total_cost": 4500000, // FLOAT (price * duration)',
            '      "rating": 4.5, // FLOAT (0.0 to 5.0)',
            '      "distance_to_center": "String (e.g. 2km)",',
            '      "amenities": ["String (Tiếng Việt)", "String"],',
            '      "booking_platforms": ["String"],',
            '      "notes": "String (Tiếng Việt - Mention budget/style fit)"',
            "    }",
            "  ],",
            '  "best_areas": ["String (Area 1 description)", "String (Area 2)"],',
            '  "average_price_per_night": 0.0, // FLOAT',
            '  "total_estimated_cost": 0.0, // FLOAT (Total trip accommodation cost)',
            '  "booking_tips": ["String (Tiếng Việt)"]',
            "}",
            "",
            "### 4. VIETNAMESE LANGUAGE REQUIREMENT 🇻🇳",
            "- Apart from Hotel names, ALL text output (area, amenities, notes, tips) must be in natural **VIETNAMESE**.",
        ],
        input_schema=AccommodationAgentInput,
        output_schema=AccommodationAgentOutput,
        markdown=True,
        debug_mode=False,
    )


async def run_accommodation_agent(
    agent: Agent,
    destination: str,
    departure_date,
    duration: int,
    budget: float,
    num_travelers: int,
    travel_style: str,
    preferences: str = "",
) -> AccommodationAgentOutput:
    """
    Run the accommodation agent with structured input and output.

    Args:
        agent: The configured Accommodation Agent
        destination: Destination location/city
        departure_date: Check-in date
        duration: Number of nights
        budget: Total budget in VND
        num_travelers: Number of travelers
        travel_style: Travel style (luxury, budget, self_guided, etc.)
        preferences: User preferences for accommodation

    Returns:
        AccommodationAgentOutput with structured accommodation recommendations
    """
    print(f"[AccommodationAgent] Searching accommodations in {destination}")
    print(
        f"[AccommodationAgent] Check-in: {departure_date}, Nights: {duration}, Budget: {budget:,.0f} VND"
    )
    print(f"[AccommodationAgent] Travelers: {num_travelers}, Style: {travel_style}")

    # Create structured input
    agent_input = AccommodationAgentInput(
        destination=destination,
        departure_date=departure_date,
        duration_nights=duration,
        budget_per_night=budget,
        num_travelers=num_travelers,
        travel_style=travel_style,
        preferences=preferences,
    )

    # Run agent with structured input
    response = await agent.arun(input=agent_input)

    # Response.content will be an AccommodationAgentOutput object
    if isinstance(response.content, AccommodationAgentOutput):
        num_hotels = len(response.content.recommendations)
        print(f"[AccommodationAgent] ✓ Found {num_hotels} accommodation options")

        # Check if data is from API or LLM by inspecting agent's run messages
        if num_hotels > 0:
            # Look for API success markers in the agent's execution
            run_response = str(
                response.model_dump() if hasattr(response, "model_dump") else response
            )
            api_success = "TripAdvisor API] SUCCESS" in run_response
            if api_success:
                print(f"   📡 DATA SOURCE: External API (TripAdvisor)")
            else:
                print(f"   🤖 DATA SOURCE: LLM Generation (API failed or not called)")

        print(
            f"[AccommodationAgent] ✓ Average price: {response.content.average_price_per_night:,.0f} VND/night"
        )
        return response.content
    else:
        print(
            f"[AccommodationAgent] ⚠ Unexpected response type: {type(response.content)}"
        )
        raise ValueError(
            f"Expected AccommodationAgentOutput, got {type(response.content)}"
        )
