import os
from dotenv import load_dotenv
from agents.google_adk_agent import GoogleADKCoordinator
from agent_utils import AGENT_GETTERS, load_agent, get_gemini_response

# Import real-time coordinator
try:
    from realtime_coordinator import solve_problem_realtime, RealTimeCoordinator
    REALTIME_AVAILABLE = True
except (ImportError, ValueError) as e:
    REALTIME_AVAILABLE = False
    # Warning will be shown when real-time mode is actually requested

load_dotenv()

def extract_agent_output(agent_name: str, current_data: dict, previous_data: dict) -> str:
    if agent_name == "spacex_agent":
        spacex_data = current_data.get("spacex", {})
        if spacex_data:
            coordinates = spacex_data.get('coordinates', {})
            coord_str = f"{coordinates.get('name', 'Unknown')} ({coordinates.get('latitude', 'N/A')}, {coordinates.get('longitude', 'N/A')})" if coordinates else 'N/A'
            mission = spacex_data.get('mission', 'Unknown')
            output = f"""🚀 SpaceX Data Retrieved:
• Mission: {mission}
• Date: {spacex_data.get('date', 'TBD')}
• Launchpad ID: {spacex_data.get('launchpad_id', 'Unknown')}
• Location: {coord_str}"""
            # Add note if mission search failed
            if spacex_data.get('mission_search_note'):
                output += f"\n⚠️ {spacex_data.get('mission_search_note')}"
            return output
        else:
            return "🚀 SpaceX Agent: No launch data retrieved"

    elif agent_name == "weather_agent":
        weather_data = current_data.get("weather", {})
        if weather_data:
            return f"""🌍 Weather Data Retrieved:
• Temperature: {weather_data.get('temperature', 'N/A')}°C
• Wind Speed: {weather_data.get('wind_speed', 'N/A')} m/s
• Cloud Cover: {weather_data.get('clouds', 'N/A')}%
• Humidity: {weather_data.get('humidity', 'N/A')}%
• Location: {weather_data.get('location', 'N/A')}"""
        else:
            return "🌍 Weather Agent: No weather data retrieved"

    elif agent_name == "summary_agent":
        summary = current_data.get("summary", "")
        return f"📝 Summary Generated:\n{summary}" if summary else "📝 Summary Agent: No summary generated"

    elif agent_name == "calculator_agent":
        calculation = current_data.get("calculation", {})
        if calculation.get("success"):
            calculations = calculation.get("calculations", [])
            output = "🧮 Calculation Results:\n"
            for calc in calculations:
                if calc.get("success"):
                    output += f"• {calc['expression']} = {calc['result']}\n"
                else:
                    output += f"• {calc['expression']}: Error - {calc.get('error', 'Unknown')}\n"
            return output.strip()
        return f"🧮 Calculator Agent: {calculation.get('error', 'No calculation performed')}"

    elif agent_name == "dictionary_agent":
        definition = current_data.get("definition", {})
        if definition.get("success"):
            # Handle multiple words format
            if "words" in definition and "definitions" in definition:
                # Multiple words
                words = definition.get("words", [])
                definitions_list = definition.get("definitions", [])
                output = "📖 Definitions Retrieved:\n"
                for i, (word, def_data) in enumerate(zip(words, definitions_list), 1):
                    defs = def_data.get("definitions", [])
                    if defs and defs[0].get("meanings"):
                        meanings = defs[0]["meanings"]
                        if meanings and meanings[0].get("definitions"):
                            def_text = meanings[0]["definitions"][0].get("definition", "")
                            output += f"{i}. **{word.upper()}**: {def_text}\n"
                return output.strip()
            else:
                # Single word format
                word = definition.get("word", "")
                definitions = definition.get("definitions", [])
                if definitions:
                    first_def = definitions[0]
                    meanings = first_def.get("meanings", [])
                    if meanings:
                        defs = meanings[0].get("definitions", [])
                        if defs:
                            return f"📖 Definition of '{word.upper()}':\n{defs[0].get('definition', '')}"
                return f"📖 Dictionary Agent: Definition found for '{word}'"
        return f"📖 Dictionary Agent: {definition.get('error', 'No definition found')}"

    elif agent_name == "news_agent":
        news = current_data.get("news", {})
        if news.get("success"):
            topic = news.get("topic", "")
            articles = news.get("articles", [])
            output = f"📰 Latest News: {topic}\n"
            for i, article in enumerate(articles[:2], 1):
                title = article.get('title', 'No title')
                source = article.get('source', 'Unknown')
                output += f"• {title} ({source})\n"
            if len(articles) > 2:
                output += f"• ... and {len(articles) - 2} more articles"
            return output.strip()
        return f"📰 News Agent: {news.get('error', 'No news found')}"

    elif agent_name == "satellite_data_agent":
        satellite_data = current_data.get("satellite", {})
        if satellite_data:
            satellite_name = satellite_data.get('satellite_name', 'Unknown')
            orbital_params = satellite_data.get('orbital_parameters', {})
            current_pos = satellite_data.get('current_position', {})
            output = f"🛰️ Satellite Data Retrieved:\n"
            output += f"• Satellite: {satellite_name}\n"
            
            # Check orbital parameters (handle both dict and empty dict)
            if orbital_params and isinstance(orbital_params, dict):
                altitude = orbital_params.get('altitude_km') or orbital_params.get('altitude')
                velocity = orbital_params.get('velocity_km_s') or orbital_params.get('velocity')
                period = orbital_params.get('period_minutes') or orbital_params.get('period')
                if altitude is not None:
                    output += f"• Altitude: {altitude} km\n"
                if velocity is not None:
                    output += f"• Velocity: {velocity} km/s\n"
                if period is not None:
                    output += f"• Period: {period} minutes\n"
            
            # Check current position (handle both dict and empty dict)
            if current_pos and isinstance(current_pos, dict):
                lat = current_pos.get('latitude')
                lon = current_pos.get('longitude')
                if lat is not None and lon is not None:
                    output += f"• Current Position: Lat {lat}, Lon {lon}\n"
            
            # Fallback: check if data is directly in satellite_data (if nested structure is empty)
            has_orbital_data = orbital_params and isinstance(orbital_params, dict) and \
                              (orbital_params.get('altitude_km') or orbital_params.get('altitude') or 
                               orbital_params.get('velocity_km_s') or orbital_params.get('velocity'))
            has_position_data = current_pos and isinstance(current_pos, dict) and \
                               (current_pos.get('latitude') is not None or current_pos.get('longitude') is not None)
            
            if not has_orbital_data and not has_position_data:
                # Try direct access
                altitude = satellite_data.get('altitude_km') or satellite_data.get('altitude')
                velocity = satellite_data.get('velocity_km_s') or satellite_data.get('velocity')
                period = satellite_data.get('period_minutes') or satellite_data.get('period')
                lat = satellite_data.get('latitude')
                lon = satellite_data.get('longitude')
                
                if altitude is not None:
                    output += f"• Altitude: {altitude} km\n"
                if velocity is not None:
                    output += f"• Velocity: {velocity} km/s\n"
                if period is not None:
                    output += f"• Period: {period} minutes\n"
                if lat is not None and lon is not None:
                    output += f"• Current Position: Lat {lat}, Lon {lon}\n"
            
            # Add status if available
            status = satellite_data.get('status', '')
            if status:
                output += f"• Status: {status}\n"
            
            return output.strip()
        return "🛰️ Satellite Agent: No satellite data retrieved"

    elif agent_name == "anomalies_detection_agent":
        anomalies_data = current_data.get("anomalies", {})
        if anomalies_data:
            total = anomalies_data.get('total_anomalies', 0)
            status = anomalies_data.get('status', 'unknown')
            critical = anomalies_data.get('critical_count', 0)
            warning = anomalies_data.get('warning_count', 0)
            output = f"🔍 Anomalies Detection Results:\n"
            output += f"• Status: {status.upper()}\n"
            output += f"• Total Anomalies: {total}\n"
            output += f"• Critical: {critical}\n"
            output += f"• Warnings: {warning}\n"
            anomalies_list = anomalies_data.get('anomalies', [])
            if anomalies_list:
                output += f"\nDetected Issues:\n"
                for i, anomaly in enumerate(anomalies_list[:3], 1):
                    output += f"{i}. {anomaly.get('message', 'Unknown issue')} ({anomaly.get('severity', 'unknown')})\n"
            return output.strip()
        return "🔍 Anomalies Detection Agent: No anomalies detected"

    else:
        new_keys = set(current_data.keys()) - set(previous_data.keys())
        if new_keys:
            return "🔧 Agent Output:\n" + "\n".join(f"• {k}: {current_data[k]}" for k in new_keys)
        return "🔧 Agent: Data processed (no new keys added)"

