"""
Travel Planner API - FastAPI Application
Multi-agent travel planning system using Agno-AGI
"""

import json
from datetime import date, datetime
from pathlib import Path

import uvicorn
from agents.orchestrator_agent import OrchestratorAgent
from config import settings, model_settings, ModelProvider
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import API schemas
from schemas import TravelPlan, TravelRequest

# Global orchestrator instance
orchestrator = None

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Multi-agent Travel Planning System powered by Agno-AGI

    ## Features
    - Detailed day-by-day itinerary planning
    - Comprehensive budget breakdown
    - Travel advisories and location descriptions
    - Souvenir recommendations
    - Logistics planning (flights & accommodation)

    ## Architecture
    - 7 specialist agents working as an intelligent team
    - Team Leader with automatic task delegation
    - Parallel execution with dependency management
    - Real-time internet search capabilities
    """,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allow_methods,
    allow_headers=settings.allow_headers,
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    global orchestrator

    print(f"\n{'=' * 80}")
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"{'=' * 80}")

    # ============================================================================
    # 🔥 MODEL CONFIGURATION - Change provider here if needed
    # ============================================================================
    # Default: Uses OpenAI (configured in model_settings)
    # To switch provider, uncomment one of these:
    
    # model_settings.default_provider = ModelProvider.GOOGLE  # Switch to Gemini
    model_settings.default_provider = ModelProvider.DEEPSEEK  # Switch to DeepSeek
    # model_settings.default_provider = ModelProvider.ANTHROPIC  # Switch to Claude
    
    # ============================================================================
    
    # Validate API keys
    keys = model_settings.validate_api_keys()
    configured_providers = [k for k, v in keys.items() if v]
    
    if not configured_providers:
        print("\n⚠️  WARNING: No AI provider API keys found!")
        print("   Please add at least one API key to your .env file")
        print("   Example: OPENAI_API_KEY=sk-proj-xxx\n")
        raise ValueError("No AI provider API keys configured")
    
    print(f"✓ Configured providers: {', '.join(configured_providers)}")
    
    # Print model configuration
    print(f"\n🤖 Model Configuration:")
    print(f"   Provider: {model_settings.default_provider.value}")
    print(f"   Model: {model_settings.model_mappings[model_settings.default_provider]}")
    print(f"   Temperature: {model_settings.default_temperature}")
    
    # Initialize orchestrator with centralized model config
    orchestrator = OrchestratorAgent()
    print(f"\n✓ Orchestrator initialized with 7 specialist agents")

    print(f"\n{'=' * 80}")
    print(f"API ready at: http://{settings.host}:{settings.port}{settings.api_prefix}")
    print(f"Documentation: http://{settings.host}:{settings.port}{settings.api_prefix}/docs")
    print(f"{'=' * 80}\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\nShutting down Travel Planner API...")


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs_url": f"{settings.api_prefix}/docs",
    }


@app.get(f"{settings.api_prefix}/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "openai_configured": bool(settings.openai_api_key),
    }


@app.post(
    f"{settings.api_prefix}/plan_trip",
    response_model=TravelPlan,
    summary="Create Travel Plan",
    description="""
    Generate a comprehensive travel plan using structured agent orchestration.

    **Sequential Workflow with Structured I/O:**
    1. Phase 1: Weather Specialist provides forecast and seasonal events
    2. Phase 2: Flight & Accommodation Specialists find options
    3. Phase 3: Itinerary Planner selects best options and creates schedule
    4. Phase 4: Budget, Souvenir & Advisory Specialists analyze
    5. Phase 5: Build comprehensive TravelPlan with all structured data

    **Processing Time:** Typically 2-5 minutes depending on complexity
    """,
    responses={
        200: {
            "description": "Travel plan generated successfully with structured data",
            "model": TravelPlan,
        },
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"},
        503: {"description": "Service unavailable (OpenAI API key not configured)"},
    },
)
async def plan_trip(request: TravelRequest):
    """
    Main endpoint to generate travel plans using structured orchestration

    Args:
        request: TravelRequest with all planning parameters

    Returns:
        TravelPlan: Comprehensive structured travel plan v2.0
    """

    # Validate OpenAI API key
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.",
        )

    try:
        # Log request
        print(f"\n[API] New travel plan request received")
        print(f"  - Destination: {request.destination}")
        print(f"  - Departure Date: {request.departure_date}")
        print(f"  - Duration: {request.trip_duration} days")
        print(f"  - Budget: {request.budget:,.0f}")
        print(f"  - Travelers: {request.num_travelers}")
        print(f"  - Style: {request.travel_style}")

        # Execute structured orchestration
        travel_plan = await orchestrator.plan_trip(request)

        print(f"\n[API] Travel plan generated successfully!")
        print(f"  - Version: {travel_plan.version}")
        print(f"  - Generated at: {travel_plan.generated_at}")

        return travel_plan

    except Exception as e:
        print(f"\n[API] Error generating travel plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating travel plan: {str(e)}")


@app.get(f"{settings.api_prefix}/test-openai")
async def test_openai():
    """Test OpenAI API connection"""
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)

        # Test with a simple completion
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello, OpenAI connection is working!'",
                }
            ],
            max_tokens=50,
        )

        return {
            "status": "success",
            "message": "OpenAI connection is working",
            "model": settings.openai_model,
            "response": response.choices[0].message.content,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI connection failed: {str(e)}")


@app.get(f"{settings.api_prefix}/config")
async def get_config():
    """Get current API configuration (non-sensitive)"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "model": settings.openai_model,
        "api_prefix": settings.api_prefix,
        "orchestrator_status": "initialized" if orchestrator else "not initialized",
        "agents": "7 specialist agents (Weather, Logistics, Accommodation, Itinerary, Budget, Souvenir, Advisory)",
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


