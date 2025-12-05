"""Orchestrator Agent - Coordinates 7 specialists in 5 phases"""

import asyncio
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import model_settings, settings
from config.database import get_db
from models.schemas import (
    AccommodationAgentInput,
    AdvisoryAgentInput,
    BudgetAgentInput,
    ItineraryAgentInput,
    LogisticsAgentInput,
    SouvenirAgentInput,
    WeatherAgentInput,
)
from schemas import (
    AccommodationInfo,
    AdvisoryInfo,
    BudgetBreakdown,
    ItineraryTimeline,
    LogisticsInfo,
    TravelPlan,
    TravelRequest,
)

from .accommodation_agent import create_accommodation_agent
from .advisory_agent import create_advisory_agent
from .budget_agent import create_budget_agent
from .itinerary_agent import create_itinerary_agent
from .logistics_agent import create_logistics_agent
from .souvenir_agent import create_souvenir_agent
from .weather_agent import create_weather_agent


class OrchestratorAgent:
    """
    Orchestrator Agent - Coordinates 7 specialist agents in 5 sequential phases

    Pipeline Architecture:
    =====================
    Phase 1: Context Gathering
      └─ Weather Agent: Provides season, temperature, events for planning context

    Phase 2: Options Research (Parallel)
      ├─ Logistics Agent: Finds 3-5 flight options (different airlines, times, prices)
      └─ Accommodation Agent: Finds 4-6 hotel options (different areas, budgets, types)

    Phase 3: Core Planning & Selection
      └─ Itinerary Agent:
           • Selects BEST flight from Phase 2 options
           • Selects BEST hotel from Phase 2 options
           • Creates day-by-day itinerary with activities
           • Outputs: selected_flight, selected_accommodation, daily_schedule

    Phase 4: Analysis & Recommendations (Parallel)
      ├─ Budget Agent: Analyzes costs using selected flight/hotel from Phase 3
      ├─ Souvenir Agent: Recommends gifts within budget
      └─ Advisory Agent: Safety tips, visa info, location descriptions

    Phase 5: Compilation
      └─ Build final TravelPlan with all structured data

    Key Design Principles:
    =====================
    1. Structured I/O: All agents use Pydantic schemas (no natural language delegation)
    2. Clear Dependencies: Phase 3 depends on Phase 2, Phase 4 depends on Phase 3
    3. Parallel Execution: Phases 2 and 4 run agents in parallel for speed
    4. Single Source of Truth: Itinerary Agent makes all selection decisions
    5. No Redundancy: Each agent has a specific role, no overlap
    """

    def __init__(self, user_id: str = None, session_id: str = None, enable_memory: bool = True):
        """
        Initialize orchestrator with all 7 specialist agents using centralized model config

        Args:
            user_id: User ID for session and memory tracking
            session_id: Session ID for conversation continuity across multiple runs
            enable_memory: Enable user memory management across agents (default: True)
        """
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set")

        # Get shared database instance for all agents
        self.db = get_db()
        self.user_id = user_id
        self.session_id = session_id
        self.enable_memory = enable_memory

        # Create all agents using centralized model configuration with database support
        # Each agent will automatically use the model specified in model_settings
        # AND share the same database for session/memory tracking
        self.weather_agent = create_weather_agent(
            "weather", db=self.db, user_id=user_id, enable_memory=enable_memory
        )
        self.logistics_agent = create_logistics_agent(
            "logistics", db=self.db, user_id=user_id, enable_memory=enable_memory
        )
        self.accommodation_agent = create_accommodation_agent(
            "accommodation", db=self.db, user_id=user_id, enable_memory=enable_memory
        )
        self.itinerary_agent = create_itinerary_agent(
            "itinerary", db=self.db, user_id=user_id, enable_memory=enable_memory
        )
        self.budget_agent = create_budget_agent(
            "budget", db=self.db, user_id=user_id, enable_memory=enable_memory
        )
        self.souvenir_agent = create_souvenir_agent(
            "souvenir", db=self.db, user_id=user_id, enable_memory=enable_memory
        )
        self.advisory_agent = create_advisory_agent(
            "advisory", db=self.db, user_id=user_id, enable_memory=enable_memory
        )

        # Print configuration summary
        print("[Orchestrator] ✓ 7 specialist agents initialized")
        print(f"[Orchestrator] ✓ Model provider: {model_settings.default_provider.value}")
        print(
            f"[Orchestrator] ✓ Default model: {model_settings.model_mappings[model_settings.default_provider]}"
        )
        print(f"[Orchestrator] ✓ Database: Connected to PostgreSQL (Supabase)")
        print(f"[Orchestrator] ✓ User tracking: {'Enabled' if user_id else 'Disabled'}")
        print(f"[Orchestrator] ✓ Memory management: {'Enabled' if enable_memory else 'Disabled'}")
        print(f"[Orchestrator] ✓ 5-phase sequential workflow ready")

    async def plan_trip(self, request: TravelRequest, session_id: str = None) -> TravelPlan:
        """
        Execute 5-phase travel planning workflow with structured I/O

        Workflow:
        1. Weather → 2. Options (Parallel) → 3. Itinerary (Selector) → 4. Analysis (Parallel) → 5. Compilation

        Args:
            request: TravelRequest with planning parameters
            session_id: Optional session ID for this planning session (overrides instance session_id)
        """
        # Use provided session_id or fall back to instance session_id
        active_session_id = session_id or self.session_id

        print(f"\n{'=' * 80}")
        print(f"🌍 ORCHESTRATOR - 5-Phase Travel Planning Pipeline")
        print(f"{'=' * 80}")
        print(f"📍 Destination: {request.destination}")
        print(f"📅 Dates: {request.departure_date} ({request.trip_duration} days)")
        print(f"💰 Budget: {request.budget:,.0f} VND")
        print(f"👥 Travelers: {request.num_travelers}")
        print(f"🎯 Style: {request.travel_style}")
        if self.user_id:
            print(f"👤 User: {self.user_id}")
        if active_session_id:
            print(f"💬 Session: {active_session_id}")
        print(f"{'=' * 80}\n")

        return_date = request.departure_date + timedelta(days=request.trip_duration)

        # Convert date objects to strings for JSON serialization in Agno session storage
        departure_date_str = request.departure_date.isoformat()
        return_date_str = return_date.isoformat()

        # =====================================================================
        # PHASE 1: WEATHER CONTEXT
        # =====================================================================
        print(f"📊 [Phase 1] Weather Context Provider")
        print(f"   → Getting season, temperature, and events...")

        weather_response = await self.weather_agent.arun(
            WeatherAgentInput(
                destination=request.destination,
                departure_date=departure_date_str,
                duration_days=request.trip_duration,
            ),
            session_id=active_session_id,
        )
        weather_out = weather_response.content

        print(f"   ✓ Season: {weather_out.season if weather_out else 'N/A'}")
        print(f"   ✓ Weather info provided for planning\n")

        # =====================================================================
        # PHASE 2: OPTIONS RESEARCH (PARALLEL)
        # =====================================================================
        print(f"🔍 [Phase 2] Options Research (Parallel Execution)")
        print(f"   → Logistics Agent: Finding 3-5 flight options...")
        print(f"   → Accommodation Agent: Finding 4-6 hotel options...")

        # Calculate budget allocations
        flight_budget_per_person = (
            request.budget * 0.40
        ) / request.num_travelers  # 40% for flights
        accommodation_budget_per_night = (
            request.budget * 0.30
        ) / request.trip_duration  # 30% for accommodation

        logistics_response, accommodation_response = await asyncio.gather(
            self.logistics_agent.arun(
                LogisticsAgentInput(
                    destination=request.destination,
                    departure_point=request.departure_point,
                    departure_date=departure_date_str,
                    return_date=return_date_str,
                    num_travelers=request.num_travelers,
                    budget_per_person=flight_budget_per_person,
                    preferences=request.customer_notes or "",
                ),
                session_id=active_session_id,
            ),
            self.accommodation_agent.arun(
                AccommodationAgentInput(
                    destination=request.destination,
                    departure_date=departure_date_str,
                    duration_nights=request.trip_duration,
                    budget_per_night=accommodation_budget_per_night,
                    num_travelers=request.num_travelers,
                    travel_style=request.travel_style,
                    preferences=request.customer_notes or "",
                ),
                session_id=active_session_id,
            ),
        )
        logistics_out = logistics_response.content
        accommodation_out = accommodation_response.content

        flight_count = len(logistics_out.flight_options) if logistics_out.flight_options else 0
        hotel_count = (
            len(accommodation_out.recommendations) if accommodation_out.recommendations else 0
        )
        print(f"   ✓ Found {flight_count} flight options")
        print(f"   ✓ Found {hotel_count} accommodation options\n")

        # =====================================================================
        # PHASE 3: ITINERARY PLANNING & SELECTION
        # =====================================================================
        print(f"🎯 [Phase 3] Itinerary Planning & Selection (Core Phase)")
        print(f"   → Analyzing {flight_count} flights + {hotel_count} hotels...")
        print(f"   → Selecting best flight and accommodation...")
        print(f"   → Creating day-by-day itinerary...")

        itinerary_response = await self.itinerary_agent.arun(
            ItineraryAgentInput(
                destination=request.destination,
                departure_date=departure_date_str,
                duration_days=request.trip_duration,
                num_travelers=request.num_travelers,
                total_budget=request.budget,
                travel_style=request.travel_style,
                preferences=request.customer_notes or "",
                weather_info=weather_out.model_dump() if weather_out else None,
                available_flights=(
                    [f.model_dump() for f in logistics_out.flight_options]
                    if logistics_out.flight_options
                    else []
                ),
                available_accommodations=(
                    [a.model_dump() for a in accommodation_out.recommendations]
                    if accommodation_out.recommendations
                    else []
                ),
            ),
            session_id=active_session_id,
        )
        itinerary_out = itinerary_response.content

        days_count = len(itinerary_out.daily_schedules) if itinerary_out.daily_schedules else 0
        print(f"   ✓ Created {days_count}-day itinerary")
        if itinerary_out.selected_flight:
            print(f"   ✓ Selected Flight: {itinerary_out.selected_flight.airline}")
        if itinerary_out.selected_accommodation:
            print(f"   ✓ Selected Hotel: {itinerary_out.selected_accommodation.name}\n")

        # =====================================================================
        # PHASE 4: ANALYSIS & RECOMMENDATIONS (PARALLEL)
        # =====================================================================
        print(f"📈 [Phase 4] Analysis & Recommendations (Parallel Execution)")
        print(f"   → Budget Agent: Analyzing costs with selected flight/hotel...")
        print(f"   → Souvenir Agent: Finding gift recommendations...")
        print(f"   → Advisory Agent: Safety tips & location descriptions...")

        budget_response, souvenir_response, advisory_response = await asyncio.gather(
            self.budget_agent.arun(
                BudgetAgentInput(
                    destination=request.destination,
                    trip_duration=request.trip_duration,
                    num_travelers=request.num_travelers,
                    total_budget=request.budget,
                    itinerary=itinerary_out.model_dump() if itinerary_out else None,
                    selected_flight_cost=(
                        itinerary_out.selected_flight.total_cost
                        if itinerary_out.selected_flight
                        else 0
                    ),
                    selected_accommodation_cost=(
                        itinerary_out.selected_accommodation.total_cost
                        if itinerary_out.selected_accommodation
                        else 0
                    ),
                ),
                session_id=active_session_id,
            ),
            self.souvenir_agent.arun(
                SouvenirAgentInput(
                    destination=request.destination,
                    budget=request.budget * 0.05,
                    travel_style=request.travel_style,
                ),
                session_id=active_session_id,
            ),
            self.advisory_agent.arun(
                AdvisoryAgentInput(
                    destination=request.destination,
                    trip_duration=request.trip_duration,
                    travel_style=request.travel_style,
                    itinerary=itinerary_out.model_dump() if itinerary_out else None,
                ),
                session_id=active_session_id,
            ),
        )
        budget_out = budget_response.content
        souvenir_out = souvenir_response.content
        advisory_out = advisory_response.content

        print(f"   ✓ Budget Status: {budget_out.budget_status}")
        print(f"   ✓ Total Estimated: {budget_out.total_estimated_cost:,.0f} VND")
        print(
            f"   ✓ Souvenirs: {len(souvenir_out.souvenirs) if souvenir_out.souvenirs else 0} items"
        )
        print(
            f"   ✓ Advisory: {len(advisory_out.warnings_and_tips) if advisory_out.warnings_and_tips else 0} tips\n"
        )

        # =====================================================================
        # PHASE 5: COMPILATION
        # =====================================================================
        print(f"📦 [Phase 5] Compiling Comprehensive Travel Plan...")
        from datetime import datetime

        travel_plan = TravelPlan(
            version="3.0-orchestrated",
            request_summary={
                "destination": request.destination,
                "departure_point": request.departure_point,
                "departure_date": str(request.departure_date),
                "trip_duration": request.trip_duration,
                "budget": request.budget,
                "num_travelers": request.num_travelers,
                "travel_style": request.travel_style,
                "customer_notes": request.customer_notes,
            },
            itinerary=ItineraryTimeline(
                daily_schedules=itinerary_out.daily_schedules,
                location_list=itinerary_out.location_list,
                summary=itinerary_out.summary,
                selected_flight=itinerary_out.selected_flight,
                selected_accommodation=itinerary_out.selected_accommodation,
            ),
            budget=BudgetBreakdown(
                categories=budget_out.categories,
                total_estimated_cost=budget_out.total_estimated_cost,
                budget_status=budget_out.budget_status,
                recommendations=budget_out.recommendations,
            ),
            advisory=AdvisoryInfo(
                warnings_and_tips=advisory_out.warnings_and_tips,
                location_descriptions=advisory_out.location_descriptions,
                visa_info=advisory_out.visa_info,
                weather_info=weather_out.weather_summary if weather_out else "N/A",
                sim_and_apps=advisory_out.sim_and_apps,
                safety_tips=advisory_out.safety_tips,
            ),
            souvenirs=souvenir_out.souvenirs,
            logistics=LogisticsInfo(
                flight_options=logistics_out.flight_options,
                recommended_flight=logistics_out.recommended_flight,
                average_price=logistics_out.average_price,
                booking_tips=logistics_out.booking_tips,
                visa_requirements=logistics_out.visa_requirements,
            ),
            accommodation=AccommodationInfo(
                recommendations=accommodation_out.recommendations,
                best_areas=accommodation_out.best_areas,
                average_price_per_night=accommodation_out.average_price_per_night,
                booking_tips=accommodation_out.booking_tips,
                total_estimated_cost=accommodation_out.total_estimated_cost,
            ),
            generated_at=datetime.utcnow().isoformat(),
        )

        print(f"\n{'=' * 80}")
        print(f"✅ ORCHESTRATOR - Travel Plan Complete!")
        print(f"{'=' * 80}")
        print(f"📄 Version: {travel_plan.version}")
        print(f"📊 Budget Status: {budget_out.budget_status}")
        print(f"💵 Total Cost: {budget_out.total_estimated_cost:,.0f} VND")
        print(f"📅 Itinerary: {days_count} days planned")
        print(
            f"✈️  Flight: {itinerary_out.selected_flight.airline if itinerary_out.selected_flight else 'N/A'}"
        )
        print(
            f"🏨 Hotel: {itinerary_out.selected_accommodation.name if itinerary_out.selected_accommodation else 'N/A'}"
        )
        print(f"{'=' * 80}\n")

        return travel_plan
