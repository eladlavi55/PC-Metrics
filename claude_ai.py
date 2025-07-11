#!/usr/bin/env python3
"""
Claude AI Integration for PC MetricsX
Provides intelligent fan curve recommendations based on data analysis.
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class ClaudeAIOptimizer:
    """
    AI-powered fan curve optimizer using Claude API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-sonnet-20240229"
        
        if not self.api_key:
            print("WARNING: Claude API key not found. Using simulated AI recommendations.")
            self.use_simulation = True
        else:
            print("SUCCESS: Claude AI optimizer initialized")
            self.use_simulation = False
    
    def analyze_temperature_data(self, sensor_data: List[Dict]) -> Dict:
        """
        Analyze temperature patterns from sensor data
        """
        if not sensor_data:
            return {}
        
        # Extract temperature data
        cpu_temps = [d.get('cpu_temp', 0) for d in sensor_data]
        gpu_temps = [d.get('gpu_temp', 0) for d in sensor_data]
        ssd_temps = [d.get('ssd_temp', 0) for d in sensor_data]
        mb_temps = [d.get('motherboard_temp', 0) for d in sensor_data]
        
        # Extract fan data
        cpu_fan_rpms = [d.get('cpu_fan_rpm', 0) for d in sensor_data]
        gpu_fan_rpms = [d.get('gpu_fan_rpm', 0) for d in sensor_data]
        case_fan_rpms = [d.get('case_fan_rpm', 0) for d in sensor_data]
        
        # Gaming session analysis
        gaming_sessions = sum(1 for d in sensor_data if d.get('gaming_session', False))
        gaming_intensity_avg = sum(d.get('gaming_intensity', 0) for d in sensor_data) / len(sensor_data)
        
        # Calculate statistics
        analysis = {
            'cpu': {
                'avg': sum(cpu_temps) / len(cpu_temps),
                'max': max(cpu_temps),
                'min': min(cpu_temps),
                'std': self._calculate_std(cpu_temps)
            },
            'gpu': {
                'avg': sum(gpu_temps) / len(gpu_temps),
                'max': max(gpu_temps),
                'min': min(gpu_temps),
                'std': self._calculate_std(gpu_temps)
            },
            'ssd': {
                'avg': sum(ssd_temps) / len(ssd_temps),
                'max': max(ssd_temps),
                'min': min(ssd_temps),
                'std': self._calculate_std(ssd_temps)
            },
            'motherboard': {
                'avg': sum(mb_temps) / len(mb_temps),
                'max': max(mb_temps),
                'min': min(mb_temps),
                'std': self._calculate_std(mb_temps)
            },
            'fans': {
                'cpu_fan': {
                    'avg': sum(cpu_fan_rpms) / len(cpu_fan_rpms),
                    'max': max(cpu_fan_rpms),
                    'min': min(cpu_fan_rpms)
                },
                'gpu_fan': {
                    'avg': sum(gpu_fan_rpms) / len(gpu_fan_rpms),
                    'max': max(gpu_fan_rpms),
                    'min': min(gpu_fan_rpms)
                },
                'case_fan': {
                    'avg': sum(case_fan_rpms) / len(case_fan_rpms),
                    'max': max(case_fan_rpms),
                    'min': min(case_fan_rpms)
                }
            },
            'gaming': {
                'sessions': gaming_sessions,
                'avg_intensity': gaming_intensity_avg,
                'gaming_percentage': (gaming_sessions / len(sensor_data)) * 100
            },
            'data_points': len(sensor_data),
            'time_span_hours': self._calculate_time_span(sensor_data)
        }
        
        return analysis
    
    def generate_fan_curves(self, analysis: Dict, preference: str = 'balanced') -> Dict:
        """
        Generate optimized fan curves using Claude AI or simulation
        """
        if self.use_simulation:
            return self._generate_simulated_curves(analysis, preference)
        else:
            return self._generate_claude_curves(analysis, preference)
    
    def _generate_claude_curves(self, analysis: Dict, preference: str) -> Dict:
        """
        Generate fan curves using Claude AI API
        """
        try:
            # Prepare the prompt for Claude
            prompt = self._build_claude_prompt(analysis, preference)
            
            # Make API request to Claude
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': self.api_key,
                'anthropic-version': '2023-06-01'
            }
            
            payload = {
                'model': self.model,
                'max_tokens': 1000,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                claude_response = result['content'][0]['text']
                
                # Parse Claude's response
                return self._parse_claude_response(claude_response, analysis, preference)
            else:
                print(f"WARNING: Claude API error: {response.status_code}")
                return self._generate_simulated_curves(analysis, preference)
                
        except Exception as e:
            print(f"WARNING: Claude AI error: {e}")
            return self._generate_simulated_curves(analysis, preference)
    
    def _build_claude_prompt(self, analysis: Dict, preference: str) -> str:
        """
        Build the prompt for Claude AI
        """
        prompt = f"""
        You are an expert PC cooling specialist. Analyze this gaming PC's temperature data and provide optimized fan curve recommendations.

        SYSTEM SPECIFICATIONS:
        - CPU: {analysis.get('cpu', {}).get('avg', 'High-end Gaming CPU')}
        - GPU: {analysis.get('gpu', {}).get('avg', 'High-end Gaming GPU')}
        - CPU Cooler: {analysis.get('fans', {}).get('cpu_fan', {}).get('avg', 'High-performance Air Cooler')}
        - Case: Gaming case with good airflow

        TEMPERATURE ANALYSIS ({analysis.get('data_points', 0)} data points over {analysis.get('time_span_hours', 0):.1f} hours):
        - CPU: Avg {analysis['cpu']['avg']:.1f}°C, Max {analysis['cpu']['max']:.1f}°C, Min {analysis['cpu']['min']:.1f}°C
        - GPU: Avg {analysis['gpu']['avg']:.1f}°C, Max {analysis['gpu']['max']:.1f}°C, Min {analysis['gpu']['min']:.1f}°C
        - SSD: Avg {analysis['ssd']['avg']:.1f}°C, Max {analysis['ssd']['max']:.1f}°C
        - Motherboard: Avg {analysis['motherboard']['avg']:.1f}°C, Max {analysis['motherboard']['max']:.1f}°C

        CURRENT FAN PERFORMANCE:
        - CPU Fan: Avg {analysis['fans']['cpu_fan']['avg']:.0f} RPM, Max {analysis['fans']['cpu_fan']['max']:.0f} RPM
        - GPU Fan: Avg {analysis['fans']['gpu_fan']['avg']:.0f} RPM, Max {analysis['fans']['gpu_fan']['max']:.0f} RPM
        - Case Fan: Avg {analysis['fans']['case_fan']['avg']:.0f} RPM, Max {analysis['fans']['case_fan']['max']:.0f} RPM

        GAMING USAGE:
        - Gaming sessions: {analysis['gaming']['sessions']} ({analysis['gaming']['gaming_percentage']:.1f}% of time)
        - Average gaming intensity: {analysis['gaming']['avg_intensity']:.2f}

        USER PREFERENCE: {preference}
        - 'balanced': Balance between cooling performance and noise
        - 'best_temps': Prioritize lowest temperatures (aggressive cooling)
        - 'most_quiet': Prioritize noise reduction (conservative cooling)

        Please provide optimized fan curves for each component:
        1. CPU Fan curve (RPM values for: 30°C, 50°C, 70°C, 85°C, 95°C)
        2. GPU Fan curve (RPM values for: 30°C, 50°C, 70°C, 85°C, 90°C)
        3. Case Fan curve (RPM values for: 30°C, 50°C, 70°C, 85°C, 90°C)

        Also provide:
        - Analysis of current cooling efficiency
        - Specific recommendations for this user's usage pattern
        - Expected temperature improvements
        - Noise level considerations

        Format your response as JSON with the following structure:
        {{
            "fan_curves": {{
                "cpu_fan": [rpm1, rpm2, rpm3, rpm4, rpm5],
                "gpu_fan": [rpm1, rpm2, rpm3, rpm4, rpm5],
                "case_fan": [rpm1, rpm2, rpm3, rpm4, rpm5]
            }},
            "analysis": {{
                "efficiency": "Current cooling efficiency assessment",
                "recommendations": "Specific recommendations",
                "temperature_improvement": "Expected improvements",
                "noise_impact": "Noise level considerations"
            }}
        }}
        """
        
        return prompt
    
    def _parse_claude_response(self, response: str, analysis: Dict, preference: str) -> Dict:
        """
        Parse Claude's JSON response
        """
        try:
            # Try to extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                claude_data = json.loads(json_str)
                
                return {
                    'preference': preference,
                    'fan_curves': claude_data.get('fan_curves', {}),
                    'analysis': analysis,
                    'claude_analysis': claude_data.get('analysis', {}),
                    'recommendations': {
                        'efficiency': claude_data.get('analysis', {}).get('efficiency', 'Analysis complete'),
                        'recommendations': claude_data.get('analysis', {}).get('recommendations', 'Optimized for your usage'),
                        'temperature_improvement': claude_data.get('analysis', {}).get('temperature_improvement', 'Improved cooling expected'),
                        'noise_impact': claude_data.get('analysis', {}).get('noise_impact', 'Balanced noise levels')
                    },
                    'timestamp': datetime.now().isoformat(),
                    'ai_generated': True
                }
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            print(f"WARNING: Error parsing Claude response: {e}")
            # Fallback to simulated curves
            return self._generate_simulated_curves(analysis, preference)
    
    def _generate_simulated_curves(self, analysis: Dict, preference: str) -> Dict:
        """
        Generate simulated fan curves when Claude AI is not available
        """
        # Base fan curves for different preferences
        base_curves = {
            'best_temps': {
                'cpu_fan': [800, 1400, 2200, 3600, 4500],
                'gpu_fan': [0, 1200, 2400, 3900, 4200],
                'case_fan': [600, 1000, 1600, 2400, 2800]
            },
            'most_quiet': {
                'cpu_fan': [600, 1000, 1600, 2400, 3200],
                'gpu_fan': [0, 800, 1800, 3000, 3400],
                'case_fan': [400, 700, 1200, 1800, 2200]
            },
            'balanced': {
                'cpu_fan': [700, 1200, 1900, 3000, 3800],
                'gpu_fan': [0, 1000, 2100, 3400, 3800],
                'case_fan': [500, 850, 1400, 2100, 2500]
            }
        }
        
        # Adjust curves based on analysis
        curves = base_curves[preference].copy()
        
        # If temperatures are consistently high, increase fan speeds
        if analysis.get('cpu', {}).get('avg', 0) > 70:
            curves['cpu_fan'] = [rpm + 200 for rpm in curves['cpu_fan']]
        if analysis.get('gpu', {}).get('avg', 0) > 75:
            curves['gpu_fan'] = [rpm + 200 for rpm in curves['gpu_fan']]
            
        # If gaming intensity is high, boost cooling
        if analysis.get('gaming', {}).get('avg_intensity', 0) > 0.7:
            curves['case_fan'] = [rpm + 150 for rpm in curves['case_fan']]
        
        return {
            'preference': preference,
            'fan_curves': curves,
            'analysis': analysis,
            'recommendations': {
                'cpu': f"CPU averaging {analysis.get('cpu', {}).get('avg', 0):.1f}°C - " + 
                       ("aggressive cooling recommended" if analysis.get('cpu', {}).get('avg', 0) > 70 else "current cooling adequate"),
                'gpu': f"GPU reaching {analysis.get('gpu', {}).get('max', 0):.1f}°C max - " + 
                       ("enhanced cooling suggested" if analysis.get('gpu', {}).get('max', 0) > 80 else "cooling performance good"),
                'gaming': f"Gaming detected {analysis.get('gaming', {}).get('gaming_percentage', 0):.1f}% of time - " + 
                         ("optimized for gaming workloads" if analysis.get('gaming', {}).get('gaming_percentage', 0) > 30 else "general usage optimization")
            },
            'timestamp': datetime.now().isoformat(),
            'ai_generated': False
        }
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if not values:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _calculate_time_span(self, sensor_data: List[Dict]) -> float:
        """Calculate time span of data in hours"""
        if len(sensor_data) < 2:
            return 0
        
        timestamps = [d.get('timestamp', 0) for d in sensor_data]
        time_span_seconds = max(timestamps) - min(timestamps)
        return time_span_seconds / 3600  # Convert to hours

# Example usage
if __name__ == "__main__":
    # Example sensor data
    sample_data = [
        {
            "timestamp": 1750263292,
            "cpu_temp": 45.2,
            "gpu_temp": 42.1,
            "ssd_temp": 38.5,
            "motherboard_temp": 35.2,
            "cpu_fan_rpm": 1450,
            "gpu_fan_rpm": 1200,
            "case_fan_rpm": 900,
            "gaming_session": False,
            "gaming_intensity": 0.0
        }
    ]
    
    # Initialize optimizer
    optimizer = ClaudeAIOptimizer()
    
    # Analyze data
    analysis = optimizer.analyze_temperature_data(sample_data)
    print("Analysis:", json.dumps(analysis, indent=2))
    
    # Generate recommendations
    recommendations = optimizer.generate_fan_curves(analysis, 'balanced')
    print("Recommendations:", json.dumps(recommendations, indent=2)) 