def run():
    """Run the application"""
    import sys

    if sys.platform == "win32":
        import multiprocessing

        multiprocessing.freeze_support()

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        reload_delay=0.5,
    )


async def main():
    """Main function for testing."""
    global travel_team
    
    # Initialize team
    travel_team = create_travel_planning_team(model=settings.openai_model)
    
    # Create structured travel request
    travel_request = TravelRequest(
        destination="Châu Âu, Pháp, Anh, Đức",
        departure_point="Hanoi",
        departure_date=date(2024, 6, 1),
        trip_duration=7,
        budget=50_000_000,
        num_travelers=4,
        travel_style="self_guided",
        customer_notes="Thích quẩy, thích bar, thích ăn chơi nhảy múa",
    )

    # Convert to team input
    team_input = TravelPlanningTeamInput(
        destination=travel_request.destination,
        departure_point=travel_request.departure_point,
        departure_date=travel_request.departure_date,
        trip_duration=travel_request.trip_duration,
        budget=travel_request.budget,
        num_travelers=travel_request.num_travelers,
        travel_style=travel_request.travel_style,
        customer_notes=travel_request.customer_notes,
    )

    # Run team
    team_response = await run_travel_planning_team(travel_team, team_input)
    
    # Create travel plan
    travel_plan = TravelPlan(
        version="2.0-team",
        destination=travel_request.destination,
        departure_point=travel_request.departure_point,
        departure_date=travel_request.departure_date,
        trip_duration=travel_request.trip_duration,
        budget=travel_request.budget,
        num_travelers=travel_request.num_travelers,
        travel_style=travel_request.travel_style,
        team_full_response=team_response,
        generated_at=datetime.utcnow(),
    )

    # Save structured output
    output_file = Path("travel_plan_output.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(travel_plan.model_dump(), f, ensure_ascii=False, indent=2, default=str)

    print(f"\n✅ Travel plan saved to: {output_file}")


if __name__ == "__main__":
    run()
    # main()
