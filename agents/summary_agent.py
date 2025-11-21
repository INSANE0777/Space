# summary_agent.py

def run(data):
    """
    Generate a summary based on available data:
    - Friendly greeting/help message for casual queries
    - Detailed SpaceX + weather launch summary when data present
    - Polite fallback when no relevant data found
    """

    spacex = data.get('spacex', {})
    weather = data.get('weather', {})
    user_goal = data.get('goal', '').lower()

    greetings_keywords = ['hello', 'hi', 'help', 'what can you do', 'introduce', 'how are you']

    # Detect greeting/help queries - but only if it's a simple greeting, not a complex query
    is_greeting = any(kw in user_goal for kw in greetings_keywords) and len(user_goal.split()) < 10

    if is_greeting:
        summary_text = (
            "👋 Hello! I'm your space-focused multi-agent AI assistant. 🚀\n\n"
            "I specialize in SPACE-RELATED queries and can help you with:\n"
            "• Getting the latest SpaceX launch info and mission details 🚀\n"
            "• Checking weather conditions at launch sites (Kennedy Space Center, etc.) 🌤️\n"
            "• Performing space-related calculations (trajectories, velocities, orbital mechanics) 🧮\n"
            "• Fetching the latest space news and articles 📰\n"
            "• Analyzing launch readiness and mission data 📊\n\n"
            "⚠️ Note: I only handle space-related queries (SpaceX, rockets, launches, missions, satellites, etc.)\n\n"
            "What space-related question can I help you with today? 🌌"
        )
        data['summary'] = summary_text
        return data

    # Check for data from all agents
    mission = spacex.get('mission')
    date = spacex.get('date')
    launchpad_id = spacex.get('launchpad_id')
    location_name = weather.get('location')
    calculation = data.get('calculation', {})
    definition = data.get('definition', {})
    news = data.get('news', {})

    # Check if we have multi-agent data (calculator, dictionary, news, etc.)
    has_multi_agent_data = (
        calculation.get('success') or 
        definition.get('success') or 
        news.get('success')
    )

    # Handle weather-only case
    if location_name and not any([mission, date, launchpad_id]) and not has_multi_agent_data:
        data['summary'] = generate_weather_only_summary(weather)
        return data

    if not any([mission, date, launchpad_id, location_name]) and not has_multi_agent_data:
        # Check if this is a space-related query
        goal_lower = user_goal.lower()
        space_keywords = ["spacex", "space", "rocket", "launch", "mission", "satellite", "orbit", 
                         "astronaut", "nasa", "mars", "moon", "lunar", "stellar", "galaxy"]
        is_space_query = any(kw in goal_lower for kw in space_keywords)
        
        if is_space_query:
            # Space-related query but no data
            data['summary'] = (
                "🚀 I'm a space-focused assistant, but I couldn't retrieve the requested space data. "
                "This might be due to:\n"
                "• API connectivity issues\n"
                "• The requested launch/mission not being available\n"
                "• Network problems\n\n"
                "Please try again or ask about a different space-related topic."
            )
        else:
            # Non-space query
            data['summary'] = (
                "⚠️ This system only handles space-related queries (SpaceX, rockets, launches, missions, etc.).\n\n"
                "Please ask about:\n"
                "• SpaceX launches and missions\n"
                "• Rocket launches and trajectories\n"
                "• Space missions and satellites\n"
                "• Launch weather conditions\n"
                "• Space-related calculations"
            )
        return data

    # Generate comprehensive summary with all available data
    data['summary'] = generate_comprehensive_summary(spacex, weather, calculation, definition, news)
    return data


