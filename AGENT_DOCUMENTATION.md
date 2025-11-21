# Agent Documentation

## Overview
This document explains how the **Satellite Data Agent** and **Anomalies Detection Agent** work in the INTOSPACE AI system.

---

## 🛰️ Satellite Data Agent

### Purpose
The Satellite Data Agent fetches real-time satellite tracking information, orbital parameters, and position data for space missions.

### How It Works

1. **Data Source Selection**:
   - **Primary**: N2YO API (if `N2YO_API_KEY` is set in environment)
   - **Fallback**: Mock data (for demonstration when API key is unavailable)

2. **Data Collection Process**:
   ```
   Input: previous_data (dict containing SpaceX launch coordinates)
   ↓
   Extract observer location (defaults to Kennedy Space Center if not available)
   ↓
   Fetch satellite positions from N2YO API (ISS by default, NORAD ID: 25544)
   ↓
   Fetch orbital parameters (TLE data)
   ↓
   Output: Updated previous_data with satellite information
   ```

3. **Data Structure Returned**:
   ```python
   {
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
       "source": "N2YO API" or "mock_data"
   }
   ```

4. **Integration with Other Agents**:
   - Uses SpaceX launch coordinates (if available) as observer location
   - Falls back to Kennedy Space Center coordinates (28.6080585, -80.6039558) if SpaceX data not available
   - Data is stored in `previous_data["satellite"]` for use by other agents

5. **Output Display**:
   - Satellite name
   - Altitude (km)
   - Velocity (km/s)
   - Orbital period (minutes)
   - Current position (latitude, longitude)

---

## 🔍 Anomalies Detection Agent

### Purpose
The Anomalies Detection Agent analyzes data from all previous agents to identify potential issues, inconsistencies, or anomalies that could affect space mission readiness.

### How It Works

1. **Analysis Process**:
   ```
   Input: previous_data (dict containing data from all previous agents)
   ↓
   Check Weather Anomalies
   ↓
   Check Launch Readiness Anomalies
   ↓
   Check Satellite Data Anomalies
   ↓
   Check Data Consistency Issues
   ↓
   Aggregate all anomalies with severity levels
   ↓
   Output: Updated previous_data with anomaly detection results
   ```

2. **Anomaly Detection Categories**:

   **a) Weather Anomalies**:
   - **Wind Speed**: Flags if > 15 m/s (warning) or > 20 m/s (critical)
   - **Cloud Cover**: Flags if > 80% (warning)
   - **Temperature**: Flags if < 0°C or > 40°C (warning)

   **b) Launch Anomalies**:
   - **Missing Data**: Checks for required fields (mission, date, coordinates)
   - **Date Format**: Validates launch date consistency

   **c) Satellite Anomalies**:
   - **Altitude**: Flags if outside normal ISS range (350-450 km)
   - **Missing Position**: Checks if position data is available

   **d) Data Consistency**:
   - **Location Mismatch**: Compares SpaceX coordinates with weather location
   - Flags if distance > 100 km between locations

3. **Severity Levels**:
   - **Critical**: Issues that could prevent launch (e.g., high wind speed > 20 m/s, launch failure)
   - **Warning**: Issues that need attention (e.g., high cloud cover, unusual altitude)
   - **Info**: Informational anomalies (e.g., missing optional data)

4. **Data Structure Returned**:
   ```python
   {
       "total_anomalies": 2,
       "critical_count": 0,
       "warning_count": 1,
       "info_count": 1,
       "status": "warning",  # or "normal" or "critical"
       "anomalies": [
           {
               "type": "weather",
               "category": "wind_speed",
               "severity": "warning",
               "message": "High wind speed detected: 18 m/s. May affect launch conditions.",
               "value": 18,
               "threshold": 15,
               "recommendation": "Monitor wind conditions closely."
           },
           # ... more anomalies
       ],
       "timestamp": "2024-01-15T10:30:00Z"
   }
   ```

5. **Integration with Other Agents**:
   - **Requires**: Data from `weather_agent`, `spacex_agent`, and `satellite_data_agent`
   - **Analyzes**: All data collected by previous agents
   - **Outputs**: Structured anomaly report with recommendations
   - **Best Practice**: Run this agent AFTER other data collection agents

