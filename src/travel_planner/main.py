"""
Travel Planner API - FastAPI Application
Multi-agent travel planning system using Agno-AGI
"""

import json
import uuid
from datetime import date, datetime
from pathlib import Path

import uvicorn
from travel_planner.agents.orchestrator_agent import OrchestratorAgent
from config import ModelProvider, model_settings, settings
from fastapi import FastAPI, HTTPException, Body
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
    # 🔥 MODEL CONFIGURATION
    # ============================================================================
    # Model provider is configured in config/model_config.py
    # Current: model_settings = create_deepseek_config()
    #
    # To change provider, edit config/model_config.py line 339:
    #   - create_default_config() → OpenAI
    #   - create_deepseek_config() → DeepSeek (current)
    #   - create_gemini_config() → Google Gemini
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
    print(
        f"   Memory Model: {model_settings.memory_model_mappings[model_settings.default_provider]}"
    )
    print(f"   Temperature: {model_settings.default_temperature}")

    # Initialize orchestrator with centralized model config and database support
    # Note: user_id and session_id will be extracted from request in plan_trip endpoint
    orchestrator = OrchestratorAgent(user_id=None, session_id=None, enable_memory=True)
    print(f"\n✓ Orchestrator initialized with 7 specialist agents + Database")

    print(f"\n{'=' * 80}")
    print(f"API ready at: http://{settings.host}:{settings.port}{settings.api_prefix}")
    print(
        f"Documentation: http://{settings.host}:{settings.port}{settings.api_prefix}/docs"
    )
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

    **Database Integration:**
    - All agent conversations are automatically saved to PostgreSQL
    - Session history tracked for context awareness
    - User preferences stored in memory for personalization
    - Send user_id in request body to enable user-specific memory

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
        request: TravelRequest with all planning parameters (including optional user_id and session_id)

    Returns:
        TravelPlan: Comprehensive structured travel plan v3.0 with database integration
    """

    # Validate OpenAI API key
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.",
        )

    try:
        # Extract user_id from request
        user_id = request.user_id

        # Auto-generate session_id for this request
        # Session ID stores chat history between agents internally
        # Pattern: {user_id or 'guest'}_{timestamp}_{unique_id}
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        user_prefix = user_id if user_id else "guest"
        session_id = f"{user_prefix}_{timestamp}_{unique_id}"

        # Log request
        print(f"\n[API] New travel plan request received")
        print(f"  - Destination: {request.destination}")
        print(f"  - Departure Date: {request.departure_date}")
        print(f"  - Duration: {request.trip_duration} days")
        print(f"  - Budget: {request.budget:,.0f}")
        print(f"  - Travelers: {request.num_travelers}")
        print(f"  - Style: {request.travel_style}")
        if user_id:
            print(f"  - User ID: {user_id}")
        print(f"  - Session ID (auto-generated): {session_id}")

        # Update orchestrator with user_id if provided
        if user_id and user_id != orchestrator.user_id:
            print(f"[API] Updating orchestrator with user_id: {user_id}")
            orchestrator.user_id = user_id
            # Update all agents with new user_id
            for agent in [
                orchestrator.weather_agent,
                orchestrator.logistics_agent,
                orchestrator.accommodation_agent,
                orchestrator.itinerary_agent,
                orchestrator.budget_agent,
                orchestrator.souvenir_agent,
                orchestrator.advisory_agent,
            ]:
                agent.user_id = user_id

        # Execute structured orchestration with session_id
        travel_plan = await orchestrator.plan_trip(request, session_id=session_id)

        print(f"\n[API] Travel plan generated successfully!")
        print(f"  - Version: {travel_plan.version}")
        print(f"  - Generated at: {travel_plan.generated_at}")
        if user_id:
            print(f"  - Session saved to database for user: {user_id}")

        # 🔍 DEBUG: Print full JSON response structure
        try:
            response_dict = travel_plan.model_dump() if hasattr(travel_plan, 'model_dump') else travel_plan.dict()
            print(f"\n{'='*80}")
            print(f"📋 FULL JSON RESPONSE STRUCTURE:")
            print(f"{'='*80}")
            print(json.dumps(response_dict, indent=2, default=str, ensure_ascii=False))
            print(f"{'='*80}\n")
        except Exception as debug_error:
            print(f"⚠️  Debug serialization error: {debug_error}")

        return travel_plan

    except Exception as e:
        print(f"\n[API] Error generating travel plan: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error generating travel plan: {str(e)}"
        )


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
        raise HTTPException(
            status_code=500, detail=f"OpenAI connection failed: {str(e)}"
        )


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


# ============================================================================
# GUIDEBOOK GENERATION ENDPOINTS
# ============================================================================

# Storage for generated guidebooks (in production, use a proper storage solution)
_guidebook_storage: dict = {}


@app.post(
    f"{settings.api_prefix}/generate_guidebook",
    summary="Generate Travel Guidebook",
    description="""
    Generate a professional travel guidebook from a travel plan.

    Supports multiple output formats:
    - **PDF**: Professional PDF with table of contents, page numbers, and print-ready layout
    - **HTML**: Responsive web page with interactive elements and print support
    - **Markdown**: Clean, readable markdown with GitHub-flavored markdown support

    **Processing Time:** Typically 2-10 seconds depending on content size
    """,
    responses={
        200: {"description": "Guidebook generated successfully"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error during generation"},
    },
)
async def generate_guidebook(
    travel_plan: TravelPlan = Body(..., description="Travel plan data"),
    formats: list = Body(default=["html"], description="Output formats"),
    language: str = Body(default="vi", description="Language"),
):
    """
    Generate travel guidebook from a TravelPlan.

    Args:
        travel_plan: TravelPlan object with travel data
        formats: List of formats to generate (pdf, html, markdown). Default: html
        language: Language for content (vi or en). Default: vi

    Returns:
        GuidebookResponse with generated file paths
    """
    from schemas import GuidebookResponse

    from travel_planner.guidebook import GuidebookGenerator

    # Debug logging
    print(f"\n[API] 📚 Generate guidebook endpoint called")
    print(f"  - travel_plan type: {type(travel_plan)}")
    print(f"  - travel_plan version: {travel_plan.version if travel_plan else 'None'}")
    print(f"  - formats: {formats}")
    print(f"  - language: {language}")

    try:
        print(f"\n[API] Generating guidebook...")
        print(f"  - Formats: {formats}")
        print(f"  - Language: {language}")

        # Create generator
        generator = GuidebookGenerator(
            travel_plan_data=travel_plan.model_dump(),
            output_dir="guidebooks",
            language=language,
        )

        # Generate guidebooks
        files = generator.generate_all_formats(formats=formats)

        # Get response data
        response_data = generator.get_guidebook_response()

        # Store for later retrieval
        _guidebook_storage[response_data["guidebook_id"]] = response_data

        print(f"[API] Guidebook generated successfully!")
        print(f"  - ID: {response_data['guidebook_id']}")
        print(f"  - Files: {files}")

        return GuidebookResponse(**response_data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[API] Error generating guidebook: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error generating guidebook: {str(e)}"
        )


@app.get(
    f"{settings.api_prefix}/guidebook/{{guidebook_id}}",
    summary="Get Guidebook Info",
    description="Get information about a generated guidebook.",
)
async def get_guidebook_info(guidebook_id: str):
    """
    Get information about a previously generated guidebook.

    Args:
        guidebook_id: Unique identifier for the guidebook

    Returns:
        Guidebook information including file paths
    """
    if guidebook_id not in _guidebook_storage:
        raise HTTPException(status_code=404, detail="Guidebook not found")

    return _guidebook_storage[guidebook_id]


@app.get(
    f"{settings.api_prefix}/guidebook/{{guidebook_id}}/download",
    summary="Download Guidebook File",
    description="Download a specific guidebook file.",
)
async def download_guidebook(guidebook_id: str, format: str = "pdf"):
    """
    Download a guidebook file.

    Args:
        guidebook_id: Unique identifier for the guidebook
        format: File format to download (pdf, html, markdown)

    Returns:
        File response for download
    """
    from fastapi.responses import FileResponse

    if guidebook_id not in _guidebook_storage:
        raise HTTPException(status_code=404, detail="Guidebook not found")

    guidebook = _guidebook_storage[guidebook_id]
    files = guidebook.get("files", {})

    # Normalize format
    format_lower = format.lower()
    if format_lower == "md":
        format_lower = "markdown"

    if format_lower not in files:
        raise HTTPException(
            status_code=404,
            detail=f"Format '{format}' not found. Available: {list(files.keys())}",
        )

    file_path = Path(files[format_lower])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    # Determine media type
    media_types = {
        "pdf": "application/pdf",
        "html": "text/html",
        "markdown": "text/markdown",
    }

    return FileResponse(
        path=str(file_path),
        media_type=media_types.get(format_lower, "application/octet-stream"),
        filename=file_path.name,
    )


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


if __name__ == "__main__":
    run()
    # main()
