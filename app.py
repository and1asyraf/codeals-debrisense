from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

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

# Serve the main dashboard
@app.route('/')
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

if __name__ == '__main__':
    print("🚀 Debrisense AI Dashboard Starting...")
    print("📊 Dashboard: http://localhost:5000")
    print("🤖 AI Backend: http://localhost:5000/predict_debris")
    print("📸 Images: http://localhost:5000/data/image/")
    app.run(debug=True, port=5000)
