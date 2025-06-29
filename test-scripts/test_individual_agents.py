# test_individual_agents.py
# Comprehensive individual agent testing script

import sys
import time
import os
sys.path.append('..')  # Add parent directory to path for imports

def test_spacex_agent():
    """Test SpaceX agent individually"""
    print("🧪 Testing SpaceX Agent")
    print("-" * 40)
    
    # Import the agent
    from agents import spacex_agent
    
    # Create test data
    test_data = {"goal": "Get SpaceX launch data"}
    
    try:
        # Run the agent
        start_time = time.time()
        result = spacex_agent.run(test_data)
        end_time = time.time()
        
        # Display results
        print("✅ SpaceX Agent Test Results:")
        print(f"⏱️ Execution time: {end_time - start_time:.3f} seconds")        
        print(f"📊 Data returned: {list(result.keys())}")
        
        if "spacex" in result:
            spacex_data = result["spacex"]
            coordinates = spacex_data.get("coordinates", {})
            
            print(f"🚀 Mission: {spacex_data.get('mission', 'Unknown')}")
            print(f"📅 Date: {spacex_data.get('date', 'TBD')}")
            print(f"🚀 Launchpad ID: {spacex_data.get('launchpad_id', 'Unknown')}")
            
            if coordinates:
                print(f"🌍 Coordinates: {coordinates.get('latitude', 'N/A')}, {coordinates.get('longitude', 'N/A')}")
                print(f"📍 Location: {coordinates.get('name', 'N/A')}")
        else:
            print("⚠️ No SpaceX data in result")
        
        return True, result
    except Exception as e:
        print(f"❌ SpaceX Agent Test Failed: {e}")
        return False, None

def test_weather_agent(spacex_data=None):
    """Test Weather agent individually"""
    print("\n🧪 Testing Weather Agent")
    print("-" * 40)
    
    from agents import weather_agent
    
    # Create test data with coordinates
    if spacex_data and "spacex_data" in spacex_data:
        # Use real coordinates from SpaceX agent
        test_data = {
            "goal": "Get weather data",
            "spacex": spacex_data["spacex_data"]
        }
        print("🔗 Using coordinates from SpaceX agent")
    else:
        # Use mock coordinates
        test_data = {
            "goal": "Get weather data",
            "spacex": {
                "coordinates": {
                    "latitude": 28.6080585,
                    "longitude": -80.6039558,
                    "name": "KSC LC 39A"
                }
            }
        }
        print("🎭 Using mock coordinates")
    
    try:
        start_time = time.time()
        result = weather_agent.run(test_data)
        end_time = time.time()
        
        print("✅ Weather Agent Test Results:")
        print(f"⏱️ Execution time: {end_time - start_time:.3f} seconds")
        print(f"📊 Data returned: {list(result.keys())}")
        
        if "weather" in result:
            weather = result["weather"]
            print(f"🌡️ Temperature: {weather.get('temperature', 'N/A')}°F")
            print(f"💨 Wind Speed: {weather.get('wind_speed', 'N/A')} mph")
            print(f"☁️ Cloud Cover: {weather.get('clouds', 'N/A')}%")
            print(f"💧 Humidity: {weather.get('humidity', 'N/A')}%")
            print(f"📍 Location: {weather.get('location', 'N/A')}")
        else:
            print("⚠️ No weather data in result")
        
        return True, result
    except Exception as e:
        print(f"❌ Weather Agent Test Failed: {e}")
        return False, None

def test_summary_agent(combined_data=None):
    """Test Summary agent individually"""
    print("\n🧪 Testing Summary Agent")
    print("-" * 40)
    
    from agents import summary_agent
    
    # Test different types of inputs
    test_cases = [
        ("Conversational", {"goal": "hi there"}),
        ("Help Request", {"goal": "what can you do"}),
        ("Data Analysis", combined_data or {"goal": "analyze the data"})
    ]
    
    results = []
    
    for test_name, test_data in test_cases:
        print(f"\n🔍 Testing: {test_name}")
        print("  " + "-" * 30)
        
        try:
            start_time = time.time()
            result = summary_agent.run(test_data)
            end_time = time.time()
            
            print(f"  ✅ Success - {end_time - start_time:.3f}s")
            if "summary" in result:
                summary = result["summary"]
                preview = summary[:100] + "..." if len(summary) > 100 else summary
                print(f"  📝 Summary: {preview}")
            
            results.append((True, result))
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results.append((False, None))
    
    return results

def test_google_adk_agent():
    """Test Google ADK agent individually"""
    print("\n🧪 Testing Google ADK Agent")
    print("-" * 40)
    
    try:
        from agents.google_adk_agent import GoogleADKCoordinator
        
        adk = GoogleADKCoordinator()
        
        # Test planning
        test_goals = [
            "hi there",
            "get spacex data",
            "check weather",
            "spacex launch and weather analysis"
        ]
        
        print("🧠 Testing Agent Planning:")
        for goal in test_goals:
            try:
                start_time = time.time()
                sequence = adk.plan_agent_sequence(goal)
                end_time = time.time()
                
                print(f"  📝 '{goal}' -> {sequence} ({end_time - start_time:.3f}s)")
            except Exception as e:
                print(f"  ❌ '{goal}' -> Error: {e}")
        
        # Test validation
        print("\n🔍 Testing Goal Validation:")
        mock_data = {
            "goal": "test validation",
            "weather": {"temperature": 72, "wind_speed": 8},
            "summary": "Test completed successfully"
        }
        
        try:
            start_time = time.time()
            validation = adk.validate_goal_completion("test validation", mock_data)
            end_time = time.time()
            
            print(f"  ✅ Validation completed ({end_time - start_time:.3f}s)")
            print(f"  🎯 Goal Achieved: {validation.get('goal_achieved', 'Unknown')}")
            print(f"  📊 Confidence: {validation.get('confidence', 0)}%")
            print(f"  ⭐ Quality Score: {validation.get('quality_score', 0)}%")
            
        except Exception as e:
            print(f"  ❌ Validation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Google ADK Agent Test Failed: {e}")
        return False

def run_integration_test():
    """Test how agents work together"""
    print("\n🔗 Testing Agent Integration")
    print("=" * 50)
    
    # Step 1: Get SpaceX data
    spacex_success, spacex_result = test_spacex_agent()
    
    # Step 2: Get weather data (using SpaceX coordinates if available)
    weather_success, weather_result = test_weather_agent(spacex_result)
    
    # Step 3: Create combined data for summary
    combined_data = {"goal": "analyze spacex and weather data"}
    if spacex_result:
        combined_data.update(spacex_result)
    if weather_result:
        combined_data.update(weather_result)
    
    # Step 4: Test summary with combined data
    summary_results = test_summary_agent(combined_data)
    
    # Step 5: Test ADK coordination
    adk_success = test_google_adk_agent()
    
    return {
        "spacex": spacex_success,
        "weather": weather_success,
        "summary": all(result[0] for result in summary_results),
        "adk": adk_success
    }

def main():
    """Main testing function"""
    print("🔬 Individual Agent Testing Suite")
    print("=" * 60)
    print("This script tests each agent individually and their integration")
    print("=" * 60)
    
    # Run all tests
    results = run_integration_test()
    
    # Display final summary
    print("\n📊 Final Test Summary")
    print("=" * 40)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for agent, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{agent.upper():.<20} {status}")
    
    print("-" * 40)
    print(f"TOTAL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All agent tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
