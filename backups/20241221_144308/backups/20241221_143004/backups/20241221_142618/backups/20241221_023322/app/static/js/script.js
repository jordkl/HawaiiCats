// Function to toggle advanced mode
function toggleAdvancedMode() {
    const advancedSection = document.getElementById('advancedSection');
    const advancedModeCheckbox = document.getElementById('advancedMode');
    const dashboardContainer = document.getElementById('dashboardContainer');
    const sidebar = document.getElementById('sidebar');
    
    if (advancedModeCheckbox?.checked) {
        advancedSection?.classList.add('active');
        dashboardContainer?.classList.add('advanced-mode');
        if (sidebar) {
            sidebar.style.display = 'block';  // Keep sidebar visible
            sidebar.classList.add('advanced-mode');
        }
    } else {
        advancedSection?.classList.remove('active');
        dashboardContainer?.classList.remove('advanced-mode');
        if (sidebar) {
            sidebar.style.display = 'block';
            sidebar.classList.remove('advanced-mode');
        }
    }
}

// Function to toggle Monte Carlo mode
function toggleMonteCarlo() {
    const useMonteCarloCheckbox = document.getElementById('useMonteCarlo');
    // You can add additional logic here based on the Monte Carlo checkbox state
    if (useMonteCarloCheckbox?.checked) {
        console.log('Monte Carlo mode enabled');
    } else {
        console.log('Monte Carlo mode disabled');
    }
}

// Initialize the advanced mode state when the page loads
document.addEventListener('DOMContentLoaded', function() {
    toggleAdvancedMode();
});

// Function to collect all input values and results
function collectScenarioData() {
    // Helper function to get value with default
    const getValueWithDefault = (id, defaultValue) => {
        const element = document.getElementById(id);
        return element?.value || defaultValue;
    };

    // Basic parameters
    const inputs = {
        // Basic Parameters
        currentSize: getValueWithDefault('currentSize', ''),
        sterilizedCount: getValueWithDefault('sterilizedCount', ''),
        monthlysterilization: getValueWithDefault('monthlysterilization', ''),
        sterilizationCost: getValueWithDefault('sterilizationCost', ''),
        months: getValueWithDefault('months', ''),
        
        // Mortality Risk Factors
        urbanRisk: getValueWithDefault('urbanRisk', '0.1'),
        diseaseRisk: getValueWithDefault('diseaseRisk', '0.15'),
        naturalRisk: getValueWithDefault('naturalRisk', '0.1'),
        densityMortalityFactor: getValueWithDefault('densityMortalityFactor', '0.5'),
        mortalityThreshold: getValueWithDefault('mortalityThreshold', '30'),
        
        // Environmental Factors
        waterAvailability: getValueWithDefault('waterAvailability', '0.7'),
        shelterQuality: getValueWithDefault('shelterQuality', '0.7'),
        caretakerSupport: getValueWithDefault('caretakerSupport', '1.0'),
        feedingConsistency: getValueWithDefault('feedingConsistency', '0.8'),
        territorySize: getValueWithDefault('territorySize', '500'),
        baseFoodCapacity: getValueWithDefault('baseFoodCapacity', '0.9'),
        foodScalingFactor: getValueWithDefault('foodScalingFactor', '0.8'),
        
        // Survival Rates
        kittenSurvivalRate: getValueWithDefault('kittenSurvivalRate', '0.6'),
        adultSurvivalRate: getValueWithDefault('adultSurvivalRate', '0.7'),
        survivalDensityFactor: getValueWithDefault('survivalDensityFactor', '0.3'),
        
        // Breeding Parameters
        breedingRate: getValueWithDefault('breedingRate', '0.7'),
        kittensPerLitter: getValueWithDefault('kittensPerLitter', '4.0'),
        littersPerYear: getValueWithDefault('littersPerYear', '2.0'),
        seasonalBreedingAmplitude: getValueWithDefault('seasonalBreedingAmplitude', '0.3'),
        peakBreedingMonth: getValueWithDefault('peakBreedingMonth', '6')
    };

    // Get all model results
    const results = {
        // Population Details
        finalPopulation: document.getElementById('finalPopulation')?.innerText || '',
        populationChange: document.getElementById('populationChange')?.innerText || '',
        sterilizationRate: document.getElementById('sterilizationRate')?.innerText || '',
        
        // Cost Analysis
        totalCost: document.getElementById('totalCost')?.innerText || '',
        
        // Mortality Statistics
        totalDeaths: document.getElementById('totalDeaths')?.innerText || '',
        kittenDeaths: document.getElementById('kittenDeaths')?.innerText || '',
        adultDeaths: document.getElementById('adultDeaths')?.innerText || '',
        mortalityRate: document.getElementById('mortalityRate')?.innerText || '',
        
        // Monte Carlo Statistics (if available)
        monteCarloStats: {
            finalPopulation: {
                lower: document.getElementById('finalPopulation_lower')?.innerText || '',
                upper: document.getElementById('finalPopulation_upper')?.innerText || ''
            },
            populationChange: {
                lower: document.getElementById('populationChange_lower')?.innerText || '',
                upper: document.getElementById('populationChange_upper')?.innerText || ''
            },
            sterilizationRate: {
                lower: document.getElementById('sterilizationRate_lower')?.innerText || '',
                upper: document.getElementById('sterilizationRate_upper')?.innerText || ''
            }
        },

        // Graph Data
        graphData: (window.populationGraph && window.populationGraph.data) ? {
            labels: window.populationGraph.data.labels || [],
            datasets: window.populationGraph.data.datasets?.map(dataset => ({
                label: dataset.label || '',
                data: dataset.data || []
            })) || []
        } : null
    };

    return {
        inputs: inputs,
        results: results,
        advancedMode: document.getElementById('advancedMode')?.checked || false,
        timestamp: new Date().toISOString(),
        category: document.querySelector('input[name="category"]:checked')?.value || '',
        userNote: document.getElementById('flagScenarioNotes')?.value || '',
        email: document.getElementById('flagScenarioEmail')?.value || '',
        version: window.CALCULATOR_VERSION || '1.0.0'
    };
}

