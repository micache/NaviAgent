"""
Souvenir Agent
Suggests souvenirs and where to buy them using Agno's structured input/output
"""

import sys
from pathlib import Path

from agno.agent import Agent
from agno.db import PostgresDb
from agno.memory import MemoryManager

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import model_settings
from models.schemas import SouvenirAgentInput, SouvenirAgentOutput
from tools.search_tool import search_tools


def create_souvenir_agent(
    agent_name: str = "souvenir",
    db: PostgresDb = None,
    user_id: str = None,
    enable_memory: bool = True,
) -> Agent:
    """
    Create a Souvenir Agent with structured input/output and database support.

    Args:
        agent_name: Name of agent for model configuration (default: "souvenir")
        db: PostgreSQL database instance for session/memory storage
        user_id: Optional default user ID for memory management
        enable_memory: Enable user memory management (default: True)

    Returns:
        Agent configured with SouvenirAgentInput and SouvenirAgentOutput schemas
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
        name="SouvenirAgent",
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
            "  If any price info you find is in USD, convert to VND before using it.",
            "    Use a realistic FX rate (e.g., 1 USD ≈ 25,000 VND) or a quick-search current rate.",
            "",
            "  Each item needs:",
            "    • item_name: Specific item (e.g., 'Vietnamese Coffee', 'Ao Dai Silk Scarf')",
            "    • description: What it is, why it's special (2 sentences)",
            "    • estimated_price: Price range in VND (convert from USD if needed, e.g., '50,000-200,000 VND')",
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
            "",
            "=" * 80,
            "🇻🇳 VIETNAMESE OUTPUT REQUIREMENT",
            "=" * 80,
            "ALL text in your output MUST be in VIETNAMESE:",
            "  • name: Tiếng Việt (souvenir name)",
            "  • description: Tiếng Việt (detailed description why it's special)",
            "  • where_to_buy: Tiếng Việt (specific locations/markets)",
            "  • category: Tiếng Việt (e.g., 'Đồ ăn', 'Thủ công mỹ nghệ', 'Trang sức')",
            "=" * 80,
        ],
        input_schema=SouvenirAgentInput,
        output_schema=SouvenirAgentOutput,
        markdown=True,
        debug_mode=False,
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
