import requests
import re

API_BASE_URL = "https://api.spacexdata.com/v4"

COLLECTION_ENDPOINTS = {
    "capsules": {"endpoint": "capsules", "fields": ["serial", "status", "type"], "limit": 4},
    "cores": {"endpoint": "cores", "fields": ["serial", "status", "reuse_count"], "limit": 4},
    "dragons": {"endpoint": "dragons", "fields": ["name", "type", "crew_capacity"], "limit": 3},
    "history": {"endpoint": "history", "fields": ["title", "event_date_utc"], "limit": 5},
    "launches_upcoming": {"endpoint": "launches/upcoming", "fields": ["name", "date_utc", "launchpad"], "limit": 5},
    "launches_past": {"endpoint": "launches/past", "fields": ["name", "date_utc", "success"], "limit": 5},
    "landpads": {"endpoint": "landpads", "fields": ["name", "full_name", "status", "type"], "limit": 4},
    "launchpads": {"endpoint": "launchpads", "fields": ["name", "locality", "status"], "limit": 4},
    "payloads": {"endpoint": "payloads", "fields": ["name", "type", "mass_kg"], "limit": 5},
    "rockets": {"endpoint": "rockets", "fields": ["name", "type", "active"], "limit": 4},
    "ships": {"endpoint": "ships", "fields": ["name", "type", "home_port"], "limit": 4},
}

SINGLE_ENDPOINTS = {
    "company": {"endpoint": "company", "fields": ["name", "founder", "founded", "employees", "launch_sites", "vehicles"]},
    "roadster": {"endpoint": "roadster", "fields": ["name", "launch_date_utc", "earth_distance_km", "mars_distance_km", "speed_kph"]},
}

V3_MISSIONS_ENDPOINT = "https://api.spacexdata.com/v3/missions"


def run(previous_data: dict) -> dict:
    """
    Fetch an expanded snapshot of SpaceX data:
    - Next launch with rocket, payload, capsule, and launchpad metadata
    - Latest launch summary
    - Company + Roadster info
    - Overviews of additional resources (capsules, cores, dragons, etc.)
    - Can search for specific missions by name if mentioned in goal
    """
    goal_text = (previous_data or {}).get("goal", "")
    wants_latest = _goal_requests_latest(goal_text)
    
    # Try to find a specific mission mentioned in the goal
    mission_name = _extract_mission_name(goal_text)
    primary_launch = None
    mission_requested = False
    
    if mission_name:
        mission_requested = True
        print(f"🔍 SpaceX Agent: Searching for mission '{mission_name}'...")
        primary_launch = _search_mission_by_name(mission_name)
        if primary_launch:
            found_mission = primary_launch.get("name", "Unknown")
            print(f"✅ SpaceX Agent: Found mission '{mission_name}' (Launch: {found_mission})")
        else:
            print(f"⚠️ SpaceX Agent: Mission '{mission_name}' not found in SpaceX API")
            print(f"   This mission may not be available in the API or may use a different name.")
            print(f"   Falling back to default launch...")
    
    # Fallback to next/latest if no specific mission found
    if not primary_launch:
        primary_endpoint = "launches/latest" if wants_latest else "launches/next"
        try:
            primary_launch = _fetch(primary_endpoint)
            if mission_requested:
                fallback_mission = primary_launch.get("name", "Unknown")
                print(f"⚠️ SpaceX Agent: Using fallback launch: {fallback_mission}")
                print(f"   Note: Requested mission '{mission_name}' was not found.")
        except requests.RequestException as e:
            if wants_latest:
                print(f"⚠️ SpaceX Agent: latest launch unavailable, falling back to next: {e}")
                wants_latest = False
                primary_launch = _fetch("launches/next")
            else:
                raise Exception(f"SpaceX API request failed: {e}") from e

    launch_info = _build_launch_snapshot(primary_launch)
    next_launch_snapshot = (
        launch_info if not wants_latest else _build_launch_snapshot(_safe_fetch("launches/next"))
    )
    latest_launch_detail = (
        launch_info if wants_latest else _build_launch_snapshot(_safe_fetch("launches/latest"))
    )
    latest_launch = _safe_launch_summary("launches/latest", launch=primary_launch if wants_latest else None)
    resource_overview = _collect_resource_overview()
    single_resource_data = _collect_single_resources()

    spacex_payload = {
        "primary_focus": "latest" if wants_latest else "next",
        "next_launch": next_launch_snapshot,
        "latest_launch_detail": latest_launch_detail,
        "latest_launch": latest_launch,
        "resources": resource_overview,
    }
    if launch_info:
        spacex_payload.update(
            {
                "mission": launch_info.get("mission"),
                "date": launch_info.get("date"),
                "launchpad_id": launch_info.get("launchpad_id"),
                "coordinates": launch_info.get("coordinates"),
            }
        )
        # Add note if a specific mission was requested but not found
        if mission_requested and mission_name:
            found_mission = launch_info.get("mission", "")
            if mission_name.lower() not in found_mission.lower() and found_mission.lower() not in mission_name.lower():
                spacex_payload["mission_search_note"] = f"Requested mission '{mission_name}' not found. Showing: {found_mission}"
    spacex_payload.update(single_resource_data)

    previous_data.update({"spacex": spacex_payload})
    print("🚀 SpaceX Agent: enriched SpaceX snapshot loaded.")
    return previous_data


