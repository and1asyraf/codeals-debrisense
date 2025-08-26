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

// Add Sungai Inanam marker
const sungaiInanamMarker = L.marker([5.997846609055653, 116.12997039272707], { icon: donutIcon })
    .addTo(map);

// Add click event to toggle sidebar
sungaiInanamMarker.on('click', function() {
    showLocationInfo();
    toggleSidebar();
});

// Function to toggle sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

// Function to show location information
function showLocationInfo() {
    const locationInfo = document.getElementById('location-info');
    locationInfo.innerHTML = `
        <div class="location-image">
            <img src="data/image/sungaiInanam.png" alt="Sungai Inanam" class="location-img">
        </div>
        
        <div class="river-name">
            <h3>Sungai Inanam</h3>
        </div>
    `;
}

// Ensure map fills the available space
map.invalidateSize();
