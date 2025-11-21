"""
Example script demonstrating real-time multi-agent problem solving.
Shows how problems are automatically divided and solved by multiple agents.
"""

from realtime_coordinator import solve_problem_realtime

def main():
    print("=" * 60)
    print("🤖 Real-Time Multi-Agent Problem Solver - Example")
    print("=" * 60)
    print()
    
    # Example problems
    examples = [
        "Find the next SpaceX launch and check the weather at that location",
        "Calculate 15 * 23 + 45 and define the word 'astronaut'",
        "Get the latest news about space exploration",
        "What's the weather like at Kennedy Space Center?",
    ]
    
    print("Example problems:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")
    print()
    
    # Run first example
    print("Running example 1...")
    print("-" * 60)
    result = solve_problem_realtime(examples[0])
    
    print("\n" + "=" * 60)
    print("📊 Execution Summary")
    print("=" * 60)
    print(f"Agents executed: {len(result.get('agent_status', {}))}")
    print(f"Real-time updates: {len(result.get('realtime_updates', []))}")
    print(f"Sub-tasks: {len(result.get('execution_plan', {}).get('sub_tasks', []))}")
    
    if result.get("summary"):
        print("\n" + "=" * 60)
        print("📋 Final Summary")
        print("=" * 60)
        print(result["summary"])

if __name__ == "__main__":
    main()

