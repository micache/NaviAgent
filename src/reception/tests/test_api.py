"""Tests for NaviAgent Receptionist API v2 (session-based)."""

from fastapi.testclient import TestClient

from reception.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "NaviAgent Receptionist API"
    assert data["version"] == "2.0.0"
    assert "endpoints" in data


def test_start_chat():
    """Test starting a new chat session."""
    response = client.post("/start_chat", json={"user_id": "6986c9c3-947d-4978-88c2-0a2797fdc86c"})

    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

    assert response.status_code == 200
    data = response.json()

    # Should return session_id and greeting
    assert "session_id" in data
    assert "message" in data
    assert len(data["session_id"]) > 0
    assert "chào" in data["message"].lower() or "xin chào" in data["message"].lower()

    return data["session_id"]


def test_chat_with_session():
    """Test sending messages in a session."""
    # Start a new session
    start_response = client.post(
        "/start_chat", json={"user_id": "6986c9c3-947d-4978-88c2-0a2797fdc86c"}
    )

    if start_response.status_code != 200:
        print(f"❌ Start chat error: {start_response.status_code}")
        print(f"Response: {start_response.text}")

    assert start_response.status_code == 200
    data = start_response.json()

    if "session_id" not in data:
        print(f"❌ Missing session_id in response: {data}")

    session_id = data["session_id"]

    # Answer yes to destination question
    response1 = client.post("/chat", json={"session_id": session_id, "message": "có"})
    assert response1.status_code == 200
    data1 = response1.json()
    assert "message" in data1
    assert "travel_data" in data1

    # Provide destination
    response2 = client.post(
        "/chat", json={"session_id": session_id, "message": "Tôi muốn đi Đà Lạt"}
    )
    assert response2.status_code == 200
    data2 = response2.json()

    # Check destination is saved (now in "City, Country" format)
    assert data2["travel_data"]["destination"] is not None
    assert "vietnam" in data2["travel_data"]["destination"].lower()

    # Provide departure point
    response3 = client.post(
        "/chat", json={"session_id": session_id, "message": "Tôi xuất phát từ Hồ Chí Minh"}
    )
    assert response3.status_code == 200
    data3 = response3.json()
    assert data3["travel_data"]["departure_point"] is not None


def test_full_conversation_flow():
    """Test a complete conversation flow."""
    # Start session
    start_response = client.post(
        "/start_chat", json={"user_id": "6986c9c3-947d-4978-88c2-0a2797fdc86c"}
    )
    session_id = start_response.json()["session_id"]

    # Answer yes
    client.post("/chat", json={"session_id": session_id, "message": "có"})

    # Provide all information
    responses = [
        {"message": "Tôi muốn đi Nha Trang", "expected_field": "destination"},
        {"message": "Xuất phát từ Hà Nội", "expected_field": "departure_point"},
        {"message": "Ngày 20/12/2025", "expected_field": "departure_date"},
        {"message": "3 ngày", "expected_field": "trip_duration"},
        {"message": "2 người", "expected_field": "num_travelers"},
        {"message": "10 triệu", "expected_field": "budget"},
        {"message": "tự túc", "expected_field": "travel_style"},
        {"message": "không", "expected_field": "customer_notes"},
    ]

    for req in responses:
        response = client.post("/chat", json={"session_id": session_id, "message": req["message"]})
        assert response.status_code == 200
        data = response.json()

        # Check field is present (may be None for customer_notes)
        field = req["expected_field"]
        assert field in data["travel_data"], f"{field} should be in travel_data"

    # Final check - all fields should be filled
    print("\n✅ Confirming...")
    final_response = client.post("/chat", json={"session_id": session_id, "message": "ok"})
    data = final_response.json()

    # Debug: check what we got
    print(f"📝 Response message: {data['message'][:200]}...")
    print(f"📊 Travel data: {data['travel_data']}")
    print(f"🎯 Is complete: {data.get('is_complete', False)}")

    # After confirmation, API should mark conversation as complete
    assert data.get("is_complete") == True, "Conversation should be complete after confirmation"

    # Travel data should have been saved throughout the conversation
    travel_data = data["travel_data"]
    assert travel_data["destination"] is not None, f"Destination is None! Data: {travel_data}"
    assert (
        travel_data["departure_point"] is not None
    ), f"Departure point is None! Data: {travel_data}"
    assert travel_data["departure_date"] is not None, f"Departure date is None! Data: {travel_data}"
    assert travel_data["trip_duration"] is not None, f"Trip duration is None! Data: {travel_data}"
    assert travel_data["num_travelers"] is not None, f"Num travelers is None! Data: {travel_data}"
    assert travel_data["budget"] is not None, f"Budget is None! Data: {travel_data}"
    assert travel_data["travel_style"] is not None, f"Travel style is None! Data: {travel_data}"
    # customer_notes can be None

    print(
        f"✅ Travel data collected successfully: {travel_data['destination']} from {travel_data['departure_point']}"
    )


def test_invalid_session():
    """Test using an invalid session_id."""
    response = client.post("/chat", json={"session_id": "invalid_session_xyz", "message": "Hello"})

    # Should handle gracefully (might return error or create new session)
    # Depending on implementation
    assert response.status_code in [200, 404, 500]


def main():
    """Run all tests."""
    print("Running tests...")
    test_root_endpoint()
    print("✅ test_root_endpoint passed")

    test_start_chat()
    print("✅ test_start_chat passed")

    test_chat_with_session()
    print("✅ test_chat_with_session passed")

    test_full_conversation_flow()
    print("✅ test_full_conversation_flow passed")

    test_invalid_session()
    print("✅ test_invalid_session passed")

    print("\n🎉 All tests passed!")


if __name__ == "__main__":
    main()
