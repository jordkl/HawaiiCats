// Define calculator version
const CALCULATOR_VERSION = '1.0.0';
window.CALCULATOR_VERSION = CALCULATOR_VERSION;  // Make version globally available

// Determine the base URL based on the current environment
const isLocalhost = ['localhost', '127.0.0.1', '192.168.1.169'].includes(window.location.hostname);
const baseUrl = isLocalhost ? `http://${window.location.host}` : 'https://hawaiicats.org';

// Remove duplicate toggleAdvancedMode function since it's already in script.js

function updateSliderConstraints() {
    const currentSize = parseInt(document.getElementById('currentSize').value);
    const sterilizedSlider = document.getElementById('sterilizedCount');
    sterilizedSlider.max = currentSize;
    if (parseInt(sterilizedSlider.value) > currentSize) {
        sterilizedSlider.value = currentSize;
        document.getElementById('sterilizedCountValue').textContent = currentSize;
    }
}

// Function to update maximum sterilization rate based on colony size
function updateMaxSterilization() {
    const currentSize = parseInt(document.getElementById('currentSize').value) || 0;
    const sterilizedCount = parseInt(document.getElementById('sterilizedCount').value) || 0;
    const unsterilizedCount = Math.max(0, currentSize - sterilizedCount);
    
    const monthlysterilization = document.getElementById('monthlysterilization');
    monthlysterilization.max = unsterilizedCount;
    
    // Adjust current value if it exceeds new maximum
    if (parseInt(monthlysterilization.value) > unsterilizedCount) {
        monthlysterilization.value = unsterilizedCount;
        document.getElementById('monthlysterilizationValue').textContent = unsterilizedCount;
    }
}

// Update sterilized count constraints when colony size changes
function updateSterilizedConstraints() {
    const colonySize = parseInt(document.getElementById('currentSize').value);
    const sterilizedInput = document.getElementById('sterilizedCount');
    const monthlyInput = document.getElementById('monthlysterilization');
    
    // Update max values
    sterilizedInput.max = colonySize;
    monthlyInput.max = colonySize - parseInt(sterilizedInput.value);
    
    // Ensure current values don't exceed new max
    if (parseInt(sterilizedInput.value) > colonySize) {
        sterilizedInput.value = colonySize;
        document.getElementById('sterilizedCountValue').textContent = colonySize;
    }
    
    if (parseInt(monthlyInput.value) > monthlyInput.max) {
        monthlyInput.value = monthlyInput.max;
        document.getElementById('monthlysterilizationValue').textContent = monthlyInput.max;
    }
}

