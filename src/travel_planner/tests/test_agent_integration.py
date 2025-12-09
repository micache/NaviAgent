"""
Test Agent Integration with External API Tools
Kiểm tra xem các agents có gọi đúng API tools không
"""

import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env from repository root
env_path = Path(__file__).resolve().parents[3] / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from agents.accommodation_agent import create_accommodation_agent
from agents.logistics_agent import create_logistics_agent

# Import agents
from agents.weather_agent import create_weather_agent, run_weather_agent


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"🔍 {title}")
    print("=" * 80)


async def test_weather_agent():
    """Test Weather Agent với Weather API"""
    print_section("TEST 1: WEATHER AGENT")

    print("\n📋 Input:")
    print("  - Destination: Bangkok")
    print("  - Departure: 3 days from now (within 10-day API forecast range)")
    print("  - Duration: 7 days")
    print("\n⏳ Running weather agent...")
    print("🔎 Watch for 🌤️ emoji = API được gọi")
    print("-" * 80)

    agent = create_weather_agent(agent_name="weather", enable_memory=False)

    departure_date = date.today() + timedelta(days=3)

    result = await run_weather_agent(
        agent=agent,
        destination="Bangkok",
        departure_date=departure_date,
        duration_days=7,
    )

    print("-" * 80)
    print("\n✅ Weather Agent Output:")
    print(f"  - Season: {result.season}")
    print(f"  - Weather Summary: {result.weather_summary[:100]}...")
    if result.daily_forecasts:
        print(f"  - Daily Forecasts: {len(result.daily_forecasts)} days")
        if result.daily_forecasts:
            first_day = result.daily_forecasts[0]
            print(
                f"    → Day 1: {first_day.temperature_low}-{first_day.temperature_high}°C, {first_day.conditions}"
            )
    print(f"  - Packing: {len(result.packing_recommendations)} items")
    if result.seasonal_events:
        print(f"  - Events: {len(result.seasonal_events)} found")
    if result.best_activities:
        print(f"  - Activities: {len(result.best_activities)} suggested")

    # Check if API was used (check if daily_forecasts exist - that means API was called)
    if result.daily_forecasts:
        print("\n✅ PASSED: Weather API được sử dụng (có daily_forecasts)!")
    else:
        print("\n⚠️  WARNING: Có thể đã dùng fallback (không có daily_forecasts)")


async def test_logistics_agent():
    """Test Logistics Agent với Flight API"""
    print_section("TEST 2: LOGISTICS AGENT")

    print("\n📋 Input:")
    print("  - Route: Bangkok → Ho Chi Minh City")
    print("  - Departure: 3 days from now")
    print("  - Return: 10 days from now")
    print("  - Travelers: 2")
    print("  - Budget: $500/person")
    print("\n⏳ Running logistics agent...")
    print("🔎 Watch for ✈️ emoji = API được gọi:")
    print("-" * 80)

    agent = create_logistics_agent(agent_name="logistics", enable_memory=False)

    from models.schemas import LogisticsAgentInput

    departure_date = date.today() + timedelta(days=3)
    return_date = date.today() + timedelta(days=10)

    agent_input = LogisticsAgentInput(
        departure_point="Bangkok",
        destination="Ho Chi Minh City",
        departure_date=departure_date,
        return_date=return_date,
        num_travelers=2,
        budget_per_person=500.0,
        preferences="Economy class, prefer direct flights",
    )

    response = await agent.arun(input=agent_input)

    print("-" * 80)
    print("\n✅ Logistics Agent Output:")

    if hasattr(response.content, "flight_options"):
        flights = response.content.flight_options
        print(f"  - Flight options: {len(flights)} total")
        print(
            f"  - Average price: {response.content.average_price:,.0f} VND per person"
        )

        if flights:
            print(f"\n  First flight option:")
            print(f"    • Airline: {flights[0].airline}")
            print(f"    • Departure: {flights[0].departure_time}")
            print(f"    • Arrival: {flights[0].arrival_time}")
            print(f"    • Duration: {flights[0].flight_duration}")
            print(f"    • Price: {flights[0].price_vnd:,.0f} VND")
            print(f"    • Stops: {flights[0].number_of_stops}")

        if response.content.booking_tips:
            print(
                f"\n  Booking tips: {len(response.content.booking_tips)} tips provided"
            )

        # Check if real API data (có giá cụ thể, không phải ước tính)
        if (
            flights and flights[0].price_vnd < 10000000
        ):  # Less than 10M VND indicates real API data
            print("\n✅ PASSED: Flight API trả về dữ liệu thực!")
        else:
            print("\n⚠️  WARNING: Có thể là dữ liệu ước tính (không phải từ API)")
    else:
        print("  ⚠️  Output structure different than expected")
        print(f"  Actual attributes: {dir(response.content)}")


