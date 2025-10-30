import os
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from reception.suggest_destination.suggest_from_text import get_destination_suggestion

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
# print(f"Loading from: {env_path}")
load_dotenv(dotenv_path=env_path, override=True)
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")

class ReceptionistAgent(Agent):
    
    def __init__(self):
        super().__init__(
            model=OpenAIChat(id=model, api_key=api_key),
            instructions="""
            You are a friendly and helpful receptionist agent of NaviAgent - an AI travel assistant to help customers create travel itineraries and notes about their trips.
            Your task is to:
            1. Greet customers and ask where they are from (departure location)
            2. Then ask about their intended travel destination
            3. If the customer did not provide a destination:
               a. First, ask about their travel preferences (what kind of experience they want: beach, culture, adventure, food, etc.)
               b. After getting preferences, the system will suggest destinations
               c. Present the suggestions and ask the customer to choose ONE specific destination
               d. Do NOT proceed to the next question until they have selected a specific city/place
            4. Once got the SPECIFIC destination, ask customer about other information needed for the trip planning in this order:
               - Length of stay
               - Number of guests
               - Budget
               - Interests (may already be collected from step 3a)
               - Personal requirements (MUST ASK, but customer can say "no" or "none")
            5. Personal requirements: You MUST ask this question. If customer says they don't have any special requirements, accept "none" or empty as valid answer
            6. When ALL required information is collected (departure, SPECIFIC destination, length_of_stay, number_of_guests, budget, interests, and personal_requirements answered), STOP asking questions
            7. Instead, provide a summary of all collected information and ask the customer to confirm if everything is correct
            8. If customer says information needs correction, update based on their feedback
            
            CRITICAL: 
            - Always ask about preferences BEFORE suggesting destinations
            - The destination MUST be a specific city or place, not a vague description
            
            Always be conversational and natural. Ask one question at a time.
            When extracting information, be flexible with user responses.
            When all information is complete, DO NOT ask for additional details. Just confirm what you have.
            You MUST ask about personal requirements - do not skip this question.
            """,
            markdown=False
        )
        self.conversation_history = []
        self.collected_info = {
            "departure": None,
            "destination": None,
            "length_of_stay": None,
            "number_of_guests": None,
            "budget": None,
            "interests": [],
            "personal_requirements": None
        }
        self.information_confirmed = False
        self.asked_preferences = False
        self.suggested_destinations = None
        
    def greet(self) -> str:
        prompt = "Greet the customer warmly and ask where they are from (their departure location)."
        response = self.run(input=prompt, stream=False)
        message = response.content.strip()
        self.conversation_history.append({"role": "assistant", "content": message})
        return message
    
    def chat(self, user_message: str) -> str:
        """Process user message and return agent response."""
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Extract information first
        self._extract_information(user_message)
        
        # Check if we need to ask for preferences before suggesting destinations
        if self.collected_info.get("destination") is None and not self.asked_preferences:
            uncertain_keywords = ['not decided', 'don\'t know', 'not sure', 'undecided', 'haven\'t decided', 'did not know', 'didn\'t decide']
            user_lower = user_message.lower()
            
            if any(keyword in user_lower for keyword in uncertain_keywords):
                # User doesn't have a destination, need to ask preferences first
                self.asked_preferences = True
                
        # Check if user provided preferences and we should now get suggestions
        if self.asked_preferences and self.suggested_destinations is None and len(self.collected_info.get("interests", [])) > 0:
            # Get destination suggestions based on preferences
            preferences_text = ", ".join(self.collected_info.get("interests", []))
            self.suggested_destinations = self.get_suggested_destination(preferences_text)
        
        # Check if user is confirming the information
        confirmation_keywords = ['correct', 'yes', 'right', 'ok', 'confirm', 'accurate', 'good', 'perfect', 'fine']
        user_lower = user_message.lower().strip()
        
        if self.is_information_complete() and not self.information_confirmed:
            if any(keyword in user_lower for keyword in confirmation_keywords):
                self.information_confirmed = True
                final_destination = self.collected_info.get("destination", "your destination")
                return f"Thank you for confirming! Your travel information has been saved. Our team will now start preparing your personalized itinerary for {final_destination}. Have a great day!"
        
        # Build context with conversation history
        context = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Agent'}: {msg['content']}"
            for msg in self.conversation_history[-10:]
        ])
        
        # Check if all information is complete
        info_complete = self.is_information_complete()
        
        if info_complete and not self.information_confirmed:
            # All info collected, ask for confirmation ONCE
            prompt = f"""
            All required information has been collected!
            
            Collected information:
            {json.dumps(self.collected_info, ensure_ascii=False, indent=2)}
            
            Provide a friendly summary of ALL the trip details and ask the customer to confirm if everything is correct.
            Keep it concise and clear. Ask for confirmation ONCE, then wait for their response.
            Format the summary clearly with all details.
            """
        else:
            # Continue collecting information
            suggestions_context = f"\nSuggested destinations: {self.suggested_destinations}" if self.suggested_destinations else ""
            
            prompt = f"""
            Conversation so far:
            {context}
            
            Based on the conversation, continue to collect travel information naturally.
            Current collected info: {json.dumps(self.collected_info, ensure_ascii=False)}
            Asked preferences: {self.asked_preferences}{suggestions_context}
            
            CRITICAL RULES: 
            - Do NOT ask for information that is already filled (not null in current info).
            - If destination is null and asked_preferences is False, ask about travel preferences first
            - If destination is null and we have suggested destinations, present them and ask user to choose ONE specific city
            - If destination is null and suggestions were given but user hasn't chosen, keep asking them to choose
            - Only ask for the NEXT missing field in order: departure → destination → length_of_stay → number_of_guests → budget → interests → personal_requirements
            - Ask ONE question at a time.
            - If the field already has a value, skip to the next missing field.
            - Destination must be a SPECIFIC city/place, not a vague description.
            
            Your response:
            """
        
        response = self.run(input=prompt, stream=False)
        message = response.content.strip()
        
        # Remove any "Assistant:" or "Agent:" prefix if present
        if message.startswith("Assistant:"):
            message = message.replace("Assistant:", "", 1).strip()
        if message.startswith("Agent:"):
            message = message.replace("Agent:", "", 1).strip()
        
        self.conversation_history.append({"role": "assistant", "content": message})
        
        return message
    
    def _extract_information(self, user_message: str):
        """Extract structured information from user message."""
        # Get the last agent question for context
        last_agent_message = ""
        for msg in reversed(self.conversation_history):
            if msg['role'] == 'assistant':
                last_agent_message = msg['content']
                break
        
        extraction_prompt = f"""
        Last agent question: "{last_agent_message}"
        User's response: "{user_message}"
        Current info: {json.dumps(self.collected_info, ensure_ascii=False)}
        
        CRITICAL RULES:
        1. Extract information based on what the agent asked and what the user responded
        2. Only extract NEW information that is mentioned in the user's response
        3. For fields NOT mentioned in the user response, you MUST set them to null
        4. Do NOT copy values from "Current info" - only extract from the user message
        5. Use the agent's question as context to understand what field the user is answering
        
        Special cases:
        - If agent asked about departure/where from → extract as "departure"
        - If agent asked about destination/where to → extract as "destination"
        - If user says "no", "none", "nothing", "no requirements" for personal requirements → set personal_requirements to []
        - If user mentions specific requirements → add them to personal_requirements list
        
        Return ONLY a JSON object. Fields not mentioned by user should be null.
        Format: {{"departure": null, "destination": null, "length_of_stay": null, "number_of_guests": null, "budget": null, "interests": null, "personal_requirements": null}}
        """
        
        response = self.run(input=extraction_prompt, stream=False)
        try:
            # Extract JSON from response
            content = response.content.strip()
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
                
                # Debug: print what was extracted
                # print(f"[DEBUG] User said: '{user_message}'")
                # print(f"[DEBUG] Extracted: {json.dumps(extracted, ensure_ascii=False)}")
                # print(f"[DEBUG] Before update: {json.dumps(self.collected_info, ensure_ascii=False)}")
                
                # Update collected info with new data ONLY
                for key, value in extracted.items():
                    # Skip null values completely - don't touch existing data
                    if value is None or value == "null":
                        continue
                    
                    current_value = self.collected_info.get(key)
                    
                    if key == "personal_requirements":
                        # Only update if not already set
                        if isinstance(value, list) and current_value is None:
                            self.collected_info[key] = value
                    elif isinstance(value, list):
                        # For list fields like interests
                        if isinstance(current_value, list) and len(value) > 0:
                            # Merge unique values
                            self.collected_info[key].extend([v for v in value if v not in self.collected_info[key]])
                        elif current_value is None and len(value) > 0:
                            # Set new list if field is empty
                            self.collected_info[key] = value
                    elif current_value is None:
                        # Only update scalar fields if they're still None
                        self.collected_info[key] = value
                
                # print(f"[DEBUG] After update: {json.dumps(self.collected_info, ensure_ascii=False)}\n")
                        
        except (json.JSONDecodeError, AttributeError) as e:
            # print(f"[DEBUG] Extraction error: {e}")
            pass
    
    def get_suggested_destination(self, preferences: str) -> str:
        return get_destination_suggestion(preferences)
    
    def is_information_complete(self) -> bool:
        """Check if all required information has been collected."""
        required_fields = ["departure", "destination", "length_of_stay", "number_of_guests", "budget", "interests", "personal_requirements"]
        
        # All fields must be filled (personal_requirements can be empty list [], but must not be None)
        return all(self.collected_info.get(field) is not None for field in required_fields)
    
    def get_metadata_summary(self) -> Dict[str, Any]:
        """Return collected metadata as a dictionary."""
        return self.collected_info.copy()
    
    def get_metadata_json(self) -> str:
        """Return collected metadata as a JSON string."""
        return json.dumps(self.collected_info, ensure_ascii=False, indent=2)
    
    def summarize_trip(self) -> str:
        """Generate a natural language summary of the trip."""
        prompt = f"""
        Based on the collected information: {json.dumps(self.collected_info, ensure_ascii=False)}
        
        Provide a friendly summary of the trip plan and ask if the customer would like to proceed.
        """
        response = self.run(input=prompt, stream=False)
        return response.content.strip()
    
    def confirm_information(self):
        """Mark that information has been confirmed by user."""
        self.information_confirmed = True


def main():
    """Demo conversation with the receptionist agent."""
    
    def print_separator():
        print("\n" + "="*80 + "\n")
    
    print("NaviAgent Reception Demo")
    
    # Interactive mode
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'summary' to see collected metadata")
    print_separator()
    
    agent = ReceptionistAgent()
    
    greeting = agent.greet()
    print(f"Agent: {greeting}\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("\nThank you for using NaviAgent!")
            print("\nFinal Metadata:")
            print(agent.get_metadata_json())
            break
        
        if user_input.lower() == 'summary':
            print("\nCurrent Metadata:")
            print(agent.get_metadata_json())
            print()
            continue
        
        if not user_input:
            continue
        
        response = agent.chat(user_input)
        print(f"\nAgent: {response}\n")
        
        # If information is confirmed, end the conversation
        if agent.information_confirmed:
            print("\n[Conversation ended - Information confirmed]")
            print("\nFinal Metadata:")
            print(agent.get_metadata_json())
            break
        
        if agent.is_information_complete() and not agent.information_confirmed:
            print("[All required information collected! Waiting for confirmation...]\n")

if __name__ == "__main__":
    main()