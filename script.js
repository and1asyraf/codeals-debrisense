// Initialize the map with dark mode
const map = L.map('map', {
    center: [4.2105, 108.9758], // Malaysia center coordinates
    zoom: 6, // Closer zoom to show Malaysia clearly
    zoomControl: true,
    attributionControl: true,
    minZoom: 2,
    maxBounds: [
        [-90, -180], // Southwest bounds
        [90, 180]    // Northeast bounds
    ],
    maxBoundsViscosity: 1.0
});

// Add lighter dark mode tile layer with labels
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(map);

// Create custom donut marker for Sungai Inanam
const donutIcon = L.divIcon({
    className: 'custom-donut-marker',
    html: '<div class="donut-outer"><div class="donut-inner"></div></div>',
    iconSize: [20, 20],
    iconAnchor: [10, 10]
});

// Load all locations and create markers
async function loadAllLocations() {
    try {
        const response = await fetch('http://localhost:5000/get_all_locations');
        const data = await response.json();
        
        data.locations.forEach(location => {
            const marker = L.marker([location.lat, location.lng], { icon: donutIcon })
                .addTo(map);
            
            // Store location data with marker
            marker.locationData = location;
            
            // Add click event
            marker.on('click', function() {
                showLocationInfo(location);
                toggleSidebar();
            });
        });
    } catch (error) {
        console.error('Error loading locations:', error);
        // Fallback to single marker
        const sungaiInanamMarker = L.marker([5.997846609055653, 116.12997039272707], { icon: donutIcon })
            .addTo(map);
        
        sungaiInanamMarker.on('click', function() {
            showLocationInfo({
                name: 'Sungai Inanam',
                image: 'sungaiInanam.png',
                pollution_level: 300,
                rainfall: 25.5,
                wind_speed: 12.3,
                tide_level: 1.2,
                water_flow_rate: 150
            });
            toggleSidebar();
        });
    }
}

// Load locations when page loads
loadAllLocations();

// Function to toggle sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

// Function to show location information
async function showLocationInfo(locationData) {
    const locationInfo = document.getElementById('location-info');
    
            // Show loading state
        locationInfo.innerHTML = `
            <div class="location-image">
                <img src="/data/image/${locationData.image}" alt="${locationData.name}" class="location-img" 
                     onerror="console.log('Image failed to load:', this.src); this.style.display='none'; this.nextElementSibling.style.display='block';"
                     onload="console.log('Image loaded successfully:', this.src);">
                <div class="no-image" style="display: none; padding: 40px; text-align: center; color: #cccccc; background: rgba(255,255,255,0.05);">
                    <p>📸 Image not available</p>
                    <p>${locationData.name}</p>
                </div>
            </div>
        
        <div class="river-name">
            <h3>${locationData.name}</h3>
        </div>
        
        <div class="loading">
            <p>Analyzing debris patterns...</p>
        </div>
    `;
    
    try {
        // Get AI predictions
        const predictionResponse = await fetch('http://localhost:5000/predict_debris', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                rainfall: locationData.rainfall,
                wind_speed: locationData.wind_speed,
                tide_level: locationData.tide_level,
                water_flow_rate: locationData.water_flow_rate
            })
        });
        
        const prediction = await predictionResponse.json();
        
        // Get early warning
        const warningResponse = await fetch('http://localhost:5000/early_warning', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                rainfall: locationData.rainfall,
                wind_speed: locationData.wind_speed,
                tide_level: locationData.tide_level
            })
        });
        
        const warning = await warningResponse.json();
        
        // Update sidebar with AI insights
        locationInfo.innerHTML = `
            <div class="location-image">
                <img src="/data/image/${locationData.image}" alt="${locationData.name}" class="location-img">
            </div>
            
            <div class="river-name">
                <h3>${locationData.name}</h3>
            </div>
            
            <div class="ai-insights">
                <div class="prediction-card ${prediction.risk_level}">
                    <h4>AI Prediction</h4>
                    <p><strong>Predicted Debris Level:</strong> <span class="value">${prediction.prediction}</span></p>
                    <p><strong>Risk Level:</strong> <span class="value ${prediction.risk_level}">${prediction.risk_level.toUpperCase()}</span></p>
                    <p><strong>Confidence:</strong> <span class="value">${(prediction.confidence * 100).toFixed(0)}%</span></p>
                </div>
                
                <div class="warning-card ${warning.warning_level}">
                    <h4>Early Warning</h4>
                    <p><strong>Alert Level:</strong> <span class="value ${warning.warning_level}">${warning.warning_level.toUpperCase()}</span></p>
                    <p><strong>Message:</strong> <span class="value">${warning.message}</span></p>
                </div>
                
                <div class="current-data">
                    <h4>Current Conditions</h4>
                    <p><strong>Rainfall:</strong> <span class="value">${locationData.rainfall} mm</span></p>
                    <p><strong>Wind Speed:</strong> <span class="value">${locationData.wind_speed} km/h</span></p>
                    <p><strong>Tide Level:</strong> <span class="value">${locationData.tide_level} m</span></p>
                    <p><strong>Water Flow:</strong> <span class="value">${locationData.water_flow_rate} m³/s</span></p>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error getting AI predictions:', error);
        // Fallback to basic info
        locationInfo.innerHTML = `
            <div class="location-image">
                <img src="/data/image/${locationData.image}" alt="${locationData.name}" class="location-img" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                <div class="no-image" style="display: none; padding: 40px; text-align: center; color: #cccccc; background: rgba(255,255,255,0.05);">
                    <p>📸 Image not available</p>
                    <p>${locationData.name}</p>
                </div>
            </div>
            
            <div class="river-name">
                <h3>${locationData.name}</h3>
            </div>
            
            <div class="current-data">
                <h4>Current Data</h4>
                <p><strong>Pollution Level:</strong> <span class="value">${locationData.pollution_level}</span></p>
            </div>
        `;
    }
}

// Ensure map fills the available space
map.invalidateSize();
