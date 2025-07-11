#!/usr/bin/env python3
"""
PC MetricsX - Gaming PC Monitoring Dashboard
Real-time monitoring with AI-powered fan curve optimization
Elad Lavi 205576440
Course: Internet of Things
"""


CLAUDE_API_KEY = "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"

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import threading
import time
from datetime import datetime, timedelta
import os
from config import *
from claude_ai import ClaudeAIOptimizer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pc-metricsX-dashboard-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

#  variables for dashboard state
current_sensor_data = {}
sensor_history = []
aws_connection_status = False
ai_recommendations = {}
alert_messages = []

claude_optimizer = ClaudeAIOptimizer()

COMPONENT_MODELS = {
    'cpu': 'AMD Ryzen 9 7950X3D',
    'gpu': 'NVIDIA RTX 4090',
    'ssd': 'Samsung 980 PRO 2TB',
    'motherboard': 'ASUS ROG Strix X670E-E',
    'cpu_fan': 'Noctua NH-D15 chromax.black',
    'gpu_fan': 'Built-in Triple Axial',
    'case_fan': 'Corsair iCUE QL120 RGB'
}

def load_sensor_data():
    """Load recent sensor data from JSON log file"""
    global sensor_history, current_sensor_data
    
    try:
        with open(LOCAL_LOG_FILE, 'r') as f:
            content = f.read().strip()
            
        # Handle incomplete JSON
        if content and not content.endswith(']'):
            if content.endswith(','):
                content = content[:-1]
            content += '\n]'
            
        if content:
            data = json.loads(content)
        else:
            data = []
            
        sensor_history = data[-1000:] if len(data) > 1000 else data

        if sensor_history:
            current_sensor_data = sensor_history[-1]
            
        print(f"SUCCESS: Loaded {len(sensor_history)} sensor data points")
        
    except FileNotFoundError:
        print("WARNING: No sensor data file found. Please run simulate_pc_metrics.py first")
        sensor_history = []
        current_sensor_data = {}
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON parsing error: {e}")
        try:
            sensor_history = load_sensor_data_fallback()
            if sensor_history:
                current_sensor_data = sensor_history[-1]
                print(f"SUCCESS: Fallback loaded {len(sensor_history)} sensor data points")
            else:
                current_sensor_data = {}
        except Exception as fallback_error:
            print(f"WARNING: Fallback loading failed: {fallback_error}")
            sensor_history = []
            current_sensor_data = {}
    except Exception as e:
        print(f"WARNING: Error loading sensor data: {e}")
        sensor_history = []
        current_sensor_data = {}

def load_sensor_data_fallback():
    """Fallback method to load sensor data when JSON is corrupted"""
    try:
        with open(LOCAL_LOG_FILE, 'r') as f:
            content = f.read()
            
        # Try to extract JSON objects from the content
        lines = content.split('\n')
        json_objects = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                try:
                    obj = json.loads(line)
                    json_objects.append(obj)
                except json.JSONDecodeError:
                    continue
            elif line.startswith('{') and line.endswith(','):
                try:
                    obj = json.loads(line[:-1])
                    json_objects.append(obj)
                except json.JSONDecodeError:
                    continue
        
        return json_objects
        
    except Exception as e:
        print(f"WARNING: Fallback loading error: {e}")
        return []

def check_aws_connection():
    """Check AWS IoT connection status"""
    global aws_connection_status
    
    try:
        cert_exists = (os.path.exists(CERTIFICATE_PATH) and 
                      os.path.exists(PRIVATE_KEY_PATH) and 
                      os.path.exists(ROOT_CA_PATH))
        
        # Additional check: verify recent data updates
        if sensor_history:
            last_update = datetime.fromtimestamp(sensor_history[-1]['timestamp'])
            time_diff = datetime.now() - last_update
            data_fresh = time_diff.total_seconds() < 60
            
            aws_connection_status = cert_exists and data_fresh
        else:
            aws_connection_status = False
            
    except Exception as e:
        print(f"WARNING: Error checking AWS connection: {e}")
        aws_connection_status = False

def generate_ai_fan_curves(preference='balanced', sensor_data_sample=None):
    """
    Generate AI-powered fan curve recommendations using Claude API
    """
    global ai_recommendations
    
    if not sensor_data_sample:
        sensor_data_sample = sensor_history[-100:] if len(sensor_history) >= 100 else sensor_history
    
    if not sensor_data_sample:
        return {"error": "No data available for analysis"}
    
    # Claude AI optimizerrr
    analysis = claude_optimizer.analyze_temperature_data(sensor_data_sample)
    ai_recommendations = claude_optimizer.generate_fan_curves(analysis, preference)
    
    return ai_recommendations

