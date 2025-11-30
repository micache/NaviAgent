"""Tests for the ReceptionistAgent."""

import pytest

from reception.receptionist_agent import ConversationState, ReceptionistAgent


class TestReceptionistAgent:
    """Test suite for ReceptionistAgent."""

    @pytest.fixture
    def agent(self):
        """Create a fresh agent instance for each test."""
        return ReceptionistAgent()

    def test_initialization(self, agent):
        """Test agent initializes with correct default state."""
        assert agent.state == ConversationState.GREETING
        assert agent.travel_data["destination"] is None
        assert agent.travel_data["departure_point"] is None
        assert len(agent.travel_data) == 8

    def test_greet_customer(self, agent):
        """Test greeting functionality."""
        response = agent.greet_customer()
        assert "Welcome" in response
        assert "NaviAgent" in response
        assert agent.state == ConversationState.ASK_DESTINATION

    def test_handle_destination_inquiry_yes(self, agent):
        """Test handling when customer has destination."""
        agent.state = ConversationState.ASK_DESTINATION
        response = agent.handle_destination_inquiry("Yes, I have one")
        assert "destination" in response.lower()
        assert agent.state == ConversationState.COLLECT_DEPARTURE

    def test_handle_destination_inquiry_no(self, agent):
        """Test handling when customer needs suggestions."""
        agent.state = ConversationState.ASK_DESTINATION
        response = agent.handle_destination_inquiry("No, I need help")
        assert "describe" in response.lower() or "image" in response.lower()
        assert agent.state == ConversationState.SUGGEST_DESTINATION

    def test_collect_departure_point(self, agent):
        """Test collecting departure point."""
        response = agent.collect_departure_point("Ho Chi Minh City")
        assert agent.travel_data["departure_point"] == "Ho Chi Minh City"
        assert agent.state == ConversationState.COLLECT_TRAVEL_DATE
        assert "Ho Chi Minh City" in response

    def test_collect_travel_date(self, agent):
        """Test collecting travel date."""
        response = agent.collect_travel_date("December 25th")
        assert agent.travel_data["travel_date"] == "December 25th"
        assert agent.state == ConversationState.COLLECT_LENGTH_OF_STAY
        assert "December 25th" in response

    def test_collect_length_of_stay(self, agent):
        """Test collecting length of stay."""
        response = agent.collect_length_of_stay("5 days")
        assert agent.travel_data["length_of_stay"] == "5 days"
        assert agent.state == ConversationState.COLLECT_NUM_GUESTS
        assert "5 days" in response

    def test_collect_num_guests(self, agent):
        """Test collecting number of guests."""
        response = agent.collect_num_guests("3 people")
        assert agent.travel_data["num_guests"] == "3 people"
        assert agent.state == ConversationState.COLLECT_BUDGET
        assert "3 people" in response

    def test_collect_budget(self, agent):
        """Test collecting budget."""
        response = agent.collect_budget("1000 USD")
        assert agent.travel_data["budget"] == "1000 USD"
        assert agent.state == ConversationState.COLLECT_TRAVEL_STYLE
        assert "1000 USD" in response

    def test_collect_travel_style(self, agent):
        """Test collecting travel style."""
        response = agent.collect_travel_style("independent")
        assert agent.travel_data["travel_style"] == "independent"
        assert agent.state == ConversationState.COLLECT_NOTES
        assert "independent" in response

    def test_collect_special_notes(self, agent):
        """Test collecting special notes."""
        response = agent.collect_special_notes("vegetarian meals required")
        assert agent.travel_data["special_notes"] == "vegetarian meals required"
        assert agent.state == ConversationState.CONFIRM_DETAILS
        assert "Summary" in response

    def test_collect_special_notes_none(self, agent):
        """Test collecting special notes when customer has none."""
        response = agent.collect_special_notes("none")
        assert agent.travel_data["special_notes"] is None
        assert agent.state == ConversationState.CONFIRM_DETAILS

    def test_generate_summary(self, agent):
        """Test summary generation."""
        agent.travel_data = {
            "destination": "Da Lat",
            "departure_point": "Hanoi",
            "travel_date": "Jan 1",
            "length_of_stay": "3 days",
            "num_guests": "2",
            "budget": "500 USD",
            "travel_style": "tour",
            "special_notes": "early check-in",
        }
        summary = agent.generate_summary()
        assert "Da Lat" in summary
        assert "Hanoi" in summary
        assert "Jan 1" in summary
        assert "3 days" in summary
        assert "correct" in summary.lower()

    def test_handle_confirmation_yes(self, agent):
        """Test confirmation when customer approves."""
        agent.state = ConversationState.CONFIRM_DETAILS
        response = agent.handle_confirmation("Yes, looks perfect!")
        assert agent.state == ConversationState.COMPLETED
        assert "recorded" in response.lower() or "thank" in response.lower()

    def test_handle_confirmation_no(self, agent):
        """Test confirmation when customer wants changes."""
        agent.state = ConversationState.CONFIRM_DETAILS
        response = agent.handle_confirmation("No, I want to change something")
        assert agent.state == ConversationState.UPDATE_DETAILS
        assert "update" in response.lower()

    def test_update_travel_detail(self, agent):
        """Test updating a travel detail."""
        agent.travel_data["budget"] = "500 USD"
        response = agent.update_travel_detail("budget", "800 USD")
        assert agent.travel_data["budget"] == "800 USD"
        assert agent.state == ConversationState.CONFIRM_DETAILS
        assert "800 USD" in response

    def test_update_invalid_field(self, agent):
        """Test updating an invalid field."""
        response = agent.update_travel_detail("invalid_field", "value")
        assert "couldn't find" in response.lower()

    def test_get_travel_data(self, agent):
        """Test getting travel data returns a copy."""
        agent.travel_data["destination"] = "Test"
        data = agent.get_travel_data()
        data["destination"] = "Modified"
        assert agent.travel_data["destination"] == "Test"

    def test_reset(self, agent):
        """Test resetting agent state."""
        agent.state = ConversationState.COMPLETED
        agent.travel_data["destination"] = "Test"
        agent.reset()
        assert agent.state == ConversationState.GREETING
        assert agent.travel_data["destination"] is None

    def test_process_message_greeting(self, agent):
        """Test processing message in greeting state."""
        response = agent.process_message("")
        assert "Welcome" in response
        assert agent.state == ConversationState.ASK_DESTINATION

    def test_process_message_flow(self, agent):
        """Test complete conversation flow."""
        # Start
        response = agent.process_message("")
        assert agent.state == ConversationState.ASK_DESTINATION

        # Has destination
        response = agent.process_message("Yes")
        assert agent.state == ConversationState.COLLECT_DEPARTURE

        # Provide destination
        response = agent.process_message("Paris")
        assert agent.state == ConversationState.COLLECT_TRAVEL_DATE

        # Travel date
        response = agent.process_message("June 1")
        assert agent.state == ConversationState.COLLECT_LENGTH_OF_STAY

        # Length
        response = agent.process_message("7 days")
        assert agent.state == ConversationState.COLLECT_NUM_GUESTS

        # Guests
        response = agent.process_message("2")
        assert agent.state == ConversationState.COLLECT_BUDGET

        # Budget
        response = agent.process_message("2000 USD")
        assert agent.state == ConversationState.COLLECT_TRAVEL_STYLE

        # Style
        response = agent.process_message("independent")
        assert agent.state == ConversationState.COLLECT_NOTES

        # Notes
        response = agent.process_message("none")
        assert agent.state == ConversationState.CONFIRM_DETAILS

        # Confirm
        response = agent.process_message("yes")
        assert agent.state == ConversationState.COMPLETED


class TestConversationState:
    """Test ConversationState enum."""

    def test_conversation_states_exist(self):
        """Test all expected states are defined."""
        expected_states = [
            "GREETING",
            "ASK_DESTINATION",
            "SUGGEST_DESTINATION",
            "COLLECT_DEPARTURE",
            "COLLECT_TRAVEL_DATE",
            "COLLECT_LENGTH_OF_STAY",
            "COLLECT_NUM_GUESTS",
            "COLLECT_BUDGET",
            "COLLECT_TRAVEL_STYLE",
            "COLLECT_NOTES",
            "CONFIRM_DETAILS",
            "UPDATE_DETAILS",
            "COMPLETED",
        ]
        for state_name in expected_states:
            assert hasattr(ConversationState, state_name)
