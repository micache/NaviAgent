"""
Test External APIs - WeatherAPI.com and TripAdvisor via RapidAPI
Run this to verify API connections and data retrieval
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import json

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def test_weatherapi():
    """Test WeatherAPI.com for weather data"""
    print("=" * 80)
    print("TESTING WEATHERAPI.COM")
    print("=" * 80)
    
    api_key = os.getenv("WEATHERAPI_KEY")
    
    if not api_key or api_key == "your_weatherapi_key_here":
        print("❌ WEATHERAPI_KEY not configured in .env file")
        print("\n📝 How to get API key:")
        print("   1. Visit: https://www.weatherapi.com/signup.aspx")
        print("   2. Sign up for FREE account (1,000,000 calls/month)")
        print("   3. Copy your API key")
        print("   4. Add to .env: WEATHERAPI_KEY=your_actual_key")
        return False
    
    print(f"\n✓ API Key found: {api_key[:10]}...")
    
    # Test parameters
    test_location = "Bangkok, Thailand"
    test_days = 7  # Forecast for 7 days
    
    print(f"\n🌤️  Testing Weather Forecast:")
    print(f"   Location: {test_location}")
    print(f"   Forecast days: {test_days}")
    
    try:
        # WeatherAPI.com endpoint
        url = "http://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": api_key,
            "q": test_location,
            "days": test_days,
            "aqi": "no",  # Air quality index (no to save quota)
            "alerts": "yes"  # Weather alerts
        }
        
        print(f"\n📡 Making API request...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ SUCCESS! Weather data retrieved")
            print("-" * 80)
            
            # Current weather
            current = data.get("current", {})
            location = data.get("location", {})
            
            print(f"\n📍 Location:")
            print(f"   Name: {location.get('name')}")
            print(f"   Country: {location.get('country')}")
            print(f"   Timezone: {location.get('tz_id')}")
            print(f"   Local time: {location.get('localtime')}")
            
            print(f"\n🌡️  Current Weather:")
            print(f"   Temperature: {current.get('temp_c')}°C / {current.get('temp_f')}°F")
            print(f"   Feels like: {current.get('feelslike_c')}°C")
            print(f"   Condition: {current.get('condition', {}).get('text')}")
            print(f"   Wind: {current.get('wind_kph')} kph")
            print(f"   Humidity: {current.get('humidity')}%")
            print(f"   UV Index: {current.get('uv')}")
            
            # Forecast
            forecast_days = data.get("forecast", {}).get("forecastday", [])
            
            if forecast_days:
                print(f"\n📅 {len(forecast_days)}-Day Forecast:")
                for day in forecast_days[:3]:  # Show first 3 days
                    date = day.get("date")
                    day_data = day.get("day", {})
                    
                    print(f"\n   📆 {date}:")
                    print(f"      Max: {day_data.get('maxtemp_c')}°C / Min: {day_data.get('mintemp_c')}°C")
                    print(f"      Condition: {day_data.get('condition', {}).get('text')}")
                    print(f"      Rain chance: {day_data.get('daily_chance_of_rain')}%")
                    print(f"      Sunrise: {day.get('astro', {}).get('sunrise')}")
                    print(f"      Sunset: {day.get('astro', {}).get('sunset')}")
            
            # Alerts
            alerts = data.get("alerts", {}).get("alert", [])
            if alerts:
                print(f"\n⚠️  Weather Alerts:")
                for alert in alerts:
                    print(f"   - {alert.get('headline')}")
            else:
                print(f"\n✓ No weather alerts")
            
            print("\n" + "=" * 80)
            print("✅ WeatherAPI.com Test: PASSED")
            print("=" * 80)
            return True
            
        elif response.status_code == 401:
            print(f"\n❌ Authentication Failed (Status {response.status_code})")
            print("   → Check your API key is correct")
            print("   → Make sure you've activated your account")
            return False
        elif response.status_code == 403:
            print(f"\n❌ Access Denied (Status {response.status_code})")
            print("   → Your API key might be invalid or expired")
            return False
        else:
            print(f"\n❌ API Error (Status {response.status_code})")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timeout - API might be slow or down")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tripadvisor_hotels():
    """Test TripAdvisor API via RapidAPI for hotel data"""
    print("\n\n" + "=" * 80)
    print("TESTING TRIPADVISOR - HOTELS")
    print("=" * 80)
    
    api_key = os.getenv("RAPIDAPI_KEY")
    
    if not api_key or api_key == "your_rapidapi_key_here":
        print("❌ RAPIDAPI_KEY not configured in .env file")
        print("\n📝 How to get RapidAPI key:")
        print("   1. Visit: https://rapidapi.com/auth/sign-up")
        print("   2. Sign up for FREE account")
        print("   3. Go to: https://rapidapi.com/apidojo/api/tripadvisor16")
        print("   4. Subscribe to FREE plan (Basic: 500 requests/month)")
        print("   5. Copy your RapidAPI Key from header")
        print("   6. Add to .env: RAPIDAPI_KEY=your_actual_key")
        print("\n💡 Alternative TripAdvisor APIs on RapidAPI:")
        print("   - TripAdvisor (apidojo)")
        print("   - Travel Advisor API")
        print("   - TripAdvisor Content API")
        return False
    
    print(f"\n✓ RapidAPI Key found: {api_key[:15]}...")
    
    # Test parameters - Search for hotels in Bangkok
    test_location = "Bangkok"
    
    print(f"\n🏨 Testing Hotel Search:")
    print(f"   Location: {test_location}")
    print(f"   API: TripAdvisor via RapidAPI")
    
    try:
        # Step 1: Search for location to get locationId
        print(f"\n📡 Step 1: Searching for location...")
        
        search_url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchLocation"
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com"
        }
        
        search_params = {
            "query": test_location
        }
        
        search_response = requests.get(search_url, headers=headers, params=search_params, timeout=15)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            
            print("✓ Location search successful")
            
            # Get first location result
            locations = search_data.get("data", [])
            
            if not locations:
                print("⚠️  No locations found")
                return False
            
            location = locations[0]
            location_id = location.get("geoId")
            location_name = location.get("localizedName", test_location)
            
            print(f"✓ Found location: {location_name} (ID: {location_id})")
            
            # Step 2: Search for hotels in this location
            print(f"\n📡 Step 2: Searching for hotels...")
            
            hotels_url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchHotels"
            
            check_in = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            check_out = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d")
            
            hotels_params = {
                "geoId": location_id,
                "checkIn": check_in,
                "checkOut": check_out,
                "adults": "2",
                "currency": "USD",
                "sortOrder": "POPULARITY"
            }
            
            hotels_response = requests.get(hotels_url, headers=headers, params=hotels_params, timeout=15)
            
            if hotels_response.status_code == 200:
                hotels_data = hotels_response.json()
                
                print("\n✅ SUCCESS! Hotel data retrieved")
                print("-" * 80)
                
                # Parse hotel results
                hotels = hotels_data.get("data", {}).get("data", [])
                
                if hotels:
                    print(f"\n🏨 Found {len(hotels)} hotels:")
                    
                    for i, hotel in enumerate(hotels[:5], 1):  # Show first 5
                        print(f"\n   {i}. {hotel.get('title', 'N/A')}")
                        
                        # Rating
                        rating = hotel.get('bubbleRating', {}).get('rating', 'N/A')
                        review_count = hotel.get('bubbleRating', {}).get('count', 0)
                        print(f"      ⭐ Rating: {rating}/5 ({review_count} reviews)")
                        
                        # Price
                        price_info = hotel.get('priceForDisplay', 'N/A')
                        if price_info and price_info != 'N/A':
                            print(f"      💰 Price: {price_info}")
                        
                        # Location
                        if 'secondaryInfo' in hotel:
                            print(f"      📍 Area: {hotel['secondaryInfo']}")
                        
                        # Provider
                        provider = hotel.get('provider', 'TripAdvisor')
                        print(f"      🏷️  Provider: {provider}")
                        
                        # Hotel ID for details
                        hotel_id = hotel.get('id')
                        if hotel_id:
                            print(f"      🔗 Hotel ID: {hotel_id}")
                    
                    print("\n" + "=" * 80)
                    print("✅ TripAdvisor API Test: PASSED")
                    print("=" * 80)
                    print(f"\n📊 API Usage:")
                    print(f"   ✓ Location search: 1 request")
                    print(f"   ✓ Hotel search: 1 request")
                    print(f"   ✓ Total: 2 requests (out of 500/month free)")
                    
                    return True
                else:
                    print("\n⚠️  No hotels found in response")
                    print(f"   Response keys: {list(hotels_data.keys())}")
                    return False
                    
            elif hotels_response.status_code == 401:
                print(f"\n❌ Authentication Failed (Status {hotels_response.status_code})")
                print("   → Check your RapidAPI key is correct")
                print("   → Make sure you're subscribed to the API")
                return False
            elif hotels_response.status_code == 403:
                print(f"\n❌ Access Denied (Status {hotels_response.status_code})")
                print("   → You might not be subscribed to this API")
                print("   → Go to RapidAPI and subscribe to free plan")
                return False
            elif hotels_response.status_code == 429:
                print(f"\n❌ Rate Limit Exceeded (Status {hotels_response.status_code})")
                print("   → You've exceeded your monthly quota")
                print("   → Free plan: 500 requests/month")
                return False
            else:
                print(f"\n❌ Hotel Search Error (Status {hotels_response.status_code})")
                print(f"   Response: {hotels_response.text[:500]}")
                return False
                
        elif search_response.status_code == 401:
            print(f"\n❌ Authentication Failed (Status {search_response.status_code})")
            print("   → Check your RapidAPI key is correct")
            return False
        elif search_response.status_code == 403:
            print(f"\n❌ Access Denied (Status {search_response.status_code})")
            print("   → Subscribe to TripAdvisor API on RapidAPI")
            print("   → URL: https://rapidapi.com/apidojo/api/tripadvisor16")
            return False
        else:
            print(f"\n❌ Location Search Error (Status {search_response.status_code})")
            print(f"   Response: {search_response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timeout - API might be slow or down")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tripadvisor_flights():
    """Test TripAdvisor API via RapidAPI for flight search"""
    print("\n\n" + "=" * 80)
    print("TESTING TRIPADVISOR - FLIGHTS")
    print("=" * 80)
    
    api_key = os.getenv("RAPIDAPI_KEY")
    
    if not api_key or api_key == "your_rapidapi_key_here":
        print("❌ RAPIDAPI_KEY not configured")
        return False
    
    print(f"\n✓ RapidAPI Key found: {api_key[:15]}...")
    
    # Test parameters - Popular route with more flights
    origin = "BOM"  # Mumbai
    destination = "DEL"  # Delhi
    departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"\n✈️  Testing Flight Search:")
    print(f"   From: {origin}")
    print(f"   To: {destination}")
    print(f"   Date: {departure_date}")
    
    try:
        # TripAdvisor Flight Search - Correct format from RapidAPI docs
        url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchFlights"
        
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "tripadvisor16.p.rapidapi.com"
        }
        
        params = {
            "sourceAirportCode": origin,
            "destinationAirportCode": destination,
            "itineraryType": "ONE_WAY",
            "sortOrder": "ML_BEST_VALUE",
            "numAdults": "1",
            "numSeniors": "0",
            "classOfService": "ECONOMY",
            "pageNumber": "1",
            "nearby": "yes",
            "nonstop": "yes",
            "currencyCode": "USD",
            "region": "USA"
        }
        
        print(f"\n📡 Searching for flights...")
        response = requests.get(url, headers=headers, params=params, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ SUCCESS! Flight data retrieved")
            print("-" * 80)
            
            flights = data.get("data", {}).get("flights", [])
            
            if flights:
                print(f"\n✈️  Found {len(flights)} flights:")
                
                for i, flight in enumerate(flights[:5], 1):
                    segments = flight.get("segments", [])
                    
                    if segments:
                        segment = segments[0]
                        legs = segment.get("legs", [])
                        
                        if legs:
                            leg = legs[0]
                            print(f"\n   {i}. Flight Option:")
                            print(f"      🛫 Departure: {leg.get('departureDateTime', 'N/A')}")
                            print(f"      🛬 Arrival: {leg.get('arrivalDateTime', 'N/A')}")
                            print(f"      ⏱️  Duration: {leg.get('durationMinutes', 'N/A')} minutes")
                            print(f"      ✈️  Airline: {leg.get('marketingCarrier', {}).get('displayName', 'N/A')}")
                            print(f"      🔢 Flight #: {leg.get('flightNumber', 'N/A')}")
                    
                    # Price
                    price_info = flight.get("purchaseLinks", [])
                    if price_info:
                        price = price_info[0].get("totalPrice", "N/A")
                        currency = price_info[0].get("currency", "USD")
                        provider = price_info[0].get("partner", {}).get("displayName", "N/A")
                        print(f"      💰 Price: {price} {currency}")
                        print(f"      🏷️  Provider: {provider}")
                
                print("\n" + "=" * 80)
                print("✅ TripAdvisor Flights Test: PASSED")
                print("=" * 80)
                return True
            else:
                print("\n⚠️  No flights found")
                return False
                
        elif response.status_code == 401:
            print(f"\n❌ Authentication Failed (Status {response.status_code})")
            return False
        elif response.status_code == 403:
            print(f"\n❌ Access Denied - Subscribe to API on RapidAPI")
            return False
        elif response.status_code == 429:
            print(f"\n❌ Rate Limit Exceeded")
            return False
        else:
            print(f"\n❌ API Error (Status {response.status_code})")
            print(f"   Response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tripadvisor_restaurants():
    """Test TripAdvisor API via RapidAPI for restaurant search"""
    print("\n\n" + "=" * 80)
    print("TESTING TRIPADVISOR - RESTAURANTS")
    print("=" * 80)
    
    api_key = os.getenv("RAPIDAPI_KEY")
    
    if not api_key or api_key == "your_rapidapi_key_here":
        print("❌ RAPIDAPI_KEY not configured")
        return False
    
    print(f"\n✓ RapidAPI Key found: {api_key[:15]}...")
    
    test_location = "Bangkok"
    
    print(f"\n🍽️  Testing Restaurant Search:")
    print(f"   Location: {test_location}")
    
    try:
        # Step 1: Search for location
        print(f"\n📡 Step 1: Searching for location...")
        
        search_url = "https://tripadvisor16.p.rapidapi.com/api/v1/restaurant/searchLocation"
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com"
        }
        
        search_params = {"query": test_location}
        search_response = requests.get(search_url, headers=headers, params=search_params, timeout=15)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            locations = search_data.get("data", [])
            
            if not locations:
                print("⚠️  No locations found")
                return False
            
            location = locations[0]
            location_id = location.get("locationId")
            location_name = location.get("localizedName", test_location)
            
            print(f"✓ Found location: {location_name} (ID: {location_id})")
            
            # Step 2: Search for restaurants
            print(f"\n📡 Step 2: Searching for restaurants...")
            
            restaurants_url = "https://tripadvisor16.p.rapidapi.com/api/v1/restaurant/searchRestaurants"
            
            restaurants_params = {
                "locationId": location_id
            }
            
            restaurants_response = requests.get(restaurants_url, headers=headers, params=restaurants_params, timeout=15)
            
            if restaurants_response.status_code == 200:
                restaurants_data = restaurants_response.json()
                
                print("\n✅ SUCCESS! Restaurant data retrieved")
                print("-" * 80)
                
                restaurants = restaurants_data.get("data", {}).get("data", [])
                
                if restaurants:
                    print(f"\n🍽️  Found {len(restaurants)} restaurants:")
                    
                    for i, restaurant in enumerate(restaurants[:5], 1):
                        print(f"\n   {i}. {restaurant.get('name', 'N/A')}")
                        
                        # Rating
                        rating = restaurant.get('averageRating', 'N/A')
                        review_count = restaurant.get('userReviewCount', 0)
                        print(f"      ⭐ Rating: {rating}/5 ({review_count} reviews)")
                        
                        # Cuisine
                        cuisine = restaurant.get('establishmentTypeAndCuisineTags', [])
                        if cuisine:
                            cuisine_names = [c for c in cuisine[:3]]
                            print(f"      🍴 Cuisine: {', '.join(cuisine_names)}")
                        
                        # Price range
                        price_tag = restaurant.get('priceTag', 'N/A')
                        if price_tag and price_tag != 'N/A':
                            print(f"      💰 Price: {price_tag}")
                        
                        # Location
                        if 'primaryInfo' in restaurant:
                            print(f"      📍 Info: {restaurant['primaryInfo']}")
                    
                    print("\n" + "=" * 80)
                    print("✅ TripAdvisor Restaurants Test: PASSED")
                    print("=" * 80)
                    return True
                else:
                    print("\n⚠️  No restaurants found")
                    return False
            else:
                print(f"\n❌ Restaurant Search Error (Status {restaurants_response.status_code})")
                return False
        else:
            print(f"\n❌ Location Search Error (Status {search_response.status_code})")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_booking_vacation_rentals():
    """Test TripAdvisor API via RapidAPI for vacation rentals"""
    print("\n\n" + "=" * 80)
    print("TESTING TRIPADVISOR - VACATION RENTALS")
    print("=" * 80)
    
    api_key = os.getenv("RAPIDAPI_KEY")
    
    if not api_key or api_key == "your_rapidapi_key_here":
        print("❌ RAPIDAPI_KEY not configured")
        return False
    
    print(f"\n✓ RapidAPI Key found: {api_key[:15]}...")
    
    print(f"\n🏠 Testing Vacation Rentals Search:")
    print(f"   API: TripAdvisor Rentals via RapidAPI")
    
    try:
        # TripAdvisor Rentals Search - Correct format from RapidAPI docs
        url = "https://tripadvisor16.p.rapidapi.com/api/v1/rentals/rentalSearch"
        
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "tripadvisor16.p.rapidapi.com"
        }
        
        params = {
            "sortOrder": "POPULARITY",
            "page": "1",
            "currencyCode": "USD"
        }
        
        print(f"\n📡 Searching for vacation rentals...")
        response = requests.get(url, headers=headers, params=params, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ SUCCESS! Vacation rental data retrieved")
            print("-" * 80)
            
            rentals = data.get("data", {}).get("data", [])
            
            if rentals:
                print(f"\n🏠 Found {len(rentals)} vacation rentals:")
                
                for i, rental in enumerate(rentals[:5], 1):
                    print(f"\n   {i}. {rental.get('title', 'N/A')}")
                    
                    # Rating
                    rating = rental.get('bubbleRating', {}).get('rating', 'N/A')
                    review_count = rental.get('bubbleRating', {}).get('count', 0)
                    if rating != 'N/A':
                        print(f"      ⭐ Rating: {rating}/5 ({review_count} reviews)")
                    
                    # Price
                    price_info = rental.get('priceForDisplay', 'N/A')
                    if price_info and price_info != 'N/A':
                        print(f"      💰 Price: {price_info}")
                    
                    # Location
                    if 'secondaryInfo' in rental:
                        print(f"      📍 Location: {rental['secondaryInfo']}")
                    
                    # Property details
                    if 'badge' in rental:
                        print(f"      🏷️  Type: {rental['badge']}")
                    
                    # Rental ID
                    rental_id = rental.get('id')
                    if rental_id:
                        print(f"      🔗 Rental ID: {rental_id}")
                
                print("\n" + "=" * 80)
                print("✅ TripAdvisor Vacation Rentals Test: PASSED")
                print("=" * 80)
                return True
            else:
                print("\n⚠️  No vacation rentals found")
                print(f"   Response keys: {list(data.keys())}")
                return False
        elif response.status_code == 401:
            print(f"\n❌ Authentication Failed (Status {response.status_code})")
            return False
        elif response.status_code == 403:
            print(f"\n❌ Access Denied - Subscribe to API on RapidAPI")
            return False
        elif response.status_code == 429:
            print(f"\n❌ Rate Limit Exceeded")
            return False
        else:
            print(f"\n❌ API Error (Status {response.status_code})")
            print(f"   Response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rentalcars_api():
    """Test Booking.com Car Rentals API via RapidAPI"""
    print("\n\n" + "=" * 80)
    print("TESTING BOOKING.COM - RENTAL CARS")
    print("=" * 80)
    
    api_key = os.getenv("RAPIDAPI_KEY")
    
    if not api_key or api_key == "your_rapidapi_key_here":
        print("❌ RAPIDAPI_KEY not configured")
        return False
    
    print(f"\n✓ RapidAPI Key found: {api_key[:15]}...")
    
    test_location = "Bangkok"
    
    print(f"\n🚗 Testing Rental Cars Search:")
    print(f"   Location: {test_location}")
    print(f"   API: Booking.com Car Rentals via RapidAPI")
    
    try:
        # Search for car rental locations
        print(f"\n📡 Searching for car rental locations...")
        
        search_url = "https://booking-com.p.rapidapi.com/v1/car-rental/locations"
        
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "booking-com.p.rapidapi.com"
        }
        
        search_params = {
            "name": test_location,
            "locale": "en-gb"
        }
        
        search_response = requests.get(search_url, headers=headers, params=search_params, timeout=15)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            
            if not search_data:
                print("⚠️  No car rental locations found")
                return False
            
            location = search_data[0]
            location_id = location.get("city_ufi")
            location_name = location.get("city_name", test_location)
            
            print(f"✓ Found location: {location_name} (ID: {location_id})")
            
            # Search for rental cars
            print(f"\n📡 Searching for rental cars...")
            
            cars_url = "https://booking-com.p.rapidapi.com/v1/car-rental/search"
            
            pickup_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            pickup_time = "10:00"
            dropoff_date = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d")
            dropoff_time = "10:00"
            
            cars_params = {
                "pick_up_location_id": location_id,
                "drop_off_location_id": location_id,
                "pick_up_datetime": f"{pickup_date} {pickup_time}",
                "drop_off_datetime": f"{dropoff_date} {dropoff_time}",
                "driver_age": "30",
                "locale": "en-gb",
                "currency": "USD"
            }
            
            cars_response = requests.get(cars_url, headers=headers, params=cars_params, timeout=20)
            
            if cars_response.status_code == 200:
                cars_data = cars_response.json()
                
                print("\n✅ SUCCESS! Rental car data retrieved")
                print("-" * 80)
                
                cars = cars_data.get("search_results", [])
                
                if cars:
                    print(f"\n🚗 Found {len(cars)} rental cars:")
                    
                    for i, car in enumerate(cars[:5], 1):
                        vehicle = car.get("vehicle_info", {})
                        
                        print(f"\n   {i}. {vehicle.get('v_name', 'N/A')}")
                        
                        # Car details
                        category = vehicle.get("category", "N/A")
                        transmission = vehicle.get("transmission", "N/A")
                        fuel = vehicle.get("fuel_type", "N/A")
                        
                        print(f"      🚗 Category: {category}")
                        print(f"      ⚙️  Transmission: {transmission}")
                        print(f"      ⛽ Fuel: {fuel}")
                        
                        # Capacity
                        passengers = vehicle.get("passangers", "N/A")
                        bags = vehicle.get("bags_fit", "N/A")
                        print(f"      👥 Passengers: {passengers}")
                        print(f"      🧳 Bags: {bags}")
                        
                        # Price
                        price_info = car.get("price", {})
                        price = price_info.get("amount", "N/A")
                        currency = price_info.get("currency", "USD")
                        print(f"      💰 Price: {price} {currency}")
                        
                        # Provider
                        provider = car.get("provider_name", "N/A")
                        print(f"      🏷️  Provider: {provider}")
                    
                    print("\n" + "=" * 80)
                    print("✅ Rental Cars Test: PASSED")
                    print("=" * 80)
                    return True
                else:
                    print("\n⚠️  No rental cars found")
                    return False
            else:
                print(f"\n❌ Car Search Error (Status {cars_response.status_code})")
                print(f"   Response: {cars_response.text[:300]}")
                return False
        else:
            print(f"\n❌ Location Search Error (Status {search_response.status_code})")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all API tests"""
    print("\n" + "🚀" * 40)
    print("EXTERNAL API INTEGRATION TESTS")
    print("🚀" * 40 + "\n")
    
    results = {}
    
    # Test WeatherAPI.com
    #results['weather'] = test_weatherapi()
    
    # Test TripAdvisor APIs via RapidAPI
    #results['hotels'] = test_tripadvisor_hotels()
    results['flights'] = test_tripadvisor_flights()
    #results['restaurants'] = test_tripadvisor_restaurants()
    
    # Test Booking.com APIs via RapidAPI
    # results['vacation_rentals'] = test_booking_vacation_rentals()
    #results['rental_cars'] = test_rentalcars_api()
    
    # Summary
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for api_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {api_name.upper()}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All API tests passed! Ready to integrate.")
    else:
        print("\n⚠️  Some tests failed. Check API keys and documentation.")
    
    print("=" * 80 + "\n")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
