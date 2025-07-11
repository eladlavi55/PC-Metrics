#!/usr/bin/env python3
"""
PC Component Monitoring Simulation
"""

import json
import time
import random
import math
import os
from datetime import datetime

# Import our configuration
import config

# aws iot sdk - comment out if not installed yet
try:
    from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
    aws_sdk_available = True
except ImportError:
    print("WARNING: AWS IoT SDK not installed. Run: pip install AWSIoTPythonSDK")
    print("INFO: Continuing in local mode...")
    aws_sdk_available = False

class PCComponentSimulator:
    """
    Simulates PC components with temperature and fan speed behavior.
    there is also gaming session simulation.
    """
    
    def __init__(self):
        # initialize component temperatures from config
        self.cpu_temp = config.COMPONENT_IDLE_TEMPS['cpu']
        self.gpu_temp = config.COMPONENT_IDLE_TEMPS['gpu']
        self.ssd_temp = config.COMPONENT_IDLE_TEMPS['ssd']
        self.motherboard_temp = config.COMPONENT_IDLE_TEMPS['motherboard']
        
        # initialize fan speeds from config
        self.cpu_fan_rpm = config.FAN_IDLE_SPEEDS['cpu_fan']
        self.gpu_fan_rpm = config.FAN_IDLE_SPEEDS['gpu_fan']
        self.case_fan_rpm = config.FAN_IDLE_SPEEDS['case_fan']
        
        # gaming session state variables
        self.gaming_session = False
        self.gaming_intensity = 0.0  # scale from 0-1 (idle to max gaming)
        self.session_time = 0        # seconds since gaming session started
        self.cooling_phase = False   # are we cooling down after gaming?
        
        # for realistic temperature transitions
        self.ambient_temp = 22.0     # room temperature baseline
        
        print("INFO: PC Component Simulator initialized")
        print(f"   INFO: initial temps - CPU: {self.cpu_temp}°C, GPU: {self.gpu_temp}°C")
        print(f"   INFO: initial fans - CPU: {self.cpu_fan_rpm} RPM, GPU: {self.gpu_fan_rpm} RPM")
        
    def update_gaming_session(self):
        """
        Simulates the gaming session patterns with state transitions.
        """
        if not self.gaming_session:
            # random chance to start a gaming session
            if random.random() < config.GAMING_SESSION_START_PROBABILITY:
                self.gaming_session = True
                self.session_time = 0
                self.cooling_phase = False
                self.gaming_intensity = 0.1  # start with minimal load
                print("INFO: gaming session started! loading game...")
                
        else:
            self.session_time += 1
            
            if not self.cooling_phase:
                # warmup phase - gradually increase intensity
                if self.session_time <= config.GAMING_WARMUP_TIME:
                    # gradual ramp-up with some randomness
                    target_intensity = (self.session_time / config.GAMING_WARMUP_TIME) * 0.7
                    self.gaming_intensity = min(0.9, target_intensity + random.uniform(-0.1, 0.1))
                    
                # intense gaming phase - high intensity with variations
                elif self.session_time <= (config.GAMING_WARMUP_TIME + config.GAMING_DURATION):
                    # high intensity with realistic variations (different game scenes)
                    base_intensity = 0.75 + 0.2 * math.sin(self.session_time * 0.05)  # slow wave
                    scene_variation = 0.15 * math.sin(self.session_time * 0.3)        # faster changes
                    random_spikes = random.uniform(-0.1, 0.15)                        # random events
                    
                    self.gaming_intensity = max(0.5, min(1.0, base_intensity + scene_variation + random_spikes))
                    
                    # occasionally print what's happening
                    if self.session_time % 20 == 0:
                        intensity_desc = "[INTENSE]" if self.gaming_intensity > 0.8 else "[ACTIVE]"
                        print(f"   {intensity_desc} gaming (intensity: {self.gaming_intensity:.2f})")
                        
                else:
                    # time to start cooling down
                    self.cooling_phase = True
                    print("INFO: gaming session ending, starting cooldown...")
                    
            else:
                # cooling phase - gradually reduce intensity
                self.gaming_intensity = max(0, self.gaming_intensity - config.GAMING_COOLDOWN_RATE)
                if self.gaming_intensity <= 0:
                    self.gaming_session = False
                    self.session_time = 0
                    print("INFO: PC returned to idle state")
    
    def simulate_temperature_changes(self):
        """
        Updates component temperatures based on gaming load.
        """      
        time_factor = time.time() * 0.0001 
        ambient_variation = 2.0 * math.sin(time_factor)
        current_ambient = self.ambient_temp + ambient_variation
        
        cpu_gaming_load = self.gaming_intensity * 35.0    
        gpu_gaming_load = self.gaming_intensity * 40.0   
        ssd_gaming_load = self.gaming_intensity * 15.0  
        motherboard_load = self.gaming_intensity * 12.0   
        
        cpu_target = config.COMPONENT_IDLE_TEMPS['cpu'] + cpu_gaming_load + (current_ambient - 22)
        cpu_change_rate = 0.12 if self.gaming_session else 0.08 
        temp_delta = (cpu_target - self.cpu_temp) * cpu_change_rate + random.uniform(-1.2, 1.2)
        self.cpu_temp = max(25.0, min(config.COMPONENT_MAX_TEMPS['cpu'], self.cpu_temp + temp_delta))
        
        gpu_target = config.COMPONENT_IDLE_TEMPS['gpu'] + gpu_gaming_load + (current_ambient - 22)
        gpu_change_rate = 0.10 if self.gaming_session else 0.06 
        temp_delta = (gpu_target - self.gpu_temp) * gpu_change_rate + random.uniform(-1.5, 1.8)
        self.gpu_temp = max(25.0, min(config.COMPONENT_MAX_TEMPS['gpu'], self.gpu_temp + temp_delta))
        
        ssd_target = config.COMPONENT_IDLE_TEMPS['ssd'] + ssd_gaming_load + (current_ambient - 22)
        ssd_change_rate = 0.06  
        temp_delta = (ssd_target - self.ssd_temp) * ssd_change_rate + random.uniform(-0.6, 0.6)
        self.ssd_temp = max(20.0, min(config.COMPONENT_MAX_TEMPS['ssd'], self.ssd_temp + temp_delta))
        
        mb_target = config.COMPONENT_IDLE_TEMPS['motherboard'] + motherboard_load + (current_ambient - 22)
        mb_change_rate = 0.05  
        temp_delta = (mb_target - self.motherboard_temp) * mb_change_rate + random.uniform(-0.4, 0.4)
        self.motherboard_temp = max(20.0, min(config.COMPONENT_MAX_TEMPS['motherboard'], self.motherboard_temp + temp_delta))
    
    def calculate_fan_speeds(self):
        """
        Calculate fan speedsss.
        """
        if self.cpu_temp < 45:
            cpu_fan_target = 800 + (self.cpu_temp - 40) * 60
        elif self.cpu_temp < 65:
            cpu_fan_target = 1100 + (self.cpu_temp - 45) * 85
        elif self.cpu_temp < 80:
            cpu_fan_target = 2800 + (self.cpu_temp - 65) * 120
        else:
            cpu_fan_target = 4600 + (self.cpu_temp - 80) * 50
            
        if self.gpu_temp < 40:
            gpu_fan_target = max(0, 600 + (self.gpu_temp - 35) * 80)
        elif self.gpu_temp < 60:
            gpu_fan_target = 1200 + (self.gpu_temp - 40) * 70
        elif self.gpu_temp < 75:
            gpu_fan_target = 2600 + (self.gpu_temp - 60) * 90
        else:
            gpu_fan_target = 3950 + (self.gpu_temp - 75) * 60
            
        avg_temp = (self.cpu_temp + self.gpu_temp) / 2
        if avg_temp < 45:
            case_fan_target = 400 + (avg_temp - 35) * 25
        elif avg_temp < 65:
            case_fan_target = 650 + (avg_temp - 45) * 40
        else:
            case_fan_target = 1450 + (avg_temp - 65) * 55
            
        fan_response_rate = 0.15  # how quickly fans adjust to target speeds
        
        self.cpu_fan_rpm += (cpu_fan_target - self.cpu_fan_rpm) * fan_response_rate
        self.gpu_fan_rpm += (gpu_fan_target - self.gpu_fan_rpm) * fan_response_rate
        self.case_fan_rpm += (case_fan_target - self.case_fan_rpm) * fan_response_rate
        
        self.cpu_fan_rpm += random.randint(-25, 25)
        self.gpu_fan_rpm += random.randint(-20, 20)
        self.case_fan_rpm += random.randint(-15, 15)
        
        self.cpu_fan_rpm = max(0, min(4800, self.cpu_fan_rpm))
        self.gpu_fan_rpm = max(0, min(4200, self.gpu_fan_rpm))
        self.case_fan_rpm = max(0, min(2800, self.case_fan_rpm))
    
    def get_sensor_data(self):
        """
        Returns current sensor readings as a dictionary.
        """
        return {
            'timestamp': int(time.time()),
            'device_id': config.CLIENT_ID,
            'cpu_temp': round(self.cpu_temp, 1),
            'gpu_temp': round(self.gpu_temp, 1),
            'ssd_temp': round(self.ssd_temp, 1),
            'motherboard_temp': round(self.motherboard_temp, 1),
            'cpu_fan_rpm': int(self.cpu_fan_rpm),
            'gpu_fan_rpm': int(self.gpu_fan_rpm),
            'case_fan_rpm': int(self.case_fan_rpm),
            'gaming_session': self.gaming_session,
            'gaming_intensity': round(self.gaming_intensity, 2)
        }

