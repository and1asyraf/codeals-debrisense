import numpy as np
from datetime import datetime, timedelta
import math

class EnhancedAIPredictor:
    def __init__(self):
        self.base_model = None  # Will be loaded from the main app
        self.scaler = None      # Will be loaded from the main app
        
    def set_models(self, model, scaler):
        """Set the trained ML models"""
        self.base_model = model
        self.scaler = scaler
    
    def calculate_data_quality_score(self, sensor_data, weather_data):
        """Calculate confidence based on data quality"""
        score = 0.0
        max_score = 100.0
        
        # Sensor data quality (40 points)
        if sensor_data:
            sensor_score = 0
            total_sensors = 0
            
            for sensor_type, status in sensor_data.get('sensor_status', {}).items():
                total_sensors += 1
                if status == 'online':
                    sensor_score += 1
                elif status == 'offline':
                    sensor_score += 0.3  # Partial credit for historical patterns
            
            if total_sensors > 0:
                score += (sensor_score / total_sensors) * 40
        
        # Weather data quality (30 points)
        if weather_data and 'error' not in weather_data.get('current', {}):
            score += 30
        
        # Forecast data quality (20 points)
        if weather_data and 'error' not in weather_data.get('forecast', {}):
            score += 20
        
        # Data freshness (10 points)
        # This would be calculated based on how recent the data is
        score += 10
        
        return min(score, max_score) / max_score
    
    def predict_debris_level(self, sensor_data, weather_data, timeframe_hours=24):
        """Predict debris level for a specific timeframe"""
        if not self.base_model or not self.scaler:
            return {
                'error': 'AI model not loaded',
                'prediction': None,
                'confidence': 0.0
            }
        
        try:
            # Extract features from sensor data
            sensor_features = self.extract_sensor_features(sensor_data)
            
            # Extract features from weather data
            weather_features = self.extract_weather_features(weather_data, timeframe_hours)
            
            # Combine features
            combined_features = {**sensor_features, **weather_features}
            
            # Prepare feature vector for ML model
            feature_vector = np.array([
                combined_features.get('rainfall', 0),
                combined_features.get('wind_speed', 0),
                combined_features.get('tide_level', 0),
                combined_features.get('water_flow_rate', 0)
            ]).reshape(1, -1)
            
            # Scale features
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Make prediction
            base_prediction = self.base_model.predict(feature_vector_scaled)[0]
            
            # Adjust prediction based on timeframe
            adjusted_prediction = self.adjust_prediction_for_timeframe(base_prediction, timeframe_hours, weather_data)
            
            # Calculate confidence
            confidence = self.calculate_data_quality_score(sensor_data, weather_data)
            
            # Calculate risk level
            risk_level = self.calculate_risk_level(adjusted_prediction)
            
            return {
                'prediction': round(adjusted_prediction, 1),
                'risk_level': risk_level,
                'confidence': round(confidence, 2),
                'timeframe_hours': timeframe_hours,
                'features_used': combined_features
            }
            
        except Exception as e:
            return {
                'error': f'Prediction error: {str(e)}',
                'prediction': None,
                'confidence': 0.0
            }
    
    def extract_sensor_features(self, sensor_data):
        """Extract features from sensor data"""
        features = {}
        
        if sensor_data:
            # Water level (normalized to 0-1 range)
            water_level = sensor_data.get('water_level')
            if water_level is not None:
                features['water_level'] = min(water_level / 8.0, 1.0)  # Normalize to 0-1
            
            # Flow rate (normalized to 0-1 range)
            flow_rate = sensor_data.get('flow_rate')
            if flow_rate is not None:
                features['water_flow_rate'] = min(flow_rate / 500.0, 1.0)  # Normalize to 0-1
            
            # Tide level (normalized to 0-1 range)
            tide_level = sensor_data.get('tide_level')
            if tide_level is not None:
                features['tide_level'] = min(tide_level / 2.5, 1.0)  # Normalize to 0-1
        
        return features
    
    def extract_weather_features(self, weather_data, timeframe_hours):
        """Extract weather features for prediction"""
        features = {}
        
        if not weather_data or 'error' in weather_data.get('current', {}):
            # Use default values if weather data unavailable
            features['rainfall'] = 0
            features['wind_speed'] = 0
            return features
        
        try:
            # Current weather features
            current = weather_data.get('current', {})
            features['rainfall'] = current.get('precip_mm', 0)
            features['wind_speed'] = current.get('wind_kph', 0)
            
            # Forecast features for the specific timeframe
            forecast = weather_data.get('forecast', {})
            if isinstance(forecast, list) and len(forecast) > 0:
                # Calculate forecast features for the prediction timeframe
                forecast_features = self.calculate_forecast_features(forecast, timeframe_hours)
                features.update(forecast_features)
            
        except Exception as e:
            print(f"Error extracting weather features: {e}")
            features['rainfall'] = 0
            features['wind_speed'] = 0
        
        return features
    
    def calculate_forecast_features(self, forecast, timeframe_hours):
        """Calculate forecast features for the prediction timeframe"""
        features = {}
        
        try:
            # Calculate weighted average of forecast data for the timeframe
            total_rainfall = 0
            total_wind_speed = 0
            total_weight = 0
            
            current_time = datetime.now()
            
            for day_data in forecast:
                day_date = datetime.strptime(day_data.get('date', ''), '%Y-%m-%d')
                
                # Check if this day is within our prediction timeframe
                hours_ahead = (day_date - current_time).total_seconds() / 3600
                
                if 0 <= hours_ahead <= timeframe_hours:
                    # Weight decreases as we go further into the future
                    weight = max(0.1, 1.0 - (hours_ahead / timeframe_hours))
                    
                    total_rainfall += day_data.get('total_rainfall', 0) * weight
                    total_wind_speed += day_data.get('max_wind_speed', 0) * weight
                    total_weight += weight
            
            if total_weight > 0:
                features['forecast_rainfall'] = total_rainfall / total_weight
                features['forecast_wind_speed'] = total_wind_speed / total_weight
            else:
                features['forecast_rainfall'] = 0
                features['forecast_wind_speed'] = 0
                
        except Exception as e:
            print(f"Error calculating forecast features: {e}")
            features['forecast_rainfall'] = 0
            features['forecast_wind_speed'] = 0
        
        return features
    
    def adjust_prediction_for_timeframe(self, base_prediction, timeframe_hours, weather_data):
        """Adjust prediction based on timeframe and weather forecast"""
        adjustment_factor = 1.0
        
        # Adjust based on timeframe (longer predictions are less certain)
        if timeframe_hours <= 6:
            adjustment_factor = 1.0  # High confidence for short-term
        elif timeframe_hours <= 12:
            adjustment_factor = 0.9  # Medium confidence for medium-term
        else:
            adjustment_factor = 0.8  # Lower confidence for long-term
        
        # Adjust based on weather forecast
        if weather_data and 'forecast' in weather_data:
            forecast = weather_data['forecast']
            if isinstance(forecast, list) and len(forecast) > 0:
                # Check if there's significant weather change predicted
                current_rainfall = weather_data.get('current', {}).get('precip_mm', 0)
                forecast_rainfall = forecast[0].get('total_rainfall', 0) if len(forecast) > 0 else 0
                
                # If significant rainfall increase is predicted, adjust prediction upward
                if forecast_rainfall > current_rainfall * 1.5:
                    adjustment_factor *= 1.2
                elif forecast_rainfall < current_rainfall * 0.5:
                    adjustment_factor *= 0.9
        
        return base_prediction * adjustment_factor
    
    def calculate_risk_level(self, prediction):
        """Calculate risk level based on predicted debris level"""
        if prediction > 300:
            return 'critical'
        elif prediction > 250:
            return 'high'
        elif prediction > 150:
            return 'medium'
        elif prediction > 100:
            return 'low'
        else:
            return 'very_low'
    
    def get_multiple_predictions(self, sensor_data, weather_data):
        """Get predictions for multiple timeframes"""
        timeframes = [6, 12, 24]  # hours
        predictions = {}
        
        for timeframe in timeframes:
            prediction = self.predict_debris_level(sensor_data, weather_data, timeframe)
            predictions[f'{timeframe}h'] = prediction
        
        return predictions

# Global AI predictor instance
enhanced_ai = EnhancedAIPredictor()
