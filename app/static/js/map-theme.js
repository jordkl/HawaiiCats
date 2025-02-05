// Function to initialize map with Palantir-like dark theme
function initializeMap(elementId, initialView = [20.2927, -156.3737], initialZoom = 7) {
    const map = L.map(elementId, {
        zoomControl: true,
        scrollWheelZoom: true
    }).setView(initialView, initialZoom);
    
    // Base layers
    const darkLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd'
    });

    const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    });

    const lightLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd'
    });

    const streetLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });

    // Add dark layer by default
    darkLayer.addTo(map);

    // Create layer control
    const baseLayers = {
        "Dark": darkLayer,
        "Satellite": satelliteLayer,
        "Light": lightLayer,
        "Street": streetLayer
    };

    L.control.layers(baseLayers, null, {
        position: 'topright',
        collapsed: false
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
    
    .leaflet-control-zoom a,
    .leaflet-control-layers-toggle,
    .leaflet-control-layers {
        background-color: #242424 !important;
        color: #e5e7eb !important;
        border-color: #404040 !important;
    }
    
    .leaflet-control-layers {
        padding: 6px 8px;
        border-radius: 4px;
    }
    
    .leaflet-control-layers label {
        color: #e5e7eb;
    }
    
    .leaflet-control-zoom a:hover,
    .leaflet-control-layers-toggle:hover {
        background-color: #323232 !important;
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

    /* Layer control specific styles */
    .leaflet-control-layers-expanded {
        background-color: #242424;
        border-color: #404040;
        color: #e5e7eb;
    }

    .leaflet-control-layers-separator {
        border-top-color: #404040;
    }
`;
document.head.appendChild(mapStyles);
