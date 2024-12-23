// Define calculator version
const CALCULATOR_VERSION = '1.0.0';
window.CALCULATOR_VERSION = CALCULATOR_VERSION;  // Make version globally available

// Determine the base URL based on the current environment
const isLocalhost = ['localhost', '127.0.0.1', '192.168.1.169'].includes(window.location.hostname);
const baseUrl = isLocalhost ? `http://${window.location.host}` : 'https://hawaiicats.org';

// Function to collect advanced parameters from the form
function collectAdvancedParameters() {
    // Basic parameters
    const params = {
        // Population dynamics
        breedingRate: parseFloat(document.getElementById('breedingRate')?.value || '0.85'),
        kittensPerLitter: parseFloat(document.getElementById('kittensPerLitter')?.value || '4'),
        littersPerYear: parseFloat(document.getElementById('littersPerYear')?.value || '2.5'),
        kittenSurvivalRate: parseFloat(document.getElementById('kittenSurvivalRate')?.value || '0.7'),
        adultSurvivalRate: parseFloat(document.getElementById('adultSurvivalRate')?.value || '0.85'),
        femaleRatio: parseFloat(document.getElementById('femaleRatio')?.value || '0.5'),
        kittenMaturityMonths: parseFloat(document.getElementById('kittenMaturityMonths')?.value || '5'),

        // Seasonal factors
        peakBreedingMonth: parseInt(document.getElementById('peakBreedingMonth')?.value || '4'),
        seasonalityStrength: parseFloat(document.getElementById('seasonalityStrength')?.value || '0.3'),

        // Environmental factors
        territorySize: parseFloat(document.getElementById('territorySize')?.value || '1000'),
        baseFoodCapacity: parseFloat(document.getElementById('baseFoodCapacity')?.value || '0.9'),
        foodScalingFactor: parseFloat(document.getElementById('foodScalingFactor')?.value || '0.8'),
        environmentalStress: parseFloat(document.getElementById('environmentalStress')?.value || '0.15'),

        // Resource factors
        resourceCompetition: parseFloat(document.getElementById('resourceCompetition')?.value || '0.2'),
        resourceScarcityImpact: parseFloat(document.getElementById('resourceScarcityImpact')?.value || '0.25'),
        caretakerSupport: parseFloat(document.getElementById('caretakerSupport')?.value || '0.5'),
        feedingConsistency: parseFloat(document.getElementById('feedingConsistency')?.value || '0.9'),
        foodCostPerCat: parseFloat(document.getElementById('foodCostPerCat')?.value || '15.0'),

        // Colony density
        densityImpactThreshold: parseFloat(document.getElementById('densityImpactThreshold')?.value || '1.2'),
        densityStressRate: parseFloat(document.getElementById('densityStressRate')?.value || '0.15'),
        maxDensityImpact: parseFloat(document.getElementById('maxDensityImpact')?.value || '0.5'),

        // Habitat quality
        baseHabitatQuality: parseFloat(document.getElementById('baseHabitatQuality')?.value || '0.8'),
        urbanizationImpact: parseFloat(document.getElementById('urbanizationImpact')?.value || '0.2'),
        diseaseTransmissionRate: parseFloat(document.getElementById('diseaseTransmissionRate')?.value || '0.1'),

        // Monthly abandonment rate
        monthlyAbandonment: parseFloat(document.getElementById('monthlyAbandonment')?.value || '2.0')
    };

    // Log the collected parameters for debugging
    console.log('Collected parameters:', params);
    
    return params;
}

function updateSliderConstraints() {
    const currentSize = parseInt(document.getElementById('initialColonySize').value);
    const sterilizedSlider = document.getElementById('alreadySterilized');
    sterilizedSlider.max = currentSize;
    if (parseInt(sterilizedSlider.value) > currentSize) {
        sterilizedSlider.value = currentSize;
        document.getElementById('alreadySterilizedValue').textContent = currentSize;
    }
}

// Function to update maximum sterilization rate based on colony size
function updateMaxSterilization() {
    const initialColonySize = parseInt(document.getElementById('initialColonySize').value) || 0;
    const alreadySterilized = parseInt(document.getElementById('alreadySterilized').value) || 0;
    const unsterilizedCount = Math.max(0, initialColonySize - alreadySterilized);
    
    const monthlySterilizationRate = document.getElementById('monthlySterilizationRate');
    monthlySterilizationRate.max = unsterilizedCount;
    
    // Adjust current value if it exceeds new maximum
    if (parseInt(monthlySterilizationRate.value) > unsterilizedCount) {
        monthlySterilizationRate.value = unsterilizedCount;
        document.getElementById('monthlySterilizationRateValue').textContent = unsterilizedCount;
    }
}