function initializeInputListeners() {
    // Add event listener for Monte Carlo toggle
    const monteCarloToggle = document.getElementById('useMonteCarlo');
    const monteCarloParams = document.getElementById('monteCarloParams');
    if (monteCarloToggle && monteCarloParams) {
        monteCarloToggle.addEventListener('change', function() {
            monteCarloParams.style.display = this.checked ? 'block' : 'none';
        });
    }

    // Number of Simulations slider
    const numSimulationsInput = document.getElementById('numSimulations');
    const numSimulationsValue = document.getElementById('numSimulationsValue');
    if (numSimulationsInput && numSimulationsValue) {
        numSimulationsInput.addEventListener('input', () => {
            numSimulationsValue.textContent = numSimulationsInput.value;
        });
    }

    // Variation Coefficient slider
    const variationCoefficientInput = document.getElementById('variationCoefficient');
    const variationCoefficientValue = document.getElementById('variationCoefficientValue');
    if (variationCoefficientInput && variationCoefficientValue) {
        variationCoefficientInput.addEventListener('input', () => {
            variationCoefficientValue.textContent = variationCoefficientInput.value;
        });
    }

    // Initial Colony Size
    const currentSizeInput = document.getElementById('currentSize');
    if (currentSizeInput) {
        currentSizeInput.addEventListener('input', function() {
            document.getElementById('currentSizeValue').textContent = this.value;
            updateSliderConstraints();
            updateMaxSterilization();
        });
    }

    // Already Sterilized
    const sterilizedCountInput = document.getElementById('sterilizedCount');
    if (sterilizedCountInput) {
        sterilizedCountInput.addEventListener('input', function() {
            document.getElementById('sterilizedCountValue').textContent = this.value;
            updateMaxSterilization();
        });
    }

    // Monthly Sterilization Rate
    const monthlysterilizationInput = document.getElementById('monthlysterilization');
    if (monthlysterilizationInput) {
        monthlysterilizationInput.addEventListener('input', function() {
            document.getElementById('monthlysterilizationValue').textContent = this.value;
        });
    }

    // Simulation Length
    const monthsInput = document.getElementById('months');
    if (monthsInput) {
        monthsInput.addEventListener('input', function() {
            document.getElementById('monthsValue').textContent = this.value;
        });
    }

    // Advanced Mode Toggle
    const advancedModeToggle = document.getElementById('advancedMode');
    if (advancedModeToggle) {
        advancedModeToggle.addEventListener('change', function() {
            const advancedSection = document.getElementById('advancedSection');
            const dashboardContainer = document.getElementById('dashboardContainer');
            const sidebar = document.getElementById('sidebar');
            
            if (this.checked) {
                advancedSection.classList.add('active');
                dashboardContainer.classList.add('advanced-mode');
                sidebar.classList.add('advanced-mode');
            } else {
                advancedSection.classList.remove('active');
                dashboardContainer.classList.remove('advanced-mode');
                sidebar.classList.remove('advanced-mode');
            }
        });
    }

    // Colony Size
    const colonySizeInput = document.getElementById('currentSize');
    if (colonySizeInput) {
        colonySizeInput.addEventListener('input', updateSterilizedConstraints);
    }

    // Environment presets configuration
    const environmentPresets = {
        residential: {
            territory: 2000,
            density: 1.2,
            description: "Urban residential areas with moderate human activity"
        },
        street: {
            territory: 1000,
            density: 1.5,
            description: "Streets and alleys with high human activity"
        },
        park: {
            territory: 5000,
            density: 0.8,
            description: "Public parks with scattered resources"
        },
        industrial: {
            territory: 3000,
            density: 0.6,
            description: "Industrial areas with limited resources"
        },
        parking: {
            territory: 1500,
            density: 0.7,
            description: "Parking lots with moderate human activity"
        },
        forest: {
            territory: 8000,
            density: 0.4,
            description: "Natural areas with diverse wildlife"
        },
        beach: {
            territory: 4000,
            density: 0.5,
            description: "Coastal areas with variable resources"
        },
        custom: {
            territory: 1000,
            density: 1.2,
            description: "Custom environment settings"
        }
    };

    // Function to handle preset button clicks
    function handlePresetClick(preset) {
        // Remove active class from all buttons
        document.querySelectorAll('.preset-button').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Add active class to clicked button
        const clickedButton = document.querySelector(`.preset-button[data-preset="${preset}"]`);
        if (clickedButton) {
            clickedButton.classList.add('active');
        }
        
        // Update territory and density values
        const presetData = environmentPresets[preset];
        if (presetData) {
            document.getElementById('territory_size').value = presetData.territory;
            document.getElementById('territory_size_custom').value = presetData.territory;
            document.getElementById('density_threshold').value = presetData.density;
            document.getElementById('density_threshold_custom').value = presetData.density;
            document.getElementById('preset_info').textContent = presetData.description;
        }
    }

    // Initialize preset buttons
    function initializePresetButtons() {
        document.querySelectorAll('.preset-button').forEach(button => {
            button.addEventListener('click', () => {
                const preset = button.dataset.preset;
                handlePresetClick(preset);
            });
        });
        
        // Set initial active state to custom
        handlePresetClick('custom');
    }

    initializePresetButtons();

    // Update custom inputs when select values change
    document.getElementById('territory_size').addEventListener('change', function(e) {
        document.getElementById('territory_size_custom').value = e.target.value;
    });

    document.getElementById('density_threshold').addEventListener('change', function(e) {
        document.getElementById('density_threshold_custom').value = e.target.value;
    });

    // Update select inputs when custom values change
    document.getElementById('territory_size_custom').addEventListener('input', function(e) {
        const select = document.getElementById('territory_size');
        select.value = Array.from(select.options).find(opt => opt.value === e.target.value)?.value || '';
    });

    document.getElementById('density_threshold_custom').addEventListener('input', function(e) {
        const select = document.getElementById('density_threshold');
        select.value = Array.from(select.options).find(opt => opt.value === e.target.value)?.value || '';
    });

    // Initialize the constraints based on initial values
    updateSliderConstraints();
    updateMaxSterilization();
    updateSterilizedConstraints();
}

