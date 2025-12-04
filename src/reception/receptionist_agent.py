import os
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from reception.suggest_destination.suggest_from_text import get_destination_suggestion
from reception.suggest_destination.suggest_from_images import (
    GoogleVisionImagesAgent,
    DuckDuckGoImagesAgent
)

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
# print(f"Loading from: {env_path}")
load_dotenv(dotenv_path=env_path, override=True)
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")


class ConversationState(Enum):
    """Enum to track the current state of the conversation."""
    
    GREETING = "greeting"
    ASK_DESTINATION = "ask_destination"
    SUGGEST_DESTINATION = "suggest_destination"
    CONFIRM_DESTINATION = "confirm_destination"
    COLLECT_DEPARTURE = "collect_departure"
    COLLECT_TRAVEL_DATE = "collect_travel_date"
    COLLECT_LENGTH_OF_STAY = "collect_length_of_stay"
    COLLECT_NUM_GUESTS = "collect_num_guests"
    COLLECT_BUDGET = "collect_budget"
    COLLECT_TRAVEL_STYLE = "collect_travel_style"
    COLLECT_NOTES = "collect_notes"
    CONFIRM_DETAILS = "confirm_details"
    UPDATE_DETAILS = "update_details"
    COMPLETED = "completed"


class ReceptionistAgent(Agent):
    """A receptionist agent that handles customer travel inquiries.
    
    This agent guides customers through the travel planning process by:
    1. Greeting customers
    2. Asking about destination (with suggestion options)
    3. Collecting travel metadata (departure, date, length, guests, budget, style, notes)
    4. Confirming details and allowing updates
    
    Attributes:
        travel_data: Dictionary storing collected travel information.
        state: Current conversation state.
        image_agent: Agent for image-based destination suggestions.
    """
    
    def __init__(self):
        """Initialize the receptionist agent with model and state."""
        super().__init__(
            model=OpenAIChat(id=model, api_key=api_key),
            markdown=False
        )
        self.travel_data: Dict[str, Any] = {
            'destination': None,
            'departure_point': None,
            'travel_date': None,
            'length_of_stay': None,
            'num_guests': None,
            'budget': None,
            'travel_style': None,
            'special_notes': None
        }
        self.state = ConversationState.GREETING
        self.image_agent = DuckDuckGoImagesAgent()
    
    def greet_customer(self) -> str:
        """Greet the customer and introduce the service.
        
        Returns:
            A welcoming greeting message.
        """
        greeting = (
            "Hello! Welcome to NaviAgent Travel Service. "
            "I'm here to help you plan your perfect trip. "
            "Let's start by finding your ideal destination. "
            "Do you already have a destination in mind?"
        )
        self.state = ConversationState.ASK_DESTINATION
        return greeting
    
    def handle_destination_inquiry(self, response: str) -> str:
        """Handle customer's response about destination.
        
        Args:
            response: Customer's response about having a destination.
        
        Returns:
            Appropriate follow-up message based on response.
        """
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['yes', 'yeah', 'sure', 'have', 'know']):
            # Customer has a destination
            self.state = ConversationState.COLLECT_DEPARTURE
            return "Great! What is your intended destination?"
        else:
            # Customer needs suggestions
            self.state = ConversationState.SUGGEST_DESTINATION
            return (
                "No problem! I can help you find the perfect destination. "
                "You can either:\n"
                "1. Describe your ideal trip (e.g., 'a quiet beach with good food')\n"
                "2. Send me an image of a place that inspires you\n"
                "Which would you prefer?"
            )
    
    def suggest_destination_from_text(self, description: str) -> str:
        """Suggest destination based on text description.
        
        Args:
            description: Customer's description of ideal destination.
        
        Returns:
            Suggested destination with reasoning.
        """
        try:
            suggestion_json = get_destination_suggestion(description)
            suggestion = json.loads(suggestion_json)
            
            self.travel_data['destination'] = suggestion.get('destination')
            
            response = (
                f"Based on your description, I recommend {suggestion.get('destination')}. "
                f"{suggestion.get('reason')}\n\n"
                f"Does this sound good to you?"
            )
            self.state = ConversationState.CONFIRM_DESTINATION
            return response
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Could you try again?"
    
    def suggest_destination_from_image(self, image_url: str) -> str:
        """Suggest destination based on image.
        
        Args:
            image_url: URL of the image customer provided.
        
        Returns:
            Location identification and description.
        """
        try:
            result = self.image_agent.search_image_location(image_url)
            
            # Handle the result which could be a dict, JSON string, or formatted text
            location = None
            description = None
            
            if isinstance(result, str):
                # Try to parse as JSON first
                try:
                    parsed = json.loads(result)
                    if isinstance(parsed, dict):
                        location = parsed.get('location', 'Unknown location')
                        description = parsed.get('description', '')
                except json.JSONDecodeError:
                    # If not JSON, check if it's the formatted text from DuckDuckGo agent
                    if "location" in result.lower() and "description" in result.lower():
                        # Extract location and description from formatted text
                        lines = result.split('\n')
                        for i, line in enumerate(lines):
                            if '"location":' in line:
                                location = line.split('"location":')[1].strip().strip('",')
                            elif '"description":' in line:
                                # Get all remaining lines as description
                                desc_start = line.split('"description":')[1].strip().strip('"')
                                # Find the closing of description
                                remaining = '\n'.join(lines[i:])
                                if '"}' in remaining:
                                    description = remaining.split('"}')[0].strip().strip('"')
                                else:
                                    description = desc_start
                    else:
                        location = str(result)
                        description = ""
            elif isinstance(result, dict):
                location = result.get('location', 'Unknown location')
                description = result.get('description', '')
            
            # Fallback if parsing failed
            if not location:
                location = "this location"
                description = "I identified a travel destination from your image."
            
            self.travel_data['destination'] = location
            
            response = (
                f"This appears to be {location}! "
                f"{description}\n\n"
                f"Would you like to visit this destination?"
            )
            
            self.state = ConversationState.CONFIRM_DESTINATION
            return response
        except Exception as e:
            return f"I apologize, but I couldn't identify the location: {str(e)}. Could you try another image?"
    
    def collect_departure_point(self, departure: str) -> str:
        """Collect departure point information.
        
        Args:
            departure: Customer's departure location.
        
        Returns:
            Confirmation and next question.
        """
        self.travel_data['departure_point'] = departure
        self.state = ConversationState.COLLECT_TRAVEL_DATE
        return f"Got it! Departing from {departure}. When are you planning to travel?"
    
    def collect_travel_date(self, date: str) -> str:
        """Collect travel date information.
        
        Args:
            date: Customer's intended travel date.
        
        Returns:
            Confirmation and next question.
        """
        self.travel_data['travel_date'] = date
        self.state = ConversationState.COLLECT_LENGTH_OF_STAY
        return f"Perfect! Planning to travel on {date}. How long do you plan to stay?"
    
    def collect_length_of_stay(self, length: str) -> str:
        """Collect length of stay information.
        
        Args:
            length: Duration of stay (e.g., '5 days', '1 week').
        
        Returns:
            Confirmation and next question.
        """
        self.travel_data['length_of_stay'] = length
        self.state = ConversationState.COLLECT_NUM_GUESTS
        return f"Noted! A {length} trip. How many people will be traveling?"
    
    def collect_num_guests(self, num_guests: str) -> str:
        """Collect number of guests.
        
        Args:
            num_guests: Number of travelers.
        
        Returns:
            Confirmation and next question.
        """
        self.travel_data['num_guests'] = num_guests
        self.state = ConversationState.COLLECT_BUDGET
        return f"Great! {num_guests} travelers. What's your approximate budget?"
    
    def collect_budget(self, budget: str) -> str:
        """Collect budget information.
        
        Args:
            budget: Customer's budget.
        
        Returns:
            Confirmation and next question.
        """
        self.travel_data['budget'] = budget
        self.state = ConversationState.COLLECT_TRAVEL_STYLE
        return (
            f"Thank you! Budget of {budget} noted. "
            "What's your preferred travel style? (independent/self-guided or package tour)"
        )
    
    def collect_travel_style(self, style: str) -> str:
        """Collect travel style preference.
        
        Args:
            style: Travel style (independent or tour).
        
        Returns:
            Confirmation and next question.
        """
        self.travel_data['travel_style'] = style
        self.state = ConversationState.COLLECT_NOTES
        return (
            f"Understood! {style} travel style. "
            "Do you have any special requests or notes? (e.g., dietary restrictions, "
            "accessibility needs, specific activities)"
        )
    
    def collect_special_notes(self, notes: str) -> str:
        """Collect special notes and requirements.
        
        Args:
            notes: Customer's special requests.
        
        Returns:
            Confirmation and summary.
        """
        self.travel_data['special_notes'] = notes if notes.lower() not in ['no', 'none', 'nothing'] else 'None'
        self.state = ConversationState.CONFIRM_DETAILS
        return self.generate_summary()
    
    def generate_summary(self) -> str:
        """Generate a summary of collected travel information.
        
        Returns:
            Formatted summary with confirmation question.
        """
        summary = "\n=== Travel Plan Summary ===\n"
        summary += f"Destination: {self.travel_data['destination']}\n"
        summary += f"Departure Point: {self.travel_data['departure_point']}\n"
        summary += f"Travel Date: {self.travel_data['travel_date']}\n"
        summary += f"Length of Stay: {self.travel_data['length_of_stay']}\n"
        summary += f"Number of Guests: {self.travel_data['num_guests']}\n"
        summary += f"Budget: {self.travel_data['budget']}\n"
        summary += f"Travel Style: {self.travel_data['travel_style']}\n"
        
        if self.travel_data['special_notes']:
            summary += f"Special Notes: {self.travel_data['special_notes']}\n"
        
        summary += "\nIs this information correct? Would you like to make any changes?"
        return summary
    
    def handle_confirmation(self, response: str) -> str:
        """Handle customer's confirmation of travel details.
        
        Args:
            response: Customer's response to confirmation.
        
        Returns:
            Appropriate response based on confirmation.
        """
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['yes', 'correct', 'looks good', 'perfect', 'right']):
            self.state = ConversationState.COMPLETED
            return (
                "Excellent! Your travel details have been recorded. "
                "Thank you for using NaviAgent Travel Service. "
                "Have a wonderful trip!"
            )
        else:
            self.state = ConversationState.UPDATE_DETAILS
            return (
                "No problem! What would you like to update? "
                "Please specify the field (e.g., 'destination', 'budget', 'travel date') "
                "and the new value."
            )
    
    def update_travel_detail(self, field: str, value: str) -> str:
        """Update a specific travel detail.
        
        Args:
            field: The field to update.
            value: The new value.
        
        Returns:
            Confirmation of update.
        """
        field_lower = field.lower().replace(' ', '_')
        
        if field_lower in self.travel_data:
            self.travel_data[field_lower] = value
            self.state = ConversationState.CONFIRM_DETAILS
            return f"Updated {field} to {value}.\n\n{self.generate_summary()}"
        else:
            return (
                f"I couldn't find the field '{field}'. "
                f"Available fields: {', '.join(self.travel_data.keys())}"
            )
    
    def process_message(self, message: str, image_url: Optional[str] = None) -> str:
        """Process customer message based on current conversation state.
        
        Args:
            message: Customer's message.
            image_url: Optional image URL for destination suggestions.
        
        Returns:
            Agent's response based on current state.
        """
        if self.state == ConversationState.GREETING:
            return self.greet_customer()
        
        elif self.state == ConversationState.ASK_DESTINATION:
            return self.handle_destination_inquiry(message)
        
        elif self.state == ConversationState.SUGGEST_DESTINATION:
            if image_url:
                return self.suggest_destination_from_image(image_url)
            else:
                return self.suggest_destination_from_text(message)
        
        elif self.state == ConversationState.CONFIRM_DESTINATION:
            # Customer is confirming the suggested destination
            message_lower = message.lower()
            if any(word in message_lower for word in ['yes', 'yeah', 'sure', 'okay', 'ok', 'good', 'perfect', 'great', 'sounds good']):
                # Customer accepts the destination
                self.state = ConversationState.COLLECT_DEPARTURE
                return "Great! Where will you be departing from?"
            else:
                # Customer rejects, ask for another description or manual input
                self.state = ConversationState.SUGGEST_DESTINATION
                return "I understand. Could you provide a different description of your ideal destination, or tell me directly where you'd like to go?"
        
        elif self.state == ConversationState.COLLECT_DEPARTURE:
            # Now we're actually collecting departure point
            if not self.travel_data['destination']:
                # If no destination yet, treat this message as the destination
                self.travel_data['destination'] = message
                return "Great! Where will you be departing from?"
            return self.collect_departure_point(message)
        
        elif self.state == ConversationState.COLLECT_TRAVEL_DATE:
            return self.collect_travel_date(message)
        
        elif self.state == ConversationState.COLLECT_LENGTH_OF_STAY:
            return self.collect_length_of_stay(message)
        
        elif self.state == ConversationState.COLLECT_NUM_GUESTS:
            return self.collect_num_guests(message)
        
        elif self.state == ConversationState.COLLECT_BUDGET:
            return self.collect_budget(message)
        
        elif self.state == ConversationState.COLLECT_TRAVEL_STYLE:
            return self.collect_travel_style(message)
        
        elif self.state == ConversationState.COLLECT_NOTES:
            return self.collect_special_notes(message)
        
        elif self.state == ConversationState.CONFIRM_DETAILS:
            return self.handle_confirmation(message)
        
        elif self.state == ConversationState.UPDATE_DETAILS:
            # Parse update request (expecting format like "budget 5000" or "update budget to 5000")
            parts = message.split()
            if len(parts) >= 2:
                field = parts[0]
                value = ' '.join(parts[1:]).replace('to ', '')
                return self.update_travel_detail(field, value)
            else:
                return "Please specify both the field and new value (e.g., 'budget 5000')"
        
        elif self.state == ConversationState.COMPLETED:
            return "Your travel plan is complete. Is there anything else I can help you with?"
        
        return "I'm not sure how to help with that. Could you please clarify?"
    
    def get_travel_data(self) -> Dict[str, Any]:
        """Get the collected travel data.
        
        Returns:
            Dictionary containing all travel information.
        """
        return self.travel_data.copy()
    
    def reset(self) -> None:
        """Reset the agent to initial state."""
        self.travel_data = {
            'destination': None,
            'departure_point': None,
            'travel_date': None,
            'length_of_stay': None,
            'num_guests': None,
            'budget': None,
            'travel_style': None,
            'special_notes': None
        }
        self.state = ConversationState.GREETING


def main():
    """Main function to run the receptionist agent interactively."""
    agent = ReceptionistAgent()
    print("=" * 50)
    print("NaviAgent Receptionist")
    print("=" * 50)
    print("\nType 'quit' or 'exit' to end the conversation")
    print("Type 'reset' to start over")
    print("=" * 50)
    
    # Start with greeting
    print(f"\nAgent: {agent.greet_customer()}")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit']:
            print("\nAgent: Thank you for using NaviAgent. Goodbye!")
            break
        
        if user_input.lower() == 'reset':
            agent.reset()
            print(f"\nAgent: {agent.greet_customer()}")
            continue
        
        # Check if user is providing an image URL (simple check)
        image_url = None
        if user_input.startswith('http'):
            image_url = user_input
            user_input = "image provided"
        
        response = agent.process_message(user_input, image_url)
        print(f"\nAgent: {response}")
        
        if agent.state == ConversationState.COMPLETED:
            print("\n" + "=" * 50)
            print("Final Travel Data:")
            print(json.dumps(agent.get_travel_data(), indent=2))
            print("=" * 50)
            break

if __name__ == "__main__":
    main()
    