// Update sterilized count constraints when colony size changes
function updateSterilizedConstraints() {
    const initialColonySize = parseInt(document.getElementById('initialColonySize').value);
    const alreadySterilizedInput = document.getElementById('alreadySterilized');
    const monthlySterilizationRateInput = document.getElementById('monthlySterilizationRate');
    
    // Update max values
    alreadySterilizedInput.max = initialColonySize;
    monthlySterilizationRateInput.max = initialColonySize - parseInt(alreadySterilizedInput.value);
    
    // Ensure current values don't exceed new max
    if (parseInt(alreadySterilizedInput.value) > initialColonySize) {
        alreadySterilizedInput.value = initialColonySize;
        document.getElementById('alreadySterilizedValue').textContent = initialColonySize;
    }
    
    if (parseInt(monthlySterilizationRateInput.value) > monthlySterilizationRateInput.max) {
        monthlySterilizationRateInput.value = monthlySterilizationRateInput.max;
        document.getElementById('monthlySterilizationRateValue').textContent = monthlySterilizationRateInput.max;
    }
}

// Function to apply environment presets
function applyPreset(preset) {
    const presets = {
        residential: {
            territory: 2000,
            density: 1.2,
            baseFoodCapacity: 0.8,      // Good food availability from residents
            foodScalingFactor: 0.7,     // Decent scaling as residents often increase food with more cats
            environmentalStress: 0.2,    // Moderate stress from human activity
            resourceCompetition: 0.3,    // Moderate competition
            resourceScarcityImpact: 0.3, // Moderate impact
            baseHabitatQuality: 0.7,     // Good shelter options
            urbanizationImpact: 0.4,     // Moderate traffic/urban risks
            diseaseTransmissionRate: 0.15, // Moderate disease risk
            monthlyAbandonment: 3        // Higher abandonment in residential areas
        },
        street: {
            territory: 1000,
            density: 1.5,
            baseFoodCapacity: 0.3,      // Limited food sources
            foodScalingFactor: 0.3,     // Poor scaling with population
            environmentalStress: 0.5,    // High stress from traffic/noise
            resourceCompetition: 0.6,    // High competition for limited resources
            resourceScarcityImpact: 0.6, // High impact from scarcity
            baseHabitatQuality: 0.3,     // Poor shelter options
            urbanizationImpact: 0.8,     // Very high traffic/urban risks
            diseaseTransmissionRate: 0.4, // High disease risk from poor conditions
            monthlyAbandonment: 4        // Highest abandonment rate
        },
        park: {
            territory: 5000,
            density: 0.8,
            baseFoodCapacity: 0.5,      // Moderate natural food sources
            foodScalingFactor: 0.5,     // Moderate scaling
            environmentalStress: 0.2,    // Low stress
            resourceCompetition: 0.3,    // Moderate competition
            resourceScarcityImpact: 0.3, // Moderate impact
            baseHabitatQuality: 0.8,     // Good natural shelter
            urbanizationImpact: 0.2,     // Low traffic risk
            diseaseTransmissionRate: 0.2, // Moderate disease risk from wildlife
            monthlyAbandonment: 2        // Lower abandonment
        },
        industrial: {
            territory: 3000,
            density: 1.0,
            baseFoodCapacity: 0.6,      // Moderate food from workers/dumpsters
            foodScalingFactor: 0.5,     // Moderate scaling
            environmentalStress: 0.4,    // Higher stress from machinery/activity
            resourceCompetition: 0.4,    // Moderate competition
            resourceScarcityImpact: 0.4, // Moderate impact
            baseHabitatQuality: 0.5,     // Moderate shelter in buildings/equipment
            urbanizationImpact: 0.6,     // Higher risks from machinery/vehicles
            diseaseTransmissionRate: 0.3, // Higher disease risk from poor conditions
            monthlyAbandonment: 2        // Lower abandonment in industrial areas
        },
        parking: {
            territory: 1500,
            density: 1.3,
            baseFoodCapacity: 0.4,      // Limited food sources
            foodScalingFactor: 0.4,     // Poor scaling
            environmentalStress: 0.4,    // High stress from vehicles
            resourceCompetition: 0.5,    // High competition
            resourceScarcityImpact: 0.5, // High impact
            baseHabitatQuality: 0.4,     // Poor shelter options
            urbanizationImpact: 0.7,     // Very high traffic risk
            diseaseTransmissionRate: 0.3, // Higher disease risk
            monthlyAbandonment: 2        // Moderate abandonment
        },
        forest: {
            territory: 8000,
            density: 0.5,
            baseFoodCapacity: 0.6,      // Moderate natural food sources
            foodScalingFactor: 0.5,     // Moderate scaling with hunting
            environmentalStress: 0.2,    // Low human-related stress
            resourceCompetition: 0.4,    // Competition with wildlife
            resourceScarcityImpact: 0.4, // Moderate impact
            baseHabitatQuality: 0.9,     // Excellent natural shelter
            urbanizationImpact: 0.1,     // Very low traffic risk
            diseaseTransmissionRate: 0.4, // Higher disease risk from wildlife/exposure
            monthlyAbandonment: 1        // Lowest abandonment rate
        },
        beach: {
            territory: 4000,
            density: 0.7,
            baseFoodCapacity: 0.5,      // Moderate food from tourists/fishing
            foodScalingFactor: 0.5,     // Moderate scaling
            environmentalStress: 0.3,    // Moderate stress from weather/tourists
            resourceCompetition: 0.4,    // Moderate competition
            resourceScarcityImpact: 0.4, // Moderate impact
            baseHabitatQuality: 0.5,     // Limited shelter options
            urbanizationImpact: 0.3,     // Low traffic risk
            diseaseTransmissionRate: 0.3, // Moderate disease risk from exposure
            monthlyAbandonment: 2        // Moderate abandonment from tourists
        },
        custom: {
            territory: 2000,
            density: 1.0,
            baseFoodCapacity: 0.6,
            foodScalingFactor: 0.6,
            environmentalStress: 0.3,
            resourceCompetition: 0.3,
            resourceScarcityImpact: 0.3,
            baseHabitatQuality: 0.6,
            urbanizationImpact: 0.4,
            diseaseTransmissionRate: 0.15,
            monthlyAbandonment: 2
        }
    };

    const presetData = presets[preset];
    if (presetData) {
        // Update all form elements with preset values
        Object.entries(presetData).forEach(([key, value]) => {
            const element = document.getElementById(key);
            if (element) {
                element.value = value;
                // Also update any custom input if it exists
                const customElement = document.getElementById(key + 'Custom');
                if (customElement) {
                    customElement.value = value;
                }
                // Update value display if it exists
                const valueDisplay = document.getElementById(key + 'Value');
                if (valueDisplay) {
                    valueDisplay.textContent = value;
                }
            }
        });

        // Update visual state of buttons
        document.querySelectorAll('.preset-button').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.preset === preset) {
                btn.classList.add('active');
            }
        });

        // Log the applied preset for debugging
        console.log(`Applied ${preset} preset:`, presetData);
        
        // Trigger calculation immediately when preset is changed
        handleCalculate();
    }
}

