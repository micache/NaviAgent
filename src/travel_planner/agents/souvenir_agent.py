"""
Souvenir Agent
Suggests souvenirs and where to buy them using Agno's structured input/output
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
from models.schemas import SouvenirAgentInput, SouvenirAgentOutput
from tools.search_tool import search_tools


def create_souvenir_agent(model: str = "gpt-4o-mini") -> Agent:
    """
    Create a Souvenir Agent with structured input/output.

    Args:
        model: OpenAI model ID to use

    Returns:
        Agent configured with SouvenirAgentInput and SouvenirAgentOutput schemas
    """
    # Create SSL context with certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=120.0)

    return Agent(
        name="SouvenirAgent",
        model=OpenAIChat(id=model, api_key=settings.openai_api_key, http_client=http_client),
        instructions=[
            "You are a souvenir and gift specialist with extensive knowledge of authentic local products, traditional crafts, and popular gift items.",
            "Search for popular and authentic souvenirs from the destination.",
            "Recommend a mix of traditional items, food products, and practical gifts.",
            "Include price ranges in VND based on current market prices.",
            "Suggest specific shops, markets, or districts where items can be purchased.",
            "Consider portability and customs regulations.",
            "Include both budget-friendly and premium options.",
            "Highlight items unique to the destination.",
            "Recommend at least 5-8 different souvenirs with varied price points.",
            "Be specific about shopping locations and neighborhoods.",
        ],
        input_schema=SouvenirAgentInput,
        output_schema=SouvenirAgentOutput,
        markdown=True,
        debug_mode=True,
        add_datetime_to_context=True,
        add_location_to_context=True,
    )


async def run_souvenir_agent(agent: Agent, destination: str) -> SouvenirAgentOutput:
    """
    Run the souvenir agent with structured input and output.

    Args:
        agent: The configured Souvenir Agent
        destination: Destination location

    Returns:
        SouvenirAgentOutput with structured souvenir recommendations
    """
    print(f"[SouvenirAgent] Finding souvenir recommendations for {destination}")

    # Create structured input
    agent_input = SouvenirAgentInput(destination=destination)

    # Run agent with structured input
    response = await agent.arun(input=agent_input)

    # Response.content will be a SouvenirAgentOutput object
    if isinstance(response.content, SouvenirAgentOutput):
        print(f"[SouvenirAgent] ✓ Recommended {len(response.content.souvenirs)} souvenir items")
        return response.content
    else:
        print(f"[SouvenirAgent] ⚠ Unexpected response type: {type(response.content)}")
        raise ValueError(f"Expected SouvenirAgentOutput, got {type(response.content)}")
