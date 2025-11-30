"""Receptionist Agent - Simplified version without FSM."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

from reception.suggest_destination.suggest_from_images import DuckDuckGoImagesAgent
from reception.suggest_destination.suggest_from_text import get_destination_suggestion

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")
supabase_url = os.getenv("DATABASE_URL")

db = PostgresDb(db_url=supabase_url)


class ReceptionistAgent(Agent):
    """A conversational receptionist agent for travel planning.

    No state machine - LLM handles the conversation flow naturally.
    """

    def __init__(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """Initialize the receptionist agent.

        Args:
            user_id: User ID for this conversation
            session_id: Session ID for continuing conversations
            storage: Storage for persisting chat history
        """
        # Travel data storage
        self.travel_data: Dict[str, Any] = {
            "destination": None,
            "departure_point": None,
            "departure_date": None,
            "trip_duration": None,
            "num_travelers": None,
            "budget": None,
            "travel_style": None,
            "customer_notes": None,
        }

        # Image agent for destination suggestions
        self.image_agent = DuckDuckGoImagesAgent()

        # Instructions for the agent (in English for consistency)
        instructions = [
            "You are a professional travel receptionist for NaviAgent Travel Service.",
            "Mission: Collect information to create a travel plan for customers.",
            "IMPORTANT: Always respond to customers in Vietnamese, friendly and natural.",
            "",
            "INFORMATION TO COLLECT (in order):",
            "1. destination - If customer doesn't know → ask preferences to suggest",
            "2. departure_point - Where they depart from",
            "3. departure_date - When they want to depart",
            "4. trip_duration - How many days",
            "5. num_travelers - Number of people",
            "6. budget - Budget amount in VND",
            "7. travel_style - Ask if they want 'tự túc' or 'tour' (internally saved as 'self-guided' or 'tour')",
            "8. customer_notes - Any special requests or notes (optional)",
            "",
            "RULES:",
            "- Ask ONE piece of information at a time, DON'T ask multiple at once",
            "- IMMEDIATELY call the appropriate save tool when customer provides information",
            "- If customer provides multiple info at once → save ALL using respective tools",
            "- If customer changes information → update and confirm",
            "- ALWAYS ask for customer_notes (item 8) after collecting travel_style",
            "- After collecting all info including customer_notes → summarize and ask for confirmation",
            "- Always respond in Vietnamese, friendly, natural tone",
            "- DON'T include validation rules in your questions (like 'must be > 0', 'must be future date')",
            "- DON'T include English translations in your questions (like 'self-guided hoặc tour')",
            "- Use ONLY Vietnamese terms when asking questions (e.g., 'tự túc' or 'tour')",
            "- The tools will handle validation automatically",
            "",
            "USING TOOLS:",
            "- ALWAYS use suggest_from_text() when customer describes their ideal trip",
            "- ALWAYS use suggest_from_image() when customer provides an image URL",
            "- ALWAYS use save_destination() IMMEDIATELY when customer mentions destination",
            "- ALWAYS use save_departure() IMMEDIATELY when customer mentions departure point",
            "- ALWAYS use save_dates() IMMEDIATELY when customer mentions dates and duration",
            "- ALWAYS use save_travelers() IMMEDIATELY when customer mentions number of people",
            "- ALWAYS use save_budget() IMMEDIATELY when customer mentions budget",
            "- ALWAYS use save_style() IMMEDIATELY when customer mentions travel style",
            "- ALWAYS use save_notes() when customer mentions special requests (optional)",
            "- ALWAYS use get_travel_summary() to view collected information",
            "- ALWAYS use export_travel_data() when customer confirms → this displays JSON and ENDS conversation",
            "- After calling export_travel_data(), the conversation is COMPLETE - don't ask anything more",
        ]

        # Create bound tools that close over self
        def suggest_from_text(description: str) -> str:
            """Suggest destination based on customer's description of ideal trip."""
            return self._suggest_from_text(description)

        def suggest_from_image(image_url: str) -> str:
            """Suggest destination based on an image provided by customer."""
            return self._suggest_from_image(image_url)

        def save_destination(destination: str) -> str:
            """Save the travel destination."""
            return self._save_destination(destination)

        def save_departure(departure_point: str) -> str:
            """Save the departure point."""
            return self._save_departure(departure_point)

        def save_dates(departure_date: str, trip_duration: str) -> str:
            """Save travel dates and duration."""
            return self._save_dates(departure_date, trip_duration)

        def save_travelers(num_travelers: int) -> str:
            """Save number of travelers."""
            return self._save_travelers(num_travelers)

        def save_budget(budget: str) -> str:
            """Save travel budget."""
            return self._save_budget(budget)

        def save_style(travel_style: str) -> str:
            """Save travel style preference."""
            return self._save_style(travel_style)

        def save_notes(notes: str) -> str:
            """Save additional notes or requests."""
            return self._save_notes(notes)

        def get_travel_summary() -> str:
            """Get summary of collected travel information."""
            return self._get_travel_summary()

        def export_travel_data() -> str:
            """Export travel data as JSON after customer confirms."""
            return self._export_travel_data()

        # Initialize parent Agent
        super().__init__(
            model=OpenAIChat(
                id=model,
                api_key=api_key,
            ),
            user_id=user_id,
            session_id=session_id,
            db=db,
            add_history_to_context=True,
            num_history_runs=5,
            read_chat_history=True,
            instructions=instructions,
            tools=[
                suggest_from_text,
                suggest_from_image,
                save_destination,
                save_departure,
                save_dates,
                save_travelers,
                save_budget,
                save_style,
                save_notes,
                get_travel_summary,
                export_travel_data,
            ],
            markdown=True,
        )

    def _suggest_from_text(self, description: str) -> str:
        """Suggest destination based on customer's description of ideal trip.

        Args:
            description: Customer's description (e.g., "quiet beach with good food")

        Returns:
            Suggested destination with reasoning
        """
        try:
            suggestion_json = get_destination_suggestion(description)
            suggestion = json.loads(suggestion_json)

            destination = suggestion.get("destination")
            reason = suggestion.get("reason")

            return f"Based on your description, I recommend {destination}. {reason}"
        except Exception as e:
            return f"I encountered an error while suggesting: {str(e)}. Could you describe your ideal trip differently?"

    def _suggest_from_image(self, image_url: str) -> str:
        """Suggest destination based on an image provided by customer.

        Args:
            image_url: URL of the image

        Returns:
            Location identification and description
        """
        try:
            result = self.image_agent.search_image_location(image_url)

            # Parse result
            location = None
            description = None

            if isinstance(result, str):
                try:
                    parsed = json.loads(result)
                    if isinstance(parsed, dict):
                        location = parsed.get("location", "Unknown location")
                        description = parsed.get("description", "")
                except json.JSONDecodeError:
                    if "location" in result.lower():
                        lines = result.split("\n")
                        for i, line in enumerate(lines):
                            if '"location":' in line:
                                location = line.split('"location":')[1].strip().strip(',"')
                            elif '"description":' in line:
                                desc_start = line.split('"description":')[1].strip().strip('"')
                                remaining = "\n".join(lines[i:])
                                if '"}' in remaining:
                                    description = remaining.split('"}')[0].strip().strip('"')
                                else:
                                    description = desc_start
                    else:
                        location = str(result)
            elif isinstance(result, dict):
                location = result.get("location", "Unknown location")
                description = result.get("description", "")

            if not location:
                location = "this location"
                description = "I identified a travel destination from your image."

            return f"This appears to be {location}! {description}"
        except Exception as e:
            return f"I couldn't identify the location: {str(e)}. Could you try another image?"

    def _save_destination(self, destination: str) -> str:
        """Save the travel destination in 'City, Country' format.

        Args:
            destination: Travel destination (e.g., "Đà Lạt", "Paris", "Tokyo")

        Returns:
            Confirmation message
        """
        # Check if already in "City, Country" format
        if "," in destination:
            formatted_dest = destination.strip()
        else:
            # Use LLM to infer country from city
            try:
                prompt = (
                    f"Convert this destination to 'City, Country' format: '{destination}'\n\n"
                    f"Examples:\n"
                    f"- 'Đà Lạt' → 'Da Lat, Vietnam'\n"
                    f"- 'Paris' → 'Paris, France'\n"
                    f"- 'Tokyo' → 'Tokyo, Japan'\n"
                    f"- 'Hồ Chí Minh' → 'Ho Chi Minh City, Vietnam'\n"
                    f"- 'New York' → 'New York, United States'\n\n"
                    f"Return ONLY 'City, Country' format, nothing else."
                )

                response = self.run(prompt)
                formatted_dest = response.content.strip()

                # Fallback if conversion fails
                if "," not in formatted_dest:
                    formatted_dest = destination
            except Exception:
                # If anything fails, just use the original
                formatted_dest = destination

        self.travel_data["destination"] = formatted_dest
        return f"✓ Đã lưu điểm đến: {formatted_dest}"

    def _save_departure(self, departure_point: str) -> str:
        """Save the departure point.

        Args:
            departure_point: Departure city (e.g., "Hà Nội", "Hồ Chí Minh")

        Returns:
            Confirmation message
        """
        self.travel_data["departure_point"] = departure_point
        return f"✓ Đã lưu điểm xuất phát: {departure_point}"

    def _save_dates(self, departure_date: str, trip_duration: str) -> str:
        """Save travel dates and duration.

        Args:
            departure_date: Departure date (e.g., "2025-12-20", "20/12/2025")
            trip_duration: Trip duration (e.g., "3 ngày", "1 tuần")

        Returns:
            Confirmation message
        """
        from datetime import datetime

        # Validate departure date is in the future
        try:
            # Try parsing different date formats
            date_obj = None
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]:
                try:
                    date_obj = datetime.strptime(departure_date, fmt)
                    break
                except:
                    continue

            if date_obj:
                if date_obj.date() <= datetime.now().date():
                    return "❌ Ngày khởi hành phải là ngày trong tương lai. Vui lòng chọn ngày khác."
            else:
                return "❌ Không thể đọc được định dạng ngày. Vui lòng nhập theo định dạng DD/MM/YYYY hoặc YYYY-MM-DD."
        except Exception as e:
            return f"❌ Lỗi khi kiểm tra ngày: {str(e)}"

        # Validate trip duration is positive
        try:
            # Extract number from trip_duration
            import re

            duration_match = re.search(r"(\d+)", trip_duration)
            if duration_match:
                days = int(duration_match.group(1))
                if days <= 0:
                    return "❌ Thời gian chuyến đi phải lớn hơn 0 ngày."
            else:
                return "❌ Không thể đọc được thời gian chuyến đi. Vui lòng nhập số ngày rõ ràng."
        except:
            pass  # If can't parse, still save

        self.travel_data["departure_date"] = departure_date
        self.travel_data["trip_duration"] = trip_duration
        return f"✓ Đã lưu ngày: {departure_date}, thời gian: {trip_duration}"

    def _save_travelers(self, num_travelers: int) -> str:
        """Save number of travelers.

        Args:
            num_travelers: Number of people traveling

        Returns:
            Confirmation message
        """
        self.travel_data["num_travelers"] = num_travelers
        return f"✓ Đã lưu số người: {num_travelers}"

    def _save_budget(self, budget: str) -> str:
        """Save travel budget.

        Args:
            budget: Budget amount (e.g., "10 triệu", "5-7 triệu VND")

        Returns:
            Confirmation message
        """
        import re

        # Extract budget amount in VND
        budget_vnd = None
        try:
            # Look for numbers
            numbers = re.findall(r"(\d+(?:[.,]\d+)?)", budget.lower())
            if numbers:
                amount = float(numbers[0].replace(",", "."))

                # Convert to VND if needed
                if "triệu" in budget.lower() or "million" in budget.lower():
                    budget_vnd = amount * 1_000_000
                elif "tỷ" in budget.lower() or "billion" in budget.lower():
                    budget_vnd = amount * 1_000_000_000
                elif (
                    "nghìn" in budget.lower()
                    or "thousand" in budget.lower()
                    or "k" in budget.lower()
                ):
                    budget_vnd = amount * 1_000
                elif "usd" in budget.lower() or "$" in budget:
                    budget_vnd = amount * 25_000  # Approximate rate
                else:
                    budget_vnd = amount
        except:
            pass

        # Validate budget reasonableness
        if budget_vnd and self.travel_data.get("destination"):
            destination = self.travel_data["destination"].lower()
            num_travelers = self.travel_data.get("num_travelers", 1)
            trip_duration = self.travel_data.get("trip_duration", "3")

            # Extract days
            import re

            duration_match = re.search(r"(\d+)", str(trip_duration))
            days = int(duration_match.group(1)) if duration_match else 3

            # Rough estimate: minimum budget per person per day
            international_destinations = [
                "paris",
                "london",
                "tokyo",
                "new york",
                "singapore",
                "sydney",
                "dubai",
            ]
            is_international = any(dest in destination for dest in international_destinations)

            min_per_day = 2_000_000 if is_international else 500_000  # VND per person per day
            min_budget = min_per_day * num_travelers * days

            if budget_vnd < min_budget * 0.5:  # Allow some flexibility
                return (
                    f"⚠️ Ngân sách {budget} có vẻ thấp cho chuyến đi {days} ngày đến {self.travel_data['destination']} "
                    f"với {num_travelers} người. Ngân sách tối thiểu gợi ý: {min_budget:,.0f} VND. "
                    f"Bạn có chắc chắn muốn tiếp tục với ngân sách này không?"
                )

        self.travel_data["budget"] = budget
        return f"✓ Đã lưu ngân sách: {budget}"

    def _save_style(self, travel_style: str) -> str:
        """Save travel style preference.

        Args:
            travel_style: Travel style (ONLY 'self-guided' or 'tour')

        Returns:
            Confirmation message
        """
        style_lower = travel_style.lower().strip()

        # Map various terms to standard values
        if any(
            term in style_lower for term in ["self", "tự túc", "độc lập", "diy", "tự do", "tự đi"]
        ):
            standard_style = "self-guided"
            display_name = "tự túc"
        elif any(term in style_lower for term in ["tour", "đoàn", "hướng dẫn", "guide"]):
            standard_style = "tour"
            display_name = "tour"
        else:
            return "❌ Phong cách du lịch chỉ có thể là 'tự túc' hoặc 'tour'. Vui lòng chọn một trong hai."

        self.travel_data["travel_style"] = standard_style
        return f"✓ Đã lưu phong cách: {display_name}"

    def _save_notes(self, notes: str) -> str:
        """Save additional notes or requests.

        Args:
            notes: Customer notes or special requests

        Returns:
            Confirmation message
        """
        # Check if customer said no/none
        notes_lower = notes.lower().strip()
        if notes_lower in ["không", "ko", "khong", "no", "none", "nothing", "không có", "ko có"]:
            self.travel_data["customer_notes"] = None
            return "✓ Không có ghi chú đặc biệt"

        self.travel_data["customer_notes"] = notes
        return f"✓ Đã lưu ghi chú: {notes}"

    def _get_travel_summary(self) -> str:
        """Get summary of collected travel information.

        Returns:
            Summary of all collected data
        """
        summary = "📋 THÔNG TIN ĐÃ THU THẬP:\n\n"

        if self.travel_data["destination"]:
            summary += f"📍 Điểm đến: {self.travel_data['destination']}\n"
        if self.travel_data["departure_point"]:
            summary += f"🚀 Xuất phát: {self.travel_data['departure_point']}\n"
        if self.travel_data["departure_date"]:
            summary += f"📅 Ngày đi: {self.travel_data['departure_date']}\n"
        if self.travel_data["trip_duration"]:
            summary += f"⏱️ Thời gian: {self.travel_data['trip_duration']}\n"
        if self.travel_data["num_travelers"]:
            summary += f"👥 Số người: {self.travel_data['num_travelers']}\n"
        if self.travel_data["budget"]:
            summary += f"💰 Ngân sách: {self.travel_data['budget']}\n"
        if self.travel_data["travel_style"]:
            summary += f"🎨 Phong cách: {self.travel_data['travel_style']}\n"
        if self.travel_data["customer_notes"]:
            summary += f"📝 Ghi chú: {self.travel_data['customer_notes']}\n"

        # Check missing fields
        missing = []
        required_fields = {
            "destination": "Điểm đến",
            "departure_point": "Điểm xuất phát",
            "departure_date": "Ngày đi",
            "trip_duration": "Thời gian",
            "num_travelers": "Số người",
            "budget": "Ngân sách",
            "travel_style": "Phong cách",
        }

        for field, label in required_fields.items():
            if not self.travel_data[field]:
                missing.append(label)

        if missing:
            summary += f"\n⚠️ Còn thiếu: {', '.join(missing)}"
        else:
            summary += "\n✅ Đã đủ thông tin!"

        return summary

    def _export_travel_data(self) -> str:
        """Export travel data as JSON after confirmation and end conversation.

        Returns:
            JSON string of travel data with goodbye message
        """
        # Check if all required fields are filled
        required_fields = [
            "destination",
            "departure_point",
            "departure_date",
            "trip_duration",
            "num_travelers",
            "budget",
            "travel_style",
        ]

        missing = [f for f in required_fields if not self.travel_data.get(f)]
        if missing:
            return f"❌ Không thể hoàn tất vì còn thiếu thông tin: {', '.join(missing)}"

        # Export as formatted JSON
        json_output = json.dumps(self.travel_data, ensure_ascii=False, indent=2)

        return (
            f"🎉 Cảm ơn bạn! Đây là thông tin chuyến đi của bạn:\n\n"
            f"```json\n{json_output}\n```\n\n"
            f"Chúc bạn có một chuyến đi tuyệt vời! 🌏✈️"
        )

    def get_travel_data(self) -> Dict[str, Any]:
        """Get the collected travel data.

        Returns:
            Dictionary of travel data
        """
        return self.travel_data.copy()

    def greet_customer(self) -> str:
        """Generate initial greeting.

        Returns:
            Greeting message in Vietnamese
        """
        greeting_prompt = (
            "Greet the customer for the first time. Introduce yourself as a receptionist at NaviAgent Travel Service. "
            "Ask if they already have a destination in mind (yes/no). "
            "If yes → ask for the destination name. "
            "If no → mention you can suggest based on their preferences. "
            "Remember to respond in Vietnamese."
        )
        response = self.run(greeting_prompt)
        return response.content


