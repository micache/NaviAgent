"""Pydantic models for structured input and output - Agent schemas for Agno."""

from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

# ============ AGENT INPUT SCHEMAS (for Agno structured input) ============


class WeatherAgentInput(BaseModel):
    """Structured input for Weather Agent."""

    destination: str = Field(..., description="Destination location/city")
    departure_date: date = Field(..., description="Departure date (YYYY-MM-DD)")
    duration_days: int = Field(..., description="Number of days for the trip", gt=0)


class ItineraryAgentInput(BaseModel):
    """Structured input for Itinerary Agent."""

    destination: str = Field(..., description="Destination location(s) for the trip")
    departure_date: date = Field(..., description="Departure date (YYYY-MM-DD)")
    duration_days: int = Field(..., description="Number of days for the trip", gt=0)
    travel_style: str = Field(
        ..., description="Travel style: self_guided, tour, luxury, budget, adventure"
    )
    preferences: str = Field(
        default="", description="Customer preferences, special requests, interests"
    )
    weather_info: str = Field(
        default="", description="Weather forecast and seasonal information from Weather Agent"
    )


class BudgetAgentInput(BaseModel):
    """Structured input for Budget Agent."""

    destination: str = Field(..., description="Destination location")
    duration_days: int = Field(..., description="Number of days for the trip", gt=0)
    num_travelers: int = Field(..., description="Number of travelers", gt=0)
    total_budget: float = Field(..., description="Total budget in VND", gt=0)
    travel_style: str = Field(..., description="Travel style")
    activities_summary: str = Field(
        default="", description="Summary of planned activities from itinerary"
    )


class AdvisoryAgentInput(BaseModel):
    """Structured input for Advisory Agent."""

    destination: str = Field(..., description="Destination location")
    departure_date: date = Field(..., description="Departure date (YYYY-MM-DD)")
    duration_days: int = Field(..., description="Number of days for the trip", gt=0)
    location_list: Optional[List[str]] = Field(
        None, description="List of specific locations to describe from the itinerary"
    )


class SouvenirAgentInput(BaseModel):
    """Structured input for Souvenir Agent."""

    destination: str = Field(..., description="Destination location for souvenir recommendations")


class LogisticsAgentInput(BaseModel):
    """Structured input for Logistics Agent."""

    departure_point: str = Field(..., description="Starting location/city")
    destination: str = Field(..., description="Destination location/city")
    departure_date: date = Field(..., description="Departure date (YYYY-MM-DD)")
    budget: float = Field(..., description="Total budget in VND", gt=0)
    duration_days: int = Field(..., description="Number of days for the trip", gt=0)
    weather_info: str = Field(
        default="", description="Weather forecast and seasonal information from Weather Agent"
    )


# ============ AGENT OUTPUT SCHEMAS (for Agno structured output) ============


class WeatherForecast(BaseModel):
    """Weather forecast for a specific date."""

    date: str = Field(..., description="Date in format YYYY-MM-DD")
    temperature_high: Optional[float] = Field(None, description="High temperature in Celsius")
    temperature_low: Optional[float] = Field(None, description="Low temperature in Celsius")
    conditions: str = Field(..., description="Weather conditions (e.g., sunny, rainy, cloudy)")
    precipitation_chance: Optional[int] = Field(
        None, description="Chance of precipitation (0-100%)"
    )
    notes: Optional[str] = Field(None, description="Special weather notes or warnings")


class WeatherAgentOutput(BaseModel):
    """Weather and seasonal information from Weather Agent."""

    destination: str = Field(..., description="Destination location")
    season: str = Field(
        ..., description="Season during travel period (e.g., 'Winter', 'Summer', 'Monsoon season')"
    )
    daily_forecasts: Optional[List[WeatherForecast]] = Field(
        None, description="Daily weather forecasts for the trip duration"
    )
    seasonal_events: Optional[List[str]] = Field(
        None, description="Festivals, holidays, or special events during the travel period"
    )
    packing_recommendations: List[str] = Field(
        ..., description="Clothing and item recommendations based on weather"
    )
    weather_summary: str = Field(
        ..., description="Overall weather summary and what to expect (2-3 sentences)"
    )
    best_activities: Optional[List[str]] = Field(
        None, description="Activities best suited for the weather conditions"
    )


class Activity(BaseModel):
    """Single activity in the itinerary."""

    time: str = Field(..., description="Time range for the activity (e.g., '08:00 - 10:00')")
    location_name: str = Field(..., description="Name of the location")
    address: str = Field(..., description="Full address of the location")
    activity_type: str = Field(
        ..., description="Type: sightseeing, food, shopping, nightlife, etc."
    )
    description: str = Field(..., description="Detailed description of the activity")
    estimated_cost: float = Field(..., description="Estimated cost per person in VND")
    notes: Optional[str] = Field(None, description="Additional notes, tips, or warnings")


class DailySchedule(BaseModel):
    """Schedule for one day."""

    day_number: int = Field(..., description="Day number in the trip (1, 2, 3, ...)")
    date: Optional[str] = Field(None, description="Date in format YYYY-MM-DD if known")
    title: str = Field(
        ..., description="Title or theme for the day (e.g., 'Explore Historic Tokyo')"
    )
    activities: List[Activity] = Field(..., description="List of activities for this day")