def _fetch(endpoint, resource_id=None):
    url = f"{API_BASE_URL}/{endpoint}"
    if resource_id:
        url = f"{url}/{resource_id}"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


def _safe_fetch(endpoint, resource_id=None):
    try:
        return _fetch(endpoint, resource_id)
    except requests.RequestException as exc:
        print(f"⚠️ SpaceX Agent: failed to fetch {endpoint}{'/' + resource_id if resource_id else ''}: {exc}")
        return None


def _build_launch_snapshot(launch):
    if not launch:
        return {}

    launchpad_id = launch.get("launchpad")
    rocket_id = launch.get("rocket")
    payload_ids = launch.get("payloads", []) or []
    capsule_ids = launch.get("capsules", []) or []

    launchpad = _safe_fetch("launchpads", launchpad_id) if launchpad_id else None
    rocket = _safe_fetch("rockets", rocket_id) if rocket_id else None

    payloads = [_summarize_payload(_safe_fetch("payloads", payload_id)) for payload_id in payload_ids[:3]]
    payloads = [payload for payload in payloads if payload]

    capsules = [_summarize_capsule(_safe_fetch("capsules", capsule_id)) for capsule_id in capsule_ids[:3]]
    capsules = [capsule for capsule in capsules if capsule]

    coordinates = None
    if launchpad:
        lat = launchpad.get("latitude")
        lon = launchpad.get("longitude")
        if lat is not None and lon is not None:
            coordinates = {
                "latitude": lat,
                "longitude": lon,
                "name": launchpad.get("name"),
                "location": launchpad.get("locality"),
            }

    return {
        "mission": launch.get("name"),
        "date": launch.get("date_utc"),
        "launchpad_id": launchpad_id,
        "rocket": _summarize_rocket(rocket),
        "payloads": payloads,
        "capsules": capsules,
        "coordinates": coordinates,
        "details": launch.get("details"),
        "links": launch.get("links"),
    }


def _safe_launch_summary(endpoint, launch=None):
    if launch is None:
        launch = _safe_fetch(endpoint)
    if not launch:
        return None
    return {
        "mission": launch.get("name"),
        "date": launch.get("date_utc"),
        "success": launch.get("success"),
        "rocket": launch.get("rocket"),
        "launchpad": launch.get("launchpad"),
    }


