import requests

def run(previous_data: dict) -> dict:
    """
    Fetches next SpaceX launch data and resolves launchpad coordinates.
    Updates previous_data with the launch info and coordinates.
    """
    try:
        url = "https://api.spacexdata.com/v4/launches/next"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        launchpad_id = data.get("launchpad")
        
        coordinates = None
        if launchpad_id:
            launchpad_url = f"https://api.spacexdata.com/v4/launchpads/{launchpad_id}"
            launchpad_response = requests.get(launchpad_url, timeout=10)
            if launchpad_response.status_code == 200:
                launchpad_data = launchpad_response.json()
                lat = launchpad_data.get("latitude")
                lon = launchpad_data.get("longitude")
                name = launchpad_data.get("name")
                location = launchpad_data.get("locality")
                
                if lat is not None and lon is not None:
                    coordinates = {
                        "latitude": lat,
                        "longitude": lon,
                        "name": name,
                        "location": location
                    }
            else:
                print(f"⚠️ Launchpad API returned error: {launchpad_response.status_code}")
        
        launch_info = {
            "mission": data.get("name"),
            "date": data.get("date_utc"),
            "launchpad_id": launchpad_id,
            "coordinates": coordinates
        }
        
        previous_data.update({"spacex": launch_info})
        print(f"🚀 SpaceX Agent: launch info added with coordinates: {coordinates}")
        return previous_data

    except requests.RequestException as e:
        raise Exception(f"SpaceX API request failed: {e}")
