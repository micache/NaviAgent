"""
Travel Planning Team - Using Agno's Team feature for intelligent agent collaboration
All agents work together as a team with intelligent task delegation
"""

import asyncio
import ssl
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from textwrap import dedent

import certifi
import httpx
from agno.models.openai import OpenAIChat
from agno.team.team import Team

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from models.schemas import (
    AccommodationAgentOutput,
    AdvisoryAgentOutput,
    BudgetAgentOutput,
    ItineraryAgentOutput,
    LogisticsAgentOutput,
    SouvenirAgentOutput,
    WeatherAgentOutput,
)

# Import all specialist agents
from .accommodation_agent import create_accommodation_agent
from .advisory_agent import create_advisory_agent
from .budget_agent import create_budget_agent
from .itinerary_agent import create_itinerary_agent
from .logistics_agent import create_logistics_agent
from .souvenir_agent import create_souvenir_agent
from .weather_agent import create_weather_agent


def create_travel_planning_team(model: str = "gpt-4o-mini") -> Team:
    """
    Create a collaborative Travel Planning Team where all agents work together.
    
    The team uses Agno's intelligent delegation to coordinate between:
    - Weather Agent (provides context for others)
    - Logistics Agent (flight specialist)
    - Accommodation Agent (hotel specialist)
    - Itinerary Agent (selects flights/hotels and creates schedule)
    - Budget Agent (analyzes costs from all sources)
    - Souvenir Agent (depends on budget)
    - Advisory Agent (safety and tips based on itinerary)
    
    Args:
        model: OpenAI model to use for team leader and agents
        
    Returns:
        Configured Team ready to plan trips
    """
    # Create SSL context
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=180.0)
    
    # Create all specialist agents with clear roles
    weather_agent = create_weather_agent(model)
    weather_agent.name = "Weather Specialist"
    weather_agent.role = "Provide weather forecasts, seasonal events, and packing recommendations"
    weather_agent.add_name_to_context = True
    # Disable structured I/O for team usage (Team Leader uses natural language)
    weather_agent.input_schema = None
    weather_agent.output_schema = None
    
    logistics_agent = create_logistics_agent(model)
    logistics_agent.name = "Flight Specialist"
    logistics_agent.role = "Find and recommend flight options with detailed pricing and benefits"
    logistics_agent.add_name_to_context = True
    # Disable structured I/O for team usage
    logistics_agent.input_schema = None
    logistics_agent.output_schema = None
    
    accommodation_agent = create_accommodation_agent(model)
    accommodation_agent.name = "Accommodation Specialist"
    accommodation_agent.role = "Find hotels, hostels, and accommodations with pricing and amenities"
    accommodation_agent.add_name_to_context = True
    # Disable structured I/O for team usage
    accommodation_agent.input_schema = None
    accommodation_agent.output_schema = None
    
    itinerary_agent = create_itinerary_agent(model)
    itinerary_agent.name = "Itinerary Planner"
    itinerary_agent.role = "Create day-by-day schedules and select best flights/hotels from available options"
    itinerary_agent.add_name_to_context = True
    # Disable structured I/O for team usage
    itinerary_agent.input_schema = None
    itinerary_agent.output_schema = None
    
    budget_agent = create_budget_agent(model)
    budget_agent.name = "Budget Analyst"
    budget_agent.role = "Analyze costs from flights, hotels, activities, and souvenirs to ensure budget compliance"
    budget_agent.add_name_to_context = True
    # Disable structured I/O for team usage
    budget_agent.input_schema = None
    budget_agent.output_schema = None
    
    souvenir_agent = create_souvenir_agent(model)
    souvenir_agent.name = "Souvenir Specialist"
    souvenir_agent.role = "Recommend souvenirs within budget constraints"
    souvenir_agent.add_name_to_context = True
    # Disable structured I/O for team usage
    souvenir_agent.input_schema = None
    souvenir_agent.output_schema = None
    
    advisory_agent = create_advisory_agent(model)
    advisory_agent.name = "Travel Advisor"
    advisory_agent.role = "Provide safety tips, visa info, and location descriptions based on itinerary"
    advisory_agent.add_name_to_context = True
    # Disable structured I/O for team usage
    advisory_agent.input_schema = None
    advisory_agent.output_schema = None
    
    # Create the Travel Planning Team
    team = Team(
        name="Travel Planning Team",
        model=OpenAIChat(id=model, api_key=settings.openai_api_key, http_client=http_client),
        members=[
            weather_agent,
            logistics_agent,
            accommodation_agent,
            itinerary_agent,
            budget_agent,
            souvenir_agent,
            advisory_agent,
        ],
        instructions=dedent("""
        You are the Travel Planning Team Leader coordinating a group of specialist agents.
        
        **Your Coordination Strategy:**
        
        1. **PHASE 1 - Context Gathering (Weather first):**
           - Delegate to Weather Specialist to get seasonal info and events
           - This provides context for all other agents
        
        2. **PHASE 2 - Options Research (Parallel):**
           - Delegate to Flight Specialist to find flight options
           - Delegate to Accommodation Specialist to find hotel options
           - These can run in parallel (use arun for concurrency)
        
        3. **PHASE 3 - Planning (Sequential):**
           - Delegate to Itinerary Planner with:
             * Weather information from Phase 1
             * Flight options from Phase 2
             * Hotel options from Phase 2
           - Itinerary Planner will select best flight/hotel and create schedule
        
        4. **PHASE 4 - Analysis (Parallel):**
           - Delegate to Budget Analyst with itinerary data
           - Delegate to Souvenir Specialist with budget info
           - Delegate to Travel Advisor with itinerary locations
           - These can run in parallel
        
        5. **PHASE 5 - Synthesis:**
           - Compile all agent outputs into a comprehensive travel plan
           - Ensure selected flight and hotel are highlighted
           - Verify budget compliance
           - Include all safety tips and recommendations
        
        **Important Rules:**
        - Weather Specialist must run FIRST (others depend on it)
        - Flight & Accommodation Specialists must complete BEFORE Itinerary Planner
        - Budget Analyst, Souvenir Specialist, and Travel Advisor need itinerary data
        - Always synthesize results into a cohesive final plan
        - Highlight the selected flight and accommodation clearly
        
        **When delegating tasks:**
        - Be specific about what information each agent needs
        - Pass relevant context from previous phases
        - Ensure dependencies are met before delegation
        """),
        markdown=True,
        show_members_responses=True,
        determine_input_for_members=True,  # Team leader determines task for each member
        delegate_task_to_all_members=False,  # Sequential delegation based on dependencies
        debug_mode=False,
    )
    
    return team