6. **Output Display**:
   - Overall status (NORMAL, WARNING, CRITICAL)
   - Total anomalies count
   - Breakdown by severity (Critical, Warnings, Info)
   - List of detected issues with recommendations

---

## 🔄 Agent Execution Flow

### Typical Comprehensive Analysis Flow:

```
User Query: "Perform comprehensive space mission analysis"
↓
1. spacex_agent → Gets launch data and coordinates
↓
2. weather_agent → Gets weather at launch location (uses SpaceX coordinates)
↓
3. satellite_data_agent → Tracks ISS/satellites (uses SpaceX coordinates as observer location)
↓
4. anomalies_detection_agent → Analyzes all collected data for issues
↓
5. summary_agent → Generates human-readable summary
↓
6. Gemini AI → Final comprehensive summary (if available)
```

### Data Flow Between Agents:

```
previous_data = {"goal": "..."}
↓
spacex_agent.run(previous_data)
  → Adds: {"spacex": {...}, "coordinates": {...}}
↓
weather_agent.run(previous_data)
  → Uses: previous_data["spacex"]["coordinates"]
  → Adds: {"weather": {...}}
↓
satellite_data_agent.run(previous_data)
  → Uses: previous_data["spacex"]["coordinates"]
  → Adds: {"satellite": {...}}
↓
anomalies_detection_agent.run(previous_data)
  → Analyzes: previous_data["spacex"], previous_data["weather"], previous_data["satellite"]
  → Adds: {"anomalies": {...}}
↓
summary_agent.run(previous_data)
  → Uses: All previous data
  → Adds: {"summary": "..."}
```

---

## 🛠️ Configuration

### Environment Variables:

1. **N2YO_API_KEY** (Optional):
   - Required for real satellite data from N2YO API
   - Get free API key from: https://www.n2yo.com/api/
   - If not set, agent uses mock data

2. **GOOGLE_API_KEY** (Required for AI summaries):
   - Used by Gemini AI for final summary generation
   - If not available, system uses fallback summary

---

## 📊 Example Outputs

### Satellite Data Agent Output:
```
🛰️ Satellite Data Retrieved:
• Satellite: International Space Station (ISS)
• Altitude: 408 km
• Velocity: 7.66 km/s
• Period: 92.68 minutes
• Current Position: Lat 28.5, Lon -80.6
```

### Anomalies Detection Agent Output:
```
🔍 Anomalies Detection Results:
• Status: NORMAL
• Total Anomalies: 0
• Critical: 0
• Warnings: 0
```

Or if anomalies detected:
```
🔍 Anomalies Detection Results:
• Status: WARNING
• Total Anomalies: 2
• Critical: 0
• Warnings: 2

Detected Issues:
1. High wind speed detected: 18 m/s. May affect launch conditions. (warning)
2. High cloud cover: 85%. May affect visibility and launch conditions. (warning)
```

---

## 🚀 Usage Tips

1. **For Satellite Tracking**: Ensure `satellite_data_agent` runs after `spacex_agent` to use launch coordinates
2. **For Anomaly Detection**: Always run `anomalies_detection_agent` after data collection agents
3. **For Comprehensive Analysis**: Use all agents in sequence: spacex → weather → satellite → anomalies → summary
4. **API Keys**: Set `N2YO_API_KEY` for real satellite data, otherwise mock data is used

---

## 🔧 Troubleshooting

### Issue: "N2YO_API_KEY not set, using mock data"
- **Solution**: Set `N2YO_API_KEY` environment variable for real satellite tracking

### Issue: "Anomalies Detection Agent: detected 0 anomalies" when issues exist
- **Solution**: Check that threshold values in the agent match your requirements

### Issue: Satellite position not matching launch location
- **Solution**: This is expected - satellite position is tracked in real-time, not fixed to launch location

---

## 📝 Notes

- Mock data is used when APIs are unavailable, ensuring the system always works
- Anomaly thresholds are configurable in `agents/anomalies_detection_agent.py`
- Satellite tracking defaults to ISS (NORAD ID: 25544) but can be extended to other satellites
- All timestamps are in UTC format (ISO 8601)

