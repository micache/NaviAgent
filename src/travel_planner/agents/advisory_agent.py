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

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings, model_settings
from models.schemas import AdvisoryAgentInput, AdvisoryAgentOutput
from tools.search_tool import search_tools


def create_advisory_agent(agent_name: str = "advisory") -> Agent:
    """
    Create an Advisory Agent with structured input/output.

    Args:
        agent_name: Name of agent for model configuration (default: "advisory")

    Returns:
        Agent configured with AdvisoryAgentInput and AdvisoryAgentOutput schemas
    """
    # Create model from centralized configuration
    model = model_settings.create_model_for_agno(agent_name)

    return Agent(
        name="AdvisoryAgent",
        model=model,
        tools=[search_tools],
        instructions=[
            "You are the Travel Advisory Specialist - provide safety info and location context.",
            "",
            "**Your Job**: Deliver essential safety, visa, and cultural information.",
            "",
            "**Input Context**:",
            "  • itinerary: Contains location_list (from Itinerary Agent)",
            "  • Need to describe each location in location_list",
            "",
            "**Search Strategy (2-4 searches max)**:",
            "  1. '{destination} travel advisory visa requirements {year}'",
            "  2. '{destination} safety tips warnings tourists'",
            "  3. '{destination} SIM card mobile internet tourists' (if needed)",
            "",
            "**Output Requirements**:",
            "",
            "1. warnings_and_tips (5-10 tips):",
            "     • Safety warnings (scams, pickpockets, areas to avoid)",
            "     • Health tips (vaccinations, water safety, altitude)",
            "     • Cultural etiquette (dress code, tipping, customs)",
            "     • Practical tips (currency, language, emergency numbers)",
            "     • Travel insurance recommendation",
            "",
            "2. location_descriptions (for each location in location_list):",
            "     • name: Location name (e.g., 'Tokyo Tower', 'Ben Thanh Market')",
            "     • description: What it is, why visit, what to see (2-3 sentences)",
            "     • tips: Specific tips for this location (best time, entry fee, etc.)",
            "",
            "3. visa_info:",
            "     • Clear visa requirements for Vietnamese travelers",
            "     • e.g., 'Visa on arrival available', 'Visa-free for 30 days', 'eVisa required'",
            "     • Include application process if visa needed",
            "",
            "4. weather_info:",
            "     • Brief summary from Weather Agent context (if provided)",
            "     • Focus on travel implications (pack warm clothes, bring umbrella, etc.)",
            "",
            "5. sim_and_apps (3-5 items):",
            "     • SIM card options (Tourist SIM, operator names, where to buy, price)",
            "     • Essential apps (Google Maps, Grab, translation app, etc.)",
            "     • Connectivity tips (free WiFi spots, pocket WiFi rental)",
            "",
            "6. safety_tips (3-5 specific tips):",
            "     • Most important safety advice",
            "     • Emergency contacts (police, ambulance, embassy)",
            "     • Common tourist scams to avoid",
            "",
            "**Priority**: Safety and practical info over generic tourist info.",
            "Be SPECIFIC - mention actual SIM providers, real app names, specific scams.",
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
