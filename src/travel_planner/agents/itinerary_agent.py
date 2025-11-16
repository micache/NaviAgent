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
from agno.db import PostgresDb
from agno.memory import MemoryManager
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import model_settings, settings
from models.schemas import ItineraryAgentInput, ItineraryAgentOutput
from tools.search_tool import search_tools


def create_itinerary_agent(
    agent_name: str = "itinerary",
    db: PostgresDb = None,
    user_id: str = None,
    enable_memory: bool = True,
) -> Agent:
    """
    Create an Itinerary Agent with structured input/output and database support.

    Args:
        agent_name: Name of agent for model configuration (default: "itinerary")
        db: PostgreSQL database instance for session/memory storage
        user_id: Optional default user ID for memory management
        enable_memory: Enable user memory management (default: True)

    Returns:
        Agent configured with ItineraryAgentInput and ItineraryAgentOutput schemas
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
        name="ItineraryAgent",
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
        tools=[ReasoningTools(add_instructions=True, add_few_shot=False), search_tools],
        add_datetime_to_context=True,
        add_location_to_context=True,
        instructions=[
            "You are the Itinerary Planner & Selector - the CORE of the travel planning pipeline.",
            "",
            "**Input Context**: You will receive a large object containing:",
            "  - user_query: [destination, travel_style, duration_days, departure_date, num_travelers, total_budget]",
            "  - weather_context: (From WeatherAgent - includes temp, season, conditions, events)",
            "  - available_flights: [List of 3-5 complete flight objects from LogisticsAgent]",
            "  - available_accommodations: [List of 4-6 complete accommodation objects from AccommodationAgent]",
            "",
            "**Your Critical Job**:",
            "1. SELECT the single BEST flight from 'available_flights'.",
            "2. SELECT the single BEST accommodation from 'available_accommodations'.",
            "3. CREATE a detailed day-by-day itinerary for ALL 'duration_days', ensuring the total estimated cost is within the 'total_budget'.",
            "",
            "🔴 CRITICAL REQUIREMENT: You MUST create a schedule for EVERY SINGLE DAY of the trip!",
            "   • If duration_days = 5, create 5 daily schedules (day_number: 1, 2, 3, 4, 5).",
            "   • If duration_days = 7, create 7 daily schedules (day_number: 1, 2, 3, 4, 5, 6, 7).",
            "   • Each day_number must have a 'date' (YYYY-MM-DD) and a complete list of 'activities'.",
            "   • Do NOT skip any days - this is MANDATORY!",
            "   • ⚠️ The length of daily_schedules array MUST EQUAL duration_days",
            "",
            "🔴 VALIDATION CHECK: Before finalizing output, count your daily_schedules:",
            "   • Count = len(daily_schedules)",
            "   • Required = duration_days",
            "   • If Count ≠ Required → YOU MUST ADD MISSING DAYS!",
            "",
            "**Phase 1: SELECTION (Budget-Driven Decisions)**",
            "Use the 'think' tool from ReasoningTools to document your decision-making process for selections.",
            "",
            "**Flight Selection Criteria**:",
            "   • 1. Review 'travel_style' (luxury, budget, etc.).",
            "   • 2. Review 'total_cost' of each option.",
            "   • 3. ⚠️ CRITICAL RULE: 'total_cost' (for all travelers) MUST be less than 40% of the 'total_budget'.",
            "   • 4. Apply criteria: 'budget' style gets cheapest valid option; 'luxury' gets best option within 40% limit.",
            "   • 5. Prioritize reasonable arrival/departure times.",
            "",
            "**Accommodation Selection Criteria**:",
            "   • 1. Review 'travel_style' and 'area' of each option.",
            "   • 2. Review 'total_cost' of each option.",
            "   • 3. ⚠️ CRITICAL RULE: 'total_cost' MUST be less than 30% of the 'total_budget'.",
            "   • 4. Apply criteria: 'budget' style gets best-rated, well-located option; 'luxury' gets 4-5 star option.",
            "   • 5. Prioritize location ('area') that minimizes travel time for the itinerary.",
            "",
            "**Phase 2: ITINERARY CREATION (Budget-Aware)**",
            "",
            "**Internal Calculation (MANDATORY)**:",
            "   • selected_flight_cost = [cost from the flight object you selected]",
            "   • selected_accommodation_cost = [cost from the accommodation object you selected]",
            "   • 1. Calculate 'remaining_budget' = total_budget - selected_flight_cost - selected_accommodation_cost",
            "   • 2. Calculate 'daily_spending_limit' = (remaining_budget / duration_days) / num_travelers",
            "   • You MUST use this 'daily_spending_limit' to guide all 'estimated_cost' for activities and dining.",
            "",
            "**Search Strategy (4-6 searches max)**:",
            "   • 1. ❗️ **'average meal prices in {destination} for tourists' OR 'cost of food {destination}' (MUST DO THIS FIRST to set realistic meal budgets)**",
            "   • 2. 'top free things to do in {destination}' (if 'daily_spending_limit' is low)",
            "   • 3. '{destination} {duration_days} days itinerary {travel_style}'",
            "   • 4. '{destination} best local food spots' or '{destination} best restaurants'",
            "   • 5. '{destination} day trips from city center' (if duration_days >= 5 and budget allows)",
            "",
            "**Critical Logic for Scheduling (MANDATORY)**:",
            "1. **Date Calculation**: You MUST calculate the specific 'date' for each 'day_number'.",
            "   - Day 1 date = 'departure_date' (from input).",
            "   - Day 2 date = 'departure_date' + 1 day.",
            "   - ...and so on for all 'duration_days'.",
            "2. **Flight Time Integration**: Your schedule for Day 1 and the Final Day MUST be built around the 'selected_flight' times.",
            "",
            "**Daily Schedule Structure (REPEAT FOR EACH DAY)**:",
            "",
            "**Day 1 (Arrival Day - check selected_flight.outbound_details)**:",
            "   • [Time from flight]: 'Arrival at {destination} Airport' (activity_type: 'transport').",
            "   • [Time]: 'Transport to Hotel (e.g., Taxi, Metro)' (activity_type: 'transport'). Estimate cost.",
            "   • 14:00 (or later): 'Check-in at {selected_accommodation.name}' (activity_type: 'accommodation').",
            "   • *If arrival is morning/early afternoon*: Plan 1-2 light, low-cost activities near the hotel.",
            "   • *If arrival is late evening*: Plan only 'Check-in' and 'Dinner near hotel'.",
            "   • Evening (19:00-21:00): 'Welcome Dinner' (activity_type: 'dining') - cost must respect 'daily_spending_limit'.",
            "",
            "**Middle Days (Days 2 to N-1)**:",
            "   • Morning (08:00-12:00): 1-2 major attractions.",
            "   • Lunch (12:00-13:30): Local restaurant (activity_type: 'dining').",
            "   • Afternoon (14:00-18:00): 2-3 activities or 1 major site.",
            "   • Evening (19:00-22:00): 'Dinner' + optional night activity (night market, show).",
            "   • *Pacing*: Vary the pace. Mix sightseeing with 'relaxation' or 'shopping'.",
            "   • *Budget Check*: Sum of 'estimated_cost' for the day must not exceed 'daily_spending_limit' * num_travelers.",
            "",
            "**Final Day (Departure Day - check selected_flight.return_details)**:",
            "   • Morning (08:00-10:00): Last minute sightseeing or shopping (if budget remains).",
            "   • 10:00-11:00: 'Check out from {selected_accommodation.name}' (activity_type: 'accommodation').",
            "   • [Time]: 'Final Lunch' (activity_type: 'dining').",
            "   • [Time]: 'Transport to Airport' (activity_type: 'transport'). This MUST be scheduled 3-4 hours *before* the flight's departure time.",
            "",
            "**Activity Details for Each Item (in the 'activities' list)**:",
            "   • time: '09:00', '14:30', 'Afternoon'.",
            "   • location_name: Specific venue/attraction name.",
            "   • address: Area or district (e.g., 'Shibuya, Tokyo').",
            "   • activity_type: 'sightseeing', 'dining', 'shopping', 'relaxation', 'adventure', 'cultural', 'transport', 'accommodation'.",
            "   • description: What to do there (2-3 sentences).",
            "   • estimated_cost: Per person in VND. MUST be realistic and guided by the rules below.",
            "   • notes: Tips, booking requirements, photo spots.",
            "",
            "---",
            "💰 **BUDGET-CONSCIOUS PLANNING (Your Core Activity Logic)**:",
            "   • You MUST use these guidelines to set the 'estimated_cost' for activities.",
            "   • Free/cheap activities: Parks, temples, street walking tours (Cost: 0 - 50k VND - This is a general guide, adjust if {destination} is expensive).",
            "   • Mid-range activities: Museum tickets, guided tours (Cost: 100k-300k VND - Adjust based on local prices).",
            "   • Premium activities: Theme parks, special experiences (Cost: 500k-1M+ VND - Adjust based on local prices).",
            "   • **Balance the mix based on 'daily_spending_limit' and 'travel_style'**: ",
            "      - Tight budget (e.g., <30M) → Mostly free/cheap + very few mid-range.",
            "      - Moderate budget (30-50M) → Mix of free, mid-range, and 1-2 premium.",
            "      - High budget (>50M) → Can include multiple premium experiences.",
            "",
            "   • ❗️ **Meals Budget Guide (Dynamic - Destination Specific)**:",
            "      - **DO NOT use fixed VNĐ prices.** Prices in {destination} are different from Vietnam.",
            "      - You MUST use the results from your **Search Strategy Step 1** ('average meal prices {destination}').",
            "      - When creating a 'dining' activity, set 'estimated_cost' based on your research:",
            "         - 'Street food/local': Use the **low-range price** you found (e.g., '150k-300k in Seoul').",
            "         - 'Mid-range restaurant': Use the **mid-range price** you found (e.g., '400k-700k in Seoul').",
            "         - 'Fine dining': Use the **high-end price** you found (and only if 'daily_spending_limit' is very high).",
            "---",
            "",
            "**Integration Logic**:",
            "   - **Weather**: Use 'weather_context' input. If 'weather_conditions' predict 'heavy rain', prioritize indoor activities (museums, shopping).",
            "   - **Route Optimization**: Group activities by 'area'/'address' to minimize travel time. Do not zigzag across the city.",
            "",
            "**Output Requirements (CRITICAL)**:",
            "   - selected_flight: The complete flight object you chose",
            "   - selected_accommodation: The complete accommodation object you chose",
            "   - daily_schedules: Array with EXACTLY duration_days elements",
            "   - location_list: All unique location names from activities",
            "   - summary: 3-4 sentences overview",
            "",
            "**Example Output Structure for 5-day trip**:",
            "```json",
            "{",
            "  'daily_schedules': [",
            "    { 'day_number': 1, 'date': '2025-12-15', 'title': 'Arrival Day', 'activities': [3-5 activities] },",
            "    { 'day_number': 2, 'date': '2025-12-16', 'title': 'Historic Sites', 'activities': [5-7 activities] },",
            "    { 'day_number': 3, 'date': '2025-12-17', 'title': 'Modern City', 'activities': [5-7 activities] },",
            "    { 'day_number': 4, 'date': '2025-12-18', 'title': 'Day Trip', 'activities': [5-7 activities] },",
            "    { 'day_number': 5, 'date': '2025-12-19', 'title': 'Departure', 'activities': [3-4 activities] }",
            "  ],",
            "  'location_list': ['Location1', 'Location2', ...],",
            "  'summary': '...',",
            "  'selected_flight': {...},",
            "  'selected_accommodation': {...}",
            "}",
            "```",
            "",
            "**Downstream Agent Dependencies**:",
            "   - **Budget Agent**: Uses selected costs + ALL estimated_costs for calculation",
            "   - **Advisory Agent**: Uses location_list for safety tips",
            "",
            "⚠️ FINAL REMINDER: len(daily_schedules) MUST EQUAL duration_days!",
            "BE DECISIVE. Select best options and create COMPLETE, REALISTIC, BUDGET-CONSCIOUS plan!",
        ],
        input_schema=ItineraryAgentInput,
        output_schema=ItineraryAgentOutput,
        markdown=True,
        debug_mode=False,
    )


async def run_itinerary_agent(
    agent: Agent,
    destination: str,
    departure_date,
    duration: int,
    travel_style: str,
    customer_notes: str = "",
    weather_info: str = "",
    available_flights: str = "",
    available_accommodations: str = "",
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
        available_flights: Flight options from Logistics Agent (formatted string)
        available_accommodations: Accommodation options from Accommodation Agent (formatted string)

    Returns:
        ItineraryAgentOutput with structured itinerary data including selected flight and accommodation
    """
    print(f"[ItineraryAgent] Creating {duration}-day itinerary for {destination}")
    print(f"[ItineraryAgent] Travel style: {travel_style}")
    print(f"[ItineraryAgent] Departure: {departure_date}")
    if available_flights:
        print(f"[ItineraryAgent] Received flight options for selection")
    if available_accommodations:
        print(f"[ItineraryAgent] Received accommodation options for selection")

    # Create structured input
    agent_input = ItineraryAgentInput(
        destination=destination,
        departure_date=departure_date,
        duration_days=duration,
        travel_style=travel_style,
        preferences=customer_notes,
        weather_info=weather_info,
        available_flights=available_flights,
        available_accommodations=available_accommodations,
    )

    # Run agent with structured input
    response = await agent.arun(input=agent_input)

    # Response.content will be a ItineraryAgentOutput object
    if isinstance(response.content, ItineraryAgentOutput):
        print(f"[ItineraryAgent] ✓ Generated {len(response.content.daily_schedules)} days")
        print(f"[ItineraryAgent] ✓ Identified {len(response.content.location_list)} locations")
        if response.content.selected_flight:
            print(f"[ItineraryAgent] ✓ Selected flight: {response.content.selected_flight.airline}")
        if response.content.selected_accommodation:
            print(
                f"[ItineraryAgent] ✓ Selected accommodation: {response.content.selected_accommodation.name}"
            )
        return response.content
    else:
        # Fallback if structured output fails
        print(f"[ItineraryAgent] ⚠ Unexpected response type: {type(response.content)}")
        raise ValueError(f"Expected ItineraryAgentOutput, got {type(response.content)}")
