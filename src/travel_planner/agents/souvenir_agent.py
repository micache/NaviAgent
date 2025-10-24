"""
Souvenir Agent
Suggests souvenirs and where to buy them
"""

import ssl
import sys
from pathlib import Path

import certifi
import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat

sys.path.insert(0, str(Path(__file__).parent.parent))

import json

from config import settings  # Thêm dòng này
from tools.search_tool import search_tools


def create_souvenir_agent(model: str = "gpt-4") -> Agent:
    """
    Creates an agent specialized in souvenir recommendations
    """

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY not set in environment variables")

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.AsyncClient(verify=ssl_context, timeout=120.0)

    agent = Agent(
        name="SouvenirAgent",
        model=OpenAIChat(id=model, api_key=settings.openai_api_key, http_client=http_client),
        tools=[search_tools],
        description="""You are a souvenir and gift specialist with extensive knowledge
        of authentic local products, traditional crafts, and popular gift items from
        destinations around the world.""",
        instructions=[
            "Search for popular and authentic souvenirs from the destination",
            "Recommend a mix of traditional items, food products, and practical gifts",
            "Include price ranges based on current market prices",
            "Suggest specific shops, markets, or districts where items can be purchased",
            "Consider portability and customs regulations",
            "Include both budget-friendly and premium options",
            "Highlight items unique to the destination",
            "Generate a JSON array with the following format:",
            """
            [
                {
                    "item_name": "Matcha Tea Set",
                    "description": "Authentic Japanese matcha powder with traditional bamboo whisk and ceramic bowl. Perfect for tea enthusiasts.",
                    "estimated_price": "1,000,000 - 3,000,000 VND",
                    "where_to_buy": "Nakamise Shopping Street (Asakusa), Takashimaya Department Store"
                },
                {
                    "item_name": "Furoshiki (Wrapping Cloth)",
                    "description": "Traditional Japanese wrapping cloth with beautiful patterns. Eco-friendly and versatile for gift wrapping or decoration.",
                    "estimated_price": "200,000 - 800,000 VND",
                    "where_to_buy": "Oriental Bazaar (Harajuku), Tokyu Hands"
                },
                {
                    "item_name": "KitKat Special Flavors",
                    "description": "Japan-exclusive KitKat flavors like matcha, sake, and regional specialties. Easy to pack and popular gifts.",
                    "estimated_price": "50,000 - 200,000 VND per box",
                    "where_to_buy": "Airport duty-free, Don Quijote, any convenience store"
                },
                {
                    "item_name": "Kokeshi Dolls",
                    "description": "Traditional wooden dolls handcrafted with unique designs. Authentic Japanese folk art and collectibles.",
                    "estimated_price": "500,000 - 2,000,000 VND",
                    "where_to_buy": "Asakusa Nakamise, Kyoto specialty shops"
                },
                {
                    "item_name": "Japanese Snack Box",
                    "description": "Assorted traditional snacks including mochi, rice crackers, and regional specialties. Great for sharing.",
                    "estimated_price": "300,000 - 800,000 VND",
                    "where_to_buy": "Supermarkets, Don Quijote, station gift shops"
                }
            ]
            """,
            "Recommend at least 5-8 different souvenirs",
            "Include a range of price points",
            "Be specific about shopping locations",
        ],
    )

    return agent


async def run_souvenir_agent(agent: Agent, destination: str) -> list:
    """
    Run the souvenir agent and extract structured output
    """

    prompt = f"""
    Suggest authentic souvenirs and local products from {destination}.

    IMPORTANT:
    1. Search for POPULAR and AUTHENTIC local souvenirs
    2. Include items at various price points
    3. Provide specific shops or markets where to buy
    4. Return the output as a valid JSON array matching the structure in your instructions
    """

    response = await agent.arun(prompt)

    try:
        content = response.content
        start_idx = content.find("[")
        end_idx = content.rfind("]") + 1

        if start_idx != -1 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            return result
        else:
            return [
                {
                    "item_name": "Error",
                    "description": content,
                    "estimated_price": "N/A",
                    "where_to_buy": "N/A",
                }
            ]
    except Exception as e:
        return [
            {
                "item_name": "Error",
                "description": str(e),
                "estimated_price": "N/A",
                "where_to_buy": "N/A",
            }
        ]
