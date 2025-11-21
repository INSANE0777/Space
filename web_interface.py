# web_interface.py
# Interactive Web UI for Multi-Agent AI System

from flask import Flask, render_template, request, jsonify, stream_template, send_file
import json
import time
from main import run_goal, run_goal_realtime, REALTIME_AVAILABLE
import sys
import os
from automated_evaluation import AgentSystemEvaluator
import io
from contextlib import redirect_stdout, redirect_stderr
from scheduler import start_scheduler_from_config
from notifications import notification_center

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
latest_result = None
scheduler_instance = start_scheduler_from_config()


def build_workflow_logs(log_entries):
    workflow_logs = []
    for log in log_entries:
        log_msg = log['message']
        agent_type = None

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
    return workflow_logs

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
        global latest_result
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
        
        global latest_result

        # Capture stdout/stderr while running the goal
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            # Redirect output to our capture
            sys.stdout = terminal_capture
            sys.stderr = terminal_capture
            
            # Check if real-time mode is requested
            use_realtime = data.get('realtime', False) and REALTIME_AVAILABLE
            if use_realtime:
                terminal_capture.write("🚀 Real-time mode enabled - breaking problem into sub-tasks...")
                result = run_goal_realtime(message)
            else:
                result = run_goal(message)
            latest_result = result
            
            terminal_capture.write("=" * 60)
            terminal_capture.write("✅ Task completed successfully!")
            
        finally:
            # Restore original stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        # Process logs to extract agent-specific information
        workflow_logs = build_workflow_logs(terminal_capture.logs)
        
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
            
            # Check if real-time mode is requested
            use_realtime = data.get('realtime', False) and REALTIME_AVAILABLE
            if use_realtime:
                terminal_capture.write("🚀 Real-time mode enabled - breaking problem into sub-tasks...")
                result = run_goal_realtime(goal)
            else:
                result = run_goal(goal)
            latest_result = result
            
            terminal_capture.write("=" * 60)
            terminal_capture.write("✅ Goal execution completed successfully!")
            
        finally:
            # Restore original stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        workflow_logs = build_workflow_logs(terminal_capture.logs)
        
        return jsonify({
            'success': True,
            'result': result,
            'logs': terminal_capture.logs,
            'workflow_logs': workflow_logs,
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
                'calculator_agent',
                'dictionary_agent',
                'news_agent',
                'google_adk_agent'
            ],
            'scheduler_enabled': scheduler_instance is not None,
            'realtime_available': REALTIME_AVAILABLE
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })


@app.route('/api/notifications')
def get_notifications():
    return jsonify({
        'notifications': notification_center.list_events()
    })


@app.route('/api/schedules')
def list_schedules():
    if not scheduler_instance:
        return jsonify({'enabled': False, 'tasks': []})
    return jsonify({
        'enabled': True,
        'tasks': scheduler_instance.list_tasks()
    })


@app.route('/api/report/latest')
def download_report():
    if not latest_result:
        return jsonify({'error': 'No runs recorded yet'}), 404
    return jsonify({
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'result': latest_result
    })


@app.route('/system-diagram')
def serve_system_diagram():
    diagram_path = os.path.join('docs', 'WorkFlow_Diagram.png')
    if os.path.exists(diagram_path):
        return send_file(diagram_path, mimetype='image/png')
    return jsonify({'error': 'Diagram not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