async function handleCalculate() {
    try {
        // Disable calculate button to prevent double submission
        const calculateButton = document.getElementById('calculateButton');
        if (calculateButton) {
            calculateButton.disabled = true;
            calculateButton.textContent = 'Calculating...';
        }

        const isAdvanced = document.getElementById('advancedMode')?.checked || false;
        const useMonteCarlo = document.getElementById('useMonteCarlo')?.checked || false;
        
        // Show Monte Carlo loading indicator if Monte Carlo is enabled
        const monteCarloLoading = document.getElementById('monteCarloLoading');
        if (useMonteCarlo && monteCarloLoading) {
            monteCarloLoading.classList.add('active');
        }
        
        // Input validation with specific error messages
        const validateInput = (value, fieldName, min = 0, max = Infinity) => {
            const num = parseFloat(value);
            if (isNaN(num)) throw new Error(`${fieldName} must be a valid number`);
            if (num < min) throw new Error(`${fieldName} must be at least ${min}`);
            if (num > max) throw new Error(`${fieldName} must be less than ${max}`);
            return num;
        };

        // Collect and validate basic parameters
        const data = {
            current_size: validateInput(document.getElementById('currentSize')?.value, 'Colony Size', 1, 1000),
            sterilized_count: validateInput(document.getElementById('sterilizedCount')?.value, 'Sterilized Count', 0),
            monthly_sterilization: validateInput(document.getElementById('monthlysterilization')?.value, 'Monthly Sterilization Rate', 0),
            sterilization_cost: validateInput(document.getElementById('sterilizationCost')?.value, 'Sterilization Cost', 0),
            months: validateInput(document.getElementById('months')?.value, 'Months', 1, 120),
            use_monte_carlo: useMonteCarlo,
            monthly_abandonment: validateInput(document.getElementById('monthlyAbandonment')?.value || '2', 'Monthly Abandonment', 0, 50),
        };

        // Add Monte Carlo specific parameters if enabled
        if (document.getElementById('monteCarloParams').style.display !== 'none') {
            data.use_monte_carlo = true;
            data.num_simulations = validateInput(document.getElementById('numSimulations')?.value, 'Number of Simulations', 100, 1000);
            data.variation_coefficient = validateInput(document.getElementById('variationCoefficient')?.value, 'Variation Coefficient', 0, 1);
        } else {
            data.num_simulations = 1;
            data.variation_coefficient = 0;
        }

        // Validate dependencies between parameters
        if (data.sterilized_count > data.current_size) {
            throw new Error('Sterilized count cannot exceed colony size');
        }

        // Update max sterilization before collecting data
        updateMaxSterilization();
        
        // Get advanced parameters if in advanced mode
        if (isAdvanced) {
            data.params = collectAdvancedParameters();
        }

        console.log('Sending data to server:', data);

        const response = await fetch(`${baseUrl}/calculate_population`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            timeout: 30000  // 30 second timeout
        });

        if (!response.ok) {
            let errorMessage = `Server error (${response.status})`;
            try {
                const errorData = await response.text();
                if (errorData.startsWith('{')) {
                    const jsonError = JSON.parse(errorData);
                    errorMessage = jsonError.error || errorMessage;
                } else if (errorData.includes('<')) {
                    errorMessage = `Server error (${response.status}). Please try again with fewer simulations or a shorter time period.`;
                }
            } catch (e) {
                console.error('Error parsing error response:', e);
            }
            throw new Error(errorMessage);
        }

        let result;
        try {
            const responseText = await response.text();
            result = JSON.parse(responseText);
        } catch (e) {
            console.error('Error parsing response:', e);
            throw new Error('Invalid response from server');
        }

        if (!result) {
            throw new Error('Empty response from server');
        }

        console.log('Received result from server:', result);
        
        // Ensure we have the correct data structure
        if (useMonteCarlo) {
            if (!result.result || !result.result.confidence_interval || !result.result.standard_deviation) {
                console.warn('Monte Carlo simulation was requested but data is missing');
                throw new Error('Monte Carlo simulation failed. Please try again with fewer simulations.');
            }
            
            // Validate the Monte Carlo data structure
            const monteCarloResult = result.result;
            if (!monteCarloResult.final_population || !monteCarloResult.monthly_populations || 
                !monteCarloResult.monthly_sterilized || !monteCarloResult.monthly_kittens) {
                console.warn('Monte Carlo data is incomplete:', monteCarloResult);
                throw new Error('Monte Carlo simulation returned incomplete data. Please try again.');
            }
        }

        await displayResults(result.result);
        
    } catch (error) {
        console.error('Error:', error);
        // Show error in UI with more specific guidance
        const errorDiv = document.createElement('div');
        errorDiv.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4';
        errorDiv.innerHTML = `
            <strong class="font-bold">Error:</strong>
            <span class="block sm:inline">${error.message}</span>
            ${error.message.includes('server') ? 
                '<p class="mt-2 text-sm">Please check your internet connection and try again. If the problem persists, try reducing the simulation parameters.</p>' 
                : ''}
        `;
        
        // Insert error message at the top of the main content
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.insertBefore(errorDiv, mainContent.firstChild);
            // Remove error message after 8 seconds
            setTimeout(() => errorDiv.remove(), 8000);
        } else {
            alert(error.message);
        }
    } finally {
        // Re-enable calculate button and hide loading indicator
        const calculateButton = document.getElementById('calculateButton');
        const monteCarloLoading = document.getElementById('monteCarloLoading');
        
        if (calculateButton) {
            calculateButton.disabled = false;
            calculateButton.textContent = 'Calculate';
        }
        
        if (monteCarloLoading) {
            monteCarloLoading.classList.remove('active');
        }
    }
}