class TravelPlanningTeamInput:
    """Structured input for Travel Planning Team"""
    
    def __init__(
        self,
        destination: str,
        departure_point: str,
        departure_date: date,
        trip_duration: int,
        budget: float,
        num_travelers: int,
        travel_style: str = "self_guided",
        customer_notes: str = "",
    ):
        self.destination = destination
        self.departure_point = departure_point
        self.departure_date = departure_date
        self.trip_duration = trip_duration
        self.budget = budget
        self.num_travelers = num_travelers
        self.travel_style = travel_style
        self.customer_notes = customer_notes
        self.return_date = departure_date + timedelta(days=trip_duration)
        
    def to_prompt(self) -> str:
        """Convert to natural language prompt for team"""
        return dedent(f"""
        Plan a comprehensive {self.trip_duration}-day trip with the following details:
        
        **Trip Details:**
        - Destination: {self.destination}
        - Departure from: {self.departure_point}
        - Departure date: {self.departure_date.strftime('%Y-%m-%d')}
        - Return date: {self.return_date.strftime('%Y-%m-%d')}
        - Duration: {self.trip_duration} days
        
        **Travelers & Budget:**
        - Number of travelers: {self.num_travelers}
        - Total budget: {self.budget:,.0f} VND
        - Travel style: {self.travel_style}
        - Special preferences: {self.customer_notes or 'None'}
        
        **Required Outputs:**
        1. Weather forecast and seasonal events
        2. 3-5 flight options with details (airline, times, prices, benefits)
        3. 4-6 accommodation options with details (name, location, price, amenities)
        4. Day-by-day itinerary with SELECTED flight and hotel
        5. Complete budget breakdown including all costs
        6. Souvenir recommendations within budget
        7. Travel advisory with visa info and safety tips
        
        **Important:**
        - Itinerary must SELECT specific flight and accommodation from the options
        - Budget must include actual costs of selected items
        - All costs in VND
        - Ensure everything fits within budget: {self.budget:,.0f} VND
        """).strip()


async def run_travel_planning_team(
    team: Team,
    trip_request: TravelPlanningTeamInput,
) -> str:
    """
    Run the Travel Planning Team asynchronously for better performance.
    
    Args:
        team: Configured Travel Planning Team
        trip_request: Structured trip request
        
    Returns:
        String with comprehensive travel plan from all agents
    """
    print("\n" + "=" * 80)
    print("🌍 TRAVEL PLANNING TEAM - Starting Collaboration")
    print("=" * 80)
    print(f"Destination: {trip_request.destination}")
    print(f"Duration: {trip_request.trip_duration} days")
    print(f"Budget: {trip_request.budget:,.0f} VND")
    print(f"Travelers: {trip_request.num_travelers}")
    print("=" * 80 + "\n")
    
    # Convert to natural language prompt
    user_prompt = trip_request.to_prompt()
    
    # Run team asynchronously (members can work in parallel when possible)
    response = await team.arun(
        input=user_prompt,
        stream=False,
    )
    
    print("\n" + "=" * 80)
    print("✅ TRAVEL PLANNING TEAM - Collaboration Complete")
    print("=" * 80 + "\n")
    
    # Return the team leader's synthesized response
    return response.content if response.content else "No response generated"


# Example usage
async def example_usage():
    """Example of how to use the Travel Planning Team"""
    
    # Create team
    team = create_travel_planning_team("gpt-4o-mini")
    
    # Create trip request
    trip_request = TravelPlanningTeamInput(
        destination="Tokyo, Japan",
        departure_point="Hanoi",
        departure_date=date(2025, 12, 15),
        trip_duration=7,
        budget=50_000_000,
        num_travelers=2,
        travel_style="self_guided",
        customer_notes="Love photography and local food",
    )
    
    # Run team
    result = await run_travel_planning_team(team, trip_request)
    
    print("Final Travel Plan:")
    print(result)


if __name__ == "__main__":
    asyncio.run(example_usage())
