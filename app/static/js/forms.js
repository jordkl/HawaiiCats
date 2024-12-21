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
        currentSize: parseInt(data.currentSize),
        sterilizedCount: parseInt(data.sterilizedCount),
        monthlySterilizationRate: parseInt(data.monthlySterilizationRate),
        latitude: parseFloat(data.latitude),
        longitude: parseFloat(data.longitude),
        breedingRate: parseFloat(data.breedingRate),
        kittensPerLitter: parseFloat(data.kittensPerLitter),
        littersPerYear: parseFloat(data.littersPerYear),
        kittenSurvivalRate: parseFloat(data.kittenSurvivalRate),
        adultSurvivalRate: parseFloat(data.adultSurvivalRate),
        waterAvailability: parseFloat(data.waterAvailability),
        shelterQuality: parseFloat(data.shelterQuality),
        territorySize: parseInt(data.territorySize),
        urbanRisk: parseFloat(data.urbanRisk),
        diseaseRisk: parseFloat(data.diseaseRisk),
        caretakerSupport: parseFloat(data.caretakerSupport),
        feedingConsistency: parseFloat(data.feedingConsistency)
    };
}

function processSightingFormData(data) {
    return {
        bestCount: parseInt(data.bestCount),
        minimumCount: parseInt(data.minimumCount),
        maximumCount: parseInt(data.maximumCount),
        visibleCats: parseInt(data.visibleCats),
        locationType: data.locationType,
        latitude: parseFloat(data.latitude),
        longitude: parseFloat(data.longitude),
        observedFeeding: data.observedFeeding === 'on',
        uncertaintyLevel: data.uncertaintyLevel,
        movementLevel: data.movementLevel,
        timeSpent: data.timeSpent,
        notes: data.notes || ''
    };
}