def _summarize_payload(payload):
    if not payload:
        return None
    return {
        "name": payload.get("name"),
        "type": payload.get("type"),
        "mass_kg": payload.get("mass_kg"),
        "orbit": payload.get("orbit"),
    }


def _summarize_capsule(capsule):
    if not capsule:
        return None
    return {
        "serial": capsule.get("serial"),
        "status": capsule.get("status"),
        "type": capsule.get("type"),
        "last_update": capsule.get("last_update"),
    }


def _summarize_rocket(rocket):
    if not rocket:
        return None
    return {
        "name": rocket.get("name"),
        "type": rocket.get("type"),
        "active": rocket.get("active"),
        "stages": rocket.get("stages"),
        "boosters": rocket.get("boosters"),
    }


def _collect_resource_overview() -> dict:
    overview = {}
    for label, config in COLLECTION_ENDPOINTS.items():
        endpoint = config["endpoint"]
        limit = config["limit"]
        fields = config["fields"]
        data = _safe_fetch(endpoint)
        if not data:
            overview[label] = {"error": f"Unable to load {endpoint}"}
            continue
        if isinstance(data, dict):
            data_items = [data]
        else:
            data_items = data

        summary_items = []
        for item in data_items[:limit]:
            summary_items.append({field: item.get(field) for field in fields})

        overview[label] = {"count": len(data_items), "sample": summary_items}

    overview["missions"] = _fetch_v3_missions()
    return overview


def _collect_single_resources() -> dict:
    results = {}
    for label, config in SINGLE_ENDPOINTS.items():
        data = _safe_fetch(config["endpoint"])
        if not data:
            results[label] = {"error": f"Unable to load {config['endpoint']}"}
            continue
        results[label] = {field: data.get(field) for field in config["fields"]}
    return results


def _fetch_v3_missions(limit: int = 4) -> dict:
    try:
        response = requests.get(V3_MISSIONS_ENDPOINT, timeout=15)
        response.raise_for_status()
        missions = response.json()
    except requests.RequestException as exc:
        msg = f"Unable to load missions: {exc}"
        print(f"⚠️ SpaceX Agent: {msg}")
        return {"error": msg}

    sample = []
    for mission in missions[:limit]:
        sample.append({
            "mission_name": mission.get("mission_name"),
            "mission_id": mission.get("mission_id"),
            "manufacturers": mission.get("manufacturers"),
            "payload_ids": mission.get("payload_ids"),
            "description": mission.get("description"),
        })

    return {"count": len(missions), "sample": sample, "source": "v3"}


def _goal_requests_latest(goal_text: str) -> bool:
    if not goal_text:
        return False
    goal_text = goal_text.lower()
    keywords = ["past", "previous", "prior", "latest", "last", "recent", "history"]
    return any(word in goal_text for word in keywords)


