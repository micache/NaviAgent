"""
Simple Tool Call Test - Verify External APIs are working
Không cần chạy agent, chỉ test tools trực tiếp
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from tools.external_api_tools import (
    create_weather_tools,
    create_flight_tools,
    create_hotel_tools,
)


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"🧪 {title}")
    print("=" * 80)


def test_weather_api():
    """Test Weather API Tool"""
    print_section("TEST 1: WEATHER API TOOL")
    
    weather_tools = create_weather_tools()
    
    print("\n📋 Calling: get_weather_forecast('Bangkok', days=7)")
    print("-" * 80)
    
    result = weather_tools.get_weather_forecast("Bangkok", days=7)
    
    print("-" * 80)
    print("\n📊 Result preview:")
    print(result[:500])
    print("...")
    
    # Verify result
    if "Weather Forecast" in result and "Bangkok" in result:
        print("\n✅ PASSED: Weather API hoạt động đúng!")
        print("   → Agent có thể gọi tool này để lấy dữ liệu thời tiết")
    else:
        print("\n❌ FAILED: Weather API không trả về dữ liệu đúng")


def test_flight_api():
    """Test Flight API Tool"""
    print_section("TEST 2: FLIGHT API TOOL (BOOKING.COM)")
    
    flight_tools = create_flight_tools()
    
    departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"\n📋 Calling: search_flights('Bangkok', 'Ho Chi Minh', '{departure_date}')")
    print("-" * 80)
    
    result = flight_tools.search_flights(
        origin="Bangkok",
        destination="Ho Chi Minh",
        departure_date=departure_date,
        num_adults=1,
        max_results=3
    )
    
    print("-" * 80)
    print("\n📊 Result preview:")
    print(result[:800])
    if len(result) > 800:
        print("...")
    
    # Verify result
    if "Flight Search Results" in result and "Bangkok" in result:
        print("\n✅ PASSED: Flight API hoạt động đúng!")
        print("   → Agent có thể gọi tool này để tìm chuyến bay thực")
    else:
        print("\n⚠️  WARNING: Flight API có thể đang dùng fallback")
        print("   → Agent vẫn sẽ hoạt động nhưng dùng web search thay vì API")


def test_hotel_api():
    """Test Hotel API Tool"""
    print_section("TEST 3: HOTEL API TOOL (TRIPADVISOR)")
    
    hotel_tools = create_hotel_tools()
    
    check_in = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    check_out = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d")
    
    print(f"\n📋 Calling: search_hotels('Bangkok', '{check_in}', '{check_out}')")
    print("-" * 80)
    
    result = hotel_tools.search_hotels(
        location="Bangkok",
        check_in=check_in,
        check_out=check_out,
        adults=2,
        max_results=3
    )
    
    print("-" * 80)
    print("\n📊 Result preview:")
    print(result[:800])
    if len(result) > 800:
        print("...")
    
    # Verify result
    if "Hotel Search Results" in result and "Bangkok" in result:
        print("\n✅ PASSED: Hotel API hoạt động đúng!")
        print("   → Agent có thể gọi tool này để tìm khách sạn thực")
    else:
        print("\n❌ FAILED: Hotel API không trả về dữ liệu đúng")


def main():
    """Run all tool tests"""
    print("\n" + "🔧" * 40)
    print("EXTERNAL API TOOLS - DIRECT TEST")
    print("🔧" * 40)
    print("\nMục đích: Kiểm tra tools có hoạt động không")
    print("Các tools này sẽ được agents gọi khi planning travel")
    print("\nChú ý emoji:")
    print("  🌤️  = WeatherAPI đang được gọi")
    print("  ✈️  = Booking.com Flight API đang được gọi")
    print("  🏨 = TripAdvisor Hotel API đang được gọi")
    
    try:
        # Test each tool
        test_weather_api()
        test_flight_api()
        test_hotel_api()
        
        print("\n" + "=" * 80)
        print("🎉 TOOL TESTING COMPLETED!")
        print("=" * 80)
        print("\n📋 Kết luận:")
        print("  • Nếu tất cả PASSED → Agents sẽ sử dụng external APIs")
        print("  • Nếu có WARNING/FAILED → Agents sẽ dùng web search fallback")
        print("  • Agents tự động chọn tool phù hợp dựa trên instructions")
        print("\n💡 Cách kiểm tra khi chạy agent:")
        print("  1. Chạy main.py hoặc test agent")
        print("  2. Xem output có emoji 🌤️ ✈️ 🏨 không")
        print("  3. Nếu có → API đã được gọi")
        print("  4. Nếu không có → Agent đang dùng fallback (search_tools)")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
