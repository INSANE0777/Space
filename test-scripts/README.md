# 🧪 Test Scripts Directory

This directory contains all testing and evaluation scripts for the Multi-Agent AI System.

## 📋 Available Test Scripts

### 🚀 Quick Agent Test (`quick_agent_test.py`)
**Interactive menu-driven testing for individual agents**

```bash
cd test-scripts
python quick_agent_test.py
```

**Features:**
- Interactive menu to select specific agents to test
- Option to test all agents at once
- Real-time feedback and diagnostics
- Input prompts for custom test data

**Menu Options:**
- `1` - SpaceX Agent
- `2` - Weather Agent  
- `3` - Summary Agent
- `4` - Google ADK Agent
- `5` - Calculator Agent
- `6` - Dictionary Agent
- `0` - Test All Agents

---

### 🔬 Individual Agent Testing (`test_individual_agents.py`) 
**Comprehensive testing suite with detailed analysis**

```bash
cd test-scripts
python test_individual_agents.py
```

**Features:**
- Detailed performance metrics and timing
- Multiple test scenarios per agent
- Integration testing included
- Pass/fail status reporting
- Comprehensive output analysis

---

### ⚙️ Enhanced Workflow Test (`test_enhanced_workflow.py`)
**Tests the main Gemini-powered workflow**

```bash
cd test-scripts
python test_enhanced_workflow.py
```

**Features:**
- Tests end-to-end workflow execution
- Validates Gemini agent selection
- Checks multi-agent coordination
- Verifies intelligent summarization

---

### 🔧 System Test (`test_system.py`)
**Basic system integration testing**

```bash
cd test-scripts
python test_system.py
```

**Features:**
- Core system functionality validation
- Basic agent execution tests
- System health checks

---

### 🔗 LangChain Integration Test (`test_langchain_integration.py`)
**Tests LangChain and Gemini integration**

```bash
cd test-scripts
python test_langchain_integration.py
```

**Features:**
- Validates LangChain setup
- Tests Gemini API connectivity
- Checks model responses

---

### 📊 Automated Evaluation (`automated_evaluation.py`)
**Automated testing and evaluation framework**

```bash
cd test-scripts
python automated_evaluation.py
```

**Features:**
- Automated test execution
- Performance benchmarking
- Success rate analysis
- Detailed reporting

---

## 🎯 Usage Instructions

### Running from Test Scripts Directory
```bash
# Navigate to test scripts directory
cd test-scripts

# Run any test script
python quick_agent_test.py
python test_individual_agents.py
python test_enhanced_workflow.py
```

### Running from Main Directory
```bash
# Run from main directory with relative path
python test-scripts/quick_agent_test.py
python test-scripts/test_individual_agents.py
```

### Import Path Considerations
All test scripts are configured to work from the test-scripts directory. They include proper path adjustments to import the main system modules:

```python
import sys
import os
sys.path.append('..')  # Add parent directory to path
```

---

## 🧭 Testing Workflow Recommendations

### 1. Quick Development Testing
```bash
cd test-scripts
python quick_agent_test.py
```
Use this for rapid testing during development.

### 2. Comprehensive Validation
```bash
cd test-scripts
python test_individual_agents.py
```
Use this for thorough validation before releases.

### 3. End-to-End Testing
```bash
cd test-scripts
python test_enhanced_workflow.py
```
Use this to test the complete user workflow.

### 4. Performance Analysis
```bash
cd test-scripts
python automated_evaluation.py
```
Use this for performance benchmarking and analysis.

---

## 📝 Test Script Descriptions

| Script | Purpose | Usage | Output |
|--------|---------|--------|--------|
| `quick_agent_test.py` | Interactive agent testing | Development & debugging | Interactive feedback |
| `test_individual_agents.py` | Comprehensive agent validation | Quality assurance | Detailed reports |
| `test_enhanced_workflow.py` | End-to-end workflow testing | Integration testing | Workflow validation |
| `test_system.py` | Basic system health checks | System monitoring | Health status |
| `test_langchain_integration.py` | LangChain/Gemini testing | API validation | Connection status |
| `automated_evaluation.py` | Automated benchmarking | Performance analysis | Metrics & reports |

---

## 🛠️ Troubleshooting

### Common Issues

**Import Errors:**
```python
# If you get import errors, ensure you're in the right directory
cd test-scripts
python quick_agent_test.py
```

**API Key Issues:**
```bash
# Make sure .env file is in the parent directory
ls ../.env
```

**Module Not Found:**
```python
# Check if the path adjustment is working
import sys
print(sys.path)
```

### Path Configuration
All test scripts include this configuration:
```python
import sys
import os
sys.path.append('..')  # Adds parent directory to Python path
```

This allows the scripts to import modules from the main system directory.

---

## 📊 Expected Test Results

### Quick Agent Test - All Agents Working
```
📊 Results: 6/6 agents working
✅ SpaceX: OK
✅ Weather: OK  
✅ Calculator: OK
✅ Dictionary: OK
✅ Summary: OK
✅ Google ADK: OK
```

### Individual Agent Test - All Passing
```
SPACEX.............. ✅ PASS
WEATHER............. ✅ PASS
SUMMARY............. ✅ PASS
CALCULATOR.......... ✅ PASS
DICTIONARY.......... ✅ PASS
ADK................. ✅ PASS
----------------------------------------
TOTAL: 6/6 tests passed
🎉 All agent tests passed!
```

---

## 🚀 Getting Started

1. **Navigate to test scripts directory:**
   ```bash
   cd test-scripts
   ```

2. **Start with quick testing:**
   ```bash
   python quick_agent_test.py
   ```

3. **Run comprehensive tests:**
   ```bash
   python test_individual_agents.py
   ```

4. **Test the main workflow:**
   ```bash
   python test_enhanced_workflow.py
   ```

All test scripts are ready to use and properly configured for the Multi-Agent AI System! 🎉
