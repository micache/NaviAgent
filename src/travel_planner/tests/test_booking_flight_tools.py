"""
Test Booking.com Flight Tools integration
"""

import os
import sys

from dotenv import load_dotenv
from pathlib import Path

# Load .env from repository root
env_path = Path(__file__).resolve().parents[3] / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from tools.external_api_tools import create_flight_tools

print("=" * 80)
print("TESTING BOOKING.COM FLIGHT TOOLS")
print("=" * 80)

# Create flight tools instance
flight_tools = create_flight_tools()

# Test 1: Search destinations
print("\n1. TEST search_destination - Bangkok")
print("-" * 80)
result = flight_tools.search_destination("bangkok")
print(result)

# Test 2: Search destinations - Ho Chi Minh
print("\n2. TEST search_destination - Ho Chi Minh")
print("-" * 80)
result = flight_tools.search_destination("ho chi minh")
print(result)

# Test 3: Search flights BKK -> SGN
print("\n3. TEST search_flights - Bangkok to Ho Chi Minh")
print("-" * 80)
departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
result = flight_tools.search_flights(
    origin="Bangkok",
    destination="Ho Chi Minh",
    departure_date=departure_date,
    num_adults=1,
    max_results=5,
)
print(result)

# Test 4: Search flights with airport codes
print("\n4. TEST search_flights - BKK to SGN (with codes)")
print("-" * 80)
result = flight_tools.search_flights(
    origin="BKK",
    destination="SGN",
    departure_date=departure_date,
    num_adults=2,
    cabin_class="ECONOMY",
    max_results=3,
)
print(result)

print("\n" + "=" * 80)
print("TESTING COMPLETED")
print("=" * 80)
