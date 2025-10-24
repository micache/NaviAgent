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
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=120.0)

    return Agent(
        name="ItineraryAgent",
        model=OpenAIChat(id=model, api_key=settings.openai_api_key, http_client=http_client),
        tools=[ReasoningTools(add_instructions=True, add_few_shot=True), search_tools],
        instructions=[
            "You are a travel itinerary planner specializing in creating detailed day-by-day schedules.",
            "CRITICAL: Use the 'think' tool to reason through complex scheduling decisions and optimize the itinerary.",
            "Use 'analyze' tool to evaluate different routing options and activity combinations.",
            "CRITICAL: Use search tools to find current information about festivals, events, and special occasions during the travel dates.",
            "Search for '{destination} festivals {month} {year}' and '{destination} events {specific dates}'.",
            "Consider the weather information provided and plan indoor/outdoor activities accordingly.",
            "If special events or festivals are found during the travel period, incorporate them into the itinerary.",
            "Create comprehensive daily schedules with activities, locations, and timing.",
            "For each activity, include: time slot, location name, full address, activity type, detailed description, estimated cost per person, and helpful notes.",
            "Provide practical tips and notes for each location.",
            "Organize activities logically by time and location to minimize travel time.",
            "Include a variety of activity types: sightseeing, dining, shopping, entertainment, festivals/events, etc.",
            "Match activities to weather conditions (e.g., indoor activities for rainy days, outdoor for sunny days).",
        ],
        input_schema=ItineraryAgentInput,
        output_schema=ItineraryAgentOutput,
        markdown=True,
        debug_mode=True,
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

    Returns:
        ItineraryAgentOutput with structured itinerary data
    """
    print(f"[ItineraryAgent] Creating {duration}-day itinerary for {destination}")
    print(f"[ItineraryAgent] Travel style: {travel_style}")
    print(f"[ItineraryAgent] Departure: {departure_date}")

    # Create structured input
    agent_input = ItineraryAgentInput(
        destination=destination,
        departure_date=departure_date,
        duration_days=duration,
        travel_style=travel_style,
        preferences=customer_notes,
        weather_info=weather_info,
    )

    # Run agent with structured input
    response = await agent.arun(input=agent_input)

    # Response.content will be a ItineraryAgentOutput object
    if isinstance(response.content, ItineraryAgentOutput):
        print(f"[ItineraryAgent] ✓ Generated {len(response.content.daily_schedules)} days")
        print(f"[ItineraryAgent] ✓ Identified {len(response.content.location_list)} locations")
        return response.content
    else:
        # Fallback if structured output fails
        print(f"[ItineraryAgent] ⚠ Unexpected response type: {type(response.content)}")
        raise ValueError(f"Expected ItineraryAgentOutput, got {type(response.content)}")
