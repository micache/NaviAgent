"""
Response Parser - Extract structured data from team response
"""

from datetime import datetime
from typing import Optional

from agno.agent import Agent
from pydantic import BaseModel, Field

from schemas.response import (
    Activity,
    DaySchedule,
    ItineraryTimeline,
    BudgetCategory,
    BudgetBreakdown,
    LocationDescription,
    AdvisoryInfo,
    SouvenirSuggestion,
    FlightOption,
    LogisticsInfo,
    AccommodationOption,
    AccommodationInfo,
    SelectedFlightInfo,
    SelectedAccommodationInfo,
    TravelPlan,
)


class ParsedTravelPlanOutput(BaseModel):
    """Output schema for parsed travel plan"""
    
    itinerary: ItineraryTimeline
    budget: BudgetBreakdown
    advisory: AdvisoryInfo
    souvenirs: list[SouvenirSuggestion]
    logistics: LogisticsInfo
    accommodation: Optional[AccommodationInfo] = None


def create_response_parser(model: str = "gpt-4o-mini") -> Agent:
    """
    Create Response Parser Agent to extract structured data from team response
    
    Args:
        model: OpenAI model to use
        
    Returns:
        Agent: Configured response parser agent
    """
    
    agent = Agent(
        name="Response Parser",
        model=model,
        description="Extract structured travel plan data from team synthesized response",
        instructions=[
            "You are a precise data extraction specialist.",
            "Your task is to parse a team-synthesized travel plan response and extract structured data.",
            "",
            "## Input Format",
            "You will receive a markdown-formatted travel plan with sections like:",
            "- Weather Forecast and Seasonal Events",
            "- Flight Options",
            "- Accommodation Options",
            "- Day-by-Day Itinerary",
            "- Complete Budget Breakdown",
            "- Souvenir Recommendations",
            "- Travel Advisory",
            "",
            "## Your Task",
            "Extract and structure the data into these components:",
            "",
            "### 1. Itinerary Timeline",
            "- Extract daily schedules with activities",
            "- Each activity should have: time, location_name, activity_type, description, estimated_cost",
            "- Extract location list (main places)",
            "- Extract selected flight info (if mentioned)",
            "- Extract selected accommodation info (if mentioned)",
            "",
            "### 2. Budget Breakdown",
            "- Extract all budget categories (Flights, Accommodation, Activities, Transportation, Meals, Souvenirs, etc.)",
            "- Calculate total estimated cost",
            "- Determine budget status (within budget / over budget / under budget)",
            "",
            "### 3. Advisory Info",
            "- Extract all warnings and tips",
            "- Extract location descriptions",
            "- Extract visa information",
            "- Extract weather information",
            "- Extract safety tips",
            "",
            "### 4. Souvenirs",
            "- Extract souvenir suggestions with name, description, estimated price, where to buy",
            "",
            "### 5. Logistics (Flights)",
            "- Extract all flight options mentioned",
            "- Each flight should have: airline, flight_type, departure_time, price_per_person, cabin_class, benefits",
            "- Extract booking tips",
            "- Calculate average price",
            "",
            "### 6. Accommodation",
            "- Extract all accommodation options mentioned",
            "- Each should have: name, type, area, price_per_night, amenities, booking_platforms",
            "- Extract best areas to stay",
            "- Extract booking tips",
            "- Calculate total estimated cost",
            "",
            "## Important Rules",
            "1. If information is not explicitly mentioned, use reasonable defaults or None/empty list",
            "2. Be precise with numbers (prices, costs) - extract exact values mentioned",
            "3. For activity types, use: 'sightseeing', 'dining', 'shopping', 'transportation', 'accommodation', 'entertainment'",
            "4. For time fields, use format: 'HH:MM - HH:MM' or 'HH:MM AM/PM'",
            "5. All costs should be in VND (Vietnam Dong)",
            "6. Extract ALL activities from each day - don't skip any",
            "7. If a selected flight is mentioned, extract it into selected_flight field",
            "8. If a selected hotel is mentioned, extract it into selected_accommodation field",
        ],
        response_model=ParsedTravelPlanOutput,
        markdown=False,
        show_tool_calls=False,
    )
    
    return agent


async def parse_team_response_to_structured(
    team_response: str,
    request_data: dict,
    model: str = "gpt-4o-mini"
) -> TravelPlan:
    """
    Parse team response into structured TravelPlan
    
    Args:
        team_response: Markdown response from travel planning team
        request_data: Original request data for request_summary
        model: OpenAI model to use for parsing
        
    Returns:
        TravelPlan: Structured travel plan with all fields populated
    """
    
    # Create parser agent
    parser = create_response_parser(model=model)
    
    # Parse the team response
    print("\n[Parser] Extracting structured data from team response...")
    parsed_output = await parser.arun(team_response)
    
    # Create TravelPlan with structured data
    travel_plan = TravelPlan(
        version="2.0-team-structured",
        request_summary=request_data,
        itinerary=parsed_output.itinerary,
        budget=parsed_output.budget,
        advisory=parsed_output.advisory,
        souvenirs=parsed_output.souvenirs,
        logistics=parsed_output.logistics,
        accommodation=parsed_output.accommodation,
        generated_at=datetime.utcnow().isoformat(),
        team_full_response=team_response,  # Keep original for reference
    )
    
    print("[Parser] ✓ Structured data extraction complete")
    
    return travel_plan
