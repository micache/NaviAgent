"""
Itinerary Agent
Generates detailed day-by-day travel itineraries
"""

import ssl
import sys
from pathlib import Path

import certifi
import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import json

from config import settings  # Thêm dòng này
from tools.search_tool import search_tools


def create_itinerary_agent(model: str = "gpt-4") -> Agent:
    """
    Creates an agent specialized in travel itinerary planning

    Args:
        model: OpenAI model to use (default: gpt-4)

    Returns:
        Configured Agent instance
    """

    # Kiểm tra API key
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY not set in environment variables")

    # Tăng timeout lên 120 giây (2 phút)
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=120.0)

    agent = Agent(
        name="ItineraryAgent",
        model=OpenAIChat(id=model, api_key=settings.openai_api_key, http_client=http_client),
        tools=[search_tools],
        description="""You are a world-class travel itinerary planner with extensive knowledge
        of tourist destinations, local attractions, and optimal travel routes.""",
        instructions=[
            "ALWAYS search for current information about the destination before creating the itinerary",
            "Create a HIGHLY DETAILED timeline with SPECIFIC times for each activity",
            "Include FULL NAMES and ADDRESSES of locations whenever possible",
            "Consider realistic travel times between locations",
            "Account for opening hours, rush hours, and meal times",
            "Include a mix of must-see attractions, hidden gems, and rest periods",
            "Suggest optimal routes to minimize travel time",
            "Add operational notes (booking requirements, tips, etc.)",
            "Generate a JSON structure with the following format:",
            """
            {
                "daily_schedules": [
                    {
                        "day_number": 1,
                        "date": "Optional",
                        "title": "Day 1: Exploring Historic Tokyo",
                        "activities": [
                            {
                                "time": "08:00 - 10:00",
                                "location_name": "Senso-ji Temple",
                                "address": "2-3-1 Asakusa, Taito City, Tokyo",
                                "activity_type": "sightseeing",
                                "description": "Visit Tokyo's oldest Buddhist temple, explore Nakamise shopping street",
                                "estimated_cost": 0,
                                "notes": "Arrive early to avoid crowds. Free admission."
                            }
                        ]
                    }
                ],
                "location_list": ["Senso-ji Temple", "Tokyo Tower", "Shibuya Crossing"],
                "summary": "A comprehensive 7-day itinerary covering Tokyo's highlights"
            }
            """,
            "The location_list must contain ONLY the main attraction names (no addresses)",
            "Be specific with timing - use exact hours (e.g., '09:00 - 11:30')",
            "Include buffer time for meals and rest",
        ],
    )

    return agent


async def run_itinerary_agent(
    agent: Agent,
    destination: str,
    duration: int,
    travel_style: str,
    customer_notes: str,
) -> dict:
    """
    Run the itinerary agent and extract structured output
    """

    # Đơn giản hóa prompt nếu cần
    prompt = f"""
    Create a {duration}-day itinerary for {destination}.
    Travel Style: {travel_style}
    Notes: {customer_notes}

    Important:
    1. Create day-by-day schedule
    2. Include specific activities with time slots
    3. Return as valid JSON
    4. Keep it concise and practical
    """

    response = await agent.arun(prompt)

    try:
        content = response.content
        start_idx = content.find("{")
        end_idx = content.rfind("}") + 1

        if start_idx != -1 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            return result
        else:
            return {
                "daily_schedules": [],
                "location_list": [],
                "summary": content,
                "raw_response": content,
            }
    except Exception as e:
        return {
            "daily_schedules": [],
            "location_list": [],
            "summary": f"Error: {str(e)}",
            "raw_response": response.content,
        }
