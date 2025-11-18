"""Quick API test"""

import json
from datetime import date

import requests

# Test health check
print("Testing health check...")
response = requests.get("http://localhost:8000/v1/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test travel plan
print("Testing travel plan with parser...")
print("This will take 2-3 minutes (Team + Parser)...\n")

request_data = {
    "destination": "Paris, France",
    "departure_point": "Hanoi",
    "departure_date": "2024-06-01",
    "trip_duration": 3,
    "budget": 20000000,
    "num_travelers": 2,
    "travel_style": "self_guided",
    "customer_notes": "First time in Europe",
}

response = requests.post("http://localhost:8000/v1/plan_trip", json=request_data, timeout=600)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"\n✅ SUCCESS! Structured JSON response received!")
    print(f"Version: {result['version']}")

    # Check structured fields
    if result.get("itinerary"):
        print(f"✓ Itinerary: {len(result['itinerary']['daily_schedules'])} days")
    if result.get("budget"):
        print(f"✓ Budget: {result['budget']['total_estimated_cost']:,.0f} VND")
    if result.get("advisory"):
        print(f"✓ Advisory: {len(result['advisory']['warnings_and_tips'])} tips")
    if result.get("souvenirs"):
        print(f"✓ Souvenirs: {len(result['souvenirs'])} suggestions")
    if result.get("logistics"):
        print(f"✓ Logistics: {len(result['logistics']['flight_options'])} flights")
    if result.get("accommodation"):
        print(f"✓ Accommodation: {len(result['accommodation']['recommendations'])} hotels")

    # Save to file
    with open("travel_plan_structured.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved to: travel_plan_structured.json")

else:
    print(f"\n❌ FAILED!")
    print(f"Error: {response.json()}")