# def main():
#     """Interactive chat with receptionist agent."""
#     print("=" * 60)
#     print("NaviAgent Receptionist v2 - Interactive Test")
#     print("=" * 60)
#     print("Type 'quit' or 'exit' to end the conversation")
#     print("Type 'data' to see collected travel data")
#     print("Type 'reset' to start over")
#     print("=" * 60)
#     print()

#     # Create agent (without storage for testing)
#     agent = ReceptionistAgent(
#         user_id="test_user",
#         session_id="test_session"
#     )

#     # Initial greeting
#     greeting = agent.greet_customer()
#     print(f"AGENT: {greeting}")
#     print()

#     # Chat loop
#     while True:
#         try:
#             # Get user input
#             user_input = input("YOU: ").strip()

#             if not user_input:
#                 continue

#             # Check commands
#             if user_input.lower() in ['quit', 'exit', 'q']:
#                 print("\nGoodbye! 👋")
#                 break

#             if user_input.lower() == 'data':
#                 print("\n📋 TRAVEL DATA:")
#                 data = agent.get_travel_data()
#                 for key, value in data.items():
#                     if value:
#                         print(f"  {key}: {value}")
#                 print()
#                 continue

#             if user_input.lower() == 'reset':
#                 agent = ReceptionistAgent(
#                     user_id="test_user",
#                     session_id="test_session_new"
#                 )
#                 greeting = agent.greet_customer()
#                 print(f"\nAGENT: {greeting}\n")
#                 continue

#             # Send message to agent
#             response = agent.run(user_input)
#             print(f"AGENT: {response.content}")
#             print()

#             if "chúc bạn có một chuyến đi tuyệt vời" in response.content.lower():
#                 print("Conversation ended. Goodbye! 👋")
#                 break

#         except KeyboardInterrupt:
#             print("\n\nInterrupted. Goodbye! 👋")
#             break
#         except Exception as e:
#             print(f"\n❌ Error: {e}\n")


# if __name__ == "__main__":
#     main()
