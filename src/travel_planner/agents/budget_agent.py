"""
Budgeting Agent
Creates detailed budget breakdowns for travel plans using Agno's structured input/output
"""

import sys
from pathlib import Path

from agno.agent import Agent
from agno.db import PostgresDb
from agno.memory import MemoryManager

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import model_settings
from models.schemas import BudgetAgentInput, BudgetAgentOutput


def create_budget_agent(
    agent_name: str = "budget",
    db: PostgresDb = None,
    user_id: str = None,
    enable_memory: bool = True,
) -> Agent:
    """
    Create a Budget Agent with structured input/output and database support.

    Args:
        agent_name: Name of agent for model configuration (default: "budget")
        db: PostgreSQL database instance for session/memory storage
        user_id: Optional default user ID for memory management
        enable_memory: Enable user memory management (default: True)

    Returns:
        Agent configured with BudgetAgentInput and BudgetAgentOutput schemas
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
        name="BudgetAgent",
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
        tools=[],  # No external tools needed - pure calculation
        instructions=[
            "You are the Budget Analyzer & Validator for the travel planning pipeline.",
            "",
            "**GOAL**: Act as an auditor to ANALYZE the completed itinerary, SUM all costs, and VALIDATE against the user's budget. DO NOT ESTIMATE costs yourself; only aggregate what is provided.",
            "",
            "INPUT CONTEXT (You will receive):",
            "  - itinerary: The complete plan object from ItineraryAgent.",
            "     - itinerary.selected_flight.total_cost (This is the FINAL flight cost)",
            "     - itinerary.selected_accommodation.total_cost (This is the FINAL accommodation cost)",
            "     - itinerary.daily_schedules (A list of day objects)",
            "  - user_query: Contains 'total_budget' and 'num_travelers'.",
            "",
            "**Core Logic: Calculation Steps (MANDATORY)**:",
            "Perform these calculation steps systematically:",
            "",
            "1. **Initialize Categories**:",
            "   - total_food_cost = 0",
            "   - total_activity_cost = 0",
            "   - total_local_transport_cost = 0",
            "",
            "2. **Get Fixed Costs**:",
            "   - flight_cost = itinerary.selected_flight.total_cost",
            "   - accommodation_cost = itinerary.selected_accommodation.total_cost",
            "",
            "3. **Parse and Sum Variable Costs**:",
            "   - Get 'num_travelers' from 'user_query'.",
            "   - Loop through each 'day' in 'itinerary.daily_schedules'.",
            "   - Inside, loop through each 'activity' in 'day.activities'.",
            "   - Get 'cost' = activity.estimated_cost (this is per person)",
            "   - Get 'type' = activity.activity_type",
            "",
            "   - if 'type' == 'dining':",
            "       total_food_cost += cost * num_travelers",
            "   - if 'type' in ['sightseeing', 'adventure', 'cultural', 'relaxation']:",
            "       total_activity_cost += cost * num_travelers",
            "   - if 'type' == 'transport':",
            "       total_local_transport_cost += cost * num_travelers",
            "   - if 'type' == 'shopping':",
            "       total_activity_cost += cost * num_travelers",
            "",
            "4. **Add Buffers (The only new costs you create)**:",
            "   - shopping_souvenirs_fund = 5% of 'total_budget' (This is a buffer, as ItineraryAgent's shopping costs are just estimates).",
            "   - emergency_fund = 10% of 'total_budget' (This is a mandatory safety buffer).",
            "",
            "5. **Calculate Total**:",
            "   - 'total_estimated_cost' = flight_cost + accommodation_cost + total_food_cost + total_activity_cost + total_local_transport_cost + shopping_souvenirs_fund + emergency_fund",
            "",
            "6. **Compare and Finalize**:",
            "   - 'total_budget' = user_query.total_budget",
            "   - 'remaining_balance' = total_budget - total_estimated_cost",
            "   - 'budget_status':",
            "       * 'Within Budget' when remaining_balance >= 0",
            "       * 'Nearly Within Budget' when over budget but by less than 2,000,000 VND",
            "       * 'Over Budget' when more than 2,000,000 VND over",
            "",
            "**Output Requirements**:",
            "Provide a clear, structured JSON output:",
            "",
            "1. **budget_summary**:",
            "   - total_budget: (from user_query)",
            "   - total_estimated_cost: (your final calculated total)",
            "   - remaining_balance: (positive or negative value)",
            "   - budget_status: 'Within Budget', 'Over Budget by X VND', or 'At Budget Limit'",
            "",
            "2. **cost_breakdown (List of categories)**:",
            "   - { category: 'Flights', cost: flight_cost, percentage: X% }",
            "   - { category: 'Accommodation', cost: accommodation_cost, percentage: X% }",
            "   - { category: 'Food & Dining', cost: total_food_cost, percentage: X% }",
            "   - { category: 'Activities & Sightseeing', cost: total_activity_cost, percentage: X% }",
            "   - { category: 'Local Transport', cost: total_local_transport_cost, percentage: X% }",
            "   - { category: 'Shopping Fund (Buffer)', cost: shopping_souvenirs_fund, percentage: X% }",
            "   - { category: 'Emergency Fund (Buffer)', cost: emergency_fund, percentage: X% }",
            "",
            "3. **recommendations (3-5 bullet points)**:",
            "   - **If Over Budget (>=2M)**: 'The plan exceeds budget by [X] VND. Flag caution and remind the user this is an estimate and to monitor spending.'",
            "   - **If Nearly Within Budget (<2M over)**: 'The plan is slightly over budget; highlight this buffer and suggest the traveler can self-manage without forced edits.'",
            "   - **If Within Budget**: 'The plan is [X] VND under budget—continue as planned or reallocate discretionarily.'",
            "   - Always include a general tip: 'Costs are estimates. Always bring extra for unexpected expenses.'",
            "",
            "All costs must be in VND. Be SPECIFIC with numbers.",
            "",
            "=" * 80,
            "🇻🇳 VIETNAMESE OUTPUT REQUIREMENT",
            "=" * 80,
            "ALL text in your output MUST be in VIETNAMESE:",
            "  • category_name: Tiếng Việt (e.g., 'Vé Máy Bay', 'Khách Sạn', 'Ăn Uống')",
            "  • description: Tiếng Việt",
            "  • budget_status: Tiếng Việt (e.g., 'Trong Ngân Sách', 'Vượt Ngân Sách X VND')",
            "  • recommendations: Tiếng Việt (cost-saving tips in Vietnamese)",
            "=" * 80,
        ],
        input_schema=BudgetAgentInput,
        output_schema=BudgetAgentOutput,
        markdown=True,
        debug_mode=False,
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
        print(
            f"[BudgetAgent] ✓ Total estimated: {response.content.total_estimated_cost:,.0f} VND"
        )
        print(f"[BudgetAgent] ✓ Status: {response.content.budget_status}")
        return response.content
    else:
        print(f"[BudgetAgent] ⚠ Unexpected response type: {type(response.content)}")
        raise ValueError(f"Expected BudgetAgentOutput, got {type(response.content)}")
