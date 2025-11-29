from enum import Enum

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