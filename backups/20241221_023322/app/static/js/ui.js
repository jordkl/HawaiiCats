// UI state management
window.currentView = 'colonies';  // Make currentView globally accessible

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    if (notification) {
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.style.display = 'block';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }
}

// Switch between colonies and sightings views
function switchView(view) {
    window.currentView = view;
    
    // Update tab styles
    document.querySelectorAll('.tab').forEach(tab => {
        if (tab.dataset.view === view) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Show/hide content
    document.querySelectorAll('.content').forEach(content => {
        content.style.display = content.dataset.view === view ? 'block' : 'none';
    });
    
    // Update visible items on the map
    updateVisibleItems();
}

// Handle tab switching
function setupTabs() {
    const coloniesTab = document.getElementById('coloniesTab');
    const sightingsTab = document.getElementById('sightingsTab');

    if (coloniesTab && sightingsTab) {
        coloniesTab.addEventListener('click', () => {
            switchView('colonies');
        });

        sightingsTab.addEventListener('click', () => {
            switchView('sightings');
        });
    }
}

// Show sighting list
function showSightingList() {
    const sightingList = document.getElementById('sightingList');
    const sightingDetails = document.getElementById('sightingDetails');

    if (sightingList && sightingDetails) {
        sightingList.classList.remove('hidden');
        sightingDetails.classList.add('hidden');
    }
}

// Show sighting details
function showSightingDetails(sighting) {
    console.log('Showing sighting details:', sighting);
    
    const sightingList = document.getElementById('sightingList');
    const sightingDetails = document.getElementById('sightingDetails');
    const countElement = document.getElementById('sightingDetailCount');
    const typeElement = document.getElementById('sightingDetailType');
    const dateElement = document.getElementById('sightingDetailDate');
    const feedingElement = document.getElementById('sightingDetailFeeding');
    const locationElement = document.getElementById('sightingDetailLocation');

    // Debug log elements
    console.log('Elements found:', {
        sightingList: !!sightingList,
        sightingDetails: !!sightingDetails,
        countElement: !!countElement,
        typeElement: !!typeElement,
        dateElement: !!dateElement,
        feedingElement: !!feedingElement,
        locationElement: !!locationElement
    });

    if (!sightingDetails || !sighting) {
        console.error('Missing required elements or sighting data');
        return;
    }

    // Update details
    if (countElement) countElement.textContent = sighting.best_count || 'Unknown';
    if (typeElement) typeElement.textContent = sighting.location_type || 'Unknown';
    if (dateElement && sighting.timestamp) {
        const date = new Date(sighting.timestamp);
        dateElement.textContent = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
    if (feedingElement) feedingElement.textContent = sighting.is_feeding ? 'Yes' : 'No';
    if (locationElement) locationElement.textContent = `${sighting.latitude.toFixed(6)}, ${sighting.longitude.toFixed(6)}`;

    // Show details view, hide list
    if (sightingList) sightingList.classList.add('hidden');
    sightingDetails.classList.remove('hidden');
    
    console.log('Sighting details updated and shown');
}

// Toggle adding sighting
function toggleAddingSighting() {
    const sightingList = document.getElementById('sightingList');
    const sightingDetails = document.getElementById('sightingDetails');
    const sightingForm = document.getElementById('sightingForm');
    
    if (sightingList && sightingDetails && sightingForm) {
        sightingForm.classList.remove('hidden');
        sightingList.classList.add('hidden');
        sightingDetails.classList.add('hidden');
        
        // Reset form
        sightingForm.reset();
    }
}

// Tab switching functionality
document.addEventListener('DOMContentLoaded', () => {
    const coloniesTab = document.getElementById('coloniesTab');
    const sightingsTab = document.getElementById('sightingsTab');
    const colonyList = document.getElementById('colonyList');
    const sightingList = document.getElementById('sightingList');

    coloniesTab.addEventListener('click', () => {
        // Update tab styles
        coloniesTab.classList.add('active');
        sightingsTab.classList.remove('active');

        // Show/hide lists
        colonyList.classList.remove('hidden');
        sightingList.classList.add('hidden');

        // Update current view and refresh map
        window.currentView = 'colonies';
        updateVisibleItems();
    });

    sightingsTab.addEventListener('click', () => {
        // Update tab styles
        sightingsTab.classList.add('active');
        coloniesTab.classList.remove('active');

        // Show/hide lists
        sightingList.classList.remove('hidden');
        colonyList.classList.add('hidden');

        // Update current view and refresh map
        window.currentView = 'sightings';
        updateVisibleItems();
    });
});

// Initialize UI
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    showSightingList(); // Show sighting list by default
    
    // Load initial data
    loadSightings();
});
