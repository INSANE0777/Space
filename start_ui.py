# start_ui.py
# Quick start script for the Multi-Agent AI System Web Interface

import os
import sys
import subprocess
import webbrowser
import time

def check_environment():
    """Check if the environment is properly set up"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file with your API keys.")
        return False
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_keys = ['WEATHER_API_KEY', 'GOOGLE_API_KEY']
        missing_keys = []
        
        for key in required_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        if missing_keys:
            print(f"❌ Missing API keys: {', '.join(missing_keys)}")
            return False
            
        print("✅ Environment check passed!")
        return True
        
    except ImportError:
        print("❌ Required packages not installed. Run: pip install -r requirements.txt")
        return False

def start_web_interface():
    """Start the Flask web interface"""
    print("🚀 Starting Multi-Agent AI System Web Interface...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("⏳ Starting server...")
    
    try:
        # Start Flask app
        subprocess.run([sys.executable, 'web_interface.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

if __name__ == "__main__":
    print("🧠 Multi-Agent AI System - Web Interface Launcher")
    print("=" * 50)
    
    if check_environment():
        print("\n🌐 Opening web browser...")
        # Open browser after a short delay
        import threading
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        start_web_interface()
    else:
        print("\n🔧 Please fix the environment issues and try again.")
        sys.exit(1)