def _extract_mission_name(goal_text: str) -> str:
    """
    Extract mission name from goal text.
    Looks for patterns like "Iridium NEXT", "Starlink", "Crew Dragon", etc.
    """
    if not goal_text:
        return None
    
    goal_lower = goal_text.lower()
    
    # Common mission name patterns (including Orbcomm) - check these FIRST
    mission_patterns = [
        r"orbcomm\s+og\s*\d+",  # Orbcomm OG2, Orbcomm OG-2, etc.
        r"orbcomm\s+og\d+",     # Orbcomm OG2 (no space)
        r"orbcomm",             # Just "Orbcomm" as fallback
        r"iridium\s+next",
        r"starlink\s+\d+",
        r"crew\s+dragon",
        r"crew\s*-\s*\d+",      # Crew-5, Crew-6, etc.
        r"crs\s*-\s*\d+",
        r"uscf\s*-\s*\d+",
        r"transporter\s+\d+",
        r"falcon\s+heavy",
        r"starship",
        r"artemis",
        r"dart",
        r"james\s+webb",
        r"perseverance",
    ]
    
    for pattern in mission_patterns:
        match = re.search(pattern, goal_lower, re.IGNORECASE)
        if match:
            # Extract the matched text and clean it up
            mission = goal_text[match.start():match.end()].strip()
            return mission
    
    # Priority: Look for mission name right after "mission" keyword
    mission_keywords = ['mission', 'spacex', 'launch', 'get', 'the']
    words = goal_text.split()
    mission_candidates = []
    
    # Priority 1: Right after "mission" keyword
    for i, word in enumerate(words):
        word_lower = word.lower().rstrip(',.')
        if word_lower == 'mission' and i + 1 < len(words):
            # Look ahead for capitalized words or alphanumeric (like "OG2")
            candidate = []
            j = i + 1
            while j < len(words) and j < i + 5:  # Max 4 words ahead
                next_word = words[j].rstrip(',.')
                # Allow: capitalized words, alphanumeric codes (OG2, CRS-5), or mixed
                is_valid = (
                    (next_word[0].isupper() and len(next_word) > 1) or  # Capitalized word
                    (next_word[0].isalnum() and any(c.isupper() for c in next_word) and len(next_word) > 1) or  # Mixed case like "OG2"
                    (next_word.replace('-', '').replace('_', '').isalnum() and len(next_word) > 1)  # Alphanumeric with dashes
                )
                if is_valid:
                    candidate.append(next_word)
                    j += 1
                else:
                    break
            if len(candidate) >= 1:  # At least 1 word (e.g., "Orbcomm OG2")
                candidate_str = " ".join(candidate)
                # Filter out common non-mission phrases
                if not any(phrase in candidate_str.lower() for phrase in 
                          ['international space station', 'space mission intelligence']):
                    mission_candidates.append((candidate_str, i, 1))  # Priority 1 (highest)
    
    # Priority 2: Near other mission keywords
    for i, word in enumerate(words):
        word_lower = word.lower().rstrip(',.')
        if word_lower in ['spacex', 'launch', 'get'] and i + 1 < len(words):
            candidate = []
            j = i + 1
            while j < len(words) and j < i + 4:  # Max 3 words ahead
                next_word = words[j].rstrip(',.')
                is_valid = (
                    (next_word[0].isupper() and len(next_word) > 1) or
                    (next_word[0].isalnum() and any(c.isupper() for c in next_word) and len(next_word) > 1)
                )
                if is_valid:
                    candidate.append(next_word)
                    j += 1
                else:
                    break
            if len(candidate) >= 2:  # At least 2 words
                candidate_str = " ".join(candidate)
                if not any(phrase in candidate_str.lower() for phrase in 
                          ['international space station', 'space mission intelligence',
                           'launch details', 'rocket specifications']):
                    mission_candidates.append((candidate_str, i, 2))  # Priority 2
    
    # Priority 3: General capitalized phrases
    if not mission_candidates:
        i = 0
        while i < len(words):
            word = words[i].rstrip(',.')
            if (word[0].isupper() or (word[0].isalnum() and any(c.isupper() for c in word))) and len(word) > 1:
                candidate = [word]
                i += 1
                while i < len(words):
                    next_word = words[i].rstrip(',.')
                    is_valid = (
                        (next_word[0].isupper() and len(next_word) > 1) or
                        (next_word[0].isalnum() and any(c.isupper() for c in next_word) and len(next_word) > 1) or
                        (next_word.replace('-', '').replace('_', '').isalnum() and len(next_word) > 1)
                    )
                    if is_valid:
                        candidate.append(next_word)
                        i += 1
                    else:
                        break
                if len(candidate) >= 2:  # At least 2 words
                    candidate_str = " ".join(candidate)
                    if not any(phrase in candidate_str.lower() for phrase in 
                              ['international space station', 'space mission intelligence', 
                               'launch details', 'rocket specifications', 'crew-5', 'crew-6']):
                        mission_candidates.append((candidate_str, i, 3))  # Priority 3
            else:
                i += 1
    
    # Return the candidate with highest priority (lowest number), then earliest position
    if mission_candidates:
        mission_candidates.sort(key=lambda x: (x[2], x[1]))  # Sort by priority, then position
        return mission_candidates[0][0]
    
    return None


