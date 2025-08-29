// Enhanced Debrisense Dashboard JavaScript
let currentRiver = null;
let updateSchedule = null;
let charts = {};

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
window.darkTileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(map);

// Store map globally for theme switching
window.map = map;

// Create custom donut marker for rivers
const donutIcon = L.divIcon({
    className: 'custom-donut-marker',
    html: '<div class="donut-outer"><div class="donut-inner"></div></div>',
    iconSize: [20, 20],
    iconAnchor: [10, 10]
});

// Load all locations and create markers
async function loadAllLocations() {
    try {
        const response = await fetch('/get_all_locations');
        const data = await response.json();
        
        data.locations.forEach(location => {
            const marker = L.marker([location.lat, location.lng], { icon: donutIcon })
                .addTo(map);
            
            // Store location data with marker
            marker.locationData = location;
            
            // Add click event
            marker.on('click', function() {
                showEnhancedLocationInfo(location);
                toggleSidebar();
            });
        });
        
        // Get update schedule
        await getUpdateSchedule();
        
    } catch (error) {
        console.error('Error loading locations:', error);
        // Fallback to basic functionality
        showBasicFallback();
    }
}

// Get update schedule information
async function getUpdateSchedule() {
    try {
        const response = await fetch('/get_update_schedule');
        updateSchedule = await response.json();
    } catch (error) {
        console.error('Error getting update schedule:', error);
    }
}

