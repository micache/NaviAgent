"""Receptionist Agent - Simplified version without FSM."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

from reception.suggest_destination.suggest_from_text import get_top_k_destination_suggestion

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")
supabase_uri = os.getenv("DATABASE_URL")

db = PostgresDb(db_url=supabase_uri)

class SuggestionAgent(Agent):
    """Agent to suggest travel destinations based on user input."""

    def __init__(self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        super().__init__(model=OpenAIChat(id=model, api_key=api_key), markdown=False)
        self.user_id = user_id
        self.session_id = session_id
        
        instructions = f"""
        You are a travel suggestion agent. You will be received:
        1. A user description of desired travel features.
        2. Top 5 best match suggestion made by my destination retrieval system (if any).
        3. Previous destination visited by the user (if any).
        Based on the above information, suggest ONLY THREE suitable travel destinations in Vietnam or East Asia.
        You may not suggest destinations outside this region.
        You may not choose destinations that does not match the user's description, if there are less than three destinations qualified, only pick those qualified.
        It is okay to suggest less than three destinations.
        RETRIEVED DESTINATIONS MAY NOT ALL CORRECT. Do not pick destinations that does not have attributes described by the user. (e.g. if user wants to see sakura blossom, only pick destinations that have sakura blossom like Japan, South Korea, China, Taiwan; if the traveler wants to see snow, only pick destinations that really have snow).
        You may not suggest previously visited destinations unless the user description strongly indicates so.
        """

def get_suggestion_from_text(
    description: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """Get travel destination suggestion based on user description."""
    agent = SuggestionAgent(user_id=user_id, session_id=session_id)
    result = get_top_k_destination_suggestion(description, k=5)
    
    prompt = f"""
    You are a travel expert. Pick three best destinations from the following retrieved results based on the user description.
    
    User Description: "{description}"
    Retrieved Results: {result}
    
    CRITICAL RULES - YOU MUST FOLLOW THESE:
    1. VERIFY that each destination ACTUALLY HAS the features mentioned in user description
    2. DO NOT suggest destinations based on vague similarity - be specific and accurate
    3. For example: If user asks for cherry blossoms (hoa anh đào), ONLY suggest places that actually have cherry blossoms:
       - Japan (Tokyo, Kyoto, Osaka) - YES, has cherry blossoms
       - South Korea (Seoul, Jeju) - YES, has cherry blossoms  
       - Taiwan - YES, has cherry blossoms
       - Da Lat, Vietnam - NO, does NOT have cherry blossoms (has hydrangeas, mimosa)
       - Hue, Vietnam - NO, does NOT have cherry blossoms
       - Hanoi, Vietnam - NO, does NOT have cherry blossoms
    4. If the retrieved results don't contain accurate matches, use your knowledge to suggest correct destinations in Vietnam and East/Southeast Asia
    5. Be honest about what each destination offers - don't invent features
    
    Format your response with markdown EXACTLY like this (in Vietnamese):
    Tôi gợi ý một vài điểm đến phù hợp với yêu cầu của bạn ✨
    
    🌍 **Destination Name, Country**
    Brief ACCURATE description with specific features that match the request.
    (blank line)
    🌍 **Destination Name, Country**
    Brief ACCURATE description with specific features that match the request.
    (blank line)
    🌍 **Destination Name, Country**
    Brief ACCURATE description with specific features that match the request.
    
    Chúc bạn sớm tìm được điểm đến cho chuyến đi tiếp theo! 🎒
    
    Use emoji 🌍, bold destination, new line between name and description, add a line break between destinations.
    Answer in Vietnamese.
    Return ONLY the markdown text without any JSON formatting.
    """
    response = agent.run(input=prompt, stream=False)
    return response.content.strip()
        
    