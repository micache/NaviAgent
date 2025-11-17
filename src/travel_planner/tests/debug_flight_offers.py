"""
Debug flightOffers structure
"""
import requests
import json
from datetime import datetime, timedelta

headers = {
    "x-rapidapi-key": "4474c9c793msh3cf72c8184daf74p137175jsn88cdd1fcb2d2",
    "x-rapidapi-host": "booking-com15.p.rapidapi.com"
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
    "pageNo": "1"
}

try:
    response = requests.get(url, headers=headers, params=querystring, timeout=20)
    data = response.json()
    
    if data.get("status"):
        flight_data = data.get("data", {})
        flight_offers = flight_data.get("flightOffers", [])
        
        print(f"Total flightOffers: {len(flight_offers)}")
        
        if flight_offers:
            print("\n" + "=" * 80)
            print("FIRST FLIGHT OFFER STRUCTURE:")
            print("=" * 80)
            print(json.dumps(flight_offers[0], indent=2))
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
