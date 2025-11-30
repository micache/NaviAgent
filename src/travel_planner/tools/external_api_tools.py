"""
External API Tools - Weather, Flights, Hotels
Provides real-time data from WeatherAPI.com and TripAdvisor via RapidAPI
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from agno.tools import Toolkit

logger = logging.getLogger(__name__)


class WeatherAPITools(Toolkit):
    """
    Weather data toolkit using WeatherAPI.com
    Free tier: 1,000,000 calls/month
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize Weather API toolkit.

        Args:
            api_key: WeatherAPI.com API key (defaults to WEATHERAPI_KEY env var)
        """
        self.api_key = api_key or os.getenv("WEATHERAPI_KEY")
        self.base_url = "http://api.weatherapi.com/v1"

        super().__init__(name="weather_api_tools", **kwargs)

        # Register tools after parent init
        self.register(self.get_weather_forecast)
        self.register(self.get_current_weather)

    def get_weather_forecast(
        self, location: str, days: int = 7, include_alerts: bool = True
    ) -> str:
        """
        Get weather forecast for a destination.

        Args:
            location: City name or coordinates (e.g., "Bangkok", "Paris, France", "48.8566,2.3522")
            days: Number of forecast days (1-10, default: 7)
            include_alerts: Include weather alerts if available

        Returns:
            str: Formatted weather forecast in Vietnamese with all details
        """
        if not self.api_key:
            return "❌ WEATHERAPI_KEY không được cấu hình trong .env file"

        try:
            url = f"{self.base_url}/forecast.json"

            params = {
                "key": self.api_key,
                "q": location,
                "days": min(days, 10),  # Max 10 days
                "aqi": "no",  # Skip air quality to save quota
                "alerts": "yes" if include_alerts else "no",
            }

            print(f"🌤️  [WeatherAPI] Calling get_weather_forecast for '{location}', {days} days")
            logger.info(f"Fetching weather forecast for {location}, {days} days")
            response = requests.get(url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ [WeatherAPI] Successfully fetched forecast for '{location}'")
                return self._format_forecast_vietnamese(data)
            elif response.status_code == 401:
                print(f"❌ [WeatherAPI] Authentication error")
                return "❌ Lỗi xác thực WeatherAPI - Kiểm tra API key"
            elif response.status_code == 400:
                print(f"❌ [WeatherAPI] Location not found: {location}")
                return f"❌ Không tìm thấy địa điểm: {location}"
            else:
                print(f"❌ [WeatherAPI] Error {response.status_code}")
                logger.error(f"WeatherAPI error: {response.status_code} - {response.text[:200]}")
                return f"❌ Lỗi lấy dữ liệu thời tiết (Status {response.status_code})"

        except requests.exceptions.Timeout:
            logger.error(f"WeatherAPI timeout for {location}")
            return "❌ Timeout khi gọi WeatherAPI - vui lòng thử lại"
        except Exception as e:
            logger.error(f"WeatherAPI exception: {e}")
            return f"❌ Lỗi không xác định: {str(e)}"

    def get_current_weather(self, location: str) -> str:
        """
        Get current weather for a destination.

        Args:
            location: City name or coordinates

        Returns:
            str: Current weather in Vietnamese
        """
        if not self.api_key:
            return "❌ WEATHERAPI_KEY không được cấu hình trong .env file"

        try:
            url = f"{self.base_url}/current.json"

            params = {"key": self.api_key, "q": location, "aqi": "no"}

            logger.info(f"Fetching current weather for {location}")
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return self._format_current_weather_vietnamese(data)
            elif response.status_code == 401:
                return "❌ Lỗi xác thực WeatherAPI"
            elif response.status_code == 400:
                return f"❌ Không tìm thấy địa điểm: {location}"
            else:
                return f"❌ Lỗi lấy dữ liệu thời tiết (Status {response.status_code})"

        except Exception as e:
            logger.error(f"Current weather error: {e}")
            return f"❌ Lỗi: {str(e)}"

    def _format_forecast_vietnamese(self, data: Dict) -> str:
        """Format forecast data in English for agents to process"""
        location = data.get("location", {})
        current = data.get("current", {})
        forecast_days = data.get("forecast", {}).get("forecastday", [])

        result = f"""Weather Forecast - {location.get('name')}, {location.get('country')}