function collectAdvancedParameters() {
    const params = {};
    
    // Helper function to safely get slider value
    const getSliderValue = (id) => {
        const element = document.getElementById(id);
        return element ? parseFloat(element.value) : null;
    };

    // Mortality Risk Factors - with density-dependent scaling
    params.urban_risk = getSliderValue('urbanRisk') || 0.1;  // Base urban risk
    params.disease_risk = getSliderValue('diseaseRisk') || 0.15;  // Base disease risk
    params.natural_risk = getSliderValue('naturalRisk') || 0.1;  // Base natural risk
    params.density_mortality_factor = 0.5;  // How much mortality increases with density
    params.mortality_threshold = 30;  // Colony size where density effects start increasing

    // Environmental Factors - now using slider values with research-based defaults
    params.water_availability = getSliderValue('waterAvailability') || 0.7;  // Adjusted based on Hawaii climate
    params.shelter_quality = getSliderValue('shelterQuality') || 0.7;
    params.caretaker_support = getSliderValue('caretakerSupport') || 1.0;  // Default to full support
    params.feeding_consistency = getSliderValue('feedingConsistency') || 0.8;
    params.territory_size = getSliderValue('territorySize') || 500;  // Adjusted based on urban environment
    params.base_food_capacity = getSliderValue('baseFoodCapacity') || 0.9;
    params.food_scaling_factor = getSliderValue('foodScalingFactor') || 0.8;

    // Survival Rates - adjusted for density dependence
    params.kitten_survival_rate = getSliderValue('kittenSurvivalRate') || 0.6;  // Base survival rate
    params.adult_survival_rate = getSliderValue('adultSurvivalRate') || 0.7;  // Base survival rate
    params.survival_density_factor = 0.3;  // How much survival decreases with density

    // Breeding Parameters - adjusted for seasonal patterns
    params.breeding_rate = getSliderValue('breedingRate') || 0.7;  // More conservative estimate
    params.kittens_per_litter = getSliderValue('kittensPerLitter') || 4.0;
    params.litters_per_year = getSliderValue('littersPerYear') || 2.0;
    params.seasonal_breeding_amplitude = getSliderValue('seasonalBreedingAmplitude') || 0.3;  // New parameter
    params.peak_breeding_month = getSliderValue('peakBreedingMonth') || 3;  // March is peak breeding month
    params.female_ratio = 0.5;  // Biological constant
    params.kitten_maturity_months = 6.0;  // Adjusted from 5 to 6 months
    params.abandoned_sterilized_ratio = getSliderValue('abandonedSterilizedRatio') || 0.2;  // New parameter from test data
    params.gestation_months = 2;  // Fixed biological constant

    // Cost Parameters
    params.sterilization_cost = getSliderValue('sterilizationCost') || 50.0;  // Default cost of $50 per sterilization

    console.log('Advanced parameters:', params);
    return params;
}