// Function to show flag scenario modal
function flagScenario() {
    // Check if a calculation has been performed
    const resultsSection = document.getElementById('resultsSection');
    if (!resultsSection || resultsSection.classList.contains('hidden')) {
        alert('Please run a calculation before flagging a scenario.');
        return;
    }

    const modal = document.getElementById('flagScenarioModal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

// Function to close flag scenario modal
function closeFlagScenarioModal() {
    const modal = document.getElementById('flagScenarioModal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    
    // Reset form
    document.querySelectorAll('input[name="category"]').forEach(radio => radio.checked = false);
    document.getElementById('flagScenarioNotes').value = '';
    document.getElementById('flagScenarioEmail').value = '';
}

// Function to validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Function to submit flag scenario
function submitFlagScenario() {
    // Get selected category
    const selectedCategory = document.querySelector('input[name="category"]:checked');
    if (!selectedCategory) {
        alert('Please select a category for your report.');
        return;
    }

    // Get notes
    const notes = document.getElementById('flagScenarioNotes').value.trim();
    if (!notes) {
        alert('Please provide some additional notes about your observation.');
        return;
    }

    // Get email (optional)
    const email = document.getElementById('flagScenarioEmail').value.trim();
    
    // Validate email format if provided
    if (email && !isValidEmail(email)) {
        alert('Please enter a valid email address or leave it empty.');
        return;
    }

    // Collect all scenario data
    const scenarioData = collectScenarioData();
    scenarioData.category = selectedCategory.value;
    scenarioData.userNote = notes;
    if (email) {
        scenarioData.userEmail = email;
    }

    // Determine the base URL based on the current environment
    const isLocalhost = ['localhost', '127.0.0.1', '192.168.1.169'].includes(window.location.hostname);
    const baseUrl = isLocalhost ? `http://${window.location.host}` : 'https://hawaiicats.org';

    // Send the data to the server
    fetch(`${baseUrl}/flag_scenario`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(scenarioData)
    })
    .then(response => response.json())
    .then(data => {
        alert('Thank you for your feedback! Your report has been saved.');
        closeFlagScenarioModal();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('There was an error saving your report. Please try again.');
    });
}

// Function to download simulation logs
function downloadLogs() {
    const scenarioData = collectScenarioData();
    
    // Create the log content
    let logContent = `Cat Colony Population Simulation Log (${scenarioData.timestamp})\n\n`;
    logContent += '=== Input Parameters ===\n';
    for (const [key, value] of Object.entries(scenarioData.inputs)) {
        logContent += `${key}: ${value}\n`;
    }
    logContent += '\n=== Simulation Results ===\n';
    logContent += `\nPopulation Details:\nFinal Population: ${scenarioData.results.finalPopulation}\nPopulation Change: ${scenarioData.results.populationChange}\nSterilization Rate: ${scenarioData.results.sterilizationRate}\n`;
    logContent += `\nCost Analysis:\nTotal Cost: ${scenarioData.results.totalCost}\n`;
    logContent += `\nMortality Statistics:\nTotal Deaths: ${scenarioData.results.totalDeaths}\nKitten Deaths: ${scenarioData.results.kittenDeaths}\nAdult Deaths: ${scenarioData.results.adultDeaths}\nMortality Rate: ${scenarioData.results.mortalityRate}\n`;

    // Create and trigger download
    const blob = new Blob([logContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cat-colony-simulation-${scenarioData.timestamp.replace(/[:.]/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Rest of your existing JavaScript code for calculations and graph plotting
