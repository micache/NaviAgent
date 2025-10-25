"""
Itinerary Agent
Generates detailed day-by-day travel itineraries using Agno's structured input/output
"""

import ssl
import sys
from pathlib import Path

import certifi
import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from models.schemas import ItineraryAgentInput, ItineraryAgentOutput
from tools.search_tool import search_tools


def create_itinerary_agent(model: str = "gpt-4o-mini") -> Agent:
    """
    Create an Itinerary Agent with structured input/output.

    Args:
        model: OpenAI model ID to use

    Returns:
        Agent configured with ItineraryAgentInput and ItineraryAgentOutput schemas
    """
    # Create SSL context with certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=180.0)

    return Agent(
        name="ItineraryAgent",
        model=OpenAIChat(id=model, api_key=settings.openai_api_key, http_client=http_client),
        tools=[ReasoningTools(add_instructions=True, add_few_shot=False), search_tools],
        instructions=[
            "You are a travel itinerary planner with flight and hotel selection capability.",
            "Be efficient - use reasoning wisely.",
            "Limit searches to 3-5 key queries: major attractions, events, practical info.",
            "Use 'think' only for complex routing. Use 'analyze' for quick comparisons.",
            "Create day-by-day schedules: time, location, activity type, cost, notes.",
            "Optimize for minimal travel time between activities.",
            "",
            "IMPORTANT - Flight & Hotel Selection:",
            "1. Review available_flights and available_accommodations from input",
            "2. SELECT the best flight option based on: price, timing, duration, benefits",
            "3. SELECT the best accommodation based on: location, price, amenities, ratings",
            "4. Fill selected_flight with: airline, outbound_flight, return_flight, total_cost",
            "5. Fill selected_accommodation with: name, area, check_in, check_out, total_cost",
            "6. Consider travel_style when selecting (luxury → high-end, budget → economical)",
        ],
        input_schema=ItineraryAgentInput,
        output_schema=ItineraryAgentOutput,
        markdown=True,
        debug_mode=False,
        add_datetime_to_context=True,
        add_location_to_context=True,
    )


async def run_itinerary_agent(
    agent: Agent,
    destination: str,
    departure_date,
    duration: int,
    travel_style: str,
    customer_notes: str = "",
    weather_info: str = "",
    available_flights: str = "",
    available_accommodations: str = "",
) -> ItineraryAgentOutput:
    """
    Run the itinerary agent with structured input and output.

    Args:
        agent: The configured Itinerary Agent
        destination: Destination location(s)
        departure_date: Departure date
        duration: Number of days
        travel_style: Travel style (self_guided, tour, etc.)
        customer_notes: Customer preferences and notes
        weather_info: Weather and seasonal information from Weather Agent
        available_flights: Flight options from Logistics Agent (formatted string)
        available_accommodations: Accommodation options from Accommodation Agent (formatted string)

    Returns:
        ItineraryAgentOutput with structured itinerary data including selected flight and accommodation
    """
    print(f"[ItineraryAgent] Creating {duration}-day itinerary for {destination}")
    print(f"[ItineraryAgent] Travel style: {travel_style}")
    print(f"[ItineraryAgent] Departure: {departure_date}")
    if available_flights:
        print(f"[ItineraryAgent] Received flight options for selection")
    if available_accommodations:
        print(f"[ItineraryAgent] Received accommodation options for selection")

    # Create structured input
    agent_input = ItineraryAgentInput(
        destination=destination,
        departure_date=departure_date,
        duration_days=duration,
        travel_style=travel_style,
        preferences=customer_notes,
        weather_info=weather_info,
        available_flights=available_flights,
        available_accommodations=available_accommodations,
    )

    # Run agent with structured input
    response = await agent.arun(input=agent_input)

    # Response.content will be a ItineraryAgentOutput object
    if isinstance(response.content, ItineraryAgentOutput):
        print(f"[ItineraryAgent] ✓ Generated {len(response.content.daily_schedules)} days")
        print(f"[ItineraryAgent] ✓ Identified {len(response.content.location_list)} locations")
        if response.content.selected_flight:
            print(
                f"[ItineraryAgent] ✓ Selected flight: {response.content.selected_flight.airline}"
            )
        if response.content.selected_accommodation:
            print(
                f"[ItineraryAgent] ✓ Selected accommodation: {response.content.selected_accommodation.name}"
            )
        return response.content
    else:
        # Fallback if structured output fails
        print(f"[ItineraryAgent] ⚠ Unexpected response type: {type(response.content)}")
        raise ValueError(f"Expected ItineraryAgentOutput, got {type(response.content)}")
