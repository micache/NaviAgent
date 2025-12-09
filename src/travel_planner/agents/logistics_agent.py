"""
Logistics Agent - Specialized for Flight Tickets
Provides detailed flight information with pricing, airlines, benefits using Agno's structured input/output
"""

import sys
from pathlib import Path

from agno.agent import Agent
from agno.db import PostgresDb
from agno.memory import MemoryManager

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import model_settings
from models.schemas import LogisticsAgentInput, LogisticsAgentOutput
from tools.external_api_tools import create_flight_tools
from tools.search_tool import search_tools


def create_logistics_agent(
    agent_name: str = "logistics",
    db: PostgresDb = None,
    user_id: str = None,
    enable_memory: bool = True,
) -> Agent:
    """
    Create a Logistics Agent specialized for flight tickets with structured input/output and database support.

    Args:
        agent_name: Name of agent for model configuration (default: "logistics")
        db: PostgreSQL database instance for session/memory storage
        user_id: Optional default user ID for memory management
        enable_memory: Enable user memory management (default: True)

    Returns:
        Agent configured with LogisticsAgentInput and LogisticsAgentOutput schemas
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

    # Create flight tools
    flight_tools = create_flight_tools()

    return Agent(
        name="LogisticsAgent",
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
        tools=[flight_tools, search_tools],  # Flight API first, then fallback to search
        add_datetime_to_context=True,
        instructions=[
            "You are the Flight Logistics Specialist for a travel planning pipeline.",
            "**GOAL**: Provide 3-5 diverse, realistic flight options based on input data and strict budget constraints.",
            "",
            "**Input Context**: You will receive:",
            "  - departure_point: str (e.g., 'Hanoi', 'Ho Chi Minh City')",
            "  - destination: str (e.g., 'Tokyo', 'Bangkok')",
            "  - departure_date: date (YYYY-MM-DD)",
            "  - return_date: date (YYYY-MM-DD)",
            "  - num_travelers: int",
            "  - budget_per_person: float (allocated budget per person for round-trip)",
            "  - preferences: str (customer notes + MAY CONTAIN PRE-FETCHED API DATA)",
            "",
            "### 1. EXECUTION WORKFLOW (DATA SOURCING)",
            "Follow the steps below to start:",
            "**Priority 1: CHECK 'preferences' INPUT FIRST**",
            '   - Scan `preferences` for text like "🔥 REAL-TIME FLIGHT DATA FROM API".',
            "   - If found: PARSE this text directly. These are REAL prices.",
            "   - Proceed directly to 'DATA PROCESSING & FILTERING'.",
            "",
            "**Priority 2: Call API Tools (if no pre-fetched data)**",
            "   - If 'preferences' does NOT contain API data:",
            "   - Call `search_flights(departure, destination, date)` for outbound.",
            "   - Call `search_flights(destination, departure, date)` for return.",
            "   - Parse results and create options with REAL prices",
            "   - Proceed directly to 'DATA PROCESSING & FILTERING'.",
            "",
            "**Priority 3: Web Search (if API fails/returns empty)**",
            "   - If search_flights() returns error or 'No flights found':",
            "   - Call duckduckgo_search() ONCE: '{departure_point} to {destination} flight prices {year}'",
            "   - Use search results to inform realistic pricing",
            "   - Proceed directly to 'DATA PROCESSING & FILTERING'.",
            "",
            "**Priority 4: General Knowledge (last resort)**",
            "   - If all tools fail or no data available:",
            "   - Use aviation knowledge to create realistic options:",
            "     - Known airlines on route (VietJet, Vietnam Airlines, ANA, etc.)",
            "     - Typical flight duration based on distance",
            "     - Realistic seasonal pricing for route/class",
            "     - Common departure times (morning, afternoon, evening)",
            "   - **CRITICAL**: Generated prices MUST try to align with `budget_per_person` if realistic.",
            "",
            "### 2. DATA PROCESSING & FILTERING (APPLY TO ALL SOURCES)",
            "**Step A: Standardization**",
            "   - Convert ALL prices to **VND** (1 USD ≈ 26,500 VND).",
            "   - Ensure dates/times are formatted clearly.",
            "",
            "**Step B: BUDGET COMPLIANCE (CRITICAL)**",
            "   - **Rule 1**: Filter for flights where `price_per_person` <= `budget_per_person`.",
            "   - **Rule 2 (Tolerance)**: Include options up to **15% over budget** ONLY IF they offer better value (Direct vs Stop).",
            "   - **Rule 3 (Impossible Budget)**: If NO flights fit the budget, return the CHEAPEST available options.",
            "   - **Rule 4 (Note)**: If an option is over budget, add a specific note in the `notes` field.",
            "",
            "### 3. OUTPUT SCHEMA (STRICT JSON)",
            "You must return a valid JSON object matching the `LogisticsAgentOutput` schema.",
            "Important: `flight_options` is a list of `FlightOption` objects. The structure MUST be:",
            "",
            "{" '  "flight_options": [',
            "    {",
            '      "airline": "String (e.g., Vietnam Airlines)",',
            '      "flight_type": "String (Bay thẳng / 1 điểm dừng)",',
            '      "departure_time": "String (e.g., 08:30)",',
            '      "arrival_time": "String",',
            '      "duration": "String (e.g., 2h 30p)",',
            '      "price_per_person": 5000000, // FLOAT or INT in VND',
            '      "cabin_class": "String (Phổ thông / Thương gia)",',
            '      "benefits": ["String"],',
            '      "booking_platforms": ["String"],',
            '      "notes": "String (Note about budget fit)"',
            "    }",
            "  ],",
            '  "recommended_flight": "String (Name of best option or null)",',
            '  "average_price": 0.0, // FLOAT (Calculate average of price_per_person)',
            '  "booking_tips": ["String", "String"],',
            '  "visa_requirements": "String (or null)"',
            "}",
            "### 4. VIETNAMESE LANGUAGE REQUIREMENT 🇻🇳",
            "- Apart from Airline names/Codes, ALL text output (notes, tips, flight types) must be in natural **VIETNAMESE**.",
        ],
        input_schema=LogisticsAgentInput,
        output_schema=LogisticsAgentOutput,
        markdown=True,
        debug_mode=False,
    )


async def run_logistics_agent(
    agent: Agent,
    departure_point: str,
    destination: str,
    departure_date,
    return_date,
    num_travelers: int,
    budget_per_person: float,
    preferences: str = "",
) -> LogisticsAgentOutput:
    """
    Run the logistics agent with structured input and output - specialized for flights.

    Args:
        agent: The configured Logistics Agent
        departure_point: Starting location/city/airport
        destination: Destination location/city/airport
        departure_date: Departure date
        return_date: Return date
        num_travelers: Number of passengers
        budget_per_person: Budget per person for round-trip flight in VND
        preferences: Flight preferences (direct, business class, etc.)

    Returns:
        LogisticsAgentOutput with structured flight ticket information
    """
    print(f"[LogisticsAgent] Searching flights from {departure_point} to {destination}")
    print(
        f"[LogisticsAgent] Departure: {departure_date}, Return: {return_date}, Travelers: {num_travelers}"
    )
    print(f"[LogisticsAgent] Budget per person: {budget_per_person:,.0f} VND")

    # Create structured input
    agent_input = LogisticsAgentInput(
        departure_point=departure_point,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        num_travelers=num_travelers,
        budget_per_person=budget_per_person,
        preferences=preferences,
    )

    # Run agent with structured input
    response = await agent.arun(input=agent_input)

    # Response.content will be a LogisticsAgentOutput object
    if isinstance(response.content, LogisticsAgentOutput):
        num_flights = len(response.content.flight_options)
        print(f"[LogisticsAgent] ✓ Found {num_flights} flight options")

        # Check if data is from API or LLM by inspecting agent's run messages
        if num_flights > 0:
            # Look for API success markers in the agent's execution
            run_response = str(
                response.model_dump() if hasattr(response, "model_dump") else response
            )
            api_success = "Booking.com API] SUCCESS" in run_response
            if api_success:
                print(f"   📡 DATA SOURCE: External API (Booking.com)")
            else:
                print(f"   🤖 DATA SOURCE: LLM Generation (API failed or not called)")

        print(
            f"[LogisticsAgent] ✓ Average price: {response.content.average_price:,.0f} VND/person"
        )
        if response.content.recommended_flight:
            print(
                f"[LogisticsAgent] ✓ Recommended: {response.content.recommended_flight}"
            )
        return response.content
    else:
        print(f"[LogisticsAgent] ⚠ Unexpected response type: {type(response.content)}")
        raise ValueError(f"Expected LogisticsAgentOutput, got {type(response.content)}")