Location:
- Timezone: {location.get('tz_id')}
- Local time: {location.get('localtime')}

Current Weather:
- Temperature: {current.get('temp_c')}°C (feels like {current.get('feelslike_c')}°C)
- Condition: {current.get('condition', {}).get('text')}
- Humidity: {current.get('humidity')}%
- Wind: {current.get('wind_kph')} km/h
- UV Index: {current.get('uv')}

{len(forecast_days)}-Day Forecast:
"""

        for day in forecast_days:
            date = day.get("date")
            day_data = day.get("day", {})
            astro = day.get("astro", {})

            result += f"""
Date: {date}
- Temperature: {day_data.get('mintemp_c')}°C - {day_data.get('maxtemp_c')}°C
- Condition: {day_data.get('condition', {}).get('text')}
- Rain chance: {day_data.get('daily_chance_of_rain')}%
- Sunrise: {astro.get('sunrise')} | Sunset: {astro.get('sunset')}
- UV Index: {day_data.get('uv')}
"""

        # Add weather alerts if any
        alerts = data.get("alerts", {}).get("alert", [])
        if alerts:
            result += "\nWeather Alerts:\n"
            for alert in alerts:
                result += f"- {alert.get('headline')}\n"

        return result

    def _format_current_weather_vietnamese(self, data: Dict) -> str:
        """Format current weather in English for agents to process"""
        location = data.get("location", {})
        current = data.get("current", {})

        return f"""Current Weather - {location.get('name')}, {location.get('country')}