class AWSIoTPublisher:
    """
    Handles AWS IoT Core MQTT connection and data publishing.
    """
    
    def __init__(self):
        self.client_id = config.CLIENT_ID
        self.topic = config.MQTT_TOPIC
        self.connected = False
        self.mqtt_client = None
        
        if not aws_sdk_available:
            print("WARNING: AWS IoT SDK not available - running in local mode only")
            return
            
        try:
            # initialize MQTT client with AWS IoT configuration
            self.mqtt_client = AWSIoTMQTTClient(self.client_id)
            self.mqtt_client.configureEndpoint(config.AWS_IOT_ENDPOINT, config.MQTT_PORT)
            self.mqtt_client.configureCredentials(
                config.ROOT_CA_PATH, 
                config.PRIVATE_KEY_PATH, 
                config.CERTIFICATE_PATH
            )
            
            # configure MQTT client behavior (student-friendly settings)
            self.mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
            self.mqtt_client.configureOfflinePublishQueueing(-1)  # infinite offline queue
            self.mqtt_client.configureDrainingFrequency(2)  # process queue at 2 Hz
            self.mqtt_client.configureConnectDisconnectTimeout(10)  # 10 second timeout
            self.mqtt_client.configureMQTTOperationTimeout(5)  # 5 second operation timeout
            
            print("INFO: AWS IoT MQTT Client configured successfully")
            
        except Exception as e:
            print(f"ERROR: Failed to configure AWS IoT client: {str(e)}")
            self.mqtt_client = None
    
    def connect(self):
        for p in [config.ROOT_CA_PATH, config.CERTIFICATE_PATH, config.PRIVATE_KEY_PATH]:
            print(f"Looking for file: {p} ", os.path.exists(p))
        """
        Establish connection to AWS IoT Core with error handling
        """
        if not self.mqtt_client:
            print("ERROR: AWS IoT client not available")
            return False
            
        try:
            print("INFO: Connecting to AWS IoT Core...")
            print(f"   INFO: Endpoint: {config.AWS_IOT_ENDPOINT}")
            print(f"   INFO: Client ID: {self.client_id}")
            
            self.mqtt_client.connect()
            self.connected = True
            print("SUCCESS: Successfully connected to AWS IoT Core!")
            print(f"   INFO: Will publish to topic: {self.topic}")
            return True
            
        except Exception as e:
            import traceback
            print(f"ERROR: Failed to connect to AWS IoT Core: {str(e)}")
            traceback.print_exc()  # <--- this shows the full traceback error
            print("INFO: Check your:")
            print("   - Internet connection")
            print("   - AWS IoT endpoint URL")
            print("   - Certificate file paths")
            print("   - Certificate permissions in AWS IoT Console")
            return False
    
    def publish_data(self, sensor_data):
        """
        Publish sensor data to AWS IoT Core with error handling
        """
        if not self.connected or not self.mqtt_client:
            return False
            
        try:
            # Format data as JSON
            json_payload = json.dumps(sensor_data, indent=2)
            
            # Publish with QoS 1 (guaranteed delivery)
            self.mqtt_client.publish(self.topic, json_payload, 1)
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to publish data: {str(e)}")
            return False
    
    def disconnect(self):
        """
        Cleanly disconnect from AWS IoT Core
        """
        if self.mqtt_client and self.connected:
            try:
                self.mqtt_client.disconnect()
                self.connected = False
                print("INFO: Disconnected from AWS IoT Core")
            except Exception as e:
                print(f"WARNING: Error during disconnect: {str(e)}")

