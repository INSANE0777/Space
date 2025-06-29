# test_system.py
# Script to test the multi-agent system automatically

import os
import sys
sys.path.append('..')  # Add parent directory to path for imports

from main import run_goal

def test_spacex_weather_goal():
    """Test the SpaceX + Weather goal"""
    print("=" * 50)
    print("🧪 TESTING: SpaceX + Weather Goal")
    print("=" * 50)
    
    goal = "Find the next SpaceX launch, check weather at that location, and summarize if it may be delayed"
    
    try:
        result = run_goal(goal)
        print("✅ Test completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_spacex_weather_goal()