Temperature: {current.get('temp_c')}°C (feels like {current.get('feelslike_c')}°C)
Condition: {current.get('condition', {}).get('text')}
Humidity: {current.get('humidity')}%
Wind: {current.get('wind_kph')} km/h
UV Index: {current.get('uv')}
Last updated: {current.get('last_updated')}
"""


class BookingFlightTools(Toolkit):
    """
    Flight search toolkit using Booking.com API via RapidAPI
    Free tier: 500 requests/month
    More reliable than TripAdvisor API - actually returns real flight data!
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize Booking.com Flight API toolkit.

        Args:
            api_key: RapidAPI key (defaults to RAPIDAPI_KEY env var)
        """
        self.api_key = api_key or os.getenv("RAPIDAPI_KEY")
        self.base_url = "https://booking-com15.p.rapidapi.com/api/v1/flights"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "booking-com15.p.rapidapi.com",
        }

        super().__init__(name="booking_flight_tools", **kwargs)

        # Register tools after parent init
        self.register(self.search_flights)
        self.register(self.search_destination)

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        num_adults: int = 1,
        cabin_class: str = "ECONOMY",
        max_results: int = 10,
        sort_order: str = "BEST",
    ) -> str:
        """
        Search for flights using Booking.com API.

        Args:
            origin: Origin city name or airport code (e.g., "Bangkok", "BKK")
            destination: Destination city name or airport code (e.g., "Ho Chi Minh", "SGN")
            departure_date: Departure date in YYYY-MM-DD format
            num_adults: Number of adult passengers (default: 1)
            cabin_class: ECONOMY, PREMIUM_ECONOMY, BUSINESS, or FIRST (default: ECONOMY)
            max_results: Maximum number of results to return (default: 10)
            sort_order: BEST, CHEAPEST, or FASTEST (default: BEST)

        Returns:
            str: Flight search results in English
        """
        if not self.api_key:
            return "❌ RAPIDAPI_KEY not configured in .env file"

        try:
            # Step 1: Get origin and destination IDs
            origin_id = self._get_destination_id(origin)
            if not origin_id:
                return (
                    f"❌ Cannot find airport/city: {origin}. Try with airport code (e.g., BKK, SGN)"
                )

            dest_id = self._get_destination_id(destination)
            if not dest_id:
                return f"❌ Cannot find airport/city: {destination}. Try with airport code (e.g., JFK, LAX)"

            # Step 2: Search flights
            url = f"{self.base_url}/searchFlights"

            params = {
                "fromId": origin_id,
                "toId": dest_id,
                "departDate": departure_date,
                "adults": str(num_adults),
                "cabinClass": cabin_class.upper(),
                "sort": sort_order.upper(),
                "currency_code": "USD",
                "pageNo": "1",
            }

            print(
                f"✈️  [Booking.com] Searching flights: {origin} ({origin_id}) → {destination} ({dest_id}) on {departure_date}"
            )
            logger.info(
                f"Searching flights: {origin} ({origin_id}) → {destination} ({dest_id}) on {departure_date}"
            )
            response = requests.get(url, headers=self.headers, params=params, timeout=25)

            if response.status_code == 200:
                data = response.json()

                # Check if API returned success
                if data.get("status") == True:
                    flight_count = len(data.get("data", {}).get("flightOffers", []))
                    print(
                        f"✅ [Booking.com] Found {flight_count} flights for {origin} → {destination}"
                    )
                    return self._format_flights_english(data, origin, destination, max_results)
                else:
                    # API returned error
                    error_msg = data.get("message", "Unknown error")
                    print(f"❌ [Booking.com] API error: {error_msg}")
                    logger.warning(f"Booking.com Flight API error: {error_msg}")
                    return f"⚠️ No flights found for route: {origin} → {destination}\n\nTry using web search tool for alternative options."

            elif response.status_code == 401:
                return "❌ RapidAPI authentication error - Check API key"
            elif response.status_code == 403:
                return "❌ Access denied - API subscription required"
            elif response.status_code == 429:
                return "❌ API rate limit exceeded (500 requests/month on free tier)"
            else:
                logger.error(f"Booking.com API error: {response.status_code}")
                return f"⚠️ Flight API error (Status {response.status_code})\n\nPlease use web search tool."

        except requests.exceptions.Timeout:
            logger.error(f"Flight API timeout: {origin} → {destination}")
            return f"⚠️ Flight API timeout\n\nPlease use web search tool for flights: {origin} → {destination} on {departure_date}"
        except Exception as e:
            logger.error(f"Flight search exception: {e}")
            return f"⚠️ Error accessing flight API: {str(e)}\n\nPlease use web search tool."

    def search_destination(self, query: str) -> str:
        """
        Search for airports and cities by name.

        Args:
            query: City or airport name (e.g., "Bangkok", "New York", "Paris")

        Returns:
            str: Destination IDs, airport codes, and names in English
        """
        if not self.api_key:
            return "❌ RAPIDAPI_KEY not configured"

        try:
            url = f"{self.base_url}/searchDestination"

            params = {"query": query}

            logger.info(f"Searching destinations for: {query}")
            response = requests.get(url, headers=self.headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                return self._format_destinations_english(data, query)
            else:
                return f"❌ No destinations found for: {query}"

        except Exception as e:
            logger.error(f"Destination search exception: {e}")
            return f"❌ Error searching destination: {str(e)}"

    def _get_destination_id(self, query: str) -> Optional[str]:
        """
        Helper to get destination ID from city/airport name or code.
        Handles airport codes (e.g., "BKK", "SGN") and city names.
        Prefers AIRPORT type, falls back to CITY.
        """
        try:
            # Check if query looks like an airport code (2-3 uppercase letters)
            query_upper = query.upper().strip()
            if len(query_upper) <= 3 and query_upper.isalpha():
                # Likely an airport code - try to find exact match
                url = f"{self.base_url}/searchDestination"
                params = {"query": query_upper}

                response = requests.get(url, headers=self.headers, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()

                    if data.get("status") and data.get("data"):
                        destinations = data["data"]

                        # Find airport with matching code
                        for dest in destinations:
                            if (
                                dest.get("code", "").upper() == query_upper
                                and dest.get("type") == "AIRPORT"
                            ):
                                logger.info(f"Found airport {query_upper}: {dest.get('id')}")
                                return dest.get("id")

                        # Try first AIRPORT in list
                        for dest in destinations:
                            if dest.get("type") == "AIRPORT":
                                logger.info(
                                    f"Using first airport for {query_upper}: {dest.get('id')}"
                                )
                                return dest.get("id")

            # Not an airport code or no match found - search as city name
            url = f"{self.base_url}/searchDestination"
            params = {"query": query}

            response = requests.get(url, headers=self.headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()

                if data.get("status") and data.get("data"):
                    destinations = data["data"]

                    # Prefer AIRPORT type
                    for dest in destinations:
                        if dest.get("type") == "AIRPORT":
                            logger.info(f"Found airport for '{query}': {dest.get('id')}")
                            return dest.get("id")

                    # Fallback to first result (might be CITY)
                    if destinations:
                        dest_id = destinations[0].get("id")
                        logger.info(f"Using first destination for '{query}': {dest_id}")
                        return dest_id

            logger.warning(f"No destination found for: {query}")
            return None
        except Exception as e:
            logger.error(f"Destination ID lookup failed for '{query}': {e}")
            return None

    def _format_flights_english(
        self, data: Dict, origin: str, destination: str, max_results: int
    ) -> str:
        """Format Booking.com flight results in English for agents to process"""
        flight_data = data.get("data", {})
        flight_offers = flight_data.get("flightOffers", [])
        aggregation = flight_data.get("aggregation", {})

        if not flight_offers:
            return f"No flights found for route {origin} → {destination}."

        total_count = aggregation.get("totalCount", len(flight_offers))

        result = f"""Flight Search Results: {origin} → {destination}