// Enhanced location information display
async function showEnhancedLocationInfo(locationData) {
    currentRiver = locationData.name;
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
            <p>Loading real-time data...</p>
        </div>
    `;
    
    try {
        // Load all data in parallel
        const [sensorData, weatherData, predictions] = await Promise.all([
            fetch(`/get_sensor_data/${locationData.name}`).then(r => r.json()),
            fetch(`/get_weather_data/${locationData.name}`).then(r => r.json()),
            fetch(`/get_enhanced_predictions/${locationData.name}`).then(r => r.json())
        ]);
        
        // Update sidebar with enhanced information
        updateSidebarWithEnhancedData(locationData, sensorData, weatherData, predictions);
        
    } catch (error) {
        console.error('Error getting enhanced data:', error);
        // Fallback to basic info
        showBasicLocationInfo(locationData);
    }
}

// Update sidebar with enhanced data
function updateSidebarWithEnhancedData(locationData, sensorData, weatherData, predictions) {
    const locationInfo = document.getElementById('location-info');
    
    locationInfo.innerHTML = `
        <div class="location-image">
            <img src="/data/image/${locationData.image}" alt="${locationData.name}" class="location-img">
        </div>
        
        <div class="river-name">
            <h3>${locationData.name}</h3>
        </div>
        
        <div class="enhanced-data">
            <!-- Sensor Data Section -->
            <div class="data-section">
                <div class="section-header" onclick="toggleSection('sensor-section')">
                    <h4>Real-time Sensors</h4>
                    <span class="toggle-icon">▼</span>
                    <span class="update-time">Updated: ${formatTimeAgo(sensorData.timestamp)}</span>
                </div>
                <div id="sensor-section" class="section-content">
                    ${generateSensorDataHTML(sensorData)}
                </div>
            </div>
            
            <!-- Weather Data Section -->
            <div class="data-section">
                <div class="section-header" onclick="toggleSection('weather-section')">
                    <h4>Weather Forecast</h4>
                    <span class="toggle-icon">▼</span>
                    <span class="update-time">Updated: ${formatTimeAgo(weatherData.timestamp)}</span>
                </div>
                <div id="weather-section" class="section-content">
                    ${generateWeatherDataHTML(weatherData)}
                </div>
            </div>
            
            <!-- AI Predictions Section -->
            <div class="data-section">
                <div class="section-header" onclick="toggleSection('predictions-section')">
                    <h4>AI Predictions</h4>
                    <span class="toggle-icon">▼</span>
                    <span class="update-time">Updated: ${formatTimeAgo(predictions.timestamp)}</span>
                </div>
                <div id="predictions-section" class="section-content">
                    ${generatePredictionsHTML(predictions)}
                </div>
            </div>
            
            <!-- Charts Section -->
            <div class="data-section">
                <div class="section-header" onclick="toggleSection('charts-section')">
                    <h4>Data Trends</h4>
                    <span class="toggle-icon">▼</span>
                </div>
                <div id="charts-section" class="section-content">
                    <div class="chart-container">
                        <canvas id="predictionChart"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- Update Schedule -->
            <div class="update-schedule">
                <p><strong>Next Update:</strong> ${formatNextUpdate()}</p>
            </div>
        </div>
    `;
    
    // Initialize charts after content is loaded
    setTimeout(() => {
        initializeCharts(predictions);
    }, 100);
}

// Generate sensor data HTML
function generateSensorDataHTML(sensorData) {
    if (sensorData.error) {
        return `<p class="error">❌ ${sensorData.error}</p>`;
    }
    
    const statusIcons = {
        'online': '🟢',
        'offline': '🔴'
    };
    
    return `
        <div class="sensor-grid">
            <div class="sensor-item ${sensorData.water_level ? 'online' : 'offline'}">
                <div class="sensor-header">
                    <span>Water Level</span>
                    <span class="status">${statusIcons[sensorData.sensor_status?.water_level || 'offline']}</span>
                </div>
                <div class="sensor-value">${sensorData.water_level || 'N/A'} m</div>
            </div>
            
            <div class="sensor-item ${sensorData.flow_rate ? 'online' : 'offline'}">
                <div class="sensor-header">
                    <span>Flow Rate</span>
                    <span class="status">${statusIcons[sensorData.sensor_status?.flow_rate || 'offline']}</span>
                </div>
                <div class="sensor-value">${sensorData.flow_rate || 'N/A'} m³/s</div>
            </div>
            
            <div class="sensor-item ${sensorData.tide_level ? 'online' : 'offline'}">
                <div class="sensor-header">
                    <span>Tide Level</span>
                    <span class="status">${statusIcons[sensorData.sensor_status?.tide_level || 'offline']}</span>
                </div>
                <div class="sensor-value">${sensorData.tide_level || 'N/A'} m</div>
            </div>
        </div>
    `;
}

// Generate weather data HTML
function generateWeatherDataHTML(weatherData) {
    console.log('Weather data received:', weatherData); // Debug log
    
    if (weatherData.error || weatherData.current?.error) {
        return `<p class="error">❌ Weather data is currently unavailable. Please try again later.</p>`;
    }
    
    // Check if using mock data
    let noteHtml = '';
    if (weatherData.note && weatherData.note.includes('mock')) {
        noteHtml = `<p style="color: #ffd93d; font-size: 0.8rem; margin-bottom: 10px;">ℹ️ ${weatherData.note}</p>`;
    }
    
    const current = weatherData.current || {};
    console.log('Current weather data:', current); // Debug log
    
    // Handle both real API data and mock data structures
    console.log('Current weather object:', current); // Debug current weather object
    
    const temp = current.temp_c || current.temp || current.current?.temp_c || 'N/A';
    const rainfall = current.precip_mm || current.rainfall || current.current?.precip_mm || '0';
    const windSpeed = current.wind_kph || current.wind_speed || current.current?.wind_kph || 'N/A';
    const humidity = current.humidity || current.current?.humidity || 'N/A';
    
    console.log('Extracted current values:', { temp, rainfall, windSpeed, humidity }); // Debug extracted values
    
    const forecast = weatherData.forecast || [];
    console.log('Forecast data:', forecast); // Debug log
    
    let html = noteHtml + `
        <div class="current-weather">
            <h5>Current Conditions</h5>
            <div class="weather-grid">
                <div class="weather-item">
                    <span>Temperature</span>
                    <span class="value">${temp}°C</span>
                </div>
                <div class="weather-item">
                    <span>Rainfall</span>
                    <span class="value">${rainfall} mm</span>
                </div>
                <div class="weather-item">
                    <span>Wind Speed</span>
                    <span class="value">${windSpeed} km/h</span>
                </div>
                <div class="weather-item">
                    <span>Humidity</span>
                    <span class="value">${humidity}%</span>
                </div>
            </div>
        </div>
    `;
    
    if (forecast && forecast.length > 0) {
        html += `
            <div class="forecast-weather">
                <h5>24-Hour Forecast</h5>
                <div class="forecast-grid">
        `;
        
        forecast.slice(0, 2).forEach(day => {
            console.log('Processing forecast day:', day); // Debug log
            console.log('Day data structure:', JSON.stringify(day, null, 2)); // Detailed debug
            
            // Extract values with multiple fallback options
            const rainfall = day.total_rainfall || day.day?.totalprecip_mm || day.precip_mm || 0;
            const windSpeed = day.max_wind_speed || day.day?.maxwind_kph || day.wind_kph || 0;
            const temperature = day.avg_temp || day.day?.avgtemp_c || day.temp_c || 0;
            
            console.log('Extracted values:', { rainfall, windSpeed, temperature }); // Debug extracted values
            
            html += `
                <div class="forecast-day">
                    <div class="forecast-date">${formatDate(day.date)}</div>
                    <div class="forecast-data">
                        <div>Rainfall: ${rainfall} mm</div>
                        <div>Wind: ${windSpeed} km/h</div>
                        <div>Temp: ${temperature}°C</div>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    } else {
        html += `
            <div class="forecast-weather">
                <h5>24-Hour Forecast</h5>
                <p style="color: #cccccc; text-align: center; padding: 20px;">No forecast data available</p>
            </div>
        `;
    }
    
    return html;
}

