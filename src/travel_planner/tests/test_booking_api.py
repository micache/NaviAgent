"""
Test Booking.com Flight API from RapidAPI
"""
import requests
import json
from datetime import datetime, timedelta

headers = {
    "x-rapidapi-key": "4474c9c793msh3cf72c8184daf74p137175jsn88cdd1fcb2d2",
    "x-rapidapi-host": "booking-com15.p.rapidapi.com"
}

print("=" * 80)
print("TESTING BOOKING.COM FLIGHT API")
print("=" * 80)

# Test 1: searchDestination
print("\n1. TEST searchDestination")
print("-" * 80)
url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchDestination"
querystring = {"query": "bangkok"}
try:
    response = requests.get(url, headers=headers, params=querystring, timeout=10)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Result: {json.dumps(data, indent=2)[:1000]}")
    
    # Extract first destination ID if available
    if data.get("status") and data.get("data"):
        first_dest = data["data"][0]
        bangkok_id = first_dest.get("id")
        print(f"\nFirst destination ID: {bangkok_id}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Search another destination
print("\n2. TEST searchDestination - Ho Chi Minh")
print("-" * 80)
querystring = {"query": "ho chi minh"}
try:
    response = requests.get(url, headers=headers, params=querystring, timeout=10)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Result: {json.dumps(data, indent=2)[:1000]}")
    
    if data.get("status") and data.get("data"):
        first_dest = data["data"][0]
        hcm_id = first_dest.get("id")
        print(f"\nFirst destination ID: {hcm_id}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: searchFlights (example route: BOM -> DEL)
print("\n3. TEST searchFlights (BOM -> DEL)")
print("-" * 80)
url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
querystring = {
    "fromId": "BOM.AIRPORT",
    "toId": "DEL.AIRPORT",
    "departDate": departure_date,
    "pageNo": "1",
    "adults": "1",
    "children": "0",
    "sort": "BEST",
    "cabinClass": "ECONOMY",
    "currency_code": "USD"
}
try:
    response = requests.get(url, headers=headers, params=querystring, timeout=15)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Result: {json.dumps(data, indent=2)[:2000]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETED")
print("=" * 80)
