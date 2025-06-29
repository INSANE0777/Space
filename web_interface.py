# web_interface.py
# Interactive Web UI for Multi-Agent AI System

from flask import Flask, render_template, request, jsonify, stream_template
import json
import time
from main import run_goal
import sys
import os
sys.path.append('test-scripts')  # Add test-scripts directory to path
from automated_evaluation import AgentSystemEvaluator
import io
from contextlib import redirect_stdout, redirect_stderr

app = Flask(__name__)

# Global variable to store terminal logs
terminal_logs = []

class TerminalCapture:
    """Capture terminal output for web display"""
    def __init__(self):
        self.logs = []
    
    def write(self, text):
        if text.strip():
            timestamp = time.strftime('%H:%M:%S')
            self.logs.append({
                'timestamp': timestamp,
                'message': text.strip(),
                'type': 'output'
            })
            # Keep only last 100 log entries
            if len(self.logs) > 100:
                self.logs = self.logs[-100:]
        return len(text)
    
    def flush(self):
        pass

# Global terminal capture instance
terminal_capture = TerminalCapture()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Chat interface page"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chat interface"""
    try:
        data = request.json
        message = data.get('message', '')
        agent = data.get('agent', None)
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Clear previous logs and add start message
        terminal_capture.logs.clear()
        terminal_capture.write(f"💬 Chat: {message}")
        
        if agent:
            terminal_capture.write(f"🎯 Focusing on agent: {agent}")
        
        terminal_capture.write("=" * 60)
        
        # Capture stdout/stderr while running the goal
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            # Redirect output to our capture
            sys.stdout = terminal_capture
            sys.stderr = terminal_capture
            
            # Run the goal/message as a task
            result = run_goal(message)
            
            terminal_capture.write("=" * 60)
            terminal_capture.write("✅ Task completed successfully!")
            
        finally:
            # Restore original stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        # Process logs to extract agent-specific information
        workflow_logs = []
        for log in terminal_capture.logs:
            log_msg = log['message']
            agent_type = None
            
            # Detect which agent is speaking
            if 'spacex' in log_msg.lower() or '🚀' in log_msg:
                agent_type = 'spacex'
            elif 'weather' in log_msg.lower() or '🌍' in log_msg:
                agent_type = 'weather'
            elif 'summary' in log_msg.lower() or '📝' in log_msg:
                agent_type = 'summary'
            elif 'adk' in log_msg.lower() or '🧠' in log_msg:
                agent_type = 'google_adk'
            
            workflow_logs.append({
                'message': log_msg,
                'timestamp': log['timestamp'],
                'agent': agent_type
            })
        
        return jsonify({
            'success': True,
            'result': {
                'summary': result.get('summary', 'Task completed successfully!'),
                'raw_data': result
            },
            'workflow_logs': workflow_logs,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        terminal_capture.write(f"❌ Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'workflow_logs': [{'message': f'Error: {str(e)}', 'timestamp': time.strftime('%H:%M:%S'), 'agent': None}]
        }), 500

@app.route('/api/run_goal', methods=['POST'])
def api_run_goal():
    """API endpoint to run a goal"""
    try:
        data = request.json
        goal = data.get('goal', '')
        
        if not goal:
            return jsonify({'error': 'Goal is required'}), 400
        
        # Clear previous logs and add start message
        terminal_capture.logs.clear()
        terminal_capture.write(f"🚀 Starting execution for goal: {goal}")
        terminal_capture.write("=" * 60)
        
        # Capture stdout/stderr while running the goal
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            # Redirect output to our capture
            sys.stdout = terminal_capture
            sys.stderr = terminal_capture
            
            # Run the goal
            result = run_goal(goal)
            
            terminal_capture.write("=" * 60)
            terminal_capture.write("✅ Goal execution completed successfully!")
            
        finally:
            # Restore original stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        return jsonify({
            'success': True,
            'result': result,
            'logs': terminal_capture.logs,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        terminal_capture.write(f"❌ Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'logs': terminal_capture.logs
        }), 500

@app.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    """API endpoint to run full evaluation"""
    try:
        # Clear logs and start evaluation
        terminal_capture.logs.clear()
        terminal_capture.write("🧪 Starting comprehensive system evaluation...")
        terminal_capture.write("=" * 60)
        
        # Capture output during evaluation
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            sys.stdout = terminal_capture
            sys.stderr = terminal_capture
            
            evaluator = AgentSystemEvaluator()
            results = evaluator.run_full_evaluation()
            
            terminal_capture.write("=" * 60)
            terminal_capture.write("✅ Evaluation completed successfully!")
            
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        return jsonify({
            'success': True,
            'evaluation': results,
            'logs': terminal_capture.logs
        })
        
    except Exception as e:
        terminal_capture.write(f"❌ Evaluation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'logs': terminal_capture.logs
        }), 500

@app.route('/api/logs')
def api_logs():
    """Get current terminal logs"""
    return jsonify({
        'logs': terminal_capture.logs,
        'count': len(terminal_capture.logs)
    })

@app.route('/api/clear_logs', methods=['POST'])
def api_clear_logs():
    """Clear terminal logs"""
    terminal_capture.logs.clear()
    terminal_capture.write("🔄 Logs cleared")
    return jsonify({'success': True})

@app.route('/api/agent_status')
def agent_status():
    """Get system status and metrics"""
    try:
        # Load latest evaluation results
        import os
        import glob
        
        eval_files = glob.glob('evals/evaluation_results_*.json')
        latest_eval = None
        
        if eval_files:
            latest_file = max(eval_files, key=os.path.getctime)
            with open(latest_file, 'r') as f:
                latest_eval = json.load(f)
        
        return jsonify({
            'status': 'active',
            'latest_evaluation': latest_eval,
            'available_agents': [
                'spacex_agent',
                'weather_agent', 
                'summary_agent',
                'google_adk_agent'
            ]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
