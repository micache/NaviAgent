"""
Logistics Agent
Provides flight information and accommodation suggestions
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


def create_logistics_agent(model: str = "gpt-4") -> Agent:
    """
    Creates an agent specialized in travel logistics
    """
    
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY not set in environment variables")
    
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=120.0)
    
    agent = Agent(
        name="LogisticsAgent",
        model=OpenAIChat(
            id=model, 
            api_key=settings.openai_api_key,
            http_client=http_client
        ),
        tools=[search_tools],
        description="""You are a travel logistics expert specializing in flights, 
        accommodation, and transportation planning.""",
        
        instructions=[
            "Search for current flight prices and options between the origin and destination",
            "Research accommodation options and recommend specific areas/neighborhoods",
            "Consider budget constraints when making recommendations",
            "Provide practical transportation tips for getting around",
            "Include information about airport transfers",
            "Suggest booking strategies and timing",
            "Generate a JSON structure with the following format:",
            """
            {
                "flight_info": "Direct flights available from Hanoi to Tokyo (Haneda/Narita). Major carriers: Vietnam Airlines, ANA, JAL. Flight time: ~5-6 hours. Best to book 2-3 months in advance for better rates.",
                "estimated_flight_cost": 15000000,
                "accommodation_suggestions": [
                    "Shibuya/Shinjuku: Central location, great for first-time visitors, extensive train connections. Budget: 1,500,000-3,000,000 VND/night",
                    "Asakusa: Traditional atmosphere, near Senso-ji Temple, more affordable. Budget: 1,000,000-2,000,000 VND/night",
                    "Ueno: Excellent value, good transportation links, near museums and parks. Budget: 800,000-1,800,000 VND/night",
                    "Ginza: Upscale area, luxury shopping, higher prices. Budget: 2,500,000-5,000,000 VND/night"
                ],
                "transportation_tips": [
                    "Purchase JR Pass before arrival for unlimited JR train travel (7-day pass ~3,000,000 VND)",
                    "Get IC card (Suica/Pasmo) for convenient metro and bus payments",
                    "Airport to city: Narita Express (1 hour, ~400,000 VND) or Airport Limousine Bus (90 min, ~350,000 VND)",
                    "Download apps: Google Maps, Hyperdia (train routes), Tokyo Metro app",
                    "Taxis are expensive - use trains/metro for most travel"
                ]
            }
            """,
            "Base estimates on current market prices",
            "Consider seasonal variations in flight and hotel prices",
            "Recommend neighborhoods based on budget and travel style",
        ]
    )
    
    return agent


async def run_logistics_agent(
    agent: Agent,
    departure_point: str,
    destination: str,
    budget: float,
    duration: int
) -> dict:
    """
    Run the logistics agent and extract structured output
    
    Args:
        agent: The LogisticsAgent instance
        departure_point: Origin city/airport
        destination: Destination city/country
        budget: Total trip budget
        duration: Trip duration in days
        
    Returns:
        Dictionary with logistics information
    """
    
    prompt = f"""
    Provide comprehensive logistics information for travel from {departure_point} to {destination}.
    
    Duration: {duration} days
    Total Budget: {budget:,.0f}
    
    IMPORTANT:
    1. Search for CURRENT flight prices from {departure_point} to {destination}
    2. Research accommodation options and prices in {destination}
    3. Recommend specific neighborhoods/areas to stay based on the budget
    4. Provide practical transportation tips
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
                "flight_info": content,
                "estimated_flight_cost": None,
                "accommodation_suggestions": [],
                "transportation_tips": [],
                "raw_response": content
            }
    except Exception as e:
        return {
            "flight_info": f"Error: {str(e)}",
            "estimated_flight_cost": None,
            "accommodation_suggestions": [],
            "transportation_tips": [],
            "raw_response": response.content
        }
