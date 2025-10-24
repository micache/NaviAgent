"""
Advisory Agent
Provides travel advisories, warnings, and location descriptions
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

def create_advisory_agent(model: str = "gpt-4") -> Agent:
    """
    Creates an agent specialized in travel advisories
    """
    
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY not set in environment variables")
    
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=120.0)
    
    agent = Agent(
        name="AdvisoryAgent",
        model=OpenAIChat(
            id=model, 
            api_key=settings.openai_api_key,
            http_client=http_client
        ),
        tools=[search_tools],
        description="""You are a travel safety and information expert who provides 
        up-to-date advisories, travel tips, and engaging location descriptions.""",
        
        instructions=[
            "ALWAYS search for the LATEST information before providing advice",
            "Search for current travel warnings, visa requirements, and safety alerts",
            "Search for current weather conditions and forecasts",
            "Research each location to write engaging descriptions",
            "For EACH location in the location_list, write a 2-3 sentence description",
            "Descriptions should be informative yet engaging, highlighting key features",
            "Provide practical tips about SIM cards, apps, and connectivity",
            "Include cultural dos and don'ts",
            "Mention health precautions if relevant",
            "Generate a JSON structure with the following format:",
            """
            {
                "warnings_and_tips": [
                    "Visa: Tourist visa required for stays over 15 days. Apply online at...",
                    "Weather: October is autumn season with comfortable temperatures (15-22°C)",
                    "Safety: Tokyo is very safe, but watch for pickpockets in crowded areas",
                    "Currency: Credit cards widely accepted, but carry some cash for small shops",
                    "Language: English signage common in tourist areas, download Google Translate",
                    "Etiquette: Remove shoes when entering homes and some restaurants"
                ],
                "location_descriptions": [
                    {
                        "location_name": "Senso-ji Temple",
                        "description": "Tokyo's oldest and most significant Buddhist temple, founded in 645 AD. The iconic Thunder Gate (Kaminarimon) welcomes visitors to a vibrant complex featuring traditional architecture and the bustling Nakamise shopping street lined with traditional snacks and souvenirs.",
                        "highlights": ["Thunder Gate", "Five-story Pagoda", "Nakamise Shopping Street"]
                    },
                    {
                        "location_name": "Tokyo Tower",
                        "description": "Inspired by Paris's Eiffel Tower, this 333-meter tall communications tower has become an iconic symbol of Tokyo. The observation decks offer stunning 360-degree views of the sprawling metropolis, best visited at sunset to see the city transition from day to night.",
                        "highlights": ["Main Observatory", "Special Observatory", "Night illumination"]
                    }
                ],
                "visa_info": "Tourist visa waiver for stays up to 15 days. For longer stays, apply for tourist visa online.",
                "weather_info": "October: 15-22°C, low rainfall, comfortable for walking. November: 10-18°C, crisp autumn weather.",
                "sim_and_apps": [
                    "SIM: Rent pocket WiFi at airport or buy tourist SIM (Sakura Mobile, Mobal)",
                    "Apps: Google Maps, Hyperdia (train routes), PayPay (mobile payment), Google Translate"
                ],
                "safety_tips": [
                    "Emergency number: 110 (police), 119 (ambulance/fire)",
                    "Earthquakes possible - know building evacuation routes",
                    "Stay hydrated during summer months",
                    "Keep valuables secure in crowded trains"
                ]
            }
            """,
            "Ensure ALL locations from the location_list have descriptions",
            "Keep descriptions concise (2-3 sentences) but informative",
            "Use search tools to verify current information, especially for visa and safety",
        ]
    )
    
    return agent


async def run_advisory_agent(
    agent: Agent,
    destination: str,
    travel_date: str,
    location_list: list
) -> dict:
    """
    Run the advisory agent and extract structured output
    """
    
    locations_str = ", ".join(location_list)
    
    prompt = f"""
    Provide comprehensive travel advisory information for {destination}.
    Travel Date: {travel_date}
    
    REQUIRED: Write descriptions for these specific locations:
    {locations_str}
    
    IMPORTANT:
    1. Search for CURRENT travel advisories and visa requirements for {destination}
    2. Search for CURRENT weather conditions and forecast
    3. Research EACH location in the list above and write a 2-3 sentence description
    4. Include practical tips about SIM cards, recommended apps, and connectivity
    5. Return the output as a valid JSON object matching the structure in your instructions
    6. Ensure the location_descriptions array has an entry for EVERY location listed above
    """
    
    response = await agent.arun(prompt)
    
    try:
        content = response.content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Ensure we have location descriptions for all locations
            described_locations = {loc["location_name"] for loc in result.get("location_descriptions", [])}
            missing_locations = set(location_list) - described_locations
            
            if missing_locations:
                for loc_name in missing_locations:
                    result.setdefault("location_descriptions", []).append({
                        "location_name": loc_name,
                        "description": f"A notable destination in {destination}.",
                        "highlights": []
                    })
            
            return result
        else:
            return {
                "warnings_and_tips": [content],
                "location_descriptions": [
                    {"location_name": loc, "description": "No description available", "highlights": []}
                    for loc in location_list
                ],
                "visa_info": None,
                "weather_info": None,
                "sim_and_apps": [],
                "safety_tips": [],
                "raw_response": content
            }
    except Exception as e:
        return {
            "warnings_and_tips": [f"Error: {str(e)}"],
            "location_descriptions": [
                {"location_name": loc, "description": "Description unavailable", "highlights": []}
                for loc in location_list
            ],
            "visa_info": None,
            "weather_info": None,
            "sim_and_apps": [],
            "safety_tips": [],
            "raw_response": response.content
        }
