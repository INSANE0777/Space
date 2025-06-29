# agents/weather_agent.py

import requests
import os

def run(previous_data: dict) -> dict:
    """
    Gets weather data at the launch location using coordinates from SpaceX agent.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    
    # Get coordinates from SpaceX data
    spacex_data = previous_data.get("spacex", {})
    coordinates = spacex_data.get("coordinates", {})
    
    if coordinates and coordinates.get("latitude") and coordinates.get("longitude"):
        lat = coordinates["latitude"]
        lon = coordinates["longitude"]
        location_name = coordinates.get("name", "Launch Site")
        print(f"🌍 Getting weather for {location_name} at ({lat}, {lon})")
    else:
        # Fallback to Kennedy Space Center if coordinates not available
        lat, lon = 28.562302, -80.577356
        location_name = "Kennedy Space Center (fallback)"
        print(f"⚠️ Using fallback location: {location_name}")

    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Weather API error: {response.status_code}")
    
    data = response.json()

    weather_summary = {
        "location": location_name,
        "latitude": lat,
        "longitude": lon,
        "temperature": data["main"]["temp"],
        "wind_speed": data["wind"]["speed"],
        "clouds": data["clouds"]["all"],
        "condition": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"]
    }

    previous_data.update({"weather": weather_summary})
    return previous_data
