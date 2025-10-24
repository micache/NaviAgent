"""
Travel Planner API - FastAPI Application
Multi-agent travel planning system using Agno-AGI
"""

from datetime import datetime

import uvicorn
from agents import OrchestratorAgent  # Import từ agents/__init__.py
from config import settings
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from schemas import TravelPlan, TravelRequest

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
    - 5 specialist agents coordinated by an orchestrator
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


# Global orchestrator instance
orchestrator = None


@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup"""
    global orchestrator

    print(f"\n{'=' * 80}")
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"{'=' * 80}")

    # Check for OpenAI API key
    if not settings.openai_api_key:
        print("\n⚠️  WARNING: OPENAI_API_KEY not found in environment variables!")
        print("   Please set OPENAI_API_KEY to use the API.\n")
    else:
        print(f"✓ OpenAI API Key configured")

    # Initialize orchestrator
    print(f"✓ Initializing Orchestrator with model: {settings.openai_model}")
    orchestrator = OrchestratorAgent(model=settings.openai_model)

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
        "orchestrator_ready": orchestrator is not None,
        "openai_configured": bool(settings.openai_api_key),
    }


@app.post(
    f"{settings.api_prefix}/plan_trip",
    response_model=TravelPlan,
    summary="Create Travel Plan",
    description="""
    Generate a comprehensive travel plan using multi-agent orchestration.

    **Workflow:**
    1. Phase 1: Itinerary, Logistics, and Souvenir agents run in parallel
    2. Phase 2: Budget and Advisory agents run in parallel (depend on itinerary)
    3. Phase 3: Results compiled into comprehensive travel plan

    **Processing Time:** Typically 2-5 minutes depending on complexity
    """,
    responses={
        200: {
            "description": "Travel plan generated successfully",
            "model": TravelPlan,
        },
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"},
        503: {"description": "Service unavailable (OpenAI API key not configured)"},
    },
)
async def plan_trip(request: TravelRequest):
    """
    Main endpoint to generate travel plans

    Args:
        request: TravelRequest with all planning parameters

    Returns:
        TravelPlan: Comprehensive travel plan v1.0
    """
    global orchestrator

    # Validate OpenAI API key
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.",
        )

    # Validate orchestrator
    if not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Orchestrator not initialized. Please restart the server.",
        )

    try:
        # Log request
        print(f"\n[API] New travel plan request received")
        print(f"  - Destination: {request.destination}")
        print(f"  - Duration: {request.trip_duration} days")
        print(f"  - Budget: {request.budget:,.0f}")
        print(f"  - Travelers: {request.num_travelers}")
        print(f"  - Style: {request.travel_style}")

        # Execute orchestration workflow
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

    # Thêm flag để tránh multiprocessing issues trên Windows
    if sys.platform == "win32":
        import multiprocessing

        multiprocessing.freeze_support()

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        reload_delay=0.5,  # Thêm delay để tránh reload quá nhanh
    )


if __name__ == "__main__":
    run()
