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
        tools=[search_tools],
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
            "🔴 IMPORTANT: Search tools may fail. Use your GENERAL KNOWLEDGE about accommodations.",
            "",
            "**Search Strategy (OPTIONAL - Only if search works, max 2 searches)**:",
            "   1. '{destination} popular hotels neighborhoods'",
            "   2. '{destination} {travel_style} accommodation typical prices'",
            "",
            "⚠️ If search fails, USE GENERAL KNOWLEDGE to provide realistic options based on:",
            "   - Well-known hotel chains and local hotels in destination",
            "   - Typical neighborhoods for tourists",
            "   - Standard pricing ranges by accommodation type and location",
            "",
            "**Accommodation Guidelines by Destination**:",
            "",
            "**Tokyo, Japan**:",
            "  • Budget: Hostels/Capsule hotels in Asakusa/Ueno (500k-800k/night)",
            "  • Mid-range: 3-star hotels in Shinjuku/Shibuya (1.2M-2M/night)",
            "  • Premium: 4-5 star in Ginza/Roppongi (2.5M-4M/night)",
            "  • Best areas: Shinjuku (transport hub), Asakusa (traditional), Shibuya (trendy)",
            "",
            "**Bangkok, Thailand**:",
            "  • Budget: Hostels in Khao San Road (200k-400k/night)",
            "  • Mid-range: Hotels in Sukhumvit/Silom (600k-1.2M/night)",
            "  • Premium: 5-star near Chao Phraya (1.5M-3M/night)",
            "  • Best areas: Sukhumvit (BTS access), Silom (business), Old Town (cultural)",
            "",
            "**Seoul, Korea**:",
            "  • Budget: Guesthouses in Hongdae/Insadong (600k-900k/night)",
            "  • Mid-range: Hotels in Myeongdong/Gangnam (1M-2M/night)",
            "  • Premium: 5-star in Gangnam (2.5M-4M/night)",
            "  • Best areas: Myeongdong (shopping), Hongdae (youth culture), Gangnam (luxury)",
            "",
            "**Singapore**:",
            "  • Budget: Hostels in Chinatown/Little India (600k-1M/night)",
            "  • Mid-range: Hotels in Bugis/Clarke Quay (1.5M-2.5M/night)",
            "  • Premium: Marina Bay Sands area (3M-5M/night)",
            "",
            "**Output Requirements**: Provide 4-6 diverse accommodation options.",
            "   Mix different: Types (hostel/hotel/guesthouse), Areas, Price ranges",
            "",
            "   **Each option MUST include**:",
            "   • name: Hotel/hostel name (realistic, can use general names like 'Tokyo Central Hotel')",
            "   • type: 'Hotel', 'Hostel', 'Guesthouse', 'Apartment', 'Capsule Hotel'",
            "   • area: District/neighborhood (e.g., 'Shinjuku', 'Asakusa', 'Shibuya')",
            "   • price_per_night: Realistic price in VND",
            "   • total_cost: price_per_night × duration_nights",
            "   • rating: Out of 5.0 (e.g., 4.2, 4.5)",
            "   • distance_to_center: Distance or metro access (e.g., '2 km', '5 min walk to metro')",
            "   • amenities: ['WiFi', 'Breakfast', 'Airport shuttle', 'Gym', 'Pool', 'Laundry']",
            "   • booking_platforms: ['Booking.com', 'Agoda', 'Hotels.com', 'Airbnb']",
            "   • notes: Pros/cons (e.g., 'Great location but small rooms', 'Excellent value')",
            "",
            "   **Summary fields**:",
            "   - recommendations: List of 4-6 options above",
            "   - best_areas: Top 3-4 neighborhoods with brief description",
            "   - average_price_per_night: Average across options",
            "   - total_estimated_cost: average_price × duration_nights",
            "   - booking_tips: ['Book 2+ months ahead', 'Check cancellation policies']",
            "",
            "**Travel Style Matching**:",
            "   • luxury → 4-5 star hotels, premium amenities (Pool, Spa, Concierge)",
            "   • budget → Hostels, guesthouses, capsule hotels. Focus on good location + safety",
            "   • self_guided → Well-located 3-star near metro/transport hubs",
            "   • adventure → Flexible options, good for early check-out/late check-in",
            "",
            "**Price Adjustment Rules**:",
            "   • Peak season (holidays, festivals): +30-50%",
            "   • Weekend rates: +15-25%",
            "   • Central locations: +20-30% vs. suburbs",
            "",
            "Be realistic with prices and locations. Provide VARIETY so Itinerary Agent can choose!",
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
