"""
Accommodation Agent
Specialized agent for finding hotels, hostels, homestays, and other accommodations
Uses Agno's structured input/output
"""

import ssl
import sys
from pathlib import Path

import certifi
import httpx
from agno.agent import Agent
from agno.db import PostgresDb
from agno.memory import MemoryManager
from agno.models.openai import OpenAIChat

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import model_settings, settings
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
        tools=[hotel_tools, search_tools],  # Hotel API first, then fallback to search
        add_datetime_to_context=True,
        instructions=[
            "You are the Accommodation Specialist for the travel planning pipeline.",
            "",
            "**Role**: Provide 4-6 diverse accommodation options for the Itinerary Agent to choose from.",
            "",
            "**Input Context**: You will receive:",
            "  - destination: str (e.g., 'Tokyo', 'Bangkok')",
            "  - departure_date: date (check-in date)",
            "  - duration_nights: int (number of nights)",
            "  - budget_per_night: float (allocated budget per night)",
            "  - num_travelers: int",
            "  - travel_style: str ('budget', 'luxury', 'self_guided', 'adventure')",
            "  - preferences: str (customer notes)",
            "",
            "**Available Tools (CALL ONCE ONLY)**:",
            "1. **Hotel API Tools (TRY FIRST)**:",
            "   • search_hotels(location, check_in, check_out, adults, max_results)",
            "     - Returns: Real hotel data with prices, ratings, reviews",
            "     - Can use city name directly (auto-converts to location ID)",
            "     - ⚠️ IMPORTANT: Call ONCE with max_results=15-20. DO NOT call multiple times!",
            "",
            "2. **Search Tool (FALLBACK if API fails)**:",
            "   • duckduckgo_search(query, max_results): Web search",
            "     - Use ONLY if API returns 'No hotels found' or error",
            "     - Call ONCE and use the result",
            "     - Query: '{destination} hotels {travel_style} prices'",
            "",
            "**Tool Selection Logic**:",
            "",
            "📅 **Step 1: Calculate Dates**",
            "   - check_in = departure_date",
            "   - check_out = departure_date + duration_nights",
            "   - Format: YYYY-MM-DD",
            "",
            "🏨 **Step 2: Search Hotels (CALL ONCE)**",
            "   → Call ONCE: search_hotels(location=destination, check_in=check_in, check_out=check_out,",
            "                               adults=num_travelers, max_results=20)",
            "   → API returns 15-20 hotels with prices, ratings, locations",
            "   → ⚠️ IMPORTANT: API price is PER NIGHT. You must calculate total_cost = price_per_night × duration_nights",
            "   ",
            "   → From these results, select 4-6 diverse options based on:",
            "     1. **Rating**: Prioritize hotels with rating ≥ 4.0/5.0 (good quality)",
            "     2. **Price**: Mix of price ranges (budget, mid-range, luxury)",
            "     3. **Location**: Different neighborhoods (central, near attractions, near metro)",
            "     4. **Type**: Various hotel types (boutique, chain, hostel, resort)",
            "   ",
            "   → Selection Strategy:",
            "     • travel_style='budget' → Choose best-rated options in low-mid price range (rating ≥ 4.0)",
            "     • travel_style='luxury' → Choose highest-rated options (rating ≥ 4.5) regardless of price",
            "     • travel_style='self_guided' → Balance rating (≥ 4.0) + good location + reasonable price",
            "   ",
            "   → DO NOT call search_hotels again!",
            "",
            "⚠️ **CRITICAL: ONE TOOL CALL**",
            "   - search_hotels() → Called ONCE with max_results=20",
            "   - Use the results to create 4-6 diverse options",
            "   - DO NOT call the tool multiple times",
            "   - If API fails → Use duckduckgo_search() ONCE",
            "",
            "🔄 **Step 3: Fallback Strategy (If API Fails)**",
            "   If search_hotels() returns 'No hotels found' or error:",
            "   → Use duckduckgo_search() ONCE + general knowledge:",
            "     - '{destination} best hotels for {travel_style}'",
            "     - '{destination} popular hotel neighborhoods'",
            "     - Use your knowledge of hotel chains and typical prices",
            "",
            "**Output Requirements**: Provide 4-6 diverse accommodation options.",
            "   Mix different: Types (hostel/hotel/guesthouse), Areas, Price ranges",
            "",
            "   **Each option MUST include**:",
            "   • name: Hotel/hostel name (from API or realistic names like 'Tokyo Central Hotel')",
            "   • type: 'Hotel', 'Hostel', 'Guesthouse', 'Apartment', 'Capsule Hotel'",
            "   • area: District/neighborhood (e.g., 'Shinjuku', 'Asakusa', 'Shibuya')",
            "   • price_per_night: Price per night in VND (from API)",
            "   • total_cost: CRITICAL - MUST calculate: price_per_night × duration_nights",
            "   • rating: From API (prefer ≥ 4.0/5.0 for good quality)",
            "   • distance_to_center: Distance or metro access (e.g., '2 km', '5 min walk to metro')",
            "   • amenities: ['WiFi', 'Breakfast', 'Airport shuttle', 'Gym', 'Pool', 'Laundry']",
            "   • booking_platforms: ['Booking.com', 'Agoda', 'Hotels.com', 'Airbnb']",
            "   • notes: Pros/cons including rating context (e.g., 'Rated 4.5/5 - Excellent location', 'Rated 4.2/5 - Good value')",
            "",
            "   **Summary fields**:",
            "   - recommendations: List of 4-6 options above",
            "   - best_areas: Top 3-4 neighborhoods with brief description",
            "   - average_price_per_night: Average across options",
            "   - total_estimated_cost: average_price × duration_nights",
            "   - booking_tips: ['Book 2+ months ahead', 'Check cancellation policies']",
            "",
            "**Travel Style Matching (with Rating Priority)**:",
            "   • luxury → Rating ≥ 4.5/5.0, 4-5 star hotels, premium amenities (Pool, Spa, Concierge)",
            "   • budget → Rating ≥ 4.0/5.0, hostels, guesthouses. Focus on good rating + location + affordable",
            "   • self_guided → Rating ≥ 4.0/5.0, well-located 3-star near metro/transport hubs",
            "   • adventure → Rating ≥ 4.0/5.0, flexible options, good for early/late check-in",
            "   ",
            "   ⚠️ CRITICAL: Always prioritize hotels with rating ≥ 4.0. Avoid low-rated hotels (<3.5).",
            "",
            "**Price Adjustment Rules**:",
            "   • Peak season (holidays, festivals): +30-50%",
            "   • Weekend rates: +15-25%",
            "   • Central locations: +20-30% vs. suburbs",
            "",
            "Be realistic with prices and locations. Provide VARIETY so Itinerary Agent can choose!",
            "",
            "=" * 80,
            "🇻🇳 VIETNAMESE OUTPUT REQUIREMENT",
            "=" * 80,
            "ALL text in your output MUST be in VIETNAMESE:",
            "  • name: Keep hotel names (e.g., 'Sheraton Hotel', 'Khách sạn ABC')",
            "  • area: Tiếng Việt (e.g., 'Trung tâm thành phố', 'Gần sân bay')",
            "  • description: Tiếng Việt (detailed hotel description)",
            "  • amenities: Tiếng Việt (e.g., 'Hồ bơi', 'Phòng gym', 'Wi-Fi miễn phí')",
            "  • best_areas: Tiếng Việt (neighborhood recommendations)",
            "  • booking_tips: Tiếng Việt",
            "=" * 80,
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
        print(
            f"[AccommodationAgent] ✓ Found {len(response.content.recommendations)} accommodation options"
        )
        print(
            f"[AccommodationAgent] ✓ Average price: {response.content.average_price_per_night:,.0f} VND/night"
        )
        return response.content
    else:
        print(f"[AccommodationAgent] ⚠ Unexpected response type: {type(response.content)}")
        raise ValueError(f"Expected AccommodationAgentOutput, got {type(response.content)}")
