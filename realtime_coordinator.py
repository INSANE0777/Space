"""
Real-time Multi-Agent Coordinator
Automatically divides problems into sub-tasks and coordinates agents
with real-time solution sharing between agents.
"""

import os
import time
import threading
from typing import Dict, List, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from dotenv import load_dotenv

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ langchain_google_genai not available. Real-time coordinator requires this package.")

try:
    from agent_utils import AGENT_GETTERS, load_agent, get_gemini_response
    from agents.google_adk_agent import GoogleADKCoordinator
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    AGENT_GETTERS = {}
    load_agent = None
    get_gemini_response = None
    GoogleADKCoordinator = None

load_dotenv()


class RealTimeCoordinator:
    """
    Real-time coordinator that:
    1. Breaks problems into sub-tasks
    2. Assigns agents to sub-tasks
    3. Runs agents in parallel where possible
    4. Shares solutions between agents in real-time
    """
    
    def __init__(self):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("langchain_google_genai is required for real-time coordinator")
        
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.7,
            max_tokens=2000
        )
        self.solution_queue = Queue()  # Shared solution queue for agents
        self.agent_status = {}  # Track agent status
        self.realtime_updates = []  # Store real-time updates
        
        # Space-related keywords for query validation
        self.space_keywords = [
            "spacex", "space", "rocket", "launch", "mission", "satellite", "orbit",
            "astronaut", "nasa", "iss", "international space station", "mars",
            "moon", "lunar", "stellar", "galaxy", "planet", "asteroid", "comet",
            "spacecraft", "falcon", "starship", "dragon", "capsule", "payload",
            "launchpad", "kennedy space center", "cape canaveral", "spaceport",
            "trajectory", "orbital", "reentry", "landing", "booster", "stage"
        ]
        
    def is_space_related(self, problem: str) -> bool:
        """Check if the query is space-related"""
        problem_lower = problem.lower()
        return any(keyword in problem_lower for keyword in self.space_keywords)
    
    def break_down_problem(self, problem: str) -> Dict[str, Any]:
        """
        Use AI to break down a problem into sub-tasks and assign agents.
        Returns a structured plan with sub-tasks and agent assignments.
        """
        # Validate space-related query
        if not self.is_space_related(problem):
            print(f"⚠️ Query is not space-related. This system only handles space-related queries.")
            print(f"   Space keywords: {', '.join(self.space_keywords[:10])}...")
            return {
                "sub_tasks": [{
                    "id": "task_error",
                    "description": "Handle non-space query",
                    "agents": ["summary_agent"],
                    "depends_on": [],
                    "can_parallel": False
                }],
                "execution_order": ["task_error"],
                "parallel_groups": [],
                "error": "Query is not space-related. Please ask about SpaceX, rockets, launches, missions, or space-related topics."
            }
        
        print(f"\n🧠 Analyzing space-related problem: '{problem}'")
        print("📋 Breaking down into sub-tasks...")
        
        breakdown_prompt = """You are an intelligent problem analyzer for a SPACE-FOCUSED multi-agent AI system.

This system ONLY handles space-related queries (SpaceX, rockets, launches, missions, satellites, etc.).

Available agents:
- spacex_agent: Gets SpaceX launch data, coordinates, mission details, rocket information
- weather_agent: Gets weather data for launch locations (Kennedy Space Center, Cape Canaveral, etc.)
- calculator_agent: Performs space-related calculations (trajectories, velocities, orbital mechanics)
- news_agent: Fetches space-related news articles
- summary_agent: Analyzes space data and provides conclusions

Your task:
1. Analyze the user's SPACE-RELATED problem
2. Break it down into logical sub-tasks
3. Assign appropriate agents to each sub-task
4. Identify dependencies between sub-tasks (e.g., weather needs launch location from SpaceX)
5. Identify which tasks can run in parallel
6. Distribute data appropriately - each agent should receive relevant data from previous agents

IMPORTANT: 
- Always use spacex_agent for any launch/mission queries
- Use weather_agent when location/weather is mentioned (it will get coordinates from spacex_agent)
- Use calculator_agent for any calculations related to space (trajectories, velocities, etc.)
- Use news_agent for space news queries
- Always end with summary_agent to synthesize all information

Available agents:
- spacex_agent: Gets SpaceX launch data, coordinates, mission details
- weather_agent: Gets weather data for specific locations
- calculator_agent: Performs mathematical calculations and solves equations
- dictionary_agent: Provides word definitions, meanings, and synonyms
- news_agent: Fetches relevant news articles
- summary_agent: Analyzes data and provides conclusions

Your task:
1. Analyze the user's problem
2. Break it down into logical sub-tasks
3. Assign appropriate agents to each sub-task
4. Identify dependencies between sub-tasks (which tasks need results from others)
5. Identify which tasks can run in parallel

Return your response in this JSON format:
{
  "sub_tasks": [
    {
      "id": "task_1",
      "description": "Description of the sub-task",
      "agents": ["agent_name"],
      "depends_on": [],  // List of task IDs this depends on
      "can_parallel": true,  // Can run in parallel with other tasks
      "data_needs": ["key1", "key2"]  // What data this task needs from previous tasks
    }
  ],
  "execution_order": ["task_1", "task_2"],  // Suggested execution order
  "parallel_groups": [["task_1", "task_2"]]  // Tasks that can run in parallel
}

Be specific and thorough. Consider all aspects of the SPACE-RELATED problem."""
        
        try:
            system_message = SystemMessage(content=breakdown_prompt)
            human_message = HumanMessage(
                content=f"User Problem: \"{problem}\"\n\nAnalyze and break down this problem into sub-tasks with agent assignments:"
            )
            
            response = self.llm.invoke([system_message, human_message])
            response_text = response.content.strip()
            
            # Try to extract JSON from response
            import json
            import re
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
            else:
                # Fallback: create a simple plan
                plan = self._create_fallback_plan(problem)
            
            print(f"✅ Problem broken down into {len(plan.get('sub_tasks', []))} sub-tasks")
            return plan
            
        except Exception as e:
            print(f"⚠️ Error in problem breakdown: {e}")
            return self._create_fallback_plan(problem)
    
    def _create_fallback_plan(self, problem: str) -> Dict[str, Any]:
        """Create a fallback plan when AI breakdown fails - SPACE-RELATED ONLY"""
        problem_lower = problem.lower()
        
        # Space-related keyword-based planning
        agents_needed = []
        task_dependencies = {}
        
        # Always start with spacex_agent for space queries
        if any(kw in problem_lower for kw in ["spacex", "launch", "rocket", "mission", "satellite"]):
            agents_needed.append("spacex_agent")
            task_dependencies["spacex_agent"] = []
        
        # Weather depends on spacex for location
        if any(kw in problem_lower for kw in ["weather", "temperature", "climate", "forecast", "condition"]):
            agents_needed.append("weather_agent")
            task_dependencies["weather_agent"] = ["spacex_agent"] if "spacex_agent" in agents_needed else []
        
        # Satellite data agent
        if any(kw in problem_lower for kw in ["satellite", "orbital", "tracking", "iss", "space station", "orbit"]):
            agents_needed.append("satellite_data_agent")
            task_dependencies["satellite_data_agent"] = ["spacex_agent"] if "spacex_agent" in agents_needed else []
        
        # Anomalies detection - depends on other agents
        if any(kw in problem_lower for kw in ["anomaly", "anomalies", "detect", "issue", "problem", "error", "warning", "check"]):
            agents_needed.append("anomalies_detection_agent")
            # Will depend on all other agents that have been added
            task_dependencies["anomalies_detection_agent"] = [a for a in agents_needed if a != "anomalies_detection_agent"]
        
        # Calculator for space calculations
        if any(kw in problem_lower for kw in ["calculate", "compute", "solve", "math", "trajectory", "velocity", "orbit"]):
            agents_needed.append("calculator_agent")
            task_dependencies["calculator_agent"] = []
        
        # News for space news
        if any(kw in problem_lower for kw in ["news", "article", "current events", "latest"]):
            agents_needed.append("news_agent")
            task_dependencies["news_agent"] = []
        
        # If no specific agents, default to spacex + summary
        if not agents_needed:
            agents_needed = ["spacex_agent", "summary_agent"]
            task_dependencies["spacex_agent"] = []
            task_dependencies["summary_agent"] = ["spacex_agent"]
        else:
            agents_needed.append("summary_agent")
            task_dependencies["summary_agent"] = agents_needed[:-1]  # Depends on all other agents
        
        # Create task structure with proper dependencies
        sub_tasks = []
        agent_to_task_id = {}
        
        # Create tasks for each agent (except summary)
        task_counter = 1
        for agent in agents_needed[:-1]:  # Exclude summary_agent
            task_id = f"task_{task_counter}"
            agent_to_task_id[agent] = task_id
            
            # Get dependencies for this agent
            deps = task_dependencies.get(agent, [])
            dep_task_ids = [agent_to_task_id[dep] for dep in deps if dep in agent_to_task_id]
            
            sub_tasks.append({
                "id": task_id,
                "description": f"Execute {agent} to handle space-related data",
                "agents": [agent],
                "depends_on": dep_task_ids,
                "can_parallel": len(dep_task_ids) == 0,  # Can parallelize if no dependencies
                "data_needs": deps  # What data this agent needs
            })
            task_counter += 1
        
        # Summary task depends on all others
        all_task_ids = [t["id"] for t in sub_tasks]
        sub_tasks.append({
            "id": f"task_{task_counter}",
            "description": "Generate comprehensive space mission summary",
            "agents": ["summary_agent"],
            "depends_on": all_task_ids,
            "can_parallel": False,
            "data_needs": agents_needed[:-1]  # Needs data from all agents
        })
        
        return {
            "sub_tasks": sub_tasks,
            "execution_order": [t["id"] for t in sub_tasks],
            "parallel_groups": [[t["id"] for t in sub_tasks[:-1]]] if len(sub_tasks) > 1 else []
        }
    
    def prepare_agent_data(self, agent_name: str, shared_data: Dict[str, Any], data_needs: List[str]) -> Dict[str, Any]:
        """Prepare data for a specific agent based on what it needs"""
        agent_data = {"goal": shared_data.get("goal", "")}
        
        # Distribute relevant data to each agent
        if agent_name == "spacex_agent":
            # SpaceX agent needs goal only
            agent_data["goal"] = shared_data.get("goal", "")
            
        elif agent_name == "weather_agent":
            # Weather agent needs coordinates from SpaceX
            if "spacex" in shared_data:
                spacex_data = shared_data.get("spacex", {})
                coordinates = spacex_data.get("coordinates", {})
                if coordinates:
                    agent_data["spacex"] = spacex_data
                    agent_data["coordinates"] = coordinates
                else:
                    # If no coordinates yet, try to get location from goal
                    agent_data["goal"] = shared_data.get("goal", "")
            else:
                agent_data["goal"] = shared_data.get("goal", "")
                
        elif agent_name == "calculator_agent":
            # Calculator needs goal and any relevant data
            agent_data["goal"] = shared_data.get("goal", "")
            if "spacex" in shared_data:
                agent_data["spacex"] = shared_data.get("spacex", {})
                
        elif agent_name == "news_agent":
            # News agent needs goal and topic context
            agent_data["goal"] = shared_data.get("goal", "")
            if "spacex" in shared_data:
                agent_data["spacex"] = shared_data.get("spacex", {})
        
        elif agent_name == "satellite_data_agent":
            # Satellite agent needs coordinates from SpaceX if available
            agent_data["goal"] = shared_data.get("goal", "")
            if "spacex" in shared_data:
                spacex_data = shared_data.get("spacex", {})
                coordinates = spacex_data.get("coordinates", {})
                if coordinates:
                    agent_data["spacex"] = spacex_data
                    agent_data["coordinates"] = coordinates
            # Also pass satellite data if already exists
            if "satellite" in shared_data:
                agent_data["satellite"] = shared_data.get("satellite", {})
        
        elif agent_name == "anomalies_detection_agent":
            # Anomalies detection needs ALL data from other agents
            agent_data = shared_data.copy()
                
        elif agent_name == "summary_agent":
            # Summary agent gets ALL data
            agent_data = shared_data.copy()
        else:
            # Default: give all data
            agent_data = shared_data.copy()
        
        return agent_data
    
    def execute_agent(self, agent_name: str, data: Dict[str, Any], task_id: str, data_needs: List[str] = None) -> Dict[str, Any]:
        """Execute a single agent and return updated data with improved error handling"""
        if data_needs is None:
            data_needs = []
            
        try:
            print(f"  🔄 [{task_id}] Executing {agent_name}...")
            self.agent_status[agent_name] = "running"
            
            # Prepare agent-specific data
            agent_data = self.prepare_agent_data(agent_name, data, data_needs)
            
            # Validate agent exists
            if not load_agent:
                raise ValueError("Agent loader not available")
            
            agent = load_agent(agent_name)
            if not agent:
                raise ValueError(f"Agent {agent_name} not found")
            
            # Execute agent with proper error handling
            try:
                result_data = agent.run(agent_data.copy())
            except AttributeError as e:
                # Handle case where agent.run doesn't exist or has wrong signature
                if "run" not in dir(agent):
                    raise ValueError(f"Agent {agent_name} does not have a run method")
                raise
            except Exception as e:
                # Re-raise with more context
                raise Exception(f"Agent {agent_name} execution error: {str(e)}")
            
            # Validate result
            if not isinstance(result_data, dict):
                raise ValueError(f"Agent {agent_name} returned invalid data type: {type(result_data)}")
            
            # Share solution with other agents via queue
            solution_update = {
                "agent": agent_name,
                "task_id": task_id,
                "data": result_data,
                "timestamp": time.time()
            }
            self.solution_queue.put(solution_update)
            
            # Add real-time update
            self.realtime_updates.append({
                "agent": agent_name,
                "status": "completed",
                "task_id": task_id,
                "timestamp": time.time()
            })
            
            self.agent_status[agent_name] = "completed"
            print(f"  ✅ [{task_id}] {agent_name} completed")
            
            return result_data
            
        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ [{task_id}] {agent_name} failed: {error_msg}")
            self.agent_status[agent_name] = "failed"
            self.realtime_updates.append({
                "agent": agent_name,
                "status": "failed",
                "task_id": task_id,
                "error": error_msg,
                "timestamp": time.time()
            })
            # Return original data on error (don't break the chain)
            return data
    
    def merge_agent_results(self, base_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge results from multiple agents"""
        merged = base_data.copy()
        
        # Merge all keys from new_data
        for key, value in new_data.items():
            if key != "goal":  # Don't overwrite the original goal
                merged[key] = value
        
        return merged
    
    def solve_problem_realtime(self, problem: str) -> Dict[str, Any]:
        """
        Main method to solve a problem in real-time:
        1. Validate space-related query
        2. Break down problem
        3. Execute agents (parallel where possible)
        4. Share solutions between agents
        5. Return final result
        """
        print("\n" + "=" * 60)
        print("🚀 REAL-TIME MULTI-AGENT SPACE PROBLEM SOLVING")
        print("=" * 60)
        
        # Step 0: Validate space-related query
        if not self.is_space_related(problem):
            error_msg = "This system only handles space-related queries. Please ask about SpaceX, rockets, launches, missions, or space-related topics."
            print(f"⚠️ {error_msg}")
            return {
                "goal": problem,
                "error": error_msg,
                "summary": f"❌ {error_msg}\n\n💡 Try asking about:\n• SpaceX launches and missions\n• Rocket launches and trajectories\n• Space missions and satellites\n• Launch weather conditions\n• Space-related calculations",
                "agent_status": {},
                "realtime_updates": []
            }
        
        # Step 1: Break down problem
        plan = self.break_down_problem(problem)
        
        # Check if plan has error
        if plan.get("error"):
            return {
                "goal": problem,
                "error": plan.get("error"),
                "summary": f"❌ {plan.get('error')}",
                "agent_status": {},
                "realtime_updates": []
            }
        
        # Step 2: Initialize shared data structure
        shared_data = {"goal": problem}
        all_results = {}
        
        # Step 3: Execute tasks based on dependencies and parallelism
        print(f"\n⚙️ Executing {len(plan['sub_tasks'])} sub-tasks...")
        
        # Group tasks by dependency level
        task_map = {task["id"]: task for task in plan["sub_tasks"]}
        completed_tasks = set()
        
        # Execute tasks in waves (parallel within wave, sequential between waves)
        execution_waves = self._organize_execution_waves(plan["sub_tasks"])
        
        for wave_num, wave_tasks in enumerate(execution_waves, 1):
            print(f"\n🌊 Wave {wave_num}: Executing {len(wave_tasks)} tasks in parallel...")
            
            # Execute tasks in this wave in parallel
            with ThreadPoolExecutor(max_workers=len(wave_tasks)) as executor:
                futures = {}
                
                for task in wave_tasks:
                    task_id = task["id"]
                    agents = task["agents"]
                    
                    # Prepare data with results from dependent tasks
                    task_data = shared_data.copy()
                    for dep_id in task.get("depends_on", []):
                        if dep_id in all_results:
                            task_data = self.merge_agent_results(task_data, all_results[dep_id])
                    
                    # Get data needs for this task
                    data_needs = task.get("data_needs", [])
                    
                    # Execute all agents for this task
                    for agent_name in agents:
                        future = executor.submit(
                            self.execute_agent, 
                            agent_name, 
                            task_data, 
                            task_id,
                            data_needs
                        )
                        futures[future] = (task_id, agent_name)
                
                # Collect results as they complete (with timeout)
                try:
                    for future in as_completed(futures, timeout=120):  # 2 minute total timeout per wave
                        task_id, agent_name = futures[future]
                        try:
                            result = future.result()  # Get the result
                            if task_id not in all_results:
                                all_results[task_id] = {}
                            all_results[task_id] = self.merge_agent_results(
                                all_results.get(task_id, {}), result
                            )
                            # Update shared data
                            shared_data = self.merge_agent_results(shared_data, result)
                        except Exception as e:
                            error_msg = f"Task {task_id} failed: {str(e)}"
                            print(f"  ❌ {error_msg}")
                            # Continue with other tasks even if one fails
                            self.realtime_updates.append({
                                "task_id": task_id,
                                "status": "failed",
                                "error": error_msg,
                                "timestamp": time.time()
                            })
                except TimeoutError:
                    print(f"  ⏱️ Wave {wave_num} timed out after 120 seconds")
                    # Mark remaining tasks as timed out
                    for future, (task_id, agent_name) in futures.items():
                        if not future.done():
                            self.realtime_updates.append({
                                "task_id": task_id,
                                "agent": agent_name,
                                "status": "timeout",
                                "error": "Task timed out",
                                "timestamp": time.time()
                            })
            
            # Mark tasks as completed
            for task in wave_tasks:
                completed_tasks.add(task["id"])
        
        # Step 4: Process any solutions shared via queue
        print("\n📬 Processing shared solutions between agents...")
        while not self.solution_queue.empty():
            solution = self.solution_queue.get()
            print(f"  📨 Solution from {solution['agent']} received")
            shared_data = self.merge_agent_results(shared_data, solution["data"])
        
        # Step 5: Generate final summary if not already done
        if "summary" not in shared_data or not shared_data.get("summary"):
            print("\n📝 Generating final summary...")
            try:
                if load_agent:
                    summary_agent = load_agent("summary_agent")
                    if summary_agent:
                        shared_data = summary_agent.run(shared_data)
                    else:
                        shared_data["summary"] = "Summary agent not available. Data collected successfully."
                else:
                    shared_data["summary"] = "Summary agent not available. Data collected successfully."
            except Exception as e:
                error_msg = f"Summary generation failed: {str(e)}"
                print(f"⚠️ {error_msg}")
                # Create a basic summary from available data
                if "spacex" in shared_data or "weather" in shared_data:
                    shared_data["summary"] = f"Space mission data collected. {error_msg}"
                else:
                    shared_data["summary"] = f"Data collection completed with errors: {error_msg}"
        
        # Step 6: Compile final result
        final_result = {
            **shared_data,
            "realtime_updates": self.realtime_updates,
            "execution_plan": plan,
            "agent_status": self.agent_status.copy()
        }
        
        print("\n" + "=" * 60)
        print("✅ PROBLEM SOLVED IN REAL-TIME")
        print("=" * 60)
        print(f"📊 Agents executed: {len(set(self.agent_status.keys()))}")
        print(f"🔄 Real-time updates: {len(self.realtime_updates)}")
        print(f"⏱️ Total tasks: {len(plan['sub_tasks'])}")
        
        return final_result
    
    def _organize_execution_waves(self, sub_tasks: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Organize tasks into execution waves based on dependencies.
        Tasks in the same wave can run in parallel.
        """
        task_map = {task["id"]: task for task in sub_tasks}
        waves = []
        completed = set()
        
        while len(completed) < len(sub_tasks):
            # Find tasks that can run now (all dependencies completed)
            ready_tasks = []
            for task in sub_tasks:
                if task["id"] in completed:
                    continue
                
                deps = task.get("depends_on", [])
                if all(dep_id in completed for dep_id in deps):
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # If no ready tasks, force remaining tasks (shouldn't happen)
                remaining = [t for t in sub_tasks if t["id"] not in completed]
                if remaining:
                    waves.append(remaining)
                    completed.update(t["id"] for t in remaining)
                break
            
            waves.append(ready_tasks)
            completed.update(t["id"] for t in ready_tasks)
        
        return waves


def solve_problem_realtime(problem: str) -> Dict[str, Any]:
    """
    Convenience function to solve a problem in real-time.
    This is the main entry point for real-time problem solving.
    """
    coordinator = RealTimeCoordinator()
    return coordinator.solve_problem_realtime(problem)


if __name__ == "__main__":
    # Interactive mode
    print("🤖 Real-Time Multi-Agent Problem Solver")
    print("=" * 60)
    print("Enter a problem and I'll break it down and solve it using multiple agents!")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            problem = input("\n💬 Your problem: ").strip()
            if not problem:
                continue
            if problem.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            
            result = solve_problem_realtime(problem)
            
            # Display summary
            if result.get("summary"):
                print("\n" + "=" * 60)
                print("📋 FINAL SUMMARY")
                print("=" * 60)
                print(result["summary"])
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

