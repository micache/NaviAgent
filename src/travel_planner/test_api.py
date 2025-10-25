"""
Test script for Travel Planner API
Run this after starting the API server
"""

import json
from pprint import pprint

import requests


def test_health_check():
    """Test health check endpoint"""
    print("\n" + "=" * 80)
    print("Testing Health Check Endpoint")
    print("=" * 80)

    response = requests.get("http://localhost:8000/v1/health")
    print(f"Status Code: {response.status_code}")
    print("Response:")
    pprint(response.json())


def test_plan_trip():
    """Test plan trip endpoint"""
    print("\n" + "=" * 80)
    print("Testing Plan Trip Endpoint")
    print("=" * 80)

    # Sample request with departure_date
    request_data = {
        "departure_point": "Hanoi",
        "destination": "Châu Âu",
        "departure_date": "2025-12-15",  # Added departure date
        "budget": 50000000,
        "num_travelers": 2,
        "trip_duration": 7,
        "travel_style": "self_guided",
        "customer_notes": "Thích địa điểm đẹp, chụp ảnh sống.",
    }

    print("\nRequest Data:")
    pprint(request_data)

    print("\nSending request (this may take 2-5 minutes)...")
    print("Weather Agent will search for seasonal events and weather forecast...")
    print("Please wait...")

    try:
        response = requests.post(
            "http://localhost:8000/v1/plan_trip",
            json=request_data,
            timeout=900,  # 15 minutes timeout (increased from 10)
        )

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            print("\n✓ Travel plan generated successfully!")
            travel_plan = response.json()

            # Print summary
            print("\n" + "-" * 80)
            print("TRAVEL PLAN SUMMARY")
            print("-" * 80)

            print(f"\nVersion: {travel_plan['version']}")
            print(f"Generated at: {travel_plan['generated_at']}")

            # Itinerary summary
            if travel_plan.get("itinerary"):
                itinerary = travel_plan["itinerary"]
                print(f"\n✓ Itinerary: {len(itinerary['daily_schedules'])} days planned")
                print(f"  Main locations: {', '.join(itinerary['location_list'][:5])}")
                if itinerary.get('selected_flight'):
                    print(f"  Selected Flight: {itinerary['selected_flight']['airline']}")
                if itinerary.get('selected_accommodation'):
                    print(f"  Selected Hotel: {itinerary['selected_accommodation']['name']}")

            # Budget summary
            if travel_plan.get("budget"):
                budget = travel_plan["budget"]
                print(f"\n✓ Budget:")
                print(f"  Total Estimated Cost: {budget['total_estimated_cost']:,.0f} VND")
                print(f"  Budget Status: {budget['budget_status']}")
                print(f"  Categories: {len(budget['categories'])} items")

            # Advisory summary
            if travel_plan.get("advisory"):
                advisory = travel_plan["advisory"]
                print(f"\n✓ Advisory:")
                print(f"  Tips & Warnings: {len(advisory['warnings_and_tips'])} items")
                print(f"  Location Descriptions: {len(advisory['location_descriptions'])} locations")

            # Souvenirs
            if travel_plan.get("souvenirs"):
                print(f"\n✓ Souvenirs: {len(travel_plan['souvenirs'])} suggestions")

            # Logistics
            if travel_plan.get("logistics"):
                logistics = travel_plan["logistics"]
                print(f"\n✓ Logistics:")
                print(f"  Flight Options: {len(logistics['flight_options'])} available")
                print(f"  Average Price: {logistics['average_price']:,.0f} VND/person")

            # Accommodation
            if travel_plan.get("accommodation"):
                accommodation = travel_plan["accommodation"]
                print(f"\n✓ Accommodation:")
                print(f"  Recommendations: {len(accommodation['recommendations'])} options")
                print(f"  Total Estimated: {accommodation['total_estimated_cost']:,.0f} VND")

            # Save to file
            output_file = "travel_plan_output.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(travel_plan, f, indent=2, ensure_ascii=False)

            print(f"\n✓ Full travel plan saved to: {output_file}")
            print(f"✓ Structured JSON with all fields populated!")

        else:
            print("\n✗ Error generating travel plan")
            print("Response:")
            pprint(response.json())

    except requests.exceptions.Timeout:
        print("\n✗ Request timeout (>15 minutes)")
        print("The server might still be processing. Check server logs.")
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection error")
        print("Make sure the API server is running at http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


def test_config():
    """Test config endpoint"""
    print("\n" + "=" * 80)
    print("Testing Config Endpoint")
    print("=" * 80)

    response = requests.get("http://localhost:8000/v1/config")
    print(f"Status Code: {response.status_code}")
    print("Response:")
    pprint(response.json())


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TRAVEL PLANNER API - TEST SCRIPT")
    print("=" * 80)
    print("\nMake sure the API server is running:")
    print("  cd travel_planner_api")
    print("  python main.py")
    print("\nThen run this script:")
    print("  python test_api.py")
    print("=" * 80)

    # Run tests
    try:
        test_health_check()
        test_config()

        print("\n" + "=" * 80)
        print("Starting main test - Plan Trip")
        print("This will take several minutes...")
        print("=" * 80)

        test_plan_trip()

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed: {str(e)}")

    print("\n" + "=" * 80)
    print("Tests completed")
    print("=" * 80 + "\n")
