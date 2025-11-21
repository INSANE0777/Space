"""
Satellite Data Agent
Fetches satellite information, tracking data, and orbital parameters.
"""

import requests
import os
from datetime import datetime, timezone

# N2YO API for satellite data (free tier available)
N2YO_API_BASE = "https://api.n2yo.com/rest/v1/satellite"

def run(previous_data: dict) -> dict:
    """
    Fetches satellite data including:
    - Satellite positions and tracking
    - Orbital parameters
    - Satellite catalog information
    - Pass predictions
    """
    api_key = os.getenv("N2YO_API_KEY")
    
    # For demo purposes, we'll use mock data if API key is not available
    # In production, you would use the N2YO API or similar service
    if not api_key:
        print("⚠️ Satellite Agent: N2YO_API_KEY not set, using mock data")
        satellite_data = _get_mock_satellite_data()
    else:
        try:
            satellite_data = _fetch_satellite_data(api_key, previous_data)
        except Exception as e:
            print(f"⚠️ Satellite Agent: API error, using mock data: {e}")
            satellite_data = _get_mock_satellite_data()
    
    previous_data.update({"satellite": satellite_data})
    print("🛰️ Satellite Agent: satellite data loaded.")
    return previous_data


def _fetch_satellite_data(api_key: str, previous_data: dict) -> dict:
    """Fetch real satellite data from N2YO API"""
    # Example: Get positions of popular satellites
    # ISS (International Space Station) - NORAD ID: 25544
    iss_norad_id = 25544
    
    # Get observer location (default to Kennedy Space Center)
    spacex_data = previous_data.get("spacex", {})
    coordinates = spacex_data.get("coordinates", {})
    
    observer_lat = coordinates.get("latitude", 28.6080585)
    observer_lon = coordinates.get("longitude", -80.6039558)
    observer_alt = 0  # Sea level
    
    # Get current positions
    positions_url = f"{N2YO_API_BASE}/positions/{iss_norad_id}/{observer_lat}/{observer_lon}/{observer_alt}/1"
    params = {"apiKey": api_key}
    
    try:
        response = requests.get(positions_url, params=params, timeout=10)
        response.raise_for_status()
        positions_data = response.json()
        
        # Get satellite info
        tle_url = f"{N2YO_API_BASE}/tle/{iss_norad_id}"
        tle_response = requests.get(tle_url, params=params, timeout=10)
        tle_data = tle_response.json() if tle_response.status_code == 200 else {}
        
        return {
            "satellite_name": "International Space Station (ISS)",
            "norad_id": iss_norad_id,
            "positions": positions_data.get("positions", []),
            "tle": tle_data,
            "observer_location": {
                "latitude": observer_lat,
                "longitude": observer_lon,
                "altitude": observer_alt
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "N2YO API"
        }
    except requests.RequestException as e:
        raise Exception(f"N2YO API request failed: {e}")


def _get_mock_satellite_data() -> dict:
    """Generate mock satellite data for demonstration"""
    return {
        "satellite_name": "International Space Station (ISS)",
        "norad_id": 25544,
        "orbital_parameters": {
            "inclination": 51.64,
            "period_minutes": 92.68,
            "altitude_km": 408,
            "velocity_km_s": 7.66
        },
        "current_position": {
            "latitude": 28.5,
            "longitude": -80.6,
            "altitude_km": 408,
            "velocity_km_s": 7.66
        },
        "next_pass": {
            "start_time": "2024-01-15T18:30:00Z",
            "max_elevation": 45.2,
            "duration_minutes": 6
        },
        "status": "operational",
        "mission_type": "Space Station",
        "launch_date": "1998-11-20",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "mock_data"
    }

