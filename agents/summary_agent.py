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

    # Detect greeting/help queries
    is_greeting = any(kw in user_goal for kw in greetings_keywords)

    if is_greeting:
        summary_text = (
            "👋 Hello! I'm your multi-agent AI assistant. "
            "I can help you with things like:\n"
            "• Getting the latest SpaceX launch info 🚀\n"
            "• Checking weather conditions at launch sites 🌤️\n"
            "• Performing calculations and solving math problems 🧮\n"
            "• Looking up word definitions and meanings 📖\n"
            "• Fetching the latest news headlines 📰\n\n"
            "Just ask me anything related to these topics, and I'll do my best to help! "
            "What would you like to do today?"
        )
        data['summary'] = summary_text
        return data

    # Check if SpaceX or Weather data present
    mission = spacex.get('mission')
    date = spacex.get('date')
    launchpad_id = spacex.get('launchpad_id')
    location_name = weather.get('location')

    if not any([mission, date, launchpad_id, location_name]):
        # No data available fallback
        data['summary'] = (
            "🤔 I currently don't have any SpaceX launch or weather data available. "
            "Please try again later or ask about something else I can help with."
        )
        return data

    # Generate detailed summary combining SpaceX and Weather info
    data['summary'] = generate_detailed_summary(spacex, weather)
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
        summary_lines.append(f"- Temperature: {temperature}°F")
    else:
        summary_lines.append("- Temperature data not available")

    if wind_speed is not None:
        summary_lines.append(f"- Wind speed: {wind_speed} mph")
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

    # Analyze potential delay factors
    delay_reasons = []
    if temperature is not None and temperature < 32:
        delay_reasons.append("chilly temperature 🥶")
    if wind_speed is not None and wind_speed > 20:
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


if __name__ == "__main__":
    # Simple local test
    test_data = {
        "goal": "Hello, help me understand what you can do",
        "spacex": {},
        "weather": {}
    }
    print(run(test_data)['summary'])
