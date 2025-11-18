"""
Test all TripAdvisor Flight API endpoints to find which ones work
"""
import requests
import json
from datetime import datetime, timedelta

headers = {
    "x-rapidapi-key": "4474c9c793msh3cf72c8184daf74p137175jsn88cdd1fcb2d2",
    "x-rapidapi-host": "tripadvisor16.p.rapidapi.com"
}

print("=" * 80)
print("TESTING ALL TRIPADVISOR FLIGHT API ENDPOINTS")
print("=" * 80)

# Test 1: searchAirport (should work)
print("\n1. TEST searchAirport")
print("-" * 80)
url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchAirport"
querystring = {"query": "bangkok"}
try:
    response = requests.get(url, headers=headers, params=querystring, timeout=10)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Result: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: getFilters
print("\n2. TEST getFilters")
print("-" * 80)
url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/getFilters"
querystring = {
    "sourceAirportCode": "BOM",
    "destinationAirportCode": "DEL",
    "itineraryType": "ONE_WAY",
    "classOfService": "ECONOMY"
}
try:
    response = requests.get(url, headers=headers, params=querystring, timeout=10)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Result: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: searchFlights - minimal params
print("\n3. TEST searchFlights (minimal params)")
print("-" * 80)
url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchFlights"
querystring = {
    "sourceAirportCode": "BOM",
    "destinationAirportCode": "DEL",
    "itineraryType": "ONE_WAY",
    "classOfService": "ECONOMY",
    "numAdults": "1",
    "currencyCode": "USD"
}
try:
    response = requests.get(url, headers=headers, params=querystring, timeout=10)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Result: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: searchFlights - with date
print("\n4. TEST searchFlights (with date)")
print("-" * 80)
url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchFlights"
querystring = {
    "sourceAirportCode": "BOM",
    "destinationAirportCode": "DEL",
    "date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
    "itineraryType": "ONE_WAY",
    "classOfService": "ECONOMY",
    "numAdults": "1",
    "currencyCode": "USD"
}
try:
    response = requests.get(url, headers=headers, params=querystring, timeout=10)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Result: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("Check which endpoints returned status: true")