Total flights available: {total_count}
Showing top {min(max_results, len(flight_offers))} results:

"""

        for i, flight in enumerate(flight_offers[:max_results], 1):
            # Get segments (outbound/return flights)
            segments = flight.get("segments", [])
            if not segments:
                continue

            # Process first segment (outbound)
            segment = segments[0]
            departure_airport = segment.get("departureAirport", {})
            arrival_airport = segment.get("arrivalAirport", {})
            departure_time = segment.get("departureTime", "")
            arrival_time = segment.get("arrivalTime", "")

            # Duration
            total_time_seconds = segment.get("totalTime", 0)
            duration_hours = total_time_seconds // 3600
            duration_minutes = (total_time_seconds % 3600) // 60

            # Legs (individual flights in segment)
            legs = segment.get("legs", [])
            airlines_set = set()
            flight_numbers = []
            stops = len(legs) - 1  # Number of stops

            for leg in legs:
                carriers_data = leg.get("carriersData", [])
                if carriers_data:
                    airline_info = carriers_data[0]
                    airlines_set.add(airline_info.get("name", "Unknown"))

                    flight_info = leg.get("flightInfo", {})
                    flight_num = flight_info.get("flightNumber", "")
                    carrier_code = airline_info.get("code", "")
                    if flight_num:
                        flight_numbers.append(f"{carrier_code}{flight_num}")

            # Price
            price_breakdown = flight.get("priceBreakdown", {})
            total_price_obj = price_breakdown.get("total", {})
            price_units = total_price_obj.get("units", 0)
            price_nanos = total_price_obj.get("nanos", 0)
            price = price_units + (price_nanos / 1000000000)
            currency = total_price_obj.get("currencyCode", "USD")

            # Format departure and arrival times
            dep_time_str = (
                departure_time.replace("T", " ") if "T" in departure_time else departure_time
            )
            arr_time_str = arrival_time.replace("T", " ") if "T" in arrival_time else arrival_time

            result += f"""Flight #{i}:
- Airline: {", ".join(airlines_set) if airlines_set else "N/A"}
- Flight number: {", ".join(flight_numbers) if flight_numbers else "N/A"}
- Departure: {departure_airport.get('code', 'N/A')} at {dep_time_str}
- Arrival: {arrival_airport.get('code', 'N/A')} at {arr_time_str}
- Duration: {duration_hours}h {duration_minutes}m
- Stops: {"Non-stop" if stops == 0 else f"{stops} stop(s)"}
- Price: ${price:.2f} {currency}