def _search_mission_by_name(mission_name: str) -> dict:
    """
    Search for a specific mission by name in both upcoming and past launches.
    Returns the launch data if found, None otherwise.
    """
    if not mission_name:
        return None
    
    mission_lower = mission_name.lower()
    
    def _search_in_launches(launches_data):
        """Helper to search in a list of launches"""
        if not launches_data:
            return None
        
        # Handle both list and single dict responses
        if isinstance(launches_data, dict):
            launches_list = [launches_data]
        else:
            launches_list = launches_data
        
        for launch in launches_list:
            launch_name = launch.get("name", "").lower()
            # Check launch name
            if mission_lower in launch_name or launch_name in mission_lower:
                return launch
            
            # Also check payloads - mission name might be in payload (e.g., "Orbcomm OG2")
            payload_ids = launch.get("payloads", [])
            if payload_ids:
                for payload_id in payload_ids[:5]:  # Check first 5 payloads
                    try:
                        payload = _safe_fetch("payloads", payload_id)
                        if payload:
                            payload_name = payload.get("name", "").lower()
                            # Check if mission name is in payload name
                            if mission_lower in payload_name or payload_name in mission_lower:
                                return launch
                            # Also check partial match (e.g., "orbcomm" in "Orbcomm OG2 Mission 1")
                            mission_words = mission_lower.split()
                            for word in mission_words:
                                if len(word) > 3 and word in payload_name:
                                    return launch
                    except:
                        continue
        return None
    
    # Search in upcoming launches first
    try:
        upcoming = _safe_fetch("launches/upcoming")
        result = _search_in_launches(upcoming)
        if result:
            return result
    except Exception as e:
        print(f"⚠️ SpaceX Agent: Error searching upcoming launches: {e}")
    
    # Search in past launches
    try:
        past = _safe_fetch("launches/past")
        result = _search_in_launches(past)
        if result:
            return result
    except Exception as e:
        print(f"⚠️ SpaceX Agent: Error searching past launches: {e}")
    
    # Try partial matching with each keyword separately
    mission_keywords = mission_lower.split()
    
    # Try each keyword (e.g., "orbcomm" or "og2")
    for keyword in mission_keywords:
        if len(keyword) > 2:  # Only if it's substantial
            try:
                upcoming = _safe_fetch("launches/upcoming")
                result = _search_in_launches(upcoming)
                if result:
                    return result
            except:
                pass
            
            try:
                past = _safe_fetch("launches/past")
                result = _search_in_launches(past)
                if result:
                    return result
            except:
                pass
    
    # Last resort: try searching with just "orbcomm" if mission contains it
    if "orbcomm" in mission_lower:
        try:
            past = _safe_fetch("launches/past")
            if isinstance(past, dict):
                launches_list = [past]
            else:
                launches_list = past or []
            # Search more thoroughly in past launches
            for launch in launches_list:
                launch_name = launch.get("name", "").lower()
                # Check for variations: "orbcomm", "orbcomm og", "orbcomm-og"
                if "orbcomm" in launch_name:
                    # Also check payloads
                    payload_ids = launch.get("payloads", [])
                    if payload_ids:
                        for payload_id in payload_ids[:5]:
                            payload = _safe_fetch("payloads", payload_id)
                            if payload:
                                payload_name = payload.get("name", "").lower()
                                if "orbcomm" in payload_name and ("og" in payload_name or "og2" in payload_name):
                                    return launch
                    # If launch name contains orbcomm, return it
                    if "orbcomm" in launch_name:
                        return launch
        except Exception as e:
            print(f"⚠️ SpaceX Agent: Error in Orbcomm search: {e}")
    
    return None