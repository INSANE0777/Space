"""
Anomalies Detection Agent
Detects anomalies in space-related data including:
- Launch anomalies
- Weather anomalies
- Satellite tracking anomalies
- Data inconsistencies
"""

import os
from datetime import datetime, timezone
from typing import Dict, List, Any

def run(previous_data: dict) -> dict:
    """
    Analyzes data from previous agents to detect anomalies:
    - Weather conditions that could affect launches
    - Satellite tracking anomalies
    - Data inconsistencies
    - Launch readiness issues
    """
    anomalies = []
    
    # Check weather anomalies
    weather_anomalies = _detect_weather_anomalies(previous_data)
    anomalies.extend(weather_anomalies)
    
    # Check launch readiness anomalies
    launch_anomalies = _detect_launch_anomalies(previous_data)
    anomalies.extend(launch_anomalies)
    
    # Check satellite data anomalies
    satellite_anomalies = _detect_satellite_anomalies(previous_data)
    anomalies.extend(satellite_anomalies)
    
    # Check data consistency
    consistency_anomalies = _detect_data_consistency_issues(previous_data)
    anomalies.extend(consistency_anomalies)
    
    anomaly_summary = {
        "total_anomalies": len(anomalies),
        "critical_count": sum(1 for a in anomalies if a.get("severity") == "critical"),
        "warning_count": sum(1 for a in anomalies if a.get("severity") == "warning"),
        "info_count": sum(1 for a in anomalies if a.get("severity") == "info"),
        "anomalies": anomalies,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "critical" if any(a.get("severity") == "critical" for a in anomalies) else 
                  "warning" if any(a.get("severity") == "warning" for a in anomalies) else 
                  "normal"
    }
    
    previous_data.update({"anomalies": anomaly_summary})
    print(f"🔍 Anomalies Detection Agent: detected {len(anomalies)} anomalies.")
    return previous_data


def _detect_weather_anomalies(previous_data: dict) -> List[Dict[str, Any]]:
    """Detect weather-related anomalies that could affect launches"""
    anomalies = []
    weather_data = previous_data.get("weather", {})
    
    if not weather_data:
        return anomalies
    
    # Check wind speed
    wind_speed = weather_data.get("wind_speed")
    if isinstance(wind_speed, (int, float)):
        if wind_speed > 15:  # m/s threshold for launch concerns
            anomalies.append({
                "type": "weather",
                "category": "wind_speed",
                "severity": "critical" if wind_speed > 20 else "warning",
                "message": f"High wind speed detected: {wind_speed} m/s. May affect launch conditions.",
                "value": wind_speed,
                "threshold": 15,
                "recommendation": "Monitor wind conditions closely. Consider launch delay if wind speed exceeds 20 m/s."
            })
    
    # Check cloud cover
    clouds = weather_data.get("clouds")
    if isinstance(clouds, (int, float)):
        if clouds > 80:
            anomalies.append({
                "type": "weather",
                "category": "cloud_cover",
                "severity": "warning",
                "message": f"High cloud cover: {clouds}%. May affect visibility and launch conditions.",
                "value": clouds,
                "threshold": 80,
                "recommendation": "Assess visibility requirements for launch."
            })
    
    # Check temperature extremes
    temperature = weather_data.get("temperature")
    if isinstance(temperature, (int, float)):
        if temperature < 0 or temperature > 40:
            anomalies.append({
                "type": "weather",
                "category": "temperature",
                "severity": "warning",
                "message": f"Extreme temperature: {temperature}°C. May affect equipment performance.",
                "value": temperature,
                "threshold": "0-40°C",
                "recommendation": "Verify equipment operating temperature ranges."
            })
    
    return anomalies


