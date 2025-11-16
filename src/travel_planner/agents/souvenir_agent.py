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

from config import settings, model_settings
from models.schemas import SouvenirAgentInput, SouvenirAgentOutput
from tools.search_tool import search_tools


def create_souvenir_agent(agent_name: str = "souvenir") -> Agent:
    """
    Create a Souvenir Agent with structured input/output.

    Args:
        agent_name: Name of agent for model configuration (default: "souvenir")

    Returns:
        Agent configured with SouvenirAgentInput and SouvenirAgentOutput schemas
    """
    # Create model from centralized configuration
    model = model_settings.create_model_for_agno(agent_name)

    return Agent(
        name="SouvenirAgent",
        model=model,
        tools=[search_tools],
        instructions=[
            "You are a Souvenir Specialist - recommend authentic local gifts within budget.",
            "",
            "**Your Job**: Suggest 5-8 souvenir items that travelers can buy.",
            "",
            "**Search Strategy (2-3 searches max)**:",
            "  1. '{destination} best souvenirs authentic local'",
            "  2. '{destination} where to buy souvenirs markets'",
            "",
            "**Output: 5-8 Souvenir Items with VARIETY**:",
            "  Mix of:",
            "    • Traditional crafts (handicrafts, textiles, ceramics)",
            "    • Local food/snacks (coffee, tea, spices, sweets)",
            "    • Practical gifts (clothing, accessories)",
            "    • Premium items (art, jewelry)",
            "",
            "  Each item needs:",
            "    • item_name: Specific item (e.g., 'Vietnamese Coffee', 'Ao Dai Silk Scarf')",
            "    • description: What it is, why it's special (2 sentences)",
            "    • estimated_price: Price range in VND (e.g., '50,000-200,000 VND')",
            "    • where_to_buy: Specific markets/shops (e.g., 'Ben Thanh Market', 'Old Quarter shops')",
            "",
            "**Budget Consideration**:",
            "  • budget input = souvenir allocation (usually 5% of total trip budget)",
            "  • Suggest items within this budget",
            "  • Include both cheap (50k-200k) and premium (500k-1M+) options",
            "",
            "**Travel Style Matching**:",
            "  • luxury → premium crafts, art, jewelry",
            "  • budget → affordable snacks, small crafts",
            "  • self_guided/adventure → practical, unique local items",
            "",
            "Focus on AUTHENTIC local items, not generic tourist traps!",
        ],
        input_schema=SouvenirAgentInput,
        output_schema=SouvenirAgentOutput,
        markdown=True,
        debug_mode=False,
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