def analyze_temperature_patterns(data):
    """Analyze temperature patterns from sensor data"""
    if not data:
        return {}
    
    cpu_temps = [d['cpu_temp'] for d in data]
    gpu_temps = [d['gpu_temp'] for d in data]
    gaming_sessions = sum(1 for d in data if d.get('gaming_session', False))
    
    return {
        'cpu': {
            'avg': sum(cpu_temps) / len(cpu_temps),
            'max': max(cpu_temps),
            'min': min(cpu_temps)
        },
        'gpu': {
            'avg': sum(gpu_temps) / len(gpu_temps),
            'max': max(gpu_temps),
            'min': min(gpu_temps)
        },
        'gaming_sessions': gaming_sessions
    }

def generate_simulated_recommendations(preference, temp_analysis):
    """Generate simulated AI recommendations (replace with actual Claude API)"""
    
    base_curves = {
        'best_temps': {
            'cpu_fan': [800, 1200, 2000, 3500, 4500],
            'gpu_fan': [0, 1000, 2200, 3800, 4200],
            'case_fan': [600, 900, 1400, 2200, 2800]
        },
        'most_quiet': {
            'cpu_fan': [600, 900, 1400, 2200, 3000],
            'gpu_fan': [0, 800, 1600, 2800, 3200],
            'case_fan': [400, 600, 1000, 1600, 2000]
        },
        'balanced': {
            'cpu_fan': [700, 1000, 1700, 2800, 3800],
            'gpu_fan': [0, 900, 1900, 3200, 3700],
            'case_fan': [500, 750, 1200, 1900, 2400]
        }
    }
    
    return {
        'preference': preference,
        'fan_curves': base_curves[preference],
        'analysis': temp_analysis,
        'recommendations': {
            'cpu': f"Your {COMPONENT_MODELS['cpu']} runs at avg {temp_analysis['cpu']['avg']:.1f}°C",
            'gpu': f"Your {COMPONENT_MODELS['gpu']} reaches {temp_analysis['gpu']['max']:.1f}°C max",
            'gaming': f"Detected {temp_analysis['gaming_sessions']} gaming sessions in data sample"
        },
        'timestamp': datetime.now().isoformat()
    }

def background_data_monitor():
    """Background thread to monitor data updates and AWS connection"""
    while True:
        try:
            load_sensor_data()
            check_aws_connection()
            
            # Emit real-time updates to connected clients
            if current_sensor_data:
                socketio.emit('sensor_update', {
                    'data': current_sensor_data,
                    'aws_status': aws_connection_status,
                    'component_models': COMPONENT_MODELS
                })
                
        except Exception as e:
            print(f"WARNING: Error in background monitor: {e}")
            
        time.sleep(2)  # Update every 2 sec

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html', 
                         component_models=COMPONENT_MODELS)

@app.route('/api/current_data')
def api_current_data():
    """API endpoint for current sensor data"""
    return jsonify({
        'current_data': current_sensor_data,
        'aws_connected': aws_connection_status,
        'component_models': COMPONENT_MODELS,
        'alerts': alert_messages
    })

@app.route('/api/history_data')
def api_history_data():
    """API endpoint for historical sensor data"""
    # Get last N minutes of data
    minutes = int(request.args.get('minutes', 30))
    cutoff_time = time.time() - (minutes * 60)
    
    filtered_data = [d for d in sensor_history if d['timestamp'] >= cutoff_time]
    
    return jsonify({
        'history': filtered_data,
        'total_points': len(filtered_data)
    })

@app.route('/api/ai_recommendations', methods=['POST'])
def api_ai_recommendations():
    """API endpoint for AI fan curve recommendations"""
    try:
        data = request.get_json()
        preference = data.get('preference', 'balanced')
        
        # Generate AI recommendations
        recommendations = generate_ai_fan_curves(preference)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts')
def api_alerts():
    """API endpoint for system alerts"""
    return jsonify({
        'alerts': alert_messages,
        'aws_status': aws_connection_status
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('INFO: Client connected to PC MetricsX dashboard')
    emit('connection_status', {'connected': True})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('INFO: Client disconnected from dashboard')

if __name__ == '__main__':
    print("STARTING: PC MetricsX Dashboard...")
    print("INFO: Gaming PC Monitoring with AI Recommendations")
    
    # Load initial data
    load_sensor_data()
    check_aws_connection()

    monitor_thread = threading.Thread(target=background_data_monitor, daemon=True)
    monitor_thread.start()
    
    print("SUCCESS: Dashboard ready at http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True) 