def setup_local_logging():
    """
    Initialize local JSON file for data logging
    """
    if config.ENABLE_LOCAL_LOGGING:
        try:
            # Create new log file with JSON array structure
            with open(config.LOCAL_LOG_FILE, 'w') as f:
                f.write('[\n')
            print(f"INFO: Local logging enabled: {config.LOCAL_LOG_FILE}")
            return True
        except Exception as e:
            print(f"WARNING: Could not setup local logging: {str(e)}")
            return False
    return False

def log_data_locally(sensor_data, is_first_entry=False):
    """
    Append sensor data to local JSON log file
    """
    try:
        with open(config.LOCAL_LOG_FILE, 'a') as f:
            if not is_first_entry:
                f.write(',\n')
            f.write('  ' + json.dumps(sensor_data, indent=2).replace('\n', '\n  '))
        return True
    except Exception as e:
        print(f"WARNING: Local logging error: {str(e)}")
        return False

def finalize_local_log():
    """
    Close the JSON array in the log file
    """
    try:
        with open(config.LOCAL_LOG_FILE, 'a') as f:
            f.write('\n]')
        print(f"INFO: Local log finalized: {config.LOCAL_LOG_FILE}")
    except Exception as e:
        print(f"WARNING: Error finalizing log: {str(e)}")

