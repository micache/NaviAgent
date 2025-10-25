"""
Advisory Agent
Provides travel advisories, warnings, and location descriptions using Agno's structured input/output
"""

import ssl
import sys
from pathlib import Path

import certifi
import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from models.schemas import AdvisoryAgentInput, AdvisoryAgentOutput

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from tools.search_tool import search_tools


def create_advisory_agent(model: str = "gpt-4o-mini") -> Agent:
    """
    Create an Advisory Agent with structured input/output.

    Args:
        model: OpenAI model ID to use

    Returns:
        Agent configured with AdvisoryAgentInput and AdvisoryAgentOutput schemas
    """
    # Create SSL context with certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=180.0)

    return Agent(
        name="AdvisoryAgent",
        model=OpenAIChat(id=model, api_key=settings.openai_api_key, http_client=http_client),
        tools=[search_tools],
        instructions=[
            "You are a travel advisory expert. Be efficient and practical.",
            "Limit to 2-3 searches: visa, travel advisory, major holidays.",
            "Provide safety tips, visa info, cultural etiquette, connectivity info.",
            "Describe top locations briefly (2 sentences each).",
            "Keep all recommendations actionable.",
        ],
        input_schema=AdvisoryAgentInput,
        output_schema=AdvisoryAgentOutput,
        markdown=True,
        debug_mode=False,
        add_datetime_to_context=True,
        add_location_to_context=True,
    )


async def run_advisory_agent(
    agent: Agent, destination: str, departure_date, duration_days: int, location_list: list = None
) -> AdvisoryAgentOutput:
    """
    Run the advisory agent with structured input and output.

    Args:
        agent: The configured Advisory Agent
        destination: Destination location
        departure_date: Departure date
        duration_days: Trip duration in days
        location_list: Optional list of specific locations to describe

    Returns:
        AdvisoryAgentOutput with structured advisory information
    """
    print(f"[AdvisoryAgent] Gathering advisory information for {destination}")
    print(f"[AdvisoryAgent] Departure: {departure_date}, Duration: {duration_days} days")

    if location_list:
        print(f"[AdvisoryAgent] Will describe {len(location_list)} locations")

    # Create structured input
    agent_input = AdvisoryAgentInput(
        destination=destination,
        departure_date=departure_date,
        duration_days=duration_days,
        location_list=location_list if location_list else None,
    )

    # Run agent with structured input
    response = await agent.arun(input=agent_input)

    # Response.content will be an AdvisoryAgentOutput object
    if isinstance(response.content, AdvisoryAgentOutput):
        print(f"[AdvisoryAgent] ✓ Generated {len(response.content.warnings_and_tips)} tips")
        print(
            f"[AdvisoryAgent] ✓ Described {len(response.content.location_descriptions)} locations"
        )
        return response.content
    else:
        print(f"[AdvisoryAgent] ⚠ Unexpected response type: {type(response.content)}")
        raise ValueError(f"Expected AdvisoryAgentOutput, got {type(response.content)}")
