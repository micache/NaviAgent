"""
Logistics Agent
Provides flight information and accommodation suggestions using Agno's structured input/output
"""

import ssl
import sys
from pathlib import Path

import certifi
import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from models.schemas import LogisticsAgentInput, LogisticsAgentOutput
from tools.search_tool import search_tools


def create_logistics_agent(model: str = "gpt-4o-mini") -> Agent:
    """
    Create a Logistics Agent with structured input/output.

    Args:
        model: OpenAI model ID to use

    Returns:
        Agent configured with LogisticsAgentInput and LogisticsAgentOutput schemas
    """
    # Create SSL context with certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=120.0)

    return Agent(
        name="LogisticsAgent",
        model=OpenAIChat(id=model, api_key=settings.openai_api_key, http_client=http_client),
        tools=[ReasoningTools(add_instructions=True, add_few_shot=True), search_tools],
        instructions=[
            "You are a travel logistics expert specializing in flights, accommodation, and transportation planning.",
            "CRITICAL: Use the 'think' tool to reason through cost optimization and booking strategies.",
            "Use 'analyze' tool to compare different flight options, accommodation areas, and transportation methods.",
            "CRITICAL: Use search tools to find current flight prices for the specific departure date.",
            "Search for '{departure_point} to {destination} flights {date}' to get accurate pricing.",
            "Consider the weather information when recommending accommodation (e.g., suggest hotels with pools for hot weather).",
            "Search for accommodation options and recommend specific areas/neighborhoods based on budget and travel style.",
            "Consider budget constraints when making recommendations.",
            "Provide practical transportation tips for getting around the destination.",
            "Include information about airport transfers and public transportation.",
            "Suggest booking strategies and optimal timing for best prices.",
            "Base all cost estimates on current market prices in VND.",
            "Consider seasonal variations in flight and hotel prices based on the travel date.",
            "Recommend specific neighborhoods/areas to stay with price ranges.",
        ],
        input_schema=LogisticsAgentInput,
        output_schema=LogisticsAgentOutput,
        markdown=True,
        debug_mode=True,
        add_datetime_to_context=True,
        add_location_to_context=True,
    )


async def run_logistics_agent(
    agent: Agent,
    departure_point: str,
    destination: str,
    departure_date,
    budget: float,
    duration: int,
    weather_info: str = "",
) -> LogisticsAgentOutput:
    """
    Run the logistics agent with structured input and output.

    Args:
        agent: The configured Logistics Agent
        departure_point: Starting location/city
        destination: Destination location/city
        departure_date: Departure date
        budget: Total budget in VND
        duration: Trip duration in days
        weather_info: Weather information from Weather Agent

    Returns:
        LogisticsAgentOutput with structured logistics information
    """
    print(f"[LogisticsAgent] Planning logistics from {departure_point} to {destination}")
    print(
        f"[LogisticsAgent] Departure: {departure_date}, Duration: {duration} days, Budget: {budget:,.0f} VND"
    )

    # Create structured input
    agent_input = LogisticsAgentInput(
        departure_point=departure_point,
        destination=destination,
        departure_date=departure_date,
        budget=budget,
        duration_days=duration,
        weather_info=weather_info,
    )

    # Run agent with structured input
    response = await agent.arun(input=agent_input)

    # Response.content will be a LogisticsAgentOutput object
    if isinstance(response.content, LogisticsAgentOutput):
        print(
            f"[LogisticsAgent] ✓ Estimated flight cost: {response.content.estimated_flight_cost:,.0f} VND"
        )
        print(
            f"[LogisticsAgent] ✓ Provided {len(response.content.accommodation_suggestions)} accommodation suggestions"
        )
        return response.content
    else:
        print(f"[LogisticsAgent] ⚠ Unexpected response type: {type(response.content)}")
        raise ValueError(f"Expected LogisticsAgentOutput, got {type(response.content)}")
