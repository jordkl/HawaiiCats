// Colony management functionality
let currentColony = null;

// Show colony details in the sidebar
function showColonyDetails(colony) {
    if (!colony) {
        console.error('No colony data provided');
        return;
    }
    
    currentColony = colony;
    
    // Clear previous selection
    if (selectedMarker) {
        selectedMarker.getElement().classList.remove('selected');
        selectedMarker = null;
    }
    
    // Update view mode display
    document.getElementById('colonyDetailName').textContent = colony.name || 'Unnamed Colony';
    document.getElementById('colonyDetailPopulation').textContent = colony.current_size || 'Unknown';
    document.getElementById('colonyDetailLocation').textContent = `${colony.latitude.toFixed(6)}, ${colony.longitude.toFixed(6)}`;
    
    // Format timestamps
    if (colony.created_at) {
        const createdDate = new Date(colony.created_at);
        document.getElementById('colonyDetailCreatedAt').textContent = createdDate.toLocaleDateString() + ' ' + createdDate.toLocaleTimeString();
    }
    if (colony.updated_at) {
        const updatedDate = new Date(colony.updated_at);
        document.getElementById('colonyDetailUpdatedAt').textContent = updatedDate.toLocaleDateString() + ' ' + updatedDate.toLocaleTimeString();
    }
    
    document.getElementById('colonyDetailNotes').textContent = colony.notes || 'No notes available';

    // Show colony details view
    const colonyList = document.getElementById('colonyList');
    const colonyDetails = document.getElementById('colonyDetails');
    const viewMode = document.getElementById('colonyViewMode');
    const editMode = document.getElementById('colonyEditMode');
    
    colonyList.classList.add('hidden');
    colonyDetails.classList.remove('hidden');
    viewMode.classList.remove('hidden');
    editMode.classList.add('hidden');
}

// Toggle between view and edit modes for colony details
function toggleColonyEdit() {
    const viewMode = document.getElementById('colonyViewMode');
    const editMode = document.getElementById('colonyEditMode');
    const isEditing = viewMode.classList.contains('hidden');

    if (isEditing) {
        // Switch to view mode
        viewMode.classList.remove('hidden');
        editMode.classList.add('hidden');
    } else {
        // Switch to edit mode and populate form
        viewMode.classList.add('hidden');
        editMode.classList.remove('hidden');
        populateEditForm();
    }
}

// Populate the edit form with current colony data
function populateEditForm() {
    const colony = currentColony;
    if (!colony) return;

    // Basic Information
    document.getElementById('editColonyId').value = colony.id;
    document.getElementById('editColonyName').value = colony.name;
    document.getElementById('editColonyPopulation').value = colony.current_size;
    document.getElementById('editColonySterilized').value = colony.sterilized_count;
    document.getElementById('editColonyMonthlyRate').value = colony.monthly_sterilization_rate || 0;
    document.getElementById('editColonyNotes').value = colony.notes || '';

    // Environmental Factors
    document.getElementById('editWaterAvailability').value = colony.water_availability || 0.8;
    document.getElementById('editShelterQuality').value = colony.shelter_quality || 0.7;
    document.getElementById('editTerritorySize').value = colony.territory_size || 500;

    // Breeding Parameters
    document.getElementById('editBreedingRate').value = colony.breeding_rate || 0.85;
    document.getElementById('editKittensPerLitter').value = colony.kittens_per_litter || 4;
    document.getElementById('editLittersPerYear').value = colony.litters_per_year || 2.5;
    document.getElementById('editKittenSurvival').value = colony.kitten_survival_rate || 0.75;
    document.getElementById('editAdultSurvival').value = colony.adult_survival_rate || 0.85;

    // Risk Factors
    document.getElementById('editUrbanRisk').value = colony.urban_risk || 0.15;
    document.getElementById('editDiseaseRisk').value = colony.disease_risk || 0.1;

    // Support Factors
    document.getElementById('editCaretakerSupport').value = colony.caretaker_support || 0.8;
    document.getElementById('editFeedingConsistency').value = colony.feeding_consistency || 0.8;
}

// Handle colony edit form submission
document.addEventListener('DOMContentLoaded', () => {
    const colonyEditForm = document.getElementById('colonyEditForm');
    if (colonyEditForm) {
        colonyEditForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const colonyId = document.getElementById('editColonyId').value;

            const formData = {
                name: document.getElementById('editColonyName').value,
                current_size: parseInt(document.getElementById('editColonyPopulation').value),
                sterilized_count: parseInt(document.getElementById('editColonySterilized').value),
                monthly_sterilization_rate: parseFloat(document.getElementById('editColonyMonthlyRate').value),
                notes: document.getElementById('editColonyNotes').value,
                
                // Keep location data
                latitude: currentColony.latitude,
                longitude: currentColony.longitude,
                
                // Environmental factors
                water_availability: parseFloat(document.getElementById('editWaterAvailability').value),
                shelter_quality: parseFloat(document.getElementById('editShelterQuality').value),
                territory_size: parseInt(document.getElementById('editTerritorySize').value),
                
                // Breeding parameters
                breeding_rate: parseFloat(document.getElementById('editBreedingRate').value),
                kittens_per_litter: parseFloat(document.getElementById('editKittensPerLitter').value),
                litters_per_year: parseFloat(document.getElementById('editLittersPerYear').value),
                kitten_survival_rate: parseFloat(document.getElementById('editKittenSurvival').value),
                adult_survival_rate: parseFloat(document.getElementById('editAdultSurvival').value),
                
                // Risk factors
                urban_risk: parseFloat(document.getElementById('editUrbanRisk').value),
                disease_risk: parseFloat(document.getElementById('editDiseaseRisk').value),
                
                // Support factors
                caretaker_support: parseFloat(document.getElementById('editCaretakerSupport').value),
                feeding_consistency: parseFloat(document.getElementById('editFeedingConsistency').value)
            };

            try {
                const response = await fetch(`/api/colonies/${colonyId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                if (!response.ok) {
                    throw new Error('Failed to update colony');
                }

                const updatedColony = await response.json();
                currentColony = updatedColony; // Update the current colony data
                
                // Switch back to view mode and refresh the display
                toggleColonyEdit();
                showColonyDetails(updatedColony);
                
                // Refresh the map markers
                await loadColonies();
                
                // Show success message
                showNotification('Colony updated successfully', 'success');
            } catch (error) {
                console.error('Error updating colony:', error);
                showNotification('Failed to update colony', 'error');
            }
        });
    }
});