// Generate predictions HTML
function generatePredictionsHTML(predictions) {
    if (predictions.error) {
        return `<p class="error">❌ ${predictions.error}</p>`;
    }
    
    const preds = predictions.predictions || {};
    let html = `
        <div class="prediction-timeframes">
            <div class="timeframe-selector">
                <button class="timeframe-btn active" onclick="showTimeframe('6h')">6 Hours</button>
                <button class="timeframe-btn" onclick="showTimeframe('12h')">12 Hours</button>
                <button class="timeframe-btn" onclick="showTimeframe('24h')">24 Hours</button>
            </div>
        </div>
    `;
    
    Object.entries(preds).forEach(([timeframe, prediction]) => {
        if (prediction.error) {
            html += `<p class="error">❌ ${prediction.error}</p>`;
            return;
        }
        
        const riskColors = {
            'critical': '#ff0000',
            'high': '#ff6b6b',
            'medium': '#ffd93d',
            'low': '#6bcf7f',
            'very_low': '#4a9eff'
        };
        
        // Format risk level text (replace underscores with spaces and capitalize properly)
        const riskLevelText = prediction.risk_level.replace(/_/g, ' ').toUpperCase();
        
        // Show only 6h prediction by default, hide others
        const displayStyle = timeframe === '6h' ? 'block' : 'none';
        
        html += `
            <div class="prediction-card ${prediction.risk_level}" data-timeframe="${timeframe}" style="display: ${displayStyle}">
                <div class="prediction-header">
                    <h5>${timeframe} Prediction</h5>
                    <span class="confidence">${Math.round(prediction.confidence * 100)}% confidence</span>
                </div>
                <div class="prediction-body">
                    <div class="prediction-value" style="color: ${riskColors[prediction.risk_level]}">
                        ${prediction.prediction} kg/m³
                    </div>
                    <div class="risk-level ${prediction.risk_level}">
                        ${riskLevelText} RISK
                    </div>
                </div>
            </div>
        `;
    });
    
    return html;
}

// Initialize charts
function initializeCharts(predictions) {
    const ctx = document.getElementById('predictionChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (charts.predictionChart) {
        charts.predictionChart.destroy();
    }
    
    const preds = predictions.predictions || {};
    const timeframes = Object.keys(preds);
    const values = timeframes.map(tf => preds[tf]?.prediction || 0);
    const confidences = timeframes.map(tf => (preds[tf]?.confidence || 0) * 100);
    
    // Get current theme colors
    const isLightMode = document.body.classList.contains('light-mode');
    const textColor = isLightMode ? '#333' : '#ffffff';
    const gridColor = isLightMode ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)';
    
    charts.predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeframes,
            datasets: [{
                label: 'Predicted Debris Level',
                data: values,
                borderColor: '#4a9eff',
                backgroundColor: 'rgba(74, 158, 255, 0.1)',
                tension: 0.4
            }, {
                label: 'Confidence (%)',
                data: confidences,
                borderColor: '#ffd93d',
                backgroundColor: 'rgba(255, 217, 61, 0.1)',
                tension: 0.4,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    },
                    title: {
                        display: true,
                        text: 'Debris Level',
                        color: textColor
                    }
                },
                y1: {
                    position: 'right',
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    },
                    title: {
                        display: true,
                        text: 'Confidence (%)',
                        color: textColor
                    }
                },
                x: {
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: textColor
                    }
                }
            }
        }
    });
}

// Utility functions
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const header = section.previousElementSibling;
    const icon = header.querySelector('.toggle-icon');
    
    if (section.style.display === 'none') {
        section.style.display = 'block';
        icon.textContent = '▼';
    } else {
        section.style.display = 'none';
        icon.textContent = '▶';
    }
}

