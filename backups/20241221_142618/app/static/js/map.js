// Global variables
let map;
let colonyMarkers = [];
let sightingMarkers = [];
let selectedMarker = null;
let cachedColonies = [];
let cachedSightings = [];
let isAddingColony = false;  // Initialize isAddingColony
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
let currentView = 'colonies'; // Initialize currentView

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
        // Initialize the map using our dark theme
        map = initializeMap('map', [21.3099, -157.8581], 11);
        
        // Set up map click handler for colony placement
        map.on('click', function(e) {
            // Only show modal if we're in colony placement mode
            if (!isAddingColony) {
                return;
            }
            
            const lat = e.latlng.lat.toFixed(6);
            const lng = e.latlng.lng.toFixed(6);
            
            // Fill in the form with the coordinates
            document.getElementById('colonyLat').value = lat;
            document.getElementById('colonyLng').value = lng;
            
            // Show the modal
            document.getElementById('addColonyModal').classList.remove('hidden');
            
            // Exit colony placement mode
            exitAddColonyMode();
        });

        // Set up UI components first
        setupAddColonyButton();

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

// Set up add colony button and form handlers
function setupAddColonyButton() {
    const addColonyBtn = document.getElementById('addColonyBtn');
    const addColonyModal = document.getElementById('addColonyModal');
    const closeModalBtn = document.getElementById('closeAddColonyModal');
    const cancelBtn = document.getElementById('cancelAddColony');
    const addColonyForm = document.getElementById('addColonyForm');
    
    console.log('Setting up add colony button...'); // Debug log
    
    // Add colony button click handler
    addColonyBtn.addEventListener('click', (e) => {
        e.preventDefault();  // Prevent any default button behavior
        e.stopPropagation(); // Prevent event bubbling
        console.log('Add colony button clicked, current isAddingColony:', isAddingColony); // Debug log
        
        if (isAddingColony) {
            console.log('Exiting add colony mode...'); // Debug log
            exitAddColonyMode();
        } else {
            console.log('Entering add colony mode...'); // Debug log
            enterAddColonyMode();
        }
    });
    
    // Close modal handlers
    [closeModalBtn, cancelBtn].forEach(btn => {
        if (btn) {  // Check if button exists
            btn.addEventListener('click', () => {
                addColonyModal.classList.add('hidden');
                exitAddColonyMode();
                addColonyForm.reset(); // Reset form when closing
            });
        }
    });

    // Form submission handler
    addColonyForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        try {
            console.log('Checking Firebase initialization...');
            if (!window.auth) {
                throw new Error('Firebase Auth not initialized');
            }

            console.log('Waiting for auth state...');
            // Wait for Firebase Auth to initialize
            await new Promise((resolve, reject) => {
                const unsubscribe = window.auth.onAuthStateChanged(user => {
                    unsubscribe();
                    console.log('Auth state changed, user:', user);
                    resolve();
                }, error => {
                    console.error('Auth state change error:', error);
                    reject(error);
                });
            });

            console.log('Checking current user...');
            // Get current user's email
            const currentUser = window.auth.currentUser;
            if (!currentUser) {
                console.log('No user logged in');
                showNotification('You must be logged in to add a colony', 'error');
                return;
            }
            console.log('Current user:', currentUser.email);

            const formData = {
                name: document.getElementById('colonyName').value,
                latitude: parseFloat(document.getElementById('colonyLat').value),
                longitude: parseFloat(document.getElementById('colonyLng').value),
                currentSize: parseInt(document.getElementById('colonySize').value),
                sterilizedCount: parseInt(document.getElementById('sterilizedCount').value),
                monthlySterilizationRate: parseFloat(document.getElementById('monthlyRate').value) || 0,
                breedingRate: parseFloat(document.getElementById('breedingRate').value) || 0.7,
                kittensPerLitter: parseInt(document.getElementById('kittensPerLitter').value) || 4,
                littersPerYear: parseInt(document.getElementById('littersPerYear').value) || 2,
                adultSurvivalRate: parseFloat(document.getElementById('adultSurvivalRate').value) || 0.7,
                kittenSurvivalRate: parseFloat(document.getElementById('kittenSurvivalRate').value) || 0.6,
                territorySize: parseInt(document.getElementById('territorySize').value) || 2500,
                baseFoodCapacity: parseFloat(document.getElementById('baseFoodCapacity').value) || 0.9,
                foodScalingFactor: parseFloat(document.getElementById('foodScalingFactor').value) || 0.8,
                feedingConsistency: parseFloat(document.getElementById('feedingConsistency').value) || 0.8,
                waterAvailability: parseFloat(document.getElementById('waterAvailability').value) || 0.7,
                shelterQuality: parseFloat(document.getElementById('shelterQuality').value) || 0.7,
                diseaseRisk: parseFloat(document.getElementById('diseaseRisk').value) || 0.1,
                naturalRisk: parseFloat(document.getElementById('naturalRisk').value) || 0.1,
                urbanRisk: parseFloat(document.getElementById('urbanRisk').value) || 0.1,
                densityMortalityFactor: parseFloat(document.getElementById('densityMortalityFactor').value) || 0.5,
                survivalDensityFactor: parseFloat(document.getElementById('survivalDensityFactor').value) || 0.3,
                mortalityThreshold: parseInt(document.getElementById('mortalityThreshold').value) || 30,
                peakBreedingMonth: parseInt(document.getElementById('peakBreedingMonth').value) || 1,
                seasonalBreedingAmplitude: parseFloat(document.getElementById('seasonalBreedingAmplitude').value) || 0.3,
                caretakerSupport: parseFloat(document.getElementById('caretakerSupport').value) || 1,
                notes: document.getElementById('colonyNotes').value || '',
                status: 'active',
                timestamp: new Date().toISOString(),
                createdBy: currentUser.email
            };
            
            try {
                const response = await fetch('/api/colonies', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) {
                    throw new Error('Failed to add colony');
                }
                
                // Add the new colony to the cache and update the map
                const newColony = await response.json();
                cachedColonies.push(newColony);
                updateVisibleItems();
                
                // Hide the modal and show success message
                addColonyModal.classList.add('hidden');
                showNotification('Colony added successfully', 'success');
                exitAddColonyMode();
                
                // Clear the form
                addColonyForm.reset();
            } catch (error) {
                console.error('Error adding colony:', error);
                showNotification('Failed to add colony', 'error');
            }
        } catch (error) {
            console.error('Error adding colony:', error);
            showNotification('Failed to add colony', 'error');
        }
    });
}

