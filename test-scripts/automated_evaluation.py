# automated_evaluation.py
# Comprehensive evaluation system for the Multi-Agent AI System

import sys
import os
sys.path.append('..')  # Add parent directory to path for imports

import json
import time
from main import run_goal
from typing import Dict, List, Any

class AgentSystemEvaluator:
    """
    Automated evaluation system for testing agent performance and goal satisfaction
    """
    
    def __init__(self, test_file: str = "evals/test_goals.json"):
        self.test_file = test_file
        self.results = []
    
    def load_test_cases(self) -> List[Dict]:
        """Load test cases from JSON file"""
        try:
            with open(self.test_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Test file {self.test_file} not found")
            return []
    
    def evaluate_goal(self, goal: str, expected_keys: List[str]) -> Dict[str, Any]:
        """
        Evaluate a single goal and check if expected data is present
        """
        print(f"\n🧪 Testing Goal: {goal}")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            result = run_goal(goal)
            execution_time = time.time() - start_time
            
            # Check if expected keys are present
            missing_keys = [key for key in expected_keys if key not in result]
            success = len(missing_keys) == 0
            
            # Get ADK validation if available
            adk_validation = result.get("adk_validation", {})
            
            evaluation = {
                "goal": goal,
                "success": success,
                "execution_time": round(execution_time, 2),
                "missing_keys": missing_keys,
                "data_keys": list(result.keys()),
                "adk_confidence": adk_validation.get("confidence", 0),
                "adk_quality_score": adk_validation.get("quality_score", 0),
                "adk_goal_achieved": adk_validation.get("goal_achieved", False),
                "result_summary": result.get("summary", "No summary"),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print(f"✅ Success: {success}")
            print(f"⏱️ Execution Time: {execution_time:.2f}s")
            print(f"🎯 ADK Confidence: {adk_validation.get('confidence', 0)}%")
            print(f"📊 Quality Score: {adk_validation.get('quality_score', 0)}%")
            
            return evaluation
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ Test failed with error: {e}")
            
            return {
                "goal": goal,
                "success": False,
                "execution_time": round(execution_time, 2),
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def run_full_evaluation(self) -> Dict[str, Any]:
        """
        Run evaluation on all test cases and generate comprehensive report
        """
        print("🚀 Starting Full Agent System Evaluation")
        print("=" * 60)
        
        test_cases = self.load_test_cases()
        if not test_cases:
            return {"error": "No test cases found"}
        
        total_start_time = time.time()
        
        for test_case in test_cases:
            goal = test_case.get("goal", "")
            expected_keys = test_case.get("expected_keys", [])
            
            evaluation = self.evaluate_goal(goal, expected_keys)
            self.results.append(evaluation)
        
        total_time = time.time() - total_start_time
        
        # Generate summary statistics
        successful_tests = [r for r in self.results if r.get("success", False)]
        success_rate = len(successful_tests) / len(self.results) * 100
        avg_confidence = sum(r.get("adk_confidence", 0) for r in successful_tests) / len(successful_tests) if successful_tests else 0
        avg_quality = sum(r.get("adk_quality_score", 0) for r in successful_tests) / len(successful_tests) if successful_tests else 0
        avg_time = sum(r.get("execution_time", 0) for r in self.results) / len(self.results)
        
        summary = {
            "total_tests": len(self.results),
            "successful_tests": len(successful_tests),
            "success_rate": round(success_rate, 2),
            "average_confidence": round(avg_confidence, 2),
            "average_quality_score": round(avg_quality, 2),
            "average_execution_time": round(avg_time, 2),
            "total_evaluation_time": round(total_time, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "detailed_results": self.results
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Success Rate: {summary['success_rate']}%")
        print(f"Average ADK Confidence: {summary['average_confidence']}%")
        print(f"Average Quality Score: {summary['average_quality_score']}%")
        print(f"Average Execution Time: {summary['average_execution_time']}s")
        print(f"Total Evaluation Time: {summary['total_evaluation_time']}s")
        
        # Save results
        self.save_results(summary)
        
        return summary
    
    def save_results(self, summary: Dict[str, Any]):
        """Save evaluation results to file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"evals/evaluation_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"💾 Results saved to {filename}")
        except Exception as e:
            print(f"⚠️ Failed to save results: {e}")

def main():
    """Run the automated evaluation"""
    evaluator = AgentSystemEvaluator()
    evaluator.run_full_evaluation()

if __name__ == "__main__":
    main()
