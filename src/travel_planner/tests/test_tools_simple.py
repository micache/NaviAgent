"""
Simple Test - External API Tools Integration
Tests tools directly like plain Python functions
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.external_api_tools import (
    create_flight_tools,
    create_hotel_tools,
    create_weather_tools,
)


def test_weather():
    """Test weather tools - simple function calls"""
    print("=" * 80)
    print("TEST 1: WEATHER TOOLS")
    print("=" * 80)

    weather = create_weather_tools()

    # Test current weather
    print("\n📍 Current Weather in Bangkok:")
    result = weather.get_current_weather("Bangkok")
    print(result)

    # Test forecast
    print("\n\n📅 7-Day Forecast for Paris:")
    result = weather.get_weather_forecast("Paris, France", days=7)
    print(result)

    print("\n✅ Weather tools working!")


def test_flights():
    """Test flight tools - simple function calls"""
    print("\n\n" + "=" * 80)
    print("TEST 2: FLIGHT TOOLS")
    print("=" * 80)

    flights = create_flight_tools()

    # Test airport search
    print("\n📍 Search airports in Bangkok:")
    result = flights.search_airport_by_city("Bangkok")
    print(result)

    # Test flight search
    print("\n\n✈️ Search flights BKK → SGN:")
    departure = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    result = flights.search_flights(
        origin="BKK",
        destination="SGN",
        departure_date=departure,
        num_adults=1,
        max_results=3,
    )
    print(result)

    print("\n✅ Flight tools working!")


def test_hotels():
    """Test hotel tools - simple function calls"""
    print("\n\n" + "=" * 80)
    print("TEST 3: HOTEL TOOLS")
    print("=" * 80)

    hotels = create_hotel_tools()

    # Test location search
    print("\n📍 Search hotel locations in Bangkok:")
    result = hotels.search_hotel_location("Bangkok")
    print(result)

    # Test hotel search
    print("\n\n🏨 Search hotels in Bangkok:")
    check_in = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    check_out = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d")

    result = hotels.search_hotels(
        location="Bangkok",
        check_in=check_in,
        check_out=check_out,
        adults=2,
        max_results=3,
    )
    print(result)

    print("\n✅ Hotel tools working!")


if __name__ == "__main__":
    print("\n" + "🚀" * 40)
    print("SIMPLE API TOOLS TEST")
    print("🚀" * 40 + "\n")

    try:
        test_weather()
        test_flights()
        test_hotels()

        print("\n\n" + "=" * 80)
        print("🎉 ALL TESTS COMPLETE!")
        print("=" * 80)
        print("\nTools are now integrated into agents:")
        print("  ✅ WeatherAPITools → weather_agent.py")
        print("  ✅ TripAdvisorFlightTools → logistics_agent.py")
        print("  ✅ TripAdvisorHotelTools → accommodation_agent.py")
        print("\n" + "=" * 80 + "\n")

    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
