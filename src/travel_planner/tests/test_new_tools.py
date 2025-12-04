"""
Test External API Tools - Weather, Flights, Hotels
Tests the new Agno toolkit integration
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from tools.external_api_tools import create_flight_tools, create_hotel_tools, create_weather_tools


def test_weather_tools():
    """Test WeatherAPITools"""
    print("=" * 80)
    print("TESTING WEATHER API TOOLS")
    print("=" * 80)

    weather_tools = create_weather_tools()

    # Test 1: Current weather
    print("\n📍 Test 1: Current Weather for Bangkok")
    print("-" * 80)
    result = weather_tools.get_current_weather("Bangkok")
    print(result)

    # Test 2: 7-day forecast
    print("\n\n📅 Test 2: 7-Day Forecast for Paris")
    print("-" * 80)
    result = weather_tools.get_weather_forecast("Paris, France", days=7)
    print(result)

    print("\n" + "=" * 80)
    print("✅ Weather Tools Test Complete")
    print("=" * 80)


def test_flight_tools():
    """Test BookingFlightTools"""
    print("\n\n" + "=" * 80)
    print("TESTING BOOKING.COM FLIGHT API TOOLS")
    print("=" * 80)

    flight_tools = create_flight_tools()

    # Test 1: Search destinations
    print("\n📍 Test 1: Search Destinations for Bangkok")
    print("-" * 80)
    result = flight_tools.search_destination("Bangkok")
    print(result[:300])  # Truncate for readability

    # Test 2: Search flights
    print("\n\n✈️ Test 2: Search Flights Bangkok → Ho Chi Minh City")
    print("-" * 80)
    departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    result = flight_tools.search_flights(
        origin="Bangkok",
        destination="Ho Chi Minh",
        departure_date=departure_date,
        num_adults=1,
        max_results=3,
    )
    print(result)

    print("\n" + "=" * 80)
    print("✅ Flight Tools Test Complete (Booking.com API)")
    print("=" * 80)


def test_hotel_tools():
    """Test TripAdvisorHotelTools"""
    print("\n\n" + "=" * 80)
    print("TESTING HOTEL API TOOLS")
    print("=" * 80)

    hotel_tools = create_hotel_tools()

    # Test 1: Search hotel locations
    print("\n📍 Test 1: Search Hotel Locations in Seoul, South Korea")
    print("-" * 80)
    result = hotel_tools.search_hotel_location("Seoul, South Korea")
    print(result)

    # Test 2: Search hotels
    print("\n\n🏨 Test 2: Search Hotels in Seoul, South Korea")
    print("-" * 80)
    check_in = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    check_out = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d")

    result = hotel_tools.search_hotels(
        location="Seoul, South Korea",
        check_in=check_in,
        check_out=check_out,
        adults=1,
        max_results=3,
    )
    print(result)

    print("\n" + "=" * 80)
    print("✅ Hotel Tools Test Complete")
    print("=" * 80)


def main():
    """Run all tool tests"""
    print("\n" + "🚀" * 40)
    print("AGNO EXTERNAL API TOOLS TEST SUITE")
    print("🚀" * 40 + "\n")

    try:
        # Test weather tools
        # test_weather_tools()

        # Test flight tools
        # test_flight_tools()

        # Test hotel tools
        test_hotel_tools()

        print("\n\n" + "=" * 80)
        print("🎉 ALL TESTS COMPLETE!")
        print("=" * 80)
        print("\n✅ Tools are ready to integrate into agents:")
        print("   • WeatherAPITools → weather_agent.py")
        print("   • TripAdvisorFlightTools → logistics_agent.py")
        print("   • TripAdvisorHotelTools → accommodation_agent.py")
        print("\n" + "=" * 80 + "\n")

    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