def generate_detailed_summary(spacex, weather):
    # Extract SpaceX info
    mission = spacex.get('mission', 'Unknown mission')
    date = spacex.get('date', 'Unknown date/time')
    launchpad_id = spacex.get('launchpad_id', 'Unknown launchpad')
    coordinates = spacex.get('coordinates', {})
    loc_name = coordinates.get('name', 'Unknown location')
    lat = coordinates.get('latitude', 'N/A')
    lon = coordinates.get('longitude', 'N/A')

    # Extract weather info
    temperature = weather.get('temperature', None)
    wind_speed = weather.get('wind_speed', None)
    cloud_cover = weather.get('clouds', None)
    humidity = weather.get('humidity', None)

    # Build summary string
    summary_lines = [
        f"🚀 Upcoming SpaceX Mission: **{mission}**",
        f"📅 Scheduled Launch Date & Time (UTC): {date}",
        f"📍 Launchpad: {launchpad_id} at {loc_name} ({lat}, {lon})",
        "🌤️ Weather Forecast at Launch Site:"
    ]

    if temperature is not None:
        # Temperature is in Celsius from weather agent
        temp_f = (temperature * 9/5) + 32
        summary_lines.append(f"- Temperature: {temperature}°C ({temp_f:.1f}°F)")
    else:
        summary_lines.append("- Temperature data not available")

    if wind_speed is not None:
        # Wind speed is in m/s from weather agent
        wind_mph = wind_speed * 2.237
        summary_lines.append(f"- Wind speed: {wind_speed} m/s ({wind_mph:.1f} mph)")
    else:
        summary_lines.append("- Wind speed data not available")

    if cloud_cover is not None:
        summary_lines.append(f"- Cloud cover: {cloud_cover}%")
    else:
        summary_lines.append("- Cloud cover data not available")

    if humidity is not None:
        summary_lines.append(f"- Humidity: {humidity}%")
    else:
        summary_lines.append("- Humidity data not available")

    # Analyze potential delay factors (using correct units: °C and m/s)
    delay_reasons = []
    if temperature is not None and temperature < 0:
        delay_reasons.append("freezing temperature 🥶")
    elif temperature is not None and temperature < 10:
        delay_reasons.append("chilly temperature 🥶")
    if wind_speed is not None and wind_speed > 10:  # > 10 m/s = > 22.4 mph (high wind)
        delay_reasons.append("high wind speed 🌬️")
    if cloud_cover is not None and cloud_cover > 70:
        delay_reasons.append("significant cloud cover ☁️")
    if humidity is not None and humidity > 80:
        delay_reasons.append("high humidity 💧")

    if delay_reasons:
        delay_msg = "Considering the weather factors like " + ", ".join(delay_reasons) + \
                    ", there might be a possibility of a launch delay. 🚧"
    else:
        delay_msg = "Weather conditions currently look favorable for the launch with no significant delay risks detected. ✅"

    summary_lines.append("")
    summary_lines.append(delay_msg)
    summary_lines.append("🔍 Note: SpaceX’s final launch decision depends on multiple technical and safety factors beyond weather conditions. For the most accurate updates, please check official SpaceX channels closer to launch time. 🚀")
    summary_lines.append("")
    summary_lines.append("If you'd like, I can help track the launch or provide more details about the mission. Just ask!")

    return "\n".join(summary_lines)


def generate_weather_only_summary(weather):
    """Generate summary when only weather data is available"""
    location_name = weather.get('location', 'Unknown location')
    temperature = weather.get('temperature', None)
    wind_speed = weather.get('wind_speed', None)
    cloud_cover = weather.get('clouds', None)
    humidity = weather.get('humidity', None)
    condition = weather.get('condition', 'Unknown condition')
    
    summary_lines = [
        f"🌤️ Weather Conditions at {location_name}:",
        ""
    ]
    
    if temperature is not None:
        temp_f = (temperature * 9/5) + 32
        summary_lines.append(f"• Temperature: {temperature}°C ({temp_f:.1f}°F)")
    if wind_speed is not None:
        wind_mph = wind_speed * 2.237
        summary_lines.append(f"• Wind Speed: {wind_speed} m/s ({wind_mph:.1f} mph)")
    if cloud_cover is not None:
        summary_lines.append(f"• Cloud Cover: {cloud_cover}%")
    if humidity is not None:
        summary_lines.append(f"• Humidity: {humidity}%")
    if condition:
        summary_lines.append(f"• Condition: {condition}")
    
    summary_lines.append("")
    
    # Analyze conditions
    if temperature is not None and wind_speed is not None and cloud_cover is not None:
        if temperature > 15 and wind_speed < 10 and cloud_cover < 30:
            summary_lines.append("✅ Weather conditions look favorable for rocket launches with clear skies, moderate temperatures, and light winds.")
        else:
            summary_lines.append("⚠️ Weather conditions may need monitoring for launch operations.")
    
    return "\n".join(summary_lines)


