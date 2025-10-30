"""
Orchestrator Agent
Coordinates the workflow and manages dependencies between specialist agents
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

from config import settings

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
    AdvisoryAgentOutput,
    BudgetAgentOutput,
    ItineraryAgentOutput,
    LogisticsAgentOutput,
    SouvenirAgentOutput,
    WeatherAgentOutput,
)

# Import API schemas (for request and response)
from schemas import (
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

        print(f"[Orchestrator] All agents using gpt-4o-mini")
        print(
            f"[Orchestrator] Complex agents (Itinerary, Budget, Logistics) have ReasoningTools enabled"
        )
        print(f"[Orchestrator] All 6 specialist agents ready (including Weather Agent)")

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

        # --- PHASE 1: Run independent agents in parallel ---
        print("\n[Orchestrator] PHASE 1: Starting independent agents in parallel...")
        print("  - Itinerary Planner Agent (1) - with weather context")
        print("  - Logistics Agent (5) - with weather context")
        print("  - Souvenir Agent (4)")

        phase1_tasks = [
            self._run_itinerary_agent(request, weather_result),
            self._run_logistics_agent(request, weather_result),
            self._run_souvenir_agent(request),
        ]

        # Wait for Phase 1 to complete
        results_phase1 = await asyncio.gather(*phase1_tasks, return_exceptions=True)

        itinerary_result = (
            results_phase1[0] if not isinstance(results_phase1[0], Exception) else None
        )
        logistics_result = (
            results_phase1[1] if not isinstance(results_phase1[1], Exception) else None
        )
        souvenir_result = (
            results_phase1[2] if not isinstance(results_phase1[2], Exception) else None
        )

        print("\n[Orchestrator] PHASE 1 completed!")
        print(f"  ✓ Itinerary Agent: {'Success' if itinerary_result else 'Failed'}")
        print(f"  ✓ Logistics Agent: {'Success' if logistics_result else 'Failed'}")
        print(f"  ✓ Souvenir Agent: {'Success' if souvenir_result else 'Failed'}")

        # --- PHASE 2: Run dependent agents (need itinerary output) ---
        print("\n[Orchestrator] PHASE 2: Starting dependent agents in parallel...")
        print("  - Budget Agent (2) - depends on itinerary")
        print("  - Advisory Agent (3) - depends on itinerary")

        phase2_tasks = [
            self._run_budget_agent(request, itinerary_result),
            self._run_advisory_agent(request, itinerary_result),
        ]

        # Wait for Phase 2 to complete
        results_phase2 = await asyncio.gather(*phase2_tasks, return_exceptions=True)

        budget_result = results_phase2[0] if not isinstance(results_phase2[0], Exception) else None
        advisory_result = (
            results_phase2[1] if not isinstance(results_phase2[1], Exception) else None
        )

        print("\n[Orchestrator] PHASE 2 completed!")
        print(f"  ✓ Budget Agent: {'Success' if budget_result else 'Failed'}")
        print(f"  ✓ Advisory Agent: {'Success' if advisory_result else 'Failed'}")

        # --- PHASE 3: Compile final travel plan ---
        print("\n[Orchestrator] PHASE 3: Compiling final travel plan...")

        travel_plan = self._compile_travel_plan(
            request=request,
            itinerary=itinerary_result,
            budget=budget_result,
            advisory=advisory_result,
            souvenirs=souvenir_result,
            logistics=logistics_result,
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
        self, request: TravelRequest, weather_data: WeatherAgentOutput = None
    ) -> ItineraryAgentOutput:
        """Run Itinerary Planner Agent with retry"""
        print("\n[Agent 1: Itinerary Planner] Starting...")

        # Format weather info for agent
        weather_info = ""
        if weather_data:
            weather_info = f"Season: {weather_data.season}. {weather_data.weather_summary}"
            if weather_data.seasonal_events:
                weather_info += (
                    f" Events during this period: {', '.join(weather_data.seasonal_events[:3])}"
                )

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
        """Run Logistics Agent"""
        print("\n[Agent 5: Logistics] Starting...")

        # Format weather info for agent
        weather_info = ""
        if weather_data:
            weather_info = f"Season: {weather_data.season}. {weather_data.weather_summary}"

        try:
            result = await run_logistics_agent(
                agent=self.logistics_agent,
                departure_point=request.departure_point,
                destination=request.destination,
                departure_date=request.departure_date,
                budget=request.budget,
                duration=request.trip_duration,
                weather_info=weather_info,
            )

            print(f"[Agent 5: Logistics] ✓ Completed")
            if result.estimated_flight_cost:
                print(f"  - Estimated flight cost: {result.estimated_flight_cost:,.0f}")

            return result
        except Exception as e:
            print(f"[Agent 5: Logistics] ✗ Error: {str(e)}")
            return LogisticsAgentOutput(
                flight_info=f"Error: {str(e)}",
                estimated_flight_cost=0,
                accommodation_suggestions=[],
                transportation_tips=[],
            )

    def _compile_travel_plan(
        self,
        request: TravelRequest,
        itinerary: ItineraryAgentOutput,
        budget: BudgetAgentOutput,
        advisory: AdvisoryAgentOutput,
        souvenirs: SouvenirAgentOutput,
        logistics: LogisticsAgentOutput,
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

        itinerary_timeline = ItineraryTimeline(
            daily_schedules=api_daily_schedules,
            location_list=itinerary.location_list,
            summary=itinerary.summary,
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
        logistics_info = LogisticsInfo(**logistics.model_dump())

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
            generated_at=datetime.utcnow().isoformat(),
        )

        return travel_plan
