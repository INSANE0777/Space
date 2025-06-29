# test_langchain_integration.py
# Test script to verify LangChain integration with Google ADK Agent

import sys
import os
sys.path.append('..')  # Add parent directory to path for imports

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_langchain_integration():
    """Test the LangChain integration with GoogleADKCoordinator"""
    
    print("🧪 Testing LangChain Integration with Google ADK Agent")
    print("=" * 60)
    
    # Test 1: Import and initialization
    print("\n1. Testing imports and initialization...")
    try:
        from agents.google_adk_agent import GoogleADKCoordinator
        print("✅ Successfully imported GoogleADKCoordinator")
        
        # Check if API key is available
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found - skipping LangChain tests")
            return
        
        adk = GoogleADKCoordinator()
        print("✅ Successfully initialized GoogleADKCoordinator with LangChain")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Test 2: Test planning functionality
    print("\n2. Testing agent planning...")
    test_goals = [
        "Hi there!",  # Conversational
        "Get SpaceX launch info",  # SpaceX only
        "What's the weather?",  # Weather only
        "Get SpaceX launches and weather data"  # Both
    ]
    
    for goal in test_goals:
        try:
            sequence = adk.plan_agent_sequence(goal)
            print(f"✅ Goal: '{goal}' -> Sequence: {sequence}")
        except Exception as e:
            print(f"❌ Failed planning for '{goal}': {e}")
    
    # Test 3: Test validation functionality
    print("\n3. Testing goal validation...")
    try:
        mock_data = {
            "goal": "Get weather information",
            "weather_data": {"temperature": "22°C", "location": "Cape Canaveral"},
            "summary": "Current weather is 22°C at Cape Canaveral"
        }
        
        validation = adk.validate_goal_completion("Get weather information", mock_data)
        print(f"✅ Validation result: {validation}")
    except Exception as e:
        print(f"❌ Failed validation: {e}")
    
    print("\n🎉 LangChain integration testing completed!")

if __name__ == "__main__":
    test_langchain_integration()