def main():
    """
    main simulation loop - coordinates all components
    """
    print("INFO: PC Component Monitoring Simulation")
    print("=" * 65)
    print("INFO: Internet of Things - Cloud Services Project")
    print("INFO: demonstrating realistic PC sensor data with AWS IoT Core")
    print("-" * 65)
    
    # initialize simulation components
    pc_simulator = PCComponentSimulator()
    aws_publisher = AWSIoTPublisher()
    
    # setup local logging if enabled
    local_logging = setup_local_logging()
    
    # attempt AWS IoT connection (comment out these lines to test locally)
    aws_connected = False
    if aws_sdk_available:
        print("\nINFO: attempting AWS IoT Core connection...")
        aws_connected = aws_publisher.connect()
        if aws_connected:
            print("SUCCESS: AWS IoT integration active")
        else:
            print("WARNING: AWS IoT connection failed - continuing with local simulation")
    
    print("\nSTARTING: PC monitoring simulation...")
    print("INFO: sensor readings every second | gaming sessions will occur randomly")
    print("INFO: watch for temperature spikes during gaming sessions!")
    print("INFO: press Ctrl+C to stop the simulation")
    print("-" * 65)
    
    # main simulation loop
    iteration_count = 0
    last_gaming_state = False
    
    try:
        while True:
            # update PC component simulation
            pc_simulator.update_gaming_session()
            pc_simulator.simulate_temperature_changes()
            pc_simulator.calculate_fan_speeds()
            
            # get current sensor readings
            sensor_data = pc_simulator.get_sensor_data()
            
            # TODO: maybe add more sensor types later? like RAM temp or PSU temp
            
            # console output for monitoring
            current_time = datetime.now().strftime('%H:%M:%S')
            gaming_state = sensor_data['gaming_session']
            
            # print status changes or every 10 seconds
            if (iteration_count % 10 == 0 or 
                gaming_state != last_gaming_state or 
                config.ENABLE_CONSOLE_OUTPUT):
                
                # status indicator - probably could make this cleaner but it works
                if gaming_state:
                    intensity = sensor_data['gaming_intensity']
                    if intensity > 0.8:
                        status = "[INTENSE GAMING]"
                    elif intensity > 0.5:
                        status = "[ACTIVE GAMING]"
                    else:
                        status = "[LIGHT GAMING]"
                else:
                    status = "[IDLE]"
                
                # temperature status
                cpu_temp = sensor_data['cpu_temp']
                gpu_temp = sensor_data['gpu_temp']
                temp_status = ""  # this could be done better with a function
                if cpu_temp > 75 or gpu_temp > 75:
                    temp_status = "[HOT]"
                elif cpu_temp > 60 or gpu_temp > 60:
                    temp_status = "[WARM]"
                else:
                    temp_status = "[COOL]"
                
                print(f"[{current_time}] {status} {temp_status}")
                print(f"  CPU: {cpu_temp}°C ({sensor_data['cpu_fan_rpm']} RPM) | "
                      f"GPU: {gpu_temp}°C ({sensor_data['gpu_fan_rpm']} RPM)")
                print(f"  SSD: {sensor_data['ssd_temp']}°C | "
                      f"MB: {sensor_data['motherboard_temp']}°C | "
                      f"Case: {sensor_data['case_fan_rpm']} RPM")
                
                if gaming_state:
                    print(f"  Gaming intensity: {sensor_data['gaming_intensity']:.1%}")
                print()
            
            # publish to AWS IoT Core
            if aws_connected:
                success = aws_publisher.publish_data(sensor_data)
                if success and iteration_count % 30 == 0:  # confirm every 30 seconds
                    print(f"SUCCESS: data published to AWS IoT topic: {aws_publisher.topic}")
            
            # log data locally
            if local_logging:
                log_data_locally(sensor_data, iteration_count == 0)
            
            # track state changes
            last_gaming_state = gaming_state
            iteration_count += 1
            
            # wait for next sensor reading - maybe could optimize this but works fine
            time.sleep(config.SENSOR_UPDATE_INTERVAL)
            
            # debug: print iteration count every 100 iterations (might remove later)
            if iteration_count % 100 == 0:
                print(f"   debug: completed {iteration_count} iterations")
            
    except KeyboardInterrupt:
        print("\nINFO: Simulation stopped by user")
        
    except Exception as e:
        print(f"\nERROR: Simulation error: {str(e)}")
        
    finally:
        # cleanup
        print("\nINFO: cleaning up...")
        
        if aws_connected:
            aws_publisher.disconnect()
            
        if local_logging:
            finalize_local_log()
            
        print("INFO: PC component monitoring simulation ended")
        print(f"INFO: total sensor readings collected: {iteration_count}")
        
        # TODO: maybe add some stats here like avg temp, max temp, etc

if __name__ == "__main__":
    main() 