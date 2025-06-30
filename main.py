import os
from dotenv import load_dotenv
from agents import (
    get_spacex_agent,
    get_weather_agent,
    get_summary_agent,
    get_calculator_agent,
    get_dictionary_agent,
    get_news_agent,
)
from agents.google_adk_agent import GoogleADKCoordinator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# Map agent names to lazy getters
AGENT_GETTERS = {
    "spacex_agent": get_spacex_agent,
    "weather_agent": get_weather_agent,
    "summary_agent": get_summary_agent,
    "calculator_agent": get_calculator_agent,
    "dictionary_agent": get_dictionary_agent,
    "news_agent": get_news_agent,
}

def load_agent(name: str):
    getter = AGENT_GETTERS.get(name)
    if not getter:
        raise ValueError(f"Unknown agent: {name}")
    return getter()

def get_gemini_response(user_message: str, system_prompt: str, temperature: float = 0.7) -> str:
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=temperature,
            max_tokens=1000
        )

        system_message = SystemMessage(content=system_prompt)
        human_message = HumanMessage(content=user_message)
        response = llm.invoke([system_message, human_message])
        return response.content
    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        return None

def extract_agent_output(agent_name: str, current_data: dict, previous_data: dict) -> str:
    if agent_name == "spacex_agent":
        spacex_data = current_data.get("spacex", {})
        if spacex_data:
            coordinates = spacex_data.get('coordinates', {})
            coord_str = f"{coordinates.get('name', 'Unknown')} ({coordinates.get('latitude', 'N/A')}, {coordinates.get('longitude', 'N/A')})" if coordinates else 'N/A'
            return f"""🚀 SpaceX Data Retrieved:
• Mission: {spacex_data.get('mission', 'Unknown')}
• Date: {spacex_data.get('date', 'TBD')}
• Launchpad ID: {spacex_data.get('launchpad_id', 'Unknown')}
• Location: {coord_str}"""
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

    else:
        new_keys = set(current_data.keys()) - set(previous_data.keys())
        if new_keys:
            return "🔧 Agent Output:\n" + "\n".join(f"• {k}: {current_data[k]}" for k in new_keys)
        return "🔧 Agent: Data processed (no new keys added)"

def run_goal(user_goal: str):
    print(f"📝 Processing request: '{user_goal}'")

    print("\n🧠 Step 1: Consulting Gemini for agent selection...")

    selection_prompt = """You are an intelligent agent coordinator for a multi-agent AI system.
Available agents:
- spacex_agent: Gets SpaceX launch data
- weather_agent: Gets weather data
- calculator_agent: Performs calculations
- dictionary_agent: Provides definitions
- news_agent: Fetches news
- summary_agent: Handles conversations

Rules:
- Use summary_agent always at end
- For SpaceX info: spacex_agent, summary_agent
- For SpaceX + weather: spacex_agent, weather_agent, summary_agent

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

    final_summary_prompt = """You are an AI summarizer. Use the data below to generate a clear and helpful summary for the user. Be friendly, use emojis, and give insights from the data."""

    context = f"""
User Goal: {user_goal}

Agents: {', '.join(sequence)}

Agent Outputs:
{chr(10).join(f"{k}: {v}" for k, v in agent_outputs.items())}

Data: {data}
"""

    final_response = get_gemini_response(context, final_summary_prompt, temperature=0.7)

    print("\n" + "=" * 60)
    print("📋 FINAL SUMMARY")
    print("=" * 60)
    if final_response:
        print(final_response)
        data["ai_summary"] = final_response
    else:
        print("⚠️ Summary could not be generated.")
    return data

if __name__ == "__main__":
    goal = input("Enter your goal: ")
    run_goal(goal)
