"""Receptionist Agent - Simplified version without FSM."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from agno.agent import Agent
from agno.tools.sql import SQLTools
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

from reception.suggest_destination.suggest_from_text import get_top_k_destination_suggestion

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")
supabase_uri = os.getenv("DATABASE_URL")

class SuggestionAgent(Agent):
    """Agent to suggest travel destinations based on user input."""

    def __init__(self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        super().__init__(model=OpenAIChat(id=model, api_key=api_key), markdown=False)
        self.user_id = user_id
        self.session_id = session_id
        self.tools = [SQLTools(db_url=supabase_uri)]

        self.instructions = f"""
        You are a travel suggestion agent. You will be received:
        1. A user description of desired travel features.
        2. Top 5 best match suggestion made by my destination retrieval system (if any).
        3. Previous destination visited by the user (if any).
        Based on the above information, suggest ONLY THREE suitable travel destinations in Vietnam or East Asia.
        You may not suggest destinations outside this region.
        You may not choose destinations that does not match the user's description, if there are less than three destinations qualified, only pick those qualified.
        It is okay to suggest less than three destinations.
        RETRIEVED DESTINATIONS MAY NOT ALL CORRECT. Do not pick destinations that does not have attributes described by the user. (e.g. if user wants to see sakura blossom, only pick destinations that have sakura blossom like Japan, South Korea, China, Taiwan; if the traveler wants to see snow, only pick destinations that really have snow).
        You may not suggest previously visited destinations unless the user description strongly indicates so. If you suggest a previously visited destination, write in the reason that you knew the user has been there before but you highly recommend it again.
        Always provide answer in Vietnamese.
        """

def get_suggestion_from_text(
    description: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """Get travel destination suggestion based on user description."""
    agent = SuggestionAgent(user_id=user_id, session_id=session_id)
    result = get_top_k_destination_suggestion(description, k=10)
    print("Retrieved Results:", result)
    
    prompt = f"""
    You are a travel expert. Your task is to suggest THREE destinations that ACTUALLY MATCH the user's request.

    User Description: "{description}"
    Retrieved Results: {result}
    Query the 'address' column in 'trips' table in the database to find out previously visited destinations by the user with user_id = '{user_id}'.
    If you suggest a previously visited destination, write in the reason that you knew the user has been there before but you highly recommend it again.
    For example: "Tôi biết bạn đã đến Seoul, nhưng Seoul là một điểm đến lý tưởng để ngắm tuyết rơi vào mùa đông"
    
    ⚠️ CRITICAL VERIFICATION RULES - MUST FOLLOW:
    1. ONLY suggest destinations that ACTUALLY have the exact features the user requested
    2. DO NOT suggest destinations just because they are in the retrieved results
    3. If user wants SNOW (tuyết), ONLY suggest places that genuinely have snow in winter:
       ✅ YES - Has snow: Hokkaido/Tokyo/Nagano (Japan), Seoul/Busan (South Korea), Beijing/Harbin (China), parts of Taiwan
       ❌ NO - Does NOT have snow: ALL of Vietnam (including Sapa, Dalat, Hanoi), most of Southeast Asia, southern China cities
    4. If user wants cherry blossoms (hoa anh đào), ONLY suggest: Japan, South Korea, Taiwan, some parts of China
       ❌ Vietnam does NOT have cherry blossoms (Dalat has hydrangeas and mimosa, NOT cherry blossoms)
    5. If user wants beaches (biển), ONLY suggest coastal destinations
    6. If the retrieved results don't match user requirements, IGNORE them and use your knowledge to find correct destinations in Vietnam or East Asia
    7. It's better to suggest FEWER destinations that truly match than to suggest wrong ones
    8. If no destinations truly match in Vietnam/East Asia, be honest and say so

    STEP-BY-STEP PROCESS:
    1. Identify the KEY requirement from user description (e.g., snow, cherry blossoms, beach, etc.)
    2. Check each retrieved destination: Does it ACTUALLY have this feature? If NO, skip it.
    3. Use your knowledge to add correct destinations that match
    4. Pick only the top 3 that genuinely match

    Format your response with markdown EXACTLY like this (in Vietnamese):
    Tôi gợi ý một vài điểm đến phù hợp với yêu cầu của bạn ✨

    🌍 **Destination Name, Country**
    Brief ACCURATE description emphasizing the SPECIFIC feature user requested (e.g., "Nơi này có tuyết rơi từ tháng 12 đến tháng 3...")
    (blank line)
    🌍 **Destination Name, Country**
    Brief ACCURATE description emphasizing the SPECIFIC feature user requested
    If this destination was previously visited, add a sentence in the description explaining why you recommend it again. Ví dụ: "Tôi biết bạn đã đến Seoul, nhưng Seoul là một điểm đến lý tưởng để ngắm tuyết rơi vào mùa đông"
    (blank line)
    🌍 **Destination Name, Country**
    Brief ACCURATE description emphasizing the SPECIFIC feature user requested
    If this destination was previously visited, add a sentence in the description explaining why you recommend it again. Ví dụ: "Tôi biết bạn đã đến Seoul, nhưng Seoul là một điểm đến lý tưởng để ngắm tuyết rơi vào mùa đông"
    
    Chúc bạn sớm tìm được điểm đến cho chuyến đi tiếp theo! 🎒

    Use emoji 🌍, bold destination, new line between name and description, add a line break between destinations.
    Answer in Vietnamese.
    Return ONLY the markdown text without any JSON formatting.
    """
    response = agent.run(input=prompt, stream=False)
    return response.content.strip()

# def main():
#     agent = SuggestionAgent(user_id='cf6929e0-3c9c-40e5-a63d-2b1375775887')
#     # agent.print_response("Query the 'address' column in 'trips' table in the database to find out previously visited destinations by the user with user_id = 'cf6929e0-3c9c-40e5-a63d-2b1375775887'", markdown=True)
#     description = "Muốn đi ngắm tuyết rơi"
#     result = get_suggestion_from_text(description, user_id='cf6929e0-3c9c-40e5-a63d-2b1375775887')
#     print("Suggested Destinations:\n", result)
    

# if __name__ == "__main__":
#     main()
