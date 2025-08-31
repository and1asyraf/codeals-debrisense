from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime, timedelta
import threading
import time

# Import our custom systems
from sensor_system import sensor_system
from weather_system import weather_system
from enhanced_ai import enhanced_ai

app = Flask(__name__)
CORS(app)

# Load or create models
def load_or_create_models():
    if os.path.exists('models/debris_predictor.pkl'):
        debris_predictor = joblib.load('models/debris_predictor.pkl')
        scaler = joblib.load('models/scaler.pkl')
    else:
        # Create simple model for demo
        debris_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        scaler = StandardScaler()
        
        # Create sample training data
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic training data
        rainfall = np.random.uniform(0, 50, n_samples)
        wind_speed = np.random.uniform(0, 30, n_samples)
        tide_level = np.random.uniform(0, 3, n_samples)
        water_flow = np.random.uniform(50, 300, n_samples)
        
        # Create target variable (debris level) based on environmental factors
        debris_level = (
            rainfall * 2 + 
            wind_speed * 3 + 
            tide_level * 50 + 
            water_flow * 0.5 +
            np.random.normal(0, 20, n_samples)
        )
        
        # Prepare features
        X = np.column_stack([rainfall, wind_speed, tide_level, water_flow])
        X_scaled = scaler.fit_transform(X)
        
        # Train model
        debris_predictor.fit(X_scaled, debris_level)
        
        # Save models
        os.makedirs('models', exist_ok=True)
        joblib.dump(debris_predictor, 'models/debris_predictor.pkl')
        joblib.dump(scaler, 'models/scaler.pkl')
    
    return debris_predictor, scaler

debris_predictor, scaler = load_or_create_models()

# Set up enhanced AI with our models
enhanced_ai.set_models(debris_predictor, scaler)

# Global variables for scheduled updates
last_sensor_update = datetime.now()
last_weather_update = datetime.now()
next_update_time = datetime.now() + timedelta(hours=2)  # Update every 2 hours

# Serve the login page as default
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Serve the dashboard
@app.route('/dashboard')
def dashboard():
    return send_from_directory('.', 'dashboard.html')

# Serve static files (CSS, JS)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# Test route to check image files
@app.route('/test-images')
def test_images():
    import os
    image_dir = 'data/image'
    files = os.listdir(image_dir) if os.path.exists(image_dir) else []
    return jsonify({
        'image_directory': image_dir,
        'files_found': files,
        'sungaiInanam_exists': 'sungaiInanam.png' in files
    })

# Serve images from data folder
@app.route('/data/image/<path:filename>')
def serve_images(filename):
    print(f"🔍 Requesting image: {filename}")
    print(f"📁 Looking in: data/image/")
    try:
        return send_from_directory('data/image', filename)
    except Exception as e:
        print(f"❌ Error serving image {filename}: {e}")
        return f"Image not found: {filename}", 404

