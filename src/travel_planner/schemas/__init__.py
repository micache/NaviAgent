"""
Schemas package for Travel Planner API
"""

from .request import TravelRequest
from .response import (
    AccommodationInfo,
    AccommodationOption,
    Activity,
    AdvisoryInfo,
    BudgetBreakdown,
    BudgetCategory,
    DaySchedule,
    FlightOption,
    ItineraryTimeline,
    LocationDescription,
    LogisticsInfo,
    SelectedAccommodationInfo,
    SelectedFlightInfo,
    SouvenirSuggestion,
    TravelPlan,
    TravelPlanTeamResponse,
)

__all__ = [
    "TravelRequest",
    "TravelPlan",
    "TravelPlanTeamResponse",
    "ItineraryTimeline",
    "DaySchedule",
    "Activity",
    "BudgetBreakdown",
    "BudgetCategory",
    "LocationDescription",
    "AdvisoryInfo",
    "SouvenirSuggestion",
    "LogisticsInfo",
    "FlightOption",
    "AccommodationInfo",
    "AccommodationOption",
    "SelectedFlightInfo",
    "SelectedAccommodationInfo",
]
