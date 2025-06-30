# main.py - Enhanced with Gemini-first workflow and lazy agent imports

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
    """
    Send message to Gemini using LangChain and get response
    """
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
    """
    Extract and format the specific output from each agent
    """
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
• Temperature: {weather_data.get('temperature', 'N/A')}°F
• Wind Speed: {weather_data.get('wind_speed', 'N/A')} mph
• Cloud Cover: {weather_data.get('clouds', 'N/A')}%
• Humidity: {weather_data.get('humidity', 'N/A')}%
• Location: {weather_data.get('location', 'N/A')}"""
        else:
            return "🌍 Weather Agent: No weather data retrieved"
    
    elif agent_name == "summary_agent":
        summary = current_data.get("summary", "")
        if summary:
            return f"📝 Summary Generated:\n{summary}"
        else:
            return "📝 Summary Agent: No summary generated"
    
    elif agent_name == "calculator_agent":
        calculation = current_data.get("calculation", {})
        if calculation.get("success"):
            calculations = calculation.get("calculations", [])
            if calculations:
                output = "🧮 Calculation Results:\n"
                for calc in calculations:
                    if calc.get("success"):
                        output += f"• {calc['expression']} = {calc['result']}\n"
                    else:
                        output += f"• {calc['expression']}: Error - {calc.get('error', 'Unknown')}\n"
                return output.strip()
            else:
                return "🧮 Calculator Agent: Calculation completed"
        else:
            return f"🧮 Calculator Agent: {calculation.get('error', 'No calculation performed')}"
    
    elif agent_name == "dictionary_agent":
        definition = current_data.get("definition", {})
        if definition.get("success"):
            word = definition.get("word", "")
            definitions = definition.get("definitions", [])
            if definitions and len(definitions) > 0:
                first_def = definitions[0]
                meanings = first_def.get("meanings", [])
                if meanings:
                    first_meaning = meanings[0].get("definitions", [])
                    if first_meaning:
                        def_text = first_meaning[0].get("definition", "")
                        return f"📖 Definition of '{word.upper()}':\n{def_text}"
            return f"📖 Dictionary Agent: Definition found for '{word}'"
        else:
            return f"📖 Dictionary Agent: {definition.get('error', 'No definition found')}"

    elif agent_name == "news_agent":
        news = current_data.get("news", {})
        if news.get("success"):
            topic = news.get("topic", "")
            articles = news.get("articles", [])
            if articles:
                output = f"📰 Latest News: {topic}\n"
                for i, article in enumerate(articles[:2], 1):
                    title = article.get('title', 'No title')
                    source = article.get('source', 'Unknown')
                    output += f"• {title} ({source})\n"
                if len(articles) > 2:
                    output += f"• ... and {len(articles) - 2} more articles"
                return output.strip()
            else:
                return f"📰 News Agent: Found news for '{topic}'"
        else:
            return f"📰 News Agent: {news.get('error', 'No news found')}"

    else:
        new_keys = set(current_data.keys()) - set(previous_data.keys())
        if new_keys:
            output = f"🔧 {agent_name} added:\n"
            for key in new_keys:
                output += f"• {key}: {current_data[key]}\n"
            return output.strip()
        else:
            return f"🔧 {agent_name}: Data processed (no new keys added)"

def run_goal(user_goal: str):
    print(f"📝 Processing request: '{user_goal}'")
    
    # Step 1: Use Gemini to determine appropriate agents
    print("\n🧠 Step 1: Consulting Gemini for agent selection...")
    
    agent_selection_prompt = """You are an intelligent agent coordinator for a multi-agent AI system.
    
    Available agents:
    - spacex_agent: Gets SpaceX launch data, schedules, and mission information
    - weather_agent: Gets weather data for specific locations (especially launch sites)
    - calculator_agent: Performs mathematical calculations and solves equations
    - dictionary_agent: Provides word definitions, meanings, and synonyms
    - news_agent: Fetches relevant news articles and current headlines
    - summary_agent: For conversational responses, greetings, and general questions
    
    Based on the user's request, determine which agents are needed. Consider:
    - For greetings/conversations: only summary_agent
    - For calculations/math (keywords: calculate, compute, solve, math): calculator_agent, summary_agent
    - For definitions (keywords: define, meaning, what is): dictionary_agent, summary_agent
    - For news/headlines (keywords: news, article, headlines, latest): news_agent, summary_agent
    - For SpaceX info only: spacex_agent, summary_agent  
    - For weather only: weather_agent, summary_agent
    - For SpaceX + weather analysis: spacex_agent, weather_agent, summary_agent
    - For SpaceX + news: spacex_agent, news_agent, summary_agent
    
    Respond with ONLY a comma-separated list of agent names in execution order.
    Example: spacex_agent, weather_agent, summary_agent"""
    
    gemini_response = get_gemini_response(user_goal, agent_selection_prompt, temperature=0.3)
    
    if gemini_response:
        sequence = [agent.strip() for agent in gemini_response.strip().split(',')]
        
        valid_agents = list(AGENT_GETTERS.keys())
        sequence = [agent for agent in sequence if agent in valid_agents]
        
        if not sequence:
            sequence = ["summary_agent"]
            
        print(f"🎯 Gemini selected agents: {sequence}")
    else:
        try:
            adk = GoogleADKCoordinator()
            sequence = adk.plan_agent_sequence(user_goal)
            print(f"🔄 Fallback ADK selected: {sequence}")
        except Exception as e:
            import agents.planner as planner
            sequence = planner.plan(user_goal)
            print(f"🔄 Fallback basic planner selected: {sequence}")

    print(f"\n⚙️ Step 2: Executing {len(sequence)} agents...")
    data = {"goal": user_goal}
    agent_outputs = {}

    for i, agent_name in enumerate(sequence, 1):
        print(f"\n🔄 [{i}/{len(sequence)}] Executing {agent_name}...")
        try:
            agent = load_agent(agent_name)
            previous_data = data.copy()
            data = agent.run(data)
            
            agent_output = extract_agent_output(agent_name, data, previous_data)
            agent_outputs[agent_name] = agent_output
            
            print(f"✅ {agent_name} completed successfully")
            print(f"📊 {agent_name} Output:")
            print("-" * 40)
            print(agent_output)
            print("-" * 40)
        except Exception as e:
            print(f"❌ {agent_name} failed: {e}")
            agent_outputs[agent_name] = f"Error: {e}"
    
    print("\n🎯 Step 3: Generating intelligent summary with Gemini...")
    
    final_summary_prompt = """You are an intelligent summarization agent for a multi-agent AI system.
    
    Your job is to analyze the collected data and create a comprehensive, helpful response for the user.
    
    Guidelines:
    - Be conversational and friendly
    - If there's technical data, explain it clearly
    - For greetings, respond naturally and offer help
    - Combine multiple data sources intelligently
    - Use emojis appropriately to make responses engaging
    - Always end with an offer to help further
    
    Create a final response that directly addresses the user's original request."""
    
    context = f"""
Original User Request: "{user_goal}"

Agents Executed: {', '.join(sequence)}

Individual Agent Outputs:
{chr(10).join([f"{name}: {output}" for name, output in agent_outputs.items()])}

Complete Data Structure:
{data}

Please create an intelligent, helpful final response for the user."""
    
    final_response = get_gemini_response(context, final_summary_prompt, temperature=0.7)
    
    print("\n" + "="*60)
    print("📋 COMPLETE EXECUTION SUMMARY")
    print("="*60)
    
    print(f"\n🎯 Original Request: '{user_goal}'")
    print(f"🤖 Agents Used: {' → '.join(sequence)}")
    
    print(f"\n📊 Individual Agent Results:")
    print("-" * 50)
    for i, (agent_name, output) in enumerate(agent_outputs.items(), 1):
        print(f"\n[{i}] {agent_name.upper()}:")
        print(output)
    
    if final_response:
        print(f"\n🎯 Final AI-Generated Response:")
        print("="*50)
        print(final_response)
        data["ai_summary"] = final_response
    else:
        print(f"\n🎯 Final Result (Fallback):")
        print("="*50)
        print(data.get("summary", "I've processed your request, but couldn't generate a detailed summary."))
    
    print("\n" + "="*60)
    return data

if __name__ == "__main__":
    goal = input("Enter your goal: ")
    run_goal(goal)
