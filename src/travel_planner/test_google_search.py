"""
Test script for Travel Planner API with Google Search
"""
import requests
import json

# API endpoint
API_URL = "http://localhost:8000/v1/plan_trip"

# Test data - A simple trip request
test_request = {
    "destination": "Paris",
    "departure_point": "New York",
    "duration": 3,
    "budget": 3000.0,
    "num_travelers": 2,
    "travel_date": "2025-06-15",
    "travel_style": "self_guided"
}

def test_api():
    """Test the Travel Planner API"""
    print("=" * 80)
    print("Testing Travel Planner API with Google Search")
    print("=" * 80)
    print(f"\nRequest Data:")
    print(json.dumps(test_request, indent=2))
    print("\n" + "=" * 80)
    print("Sending request to API...")
    print("This may take 1-2 minutes as agents search and process information...")
    print("=" * 80 + "\n")
    
    try:
        response = requests.post(API_URL, json=test_request, timeout=300)
        
        if response.status_code == 200:
            print("✅ SUCCESS! Received response from API")
            print("=" * 80)
            
            result = response.json()
            
            # Print summary
            print("\n📋 TRAVEL PLAN SUMMARY:")
            print("=" * 80)
            
            if "itinerary" in result:
                print(f"✓ Itinerary: {len(result['itinerary'].get('daily_schedules', []))} days planned")
                if result['itinerary'].get('daily_schedules'):
                    first_day = result['itinerary']['daily_schedules'][0]
                    print(f"  - Day 1: {first_day.get('title', 'N/A')}")
                    print(f"  - Activities: {len(first_day.get('activities', []))}")
            
            if "budget" in result:
                print(f"✓ Budget: Total estimated cost: {result['budget'].get('total_estimated_cost', 'N/A')}")
                print(f"  - Status: {result['budget'].get('budget_status', 'N/A')}")
            
            if "advisories" in result:
                warnings = result['advisories'].get('warnings_and_tips', [])
                print(f"✓ Travel Advisories: {len(warnings)} tips/warnings")
                locations = result['advisories'].get('location_descriptions', [])
                print(f"  - Location Descriptions: {len(locations)} locations")
            
            if "souvenirs" in result:
                print(f"✓ Souvenirs: {len(result.get('souvenirs', []))} recommendations")
            
            if "logistics" in result:
                print(f"✓ Logistics: Flight info and accommodation suggestions provided")
            
            # Save full response to file
            with open("test_response.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print("\n" + "=" * 80)
            print("✅ Full response saved to: test_response.json")
            print("=" * 80)
            
        else:
            print(f"❌ ERROR: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out (took longer than 5 minutes)")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to API. Is the server running?")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    test_api()
