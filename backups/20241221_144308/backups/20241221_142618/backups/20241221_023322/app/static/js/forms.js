// Form handling functions
async function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    let endpoint;
    let processedData;
    
    if (form.id === 'colonyForm') {
        endpoint = '/api/colonies';
        processedData = processColonyFormData(data);
    } else if (form.id === 'sightingForm') {
        endpoint = '/api/sightings';
        processedData = processSightingFormData(data);
    }

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(processedData)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        showNotification('Successfully added!', 'success');
        form.reset();
        
        // Reload markers
        if (form.id === 'colonyForm') {
            loadColonies();
        } else {
            loadSightings();
        }
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error adding entry: ' + error.message, 'error');
    }
}

function processColonyFormData(data) {
    return {
        name: data.colonyName,
        current_size: parseInt(data.currentSize),
        sterilized_count: parseInt(data.sterilizedCount),
        monthly_sterilization_rate: parseInt(data.monthlysterilization),
        latitude: parseFloat(data.latitude),
        longitude: parseFloat(data.longitude),
        breeding_rate: parseFloat(data.breedingRate),
        kittens_per_litter: parseFloat(data.kittensPerLitter),
        litters_per_year: parseFloat(data.littersPerYear),
        kitten_survival_rate: parseFloat(data.kittenSurvivalRate),
        adult_survival_rate: parseFloat(data.adultSurvivalRate),
        water_availability: parseFloat(data.waterAvailability),
        shelter_quality: parseFloat(data.shelterQuality),
        territory_size: parseInt(data.territorySize),
        urban_risk: parseFloat(data.urbanRisk),
        disease_risk: parseFloat(data.diseaseRisk),
        caretaker_support: parseFloat(data.caretakerSupport),
        feeding_consistency: parseFloat(data.feedingConsistency)
    };
}

function processSightingFormData(data) {
    return {
        best_count: parseInt(data.bestCount),
        minimum_count: parseInt(data.minimumCount),
        maximum_count: parseInt(data.maximumCount),
        visible_cats: parseInt(data.visibleCats),
        location_type: data.locationType,
        latitude: parseFloat(data.latitude),
        longitude: parseFloat(data.longitude),
        observed_feeding: data.observedFeeding === 'on',
        uncertainty_level: data.uncertaintyLevel,
        movement_level: data.movementLevel,
        time_spent: data.timeSpent,
        notes: data.notes || ''
    };
}