def _generate_fallback_summary(user_goal: str, agent_outputs: dict, data: dict) -> str:
    """Generate a fallback summary when Gemini API is unavailable."""
    summary_parts = [f"📋 Mission Analysis Summary for: {user_goal}\n"]
    summary_parts.append("=" * 60)
    
    # SpaceX data
    if "spacex_agent" in agent_outputs:
        summary_parts.append("\n🚀 LAUNCH INFORMATION:")
        summary_parts.append(agent_outputs["spacex_agent"])
    
    # Weather data
    if "weather_agent" in agent_outputs:
        summary_parts.append("\n🌍 WEATHER CONDITIONS:")
        summary_parts.append(agent_outputs["weather_agent"])
    
    # Satellite data
    if "satellite_data_agent" in agent_outputs:
        summary_parts.append("\n🛰️ SATELLITE TRACKING:")
        summary_parts.append(agent_outputs["satellite_data_agent"])
    
    # Anomalies
    if "anomalies_detection_agent" in agent_outputs:
        summary_parts.append("\n🔍 ANOMALY DETECTION:")
        summary_parts.append(agent_outputs["anomalies_detection_agent"])
    
    # Summary agent output
    if "summary_agent" in agent_outputs:
        summary_parts.append("\n📝 DETAILED SUMMARY:")
        summary_parts.append(agent_outputs["summary_agent"])
    
    summary_parts.append("\n" + "=" * 60)
    summary_parts.append("\n✅ Analysis complete. All agents executed successfully.")
    
    return "\n".join(summary_parts)

