#!/usr/bin/env python3
"""
PC MetricsX Dashboard Startup Script
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

def check_requirements():
    """Check if all required files and dependencies are available"""
    print("INFO: Checking PC MetricsX requirements...")
    
    # Check if sensor data exists
    if not os.path.exists('sensor_data_log.json'):
        print("WARNING: No sensor data found!")
        print("   Please run 'python simulate_pc_metrics.py' first to generate data")
        return False
    
    # Check if templates directory exists
    if not os.path.exists('templates/dashboard.html'):
        print("ERROR: Dashboard template not found!")
        return False
    
    # Check sensor data has content
    try:
        with open('sensor_data_log.json', 'r') as f:
            content = f.read().strip()
            
        # Handle incomplete JSON (missing closing bracket)
        if content and not content.endswith(']'):
            print("WARNING: JSON file appears incomplete (simulation may be running)")
            # Try to fix it temporarily for reading
            if content.endswith(','):
                content = content[:-1]
            content += '\n]'
            
        if content:
            data = json.loads(content)
            if len(data) < 10:
                print("WARNING: Very little sensor data available")
                print("   Consider running simulate_pc_metrics.py for more data")
            else:
                print(f"SUCCESS: Found {len(data)} sensor data points")
        else:
            print("WARNING: Sensor data file is empty")
            return False
            
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON parsing error - {e}")
        print("   Dashboard will try to handle this automatically")
    except Exception as e:
        print(f"WARNING: Could not read sensor data file - {e}")
        return False
    
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    print("INFO: Checking dependencies...")
    
    required_packages = ['flask', 'flask_socketio', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"ERROR: Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("SUCCESS: All dependencies installed")
    return True

def check_claude_api():
    """Check if Claude API is configured"""
    claude_key = os.getenv('CLAUDE_API_KEY')
    if claude_key:
        print("SUCCESS: Claude API key found - AI recommendations enabled")
    else:
        print("WARNING: Claude API key not set - using simulated AI recommendations")
        print("   Set CLAUDE_API_KEY environment variable for real AI features")

def main():
    """Main startup function"""
    print("STARTING: PC MetricsX Dashboard Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\nERROR: Dependency check failed!")
        print("Please install required packages and try again.")
        return 1
    
    # Check requirements
    if not check_requirements():
        print("\nERROR: Requirements check failed!")
        print("Please generate sensor data first:")
        print("python simulate_pc_metrics.py")
        return 1
    
    # Check Claude API
    check_claude_api()
    
    print("\nSTARTING: PC MetricsX Dashboard...")
    print("=" * 50)
    
    # Check AWS certificates
    cert_files = ['certificates/root-CA.crt', 'certificates/GamingPC4.cert.pem', 'certificates/GamingPC4.private.key']
    aws_configured = all(os.path.exists(cert) for cert in cert_files)
    
    if aws_configured:
        print("INFO: AWS IoT certificates found - AWS features enabled")
    else:
        print("WARNING: AWS IoT certificates not found - running in local mode")
    
    print("\nINFO: Dashboard will be available at:")
    print("   -> http://localhost:5000")
    print("   -> http://127.0.0.1:5000")
    
    print("\nINFO: Features available:")
    print("   [OK] Real-time PC monitoring")
    print("   [OK] Gaming-themed UI")
    print("   [OK] Interactive charts")
    print("   [OK] Component temperature tracking")
    print("   [OK] Fan speed monitoring")
    print("   [OK] System overview")
    if claude_key:
        print("   [OK] AI-powered fan curve optimization")
    else:
        print("   [WARN] Simulated AI recommendations (set CLAUDE_API_KEY for real AI)")
    if aws_configured:
        print("   [OK] AWS IoT integration")
    else:
        print("   [WARN] Local mode only (configure AWS certificates for cloud features)")
    
    print("\nINFO: Usage Tips:")
    print("   * Keep simulate_pc_metrics.py running for live data")
    print("   * Use AI optimization panel for fan curve recommendations")
    print("   * Monitor AWS connection status in header")
    print("   * Check alerts panel for system notifications")
    
    print("\n" + "=" * 50)
    print("Press Ctrl+C to stop the dashboard")
    print("=" * 50)
    
    # Start the Flask app
    try:
        import app
        app.socketio.run(app.app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n\nINFO: PC MetricsX Dashboard stopped")
        print("Thanks for using PC MetricsX!")
    except Exception as e:
        print(f"\nERROR: Error starting dashboard: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 