@app.route('/predict_debris', methods=['POST'])
def predict_debris():
    try:
        data = request.json
        
        # Extract features
        features = np.array([
            data.get('rainfall', 0),
            data.get('wind_speed', 0),
            data.get('tide_level', 0),
            data.get('water_flow_rate', 0)
        ]).reshape(1, -1)
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = debris_predictor.predict(features_scaled)[0]
        
        # Calculate risk level
        if prediction > 250:
            risk_level = 'high'
        elif prediction > 150:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return jsonify({
            'prediction': round(prediction, 1),
            'risk_level': risk_level,
            'confidence': 0.85
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/detect_hotspots', methods=['GET'])
def detect_hotspots():
    try:
        # Read current data
        df = pd.read_csv('data/data.csv')
        
        # Identify hotspots based on pollution level
        hotspots = []
        for _, row in df.iterrows():
            if row['pollution_level'] > 200:
                hotspots.append({
                    'lat': row['latitude'],
                    'lng': row['longitude'],
                    'name': row['name'],
                    'pollution_level': row['pollution_level'],
                    'risk_level': 'high' if row['pollution_level'] > 250 else 'medium'
                })
        
        return jsonify({'hotspots': hotspots})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/early_warning', methods=['POST'])
def early_warning():
    try:
        data = request.json
        
        # Check warning conditions
        rainfall = data.get('rainfall', 0)
        wind_speed = data.get('wind_speed', 0)
        tide_level = data.get('tide_level', 0)
        
        # Simple warning logic
        warning_score = 0
        if rainfall > 30:
            warning_score += 2
        if wind_speed > 20:
            warning_score += 1
        if tide_level > 2:
            warning_score += 1
        
        if warning_score >= 3:
            warning_level = 'high'
        elif warning_score >= 2:
            warning_level = 'medium'
        else:
            warning_level = 'low'
        
        return jsonify({
            'warning_level': warning_level,
            'warning_score': warning_score,
            'message': f'Debris risk level: {warning_level}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/get_all_locations', methods=['GET'])
def get_all_locations():
    try:
        df = pd.read_csv('data/data.csv')
        locations = []
        
        for _, row in df.iterrows():
            locations.append({
                'id': row['id'],
                'lat': row['latitude'],
                'lng': row['longitude'],
                'name': row['name'],
                'pollution_level': row['pollution_level'],
                'image': row['image'],
                'rainfall': row['rainfall'],
                'wind_speed': row['wind_speed'],
                'tide_level': row['tide_level'],
                'water_flow_rate': row['water_flow_rate']
            })
        
        return jsonify({'locations': locations})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# New enhanced endpoints
@app.route('/get_sensor_data/<river_name>', methods=['GET'])
def get_sensor_data(river_name):
    """Get real-time sensor data for a specific river"""
    try:
        sensor_data = sensor_system.get_sensor_data_for_river(river_name)
        if sensor_data:
            return jsonify(sensor_data)
        else:
            return jsonify({'error': 'River not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/get_weather_data/<river_name>', methods=['GET'])
def get_weather_data(river_name):
    """Get weather data for a specific river"""
    try:
        # Get coordinates from CSV
        df = pd.read_csv('data/data.csv')
        river_data = df[df['name'].str.contains(river_name, case=False, na=False)]
        
        if river_data.empty:
            return jsonify({'error': 'River not found'}), 404
        
        lat = river_data.iloc[0]['latitude']
        lng = river_data.iloc[0]['longitude']
        
        weather_data = weather_system.get_weather_for_river(river_name, (lat, lng))
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/get_enhanced_predictions/<river_name>', methods=['GET'])
def get_enhanced_predictions(river_name):
    """Get enhanced AI predictions for multiple timeframes"""
    try:
        # Get sensor data
        sensor_data = sensor_system.get_sensor_data_for_river(river_name)
        
        # Get weather data
        df = pd.read_csv('data/data.csv')
        river_data = df[df['name'].str.contains(river_name, case=False, na=False)]
        
        if river_data.empty:
            return jsonify({'error': 'River not found'}), 404
        
        lat = river_data.iloc[0]['latitude']
        lng = river_data.iloc[0]['longitude']
        weather_data = weather_system.get_weather_for_river(river_name, (lat, lng))
        
        # Get predictions for multiple timeframes
        predictions = enhanced_ai.get_multiple_predictions(sensor_data, weather_data)
        
        return jsonify({
            'river_name': river_name,
            'timestamp': datetime.now().isoformat(),
            'predictions': predictions,
            'sensor_data': sensor_data,
            'weather_data': weather_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/get_update_schedule', methods=['GET'])
def get_update_schedule():
    """Get information about scheduled updates"""
    global last_sensor_update, last_weather_update, next_update_time
    
    return jsonify({
        'last_sensor_update': last_sensor_update.isoformat(),
        'last_weather_update': last_weather_update.isoformat(),
        'next_update': next_update_time.isoformat(),
        'update_interval_hours': 2,
        'sensor_update_interval_minutes': 5
    })

@app.route('/get_weather_api_status', methods=['GET'])
def get_weather_api_status():
    """Get weather API configuration status"""
    return jsonify(weather_system.get_api_key_instructions())

@app.route('/test_sensors', methods=['GET'])
def test_sensors():
    """Test endpoint to verify sensor system is working"""
    try:
        all_sensor_data = sensor_system.get_all_sensor_data()
        return jsonify({
            'status': 'success',
            'sensors': all_sensor_data,
            'message': 'Sensor system is working correctly'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'Sensor system has an issue'
        }), 500

@app.route('/test_weather/<river_name>', methods=['GET'])
def test_weather(river_name):
    """Test endpoint to see what weather data is being returned"""
    try:
        # Get coordinates from CSV
        df = pd.read_csv('data/data.csv')
        river_data = df[df['name'].str.contains(river_name, case=False, na=False)]
        
        if river_data.empty:
            return jsonify({'error': 'River not found'}), 404
        
        lat = river_data.iloc[0]['latitude']
        lng = river_data.iloc[0]['longitude']
        
        # Test current weather
        current_weather = weather_system.get_current_weather(lat, lng)
        
        # Test forecast
        forecast_weather = weather_system.get_weather_forecast(lat, lng, days=1)
        
        # Test processed weather data
        processed_weather = weather_system.get_weather_for_river(river_name, (lat, lng))
        
        return jsonify({
            'river_name': river_name,
            'coordinates': (lat, lng),
            'current_weather_raw': current_weather,
            'forecast_weather_raw': forecast_weather,
            'processed_weather': processed_weather,
            'api_key_status': weather_system.api_key != "YOUR_WEATHER_API_KEY_HERE"
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': str(e.__traceback__)
        }), 500

if __name__ == '__main__':
    print("Debrisense AI Dashboard Starting...")
    print("Dashboard: http://localhost:5000")
    print("AI Backend: http://localhost:5000/predict_debris")
    print("Images: http://localhost:5000/data/image/")
    app.run(debug=True, port=5000)
