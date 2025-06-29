# agents/spacex_agent.py

import requests

def run(previous_data: dict) -> dict:
    """
    Fetches next SpaceX launch data and resolves launchpad coordinates.
    """
    # Get next launch data
    url = "https://api.spacexdata.com/v4/launches/next"
    response = requests.get(url)
    data = response.json()
    
    launchpad_id = data.get("launchpad")
    
    # Resolve launchpad coordinates
    coordinates = None
    if launchpad_id:
        launchpad_url = f"https://api.spacexdata.com/v4/launchpads/{launchpad_id}"
        launchpad_response = requests.get(launchpad_url)
        if launchpad_response.status_code == 200:
            launchpad_data = launchpad_response.json()
            coordinates = {
                "latitude": launchpad_data.get("latitude"),
                "longitude": launchpad_data.get("longitude"),
                "name": launchpad_data.get("name"),
                "location": launchpad_data.get("locality")
            }

    launch_info = {
        "mission": data.get("name"),
        "date": data.get("date_utc"),
        "launchpad_id": launchpad_id,
        "coordinates": coordinates
    }

    previous_data.update({"spacex": launch_info})
    return previous_data
