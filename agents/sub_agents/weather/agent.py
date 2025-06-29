
"""websearch_agent for finding Anything on web."""

from google.adk import Agent
from google.adk.tools import google_search
# agents/weather_agent.py
import requests
import os

MODEL = "gemini-2.5-flash"



def get_weather(coordinates: dict) -> dict:
    """
    Gets weather data using latitude and longitude from input dictionary and returns a dictonary {"weather": weather_summary}.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    
    # Extract coordinates from input dictionary
    lat = coordinates["latitude"]
    lon = coordinates["longitude"]
    location_name = coordinates.get("name", "Location")
    
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    
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
    return {"weather": weather_summary}


weather_agent = Agent(
    model=MODEL,
    name="wearther_agent",
    description="Gets weather data for a given location using coordinates.",
    instruction="Get the current weather data for the specified coordinates.",
    output_key="recent_citing_papers",
    tools=[get_weather],
)
