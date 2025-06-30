import requests
import os

def run(previous_data: dict) -> dict:
    """
    Gets weather data at the launch location using coordinates from SpaceX agent
    or directly from previous_data if provided.
    Adds weather info to previous_data.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise Exception("WEATHER_API_KEY environment variable is not set.")

    # Try to get coordinates from SpaceX data first
    spacex_data = previous_data.get("spacex", {})
    coordinates = spacex_data.get("coordinates", {})

    lat = coordinates.get("latitude")
    lon = coordinates.get("longitude")
    location_name = coordinates.get("name", "Launch Site")

    # If SpaceX coordinates not present, try to get from top-level keys lat/lon or location name
    if not (lat and lon):
        lat = previous_data.get("latitude") or previous_data.get("lat")
        lon = previous_data.get("longitude") or previous_data.get("lon")
        location_name = previous_data.get("location") or location_name

    if not (lat and lon):
        raise Exception("No valid coordinates found for weather query.")

    print(f"🌍 Weather Agent: Fetching weather for {location_name} ({lat}, {lon})")

    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric"  # metric for Celsius, can switch to 'imperial' for °F
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Weather API error: {response.status_code} - {response.text}")

    data = response.json()

    # Defensive checks in case API response is incomplete
    main = data.get("main", {})
    wind = data.get("wind", {})
    clouds = data.get("clouds", {})
    weather_list = data.get("weather", [{}])

    weather_summary = {
        "location": location_name,
        "latitude": lat,
        "longitude": lon,
        "temperature": main.get("temp", "N/A"),
        "wind_speed": wind.get("speed", "N/A"),
        "clouds": clouds.get("all", "N/A"),
        "condition": weather_list[0].get("description", "N/A"),
        "humidity": main.get("humidity", "N/A")
    }

    previous_data.update({"weather": weather_summary})
    print(f"🌤️ Weather Agent: weather info added: {weather_summary}")
    return previous_data