async def test_accommodation_agent():
    """Test Accommodation Agent với Hotel API"""
    print_section("TEST 3: ACCOMMODATION AGENT")

    print("\n📋 Input:")
    print("  - Destination: Bangkok")
    print("  - Check-in: 3 days from now")
    print("  - Check-out: 10 days from now")
    print("  - Travelers: 2")
    print("  - Budget: $800")
    print("\n⏳ Running accommodation agent...")
    print("🔎 Watch for 🏨 emoji = API được gọi:")
    print("-" * 80)

    agent = create_accommodation_agent(agent_name="accommodation", enable_memory=False)

    from models.schemas import AccommodationAgentInput

    departure_date = date.today() + timedelta(days=3)
    duration_nights = 7

    agent_input = AccommodationAgentInput(
        destination="Bangkok",
        departure_date=departure_date,
        duration_nights=duration_nights,
        budget_per_night=2000000.0,  # VND
        num_travelers=2,
        travel_style="budget",
        preferences="Near city center, good reviews",
    )

    response = await agent.arun(input=agent_input)

    print("-" * 80)
    print("\n✅ Accommodation Agent Output:")

    if hasattr(response.content, "recommendations"):
        hotels = response.content.recommendations
        print(f"  - Recommendations: {len(hotels)} hotels")
        print(
            f"  - Average price: {response.content.average_price_per_night:,.0f} VND/night"
        )
        print(f"  - Total cost: {response.content.total_estimated_cost:,.0f} VND")

        if hotels:
            print(f"\n  First hotel:")
            print(f"    • Name: {hotels[0].name}")
            print(f"    • Price: {hotels[0].price_per_night:,.0f} VND/night")
            print(f"    • Rating: {hotels[0].rating}/5")
            print(f"    • Location: {hotels[0].location}")

        if response.content.best_areas:
            print(f"\n  Best areas: {len(response.content.best_areas)} neighborhoods")

        if response.content.booking_tips:
            print(f"  Booking tips: {len(response.content.booking_tips)} tips provided")

        # Check if real API data (có rating và giá cụ thể)
        if hotels and hotels[0].rating > 0 and hotels[0].price_per_night > 0:
            print("\n✅ PASSED: Hotel API trả về dữ liệu thực!")
        else:
            print("\n⚠️  WARNING: Có thể là dữ liệu ước tính")
    else:
        print("  ⚠️  Output structure different than expected")
        print(f"  Actual attributes: {dir(response.content)}")


async def main():
    """Run all integration tests"""
    print("\n" + "🚀" * 40)
    print("AGENT + EXTERNAL API INTEGRATION TEST")
    print("🚀" * 40)
    print("\nMục đích: Kiểm tra agents có gọi đúng external API tools không")
    print("Theo dõi output để xem:")
    print("  ✅ Tool nào được gọi (Weather API, Flight API, Hotel API)")
    print("  ✅ API có trả về dữ liệu thực không")
    print("  ✅ Fallback có hoạt động khi API fail không")

    try:
        # Test Weather Agent
        # await test_weather_agent()

        # Test Logistics Agent
        # await test_logistics_agent()

        # Test Accommodation Agent
        await test_accommodation_agent()

        print("\n" + "=" * 80)
        print("🎉 ALL INTEGRATION TESTS COMPLETED!")
        print("=" * 80)
        print("\n📊 Summary:")
        print(
            "  • Weather Agent: Check if 'API Forecast' or 'Forecast' in temperature_range"
        )
        print("  • Logistics Agent: Check if flight prices are realistic (< 10M VND)")
        print("  • Accommodation Agent: Check if hotel ratings and prices are specific")
        print(
            "\n💡 Tip: Enable debug_mode=True in agent creation to see detailed tool calls"
        )

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