"""

        return result

    def _format_destinations_english(self, data: Dict, query: str) -> str:
        """Format destination search results in English for agents to process"""
        destinations = data.get("data", [])

        if not destinations:
            return f"No destinations found for: {query}"

        result = f"Destinations for '{query}':\n\nFound {len(destinations)} results:\n\n"

        for i, dest in enumerate(destinations, 1):
            dest_id = dest.get("id", "N/A")
            dest_type = dest.get("type", "N/A")
            name = dest.get("name", "N/A")
            code = dest.get("code", "N/A")
            city_name = dest.get("cityName", "")
            country = dest.get("countryName", "N/A")

            result += f"{i}. {name} ({code})\n"
            result += f"   - Type: {dest_type}\n"
            result += f"   - ID: {dest_id}\n"
            if city_name and city_name != name:
                result += f"   - City: {city_name}\n"
            result += f"   - Country: {country}\n\n"

        return result


class TripAdvisorHotelTools(Toolkit):
    """
    Hotel search toolkit using TripAdvisor API via RapidAPI
    Free tier: 500 requests/month
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize TripAdvisor Hotel API toolkit.

        Args:
            api_key: RapidAPI key (defaults to RAPIDAPI_KEY env var)
        """
        self.api_key = api_key or os.getenv("RAPIDAPI_KEY")
        self.base_url = "https://tripadvisor16.p.rapidapi.com/api/v1/hotels"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "tripadvisor16.p.rapidapi.com",
        }

        super().__init__(name="tripadvisor_hotel_tools", **kwargs)

        # Register tools after parent init
        self.register(self.search_hotels)
        self.register(self.search_hotel_location)

    def search_hotels(
        self, location: str, check_in: str, check_out: str, adults: int = 2, max_results: int = 5
    ) -> str:
        """
        Search for hotels in a location.

        Args:
            location: City name or location ID from search_hotel_location
            check_in: Check-in date in YYYY-MM-DD format
            check_out: Check-out date in YYYY-MM-DD format
            adults: Number of adults (default: 2)
            max_results: Maximum number of results (default: 5)

        Returns:
            str: Hotel search results in Vietnamese
        """
        if not self.api_key:
            return "❌ RAPIDAPI_KEY không được cấu hình trong .env file"

        try:
            # Step 1: Get location ID if location is city name
            if not location.isdigit():
                logger.info(f"Searching location ID for: {location}")
                location_id = self._get_location_id(location)
                if not location_id:
                    return f"❌ Không tìm thấy địa điểm: {location}"
            else:
                location_id = location

            # Step 2: Search hotels
            url = f"{self.base_url}/searchHotels"

            params = {
                "geoId": location_id,
                "checkIn": check_in,
                "checkOut": check_out,
                "adults": str(adults),
                "currency": "USD",
                "sortOrder": "POPULARITY",
            }

            print(f"🏨 [TripAdvisor] Searching hotels in {location} (ID: {location_id})")
            logger.info(f"Searching hotels in location ID {location_id}")
            response = requests.get(url, headers=self.headers, params=params, timeout=25)

            if response.status_code == 200:
                data = response.json()
                hotel_count = len(data.get("data", {}).get("data", []))
                print(f"✅ [TripAdvisor] Found {hotel_count} hotels in {location}")
                return self._format_hotels_vietnamese(
                    data, location, check_in, check_out, max_results
                )
            elif response.status_code == 401:
                return "❌ Lỗi xác thực RapidAPI"
            elif response.status_code == 403:
                return "❌ Không có quyền truy cập - Đăng ký API trên RapidAPI"
            elif response.status_code == 429:
                return "❌ Đã vượt quá hạn mức API"
            else:
                logger.error(f"Hotel API error: {response.status_code}")
                return f"❌ Lỗi tìm khách sạn (Status {response.status_code})"

        except Exception as e:
            logger.error(f"Hotel search exception: {e}")
            return f"❌ Lỗi: {str(e)}"

    def search_hotel_location(self, query: str) -> str:
        """
        Search for hotel locations by city name.

        Args:
            query: City or location name

        Returns:
            str: Location IDs and names in Vietnamese
        """
        if not self.api_key:
            return "❌ RAPIDAPI_KEY không được cấu hình"

        try:
            url = f"{self.base_url}/searchLocation"

            params = {"query": query}

            logger.info(f"Searching hotel locations for: {query}")
            response = requests.get(url, headers=self.headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                return self._format_locations_vietnamese(data, query)
            else:
                return f"❌ Không tìm thấy địa điểm: {query}"

        except Exception as e:
            logger.error(f"Location search exception: {e}")
            return f"❌ Lỗi tìm địa điểm: {str(e)}"

    def _get_location_id(self, city_name: str) -> Optional[str]:
        """Helper to get location ID from city name"""
        try:
            url = f"{self.base_url}/searchLocation"
            params = {"query": city_name}

            response = requests.get(url, headers=self.headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                locations = data.get("data", [])

                if locations:
                    return locations[0].get("geoId")

            return None
        except Exception as e:
            logger.error(f"Location ID lookup failed: {e}")
            return None

    def _format_hotels_vietnamese(
        self, data: Dict, location: str, check_in: str, check_out: str, max_results: int
    ) -> str:
        """Format hotel results in English for agents to process"""
        hotels = data.get("data", {}).get("data", [])

        if not hotels:
            return f"No hotels found in {location}"

        result = f"Hotel Search Results: {location}\nCheck-in: {check_in} | Check-out: {check_out}\n\nFound {len(hotels)} hotels:\n"

        for i, hotel in enumerate(hotels[:max_results], 1):
            title = hotel.get("title", "N/A")

            # Rating
            rating_data = hotel.get("bubbleRating", {})
            rating = rating_data.get("rating", "N/A")
            review_count = rating_data.get("count", 0)

            # Price
            price = hotel.get("priceForDisplay", "N/A")

            # Location
            area = hotel.get("secondaryInfo", "")

            # Provider
            provider = hotel.get("provider", "TripAdvisor")

            # Hotel ID
            hotel_id = hotel.get("id", "")

            result += f"""