def run_goal(user_goal: str):
    print(f"📝 Processing request: '{user_goal}'")

    print("\n🧠 Step 1: Consulting Gemini for agent selection...")

    selection_prompt = """You are an intelligent agent coordinator for a multi-agent AI system focused on space-related queries.
Available agents:
- spacex_agent: Gets SpaceX launch data
- weather_agent: Gets weather data
- satellite_data_agent: Fetches satellite tracking and orbital data
- anomalies_detection_agent: Detects anomalies in space data and launch conditions
- calculator_agent: Performs calculations
- dictionary_agent: Provides definitions
- news_agent: Fetches news
- summary_agent: Handles conversations

Rules:
- Use summary_agent always at end
- For SpaceX info: spacex_agent, summary_agent
- For SpaceX + weather: spacex_agent, weather_agent, summary_agent
- For satellite tracking: satellite_data_agent, summary_agent
- For anomaly detection: anomalies_detection_agent (after other agents), summary_agent
- For comprehensive space analysis: spacex_agent, weather_agent, satellite_data_agent, anomalies_detection_agent, summary_agent

Return a comma-separated list like: spacex_agent, weather_agent, summary_agent"""

    gemini_response = get_gemini_response(user_goal, selection_prompt, temperature=0.3)
    sequence = []

    if gemini_response:
        sequence = [agent.strip() for agent in gemini_response.strip().split(',') if agent.strip() in AGENT_GETTERS]

        # 🧠 Auto-insert weather_agent after spacex_agent if not already in list
        if "spacex_agent" in sequence and "weather_agent" not in sequence:
            idx = sequence.index("spacex_agent")
            sequence.insert(idx + 1, "weather_agent")

        if "summary_agent" not in sequence:
            sequence.append("summary_agent")

        print(f"🎯 Gemini selected agents: {sequence}")
    else:
        try:
            adk = GoogleADKCoordinator()
            sequence = adk.plan_agent_sequence(user_goal)
        except Exception:
            import agents.planner as planner
            sequence = planner.plan(user_goal)

    print(f"\n⚙️ Step 2: Executing {len(sequence)} agents...")
    data = {"goal": user_goal}
    agent_outputs = {}

    for i, agent_name in enumerate(sequence, 1):
        print(f"\n🔄 [{i}/{len(sequence)}] Running {agent_name}...")
        try:
            agent = load_agent(agent_name)
            previous_data = data.copy()
            data = agent.run(data)
            agent_output = extract_agent_output(agent_name, data, previous_data)
            agent_outputs[agent_name] = agent_output
            print(f"✅ Output:\n{agent_output}")
        except Exception as e:
            print(f"❌ Error in {agent_name}: {e}")
            agent_outputs[agent_name] = f"Error: {e}"

    print("\n🎯 Step 3: Summarizing result with Gemini...")

    final_summary_prompt = """You are an AI summarizer for a space mission analysis system. Use the data below to generate a clear, comprehensive, and helpful summary for the user. Be friendly, use emojis appropriately, and provide actionable insights from the data. Focus on key findings, anomalies (if any), and recommendations."""

    # Create a more concise context to avoid token limits
    agent_summaries = []
    for agent_name, output in agent_outputs.items():
        # Truncate long outputs
        output_preview = output[:500] + "..." if len(output) > 500 else output
        agent_summaries.append(f"{agent_name}: {output_preview}")
    
    context = f"""
User Goal: {user_goal}

Agents Executed: {', '.join(sequence)}

Agent Results Summary:
{chr(10).join(agent_summaries)}

Key Data Points:
- SpaceX Launch: {data.get('spacex', {}).get('mission', 'N/A')}
- Weather Status: {data.get('weather', {}).get('condition', 'N/A')}
- Satellite: {data.get('satellite', {}).get('satellite_name', 'N/A')}
- Anomalies: {data.get('anomalies', {}).get('status', 'N/A')}
"""

    final_response = get_gemini_response(context, final_summary_prompt, temperature=0.7, max_tokens=2000)

    print("\n" + "=" * 60)
    print("📋 FINAL SUMMARY")
    print("=" * 60)
    if final_response:
        print(final_response)
        data["ai_summary"] = final_response
    else:
        # Fallback: Generate a basic summary from agent outputs
        print("⚠️ Gemini summary unavailable. Generating fallback summary...")
        fallback_summary = _generate_fallback_summary(user_goal, agent_outputs, data)
        print(fallback_summary)
        data["ai_summary"] = fallback_summary
    
    data["agent_outputs"] = agent_outputs
    data["agent_sequence"] = sequence
    return data

def run_goal_realtime(user_goal: str):
    """
    Run goal using real-time coordinator that breaks problems into sub-tasks
    and executes agents in parallel with solution sharing.
    Only handles space-related queries.
    """
    if not REALTIME_AVAILABLE:
        print("⚠️ Real-time coordinator not available, falling back to sequential execution")
        return run_goal(user_goal)
    
    # Space-related validation is done inside solve_problem_realtime
    return solve_problem_realtime(user_goal)

if __name__ == "__main__":
    import sys
    
    # Check if real-time mode is requested
    use_realtime = "--realtime" in sys.argv or "-r" in sys.argv
    
    goal = input("Enter your goal: ")
    
    if use_realtime:
        print("🚀 Using real-time multi-agent coordinator...")
        result = run_goal_realtime(goal)
    else:
        result = run_goal(goal)
    
    # Display summary
    if result.get("summary"):
        print("\n" + "=" * 60)
        print("📋 FINAL SUMMARY")
        print("=" * 60)
        print(result["summary"])