class ItineraryAgentOutput(BaseModel):
    """Complete itinerary output from Itinerary Agent."""

    daily_schedules: List[DailySchedule] = Field(
        ..., description="Day-by-day schedule with activities"
    )
    location_list: List[str] = Field(
        ..., description="List of all unique location names mentioned in the itinerary"
    )
    summary: str = Field(..., description="Brief summary of the itinerary (2-3 sentences)")


class BudgetCategory(BaseModel):
    """Budget breakdown by category."""

    category_name: str = Field(
        ...,
        description="Category name: Accommodation, Food, Transportation, Activities, Shopping, etc.",
    )
    estimated_cost: float = Field(..., description="Total estimated cost for this category in VND")
    breakdown: Optional[List[Dict[str, float]]] = Field(
        None, description="Optional detailed breakdown within the category"
    )
    notes: Optional[str] = Field(None, description="Additional notes about this category")


class BudgetAgentOutput(BaseModel):
    """Complete budget breakdown from Budget Agent."""

    categories: List[BudgetCategory] = Field(
        ..., description="List of budget categories with cost estimates"
    )
    total_estimated_cost: float = Field(
        ..., description="Total estimated cost for the entire trip in VND"
    )
    budget_status: str = Field(
        ...,
        description="Budget status: 'Within Budget', 'Over Budget by X VND', 'Under Budget by X VND'",
    )
    recommendations: Optional[List[str]] = Field(
        None, description="Cost-saving recommendations or spending suggestions"
    )


class LocationDescription(BaseModel):
    """Description of a specific location."""

    location_name: str = Field(..., description="Name of the location")
    description: str = Field(
        ...,
        description="Brief description (2-3 sentences) about the location, its significance, and what to expect",
    )
    highlights: Optional[List[str]] = Field(None, description="Key highlights or must-see features")


class AdvisoryAgentOutput(BaseModel):
    """Travel advisory information from Advisory Agent."""

    warnings_and_tips: List[str] = Field(
        ..., description="Important warnings, tips, and general advice for the destination"
    )
    location_descriptions: Optional[List[LocationDescription]] = Field(
        None, description="Descriptions of key locations from the itinerary"
    )
    visa_info: str = Field(..., description="Visa requirements and information for travelers")
    weather_info: str = Field(..., description="Weather conditions and what to pack")
    sim_and_apps: Optional[List[str]] = Field(
        None, description="Recommended SIM cards, mobile apps, and connectivity options"
    )
    safety_tips: Optional[List[str]] = Field(
        None, description="Safety tips and emergency information"
    )


class Souvenir(BaseModel):
    """Souvenir recommendation."""

    item_name: str = Field(..., description="Name of the souvenir item")
    description: str = Field(
        ...,
        description="Description of the item, its cultural significance, and why it makes a good souvenir",
    )
    estimated_price: str = Field(
        ..., description="Estimated price range (e.g., '100,000 - 500,000 VND')"
    )
    where_to_buy: str = Field(..., description="Recommended places or areas to purchase this item")


class SouvenirAgentOutput(BaseModel):
    """Souvenir recommendations from Souvenir Agent."""

    souvenirs: List[Souvenir] = Field(
        ..., description="List of recommended souvenir items (5-10 items)"
    )


class LogisticsAgentOutput(BaseModel):
    """Travel logistics information from Logistics Agent."""

    flight_info: str = Field(
        ..., description="Flight recommendations, airlines, typical flight duration"
    )
    estimated_flight_cost: float = Field(
        ..., description="Estimated round-trip flight cost per person in VND"
    )
    accommodation_suggestions: List[str] = Field(
        ..., description="Recommended areas or neighborhoods to stay"
    )
    transportation_tips: List[str] = Field(..., description="Local transportation options and tips")


# ============ LEGACY SCHEMAS (for backward compatibility) ============
# These are kept for any existing code that might use them


class TravelRequest(BaseModel):
    """Structured travel planning request."""

    destination: str = Field(..., description="Destination location(s)")
    departure_point: str = Field(..., description="Starting location")
    start_date: Optional[date] = Field(None, description="Trip start date")
    duration_days: int = Field(..., description="Number of days for the trip", gt=0)
    budget: float = Field(..., description="Total budget in VND", gt=0)
    num_travelers: int = Field(..., description="Number of travelers", gt=0)
    travel_style: str = Field(
        default="self_guided", description="Travel style: self_guided, luxury, budget, adventure"
    )
    preferences: Optional[str] = Field(None, description="Additional preferences and notes")


class ItineraryRequest(BaseModel):
    """Request for itinerary creation."""

    destination: str
    duration_days: int
    travel_style: str
    preferences: Optional[str] = None


class BudgetRequest(BaseModel):
    """Request for budget planning."""

    destination: str
    duration_days: int
    num_travelers: int
    total_budget: float
    travel_style: str


class AdvisoryRequest(BaseModel):
    """Request for travel advisory."""

    destination: str
    travel_month: Optional[int] = None


# Re-export output schemas with old names for backward compatibility
ItineraryOutput = ItineraryAgentOutput
BudgetOutput = BudgetAgentOutput
AdvisoryOutput = AdvisoryAgentOutput
LogisticsOutput = LogisticsAgentOutput


# ============ COMPLETE TRAVEL PLAN OUTPUT ============


class TravelPlanOutput(BaseModel):
    """Complete travel plan output."""

    version: str = "1.0"
    request_summary: dict
    itinerary: ItineraryOutput
    budget: BudgetOutput
    advisory: AdvisoryOutput
    souvenirs: List[Souvenir]
    logistics: LogisticsOutput
    generated_at: str
