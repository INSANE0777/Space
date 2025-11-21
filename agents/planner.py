# agents/planner.py

def plan(user_goal: str) -> list:
    """
    Enhanced planner that can handle more goal variations.
    This serves as a fallback when Google ADK is not available.
    """
    goal_lower = user_goal.lower().strip()
    
    # Handle conversational inputs (greetings, simple questions)
    conversational_patterns = [
        "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
        "how are you", "what's up", "what can you do", "help", "what are you",
        "who are you", "thanks", "thank you", "bye", "goodbye", "ok", "okay"
    ]
    
    if any(pattern in goal_lower for pattern in conversational_patterns) or len(goal_lower.split()) <= 3:
        return ["summary_agent"]  # Use summary agent for conversational responses
    
    # Comprehensive space analysis pattern
    if any(keyword in goal_lower for keyword in ["comprehensive", "full", "complete", "analyze", "detect", "anomaly"]):
        return ["spacex_agent", "weather_agent", "satellite_data_agent", "anomalies_detection_agent", "summary_agent"]
    
    # SpaceX + Weather + Satellite pattern
    if any(keyword in goal_lower for keyword in ["spacex", "launch", "rocket"]) and \
       any(keyword in goal_lower for keyword in ["weather", "climate", "condition"]) and \
       any(keyword in goal_lower for keyword in ["satellite", "orbital", "tracking"]):
        return ["spacex_agent", "weather_agent", "satellite_data_agent", "anomalies_detection_agent", "summary_agent"]
    
    # SpaceX + Weather + Anomalies pattern
    if any(keyword in goal_lower for keyword in ["spacex", "launch", "rocket"]) and \
       any(keyword in goal_lower for keyword in ["weather", "climate", "condition"]) and \
       any(keyword in goal_lower for keyword in ["anomaly", "detect", "issue", "problem", "check"]):
        return ["spacex_agent", "weather_agent", "anomalies_detection_agent", "summary_agent"]
    
    # SpaceX + Weather pattern
    if any(keyword in goal_lower for keyword in ["spacex", "launch", "rocket"]) and \
       any(keyword in goal_lower for keyword in ["weather", "climate", "condition"]):
        return ["spacex_agent", "weather_agent", "anomalies_detection_agent", "summary_agent"]
    
    # Satellite pattern
    elif any(keyword in goal_lower for keyword in ["satellite", "orbital", "tracking", "iss", "space station", "orbit"]):
        return ["spacex_agent", "satellite_data_agent", "summary_agent"]
    
    # Anomalies detection pattern
    elif any(keyword in goal_lower for keyword in ["anomaly", "anomalies", "detect", "issue", "problem", "error", "warning"]):
        return ["spacex_agent", "weather_agent", "anomalies_detection_agent", "summary_agent"]
    
    # Weather only pattern  
    elif any(keyword in goal_lower for keyword in ["weather", "temperature", "climate", "forecast"]):
        return ["weather_agent", "summary_agent"]
        
    # SpaceX only pattern
    elif any(keyword in goal_lower for keyword in ["spacex", "launch", "rocket", "mission"]):
        return ["spacex_agent", "anomalies_detection_agent", "summary_agent"]
        
    # News pattern
    elif any(keyword in goal_lower for keyword in ["news", "article", "current events"]):
        return ["news_agent", "summary_agent"]
    
    # Default: try a comprehensive approach
    else:
        print("⚠️ Goal pattern not recognized, trying comprehensive agent sequence")
        return ["spacex_agent", "weather_agent", "satellite_data_agent", "anomalies_detection_agent", "summary_agent"]
