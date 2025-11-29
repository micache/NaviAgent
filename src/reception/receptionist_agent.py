import os
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from reception.suggest_destination.suggest_from_text import get_destination_suggestion
from reception.suggest_destination.suggest_from_images import (
    GoogleVisionImagesAgent,
    DuckDuckGoImagesAgent
)
from reception.conversation_state import ConversationState

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
# print(f"Loading from: {env_path}")
load_dotenv(dotenv_path=env_path, override=True)
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")

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
    
    def _generate_response(self, prompt: str) -> str:
        """Generate response using LLM.
        
        Args:
            prompt: The prompt for the LLM.
        
        Returns:
            Generated response text.
        """
        full_prompt = (
            "You are a friendly travel receptionist chatting with customers. "
            "Keep responses conversational and natural - NO formal greetings like 'Dear Customer', "
            "NO signatures like 'Best regards', and NO placeholder names like '[Your Name]'. "
            "Just respond directly as if you're chatting with a friend.\n\n"
            f"{prompt}"
        )
        response = self.run(input=full_prompt, stream=False)
        return response.content.strip()
    
    def _validate_date(self, date_str: str) -> tuple[bool, Optional[str]]:
        """Validate if the date is in the future.
        
        Args:
            date_str: Date string from customer.
        
        Returns:
            Tuple of (is_valid, error_message).
        """
        from datetime import datetime
        import dateutil.parser
        
        try:
            # Try to parse the date
            parsed_date = dateutil.parser.parse(date_str, fuzzy=True)
            today = datetime.now()
            
            if parsed_date.date() <= today.date():
                return False, "The travel date must be in the future. Please provide a date after today."
            
            return True, None
        except (ValueError, TypeError):
            return False, "I couldn't understand that date. Please provide a valid date (e.g., 'December 25th' or '25/12/2025')."
    
    def _validate_number(self, num_str: str) -> tuple[bool, Optional[str], Optional[int]]:
        """Validate if the input represents a valid number.
        
        Args:
            num_str: Number string from customer (can be digit or word).
        
        Returns:
            Tuple of (is_valid, error_message, parsed_number).
        """
        # Map word numbers to digits
        word_to_num = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
            'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
            'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
            'forty': 40, 'fifty': 50, 'một': 1, 'hai': 2, 'ba': 3,
            'bốn': 4, 'năm': 5, 'sáu': 6, 'bảy': 7, 'tám': 8,
            'chín': 9, 'mười': 10
        }
        
        num_str_lower = num_str.lower().strip()
        
        # Try direct integer conversion
        try:
            num = int(num_str_lower)
            if num <= 0:
                return False, "The number of guests must be at least 1. Please provide a valid number.", None
            if num > 100:
                return False, "That seems like a very large group! Please provide a reasonable number (1-100).", None
            return True, None, num
        except ValueError:
            pass
        
        # Try word conversion
        for word, num in word_to_num.items():
            if word in num_str_lower:
                if num <= 0:
                    return False, "The number of guests must be at least 1. Please provide a valid number.", None
                return True, None, num
        
        # Use LLM to extract number
        prompt = (
            f"Extract only the number from this text: '{num_str}'. "
            f"If there's a number (either as digit or word), return just the number. "
            f"If there's no number, return 'INVALID'."
        )
        response = self._generate_response(prompt).strip()
        
        try:
            num = int(response)
            if num <= 0:
                return False, "The number of guests must be at least 1. Please provide a valid number.", None
            if num > 100:
                return False, "That seems like a very large group! Please provide a reasonable number (1-100).", None
            return True, None, num
        except ValueError:
            return False, "I couldn't find a valid number in your response. Please provide the number of guests (e.g., '2', 'two', or '2 people').", None
    
    def _validate_budget(self, budget_str: str) -> tuple[bool, Optional[str]]:
        """Validate if the budget response contains a monetary value.
        
        Args:
            budget_str: Budget string from customer.
        
        Returns:
            Tuple of (is_valid, error_message).
        """
        budget_lower = budget_str.lower()
        
        # Check for currency indicators or numbers
        currency_indicators = ['$', '€', '£', '¥', 'usd', 'eur', 'vnd', 'dollar', 'euro', 'million', 'thousand', 'triệu', 'nghìn']
        has_currency = any(indicator in budget_lower for indicator in currency_indicators)
        has_number = any(char.isdigit() for char in budget_str)
        
        if has_number or has_currency:
            return True, None
        
        # Use LLM to check if it's a valid budget response
        prompt = (
            f"Is this a valid budget or monetary amount: '{budget_str}'? "
            f"Answer only 'YES' if it contains a monetary value or amount, or 'NO' if it doesn't."
        )
        response = self._generate_response(prompt).strip().upper()
        
        if 'YES' in response:
            return True, None
        else:
            return False, "Please provide your budget as a monetary amount (e.g., '1000 USD', '20 million VND', or '$500')."
    
    def greet_customer(self) -> str:
        """Greet the customer and introduce the service.
        
        Returns:
            A welcoming greeting message.
        """
        prompt = (
            "You are a friendly travel receptionist. Greet the customer warmly and introduce "
            "NaviAgent Travel Service. Let them know you'll help plan their perfect trip. "
            "Ask if they already have a destination in mind. Keep it conversational and friendly."
        )
        greeting = self._generate_response(prompt)
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
            prompt = (
                "The customer says they already have a destination in mind. "
                "Respond positively and ask them what their intended destination is. "
                "Keep it friendly and conversational."
            )
            return self._generate_response(prompt)
        else:
            # Customer needs suggestions
            self.state = ConversationState.SUGGEST_DESTINATION
            prompt = (
                "The customer doesn't have a destination yet and needs help. "
                "Tell them you can help find the perfect destination. Offer two options: "
                "1) They can describe their ideal trip (give an example like 'a quiet beach with good food'), "
                "or 2) They can send an image of a place that inspires them. "
                "Ask which they'd prefer. Be friendly and helpful."
            )
            return self._generate_response(prompt)
    
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
            
            # Extract city/country from landmark name
            city_extraction_prompt = (
                f"The location identified is: {location}\n"
                f"If this is a specific landmark or building, extract the CITY or COUNTRY name only. "
                f"For example: 'N Seoul Tower' -> 'Seoul', 'Eiffel Tower' -> 'Paris', 'Statue of Liberty' -> 'New York'\n"
                f"If it's already a city or country name, return it as is.\n"
                f"Return ONLY the city/country name, nothing else."
            )
            city_name = self._generate_response(city_extraction_prompt).strip()
            
            self.travel_data['destination'] = city_name
            
            response = (
                f"This appears to be {location}! "
                f"{description}\n\n"
                f"Would you like to visit {city_name}?"
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
        prompt = (
            f"The customer said they're departing from {departure}. "
            f"Acknowledge this and ask when they're planning to travel. "
            f"Be friendly and conversational."
        )
        return self._generate_response(prompt)
    
    def collect_travel_date(self, date: str) -> str:
        """Collect travel date information.
        
        Args:
            date: Customer's intended travel date.
        
        Returns:
            Confirmation and next question.
        """
        # Validate date
        is_valid, error_msg = self._validate_date(date)
        if not is_valid:
            prompt = (
                f"The customer provided '{date}' as their travel date, but {error_msg.lower()} "
                f"Politely explain the issue and ask them to provide a valid future date. "
                f"Be friendly and helpful."
            )
            return self._generate_response(prompt)
        
        self.travel_data['travel_date'] = date
        self.state = ConversationState.COLLECT_LENGTH_OF_STAY
        prompt = (
            f"The customer is planning to travel on {date}. "
            f"Acknowledge this positively and ask how long they plan to stay. "
            f"Be friendly and conversational."
        )
        return self._generate_response(prompt)
    
    def collect_length_of_stay(self, length: str) -> str:
        """Collect length of stay information.
        
        Args:
            length: Duration of stay (e.g., '5 days', '1 week').
        
        Returns:
            Confirmation and next question.
        """
        self.travel_data['length_of_stay'] = length
        self.state = ConversationState.COLLECT_NUM_GUESTS
        prompt = (
            f"The customer plans to stay for {length}. "
            f"Acknowledge this and ask how many people will be traveling in total (including the customer). "
            f"Important: Ask for TOTAL travelers, not 'with you' or 'accompanying you'. "
            f"For example: 'How many people in total?' or 'How many travelers?'. Be friendly and conversational."
        )
        return self._generate_response(prompt)
    
    def collect_num_guests(self, num_guests: str) -> str:
        """Collect number of guests.
        
        Args:
            num_guests: Number of travelers.
        
        Returns:
            Confirmation and next question.
        """
        # Validate number
        is_valid, error_msg, parsed_num = self._validate_number(num_guests)
        if not is_valid:
            prompt = (
                f"The customer provided '{num_guests}' for number of guests, but {error_msg.lower()} "
                f"Politely ask them to provide a valid number. Be friendly and helpful."
            )
            return self._generate_response(prompt)
        
        # Store the validated number
        self.travel_data['num_guests'] = str(parsed_num) if parsed_num else num_guests
        self.state = ConversationState.COLLECT_BUDGET
        
        # Handle solo vs group travel
        num = parsed_num or num_guests
        if num == 1 or str(num) == '1':
            travel_description = "you'll be traveling solo"
        else:
            travel_description = f"{num} people will be traveling"
        
        prompt = (
            f"The customer said {travel_description}. "
            f"Acknowledge this appropriately and ask about their approximate budget. "
            f"Be friendly and conversational."
        )
        return self._generate_response(prompt)
    
    def collect_budget(self, budget: str) -> str:
        """Collect budget information.
        
        Args:
            budget: Customer's budget.
        
        Returns:
            Confirmation and next question.
        """
        # Validate budget
        is_valid, error_msg = self._validate_budget(budget)
        if not is_valid:
            prompt = (
                f"The customer provided '{budget}' as their budget, but {error_msg.lower()} "
                f"Politely ask them to provide a budget amount. Be friendly and helpful."
            )
            return self._generate_response(prompt)
        
        # Check if budget is reasonable for the trip
        reasonability_prompt = (
            f"Analyze if this budget is reasonable for the trip:\n"
            f"- Destination: {self.travel_data['destination']}\n"
            f"- Number of Guests: {self.travel_data['num_guests']}\n"
            f"- Length of Stay: {self.travel_data['length_of_stay']}\n"
            f"- Budget: {budget}\n\n"
            f"Respond with JSON format: {{\"reasonable\": true/false, \"reason\": \"explanation\"}}\n"
            f"Consider typical costs for accommodation, food, transportation, and activities.\n"
            f"Be realistic but not overly strict. If the budget is very low (e.g., 5 million VND for 3 people, 4 days in Seoul), mark as unreasonable.\n"
            f"Respond with ONLY the JSON, nothing else."
        )
        
        try:
            reasonability_result = self._generate_response(reasonability_prompt).strip()
            # Remove markdown code blocks if present
            if reasonability_result.startswith('```'):
                reasonability_result = reasonability_result.split('\n', 1)[1].rsplit('\n', 1)[0].strip()
            
            reasonability = json.loads(reasonability_result)
            
            if not reasonability.get('reasonable', True):
                # Budget seems too low, warn customer
                prompt = (
                    f"The customer provided a budget of {budget} for {self.travel_data['num_guests']} people "
                    f"going to {self.travel_data['destination']} for {self.travel_data['length_of_stay']}. "
                    f"This seems quite low. Reason: {reasonability.get('reason', 'The budget may not be sufficient')}.\n\n"
                    f"Politely let them know the budget might be insufficient and explain why. "
                    f"Ask if they'd like to reconsider or if they have a specific plan in mind. "
                    f"Be helpful and not judgmental."
                )
                # Don't change state, stay in COLLECT_BUDGET to allow them to update
                return self._generate_response(prompt)
        except:
            # If parsing fails, continue without budget check
            pass
        
        self.travel_data['budget'] = budget
        self.state = ConversationState.COLLECT_TRAVEL_STYLE
        prompt = (
            f"The customer's budget is {budget}. "
            f"Acknowledge this and ask about their preferred travel style "
            f"(independent/self-guided or package tour). Be friendly and conversational."
        )
        return self._generate_response(prompt)
    
    def collect_travel_style(self, style: str) -> str:
        """Collect travel style preference.
        
        Args:
            style: Travel style (independent or tour).
        
        Returns:
            Confirmation and next question.
        """
        self.travel_data['travel_style'] = style
        self.state = ConversationState.COLLECT_NOTES
        prompt = (
            f"The customer prefers {style} travel style. "
            f"Acknowledge this and ask if they have any special requests or notes, "
            f"such as dietary restrictions, accessibility needs, or specific activities. "
            f"Be friendly and helpful."
        )
        return self._generate_response(prompt)
    
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
        travel_info = {
            'Destination': self.travel_data['destination'],
            'Departure Point': self.travel_data['departure_point'],
            'Travel Date': self.travel_data['travel_date'],
            'Length of Stay': self.travel_data['length_of_stay'],
            'Number of Guests': self.travel_data['num_guests'],
            'Budget': self.travel_data['budget'],
            'Travel Style': self.travel_data['travel_style']
        }
        
        if self.travel_data['special_notes'] and self.travel_data['special_notes'] != 'None':
            travel_info['Special Notes'] = self.travel_data['special_notes']
        
        info_text = '\n'.join([f"{k}: {v}" for k, v in travel_info.items()])
        
        prompt = (
            f"You are a travel receptionist. Present the following travel plan summary "
            f"to the customer in a friendly, organized way. After the summary, ask if "
            f"the information is correct and if they'd like to make any changes.\n\n"
            f"Travel Plan Details:\n{info_text}"
        )
        
        return self._generate_response(prompt)
    
    def handle_confirmation(self, response: str) -> str:
        """Handle customer's confirmation of travel details.
        
        Args:
            response: Customer's response to confirmation.
        
        Returns:
            Appropriate response based on confirmation.
        """
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['yes', 'correct', 'looks good', 'perfect', 'right', 'ok', 'okay', 'good']):
            self.state = ConversationState.COMPLETED
            prompt = (
                "The customer has confirmed their travel details are correct. "
                "Thank them, let them know their travel details have been recorded, "
                "and wish them a wonderful trip. Be warm and friendly."
            )
            return self._generate_response(prompt)
        else:
            # Try to parse direct update request using LLM
            parse_prompt = (
                f"The customer said: '{response}'\n\n"
                f"Analyze if they are requesting to update a specific field. "
                f"Available fields: destination, departure_point, travel_date, length_of_stay, num_guests, budget, travel_style, special_notes\n\n"
                f"If they are requesting an update, respond with JSON format: {{\"field\": \"field_name\", \"value\": \"new_value\"}}\n"
                f"If they are just saying they want to change something but didn't specify what, respond with: {{\"field\": null}}\n"
                f"Examples:\n"
                f"- 'change to 4 days of stay' -> {{\"field\": \"length_of_stay\", \"value\": \"4 days\"}}\n"
                f"- 'budget to 50 million' -> {{\"field\": \"budget\", \"value\": \"50 million\"}}\n"
                f"- 'I want to change something' -> {{\"field\": null}}\n"
                f"Respond with ONLY the JSON, nothing else."
            )
            
            try:
                parse_result = self._generate_response(parse_prompt).strip()
                # Remove markdown code blocks if present
                if parse_result.startswith('```'):
                    parse_result = parse_result.split('\n', 1)[1].rsplit('\n', 1)[0].strip()
                
                parsed = json.loads(parse_result)
                
                if parsed.get('field') and parsed.get('value'):
                    # Direct update
                    return self.update_travel_detail(parsed['field'], parsed['value'])
                else:
                    # Generic change request
                    self.state = ConversationState.UPDATE_DETAILS
                    prompt = (
                        "The customer wants to make changes to their travel details. "
                        "Respond positively and ask them what they'd like to update. "
                        "Tell them to specify the field (like 'destination', 'budget', 'travel date') "
                        "and the new value. Be helpful and friendly."
                    )
                    return self._generate_response(prompt)
            except:
                # Fallback to asking for clarification
                self.state = ConversationState.UPDATE_DETAILS
                prompt = (
                    "The customer wants to make changes to their travel details. "
                    "Respond positively and ask them what they'd like to update. "
                    "Tell them to specify the field (like 'destination', 'budget', 'travel date') "
                    "and the new value. Be helpful and friendly."
                )
                return self._generate_response(prompt)
    
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
            current_value = self.travel_data[field_lower]
            
            # Use LLM to compute the actual new value based on current value and update instruction
            compute_prompt = (
                f"Current value of {field}: {current_value}\n"
                f"Customer wants to update it with: '{value}'\n\n"
                f"Compute the new value. Examples:\n"
                f"- Current: '3', Update: 'add 1 more' -> New: '4'\n"
                f"- Current: '5 days', Update: 'change to 7 days' -> New: '7 days'\n"
                f"- Current: '30 million', Update: 'increase to 50 million' -> New: '50 million'\n"
                f"- Current: 'Seoul', Update: 'Tokyo' -> New: 'Tokyo'\n\n"
                f"Respond with ONLY the new value, nothing else. No explanations."
            )
            
            new_value = self._generate_response(compute_prompt).strip()
            
            # Validate the new value if it's a special field
            if field_lower == 'num_guests':
                is_valid, error_msg, parsed_num = self._validate_number(new_value)
                if not is_valid:
                    prompt = (
                        f"The customer tried to update guests to '{value}' but {error_msg.lower()} "
                        f"Politely explain the issue. Be friendly and helpful."
                    )
                    return self._generate_response(prompt)
                new_value = str(parsed_num)
            elif field_lower == 'travel_date':
                is_valid, error_msg = self._validate_date(new_value)
                if not is_valid:
                    prompt = (
                        f"The customer tried to update travel date to '{value}' but {error_msg.lower()} "
                        f"Politely explain the issue. Be friendly and helpful."
                    )
                    return self._generate_response(prompt)
            elif field_lower == 'budget':
                is_valid, error_msg = self._validate_budget(new_value)
                if not is_valid:
                    prompt = (
                        f"The customer tried to update budget to '{value}' but {error_msg.lower()} "
                        f"Politely explain the issue. Be friendly and helpful."
                    )
                    return self._generate_response(prompt)
            
            # Update the value
            self.travel_data[field_lower] = new_value
            self.state = ConversationState.CONFIRM_DETAILS
            
            prompt = (
                f"The customer updated their {field} from {current_value} to {new_value}. "
                f"Acknowledge the update positively, then present the updated travel summary "
                f"and ask if everything looks correct now.\n\n"
                f"Updated travel details:\n"
                f"Destination: {self.travel_data['destination']}\n"
                f"Departure Point: {self.travel_data['departure_point']}\n"
                f"Travel Date: {self.travel_data['travel_date']}\n"
                f"Length of Stay: {self.travel_data['length_of_stay']}\n"
                f"Number of Guests: {self.travel_data['num_guests']}\n"
                f"Budget: {self.travel_data['budget']}\n"
                f"Travel Style: {self.travel_data['travel_style']}\n"
                f"Special Notes: {self.travel_data.get('special_notes', 'None')}"
            )
            return self._generate_response(prompt)
        else:
            prompt = (
                f"The customer tried to update a field called '{field}' but that field doesn't exist. "
                f"Politely let them know you couldn't find that field and list the available fields: "
                f"{', '.join(self.travel_data.keys())}. Be helpful and friendly."
            )
            return self._generate_response(prompt)
    
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
            # Check if customer is confirming (done with edits)
            message_lower = message.lower()
            if any(word in message_lower for word in ['ok', 'okay', 'done', 'corrected', 'finished', 'complete', 'that\'s all', 'nothing', 'good']) and len(message.split()) <= 2:
                # Customer is done editing, mark as completed
                self.state = ConversationState.COMPLETED
                prompt = (
                    "The customer has confirmed their travel details are correct. "
                    "Thank them, let them know their travel details have been recorded, "
                    "and wish them a wonderful trip. Be warm and friendly."
                )
                return self._generate_response(prompt)
            
            # Try to parse update request using LLM
            parse_prompt = (
                f"The customer said: '{message}'\n\n"
                f"Parse their update request. Available fields: destination, departure_point, travel_date, length_of_stay, num_guests, budget, travel_style, special_notes\n\n"
                f"Respond with JSON format: {{\"field\": \"field_name\", \"value\": \"new_value\"}}\n"
                f"Examples:\n"
                f"- 'change to 4 days of stay' -> {{\"field\": \"length_of_stay\", \"value\": \"4 days\"}}\n"
                f"- 'budget 50 million' -> {{\"field\": \"budget\", \"value\": \"50 million\"}}\n"
                f"- 'length_of_stay to 4' -> {{\"field\": \"length_of_stay\", \"value\": \"4 days\"}}\n"
                f"Respond with ONLY the JSON, nothing else."
            )
            
            try:
                parse_result = self._generate_response(parse_prompt).strip()
                # Remove markdown code blocks if present
                if parse_result.startswith('```'):
                    parse_result = parse_result.split('\n', 1)[1].rsplit('\n', 1)[0].strip()
                
                parsed = json.loads(parse_result)
                
                if parsed.get('field') and parsed.get('value'):
                    return self.update_travel_detail(parsed['field'], parsed['value'])
                else:
                    return "Please specify both the field and new value (e.g., 'budget 5000' or 'change to 4 days')"
            except:
                # Fallback to simple parsing
                parts = message.split()
                if len(parts) >= 2:
                    field = parts[0]
                    value = ' '.join(parts[1:]).replace('to ', '')
                    return self.update_travel_detail(field, value)
                else:
                    return "Please specify both the field and new value (e.g., 'budget 5000' or 'change to 4 days')"
        
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
    