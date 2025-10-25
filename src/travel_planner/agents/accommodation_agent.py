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
from agno.models.openai import OpenAIChat

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from models.schemas import AccommodationAgentInput, AccommodationAgentOutput
from tools.search_tool import search_tools


def create_accommodation_agent(model: str = "gpt-4o-mini") -> Agent:
    """
    Create an Accommodation Agent with structured input/output.

    Args:
        model: OpenAI model ID to use

    Returns:
        Agent configured with AccommodationAgentInput and AccommodationAgentOutput schemas
    """
    # Create SSL context with certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=180.0)

    return Agent(
        name="AccommodationAgent",
        model=OpenAIChat(id=model, api_key=settings.openai_api_key, http_client=http_client),
        tools=[search_tools],
        instructions=[
            "You are an accommodation expert specializing in hotels, hostels, homestays, and rentals.",
            "Be fast and practical. Limit to 3-5 searches for accommodation options.",
            "Search: '{destination} hotels {travel_style}', '{destination} best areas to stay', '{destination} accommodation prices {date}'.",
            "Provide 4-6 accommodation recommendations across budget ranges.",
            "Include: hotel name, area/district, price range per night, amenities, distance to attractions.",
            "Consider travel style: luxury → 4-5 star hotels, budget → hostels/guesthouses, self_guided → well-located mid-range.",
            "Mention booking platforms (Booking.com, Agoda, Airbnb) and best booking times.",
            "All prices in VND. Be specific with districts/neighborhoods.",
        ],
        input_schema=AccommodationAgentInput,
        output_schema=AccommodationAgentOutput,
        markdown=True,
        debug_mode=False,
        add_datetime_to_context=True,
        add_location_to_context=True,
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
