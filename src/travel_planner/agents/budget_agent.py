"""
Budgeting Agent
Creates detailed budget breakdowns for travel plans using Agno's structured input/output
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
from models.schemas import BudgetAgentInput, BudgetAgentOutput
from tools.search_tool import search_tools


def create_budget_agent(model: str = "gpt-4o-mini") -> Agent:
    """
    Create a Budget Agent with structured input/output.

    Args:
        model: OpenAI model ID to use

    Returns:
        Agent configured with BudgetAgentInput and BudgetAgentOutput schemas
    """
    # Create SSL context with certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=120.0)

    return Agent(
        name="BudgetAgent",
        model=OpenAIChat(id=model, api_key=settings.openai_api_key, http_client=http_client),
        tools=[ReasoningTools(add_instructions=True, add_few_shot=True)],
        instructions=[
            "You are a budget planning expert for travel.",
            "CRITICAL: Use the 'think' tool to reason through complex budget calculations and trade-offs.",
            "Use 'analyze' tool to evaluate different spending scenarios and optimization strategies.",
            "Break down costs into categories: Accommodation, Food & Dining, Transportation, Activities & Entertainment, Shopping, Emergency Fund, etc.",
            "Provide realistic cost estimates based on destination and travel style.",
            "Consider the planned activities from the itinerary when estimating costs.",
            "Compare total estimated cost against the provided budget.",
            "Give actionable recommendations for staying within budget or how to utilize extra budget.",
            "All costs should be in VND (Vietnamese Dong).",
        ],
        input_schema=BudgetAgentInput,
        output_schema=BudgetAgentOutput,
        markdown=True,
        debug_mode=True,
        add_datetime_to_context=True,
        add_location_to_context=True,
    )


async def run_budget_agent(
    agent: Agent,
    destination: str,
    duration: int,
    budget: float,
    num_travelers: int,
    itinerary_data: dict = None,
) -> BudgetAgentOutput:
    """
    Run the budget agent with structured input and output.

    Args:
        agent: The configured Budget Agent
        destination: Destination location
        duration: Number of days
        budget: Total budget in VND
        num_travelers: Number of travelers
        itinerary_data: Optional dict with itinerary information

    Returns:
        BudgetAgentOutput with structured budget breakdown
    """
    print(f"[BudgetAgent] Creating budget breakdown for {destination}")
    print(f"[BudgetAgent] Budget: {budget:,.0f} VND for {num_travelers} traveler(s)")

    # Prepare activities summary from itinerary
    activities_summary = ""
    if itinerary_data and "daily_schedules" in itinerary_data:
        activities_summary = "\n".join(
            [
                f"Day {day['day_number']}: {len(day.get('activities', []))} activities planned"
                for day in itinerary_data["daily_schedules"]
            ]
        )
    else:
        activities_summary = "No detailed itinerary available yet"

    # Create structured input
    agent_input = BudgetAgentInput(
        destination=destination,
        duration_days=duration,
        num_travelers=num_travelers,
        total_budget=budget,
        travel_style="self_guided",  # Could be passed as parameter
        activities_summary=activities_summary,
    )

    # Run agent with structured input
    response = await agent.arun(input=agent_input)

    # Response.content will be a BudgetAgentOutput object
    if isinstance(response.content, BudgetAgentOutput):
        print(f"[BudgetAgent] ✓ Total estimated: {response.content.total_estimated_cost:,.0f} VND")
        print(f"[BudgetAgent] ✓ Status: {response.content.budget_status}")
        return response.content
    else:
        print(f"[BudgetAgent] ⚠ Unexpected response type: {type(response.content)}")
        raise ValueError(f"Expected BudgetAgentOutput, got {type(response.content)}")