function showTimeframe(timeframe) {
    // Update active button
    document.querySelectorAll('.timeframe-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Show/hide prediction cards
    document.querySelectorAll('.prediction-card').forEach(card => {
        if (card.dataset.timeframe === timeframe) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function formatTimeAgo(timestamp) {
    if (!timestamp) return 'Unknown';
    
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hours ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} days ago`;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
    });
}

function formatNextUpdate() {
    if (!updateSchedule) return 'Unknown';
    
    const nextUpdate = new Date(updateSchedule.next_update);
    const now = new Date();
    const diffMs = nextUpdate - now;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 0) return 'Due now';
    if (diffMins < 60) return `in ${diffMins} minutes`;
    
    const diffHours = Math.floor(diffMins / 60);
    return `in ${diffHours} hours`;
}

// Fallback functions
function showBasicLocationInfo(locationData) {
    const locationInfo = document.getElementById('location-info');
    locationInfo.innerHTML = `
        <div class="location-image">
            <img src="/data/image/${locationData.image}" alt="${locationData.name}" class="location-img">
        </div>
        
        <div class="river-name">
            <h3>${locationData.name}</h3>
        </div>
        
        <div class="basic-data">
            <h4>Basic Information</h4>
            <p><strong>Pollution Level:</strong> ${locationData.pollution_level}</p>
            <p><strong>Location:</strong> ${locationData.lat}, ${locationData.lng}</p>
        </div>
    `;
}

// Legacy function for compatibility
async function showLocationInfo(locationData) {
    // Redirect to enhanced function
    await showEnhancedLocationInfo(locationData);
}

function showBasicFallback() {
    // Create basic markers if enhanced loading fails
    const basicLocations = [
        { name: 'Sungai Inanam', lat: 5.997846609055653, lng: 116.12997039272707, image: 'sungaiInanam.png' },
        { name: 'Sungai Klang', lat: 3.0179012973130344, lng: 101.37692352872754, image: 'sungaiKlang.png' },
        { name: 'Sungai Pinang', lat: 5.403345957392342, lng: 100.33223539657536, image: 'sungaiPinang.png' }
    ];
    
    basicLocations.forEach(location => {
        const marker = L.marker([location.lat, location.lng], { icon: donutIcon })
            .addTo(map);
        
        marker.on('click', function() {
            showBasicLocationInfo(location);
            toggleSidebar();
        });
    });
}

// Function to toggle sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

// Load locations when page loads
loadAllLocations();

// Ensure map fills the available space
map.invalidateSize();

// Theme toggle functionality
function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle.querySelector('.theme-icon');
    const themeText = themeToggle.querySelector('.theme-text');
    
    // Check for saved theme preference or default to dark
    const currentTheme = localStorage.getItem('theme') || 'dark';
    setTheme(currentTheme);
    
    themeToggle.addEventListener('click', function() {
        const newTheme = document.body.classList.contains('light-mode') ? 'dark' : 'light';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

function setTheme(theme) {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle.querySelector('.theme-icon');
    const themeText = themeToggle.querySelector('.theme-text');
    
    if (theme === 'light') {
        document.body.classList.add('light-mode');
        themeIcon.textContent = '🌙';
        themeText.textContent = 'Dark Mode';
        
        // Switch to light map tiles
        if (window.map) {
            // Remove dark tile layer
            if (window.darkTileLayer) {
                window.map.removeLayer(window.darkTileLayer);
            }
            
            // Add light tile layer
            window.lightTileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(window.map);
        }
        
        // Update chart colors for light mode
        updateChartColors('light');
    } else {
        document.body.classList.remove('light-mode');
        themeText.textContent = 'Light Mode';
        
        // Switch to dark map tiles
        if (window.map) {
            // Remove light tile layer
            if (window.lightTileLayer) {
                window.map.removeLayer(window.lightTileLayer);
            }
            
            // Add dark tile layer
            window.darkTileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '© CARTO'
            }).addTo(window.map);
        }
        
        // Update chart colors for dark mode
        updateChartColors('dark');
    }
}

function updateChartColors(theme) {
    const textColor = theme === 'light' ? '#333' : '#ffffff';
    const gridColor = theme === 'light' ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)';
    
    // Update existing charts
    Object.values(charts).forEach(chart => {
        if (chart && chart.options) {
            // Update scales
            if (chart.options.scales) {
                Object.values(chart.options.scales).forEach(scale => {
                    if (scale.grid) {
                        scale.grid.color = gridColor;
                    }
                    if (scale.ticks) {
                        scale.ticks.color = textColor;
                    }
                    if (scale.title) {
                        scale.title.color = textColor;
                    }
                });
            }
            
            // Update legend
            if (chart.options.plugins && chart.options.plugins.legend) {
                chart.options.plugins.legend.labels.color = textColor;
            }
            
            chart.update();
        }
    });
}

// Initialize theme toggle when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeThemeToggle();
});
