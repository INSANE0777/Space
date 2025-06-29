# quick_agent_test.py
# Quick and easy way to test individual agents

import sys
import os
import importlib

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def quick_test():
    """Quick interactive agent testing"""
    
    print("🚀 Quick Agent Testing Tool")
    print("=" * 40)
    
    agents = {
        "1": "spacex_agent",
        "2": "weather_agent", 
        "3": "summary_agent",
        "4": "google_adk_agent",
        "5": "calculator_agent",
        "6": "dictionary_agent",
        "7": "news_agent"
    }
    
    print("Select an agent to test:")
    for key, name in agents.items():
        print(f"  {key}. {name}")
    print("  0. Test all agents")
    
    choice = input("\nEnter choice (0-7): ").strip()
    
    if choice == "0":
        test_all_agents()
    elif choice in agents:
        test_single_agent(agents[choice])
    else:
        print("Invalid choice!")

def test_single_agent(agent_name: str):
    """Test a single agent"""
    print(f"\n🧪 Testing {agent_name}")
    print("-" * 30)
    
    try:
        if agent_name == "spacex_agent":
            spacex_agent = importlib.import_module("agents.spacex_agent")
            result = spacex_agent.run({"goal": "Get SpaceX data"})
            
            print(f"🔍 Keys returned: {list(result.keys())}")
            
            if "spacex" in result:
                spacex_data = result["spacex"]
                print(f"✅ Mission: {spacex_data.get('mission', 'No data')}")
                print(f"📅 Date: {spacex_data.get('date', 'No data')}")
                print(f"🚀 Launchpad ID: {spacex_data.get('launchpad_id', 'No data')}")
                
                coordinates = spacex_data.get('coordinates')
                if coordinates:
                    print(f"📍 Location: {coordinates.get('name', 'Unknown')}")
                    print(f"🌍 Coordinates: {coordinates.get('latitude', 'N/A')}, {coordinates.get('longitude', 'N/A')}")
                else:
                    print("📍 No coordinates available")
            else:
                print("⚠️ No SpaceX data returned")
                print(f"   Available keys: {list(result.keys())}")
                
        elif agent_name == "weather_agent":
            weather_agent = importlib.import_module("agents.weather_agent")
            
            # Test data with coordinates
            test_data = {
                "goal": "Get weather",
                "spacex": {
                    "coordinates": {
                        "latitude": 28.6,
                        "longitude": -80.6,
                        "name": "Kennedy Space Center"
                    }
                }
            }
            result = weather_agent.run(test_data)
            
            print(f"🔍 Keys returned: {list(result.keys())}")
            
            if "weather" in result:
                weather_data = result["weather"]
                if weather_data.get("success"):
                    print(f"✅ Location: {weather_data.get('location', 'Unknown')}")
                    print(f"🌡️  Temperature: {weather_data.get('temperature', 'N/A')}°F")
                    print(f"☁️  Condition: {weather_data.get('condition', 'N/A')}")
                    print(f"💨 Wind: {weather_data.get('wind_speed', 'N/A')} mph")
                    print(f"💧 Humidity: {weather_data.get('humidity', 'N/A')}%")
                else:
                    print(f"⚠️ Weather failed: {weather_data.get('error', 'Unknown error')}")
            else:
                print("⚠️ No weather data returned")
                print(f"   Available keys: {list(result.keys())}")
                
        elif agent_name == "calculator_agent":
            calculator_agent = importlib.import_module("agents.calculator_agent")
            
            expression_input = input("Enter calculation (or press Enter for '2 + 3 * 4'): ").strip()
            if not expression_input:
                expression_input = "calculate 2 + 3 * 4"
                
            result = calculator_agent.run({"goal": expression_input})
            
            print(f"🔍 Keys returned: {list(result.keys())}")
            
            if "calculation" in result:
                calc_data = result["calculation"]
                if calc_data.get("success"):
                    expression = calc_data.get("expression", "")
                    result_value = calc_data.get("result", "")
                    print(f"✅ Expression: {expression}")
                    print(f"🔢 Result: {result_value}")
                else:
                    print(f"⚠️ Calculation failed: {calc_data.get('error', 'Unknown error')}")
            else:
                print("⚠️ No calculation data returned")
                print(f"   Available keys: {list(result.keys())}")
                
        elif agent_name == "dictionary_agent":
            dictionary_agent = importlib.import_module("agents.dictionary_agent")
            
            word_input = input("Enter word to define (or press Enter for 'serendipity'): ").strip()
            if not word_input:
                word_input = "define serendipity"
                
            result = dictionary_agent.run({"goal": word_input})
            
            print(f"🔍 Keys returned: {list(result.keys())}")
            
            if "definition" in result:
                definition = result["definition"]
                if definition.get("success"):
                    word = definition.get("word", "")
                    definitions = definition.get("definitions", [])
                    if definitions and len(definitions) > 0:
                        first_def = definitions[0]
                        print(f"✅ Definition of '{word.upper()}':")
                        
                        # Show phonetic if available
                        phonetic = first_def.get("phonetic", "")
                        if phonetic:
                            print(f"🔊 {phonetic}")
                        
                        # Show first meaning
                        meanings = first_def.get("meanings", [])
                        if meanings:
                            first_meaning = meanings[0]
                            part_of_speech = first_meaning.get("partOfSpeech", "")
                            if part_of_speech:
                                print(f"📝 Part of speech: {part_of_speech}")
                            
                            definitions_list = first_meaning.get("definitions", [])
                            if definitions_list:
                                def_text = definitions_list[0].get("definition", "")
                                example = definitions_list[0].get("example", "")
                                print(f"📖 {def_text}")
                                if example:
                                    print(f"💡 Example: {example}")
                    else:
                        print(f"✅ Definition found for '{word}'")
                else:
                    print(f"⚠️ Definition failed: {definition.get('error', 'Unknown error')}")
            else:
                print("⚠️ No definition data returned")
                print(f"   Available keys: {list(result.keys())}")
                
        elif agent_name == "news_agent":
            news_agent = importlib.import_module("agents.news_agent")
            
            topic_input = input("Enter news topic (or press Enter for 'technology'): ").strip()
            if not topic_input:
                topic_input = "get latest technology news"
                
            result = news_agent.run({"goal": topic_input})
            
            print(f"🔍 Keys returned: {list(result.keys())}")
            
            if "news" in result:
                news_data = result["news"]
                if news_data.get("success"):
                    topic = news_data.get("topic", "")
                    articles = news_data.get("articles", [])
                    print(f"✅ Found {len(articles)} articles for '{topic}'")
                    
                    if articles:
                        # Show first article
                        first_article = articles[0]
                        print(f"📰 Latest: {first_article.get('title', 'No title')}")
                        print(f"📝 {first_article.get('description', 'No description')[:100]}...")
                        print(f"📰 Source: {first_article.get('source', 'Unknown')}")
                    else:
                        print(f"⚠️ No articles found for '{topic}'")
                else:
                    print(f"⚠️ News search failed: {news_data.get('error', 'Unknown error')}")
            else:
                print("⚠️ No news data returned")
                print(f"   Available keys: {list(result.keys())}")
                
        elif agent_name == "summary_agent":
            summary_agent = importlib.import_module("agents.summary_agent")
            result = summary_agent.run({"goal": "test summary"})
            
            print(f"🔍 Keys returned: {list(result.keys())}")
            
            if "summary" in result:
                print(f"✅ Summary: {result['summary']}")
            else:
                print("⚠️ No summary data returned")
                print(f"   Available keys: {list(result.keys())}")
                
        elif agent_name == "google_adk_agent":
            google_adk_agent = importlib.import_module("agents.google_adk_agent")
            coordinator = google_adk_agent.GoogleADKCoordinator()
            sequence = coordinator.plan_agent_sequence("test goal")
            print(f"✅ Agent sequence: {sequence}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"   Details: {traceback.format_exc()}")

def test_all_agents():
    """Test all agents quickly"""
    
    print("\n🔄 Testing All Agents")
    print("=" * 30)
    
    agents = [
        ("SpaceX", "agents.spacex_agent", {"goal": "Get SpaceX data"}),
        ("Weather", "agents.weather_agent", {
            "goal": "Get weather",
            "spacex": {"coordinates": {"latitude": 28.6, "longitude": -80.6, "name": "Test"}}
        }),
        ("Calculator", "agents.calculator_agent", {"goal": "calculate 2 + 3"}),
        ("Dictionary", "agents.dictionary_agent", {"goal": "define test"}),
        ("News", "agents.news_agent", {"goal": "get latest technology news"}),
        ("Summary", "agents.summary_agent", {"goal": "hi"}),
    ]
    
    results = []
    
    for name, module_name, test_data in agents:
        try:
            module = importlib.import_module(module_name)
            result = module.run(test_data)
            print(f"✅ {name}: OK")
            results.append(True)
        except Exception as e:
            print(f"❌ {name}: {e}")
            results.append(False)
    
    # Test ADK separately
    try:
        google_adk_agent = importlib.import_module("agents.google_adk_agent")
        adk = google_adk_agent.GoogleADKCoordinator()
        sequence = adk.plan_agent_sequence("test goal")
        print(f"✅ Google ADK: OK")
        results.append(True)
    except Exception as e:
        print(f"❌ Google ADK: {e}")
        results.append(False)
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} agents working")

if __name__ == "__main__":
    quick_test()
