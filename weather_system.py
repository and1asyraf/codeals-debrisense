import requests
import json
from datetime import datetime, timedelta
import time

class WeatherSystem:
    def __init__(self):
        # You'll need to get a free API key from https://www.weatherapi.com/
        # Sign up and get your free API key (1000 requests per month)
        self.api_key = "84b6782ee30a4551acc83954252608"  # Your real WeatherAPI.com key
        self.base_url = "http://api.weatherapi.com/v1"
        self.cache = {}
        self.cache_duration = 3600  # 1 hour cache
        self.last_api_call = 0
        self.api_call_interval = 1  # 1 second between API calls to respect rate limits
        
    def get_api_key_instructions(self):
        """Return instructions for getting API key"""
        return {
            "message": "To use weather forecasts, you need a free API key from WeatherAPI.com",
            "steps": [
                "1. Go to https://www.weatherapi.com/",
                "2. Click 'Sign Up' and create a free account",
                "3. Get your API key from the dashboard",
                "4. Replace 'YOUR_WEATHER_API_KEY_HERE' in weather_system.py with your actual key",
                "5. Free tier includes 1,000,000 calls per month"
            ],
            "current_status": "API key configured and ready"
        }
    
    def make_api_request(self, endpoint, params):
        """Make API request with rate limiting and error handling"""
        if not self.api_key or self.api_key == "YOUR_WEATHER_API_KEY_HERE":
            return {"error": "API key not configured", "instructions": self.get_api_key_instructions()}
        
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_api_call < self.api_call_interval:
            time.sleep(self.api_call_interval - (current_time - self.last_api_call))
        
        try:
            url = f"{self.base_url}/{endpoint}" 
            params['key'] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            self.last_api_call = time.time()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"error": "Invalid API key. Please check your WeatherAPI.com API key."}
            elif response.status_code == 429:
                return {"error": "API rate limit exceeded. Please try again later."}
            else:
                return {"error": f"Weather API error: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Weather data is currently unavailable. Please try again later. ({str(e)})"}
    
    def get_weather_forecast(self, lat, lng, days=2):
        """Get weather forecast for a location"""
        cache_key = f"forecast_{lat}_{lng}_{days}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now().timestamp() - cached_data['timestamp'] < self.cache_duration:
                return cached_data['data']
        
        # Make API request
        params = {
            'q': f"{lat},{lng}",
            'days': days,
            'aqi': 'no'
        }
        
        result = self.make_api_request('forecast.json', params)
        
        if 'error' not in result:
            # Cache successful results
            self.cache[cache_key] = {
                'timestamp': datetime.now().timestamp(),
                'data': result
            }
        
        return result
    
    def get_current_weather(self, lat, lng):
        """Get current weather for a location"""
        cache_key = f"current_{lat}_{lng}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now().timestamp() - cached_data['timestamp'] < self.cache_duration:
                return cached_data['data']
        
        # Make API request
        params = {
            'q': f"{lat},{lng}",
            'aqi': 'no'
        }
        
        result = self.make_api_request('current.json', params)
        
        if 'error' not in result:
            # Cache successful results
            self.cache[cache_key] = {
                'timestamp': datetime.now().timestamp(),
                'data': result
            }
        
        return result
    
    def extract_forecast_data(self, forecast_data):
        """Extract relevant forecast data for debris prediction"""
        if 'error' in forecast_data:
            return forecast_data
        
        try:
            forecast = forecast_data.get('forecast', {}).get('forecastday', [])
            if not forecast:
                return {"error": "No forecast data available"}
            
            extracted_data = {
                'location': forecast_data.get('location', {}),
                'current': forecast_data.get('current', {}),
                'forecast': []
            }
            
            for day in forecast:
                day_data = {
                    'date': day.get('date'),
                    'max_temp': day.get('day', {}).get('maxtemp_c'),
                    'min_temp': day.get('day', {}).get('mintemp_c'),
                    'avg_temp': day.get('day', {}).get('avgtemp_c'),
                    'total_rainfall': day.get('day', {}).get('totalprecip_mm'),
                    'max_wind_speed': day.get('day', {}).get('maxwind_kph'),
                    'avg_humidity': day.get('day', {}).get('avghumidity'),
                    'condition': day.get('day', {}).get('condition', {}).get('text'),
                    'hourly': []
                }
                
                # Extract hourly data for detailed analysis
                for hour in day.get('hour', []):
                    hour_data = {
                        'time': hour.get('time'),
                        'temp_c': hour.get('temp_c'),
                        'rainfall_mm': hour.get('precip_mm'),
                        'wind_kph': hour.get('wind_kph'),
                        'wind_degree': hour.get('wind_degree'),
                        'humidity': hour.get('humidity'),
                        'condition': hour.get('condition', {}).get('text')
                    }
                    day_data['hourly'].append(hour_data)
                
                extracted_data['forecast'].append(day_data)
            
            return extracted_data
            
        except Exception as e:
            return {"error": f"Error processing forecast data: {str(e)}"}
    
    def get_weather_for_river(self, river_name, coordinates):
        """Get weather data for a specific river location"""
        lat, lng = coordinates
        
        print(f"Getting weather for {river_name} at coordinates {lat}, {lng}")
        
        # Get current weather
        current_weather = self.get_current_weather(lat, lng)
        print(f"Current weather result: {current_weather}")
        
        # Get forecast
        forecast_weather = self.get_weather_forecast(lat, lng, days=2)
        print(f"Forecast weather result: {forecast_weather}")
        
        # Check if we got valid forecast data
        if 'error' in forecast_weather:
            print(f"Forecast error: {forecast_weather['error']}")
            return {"error": f"Forecast failed: {forecast_weather['error']}"}
        
        # Extract forecast data in the correct format
        extracted_forecast = self.extract_forecast_data(forecast_weather)
        
        # If extraction failed, return error
        if 'error' in extracted_forecast:
            print(f"Extraction error: {extracted_forecast['error']}")
            return {"error": f"Data extraction failed: {extracted_forecast['error']}"}
        
        # Extract and combine data
        result = {
            'river_name': river_name,
            'coordinates': coordinates,
            'timestamp': datetime.now().isoformat(),
            'current': current_weather,
            'forecast': extracted_forecast.get('forecast', [])  # Use the forecast array directly
        }
        
        return result
    
    def get_mock_weather_data(self, river_name, coordinates):
        """Provide realistic mock weather data when API is not available"""
        import random
        
        print(f"Using mock weather data for {river_name}")  # Debug log
        
        # Generate realistic mock data based on Malaysian climate
        current_temp = random.uniform(25, 32)  # Malaysian temperature range
        current_humidity = random.uniform(70, 90)  # High humidity
        current_wind = random.uniform(5, 20)  # Light to moderate wind
        current_rainfall = random.uniform(0, 5)  # Light rainfall
        
        # Mock current weather
        mock_current = {
            'temp_c': round(current_temp, 1),
            'humidity': round(current_humidity),
            'wind_kph': round(current_wind, 1),
            'precip_mm': round(current_rainfall, 1),
            'condition': {'text': 'Partly cloudy'},
            'last_updated': datetime.now().isoformat()
        }
        
        # Mock forecast data
        mock_forecast = [
            {
                'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'total_rainfall': round(random.uniform(0, 15), 1),
                'max_wind_speed': round(current_wind + random.uniform(0, 10), 1),
                'avg_temp': round(current_temp + random.uniform(-1, 1), 1)
            },
            {
                'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                'total_rainfall': round(random.uniform(0, 20), 1),
                'max_wind_speed': round(current_wind + random.uniform(0, 15), 1),
                'avg_temp': round(current_temp + random.uniform(-2, 2), 1)
            }
        ]
        
        result = {
            'river_name': river_name,
            'coordinates': coordinates,
            'timestamp': datetime.now().isoformat(),
            'current': mock_current,
            'forecast': mock_forecast,
            'note': 'Using mock weather data (API key not configured)'
        }
        
        print(f"Mock weather result: {result}")  # Debug log
        return result

# Global weather system instance
weather_system = WeatherSystem()