Hotel #{i}: {title}
- Rating: {rating}/5 ({review_count} reviews)
- Price: {price}
- Area: {area if area else 'N/A'}
- Provider: {provider}
- ID: {hotel_id}
"""

        return result

    def _format_locations_vietnamese(self, data: Dict, query: str) -> str:
        """Format location search results in English for agents to process"""
        locations = data.get("data", [])

        if not locations:
            return f"No locations found: {query}"

        result = f"Locations found for: {query.upper()}\n\nFound {len(locations)} locations:\n"

        for i, location in enumerate(locations, 1):
            geo_id = location.get("geoId", "N/A")
            name = location.get("localizedName", "N/A")

            result += f"\n{i}. {name} (ID: {geo_id})"

        result += "\n\nUse this ID for search_hotels"

        return result


# Create toolkit instances
# These can be imported and used directly by agents


def create_weather_tools(api_key: Optional[str] = None) -> WeatherAPITools:
    """
    Create Weather API toolkit instance.

    Args:
        api_key: Optional API key (defaults to WEATHERAPI_KEY env var)

    Returns:
        WeatherAPITools instance ready to use
    """
    return WeatherAPITools(api_key=api_key)


def create_flight_tools(api_key: Optional[str] = None) -> BookingFlightTools:
    """
    Create Booking.com Flight API toolkit instance.

    Args:
        api_key: Optional API key (defaults to RAPIDAPI_KEY env var)

    Returns:
        BookingFlightTools instance ready to use
    """
    return BookingFlightTools(api_key=api_key)


def create_hotel_tools(api_key: Optional[str] = None) -> TripAdvisorHotelTools:
    """
    Create TripAdvisor Hotel API toolkit instance.

    Args:
        api_key: Optional API key (defaults to RAPIDAPI_KEY env var)

    Returns:
        TripAdvisorHotelTools instance ready to use
    """
    return TripAdvisorHotelTools(api_key=api_key)
