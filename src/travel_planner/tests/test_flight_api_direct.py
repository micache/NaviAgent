"""
Direct test of TripAdvisor Flight API searchFlights endpoint
"""

import json

import requests

url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchFlights"

from datetime import datetime, timedelta

querystring = {
    "sourceAirportCode": "BOM",
    "destinationAirportCode": "DEL",
    "date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
    "itineraryType": "ONE_WAY",
    "sortOrder": "ML_BEST_VALUE",
    "numAdults": "1",
    "numSeniors": "0",
    "classOfService": "ECONOMY",
    "pageNumber": "1",
    "nearby": "yes",
    "nonstop": "yes",
    "currencyCode": "USD",
    "region": "USA",
}

headers = {
    "x-rapidapi-key": "4474c9c793msh3cf72c8184daf74p137175jsn88cdd1fcb2d2",
    "x-rapidapi-host": "tripadvisor16.p.rapidapi.com",
}

print("Testing TripAdvisor Flight API - searchFlights")
print("=" * 80)
print(f"Route: {querystring['sourceAirportCode']} → {querystring['destinationAirportCode']}")
print(f"URL: {url}")
print(f"Params: {querystring}")
print("=" * 80)

try:
    response = requests.get(url, headers=headers, params=querystring, timeout=15)

    print(f"\nStatus Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print("\nResponse:")
    print("=" * 80)

    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(response.text)

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
