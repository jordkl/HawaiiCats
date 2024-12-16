// Global variables
let map;
let colonyMarkers = [];
let sightingMarkers = [];
let selectedMarker = null;
let cachedColonies = [];
let cachedSightings = [];
let colonyIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});
let sightingIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// Debounce function to limit API calls
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize map and load data
async function initMap() {
    try {
        // Initialize the map
        map = L.map('map').setView([21.3099, -157.8581], 11);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
        }).addTo(map);

        // Load initial data
        await Promise.all([
            loadColonies(),
            loadSightings()
        ]);

        // Set up map event listeners
        map.on('moveend', updateVisibleItems);
        map.on('zoomend', updateVisibleItems);

        // Initial update of visible items
        updateVisibleItems();
    } catch (error) {
        console.error('Error initializing map:', error);
        showNotification('Failed to initialize map', 'error');
    }
}

// Load colonies data
async function loadColonies() {
    try {
        const response = await fetch('/api/colonies');
        if (!response.ok) {
            throw new Error('Failed to fetch colonies');
        }
        const coloniesData = await response.json();
        
        // Process colonies data
        cachedColonies = coloniesData.filter(colony => {
            if (!colony) return false;
            
            // Extract coordinates
            const lat = colony.coordinate ? colony.coordinate.latitude : colony.latitude;
            const lng = colony.coordinate ? colony.coordinate.longitude : colony.longitude;
            
            // Validate coordinates
            if (typeof lat !== 'number' || typeof lng !== 'number' || isNaN(lat) || isNaN(lng)) {
                console.log('Invalid coordinates for colony:', colony);
                return false;
            }
            
            // Add normalized coordinates
            colony.latitude = lat;
            colony.longitude = lng;
            return true;
        });
        
        console.log('Loaded colonies:', cachedColonies);
    } catch (error) {
        console.error('Error loading colonies:', error);
        showNotification('Failed to load colonies', 'error');
    }
}

// Load sightings data
async function loadSightings() {
    try {
        const response = await fetch('/api/sightings');
        if (!response.ok) {
            throw new Error('Failed to fetch sightings');
        }
        const sightingsData = await response.json();
        console.log('Raw sightings data:', sightingsData);
        
        // Process sightings data
        cachedSightings = sightingsData.filter(sighting => {
            // Validate required fields
            if (!sighting || !sighting.coordinate) {
                console.log('Missing coordinate for sighting:', sighting);
                return false;
            }

            // Extract coordinates
            const lat = parseFloat(sighting.coordinate.latitude);
            const lng = parseFloat(sighting.coordinate.longitude);
            
            // Validate coordinates
            if (isNaN(lat) || isNaN(lng)) {
                console.log('Invalid coordinates for sighting:', sighting);
                return false;
            }
            
            // Add normalized coordinates
            sighting.latitude = lat;
            sighting.longitude = lng;
            
            // Ensure timestamp is valid
            if (!sighting.timestamp) {
                console.log('Missing timestamp for sighting:', sighting);
                return false;
            }
            
            // Store timestamp as date_sighted for consistency
            sighting.date_sighted = sighting.timestamp;
            
            // Store cat count
            sighting.cat_count = sighting.best_count || 0;
            
            return true;
        });
        
        console.log('Processed sightings:', cachedSightings);
        
        // Update map if it's ready
        if (map && map.getBounds) {
            updateVisibleItems();
        }
    } catch (error) {
        console.error('Error loading sightings:', error);
        showNotification('Failed to load sightings', 'error');
    }
}

