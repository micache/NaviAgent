"""
Orchestrator Agent
Coordinates the workflow and manages dependencies between specialist agents
"""

import asyncio

# Import schemas - THÊM DÒNG NÀY
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

from config import settings

from .advisory_agent import create_advisory_agent, run_advisory_agent
from .budget_agent import create_budget_agent, run_budget_agent
from .itinerary_agent import create_itinerary_agent, run_itinerary_agent
from .logistics_agent import create_logistics_agent, run_logistics_agent
from .souvenir_agent import create_souvenir_agent, run_souvenir_agent
from .utils import retry_on_timeout

sys.path.insert(0, str(Path(__file__).parent.parent))

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

    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the orchestrator and all specialist agents

        Args:
            model: OpenAI model to use for all agents
        """
        # Kiểm tra API key trước khi khởi tạo
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables")

        self.model = model

        print(f"[Orchestrator] Using API key: {settings.openai_api_key[:20]}...")

        # Initialize all specialist agents
        self.itinerary_agent = create_itinerary_agent(model)
        self.budget_agent = create_budget_agent(model)
        self.advisory_agent = create_advisory_agent(model)
        self.souvenir_agent = create_souvenir_agent(model)
        self.logistics_agent = create_logistics_agent(model)

        print(f"[Orchestrator] Initialized with model: {model}")
        print(f"[Orchestrator] All 5 specialist agents ready")

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
        print(f"[Orchestrator] Duration: {request.trip_duration} days")
        print(f"[Orchestrator] Budget: {request.budget:,.0f}")
        print(f"{'=' * 80}\n")

        # --- PHASE 1: Run independent agents in parallel ---
        print("[Orchestrator] PHASE 1: Starting independent agents in parallel...")
        print("  - Itinerary Planner Agent (1)")
        print("  - Logistics Agent (5)")
        print("  - Souvenir Agent (4)")

        phase1_tasks = [
            self._run_itinerary_agent(request),
            self._run_logistics_agent(request),
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

    async def _run_itinerary_agent(self, request: TravelRequest) -> Dict:
        """Run Itinerary Planner Agent with retry"""
        print("\n[Agent 1: Itinerary Planner] Starting...")

        try:
            # Wrap with retry mechanism
            result = await retry_on_timeout(
                run_itinerary_agent,
                max_retries=3,
                timeout_delay=5.0,
                agent=self.itinerary_agent,
                destination=request.destination,
                duration=request.trip_duration,
                travel_style=request.travel_style,
                customer_notes=request.customer_notes or "",
            )

            print(f"[Agent 1: Itinerary Planner] ✓ Completed")
            print(f"  - Generated {len(result.get('daily_schedules', []))} days of activities")
            print(f"  - Identified {len(result.get('location_list', []))} main locations")

            return result
        except Exception as e:
            print(f"[Agent 1: Itinerary Planner] ✗ Error: {str(e)}")
            return {
                "daily_schedules": [],
                "location_list": [],
                "summary": f"Error: {str(e)}",
            }

    async def _run_budget_agent(self, request: TravelRequest, itinerary_data: Dict) -> Dict:
        """Run Budgeting Agent (depends on itinerary)"""
        print("\n[Agent 2: Budgeting] Starting...")

        try:
            result = await run_budget_agent(
                agent=self.budget_agent,
                destination=request.destination,
                duration=request.trip_duration,
                budget=request.budget,
                num_travelers=request.num_travelers,
                itinerary_data=itinerary_data,
            )

            print(f"[Agent 2: Budgeting] ✓ Completed")
            print(f"  - Total estimated cost: {result.get('total_estimated_cost', 0):,.0f}")
            print(f"  - Status: {result.get('budget_status', 'Unknown')}")

            return result
        except Exception as e:
            print(f"[Agent 2: Budgeting] ✗ Error: {str(e)}")
            return {
                "categories": [],
                "total_estimated_cost": 0,
                "budget_status": f"Error: {str(e)}",
                "recommendations": [],
            }

    async def _run_advisory_agent(self, request: TravelRequest, itinerary_data: Dict) -> Dict:
        """Run Advisory Agent (depends on itinerary for location descriptions)"""
        print("\n[Agent 3: Advisory] Starting...")

        try:
            location_list = itinerary_data.get("location_list", []) if itinerary_data else []

            result = await run_advisory_agent(
                agent=self.advisory_agent,
                destination=request.destination,
                travel_date=datetime.now().strftime("%B %Y"),
                location_list=location_list,
            )

            print(f"[Agent 3: Advisory] ✓ Completed")
            print(f"  - Generated {len(result.get('warnings_and_tips', []))} tips/warnings")
            print(f"  - Described {len(result.get('location_descriptions', []))} locations")

            return result
        except Exception as e:
            print(f"[Agent 3: Advisory] ✗ Error: {str(e)}")
            return {
                "warnings_and_tips": [f"Error: {str(e)}"],
                "location_descriptions": [],
                "visa_info": None,
                "weather_info": None,
                "sim_and_apps": [],
                "safety_tips": [],
            }

    async def _run_souvenir_agent(self, request: TravelRequest) -> list:
        """Run Souvenir Agent"""
        print("\n[Agent 4: Souvenir] Starting...")

        try:
            result = await run_souvenir_agent(
                agent=self.souvenir_agent, destination=request.destination
            )

            print(f"[Agent 4: Souvenir] ✓ Completed")
            print(f"  - Suggested {len(result)} souvenir items")

            return result
        except Exception as e:
            print(f"[Agent 4: Souvenir] ✗ Error: {str(e)}")
            return [
                {
                    "item_name": "Error",
                    "description": str(e),
                    "estimated_price": "N/A",
                    "where_to_buy": "N/A",
                }
            ]

    async def _run_logistics_agent(self, request: TravelRequest) -> Dict:
        """Run Logistics Agent"""
        print("\n[Agent 5: Logistics] Starting...")

        try:
            result = await run_logistics_agent(
                agent=self.logistics_agent,
                departure_point=request.departure_point,
                destination=request.destination,
                budget=request.budget,
                duration=request.trip_duration,
            )

            print(f"[Agent 5: Logistics] ✓ Completed")
            if result.get("estimated_flight_cost"):
                print(f"  - Estimated flight cost: {result['estimated_flight_cost']:,.0f}")

            return result
        except Exception as e:
            print(f"[Agent 5: Logistics] ✗ Error: {str(e)}")
            return {
                "flight_info": f"Error: {str(e)}",
                "estimated_flight_cost": None,
                "accommodation_suggestions": [],
                "transportation_tips": [],
            }

    def _compile_travel_plan(
        self,
        request: TravelRequest,
        itinerary: Dict,
        budget: Dict,
        advisory: Dict,
        souvenirs: list,
        logistics: Dict,
    ) -> TravelPlan:
        """
        Compile all agent outputs into a structured TravelPlan

        Args:
            request: Original travel request
            itinerary: Output from Itinerary Agent
            budget: Output from Budget Agent
            advisory: Output from Advisory Agent
            souvenirs: Output from Souvenir Agent
            logistics: Output from Logistics Agent

        Returns:
            Complete TravelPlan object
        """
        # Convert raw data to Pydantic models

        # Itinerary
        daily_schedules = []
        for day_data in itinerary.get("daily_schedules", []):
            activities = [
                Activity(**act) if isinstance(act, dict) else act
                for act in day_data.get("activities", [])
            ]
            daily_schedules.append(
                DaySchedule(
                    day_number=day_data.get("day_number", 1),
                    date=day_data.get("date"),
                    title=day_data.get("title", f"Day {day_data.get('day_number', 1)}"),
                    activities=activities,
                )
            )

        itinerary_timeline = ItineraryTimeline(
            daily_schedules=daily_schedules,
            location_list=itinerary.get("location_list", []),
            summary=itinerary.get("summary"),
        )

        # Budget
        budget_categories = [
            BudgetCategory(**cat) if isinstance(cat, dict) else cat
            for cat in budget.get("categories", [])
        ]

        budget_breakdown = BudgetBreakdown(
            categories=budget_categories,
            total_estimated_cost=budget.get("total_estimated_cost", 0),
            budget_status=budget.get("budget_status", "Unknown"),
            recommendations=budget.get("recommendations"),
        )

        # Advisory
        location_descriptions = [
            LocationDescription(**loc) if isinstance(loc, dict) else loc
            for loc in advisory.get("location_descriptions", [])
        ]

        advisory_info = AdvisoryInfo(
            warnings_and_tips=advisory.get("warnings_and_tips", []),
            location_descriptions=location_descriptions,
            visa_info=advisory.get("visa_info"),
            weather_info=advisory.get("weather_info"),
            sim_and_apps=advisory.get("sim_and_apps"),
            safety_tips=advisory.get("safety_tips"),
        )

        # Souvenirs
        souvenir_suggestions = [
            SouvenirSuggestion(**item) if isinstance(item, dict) else item for item in souvenirs
        ]

        # Logistics
        logistics_info = LogisticsInfo(
            flight_info=logistics.get("flight_info"),
            estimated_flight_cost=logistics.get("estimated_flight_cost"),
            accommodation_suggestions=logistics.get("accommodation_suggestions"),
            transportation_tips=logistics.get("transportation_tips"),
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
            generated_at=datetime.utcnow().isoformat(),
        )

        return travel_plan
