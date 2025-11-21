import os
import requests

KNOWN_LOCATIONS = {
    "kennedy space center": {
        "latitude": 28.6080585,
        "longitude": -80.6039558,
        "name": "KSC LC 39A",
    },
    "ksc": {
        "latitude": 28.6080585,
        "longitude": -80.6039558,
        "name": "KSC LC 39A",
    },
    "cape canaveral": {
        "latitude": 28.3922,
        "longitude": -80.6077,
        "name": "Cape Canaveral",
    },
    "merritt island": {
        "latitude": 28.2639,
        "longitude": -80.6800,
        "name": "Merritt Island",
    },
}


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
    lat, lon, location_name = _resolve_coordinates(previous_data, api_key)
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


def _resolve_coordinates(previous_data: dict, api_key: str):
    spacex_data = previous_data.get("spacex", {})
    coordinates = spacex_data.get("coordinates", {}) or {}

    lat = coordinates.get("latitude")
    lon = coordinates.get("longitude")
    location_name = coordinates.get("name") or "Launch Site"

    if lat and lon:
        return lat, lon, location_name

    lat = previous_data.get("latitude") or previous_data.get("lat")
    lon = previous_data.get("longitude") or previous_data.get("lon")
    location_name = previous_data.get("location") or location_name
    if lat and lon:
        return lat, lon, location_name or "Provided Location"

    location_guess = (
        previous_data.get("location")
        or _extract_location_from_goal(previous_data.get("goal", ""))
        or "Kennedy Space Center"
    )

    lat, lon, resolved_name = _match_known_location(location_guess)
    if lat and lon:
        return lat, lon, resolved_name

    geocoded = _geocode_location(location_guess, api_key)
    if geocoded:
        return geocoded["lat"], geocoded["lon"], geocoded["name"]

    return None, None, location_guess


def _extract_location_from_goal(goal_text: str) -> str | None:
    goal_text = (goal_text or "").lower()
    for name in KNOWN_LOCATIONS.keys():
        if name in goal_text:
            return name
    return goal_text.strip() or None


def _match_known_location(location_guess: str):
    if not location_guess:
        return None, None, None
    key = location_guess.lower()
    for name, info in KNOWN_LOCATIONS.items():
        if name in key:
            return info["latitude"], info["longitude"], info["name"]
    return None, None, None


def _geocode_location(location_name: str, api_key: str):
    if not location_name:
        return None
    try:
        url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {
            "q": location_name,
            "limit": 1,
            "appid": api_key,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        place = data[0]
        return {
            "lat": place.get("lat"),
            "lon": place.get("lon"),
            "name": place.get("name") or location_name.title(),
        }
    except requests.RequestException as exc:
        print(f"⚠️ Weather Agent: geocoding failed for '{location_name}': {exc}")
        return None