def generate_comprehensive_summary(spacex, weather, calculation, definition, news):
    """Generate a comprehensive summary combining data from all agents"""
    summary_lines = []
    
    # SpaceX data
    if spacex.get('mission') or spacex.get('date'):
        mission = spacex.get('mission', 'Unknown mission')
        date = spacex.get('date', 'Unknown date/time')
        coordinates = spacex.get('coordinates', {})
        loc_name = coordinates.get('name', 'Unknown location')
        
        summary_lines.append(f"🚀 SpaceX Mission: **{mission}**")
        summary_lines.append(f"📅 Launch Date & Time (UTC): {date}")
        summary_lines.append(f"📍 Launchpad: {loc_name}")
        summary_lines.append("")
    
    # Weather data
    if weather.get('location'):
        temp = weather.get('temperature')
        wind = weather.get('wind_speed')
        clouds = weather.get('clouds')
        humidity = weather.get('humidity')
        
        summary_lines.append("🌤️ Weather Conditions:")
        if temp is not None:
            temp_f = (temp * 9/5) + 32
            summary_lines.append(f"- Temperature: {temp}°C ({temp_f:.1f}°F)")
        if wind is not None:
            wind_mph = wind * 2.237
            summary_lines.append(f"- Wind Speed: {wind} m/s ({wind_mph:.1f} mph)")
        if clouds is not None:
            summary_lines.append(f"- Cloud Cover: {clouds}%")
        if humidity is not None:
            summary_lines.append(f"- Humidity: {humidity}%")
        summary_lines.append("")
    
    # Calculation data
    if calculation.get('success'):
        calcs = calculation.get('calculations', [])
        for calc in calcs:
            if calc.get('success'):
                expr = calc.get('expression', '')
                result = calc.get('result', '')
                unit = calc.get('unit', '')
                explanation = calc.get('explanation', '')
                
                summary_lines.append(f"🧮 Calculation: {expr}")
                summary_lines.append(f"   Result: {result} {unit}".strip())
                if explanation:
                    summary_lines.append(f"   {explanation}")
                summary_lines.append("")
    
    # Definition data
    if definition.get('success'):
        word = definition.get('word', '')
        definitions = definition.get('definitions', [])
        if definitions and definitions[0].get('meanings'):
            meanings = definitions[0]['meanings']
            if meanings and meanings[0].get('definitions'):
                def_text = meanings[0]['definitions'][0].get('definition', '')
                summary_lines.append(f"📖 Definition of '{word}':")
                summary_lines.append(f"   {def_text}")
                summary_lines.append("")
    
    # News data
    if news.get('success'):
        topic = news.get('topic', '')
        articles = news.get('articles', [])
        summary_lines.append(f"📰 Latest News: {topic}")
        for article in articles[:3]:
            title = article.get('title', '') if isinstance(article, dict) else str(article)
            # Handle source - could be dict or string
            source_obj = article.get('source', '') if isinstance(article, dict) else ''
            if isinstance(source_obj, dict):
                source = source_obj.get('name', 'Unknown')
            elif isinstance(source_obj, str):
                source = source_obj
            else:
                source = 'Unknown'
            summary_lines.append(f"   • {title} ({source})")
        summary_lines.append("")
    
    # Final note
    summary_lines.append("✨ This comprehensive summary combines data from multiple specialized agents to provide you with complete information.")
    
    return "\n".join(summary_lines)


if __name__ == "__main__":
    # Simple local test
    test_data = {
        "goal": "Hello, help me understand what you can do",
        "spacex": {},
        "weather": {}
    }
    print(run(test_data)['summary'])
