# Real-Time Multi-Agent Problem Solving

## Overview

The system now supports **real-time problem solving** where any problem is automatically:
1. **Divided into sub-tasks** using AI analysis
2. **Assigned to appropriate agents** based on task requirements
3. **Executed in parallel** where possible (respecting dependencies)
4. **Shared between agents** - solutions are passed to all relevant agents in real-time

## Key Features

### 🧠 Intelligent Problem Breakdown
- Uses Gemini AI to analyze problems and break them into logical sub-tasks
- Identifies dependencies between tasks
- Determines which tasks can run in parallel

### ⚡ Parallel Execution
- Agents run in parallel when there are no dependencies
- Tasks are organized into "waves" - parallel within wave, sequential between waves
- Significantly faster than sequential execution

### 📬 Real-Time Solution Sharing
- Solutions from agents are shared via a solution queue
- All agents receive updates from other agents
- Enables collaborative problem solving

### 📊 Real-Time Updates
- Track agent status (running, completed, failed)
- Monitor execution progress
- View real-time updates as agents complete

## Usage

### Command Line

#### Basic Usage (Sequential - Original)
```bash
python main.py
```

#### Real-Time Mode
```bash
python main.py --realtime
# or
python main.py -r
```

#### Direct Real-Time Coordinator
```bash
python realtime_coordinator.py
```

#### Example Script
```bash
python example_realtime.py
```

### Python API

```python
from realtime_coordinator import solve_problem_realtime

# Solve a problem in real-time
result = solve_problem_realtime(
    "Find the next SpaceX launch and check weather at that location"
)

# Access results
print(result["summary"])
print(result["realtime_updates"])
print(result["agent_status"])
```

### Web Interface

The web interface now supports real-time mode via API:

```javascript
// Enable real-time mode
fetch('/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        message: 'Your problem here',
        realtime: true  // Enable real-time mode
    })
})
```

## How It Works

### 1. Problem Analysis
```
User Problem → AI Analysis → Sub-tasks with Agent Assignments
```

### 2. Execution Planning
```
Sub-tasks → Dependency Analysis → Execution Waves
```

### 3. Parallel Execution
```
Wave 1: [Task A, Task B] (parallel)
  ↓
Wave 2: [Task C] (depends on A, B)
  ↓
Wave 3: [Task D] (depends on C)
```

### 4. Solution Sharing
```
Agent 1 completes → Solution Queue → All Agents receive update
```

## Example Problem Breakdown

**Input:** "Find the next SpaceX launch and check the weather at that location"

**Breakdown:**
```json
{
  "sub_tasks": [
    {
      "id": "task_1",
      "description": "Get SpaceX launch data and coordinates",
      "agents": ["spacex_agent"],
      "depends_on": [],
      "can_parallel": true
    },
    {
      "id": "task_2",
      "description": "Get weather at launch location",
      "agents": ["weather_agent"],
      "depends_on": ["task_1"],
      "can_parallel": false
    },
    {
      "id": "task_3",
      "description": "Generate comprehensive summary",
      "agents": ["summary_agent"],
      "depends_on": ["task_1", "task_2"],
      "can_parallel": false
    }
  ]
}
```

**Execution:**
- Wave 1: `task_1` runs
- Wave 2: `task_2` runs (uses coordinates from task_1)
- Wave 3: `task_3` runs (uses data from both tasks)

## Benefits

1. **Faster Execution**: Parallel execution reduces total time
2. **Better Coordination**: Agents share solutions in real-time
3. **Intelligent Planning**: AI determines optimal execution strategy
4. **Scalability**: Easy to add new agents and capabilities
5. **Transparency**: Real-time updates show what's happening

## Integration with Existing System

The real-time coordinator is fully integrated:
- ✅ Works with all existing agents
- ✅ Compatible with evaluation system
- ✅ Web interface support
- ✅ Backward compatible (original sequential mode still available)

## Configuration

Real-time mode is automatically available if:
- `realtime_coordinator.py` is present
- Google API key is configured
- All agent dependencies are installed

Check availability:
```python
from main import REALTIME_AVAILABLE
print(f"Real-time mode: {'Available' if REALTIME_AVAILABLE else 'Not available'}")
```

## Performance Comparison

**Sequential Mode:**
- Task 1: 2s
- Task 2: 3s (waits for Task 1)
- Task 3: 1s (waits for Task 2)
- **Total: 6s**

**Real-Time Mode (Parallel):**
- Wave 1 (Task 1): 2s
- Wave 2 (Task 2): 3s
- Wave 3 (Task 3): 1s
- **Total: 6s** (same, but with better coordination)

**Real-Time Mode (Multiple Independent Tasks):**
- Wave 1 (Task A, B, C in parallel): max(2s, 3s, 1s) = 3s
- Wave 2 (Task D): 1s
- **Total: 4s** (vs 7s sequential)

## Future Enhancements

- [ ] WebSocket support for live updates
- [ ] Agent-to-agent direct communication
- [ ] Dynamic task re-planning based on results
- [ ] Priority-based task scheduling
- [ ] Resource-aware parallel execution

