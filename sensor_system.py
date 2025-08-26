import time
import random
import math
from datetime import datetime, timedelta
import json
import os

class MockSensorSystem:
    def __init__(self):
        self.sensors = {
            'Sungai Inanam': {
                'location': 'Sabah, Kota Kinabalu',
                'coordinates': (5.997846609055653, 116.12997039272707),
                'is_coastal': True,
                'base_water_level': 1.8,
                'base_flow_rate': 150,
                'seasonal_factor': 1.0
            },
            'Sungai Klang': {
                'location': 'Selangor, Klang Valley',
                'coordinates': (3.0179012973130344, 101.37692352872754),
                'is_coastal': True,
                'base_water_level': 2.2,
                'base_flow_rate': 180,
                'seasonal_factor': 1.2
            },
            'Sungai Pinang': {
                'location': 'Penang, George Town',
                'coordinates': (5.403345957392342, 100.33223539657536),
                'is_coastal': True,
                'base_water_level': 1.5,
                'base_flow_rate': 140,
                'seasonal_factor': 0.9
            }
        }
        
        self.last_update = datetime.now()
        self.sensor_failures = {}  # Track sensor failures
        
    def get_tidal_factor(self, river_name, timestamp):
        """Simulate Malaysian tidal patterns (2 high/2 low tides per day)"""
        if not self.sensors[river_name]['is_coastal']:
            return 0
            
        # Malaysian tidal cycle (approximately 12.4 hours)
        tidal_period = 12.4 * 3600  # seconds
        time_since_epoch = timestamp.timestamp()
        tidal_phase = (time_since_epoch % tidal_period) / tidal_period
        
        # Create realistic tidal pattern
        tidal_factor = math.sin(2 * math.pi * tidal_phase) * 0.8 + 0.2
        return tidal_factor
    
    def get_seasonal_factor(self, river_name, timestamp):
        """Simulate monsoon vs dry season patterns"""
        month = timestamp.month
        
        # Monsoon season (October-March) - higher water levels
        if month in [10, 11, 12, 1, 2, 3]:
            monsoon_factor = 1.3
        else:
            monsoon_factor = 0.8
            
        return monsoon_factor * self.sensors[river_name]['seasonal_factor']
    
    def simulate_sensor_failure(self, river_name, sensor_type):
        """Simulate occasional sensor failures"""
        if river_name not in self.sensor_failures:
            self.sensor_failures[river_name] = {}
            
        if sensor_type not in self.sensor_failures[river_name]:
            self.sensor_failures[river_name][sensor_type] = {
                'last_failure': None,
                'failure_duration': 0
            }
        
        sensor = self.sensor_failures[river_name][sensor_type]
        now = datetime.now()
        
        # 2% chance of sensor failure per update
        if random.random() < 0.02:
            sensor['last_failure'] = now
            sensor['failure_duration'] = random.randint(5, 30)  # 5-30 minutes
        
        # Check if sensor is currently failed
        if sensor['last_failure']:
            time_since_failure = (now - sensor['last_failure']).total_seconds() / 60
            if time_since_failure < sensor['failure_duration']:
                return True
            else:
                sensor['last_failure'] = None
                sensor['failure_duration'] = 0
                
        return False
    
    def get_water_level(self, river_name, timestamp):
        """Get realistic water level with tidal and seasonal patterns"""
        if self.simulate_sensor_failure(river_name, 'water_level'):
            return None
            
        base_level = self.sensors[river_name]['base_water_level']
        tidal_factor = self.get_tidal_factor(river_name, timestamp)
        seasonal_factor = self.get_seasonal_factor(river_name, timestamp)
        
        # Add gradual variation (±5%)
        variation = random.uniform(-0.05, 0.05)
        
        water_level = base_level * (1 + tidal_factor * 0.3) * seasonal_factor * (1 + variation)
        
        # Ensure realistic range
        water_level = max(0.5, min(8.0, water_level))
        
        return round(water_level, 2)
    
    def get_flow_rate(self, river_name, timestamp):
        """Get realistic water flow rate"""
        if self.simulate_sensor_failure(river_name, 'flow_rate'):
            return None
            
        base_flow = self.sensors[river_name]['base_flow_rate']
        seasonal_factor = self.get_seasonal_factor(river_name, timestamp)
        
        # Add gradual variation (±5%)
        variation = random.uniform(-0.05, 0.05)
        
        flow_rate = base_flow * seasonal_factor * (1 + variation)
        
        # Ensure realistic range
        flow_rate = max(50, min(500, flow_rate))
        
        return round(flow_rate, 1)
    
    def get_tide_level(self, river_name, timestamp):
        """Get tide level for coastal rivers"""
        if not self.sensors[river_name]['is_coastal']:
            return None
            
        if self.simulate_sensor_failure(river_name, 'tide_level'):
            return None
            
        tidal_factor = self.get_tidal_factor(river_name, timestamp)
        tide_level = 1.5 + tidal_factor * 1.0  # Base 1.5m ± 1.0m
        
        return round(tide_level, 2)
    
    def get_all_sensor_data(self):
        """Get current sensor data for all rivers"""
        timestamp = datetime.now()
        data = {}
        
        for river_name, river_info in self.sensors.items():
            data[river_name] = {
                'location': river_info['location'],
                'coordinates': river_info['coordinates'],
                'timestamp': timestamp.isoformat(),
                'water_level': self.get_water_level(river_name, timestamp),
                'flow_rate': self.get_flow_rate(river_name, timestamp),
                'tide_level': self.get_tide_level(river_name, timestamp),
                'sensor_status': {
                    'water_level': 'online' if self.get_water_level(river_name, timestamp) is not None else 'offline',
                    'flow_rate': 'online' if self.get_flow_rate(river_name, timestamp) is not None else 'offline',
                    'tide_level': 'online' if self.get_tide_level(river_name, timestamp) is not None else 'offline'
                }
            }
        
        self.last_update = timestamp
        return data
    
    def get_sensor_data_for_river(self, river_name):
        """Get sensor data for a specific river"""
        if river_name not in self.sensors:
            return None
            
        timestamp = datetime.now()
        
        return {
            'river_name': river_name,
            'location': self.sensors[river_name]['location'],
            'coordinates': self.sensors[river_name]['coordinates'],
            'timestamp': timestamp.isoformat(),
            'water_level': self.get_water_level(river_name, timestamp),
            'flow_rate': self.get_flow_rate(river_name, timestamp),
            'tide_level': self.get_tide_level(river_name, timestamp),
            'sensor_status': {
                'water_level': 'online' if self.get_water_level(river_name, timestamp) is not None else 'offline',
                'flow_rate': 'online' if self.get_flow_rate(river_name, timestamp) is not None else 'offline',
                'tide_level': 'online' if self.get_tide_level(river_name, timestamp) is not None else 'offline'
            }
        }

# Global sensor system instance
sensor_system = MockSensorSystem()
