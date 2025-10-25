"""
Logistics Agent - Specialized for Flight Tickets
Provides detailed flight information with pricing, airlines, benefits using Agno's structured input/output
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
from models.schemas import LogisticsAgentInput, LogisticsAgentOutput
from tools.search_tool import search_tools


def create_logistics_agent(model: str = "gpt-4o-mini") -> Agent:
    """
    Create a Logistics Agent specialized for flight tickets with structured input/output.

    Args:
        model: OpenAI model ID to use

    Returns:
        Agent configured with LogisticsAgentInput and LogisticsAgentOutput schemas
    """
    # Create SSL context with certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=180.0)

    return Agent(
        name="LogisticsAgent",
        model=OpenAIChat(id=model, api_key=settings.openai_api_key, http_client=http_client),
        tools=[search_tools],
        instructions=[
            "You are a flight ticket specialist. Focus ONLY on flight information.",
            "Be fast and practical. Limit to 3-5 searches for flight options.",
            "Search: '{departure} to {destination} flights {date}', 'best airlines {route}', 'flight prices {date}'.",
            "Provide 3-5 flight options with different airlines, times, and price points.",
            "For EACH flight option include:",
            "  - Airline name (Vietnam Airlines, ANA, Lufthansa, etc.)",
            "  - Flight type (direct, one-stop, multi-stop)",
            "  - Departure/arrival times and duration",
            "  - Price per person (round-trip) in VND",
            "  - Cabin class (Economy, Business, etc.)",
            "  - Benefits (baggage allowance, meals, seat selection, lounge access)",
            "  - Booking platforms (airline website, Traveloka, Skyscanner)",
            "Recommend the best value option.",
            "Include booking tips: best time to book, price comparison, deals.",
            "Add brief visa requirements if you find the information.",
            "All prices in VND. Be specific with flight details.",
        ],
        input_schema=LogisticsAgentInput,
        output_schema=LogisticsAgentOutput,
        markdown=True,
        debug_mode=False,
        add_datetime_to_context=True,
        add_location_to_context=True,
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
