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
            "",
            "**Role**: Provide 3-5 diverse, realistic flight options for the Itinerary Agent to select from.",
            "",
            "**Input Context**: You will receive:",
            "  - departure_point: str (e.g., 'Hanoi', 'Ho Chi Minh City')",
            "  - destination: str (e.g., 'Tokyo', 'Bangkok')",
            "  - departure_date: date (YYYY-MM-DD)",
            "  - return_date: date (YYYY-MM-DD)",
            "  - num_travelers: int",
            "  - budget_per_person: float (allocated budget per person for round-trip)",
            "  - preferences: str (customer notes)",
            "",
            "**Available Tools (CALL EACH ONCE ONLY)**:",
            "1. **Flight API Tools (TRY FIRST)**:",
            "   • search_flights(origin, destination, departure_date, num_adults, cabin_class, max_results)",
            "     - Returns: Real flight data with prices, times, airlines",
            "     - Use city names or 3-letter codes: HAN, SGN, BKK, NRT, ICN, SIN",
            "     - IMPORTANT: Call ONCE per direction (outbound/return). DO NOT call multiple times!",
            "     - If prices are returned in USD, CONVERT to VND before comparing to budget",
            "     - Use a realistic FX rate (e.g., 1 USD ≈ 25,000 VND) or latest rate from quick search",
            "",
            "2. **Search Tool (FALLBACK if API fails)**:",
            "   • duckduckgo_search(query, max_results): Web search",
            "     - Use ONLY if API returns 'No flights found' or error",
            "     - Call ONCE and use the result",
            "     - Query: '{departure_point} to {destination} flights prices'",
            "",
            "**Tool Selection Logic**:",
            "",
            "**Step 1: Search Outbound Flights (CALL ONCE)**",
            "   → Call ONCE: search_flights(origin=departure_point, destination=destination, ",
            "                                departure_date=departure_date, num_adults=num_travelers, max_results=10)",
            "   → API will auto-convert city names to airport codes",
            "   → Use returned data to create 3-5 diverse options (different times/prices)",
            "   → DO NOT call search_flights again for outbound!",
            "   → Ensure all price_per_person values are in VND (convert from USD if needed)",
            "",
            "**Step 2: Search Return Flights (CALL ONCE)**",
            "   → Call ONCE: search_flights(origin=destination, destination=departure_point, ",
            "                                departure_date=return_date, num_adults=num_travelers, max_results=10)",
            "   → Use returned data to create 3-5 diverse options",
            "   → DO NOT call search_flights again for return!",
            "   → Ensure all price_per_person values are in VND (convert from USD if needed)",
            "",
            "**CRITICAL: TWO TOOL CALLS TOTAL**",
            "   - search_flights() for OUTBOUND → Called ONCE",
            "   - search_flights() for RETURN → Called ONCE",
            "   - Total: 2 API calls maximum",
            "   - If API fails → Use duckduckgo_search() ONCE per direction",
            "",
            "**Step 3: Fallback Strategy (If API Fails)**",
            "   If search_flights() returns error:",
            "   → Use duckduckgo_search() ONCE + general knowledge for:",
            "     - Known airlines on this route",
            "     - Typical flight durations for distance",
            "     - Standard pricing for season/route",
            "",
            "**Flight Option Guidelines by Route**:",
            "",
            "**Hanoi/HCMC → Tokyo/Osaka (Japan)**:",
            "  • Budget: Vietjet, VietJet Air, Jetstar (5-7M VND, 1 stop)",
            "  • Mid-range: Vietnam Airlines, ANA (8-12M VND, direct ~5-6h)",
            "  • Premium: JAL, Singapore Airlines (12-18M VND, direct, better service)",
            "",
            "**Vietnam → Bangkok/Phuket (Thailand)**:",
            "  • Budget: VietJet, Air Asia (2-4M VND, direct ~1-2h)",
            "  • Mid-range: Thai Airways, Vietnam Airlines (4-6M VND, direct)",
            "  • Premium: Bangkok Airways (6-8M VND, premium service)",
            "",
            "**Vietnam → Seoul (Korea)**:",
            "  • Budget: T'way, Jin Air (6-8M VND, direct ~4-5h)",
            "  • Mid-range: Korean Air, Asiana, Vietnam Airlines (8-12M VND, direct)",
            "  • Premium: Korean Air business (15-20M VND)",
            "",
            "**Vietnam → Singapore**:",
            "  • Budget: Jetstar, Scoot (3-5M VND, direct ~2h)",
            "  • Mid-range: Singapore Airlines, Vietnam Airlines (5-7M VND)",
            "",
            "**Output Requirements**: Provide 3-5 diverse flight options.",
            "   Mix different: Airlines, Prices (budget/mid/premium), Flight types (direct/1-stop)",
            "",
            "   **Each flight MUST include**:",
            "   • airline: Airline name (e.g., 'Vietnam Airlines', 'Vietjet Air')",
            "   • flight_type: 'direct', '1 stop', '2+ stops'",
            "   • departure_time: Realistic time (e.g., '08:30 AM', 'Early morning', 'Afternoon')",
            "   • arrival_time: Based on flight duration",
            "   • duration: Total flight time (e.g., '5h 30m direct', '8h 45m with 1 stop in Bangkok')",
            "   • price_per_person: Round-trip price in VND (realistic for route)",
            "     - If tool output is USD, convert to VND before writing this field",
            "   • cabin_class: 'Economy', 'Premium Economy', 'Business'",
            "   • benefits: ['20kg checked baggage', 'Meals included', 'Seat selection']",
            "   • booking_platforms: ['Airline website', 'Traveloka', 'Skyscanner', 'Trip.com']",
            "   • notes: Highlight (e.g., 'Fastest direct option', 'Best value', 'Most comfortable')",
            "",
            "   **Summary fields (STRICT JSON OUTPUT ONLY)**:",
            "   - flight_options: List of 3-5 options above",
            "   - recommended_flight: Suggest best option based on travel_style",
            "   - average_price: Average price_per_person",
            "   - booking_tips: ['Book 2-3 months ahead for best prices', 'Check airline websites for promotions']",
            "   - visa_requirements: Brief note if applicable (e.g., 'Visa on arrival for tourism')",
            "",
            "OUTPUT FORMAT RULES:",
            "- RETURN ONLY VALID JSON that matches LogisticsAgentOutput schema.",
            "- No markdown, no extra text, no explanations.",
            "- If the flight API/search fails, return an empty list for flight_options and set booking_tips to explain the failure, still as valid JSON.",
            "",
            "**Price Adjustment Rules**:",
            "   • Peak season (Dec-Feb, Jul-Aug): +20-30% to base prices",
            "   • Off-peak (Mar-May, Sep-Nov): -10-20% from base prices",
            "   • Weekend departures: +10-15%",
            "   • Red-eye flights: -10-15%",
            "",
            "Be realistic with prices and times. Don't over-rely on search - use aviation knowledge!",
            "",
            "=" * 80,
            "🇻🇳 VIETNAMESE OUTPUT REQUIREMENT",
            "=" * 80,
            "ALL text in your output MUST be in VIETNAMESE:",
            "  • airline: Keep airline names (e.g., 'Vietnam Airlines', 'VietJet Air')",
            "  • departure_airport/arrival_airport: Keep codes + add Vietnamese names",
            "  • outbound_details/return_details: Tiếng Việt descriptions",
            "  • baggage: Tiếng Việt (e.g., '7kg xách tay', '20kg ký gửi')",
            "  • recommended_flight: Tiếng Việt recommendation",
            "  • booking_tips: Tiếng Việt",
            "  • visa_requirements: Tiếng Việt",
            "=" * 80,
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
        print(f"[LogisticsAgent] ✓ Found {len(response.content.flight_options)} flight options")
        print(f"[LogisticsAgent] ✓ Average price: {response.content.average_price:,.0f} VND/person")
        if response.content.recommended_flight:
            print(f"[LogisticsAgent] ✓ Recommended: {response.content.recommended_flight}")
        return response.content
    else:
        print(f"[LogisticsAgent] ⚠ Unexpected response type: {type(response.content)}")
        raise ValueError(f"Expected LogisticsAgentOutput, got {type(response.content)}")
