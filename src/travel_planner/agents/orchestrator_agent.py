"""
Orchestrator Agent
Uses Agno Team for intelligent agent collaboration instead of manual orchestration
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

from config import settings

from .travel_planning_team import (
    TravelPlanningTeamInput,
    create_travel_planning_team,
    run_travel_planning_team,
)

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import API schemas (for request and response)
from schemas import (
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
    TravelRequest,
)


class OrchestratorAgent:
    """
    Orchestrator Agent using Agno Team for intelligent collaboration
    
    Instead of manually coordinating agents in phases, this uses Agno's Team
    feature where a team leader intelligently delegates tasks to specialist members.
    
    Benefits:
    - Automatic dependency resolution
    - Parallel execution when possible (using arun)
    - Intelligent task delegation
    - Natural collaboration between agents
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the orchestrator with Travel Planning Team
        
        Args:
            model: OpenAI model to use for all agents (default: gpt-4o-mini)
        """
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables")

        self.model = model

        print(f"[Orchestrator] Using API key: {settings.openai_api_key[:20]}...")

        # Create Travel Planning Team instead of individual agents
        self.travel_team = create_travel_planning_team(model)

        print(f"[Orchestrator] Travel Planning Team initialized with {len(self.travel_team.members)} specialist agents")
        print(f"[Orchestrator] Team members:")
        for member in self.travel_team.members:
            print(f"  - {member.name}: {member.role}")

    async def plan_trip(self, request: TravelRequest) -> TravelPlan:
        """
        Main method - delegates to Travel Planning Team
        
        Args:
            request: TravelRequest with all user inputs
            
        Returns:
            TravelPlan with comprehensive travel plan
        """
        print(f"\n{'=' * 80}")
        print(f"[Orchestrator] Starting Travel Planning Team workflow")
        print(f"[Orchestrator] Destination: {request.destination}")
        print(f"[Orchestrator] Departure Date: {request.departure_date}")
        print(f"[Orchestrator] Duration: {request.trip_duration} days")
        print(f"[Orchestrator] Budget: {request.budget:,.0f}")
        print(f"{'=' * 80}\n")

        # Convert TravelRequest to TravelPlanningTeamInput
        team_input = TravelPlanningTeamInput(
            destination=request.destination,
            departure_point=request.departure_point,
            departure_date=request.departure_date,
            trip_duration=request.trip_duration,
            budget=request.budget,
            num_travelers=request.num_travelers,
            travel_style=request.travel_style,
            customer_notes=request.customer_notes or "",
        )

        # Run Travel Planning Team (async for parallel execution)
        team_result = await run_travel_planning_team(
            team=self.travel_team,
            trip_request=team_input,
        )

        # Parse team response and compile into TravelPlan
        # Note: The team's response is synthesized by the team leader
        # We need to parse it and structure it according to our API schema
        
        print("\n[Orchestrator] ⚠️  Team returned synthesized response")
        print("[Orchestrator] 💡 For structured data, we need to extract from team response")
        print("[Orchestrator] 📋 Creating TravelPlan from team output...")
        
        # TODO: Parse team response and extract structured data
        # For now, return a basic plan with team response
        travel_plan = self._create_basic_plan_from_team_response(
            request=request,
            team_response=team_result["team_response"],
        )

        print("\n[Orchestrator] ✓ Travel Plan completed successfully!")
        print(f"{'=' * 80}\n")

        return travel_plan

    def _create_basic_plan_from_team_response(
        self,
        request: TravelRequest,
        team_response: str,
    ) -> TravelPlan:
        """
        Create a basic TravelPlan from team's synthesized response.
        
        Note: The team returns a synthesized natural language response.
        In production, you might want to:
        1. Use structured output from individual agents before synthesis
        2. Parse the team response with LLM
        3. Use respond_directly=True to get individual agent outputs
        
        Args:
            request: Original travel request
            team_response: Synthesized response from team leader
            
        Returns:
            TravelPlan with basic structure
        """
        # For now, create a minimal valid TravelPlan
        # The team_response contains all the information in natural language
        
        return TravelPlan(
            version="2.0-team",
            request_summary={
                "departure_point": request.departure_point,
                "destination": request.destination,
                "duration": request.trip_duration,
                "budget": request.budget,
                "travelers": request.num_travelers,
                "travel_style": request.travel_style,
                "customer_notes": request.customer_notes,
            },
            itinerary=ItineraryTimeline(
                daily_schedules=[],
                location_list=[],
                summary=f"Team-generated plan available in full response. {team_response[:200]}...",
                selected_flight=None,
                selected_accommodation=None,
            ),
            budget=BudgetBreakdown(
                categories=[],
                total_estimated_cost=0,
                budget_status="See team response for details",
                recommendations=[],
            ),
            advisory=AdvisoryInfo(
                warnings_and_tips=["See team response for comprehensive advisory information"],
                location_descriptions=[],
                visa_info="See team response",
                weather_info="See team response",
                sim_and_apps=[],
                safety_tips=[],
            ),
            souvenirs=[],
            logistics=LogisticsInfo(
                flight_options=[],
                recommended_flight="See team response",
                average_price=0,
                booking_tips=[],
                visa_requirements="See team response",
            ),
            accommodation=AccommodationInfo(
                recommendations=[],
                best_areas=[],
                average_price_per_night=0,
                booking_tips=[],
                total_estimated_cost=0,
            ),
            generated_at=datetime.utcnow().isoformat(),
            # Add team response as additional field
            team_full_response=team_response,
        )

import asyncio
import sys
from datetime import datetime
from pathlib import Path

from config import settings

from .accommodation_agent import create_accommodation_agent, run_accommodation_agent
from .advisory_agent import create_advisory_agent, run_advisory_agent
from .budget_agent import create_budget_agent, run_budget_agent
from .itinerary_agent import create_itinerary_agent, run_itinerary_agent
from .logistics_agent import create_logistics_agent, run_logistics_agent
from .souvenir_agent import create_souvenir_agent, run_souvenir_agent
from .utils import retry_on_timeout
from .weather_agent import create_weather_agent, run_weather_agent

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Agent schemas (for structured input/output with Agno)
from models.schemas import (
    AccommodationAgentOutput,
    AdvisoryAgentOutput,
    BudgetAgentOutput,
    ItineraryAgentOutput,
    LogisticsAgentOutput,
    SouvenirAgentOutput,
    WeatherAgentOutput,
)

# Import API schemas (for request and response)
from schemas import (
    AccommodationInfo,
    AccommodationOption,
    Activity,
    AdvisoryInfo,
    BudgetBreakdown,
    BudgetCategory,
    DaySchedule,
    ItineraryTimeline,
    LocationDescription,
    LogisticsInfo,
    SouvenirSuggestion,
    TravelPlan,
    TravelRequest,
)


class OrchestratorAgent:
    """
    Orchestrator Agent that manages the workflow and coordinates specialist agents

    Workflow:
    Phase 1: Run Itinerary, Logistics, and Souvenir agents in parallel
    Phase 2: After Itinerary completes, run Budget and Advisory agents (which depend on itinerary output)
    Phase 3: Compile results into a comprehensive travel plan
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the orchestrator and all specialist agents

        Args:
            model: OpenAI model to use for all agents (default: gpt-4o-mini)
        """
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables")

        self.model = model

        print(f"[Orchestrator] Using API key: {settings.openai_api_key[:20]}...")

        # Initialize all specialist agents - all using gpt-4o-mini
        self.weather_agent = create_weather_agent("gpt-4o-mini")
        self.itinerary_agent = create_itinerary_agent("gpt-4o-mini")
        self.budget_agent = create_budget_agent("gpt-4o-mini")
        self.advisory_agent = create_advisory_agent("gpt-4o-mini")
        self.souvenir_agent = create_souvenir_agent("gpt-4o-mini")
        self.logistics_agent = create_logistics_agent("gpt-4o-mini")
        self.accommodation_agent = create_accommodation_agent("gpt-4o-mini")

        print(f"[Orchestrator] All agents using gpt-4o-mini")
        print(
            f"[Orchestrator] Complex agents (Itinerary, Budget) have ReasoningTools enabled"
        )
        print(f"[Orchestrator] All 7 specialist agents ready (including Weather & Accommodation Agents)")

    async def plan_trip(self, request: TravelRequest) -> TravelPlan:
        """
        Main orchestration method - executes the complete workflow

        Args:
            request: TravelRequest with all user inputs

        Returns:
            TravelPlan with comprehensive travel plan
        """
        print(f"\n{'=' * 80}")
        print(f"[Orchestrator] Starting travel planning workflow")
        print(f"[Orchestrator] Destination: {request.destination}")
        print(f"[Orchestrator] Departure Date: {request.departure_date}")
        print(f"[Orchestrator] Duration: {request.trip_duration} days")
        print(f"[Orchestrator] Budget: {request.budget:,.0f}")
        print(f"{'=' * 80}\n")

        # --- PHASE 0: Run Weather Agent first (provides context for other agents) ---
        print("[Orchestrator] PHASE 0: Getting weather and seasonal information...")
        weather_result = await self._run_weather_agent(request)

        if weather_result:
            print(f"  ✓ Weather Agent: Success - Season: {weather_result.season}")
            if weather_result.seasonal_events:
                print(f"    Found {len(weather_result.seasonal_events)} events/festivals")
        else:
            print("  ⚠ Weather Agent: Failed - continuing without weather data")

        # --- PHASE 1: Run Logistics and Accommodation first (for itinerary to select from) ---
        print("\n[Orchestrator] PHASE 1: Getting flight and accommodation options...")
        print("  - Logistics Agent (5) - flight tickets")
        print("  - Accommodation Agent (6) - hotels/stays")

        phase1_tasks = [
            self._run_logistics_agent(request, weather_result),
            self._run_accommodation_agent(request),
        ]

        results_phase1 = await asyncio.gather(*phase1_tasks, return_exceptions=True)

        logistics_result = (
            results_phase1[0] if not isinstance(results_phase1[0], Exception) else None
        )
        accommodation_result = (
            results_phase1[1] if not isinstance(results_phase1[1], Exception) else None
        )

        print("\n[Orchestrator] PHASE 1 completed!")
        print(f"  ✓ Logistics Agent: {'Success' if logistics_result else 'Failed'}")
        print(f"  ✓ Accommodation Agent: {'Success' if accommodation_result else 'Failed'}")

        # --- PHASE 2: Run Itinerary with flight & accommodation selection + Souvenir ---
        print("\n[Orchestrator] PHASE 2: Creating itinerary with selections...")
        print("  - Itinerary Agent (1) - selects best flight & accommodation")
        print("  - Souvenir Agent (4)")

        phase2_tasks = [
            self._run_itinerary_agent(request, weather_result, logistics_result, accommodation_result),
            self._run_souvenir_agent(request),
        ]

        results_phase2 = await asyncio.gather(*phase2_tasks, return_exceptions=True)

        itinerary_result = (
            results_phase2[0] if not isinstance(results_phase2[0], Exception) else None
        )
        souvenir_result = (
            results_phase2[1] if not isinstance(results_phase2[1], Exception) else None
        )

        print("\n[Orchestrator] PHASE 2 completed!")
        print(f"  ✓ Itinerary Agent: {'Success' if itinerary_result else 'Failed'}")
        print(f"  ✓ Souvenir Agent: {'Success' if souvenir_result else 'Failed'}")

        # --- PHASE 3: Run dependent agents (need itinerary output) ---
        print("\n[Orchestrator] PHASE 3: Analyzing budget and advisory...")
        print("  - Budget Agent (2) - depends on itinerary")
        print("  - Advisory Agent (3) - depends on itinerary")

        phase3_tasks = [
            self._run_budget_agent(request, itinerary_result),
            self._run_advisory_agent(request, itinerary_result),
        ]

        results_phase3 = await asyncio.gather(*phase3_tasks, return_exceptions=True)

        budget_result = results_phase3[0] if not isinstance(results_phase3[0], Exception) else None
        advisory_result = (
            results_phase3[1] if not isinstance(results_phase3[1], Exception) else None
        )

        print("\n[Orchestrator] PHASE 3 completed!")
        print(f"  ✓ Budget Agent: {'Success' if budget_result else 'Failed'}")
        print(f"  ✓ Advisory Agent: {'Success' if advisory_result else 'Failed'}")

        # --- PHASE 4: Compile final travel plan ---
        print("\n[Orchestrator] PHASE 4: Compiling final travel plan...")

        travel_plan = self._compile_travel_plan(
            request=request,
            itinerary=itinerary_result,
            budget=budget_result,
            advisory=advisory_result,
            souvenirs=souvenir_result,
            logistics=logistics_result,
            accommodation=accommodation_result,
        )

        print("\n[Orchestrator] ✓ Travel Plan v1.0 completed successfully!")
        print(f"{'=' * 80}\n")

        return travel_plan

    async def _run_weather_agent(self, request: TravelRequest) -> WeatherAgentOutput:
        """Run Weather Agent to get forecast and seasonal information"""
        print("\n[Agent 0: Weather] Starting...")

        try:
            result = await retry_on_timeout(
                run_weather_agent,
                max_retries=3,
                timeout_delay=5.0,
                agent=self.weather_agent,
                destination=request.destination,
                departure_date=request.departure_date,
                duration_days=request.trip_duration,
            )

            print(f"[Agent 0: Weather] ✓ Completed")
            print(f"  - Season: {result.season}")
            print(f"  - Events: {len(result.seasonal_events or [])} found")

            return result
        except Exception as e:
            print(f"[Agent 0: Weather] ✗ Error: {str(e)}")
            # Return minimal weather data on error
            from models.schemas import WeatherAgentOutput

            return WeatherAgentOutput(
                destination=request.destination,
                season="Unknown",
                packing_recommendations=["Check weather forecast closer to departure date"],
                weather_summary=f"Weather information unavailable: {str(e)}",
            )

    async def _run_itinerary_agent(
        self, request: TravelRequest, weather_data: WeatherAgentOutput = None,
        logistics_data: LogisticsAgentOutput = None,
        accommodation_data: AccommodationAgentOutput = None
    ) -> ItineraryAgentOutput:
        """Run Itinerary Planner Agent with flight and accommodation selection"""
        print("\n[Agent 1: Itinerary Planner] Starting...")

        # Format weather info for agent
        weather_info = ""
        if weather_data:
            weather_info = f"Season: {weather_data.season}. {weather_data.weather_summary}"
            if weather_data.seasonal_events:
                weather_info += (
                    f" Events during this period: {', '.join(weather_data.seasonal_events[:3])}"
                )

        # Format flight options for agent selection
        available_flights = ""
        if logistics_data and logistics_data.flight_options:
            available_flights = "Available Flight Options:\n"
            for i, flight in enumerate(logistics_data.flight_options, 1):
                available_flights += f"{i}. {flight.airline} - {flight.flight_type}\n"
                available_flights += f"   Departure: {flight.departure_time}, Duration: {flight.duration}\n"
                available_flights += f"   Price: {flight.price_per_person:,.0f} VND/person, Class: {flight.cabin_class}\n"
                available_flights += f"   Benefits: {', '.join(flight.benefits[:3])}\n"
                if flight.notes:
                    available_flights += f"   Notes: {flight.notes}\n"

        # Format accommodation options for agent selection
        available_accommodations = ""
        if accommodation_data and accommodation_data.recommendations:
            available_accommodations = "Available Accommodation Options:\n"
            for i, hotel in enumerate(accommodation_data.recommendations, 1):
                available_accommodations += f"{i}. {hotel.name} ({hotel.type})\n"
                available_accommodations += f"   Area: {hotel.area}, Price: {hotel.price_per_night:,.0f} VND/night\n"
                if hotel.rating:
                    available_accommodations += f"   Rating: {hotel.rating}/5.0\n"
                available_accommodations += f"   Amenities: {', '.join(hotel.amenities[:4])}\n"

        try:
            # Wrap with retry mechanism
            result = await retry_on_timeout(
                run_itinerary_agent,
                max_retries=3,
                timeout_delay=5.0,
                agent=self.itinerary_agent,
                destination=request.destination,
                departure_date=request.departure_date,
                duration=request.trip_duration,
                travel_style=request.travel_style,
                customer_notes=request.customer_notes or "",
                weather_info=weather_info,
                available_flights=available_flights,
                available_accommodations=available_accommodations,
            )

            print(f"[Agent 1: Itinerary Planner] ✓ Completed")
            print(f"  - Generated {len(result.daily_schedules)} days of activities")
            print(f"  - Identified {len(result.location_list)} main locations")

            return result
        except Exception as e:
            print(f"[Agent 1: Itinerary Planner] ✗ Error: {str(e)}")
            # Return a minimal valid ItineraryAgentOutput
            return ItineraryAgentOutput(
                daily_schedules=[],
                location_list=[],
                summary=f"Error generating itinerary: {str(e)}",
            )

    async def _run_budget_agent(
        self, request: TravelRequest, itinerary_data: ItineraryAgentOutput
    ) -> BudgetAgentOutput:
        """Run Budgeting Agent (depends on itinerary)"""
        print("\n[Agent 2: Budgeting] Starting...")

        try:
            result = await run_budget_agent(
                agent=self.budget_agent,
                destination=request.destination,
                duration=request.trip_duration,
                budget=request.budget,
                num_travelers=request.num_travelers,
                itinerary_data=itinerary_data.model_dump() if itinerary_data else None,
            )

            print(f"[Agent 2: Budgeting] ✓ Completed")
            print(f"  - Total estimated cost: {result.total_estimated_cost:,.0f}")
            print(f"  - Status: {result.budget_status}")

            return result
        except Exception as e:
            print(f"[Agent 2: Budgeting] ✗ Error: {str(e)}")
            return BudgetAgentOutput(
                categories=[],
                total_estimated_cost=0,
                budget_status=f"Error: {str(e)}",
                recommendations=None,
            )

    async def _run_advisory_agent(
        self, request: TravelRequest, itinerary_data: ItineraryAgentOutput
    ) -> AdvisoryAgentOutput:
        """Run Advisory Agent (depends on itinerary for location descriptions)"""
        print("\n[Agent 3: Advisory] Starting...")

        try:
            location_list = itinerary_data.location_list if itinerary_data else []

            result = await run_advisory_agent(
                agent=self.advisory_agent,
                destination=request.destination,
                departure_date=request.departure_date,
                duration_days=request.trip_duration,
                location_list=location_list,
            )

            print(f"[Agent 3: Advisory] ✓ Completed")
            print(f"  - Generated {len(result.warnings_and_tips)} tips/warnings")
            print(f"  - Described {len(result.location_descriptions or [])} locations")

            return result
        except Exception as e:
            print(f"[Agent 3: Advisory] ✗ Error: {str(e)}")
            return AdvisoryAgentOutput(
                warnings_and_tips=[f"Error: {str(e)}"],
                location_descriptions=None,
                visa_info="Information unavailable",
                weather_info="Information unavailable",
                sim_and_apps=None,
                safety_tips=None,
            )

    async def _run_souvenir_agent(self, request: TravelRequest) -> SouvenirAgentOutput:
        """Run Souvenir Agent"""
        print("\n[Agent 4: Souvenir] Starting...")

        try:
            result = await run_souvenir_agent(
                agent=self.souvenir_agent, destination=request.destination
            )

            print(f"[Agent 4: Souvenir] ✓ Completed")
            print(f"  - Suggested {len(result.souvenirs)} souvenir items")

            return result
        except Exception as e:
            print(f"[Agent 4: Souvenir] ✗ Error: {str(e)}")
            from models.schemas import Souvenir

            return SouvenirAgentOutput(
                souvenirs=[
                    Souvenir(
                        item_name="Error",
                        description=str(e),
                        estimated_price="N/A",
                        where_to_buy="N/A",
                    )
                ]
            )

    async def _run_logistics_agent(
        self, request: TravelRequest, weather_data: WeatherAgentOutput = None
    ) -> LogisticsAgentOutput:
        """Run Logistics Agent - specialized for flight tickets"""
        print("\n[Agent 5: Logistics/Flights] Starting...")

        try:
            # Calculate return date (departure_date + trip_duration)
            from datetime import timedelta

            return_date = request.departure_date + timedelta(days=request.trip_duration)

            # Calculate budget per person for flights (assuming ~40% of total budget for flights)
            flight_budget = request.budget * 0.40
            budget_per_person = flight_budget / request.num_travelers

            result = await run_logistics_agent(
                agent=self.logistics_agent,
                departure_point=request.departure_point,
                destination=request.destination,
                departure_date=request.departure_date,
                return_date=return_date,
                num_travelers=request.num_travelers,
                budget_per_person=budget_per_person,
                preferences=request.customer_notes or "",
            )

            print(f"[Agent 5: Logistics/Flights] ✓ Completed")
            print(f"  - Found {len(result.flight_options)} flight options")
            print(f"  - Average price: {result.average_price:,.0f} VND/person")

            return result
        except Exception as e:
            print(f"[Agent 5: Logistics/Flights] ✗ Error: {str(e)}")
            from models.schemas import FlightOption

            return LogisticsAgentOutput(
                flight_options=[
                    FlightOption(
                        airline="Error",
                        flight_type="unknown",
                        departure_time="N/A",
                        duration="N/A",
                        price_per_person=0,
                        cabin_class="Economy",
                        benefits=[],
                        booking_platforms=[],
                        notes=str(e),
                    )
                ],
                recommended_flight=None,
                average_price=0,
                booking_tips=[],
                visa_requirements=None,
            )

    async def _run_accommodation_agent(self, request: TravelRequest) -> AccommodationAgentOutput:
        """Run Accommodation Agent"""
        print("\n[Agent 6: Accommodation] Starting...")

        try:
            # Calculate budget per night (assuming accommodation is ~30% of total budget)
            accommodation_budget = request.budget * 0.30
            budget_per_night = accommodation_budget / request.trip_duration

            result = await run_accommodation_agent(
                agent=self.accommodation_agent,
                destination=request.destination,
                departure_date=request.departure_date,
                duration=request.trip_duration,
                budget=budget_per_night,
                num_travelers=request.num_travelers,
                travel_style=request.travel_style,
                preferences=request.customer_notes or "",
            )

            print(f"[Agent 6: Accommodation] ✓ Completed")
            print(f"  - Found {len(result.recommendations)} accommodation options")
            print(f"  - Average price: {result.average_price_per_night:,.0f} VND/night")
            print(f"  - Total estimated: {result.total_estimated_cost:,.0f} VND")

            return result
        except Exception as e:
            print(f"[Agent 6: Accommodation] ✗ Error: {str(e)}")
            return AccommodationAgentOutput(
                recommendations=[],
                best_areas=[],
                average_price_per_night=0,
                booking_tips=[],
                total_estimated_cost=0,
            )

    def _compile_travel_plan(
        self,
        request: TravelRequest,
        itinerary: ItineraryAgentOutput,
        budget: BudgetAgentOutput,
        advisory: AdvisoryAgentOutput,
        souvenirs: SouvenirAgentOutput,
        logistics: LogisticsAgentOutput,
        accommodation: AccommodationAgentOutput,
    ) -> TravelPlan:
        """
        Compile all agent outputs into a structured TravelPlan

        Args:
            request: Original travel request
            itinerary: Output from Itinerary Agent (ItineraryAgentOutput)
            budget: Output from Budget Agent (BudgetAgentOutput)
            advisory: Output from Advisory Agent (AdvisoryAgentOutput)
            souvenirs: Output from Souvenir Agent (SouvenirAgentOutput)
            logistics: Output from Logistics Agent (LogisticsAgentOutput)
            accommodation: Output from Accommodation Agent (AccommodationAgentOutput)

        Returns:
            Complete TravelPlan object
        """
        # Convert Agent outputs to API response schemas
        # The agent outputs are already Pydantic models, so we can use them directly

        # Convert ItineraryAgentOutput to ItineraryTimeline (for API)
        # Need to convert DailySchedule (agent) to DaySchedule (API)
        api_daily_schedules = [
            DaySchedule(
                day_number=schedule.day_number,
                date=schedule.date,
                title=schedule.title,
                activities=[Activity(**activity.model_dump()) for activity in schedule.activities],
            )
            for schedule in itinerary.daily_schedules
        ]

        # Convert selected flight and accommodation from itinerary
        from schemas import SelectedFlightInfo, SelectedAccommodationInfo

        selected_flight_api = None
        if itinerary.selected_flight:
            selected_flight_api = SelectedFlightInfo(**itinerary.selected_flight.model_dump())

        selected_accommodation_api = None
        if itinerary.selected_accommodation:
            selected_accommodation_api = SelectedAccommodationInfo(
                **itinerary.selected_accommodation.model_dump()
            )

        itinerary_timeline = ItineraryTimeline(
            daily_schedules=api_daily_schedules,
            location_list=itinerary.location_list,
            summary=itinerary.summary,
            selected_flight=selected_flight_api,
            selected_accommodation=selected_accommodation_api,
        )

        # Convert BudgetAgentOutput to BudgetBreakdown (for API)
        budget_breakdown = BudgetBreakdown(
            categories=[BudgetCategory(**category.model_dump()) for category in budget.categories],
            total_estimated_cost=budget.total_estimated_cost,
            budget_status=budget.budget_status,
            recommendations=budget.recommendations or [],
        )

        # Convert AdvisoryAgentOutput to AdvisoryInfo (for API)
        advisory_info = AdvisoryInfo(
            warnings_and_tips=advisory.warnings_and_tips,
            location_descriptions=[
                LocationDescription(**location.model_dump())
                for location in advisory.location_descriptions or []
            ],
            visa_info=advisory.visa_info,
            weather_info=advisory.weather_info,
            sim_and_apps=advisory.sim_and_apps or [],
            safety_tips=advisory.safety_tips or [],
        )

        # Convert SouvenirAgentOutput to List[SouvenirSuggestion] (for API)
        souvenir_suggestions = [
            SouvenirSuggestion(**souvenir.model_dump()) for souvenir in souvenirs.souvenirs
        ]

        # Convert LogisticsAgentOutput to LogisticsInfo (for API)
        from schemas import FlightOption as FlightOptionAPI

        logistics_info = LogisticsInfo(
            flight_options=[
                FlightOptionAPI(**flight.model_dump()) for flight in logistics.flight_options
            ],
            recommended_flight=logistics.recommended_flight,
            average_price=logistics.average_price,
            booking_tips=logistics.booking_tips,
            visa_requirements=logistics.visa_requirements,
        )

        # Convert AccommodationAgentOutput to AccommodationInfo (for API)
        accommodation_info = None
        if accommodation and accommodation.recommendations:
            accommodation_info = AccommodationInfo(
                recommendations=[
                    AccommodationOption(**option.model_dump())
                    for option in accommodation.recommendations
                ],
                best_areas=accommodation.best_areas,
                average_price_per_night=accommodation.average_price_per_night,
                booking_tips=accommodation.booking_tips,
                total_estimated_cost=accommodation.total_estimated_cost,
            )

        # Create final travel plan
        travel_plan = TravelPlan(
            version="1.0",
            request_summary={
                "departure_point": request.departure_point,
                "destination": request.destination,
                "duration": request.trip_duration,
                "budget": request.budget,
                "travelers": request.num_travelers,
                "travel_style": request.travel_style,
                "customer_notes": request.customer_notes,
            },
            itinerary=itinerary_timeline,
            budget=budget_breakdown,
            advisory=advisory_info,
            souvenirs=souvenir_suggestions,
            logistics=logistics_info,
            accommodation=accommodation_info,
            generated_at=datetime.utcnow().isoformat(),
        )

        return travel_plan
