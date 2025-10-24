"""
Budgeting Agent
Creates detailed budget breakdowns for travel plans
"""
from agno.agent import Agent
from agno.models.openai import OpenAIChat
import sys
from pathlib import Path
import certifi
import ssl
import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.search_tool import search_tools
from config import settings  # Thêm dòng này
import json


def create_budget_agent(model: str = "gpt-4") -> Agent:
    """
    Creates an agent specialized in budget planning
    """
    
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY not set in environment variables")
    
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=120.0)
    
    agent = Agent(
        name="BudgetAgent",
        model=OpenAIChat(
            id=model, 
            api_key=settings.openai_api_key,
            http_client=http_client
        ),
        tools=[search_tools],
        description="""You are an expert travel budget analyst with deep knowledge of 
        costs in various destinations, including accommodation, food, transportation, 
        activities, and miscellaneous expenses.""",
        
        instructions=[
            "ALWAYS search for current prices in the destination before creating the budget",
            "Research actual costs for flights, hotels, meals, attractions, and transportation",
            "Break down the budget into clear categories",
            "Provide detailed cost estimates based on real prices",
            "Consider the number of travelers and trip duration",
            "Account for seasonal price variations",
            "Include a buffer for unexpected expenses (typically 10-15%)",
            "Compare the estimated total against the provided budget",
            "Provide recommendations if over or under budget",
            "Generate a JSON structure with the following format:",
            """
            {
                "categories": [
                    {
                        "category_name": "Accommodation",
                        "estimated_cost": 15000000,
                        "breakdown": [
                            {"Hotel per night": 2000000},
                            {"Total nights": 6}
                        ],
                        "notes": "Mid-range hotel in Shibuya area"
                    },
                    {
                        "category_name": "Food & Dining",
                        "estimated_cost": 8000000,
                        "breakdown": [
                            {"Breakfast per day": 150000},
                            {"Lunch per day": 250000},
                            {"Dinner per day": 400000}
                        ],
                        "notes": "Mix of local restaurants and street food"
                    },
                    {
                        "category_name": "Transportation",
                        "estimated_cost": 5000000,
                        "breakdown": [
                            {"JR Pass 7-day": 3000000},
                            {"Local transport": 2000000}
                        ],
                        "notes": "Includes metro and occasional taxis"
                    },
                    {
                        "category_name": "Activities & Attractions",
                        "estimated_cost": 6000000,
                        "breakdown": [],
                        "notes": "Entry fees to temples, museums, entertainment"
                    },
                    {
                        "category_name": "Shopping & Souvenirs",
                        "estimated_cost": 4000000,
                        "breakdown": [],
                        "notes": "Gifts and personal shopping"
                    },
                    {
                        "category_name": "Miscellaneous",
                        "estimated_cost": 2000000,
                        "breakdown": [],
                        "notes": "Emergency buffer, tips, etc."
                    }
                ],
                "total_estimated_cost": 40000000,
                "budget_status": "Under budget by 10,000,000 VND",
                "recommendations": [
                    "You have room to upgrade accommodation or add activities",
                    "Consider allocating extra budget for shopping"
                ]
            }
            """,
            "Always provide costs in the same currency as the input budget",
            "Be realistic and base estimates on current market prices",
        ]
    )
    
    return agent


async def run_budget_agent(
    agent: Agent,
    destination: str,
    duration: int,
    budget: float,
    num_travelers: int,
    itinerary_data: dict
) -> dict:
    """
    Run the budget agent and extract structured output
    """
    
    activities_summary = "No itinerary data available"
    if itinerary_data and "daily_schedules" in itinerary_data:
        activities_summary = "\n".join([
            f"Day {day['day_number']}: {len(day.get('activities', []))} activities planned"
            for day in itinerary_data["daily_schedules"]
        ])
    
    prompt = f"""
    Create a detailed budget breakdown for {destination}.
    Duration: {duration} days
    Budget: {budget:,.0f}
    Number of Travelers: {num_travelers}
    
    Planned Activities Summary:
    {activities_summary}
    
    IMPORTANT:
    1. Search for CURRENT prices in {destination}
    2. Break down costs by category
    3. Compare against the provided budget
    4. Provide recommendations if over/under budget
    5. Return the output as a valid JSON object matching the structure in your instructions
    """
    
    response = await agent.arun(prompt)
    
    try:
        content = response.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            return result
        else:
            return {
                "categories": [],
                "total_estimated_cost": 0,
                "budget_status": content,
                "recommendations": [],
                "raw_response": content
            }
    except Exception as e:
        return {
            "categories": [],
            "total_estimated_cost": 0,
            "budget_status": f"Error: {str(e)}",
            "recommendations": [],
            "raw_response": response.content
        }
