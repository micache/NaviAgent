"""
Test Booking.com searchFlights with different parameters
"""

from datetime import datetime, timedelta

import requests

headers = {
    "x-rapidapi-key": "4474c9c793msh3cf72c8184daf74p137175jsn88cdd1fcb2d2",
    "x-rapidapi-host": "booking-com15.p.rapidapi.com",
}

url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

print("=" * 80)
print(f"Testing searchFlights with date: {departure_date}")
print("=" * 80)

# Test 1: Exact parameters from docs
print("\n1. TEST with exact docs params (BOM -> DEL)")
print("-" * 80)
querystring = {
    "fromId": "BOM.AIRPORT",
    "toId": "DEL.AIRPORT",
    "stops": "none",
    "pageNo": "1",
    "adults": "1",
    "children": "0,17",
    "sort": "BEST",
    "cabinClass": "ECONOMY",
    "currency_code": "AED",
}
try:
    response = requests.get(url, headers=headers, params=querystring, timeout=15)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: With departDate
print("\n2. TEST with departDate parameter")
print("-" * 80)
querystring = {
    "fromId": "BOM.AIRPORT",
    "toId": "DEL.AIRPORT",
    "departDate": departure_date,
    "pageNo": "1",
    "adults": "1",
    "sort": "BEST",
    "cabinClass": "ECONOMY",
    "currency_code": "USD",
}
try:
    response = requests.get(url, headers=headers, params=querystring, timeout=15)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Bangkok -> Ho Chi Minh
print("\n3. TEST BKK -> SGN route")
print("-" * 80)
querystring = {
    "fromId": "BKK.AIRPORT",
    "toId": "SGN.AIRPORT",
    "departDate": departure_date,
    "pageNo": "1",
    "adults": "1",
    "sort": "BEST",
    "cabinClass": "ECONOMY",
    "currency_code": "USD",
}
try:
    response = requests.get(url, headers=headers, params=querystring, timeout=15)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Minimal parameters
print("\n4. TEST with minimal params")
print("-" * 80)
querystring = {
    "fromId": "BKK.AIRPORT",
    "toId": "SGN.AIRPORT",
    "departDate": departure_date,
    "adults": "1",
}
try:
    response = requests.get(url, headers=headers, params=querystring, timeout=15)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