function initializeInputListeners() {
    // Initial Colony Size
    const initialColonySizeInput = document.getElementById('initialColonySize');
    if (initialColonySizeInput) {
        initialColonySizeInput.addEventListener('input', function() {
            document.getElementById('initialColonySizeValue').textContent = this.value;
            updateSliderConstraints();
            updateMaxSterilization();
        });
    }

    // Already Sterilized
    const alreadySterilizedInput = document.getElementById('alreadySterilized');
    if (alreadySterilizedInput) {
        alreadySterilizedInput.addEventListener('input', function() {
            document.getElementById('alreadySterilizedValue').textContent = this.value;
            updateMaxSterilization();
        });
    }

    // Monthly Sterilization Rate
    const monthlySterilizationRateInput = document.getElementById('monthlySterilizationRate');
    if (monthlySterilizationRateInput) {
        monthlySterilizationRateInput.addEventListener('input', function() {
            document.getElementById('monthlySterilizationRateValue').textContent = this.value;
        });
    }

    // Simulation Length
    const simulationLengthInput = document.getElementById('simulationLength');
    if (simulationLengthInput) {
        simulationLengthInput.addEventListener('input', function() {
            document.getElementById('simulationLengthValue').textContent = this.value;
        });
    }

    // Initialize preset buttons
    const presetButtons = document.querySelectorAll('.preset-button');
    presetButtons.forEach(button => {
        button.addEventListener('click', function() {
            const preset = this.dataset.preset;
            applyPreset(preset);
            
            // Update visual state of buttons
            presetButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Initialize territory size and density threshold inputs
    const territorySize = document.getElementById('territorySize');
    const territorySizeCustom = document.getElementById('territorySizeCustom');
    const densityThreshold = document.getElementById('densityThreshold');
    const densityThresholdCustom = document.getElementById('densityThresholdCustom');

    if (territorySize && territorySizeCustom) {
        territorySize.addEventListener('input', () => {
            territorySizeCustom.value = territorySize.value;
        });

        territorySizeCustom.addEventListener('input', () => {
            territorySize.value = territorySizeCustom.value;
        });
    }

    if (densityThreshold && densityThresholdCustom) {
        densityThreshold.addEventListener('input', () => {
            densityThresholdCustom.value = densityThreshold.value;
        });

        densityThresholdCustom.addEventListener('input', () => {
            densityThreshold.value = densityThresholdCustom.value;
        });
    }

    // Initialize constraints
    updateSliderConstraints();
    updateMaxSterilization();
    updateSterilizedConstraints();
}

// Function to handle the calculation
async function handleCalculate() {
    const calculateButton = document.getElementById('calculateButton');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('resultsSection');
    const placeholderSection = document.getElementById('placeholderSection');

    if (calculateButton) calculateButton.disabled = true;
    if (loadingIndicator) loadingIndicator.classList.remove('hidden');
    if (resultsSection) resultsSection.classList.add('hidden');
    if (placeholderSection) placeholderSection.classList.add('hidden');

    try {
        // Collect all parameters
        const params = {
            params: collectAdvancedParameters(),
            initialColonySize: parseInt(document.getElementById('initialColonySize').value),
            alreadySterilized: parseInt(document.getElementById('alreadySterilized').value),
            monthlySterilizationRate: parseInt(document.getElementById('monthlySterilizationRate').value),
            simulationLength: parseInt(document.getElementById('simulationLength').value),
            sterilizationCost: parseFloat(document.getElementById('sterilizationCost').value),
            monthlyAbandonment: parseInt(document.getElementById('monthlyAbandonment').value || '0')
        };

        console.log("Sending parameters:", params); // Debug log

        // Make the API call
        const response = await fetch(`${baseUrl}/calculatePopulation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Simulation results:", data.result); // Debug log
        
        // Process and display results
        displayResults(data);
        plotPopulationGraph(data);

        // Show results section
        if (resultsSection) resultsSection.classList.remove('hidden');
        if (placeholderSection) placeholderSection.classList.add('hidden');

    } catch (error) {
        console.error('Error during calculation:', error);
        // Show error message to user
        alert('An error occurred during calculation. Please try again.');
    } finally {
        // Hide loading state
        if (calculateButton) calculateButton.disabled = false;
        if (loadingIndicator) loadingIndicator.classList.add('hidden');
    }
}

function displayResults(data) {
    // Update statistics
    const updateElement = (id, value) => {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    };

    updateElement('finalPopulation', Math.round(data.result.finalPopulation));
    updateElement('populationChange', (data.result.populationChange >= 0 ? '+' : '') + Math.round(data.result.populationChange));
    updateElement('sterilizationRate', Math.round(data.result.sterilizationRate * 100) + '%');
    updateElement('totalCost', '$' + Math.round(data.result.totalCost).toLocaleString());

    // Update mortality statistics
    updateElement('totalDeaths', Math.round(data.result.totalDeaths));
    updateElement('kittenDeaths', Math.round(data.result.kittenDeaths));
    updateElement('adultDeaths', Math.round(data.result.adultDeaths));
    updateElement('mortalityRate', (Math.round(data.result.mortalityRate * 1000) / 10) + '%');

    // Update deaths by cause
    updateElement('naturalDeaths', Math.round(data.result.naturalDeaths));
    updateElement('urbanDeaths', Math.round(data.result.urbanDeaths));
    updateElement('diseaseDeaths', Math.round(data.result.diseaseDeaths));
}

function plotPopulationGraph(data) {
    const ctx = document.getElementById('populationChart')?.getContext('2d');
    if (!ctx) {
        console.error('Could not find population chart canvas');
        return;
    }
    
    // Debug log the data
    console.log("Graph data:", {
        months: data.result.months,
        total: data.result.totalPopulation,
        sterilized: data.result.sterilizedPopulation
    });
    
    // Destroy existing chart if it exists
    if (window.populationChart instanceof Chart) {
        window.populationChart.destroy();
    }

    // Prepare data for the chart
    const months = data.result.months || Array.from({length: data.result.totalPopulation?.length || 0}, (_, i) => i);
    const totalPopulation = data.result.totalPopulation || [];
    const sterilizedPopulation = data.result.sterilizedPopulation || [];

    // Create new chart
    window.populationChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Total Population',
                    data: totalPopulation,
                    borderColor: '#60A5FA',
                    backgroundColor: '#60A5FA',
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Sterilized',
                    data: sterilizedPopulation,
                    borderColor: '#34D399',
                    backgroundColor: '#34D399',
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Months',
                        color: '#E5E7EB'
                    },
                    grid: {
                        color: '#374151'
                    },
                    ticks: {
                        color: '#E5E7EB'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Population',
                        color: '#E5E7EB'
                    },
                    grid: {
                        color: '#374151'
                    },
                    ticks: {
                        color: '#E5E7EB'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#E5E7EB'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

// Set up event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize input event listeners
    initializeInputListeners();
    
    // Apply residential preset by default
    applyPreset('residential');
    
    // Add event listeners to all preset buttons
    document.querySelectorAll('.preset-button').forEach(button => {
        button.addEventListener('click', function() {
            const preset = this.dataset.preset;
            applyPreset(preset);
        });
    });
    
    // Add event listeners to all parameter inputs to handle custom values
    document.querySelectorAll('input[type="range"], input[type="number"]').forEach(input => {
        input.addEventListener('change', function() {
            // Remove active state from all preset buttons when user modifies values
            document.querySelectorAll('.preset-button').forEach(btn => {
                btn.classList.remove('active');
            });
        });
    });

    // Initialize tooltips for preset buttons
    const presetDescriptions = {
        residential: "Urban residential areas with moderate food and shelter from residents",
        street: "Urban streets and alleys with limited resources and high risks",
        park: "Public parks with natural shelter and moderate food availability",
        industrial: "Industrial areas with regular feeding stations but urban hazards",
        parking: "Parking lots with limited shelter and moderate urban risks",
        forest: "Natural areas with excellent shelter but limited food",
        beach: "Coastal areas with moderate resources and weather impacts"
    };

    document.querySelectorAll('.preset-button').forEach(button => {
        const preset = button.dataset.preset;
        if (presetDescriptions[preset]) {
            button.title = presetDescriptions[preset];
        }
    });

    // Set up preset buttons
    document.querySelectorAll('.preset-button').forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            document.querySelectorAll('.preset-button').forEach(btn => {
                btn.classList.remove('active');
            });
            // Add active class to clicked button
            this.classList.add('active');
            // Apply the preset
            applyPreset(this.dataset.preset);
        });
    });

    // Set up calculate button
    const calculateButton = document.getElementById('calculateButton');
    if (calculateButton) {
        calculateButton.addEventListener('click', handleCalculate);
    }

    // Set up advanced mode toggle
    const advancedModeToggle = document.getElementById('advancedMode');
    const advancedSection = document.getElementById('advancedSection');
    const dashboardContainer = document.getElementById('dashboardContainer');
    
    if (advancedModeToggle && advancedSection && dashboardContainer) {
        advancedModeToggle.addEventListener('change', function() {
            if (this.checked) {
                advancedSection.classList.add('active');
                dashboardContainer.classList.add('advanced-mode');
            } else {
                advancedSection.classList.remove('active');
                dashboardContainer.classList.remove('advanced-mode');
            }
        });
    }

    // Show initial state
    const resultsSection = document.getElementById('resultsSection');
    const placeholderSection = document.getElementById('placeholderSection');
    
    if (resultsSection) resultsSection.classList.add('hidden');
    if (placeholderSection) placeholderSection.classList.remove('hidden');
});
