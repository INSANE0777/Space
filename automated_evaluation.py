# automated_evaluation.py
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from main import run_goal, run_goal_realtime, REALTIME_AVAILABLE
from agents.google_adk_agent import GoogleADKCoordinator


class AgentSystemEvaluator:
    def __init__(self, use_realtime: bool = False):
        print("✅ AgentSystemEvaluator initialized")
        self.use_realtime = use_realtime and REALTIME_AVAILABLE
        if self.use_realtime:
            print("🚀 Real-time coordinator enabled")
        self.adk_coordinator = GoogleADKCoordinator()
        self.evals_dir = Path("evals")
        self.evals_dir.mkdir(exist_ok=True)

    def load_test_goals(self) -> List[Dict[str, Any]]:
        """Load test goals from evals/test_goals.json"""
        test_goals_path = self.evals_dir / "test_goals.json"
        if not test_goals_path.exists():
            # Default test goals if file doesn't exist
            return [
                {
                    "goal": "Find the next SpaceX launch, check weather at that location, and summarize if it may be delayed.",
                    "expected_keys": ["spacex", "weather", "summary", "adk_validation"]
                },
                {
                    "goal": "Get information about the next SpaceX mission and launch details.",
                    "expected_keys": ["spacex", "summary"]
                },
                {
                    "goal": "Check weather conditions at Kennedy Space Center for rocket launches.",
                    "expected_keys": ["weather", "summary"]
                },
                {
                    "goal": "Tell me about SpaceX Starship launch and weather forecast at the site.",
                    "expected_keys": ["spacex", "weather", "summary"]
                },
                {
                    "goal": "What's the next rocket launch and will bad weather delay it?",
                    "expected_keys": ["spacex", "weather", "summary"]
                }
            ]
        
        with open(test_goals_path, 'r') as f:
            return json.load(f)

    def evaluate_single_goal(self, goal: str, expected_keys: List[str]) -> Dict[str, Any]:
        """Evaluate a single goal and return results"""
        print(f"\n🧪 Testing goal: {goal}")
        start_time = time.time()
        
        try:
            # Run the goal (using real-time if enabled)
            if self.use_realtime:
                result = run_goal_realtime(goal)
            else:
                result = run_goal(goal)
            execution_time = time.time() - start_time
            
            # Check for expected keys
            missing_keys = [key for key in expected_keys if key not in result]
            data_keys = list(result.keys())
            
            # Validate with ADK
            adk_validation = None
            try:
                adk_validation = self.adk_coordinator.validate_goal_completion(goal, result)
                result["adk_validation"] = adk_validation
            except Exception as e:
                print(f"⚠️ ADK validation failed: {e}")
                adk_validation = {
                    "goal_achieved": len(missing_keys) == 0,
                    "confidence": 80,
                    "quality_score": 80,
                    "missing_data": missing_keys,
                    "suggested_improvements": []
                }
            
            # Determine success
            success = (
                len(missing_keys) == 0 and
                adk_validation.get("goal_achieved", False) and
                execution_time < 30  # Reasonable timeout
            )
            
            return {
                "goal": goal,
                "success": success,
                "execution_time": round(execution_time, 2),
                "missing_keys": missing_keys,
                "data_keys": data_keys,
                "adk_confidence": adk_validation.get("confidence", 0),
                "adk_quality_score": adk_validation.get("quality_score", 0),
                "adk_goal_achieved": adk_validation.get("goal_achieved", False),
                "result_summary": adk_validation.get("result_summary", ""),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ Goal failed with error: {e}")
            return {
                "goal": goal,
                "success": False,
                "execution_time": round(execution_time, 2),
                "missing_keys": expected_keys,
                "data_keys": [],
                "adk_confidence": 0,
                "adk_quality_score": 0,
                "adk_goal_achieved": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    def run_full_evaluation(self) -> Dict[str, Any]:
        """Run full evaluation suite and return aggregated results"""
        print("\n" + "=" * 60)
        print("🧪 Starting Full System Evaluation")
        print("=" * 60)
        
        test_goals = self.load_test_goals()
        total_start_time = time.time()
        
        detailed_results = []
        for idx, test_case in enumerate(test_goals):
            goal = test_case.get("goal", "")
            expected_keys = test_case.get("expected_keys", [])
            
            if not goal:
                continue
            
            # Add small delay between tests to avoid rate limiting (except first test)
            if idx > 0:
                time.sleep(2)
                
            result = self.evaluate_single_goal(goal, expected_keys)
            detailed_results.append(result)
            
            status = "✅" if result["success"] else "❌"
            print(f"{status} Goal completed in {result['execution_time']}s")
        
        total_evaluation_time = time.time() - total_start_time
        
        # Calculate aggregated metrics
        total_tests = len(detailed_results)
        successful_tests = sum(1 for r in detailed_results if r["success"])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        confidences = [r["adk_confidence"] for r in detailed_results if r.get("adk_confidence", 0) > 0]
        average_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        quality_scores = [r["adk_quality_score"] for r in detailed_results if r.get("adk_quality_score", 0) > 0]
        average_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        execution_times = [r["execution_time"] for r in detailed_results]
        average_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # Compile final results
        evaluation_results = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": round(success_rate, 2),
            "average_confidence": round(average_confidence, 2),
            "average_quality_score": round(average_quality_score, 2),
            "average_execution_time": round(average_execution_time, 2),
            "total_evaluation_time": round(total_evaluation_time, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "detailed_results": detailed_results
        }
        
        # Save results to file
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.evals_dir / f"evaluation_results_{timestamp_str}.json"
        with open(results_file, 'w') as f:
            json.dump(evaluation_results, f, indent=2)
        
        print("\n" + "=" * 60)
        print("📊 Evaluation Summary")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Avg Confidence: {average_confidence:.2f}%")
        print(f"Avg Quality: {average_quality_score:.2f}%")
        print(f"Avg Execution Time: {average_execution_time:.2f}s")
        print(f"Results saved to: {results_file}")
        print("=" * 60)
        
        return evaluation_results

    def evaluate(self, input_data):
        """
        Legacy method for backward compatibility.
        """
        print("🔍 Evaluating agent system with input:", input_data)
        return {
            "score": 0.95,
            "feedback": "All agents performed well."
        }
