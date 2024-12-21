// Function to initialize map with Palantir-like dark theme
function initializeMap(elementId, initialView = [21.3069, -157.8583], initialZoom = 10) {
    const map = L.map(elementId, {
        zoomControl: true,
        scrollWheelZoom: true
    }).setView(initialView, initialZoom);
    
    // Using CARTO's dark matter style which resembles Palantir's aesthetic
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd'
    }).addTo(map);
    
    return map;
}

// Add Palantir-like styling for map elements
const mapStyles = document.createElement('style');
mapStyles.textContent = `
    .leaflet-container {
        background: #161616;
    }

    .leaflet-popup-content-wrapper,
    .leaflet-popup-tip {
        background-color: #242424;
        color: #e5e7eb;
        border: 1px solid #404040;
        border-radius: 4px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5),
                    0 2px 4px -1px rgba(0, 0, 0, 0.36);
    }

    .leaflet-popup-content {
        margin: 12px;
        line-height: 1.5;
    }
    
    .leaflet-container a {
        color: #60a5fa;
    }
    
    .leaflet-control-zoom a {
        background-color: #242424;
        color: #e5e7eb;
        border-color: #404040;
    }
    
    .leaflet-control-zoom a:hover {
        background-color: #323232;
    }
    
    .leaflet-bar {
        border-color: #404040;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .leaflet-control-attribution {
        background-color: rgba(36, 36, 36, 0.8);
        color: #a0aec0;
        border-top: 1px solid #404040;
    }
    
    .leaflet-control-attribution a {
        color: #60a5fa;
    }

    /* Custom marker styling */
    .leaflet-marker-icon {
        filter: brightness(0.9) saturate(0.8);
    }

    /* Hover effects */
    .leaflet-control-zoom a:hover,
    .leaflet-bar a:hover {
        background-color: #323232;
        border-color: #525252;
    }

    /* Focus states */
    .leaflet-control-zoom a:focus,
    .leaflet-bar a:focus {
        outline: none;
        box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.5);
    }
`;
document.head.appendChild(mapStyles);