def _detect_launch_anomalies(previous_data: dict) -> List[Dict[str, Any]]:
    """Detect anomalies in launch data"""
    anomalies = []
    spacex_data = previous_data.get("spacex", {})
    
    if not spacex_data:
        return anomalies
    
    # Check for missing critical launch data
    required_fields = ["mission", "date", "coordinates"]
    missing_fields = [field for field in required_fields if not spacex_data.get(field)]
    
    if missing_fields:
        anomalies.append({
            "type": "launch",
            "category": "missing_data",
            "severity": "warning",
            "message": f"Missing critical launch data fields: {', '.join(missing_fields)}",
            "missing_fields": missing_fields,
            "recommendation": "Verify SpaceX API connectivity and data completeness."
        })
    
    # Check launch date validity
    launch_date = spacex_data.get("date")
    if launch_date and launch_date != "TBD":
        try:
            # Simple check - if date is in the past and it's not marked as "latest"
            # This is a simplified check
            pass
        except:
            anomalies.append({
                "type": "launch",
                "category": "date_format",
                "severity": "info",
                "message": "Launch date format may be inconsistent.",
                "value": launch_date,
                "recommendation": "Verify date format consistency."
            })
    
    return anomalies


def _detect_satellite_anomalies(previous_data: dict) -> List[Dict[str, Any]]:
    """Detect anomalies in satellite tracking data"""
    anomalies = []
    satellite_data = previous_data.get("satellite", {})
    
    if not satellite_data:
        return anomalies
    
    # Check satellite altitude
    orbital_params = satellite_data.get("orbital_parameters", {})
    altitude = orbital_params.get("altitude_km")
    
    if isinstance(altitude, (int, float)):
        # Normal ISS altitude range: 400-420 km
        if altitude < 350 or altitude > 450:
            anomalies.append({
                "type": "satellite",
                "category": "orbital_altitude",
                "severity": "warning",
                "message": f"Unusual satellite altitude: {altitude} km. Outside normal range.",
                "value": altitude,
                "threshold": "350-450 km",
                "recommendation": "Verify satellite tracking data accuracy."
            })
    
    # Check for missing position data
    current_position = satellite_data.get("current_position")
    if not current_position:
        anomalies.append({
            "type": "satellite",
            "category": "missing_position",
            "severity": "info",
            "message": "Current satellite position data not available.",
            "recommendation": "Update satellite tracking data."
        })
    
    return anomalies


def _detect_data_consistency_issues(previous_data: dict) -> List[Dict[str, Any]]:
    """Detect data consistency issues across agents"""
    anomalies = []
    
    # Check if SpaceX coordinates match weather location
    spacex_data = previous_data.get("spacex", {})
    weather_data = previous_data.get("weather", {})
    
    if spacex_data and weather_data:
        spacex_coords = spacex_data.get("coordinates", {})
        weather_location = weather_data.get("location", "")
        
        # Check if coordinates are reasonably close (within 100km)
        spacex_lat = spacex_coords.get("latitude")
        spacex_lon = spacex_coords.get("longitude")
        weather_lat = weather_data.get("latitude")
        weather_lon = weather_data.get("longitude")
        
        if all(isinstance(x, (int, float)) for x in [spacex_lat, spacex_lon, weather_lat, weather_lon]):
            # Simple distance check (approximate)
            lat_diff = abs(spacex_lat - weather_lat)
            lon_diff = abs(spacex_lon - weather_lon)
            
            # Rough check: 1 degree ≈ 111 km
            distance_km = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111
            
            if distance_km > 100:
                anomalies.append({
                    "type": "consistency",
                    "category": "location_mismatch",
                    "severity": "warning",
                    "message": f"Location mismatch detected. SpaceX coordinates and weather location differ by approximately {distance_km:.1f} km.",
                    "spacex_location": f"{spacex_lat}, {spacex_lon}",
                    "weather_location": f"{weather_lat}, {weather_lon}",
                    "distance_km": distance_km,
                    "recommendation": "Verify that weather data corresponds to the correct launch location."
                })
    
    return anomalies

