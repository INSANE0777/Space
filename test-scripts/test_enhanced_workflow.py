# test_enhanced_workflow.py
# Test script to demonstrate the enhanced Gemini-first workflow

import sys
import os
sys.path.append('..')  # Add parent directory to path for imports

from main import run_goal
import time

def test_workflow():
    """Test the enhanced workflow with different types of queries"""
    
    print("🧪 Testing Enhanced Multi-Agent Workflow")
    print("=" * 60)
    
    test_cases = [
        "hi",
        "what can you do",
        "get weather information",
        "find spacex launch data",
        "get spacex launch and weather data"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST CASE {i}: '{test_case}'")
        print("=" * 60)
        
        try:
            result = run_goal(test_case)
            print(f"\n✅ Test {i} completed successfully")
        except Exception as e:
            print(f"\n❌ Test {i} failed: {e}")
        
        if i < len(test_cases):
            print("\n" + "⏳ Waiting 2 seconds before next test...")
            time.sleep(2)
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    test_workflow()
