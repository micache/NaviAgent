"""Pydantic models for structured input and output - Agent schemas for Agno."""

from datetime import date
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

# Import shared schemas from public API
from schemas.response import AccommodationOption, Activity, BudgetCategory
from schemas.response import DaySchedule as DailySchedule  # Map to internal naming
from schemas.response import (
    FlightOption,
    LocationDescription,
    SelectedAccommodationInfo,
    SelectedFlightInfo,
)
from schemas.response import SouvenirSuggestion as Souvenir

# ============ AGENT INPUT SCHEMAS (for Agno structured input) ============


class WeatherAgentInput(BaseModel):
    """Structured input for Weather Agent."""

    destination: str = Field(..., description="Destination location/city")
    departure_date: Union[str, date] = Field(..., description="Departure date (YYYY-MM-DD)")
    duration_days: int = Field(..., description="Number of days for the trip", gt=0)


class ItineraryAgentInput(BaseModel):
    """Structured input for Itinerary Agent."""

    destination: str = Field(..., description="Destination location(s) for the trip")
    departure_date: Union[str, date] = Field(..., description="Departure date (YYYY-MM-DD)")
    duration_days: int = Field(..., description="Number of days for the trip", gt=0)
    num_travelers: int = Field(..., description="Number of travelers", gt=0)
    total_budget: float = Field(..., description="Total budget for the trip in VND", gt=0)
    travel_style: str = Field(
        ..., description="Travel style: self_guided, tour, luxury, budget, adventure"
    )
    preferences: str = Field(
        default="", description="Customer preferences, special requests, interests"
    )
    weather_info: Optional[dict] = Field(
        None, description="Weather forecast and seasonal information from Weather Agent"
    )
    available_flights: Optional[List[dict]] = Field(
        None, description="Available flight options from Logistics Agent"
    )
    available_accommodations: Optional[List[dict]] = Field(
        None, description="Available accommodation options from Accommodation Agent"
    )


class BudgetAgentInput(BaseModel):
    """Structured input for Budget Agent."""

    destination: str = Field(..., description="Destination location")
    trip_duration: int = Field(..., description="Number of days for the trip", gt=0)
    num_travelers: int = Field(..., description="Number of travelers", gt=0)
    total_budget: float = Field(..., description="Total budget in VND", gt=0)
    itinerary: Optional[dict] = Field(None, description="Itinerary output from Itinerary Agent")
    selected_flight_cost: float = Field(0, description="Cost of selected flight from itinerary")
    selected_accommodation_cost: float = Field(
        0, description="Cost of selected accommodation from itinerary"
    )


class AdvisoryAgentInput(BaseModel):
    """Structured input for Advisory Agent."""

    destination: str = Field(..., description="Destination location")
    trip_duration: int = Field(..., description="Number of days for the trip", gt=0)
    travel_style: str = Field(..., description="Travel style")
    itinerary: Optional[dict] = Field(None, description="Itinerary output with location_list")


class SouvenirAgentInput(BaseModel):
    """Structured input for Souvenir Agent."""

    destination: str = Field(..., description="Destination location for souvenir recommendations")
    budget: float = Field(..., description="Budget allocated for souvenirs in VND", gt=0)
    travel_style: str = Field(..., description="Travel style to match souvenir recommendations")


class LogisticsAgentInput(BaseModel):
    """Structured input for Logistics Agent - specialized for flight tickets only."""

    departure_point: str = Field(..., description="Starting location/city/airport")
    destination: str = Field(..., description="Destination location/city/airport")
    departure_date: Union[str, date] = Field(..., description="Departure date (YYYY-MM-DD)")
    return_date: Union[str, date] = Field(..., description="Return date (YYYY-MM-DD)")
    num_travelers: int = Field(..., description="Number of travelers/passengers", gt=0)
    budget_per_person: float = Field(
        ..., description="Budget per person for round-trip flight in VND", gt=0
    )
    preferences: str = Field(
        default="",
        description="Flight preferences (e.g., 'direct flight', 'business class', 'morning departure')",
    )


class AccommodationAgentInput(BaseModel):
    """Structured input for Accommodation Agent."""

    destination: str = Field(..., description="Destination location/city")
    departure_date: Union[str, date] = Field(..., description="Check-in date (YYYY-MM-DD)")
    duration_nights: int = Field(..., description="Number of nights to stay", gt=0)
    budget_per_night: float = Field(..., description="Budget per night per room in VND", gt=0)
    num_travelers: int = Field(..., description="Number of travelers", gt=0)
    travel_style: str = Field(
        ..., description="Travel style: self_guided, tour, luxury, budget, adventure"
    )
    preferences: str = Field(
        default="",
        description="Accommodation preferences (e.g., 'close to city center', 'with pool', 'quiet area')",
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


class ItineraryAgentOutput(BaseModel):
    """Complete itinerary output from Itinerary Agent."""

    daily_schedules: List[DailySchedule] = Field(
        ..., description="Day-by-day schedule with activities"
    )
    location_list: List[str] = Field(
        ..., description="List of all unique location names mentioned in the itinerary"
    )
    summary: str = Field(..., description="Brief summary of the itinerary (2-3 sentences)")
    # NEW: Add selected flight and accommodation
    selected_flight: Optional[SelectedFlightInfo] = Field(
        None, description="Selected flight option for the trip"
    )
    selected_accommodation: Optional[SelectedAccommodationInfo] = Field(
        None, description="Selected accommodation for the trip"
    )


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


class SouvenirAgentOutput(BaseModel):
    """Souvenir recommendations from Souvenir Agent."""

    souvenirs: List[Souvenir] = Field(
        ..., description="List of recommended souvenir items (5-10 items)"
    )


class LogisticsAgentOutput(BaseModel):
    """Flight ticket information from Logistics Agent - specialized for flights only."""

    flight_options: List[FlightOption] = Field(
        ..., description="List of 3-5 flight ticket options with different airlines and times"
    )
    recommended_flight: Optional[str] = Field(
        None, description="Recommendation for best value flight option"
    )
    average_price: float = Field(
        ..., description="Average price per person across all options in VND"
    )
    booking_tips: List[str] = Field(
        ..., description="Tips for booking flights (best time, platforms, deals, etc.)"
    )
    visa_requirements: Optional[str] = Field(
        None, description="Brief visa requirements for the destination if available"
    )


class AccommodationAgentOutput(BaseModel):
    """Accommodation recommendations from Accommodation Agent."""

    recommendations: List[AccommodationOption] = Field(
        ..., description="List of 4-6 accommodation recommendations across budget ranges"
    )
    best_areas: List[str] = Field(
        ..., description="Top 3-5 recommended neighborhoods/districts with brief description"
    )
    average_price_per_night: float = Field(
        ..., description="Average price per night across recommendations in VND"
    )
    booking_tips: List[str] = Field(
        ..., description="Tips for booking (best time to book, platforms, deals, etc.)"
    )
    total_estimated_cost: float = Field(
        ..., description="Total estimated accommodation cost for the entire stay in VND"
    )


# ============ NOTE ============
# For public API schemas (TravelRequest, TravelPlan), see schemas/request.py and schemas/response.py
# This file contains only internal agent I/O schemas for the Agno framework
