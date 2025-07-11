"""
Configuration file for PC Component Monitoring Simulation
AWS IoT Core connection settings
"""

# AWS IoT Core Configuration

# your AWS IoT Core endpoint
AWS_IOT_ENDPOINT = "a1wqd7zsjd6ym4-ats.iot.us-east-1.amazonaws.com"

# certificate file paths
ROOT_CA_PATH = "certificates/root-CA.crt"
CERTIFICATE_PATH = "certificates/GamingPC4.cert.pem"
PRIVATE_KEY_PATH = "certificates/GamingPC4.private.key"

# MQTT configuration
CLIENT_ID = "GamingPC4"
MQTT_TOPIC = "gamingPC/telemetry"
MQTT_PORT = 8883

# simulation configuration
SENSOR_UPDATE_INTERVAL = 1.0  # seconds between sensor readings
ENABLE_CONSOLE_OUTPUT = True   # print sensor data to console
ENABLE_LOCAL_LOGGING = True    # save data to local JSON file
LOCAL_LOG_FILE = "sensor_data_log.json"

# temperature simulation parameters (Celsius)
COMPONENT_IDLE_TEMPS = {
    'cpu': 42.0,
    'gpu': 38.0, 
    'ssd': 35.0,
    'motherboard': 33.0
}

COMPONENT_MAX_TEMPS = {
    'cpu': 88.0,
    'gpu': 85.0,
    'ssd': 70.0,
    'motherboard': 60.0
}

# fan speed parameters (RPM)
FAN_IDLE_SPEEDS = {
    'cpu_fan': 1200,
    'gpu_fan': 1000,
    'case_fan': 800
}

# gaming simulation parameters
GAMING_SESSION_START_PROBABILITY = 0.02
GAMING_WARMUP_TIME = 30
GAMING_DURATION = 120
GAMING_COOLDOWN_RATE = 0.02 