// Enter colony placement mode
function enterAddColonyMode() {
    console.log('Entering add colony mode...'); // Debug log
    isAddingColony = true;
    console.log('isAddingColony set to:', isAddingColony); // Debug log
    
    // Get all map elements
    const mapContainer = map.getContainer();
    
    // Set cursor style using Leaflet's built-in classes
    L.DomUtil.removeClass(mapContainer, 'leaflet-grab');
    L.DomUtil.addClass(mapContainer, 'leaflet-crosshair');
    
    // Also set explicit cursor style
    mapContainer.style.cursor = 'crosshair';
    
    // Update button state and show notification
    document.getElementById('addColonyBtn').classList.add('bg-gray-500');
    showNotification('Click on the map to place the colony', 'info');
    
    // Hide modal
    const modal = document.getElementById('addColonyModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Exit colony placement mode
function exitAddColonyMode() {
    console.log('Exiting add colony mode...'); // Debug log
    isAddingColony = false;
    
    // Reset cursor style using Leaflet's built-in classes
    const mapContainer = map.getContainer();
    L.DomUtil.addClass(mapContainer, 'leaflet-grab');
    L.DomUtil.removeClass(mapContainer, 'leaflet-crosshair');
    
    // Reset explicit cursor style
    mapContainer.style.cursor = '';
    
    document.getElementById('addColonyBtn').classList.remove('bg-gray-500');
}

// Load colonies data
async function loadColonies() {
    try {
        const response = await fetch('/api/colonies');
        if (!response.ok) {
            throw new Error('Failed to fetch colonies');
        }
        const coloniesData = await response.json();
        console.log('Raw colonies data:', coloniesData);
        
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
            console.log('Processed colony:', colony);
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
    console.log('Current view:', currentView);
    
    // Clear existing markers
    colonyMarkers.forEach(marker => {
        if (marker && marker.remove) {
            marker.remove();
        }
    });
    sightingMarkers.forEach(marker => {
        if (marker && marker.remove) {
            marker.remove();
        }
    });
    colonyMarkers = [];
    sightingMarkers = [];
    
    try {
        // Filter and show items based on current view
        if ((currentView === 'colonies' || !currentView) && cachedColonies && cachedColonies.length > 0) {
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
                    console.log('Rendering colony:', colony);
                    const item = document.createElement('div');
                    item.className = 'p-2 cursor-pointer transition-colors duration-200 dark:text-gray-100 hover:bg-gray-100/50 dark:hover:bg-gray-700/50 flex items-center justify-between';
                    item.innerHTML = `
                        <span>${colony.name || 'Unnamed Colony'}</span>
                        <span class="text-sm text-gray-500 dark:text-gray-400">${colony.currentSize || colony.current_size || 0} cats</span>
                    `;
                    item.onclick = () => {
                        showColonyDetails(colony);
                        // Find and highlight the corresponding marker
                        const marker = colonyMarkers.find(m => 
                            m.colony && m.colony.id === colony.id
                        );
                        if (marker) {
                            marker.getElement().classList.add('selected');
                            selectedMarker = marker;
                            map.flyTo(marker.getLngLat(), 16);
                        }
                    };
                    colonyList.appendChild(item);
                    addColonyMarker(colony);
                });
            }

        } else if (currentView === 'sightings' && cachedSightings && cachedSightings.length > 0) {
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
                    item.className = 'p-2 cursor-pointer transition-colors duration-200 dark:text-gray-100 hover:bg-gray-100/50 dark:hover:bg-gray-700/50';
                    const date = new Date(sighting.timestamp);
                    item.textContent = `${date.toLocaleDateString()} - ${sighting.best_count || 0} cats`;
                    item.onclick = () => {
                        showSightingDetails(sighting);
                        // Find and highlight the corresponding marker
                        const marker = sightingMarkers.find(m => 
                            m.sighting && m.sighting.id === sighting.id
                        );
                        if (marker) {
                            marker.getElement().classList.add('selected');
                            selectedMarker = marker;
                            map.flyTo(marker.getLngLat(), 16);
                        }
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
                <p><strong>Current Size:</strong> ${colony.currentSize || 'Unknown'} cats</p>
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

// Show colony list view
function showColonyList() {
    const colonyList = document.getElementById('colonyList');
    const colonyDetails = document.getElementById('colonyDetails');
    
    if (colonyList && colonyDetails) {
        colonyList.classList.remove('hidden');
        colonyDetails.classList.add('hidden');
    }
}

// Initialize map when document is ready
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Initialize the map using our dark theme
        map = initializeMap('map', [21.3099, -157.8581], 11);
        
        // Set up tab switching
        const tabs = document.querySelectorAll('[data-view]');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Update current view
                currentView = tab.dataset.view;
                
                // Hide all content
                document.querySelectorAll('.content').forEach(content => {
                    content.classList.add('hidden');
                });
                
                // Show selected content
                const selectedContent = document.querySelector(`[data-view="${currentView}"]`);
                if (selectedContent) {
                    selectedContent.classList.remove('hidden');
                }
                
                // Update visible items
                updateVisibleItems();
            });
        });
        
        // Set up map click handler for colony placement
        map.on('click', function(e) {
            // Only show modal if we're in colony placement mode
            if (!isAddingColony) {
                return;
            }
            
            const lat = e.latlng.lat.toFixed(6);
            const lng = e.latlng.lng.toFixed(6);
            
            // Fill in the form with the coordinates
            document.getElementById('colonyLat').value = lat;
            document.getElementById('colonyLng').value = lng;
            
            // Show the modal
            document.getElementById('addColonyModal').classList.remove('hidden');
            
            // Exit colony placement mode
            exitAddColonyMode();
        });

        // Set up UI components first
        setupAddColonyButton();

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
});