async function calculatePopulation(data) {
    try {
        const endpoint = '/calculate_population';
        const timestamp = new Date().getTime();
        const url = `${baseUrl}${endpoint}?_=${timestamp}`;
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        
        const contentType = response.headers.get("content-type");
        
        if (!response.ok) {
            if (response.status === 500) {
                throw new Error('Server error: The log download feature is currently unavailable. Please try again later.');
            }
            const responseContent = await response.text();
            throw new Error(responseContent.error || `Server returned ${response.status}: ${response.statusText}`);
        }
        
        // Handle successful response
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = downloadUrl;
        
        // Get filename from Content-Disposition header or use default
        const disposition = response.headers.get('content-disposition');
        const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        const matches = filenameRegex.exec(disposition);
        const filename = matches ? matches[1].replace(/['"]/g, '') : 'simulation_results.csv';
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
        
    } catch (error) {
        console.error('Error downloading logs:', error);
        alert('Error downloading logs: ' + error.message);
    }
}

async function displayResults(data) {
    try {
        console.log('Starting displayResults with data:', JSON.stringify(data, null, 2));
        
        // Extract the actual result data, handling both direct results and nested results
        const resultData = data.result?.result || data.result || data;
        console.log('Extracted result data:', JSON.stringify(resultData, null, 2));
        
        // Hide placeholder and show results section
        document.getElementById('placeholderSection').classList.add('hidden');
        document.getElementById('resultsSection').classList.remove('hidden');
        
        if (!resultData.monthly_populations) {
            console.error('No monthly data found in response');
            alert('Invalid response format from server: missing monthly data');
            return;
        }

        // Helper function to safely update element content with logging
        const safeSetContent = (elementId, content, isHtml = false) => {
            const element = document.getElementById(elementId);
            if (element) {
                if (isHtml) {
                    element.innerHTML = content;
                } else {
                    element.textContent = content;
                }
                console.log(`Updated ${elementId} with value:`, content);
            } else {
                console.error(`Element with id ${elementId} not found in DOM`);
            }
        };

        // Helper function to update Monte Carlo CI elements
        const updateConfidenceIntervals = (metric, data) => {
            const lowerElement = document.getElementById(`${metric}_lower`);
            const upperElement = document.getElementById(`${metric}_upper`);
            
            if (!lowerElement || !upperElement) {
                console.error(`CI elements not found for metric: ${metric}`);
                return;
            }

            if (data && typeof data.ci_lower !== 'undefined' && typeof data.ci_upper !== 'undefined') {
                const lowerValue = Math.round(data.ci_lower);
                const upperValue = Math.round(data.ci_upper);
                lowerElement.textContent = lowerValue;
                upperElement.textContent = upperValue;
                lowerElement.classList.remove('hidden');
                upperElement.classList.remove('hidden');
                console.log(`Updated CI for ${metric}: ${lowerValue} - ${upperValue}`);
            } else {
                lowerElement.classList.add('hidden');
                upperElement.classList.add('hidden');
                console.log(`Hiding CI for ${metric} due to missing data`);
            }
        };

        // Show/hide all Monte Carlo CI elements
        const toggleMonteCarloElements = (show) => {
            const elements = document.querySelectorAll('.monte-carlo-ci');
            elements.forEach(el => {
                if (show) {
                    el.classList.remove('hidden');
                } else {
                    el.classList.add('hidden');
                }
            });
            console.log(`${show ? 'Showing' : 'Hiding'} Monte Carlo elements`);
        };

        // Ensure results section is visible
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.classList.remove('hidden');
            console.log('Results section is now visible');
        } else {
            console.error('Results section not found in DOM');
            return;
        }

        // Hide initial state if it exists
        const initialState = document.getElementById('initialState');
        if (initialState) {
            initialState.classList.add('hidden');
        }

        // Check if we have Monte Carlo data
        const hasMonteCarloData = resultData.monte_carlo_data && resultData.monte_carlo_summary;
        toggleMonteCarloElements(hasMonteCarloData);

        // Helper function to safely parse and format numbers
        const formatNumber = (value, isPrice = false) => {
            const num = parseFloat(value);
            if (isNaN(num)) return '0';
            if (isPrice) {
                return `$${num.toFixed(2)}`;
            }
            return Math.round(num).toString();
        };

        // Update basic statistics
        safeSetContent('finalPopulation', formatNumber(resultData.final_population));
        if (hasMonteCarloData && resultData.monte_carlo_summary) {
            const popData = resultData.monte_carlo_summary.population;
            if (popData) {
                updateConfidenceIntervals('finalPopulation', {
                    ci_lower: popData.lower,
                    ci_upper: popData.upper
                });
                console.log('Updated population confidence intervals:', {
                    lower: formatNumber(popData.lower),
                    upper: formatNumber(popData.upper)
                });
            }
        }

        const populationChange = resultData.final_population - resultData.monthly_populations[0];
        safeSetContent('populationChange', `${populationChange >= 0 ? '+' : ''}${populationChange}`);
        if (hasMonteCarloData && resultData.monte_carlo_summary) {
            const changeData = resultData.monte_carlo_summary.population_change;
            if (changeData) {
                updateConfidenceIntervals('populationChange', {
                    ci_lower: changeData.lower,
                    ci_upper: changeData.upper
                });
            }
        }
        
        const sterilizationRate = ((resultData.final_sterilized / resultData.final_population) * 100).toFixed(1);
        safeSetContent('sterilizationRate', `${sterilizationRate}%`);
        if (hasMonteCarloData && resultData.monte_carlo_summary) {
            const sterilizationData = resultData.monte_carlo_summary.sterilization_rate;
            if (sterilizationData) {
                updateConfidenceIntervals('sterilizationRate', {
                    ci_lower: sterilizationData.lower,
                    ci_upper: sterilizationData.upper
                });
            }
        }

        // Calculate and display total cost
        let totalCost = 0;
        if (resultData.monthly_costs) {
            // Sum up all monthly costs
            totalCost = resultData.monthly_costs.reduce((sum, cost) => sum + (parseFloat(cost) || 0), 0);
        } else if (resultData.total_cost) {
            // Use total cost if provided directly
            totalCost = resultData.total_cost;
        }
        safeSetContent('totalCost', formatNumber(totalCost, true));

        // Handle Monte Carlo data for cost if available
        if (hasMonteCarloData && resultData.monte_carlo_summary && resultData.monte_carlo_summary.cost) {
            const costData = resultData.monte_carlo_summary.cost;
            updateConfidenceIntervals('totalCost', {
                ci_lower: costData.lower,
                ci_upper: costData.upper
            });
            console.log('Updated cost confidence intervals:', {
                lower: formatNumber(costData.lower, true),
                upper: formatNumber(costData.upper, true)
            });
        }

        // Initialize mortality statistics
        let totalDeaths = 0, kittenDeaths = 0, adultDeaths = 0;
        let naturalDeaths = 0, urbanDeaths = 0, diseaseDeaths = 0;

        console.log('Processing mortality data...');
        
        if (hasMonteCarloData) {
            // Use Monte Carlo mortality data
            const mortalityData = resultData.monte_carlo_data.mortality;
            console.log('Using Monte Carlo mortality data:', mortalityData);
            
            totalDeaths = Math.round(mortalityData.total.mean) || 0;
            kittenDeaths = Math.round(mortalityData.kittens.mean) || 0;
            adultDeaths = Math.round(mortalityData.adults.mean) || 0;
            naturalDeaths = Math.round(mortalityData.by_cause.natural.mean) || 0;
            urbanDeaths = Math.round(mortalityData.by_cause.urban.mean) || 0;
            diseaseDeaths = Math.round(mortalityData.by_cause.disease.mean) || 0;

            // Update confidence intervals for mortality statistics
            updateConfidenceIntervals('totalDeaths', mortalityData.total);
            updateConfidenceIntervals('kittenDeaths', mortalityData.kittens);
            updateConfidenceIntervals('adultDeaths', mortalityData.adults);
            updateConfidenceIntervals('naturalDeaths', mortalityData.by_cause.natural);
            updateConfidenceIntervals('urbanDeaths', mortalityData.by_cause.urban);
            updateConfidenceIntervals('diseaseDeaths', mortalityData.by_cause.disease);
        } else {
            // Use regular simulation mortality data
            console.log('Using regular simulation mortality data');
            
            // Safely sum up deaths with null checks
            const sumArray = (arr) => (arr || []).reduce((a, b) => a + (b || 0), 0);
            
            naturalDeaths = sumArray(resultData.monthly_deaths_natural);
            urbanDeaths = sumArray(resultData.monthly_deaths_urban);
            diseaseDeaths = sumArray(resultData.monthly_deaths_disease);
            totalDeaths = naturalDeaths + urbanDeaths + diseaseDeaths;
            
            kittenDeaths = sumArray(resultData.monthly_deaths_kittens);
            adultDeaths = sumArray(resultData.monthly_deaths_adults);
        }

        console.log('Final mortality statistics:', {
            totalDeaths,
            kittenDeaths,
            adultDeaths,
            naturalDeaths,
            urbanDeaths,
            diseaseDeaths
        });

        // Update mortality statistics in the UI
        safeSetContent('totalDeaths', totalDeaths);
        safeSetContent('kittenDeaths', kittenDeaths);
        safeSetContent('adultDeaths', adultDeaths);
        
        // Calculate and update mortality rate
        const avgPopulation = resultData.monthly_populations.reduce((a, b) => a + b, 0) / resultData.monthly_populations.length;
        const mortalityRate = avgPopulation > 0 ? ((totalDeaths / avgPopulation) * 100).toFixed(1) : '0.0';
        safeSetContent('mortalityRate', `${mortalityRate}%`);
        
        // Update deaths by cause
        safeSetContent('naturalDeaths', naturalDeaths);
        safeSetContent('urbanDeaths', urbanDeaths);
        safeSetContent('diseaseDeaths', diseaseDeaths);

        await plotPopulationGraph(resultData);
        
        console.log('displayResults completed successfully');
    } catch (error) {
        console.error('Error in displayResults:', error);
        console.error('Error stack:', error.stack);
        alert('An error occurred while displaying results. Check the console for details.');
    }
}

async function plotPopulationGraph(data) {
    const canvas = document.getElementById('populationGraph');
    if (!canvas) {
        console.error('Population graph canvas element not found');
        return;
    }

    const ctx = canvas.getContext('2d');
    
    // Clear any existing chart
    if (window.populationChart) {
        window.populationChart.destroy();
    }

    // Extract data
    const resultData = data.result || data;
    if (!resultData || !resultData.monthly_populations) {
        console.error('Invalid data format for population graph:', resultData);
        return;
    }

    const months = Array.from({length: resultData.monthly_populations.length}, (_, i) => i);
    
    let datasets = [
        {
            label: 'Total Population',
            data: resultData.monthly_populations,
            borderColor: 'rgb(79, 70, 229)', // Indigo
            backgroundColor: 'rgba(79, 70, 229, 0.1)',
            borderWidth: 2,
            tension: 0.4,
            fill: false,
            order: 1
        },
        {
            label: 'Sterilized',
            data: resultData.monthly_sterilized,
            borderColor: 'rgb(16, 185, 129)', // Green
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 2,
            tension: 0.4,
            fill: false,
            order: 2
        },
        {
            label: 'Unsterilized',
            data: resultData.monthly_reproductive,
            borderColor: 'rgb(239, 68, 68)', // Red
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            borderWidth: 2,
            tension: 0.4,
            fill: false,
            order: 3
        },
        {
            label: 'Kittens',
            data: resultData.monthly_kittens,
            borderColor: 'rgb(245, 158, 11)', // Amber
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            borderWidth: 2,
            tension: 0.4,
            fill: false,
            order: 4
        }
    ];

    // Add confidence intervals if Monte Carlo data is available
    if (resultData.confidence_interval) {
        const [lowerBound, upperBound] = resultData.confidence_interval;
        const basePopulation = resultData.monthly_populations[0];
        const finalPopulation = resultData.monthly_populations[resultData.monthly_populations.length - 1];
        const totalChange = finalPopulation - basePopulation;
        
        // Calculate lower and upper bounds for each month
        const lowerBounds = resultData.monthly_populations.map((pop, i) => {
            if (i === 0) return pop; // First month is always actual
            const progress = (pop - basePopulation) / totalChange;
            const lowerChange = (lowerBound - basePopulation) * progress;
            return Math.max(basePopulation + lowerChange, 0);
        });
        
        const upperBounds = resultData.monthly_populations.map((pop, i) => {
            if (i === 0) return pop; // First month is always actual
            const progress = (pop - basePopulation) / totalChange;
            const upperChange = (upperBound - basePopulation) * progress;
            return basePopulation + upperChange;
        });

        // Add confidence interval area
        datasets.push({
            label: 'Population Range',
            data: upperBounds,
            borderColor: 'rgba(79, 70, 229, 0.3)',
            backgroundColor: 'rgba(79, 70, 229, 0.2)',
            fill: '+1',
            pointRadius: 0,
            order: 0
        });

        datasets.push({
            label: '_hidden',  // Hide this from legend
            data: lowerBounds,
            borderColor: 'rgba(79, 70, 229, 0.3)',
            backgroundColor: 'rgba(79, 70, 229, 0.2)',
            fill: false,
            pointRadius: 0,
            order: 0
        });
    }

    window.populationChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    labels: {
                        filter: function(legendItem, data) {
                            // Don't show legend items that start with '_'
                            return !legendItem.text.startsWith('_');
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label.startsWith('_')) return null;
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += Math.round(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Months'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Population'
                    },
                    min: 0
                }
            }
        }
    });
}

