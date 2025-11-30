"""
Debug Booking.com Flight API response structure
"""

import json
from datetime import datetime, timedelta

import requests

headers = {
    "x-rapidapi-key": "4474c9c793msh3cf72c8184daf74p137175jsn88cdd1fcb2d2",
    "x-rapidapi-host": "booking-com15.p.rapidapi.com",
}

url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

querystring = {
    "fromId": "BKK.AIRPORT",
    "toId": "SGN.AIRPORT",
    "departDate": departure_date,
    "adults": "1",
    "cabinClass": "ECONOMY",
    "sort": "BEST",
    "currency_code": "USD",
    "pageNo": "1",
}

print(f"Testing with date: {departure_date}")
print(f"Params: {querystring}")
print("=" * 80)

try:
    response = requests.get(url, headers=headers, params=querystring, timeout=20)
    print(f"Status: {response.status_code}\n")

    data = response.json()
    print("Full Response Structure:")
    print(json.dumps(data, indent=2)[:5000])

    # Check nested structure
    if data.get("status"):
        print("\n" + "=" * 80)
        print("SUCCESS! Analyzing structure...")
        print("=" * 80)

        flight_data = data.get("data", {})
        print(f"\nTop-level data keys: {list(flight_data.keys())}")

        if "flights" in flight_data:
            flights = flight_data["flights"]
            print(f"\nTotal flights: {len(flights)}")

            if flights:
                print(f"\nFirst flight structure:")
                print(json.dumps(flights[0], indent=2)[:2000])

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
