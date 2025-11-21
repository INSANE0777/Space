# Comprehensive Query Examples

## Query That Uses ALL Agents

Here's a comprehensive query that will trigger all 8 agents in the system:

---

### **Full System Query (All Agents)**

```
Perform a complete space mission intelligence analysis: Get the latest SpaceX launch details and rocket specifications, check current weather conditions and forecast at the launch location, track satellite positions and orbital data for the International Space Station, calculate the orbital velocity and escape velocity for a satellite at 400km altitude, look up the definition of "apogee" and "perigee" in space terminology, fetch the latest space news and articles about recent launches, detect any anomalies or issues in the launch readiness data including weather warnings and data inconsistencies, and provide a comprehensive summary with all findings, calculations, definitions, news updates, and actionable recommendations.
```

---

### **Alternative Shorter Version**

```
Complete space analysis: Get SpaceX launch data, weather at launch site, track ISS satellite, calculate orbital mechanics (velocity at 400km), define space terms (apogee, perigee), get latest space news, detect anomalies, and summarize everything.
```

---

### **What Each Agent Does in This Query**

1. **spacex_agent** → Fetches SpaceX launch data, rocket info, mission details
2. **weather_agent** → Gets weather conditions at launch location
3. **satellite_data_agent** → Tracks ISS and provides orbital data
4. **calculator_agent** → Calculates orbital velocity and escape velocity
5. **dictionary_agent** → Provides definitions for "apogee" and "perigee"
6. **news_agent** → Fetches latest space-related news articles
7. **anomalies_detection_agent** → Detects issues in launch readiness data
8. **summary_agent** → Generates comprehensive summary of all findings

---

### **Other Example Queries**

#### **Space Mission with Calculations**
```
Analyze the next SpaceX Starlink launch: Get launch details, calculate the delta-v required for orbit insertion at 550km altitude, check weather conditions, and summarize findings.
```

#### **Educational Space Query**
```
Explain space terminology: Define "orbital mechanics", "Hohmann transfer", and "specific impulse". Also get the latest space news and calculate escape velocity for Earth.
```

#### **Comprehensive Launch Analysis**
```
Full launch readiness check: Get SpaceX mission data, weather forecast, satellite tracking data, calculate trajectory parameters, check for anomalies, get space news updates, and provide complete analysis.
```

---

### **Tips for Using All Agents**

- **Mention calculations** → Triggers `calculator_agent`
- **Ask for definitions** → Triggers `dictionary_agent`
- **Request news** → Triggers `news_agent`
- **Ask for comprehensive analysis** → Triggers multiple agents
- **Mention specific missions** → Agent will search for that mission
- **Include anomaly detection** → Triggers `anomalies_detection_agent`

---

### **Agent Execution Order**

The system will automatically determine the best execution order, but typically:
1. Data collection agents (SpaceX, Weather, Satellite)
2. Analysis agents (Calculator, Dictionary, News)
3. Detection agents (Anomalies)
4. Summary agent (always last)