async function downloadLogs() {
    try {
        const timestamp = new Date().getTime();
        const url = `${baseUrl}/download_logs?_=${timestamp}`;
        
        const response = await fetch(url, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json, text/plain, */*'
            }
        });
        
        const contentType = response.headers.get('content-type');
        
        if (!response.ok) {
            if (response.status === 500) {
                throw new Error('Server error: The log download feature is currently unavailable. Please try again later.');
            }
            const responseContent = await response.text();
            throw new Error(responseContent.error || `Server returned ${response.status}: ${response.statusText}`);
        }
        
        // Handle successful response
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = downloadUrl;
        
        // Get filename from Content-Disposition header or use default
        const disposition = response.headers.get('content-disposition');
        const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        const matches = filenameRegex.exec(disposition);
        const filename = matches ? matches[1].replace(/['"]/g, '') : 'simulation_results.csv';
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
        
    } catch (error) {
        console.error('Error downloading logs:', error);
        alert('Error downloading logs: ' + error.message);
    }
}

async function clearLogs() {
    try {
        const timestamp = new Date().getTime();
        const url = `${baseUrl}/clear_logs?_=${timestamp}`;
        
        const response = await fetch(url, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `Server returned ${response.status}: ${response.statusText}`);
        }
        
        alert(data.message || 'Logs cleared successfully');
        
    } catch (error) {
        console.error('Error clearing logs:', error);
        alert('Error clearing logs: ' + error.message);
    }
}

async function runParameterTests() {
    const testBtn = document.getElementById('testParametersBtn');
    if (!testBtn) {
        console.error('Test parameters button not found');
        return;
    }

    const originalText = testBtn.textContent;
    testBtn.disabled = true;
    testBtn.textContent = 'Running Tests...';

    try {
        // Base configuration for Hawaiʻi
        const baseConfig = {
            months: 24,
            current_size: 50,
            sterilized_count: 0,
            monthly_sterilization: 0,
            use_monte_carlo: true,
            monte_carlo_runs: 50,
            params: {
                breeding_rate: 0.85,
                kittens_per_litter: 4,
                litters_per_year: 2.5,
                female_ratio: 0.5,
                kitten_survival_rate: 0.75,
                adult_survival_rate: 0.90,
                kitten_maturity_months: 6,
                seasonal_breeding_amplitude: 0.1,
                peak_breeding_month: 5,
                base_food_capacity: 0.9,
                food_scaling_factor: 0.8,
                water_availability: 0.8,
                urban_risk: 0.15,
                disease_risk: 0.1,
                natural_risk: 0.1,
                caretaker_support: 1.0,
                feeding_consistency: 0.8,
                territory_size: 1000,
                density_impact_threshold: 1.2
            }
        };

        // Parameter ranges for testing
        const parameterRanges = {
            breeding_rate: { min: 0.3, max: 1.0, step: 0.1, name: "Breeding Rate" },
            kittens_per_litter: { min: 1, max: 6, step: 1, name: "Kittens per Litter" },
            litters_per_year: { min: 1, max: 4, step: 0.5, name: "Litters per Year" },
            female_ratio: { min: 0.3, max: 0.7, step: 0.1, name: "Female Ratio" },
            kitten_survival_rate: { min: 0.4, max: 0.9, step: 0.1, name: "Kitten Survival Rate" },
            adult_survival_rate: { min: 0.6, max: 0.95, step: 0.05, name: "Adult Survival Rate" },
            kitten_maturity_months: { min: 4, max: 8, step: 1, name: "Kitten Maturity Months" },
            base_food_capacity: { min: 0.4, max: 1.0, step: 0.1, name: "Base Food Capacity" },
            food_scaling_factor: { min: 0.4, max: 1.0, step: 0.1, name: "Food Scaling Factor" },
            water_availability: { min: 0.4, max: 1.0, step: 0.1, name: "Water Availability" },
            urban_risk: { min: 0.05, max: 0.3, step: 0.05, name: "Urban Risk" },
            disease_risk: { min: 0.05, max: 0.3, step: 0.05, name: "Disease Risk" },
            natural_risk: { min: 0.05, max: 0.3, step: 0.05, name: "Natural Risk" },
            territory_size: { min: 200, max: 5000, step: 600, name: "Territory Size" },
            density_impact_threshold: { min: 0.5, max: 2.0, step: 0.3, name: "Density Impact Threshold" }
        };

        const tests = [];

        // Generate tests for each parameter
        for (const [param, range] of Object.entries(parameterRanges)) {
            for (let value = range.min; value <= range.max; value += range.step) {
                tests.push({
                    name: `${range.name} (${value})`,
                    config: {
                        ...baseConfig,
                        params: {
                            ...baseConfig.params,
                            [param]: value
                        }
                    },
                    expectedTrend: `Testing ${range.name} at value ${value}`,
                    parameter: param,
                    value: value
                });
            }
        }

        // Run all tests
        const results = [];
        for (const test of tests) {
            console.log(`Running test: ${test.name}`);
            
            // Run the test multiple times
            const response = await fetch(`${baseUrl}/calculate_population`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(test.config)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Extract key metrics
            const result = {
                test_name: test.name,
                parameter: test.parameter,
                value: test.value,
                final_population: data.final_population,
                population_growth: data.population_growth,
                total_deaths: data.total_deaths,
                kitten_deaths: data.kitten_deaths,
                adult_deaths: data.adult_deaths,
                natural_deaths: data.natural_deaths,
                urban_deaths: data.urban_deaths,
                disease_deaths: data.disease_deaths
            };

            if (data.monte_carlo_summary) {
                result.population_mean = data.monte_carlo_summary.final_population.mean;
                result.population_std = data.monte_carlo_summary.final_population.std;
                result.deaths_mean = data.monte_carlo_summary.total_deaths.mean;
                result.deaths_std = data.monte_carlo_summary.total_deaths.std;
            }

            results.push(result);
            
            // Update calculations.csv
            await fetch(`${baseUrl}/save_calculation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    data: result,
                    append: true
                })
            });
        }

        console.log('All parameter tests completed');
        alert('Parameter tests completed successfully. Results have been saved to calculations.csv');

    } catch (error) {
        console.error('Error running parameter tests:', error);
        alert('Error running parameter tests: ' + error.message);
    } finally {
        testBtn.disabled = false;
        testBtn.textContent = originalText;
    }
}

async function downloadResults() {
    const downloadBtn = document.getElementById('downloadCSVBtn');
    if (!downloadBtn) {
        console.error('Download button not found');
        return;
    }

    const filename = downloadBtn.dataset.filename;
    
    if (!filename) {
        alert('Please run the parameter tests first.');
        return;
    }
    
    try {
        const response = await fetch(`${baseUrl}/download_logs/${filename}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
    } catch (error) {
        console.error('Error downloading results:', error);
        alert('Error downloading results: ' + error.message);
    }
}

function showInitialState() {
    // Show placeholder data in the results section
    const safeSetContent = (elementId, content) => {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = content;
        }
    };

    // Update card values with placeholder data
    safeSetContent('final_population', '---');
    safeSetContent('population_change', '---');
    safeSetContent('sterilization_rate', '---');
    safeSetContent('total_cost', '---');

    // Show initial message in the graph container
    const graphContainer = document.getElementById('population_graph');
    if (graphContainer) {
        const layout = {
            annotations: [{
                text: 'Adjust parameters and click Calculate to see population projections',
                showarrow: false,
                font: {
                    size: 16
                },
                xref: 'paper',
                yref: 'paper',
                x: 0.5,
                y: 0.5
            }],
            xaxis: {
                visible: false
            },
            yaxis: {
                visible: false
            },
            paper_bgcolor: '#f8fafc',  // Tailwind's slate-50
            plot_bgcolor: '#f8fafc',
            margin: {
                l: 40,
                r: 40,
                t: 40,
                b: 40
            }
        };
        
        Plotly.newPlot('population_graph', [], layout);
    }

    // Show the results section
    const resultsSection = document.getElementById('results-section');
    if (resultsSection) {
        resultsSection.style.display = 'block';
    }
}

// Set up event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize input event listeners
    initializeInputListeners();
    
    // Show initial state
    showInitialState();
    
    // Set up event listeners for buttons
    const testBtn = document.getElementById('testParametersBtn');
    const downloadBtn = document.getElementById('downloadCSVBtn');
    const downloadLogsBtn = document.getElementById('downloadLogsBtn');
    const clearLogsBtn = document.getElementById('clearLogsBtn');
    
    if (testBtn) {
        testBtn.addEventListener('click', runParameterTests);
    }
    
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadResults);
    }
    
    if (downloadLogsBtn) {
        downloadLogsBtn.addEventListener('click', downloadLogs);
    }
    
    if (clearLogsBtn) {
        clearLogsBtn.addEventListener('click', clearLogs);
    }
});

// Optimize graph plotting with debouncing and memoization
const memoizedPlot = (() => {
    let lastData = null;
    let lastPlot = null;
    
    return (data, element) => {
        // Only replot if data has changed
        if (JSON.stringify(data) !== JSON.stringify(lastData)) {
            lastData = data;
            lastPlot = Plotly.newPlot(element, data.traces, data.layout, data.config);
        }
        return lastPlot;
    };
})();