// Update visible items based on map bounds
function updateVisibleItems() {
    if (!map || !map.getBounds) {
        console.log('Map not ready');
        return;
    }
    
    const bounds = map.getBounds();
    console.log('Current map bounds:', bounds);
    console.log('Current view:', window.currentView);
    
    // Clear existing markers
    colonyMarkers.forEach(marker => marker.remove());
    sightingMarkers.forEach(marker => marker.remove());
    colonyMarkers = [];
    sightingMarkers = [];
    
    try {
        // Filter and show items based on current view
        if (window.currentView === 'colonies' && cachedColonies && cachedColonies.length > 0) {
            // Filter colonies within current bounds
            const visibleColonies = cachedColonies.filter(colony => 
                bounds.contains([colony.latitude, colony.longitude])
            );
            
            console.log('Showing colonies in view:', visibleColonies.length);
            
            // Update colony list in sidebar
            const colonyList = document.getElementById('colonyList');
            if (colonyList) {
                colonyList.innerHTML = '';
                visibleColonies.forEach(colony => {
                    const item = document.createElement('div');
                    item.className = 'p-2 hover:bg-gray-100 cursor-pointer flex items-center justify-between';
                    item.innerHTML = `
                        <span>${colony.name || 'Unnamed Colony'}</span>
                        <span class="text-sm text-gray-500">${colony.current_size || 0} cats</span>
                    `;
                    item.onclick = () => {
                        map.setView([colony.latitude, colony.longitude], 15);
                        showColonyDetails(colony);
                    };
                    colonyList.appendChild(item);
                    addColonyMarker(colony);
                });
            }
        } else if (window.currentView === 'sightings' && cachedSightings && cachedSightings.length > 0) {
            // Filter sightings within current bounds
            const visibleSightings = cachedSightings.filter(sighting => 
                bounds.contains([sighting.latitude, sighting.longitude])
            );
            
            console.log('Showing sightings in view:', visibleSightings.length);
            
            // Update sighting list in sidebar
            const sightingList = document.getElementById('sightingList');
            if (sightingList) {
                sightingList.innerHTML = '';
                visibleSightings.forEach(sighting => {
                    const item = document.createElement('div');
                    item.className = 'p-2 hover:bg-gray-100 cursor-pointer';
                    item.textContent = formatSightingTitle(sighting);
                    item.onclick = () => {
                        map.setView([sighting.latitude, sighting.longitude], 15);
                        showSightingDetails(sighting);
                    };
                    sightingList.appendChild(item);
                    addSightingMarker(sighting);
                });
            }
        }
    } catch (error) {
        console.error('Error updating visible items:', error);
        showNotification('Failed to update map', 'error');
    }
}

// Add colony marker to map
function addColonyMarker(colony) {
    const marker = L.marker([colony.latitude, colony.longitude], {
        icon: colonyIcon
    });
    
    marker.on('click', () => {
        showColonyDetails(colony);
    });
    
    marker.addTo(map);
    colonyMarkers.push(marker);
    return marker;
}

// Add sighting marker to map
function addSightingMarker(sighting) {
    const marker = L.marker([sighting.latitude, sighting.longitude], {
        icon: sightingIcon
    });
    
    marker.on('click', () => {
        showSightingDetails(sighting);
    });
    
    marker.addTo(map);
    sightingMarkers.push(marker);
    return marker;
}

// Show colony details in sidebar
function showColonyDetails(colony) {
    const detailsContainer = document.getElementById('itemDetails');
    if (!detailsContainer) return;

    detailsContainer.innerHTML = `
        <div class="p-4">
            <h3 class="text-lg font-bold mb-2">${colony.name || 'Unnamed Colony'}</h3>
            <div class="space-y-2">
                <p><strong>Current Size:</strong> ${colony.current_size || 'Unknown'} cats</p>
                <p><strong>Location:</strong> ${colony.location_description || 'No description available'}</p>
                <p><strong>Status:</strong> ${colony.status || 'Unknown'}</p>
                <p><strong>Notes:</strong> ${colony.notes || 'No notes available'}</p>
            </div>
        </div>
    `;
    
    // Show the details container
    detailsContainer.classList.remove('hidden');
}

// Show sighting details in sidebar
function showSightingDetails(sighting) {
    const detailsContainer = document.getElementById('itemDetails');
    if (!detailsContainer) return;

    const date = new Date(sighting.date_sighted);
    const formattedDate = date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
    const count = sighting.cat_count || 'Unknown';
    
    detailsContainer.innerHTML = `
        <div class="p-4">
            <h3 class="text-lg font-bold mb-2">Cat Sighting</h3>
            <div class="space-y-2">
                <p><strong>Date:</strong> ${formattedDate}</p>
                <p><strong>Number of Cats:</strong> ${count} cat${count !== 1 ? 's' : ''}</p>
                <p><strong>Description:</strong> ${sighting.description || 'No description available'}</p>
                <p><strong>Location:</strong> ${sighting.location_description || 'No location description'}</p>
            </div>
        </div>
    `;
    
    // Show the details container
    detailsContainer.classList.remove('hidden');
}

// Format sighting title for display
function formatSightingTitle(sighting) {
    const date = new Date(sighting.date_sighted);
    const formattedDate = date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
    const count = sighting.cat_count || 'Unknown';
    return `${formattedDate} - ${count} cat${count !== 1 ? 's' : ''}`;
}

// Show notification
function showNotification(message, type = 'info') {
    // Implement notification display
    console.log(`${type.toUpperCase()}: ${message}`);
}

// Initialize map when document is ready
document.addEventListener('DOMContentLoaded', initMap);
