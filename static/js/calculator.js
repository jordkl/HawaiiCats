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
        if (useMonteCarlo) {
            data.num_simulations = validateInput(document.getElementById('numSimulations')?.value, 'Number of Simulations', 100, 10000);
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
            throw new Error('Invalid response from server. Please try again.');
        }

        if (!result) {
            throw new Error('Empty response from server');
        }

        console.log('Received result from server:', result);
        
        // Ensure we have the correct data structure
        if (useMonteCarlo) {
            if (!result.monte_carlo_summary || !result.monte_carlo_data) {
                console.warn('Monte Carlo simulation was requested but data is missing');
                throw new Error('Monte Carlo simulation failed. Please try again with fewer simulations.');
            }
        }

        await displayResults(result);
        
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
        // Re-enable calculate button
        const calculateButton = document.getElementById('calculateButton');
        if (calculateButton) {
            calculateButton.disabled = false;
            calculateButton.textContent = 'Calculate';
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
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        
        const contentType = response.headers.get("content-type");
        const responseText = await response.text();
        
        let result;
        try {
            result = JSON.parse(responseText);
        } catch (e) {
            console.error('Failed to parse response as JSON:', responseText);
            throw new Error('Invalid response from server');
        }
        
        if (!response.ok) {
            throw new Error(JSON.stringify(result));
        }
        
        if (!contentType || !contentType.includes("application/json")) {
            throw new TypeError("Received non-JSON response from server");
        }
        
        return result;
    } catch (error) {
        console.error('Error in calculatePopulation:', error);
        throw error;
    }
}

function displayResults(data) {
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

        // Plot the population graph
        plotPopulationGraph(resultData);
        
        console.log('displayResults completed successfully');
    } catch (error) {
        console.error('Error in displayResults:', error);
        console.error('Error stack:', error.stack);
        alert('An error occurred while displaying results. Check the console for details.');
    }
}

function plotPopulationGraph(data) {
    try {
        console.log('Plotting population graph with data:', data);
        
        // Extract the actual result data, handling both direct results and nested results
        const resultData = data.result || data;
        
        if (!resultData || !resultData.monthly_populations || !Array.isArray(resultData.monthly_populations)) {
            console.error('Invalid data format for population graph:', resultData);
            return;
        }

        const months = Array.from({length: resultData.monthly_populations.length}, (_, i) => i);
        const totalPopulation = resultData.monthly_populations;
        const sterilized = resultData.monthly_sterilized;
        const reproductive = resultData.monthly_reproductive;
        const kittens = resultData.monthly_kittens;

        console.log('Processed data for graph:', {
            months,
            totalPopulation,
            sterilized,
            reproductive,
            kittens
        });

        // Calculate confidence intervals if Monte Carlo data is available
        let ciUpper = null;
        let ciLower = null;
        if (resultData.monte_carlo_data && resultData.monte_carlo_data.final_population) {
            const startPop = totalPopulation[0];
            const endPop = totalPopulation[totalPopulation.length - 1];
            const ciStartUpper = startPop;
            const ciStartLower = startPop;
            const ciEndUpper = resultData.monte_carlo_data.final_population.upper;
            const ciEndLower = resultData.monte_carlo_data.final_population.lower;
            
            // Linear interpolation for confidence intervals
            ciUpper = months.map(month => {
                const progress = month / (months.length - 1);
                return ciStartUpper + (ciEndUpper - ciStartUpper) * progress;
            });
            ciLower = months.map(month => {
                const progress = month / (months.length - 1);
                return ciStartLower + (ciEndLower - ciStartLower) * progress;
            });
        }

        const traces = [
            {
                name: 'Total Population',
                x: months,
                y: totalPopulation,
                mode: 'lines',
                line: {
                    color: '#4F46E5',
                    width: 3
                }
            },
            {
                name: 'Sterilized',
                x: months,
                y: sterilized,
                mode: 'lines',
                line: {
                    color: '#10B981',
                    width: 2
                }
            },
            {
                name: 'Reproductive',
                x: months,
                y: reproductive,
                mode: 'lines',
                line: {
                    color: '#EF4444',
                    width: 2
                }
            },
            {
                name: 'Kittens',
                x: months,
                y: kittens,
                mode: 'lines',
                line: {
                    color: '#F59E0B',
                    width: 2
                }
            }
        ];

        // Add confidence interval if available
        if (ciUpper && ciLower) {
            traces.push({
                name: '95% Confidence Interval',
                x: [...months, ...months.slice().reverse()],
                y: [...ciUpper, ...ciLower.slice().reverse()],
                fill: 'toself',
                fillcolor: 'rgba(79, 70, 229, 0.1)',
                line: { color: 'transparent' },
                showlegend: true,
                hoverinfo: 'skip'
            });
        }

        const layout = {
            title: '',
            xaxis: {
                title: 'Months',
                showgrid: true,
                zeroline: false
            },
            yaxis: {
                title: 'Number of Cats',
                showgrid: true,
                zeroline: false
            },
            showlegend: true,
            legend: {
                x: 0,
                y: 1.1,
                orientation: 'h'
            },
            margin: { t: 20 },
            hovermode: 'x unified'
        };

        const config = {
            responsive: true,
            displayModeBar: false
        };

        console.log('Attempting to plot graph with:', {
            element: document.getElementById('populationGraph'),
            traces,
            layout,
            config
        });

        if (!document.getElementById('populationGraph')) {
            console.error('Population graph element not found in DOM');
            return;
        }

        // Add a small delay to ensure the DOM is ready
        setTimeout(() => {
            try {
                Plotly.newPlot('populationGraph', traces, layout, config)
                    .then(() => console.log('Graph plotted successfully'))
                    .catch(error => console.error('Error plotting graph:', error));
            } catch (error) {
                console.error('Error in Plotly.newPlot:', error);
            }
        }, 100);
    } catch (error) {
        console.error('Error in plotPopulationGraph:', error);
    }
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
        const baseConfig = {
            months: 24,
            current_size: 10,
            sterilized_count: 0,
            monthly_sterilization: 2,
            params: {
                breeding_rate: 0.7,
                kittens_per_litter: 4,
                litters_per_year: 2,
                female_ratio: 0.5,
                kitten_survival_rate: 0.7,
                adult_survival_rate: 0.8,
                kitten_maturity_months: 6,
                sterilization_cost: 50,
                seasonal_breeding_amplitude: 0.3,
                peak_breeding_month: 5,
                water_availability: 0.8,
                shelter_quality: 0.7,
                urban_risk: 0.1,
                disease_risk: 0.1,
                natural_risk: 0.1,
                caretaker_support: 1.0,
                feeding_consistency: 0.8,
                human_interference: 0.5,
                territory_size: 1000,
                density_impact_threshold: 1.2,
                monthly_abandonment: 0.1,
                abandoned_sterilized_ratio: 0.2
            }
        };

        const scenarios = [
            // Baseline
            { ...baseConfig },
            
            // High Urban Risk
            {
                ...baseConfig,
                params: {
                    ...baseConfig.params,
                    urban_risk: 0.3,
                    disease_risk: 0.05,
                    natural_risk: 0.05,
                    kitten_survival_rate: 0.6,
                    adult_survival_rate: 0.7
                }
            },
            
            // High Natural Risk
            {
                ...baseConfig,
                params: {
                    ...baseConfig.params,
                    urban_risk: 0.05,
                    disease_risk: 0.05,
                    natural_risk: 0.3,
                    kitten_survival_rate: 0.6,
                    adult_survival_rate: 0.7,
                    water_availability: 0.5,
                    food_scaling_factor: 0.5
                }
            },
            
            // High Disease Risk
            {
                ...baseConfig,
                params: {
                    ...baseConfig.params,
                    urban_risk: 0.05,
                    disease_risk: 0.3,
                    natural_risk: 0.05,
                    kitten_survival_rate: 0.5,
                    adult_survival_rate: 0.6,
                    density_impact_threshold: 1.2
                }
            },
            
            // Combined Environmental Stress
            {
                ...baseConfig,
                params: {
                    ...baseConfig.params,
                    urban_risk: 0.15,
                    disease_risk: 0.15,
                    natural_risk: 0.15,
                    water_availability: 0.6,
                    shelter_quality: 0.6,
                    food_scaling_factor: 0.6,
                    kitten_survival_rate: 0.5,
                    adult_survival_rate: 0.6
                }
            },

            // High Population Density Impact
            {
                ...baseConfig,
                current_size: 50,
                params: {
                    ...baseConfig.params,
                    density_impact_threshold: 1.2,
                    territory_size: 500,
                    disease_risk: 0.15,
                    food_scaling_factor: 0.6,
                    water_availability: 0.7
                }
            },

            // Seasonal Variation
            {
                ...baseConfig,
                months: 36,
                params: {
                    ...baseConfig.params,
                    seasonal_breeding_amplitude: 0.5,
                    peak_breeding_month: 5,
                    water_availability: 0.7,
                    food_scaling_factor: 0.7
                }
            },

            // Urban Environment
            {
                ...baseConfig,
                current_size: 30,
                params: {
                    ...baseConfig.params,
                    urban_risk: 0.25,
                    disease_risk: 0.15,
                    natural_risk: 0.05,
                    caretaker_support: 1.5,
                    feeding_consistency: 0.9,
                    human_interference: 0.7,
                    territory_size: 300
                }
            },

            // Rural Environment
            {
                ...baseConfig,
                current_size: 20,
                params: {
                    ...baseConfig.params,
                    urban_risk: 0.05,
                    disease_risk: 0.1,
                    natural_risk: 0.2,
                    caretaker_support: 0.5,
                    feeding_consistency: 0.6,
                    human_interference: 0.3,
                    territory_size: 2000
                }
            },

            // High Abandonment
            {
                ...baseConfig,
                params: {
                    ...baseConfig.params,
                    monthly_abandonment: 0.3,
                    abandoned_sterilized_ratio: 0.3,
                    urban_risk: 0.2,
                    disease_risk: 0.15,
                    natural_risk: 0.1
                }
            }
        ];

        let completedTests = 0;
        const totalTests = scenarios.length;
        
        for (const scenario of scenarios) {
            completedTests++;
            testBtn.textContent = `Running Tests (${completedTests}/${totalTests})...`;
            await calculatePopulation(scenario);
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        const downloadBtn = document.getElementById('downloadLogsBtn');
        if (downloadBtn) {
            downloadBtn.classList.add('highlight');
            setTimeout(() => downloadBtn.classList.remove('highlight'), 2000);
        }
        
        // Show success message in a more subtle way
        const resultsDiv = document.querySelector('.results-container');
        if (resultsDiv) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'alert alert-success mt-4';
            messageDiv.textContent = 'Parameter tests completed successfully! Click "Download Results" to view the data.';
            resultsDiv.insertBefore(messageDiv, resultsDiv.firstChild);
            setTimeout(() => messageDiv.remove(), 5000);
        }
    } catch (error) {
        console.error('Error running tests:', error);
        // Show error in a more subtle way
        const resultsDiv = document.querySelector('.results-container');
        if (resultsDiv) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'alert alert-error mt-4';
            messageDiv.textContent = 'Error running tests: ' + error.message;
            resultsDiv.insertBefore(messageDiv, resultsDiv.firstChild);
            setTimeout(() => messageDiv.remove(), 5000);
        }
    } finally {
        if (testBtn) {
            testBtn.disabled = false;
            testBtn.textContent = originalText;
        }
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

function plotPopulationGraph(data) {
    try {
        console.log('Plotting population graph with data:', data);
        
        // Extract the actual result data, handling both direct results and nested results
        const resultData = data.result || data;
        
        if (!resultData || !resultData.monthly_populations || !Array.isArray(resultData.monthly_populations)) {
            console.error('Invalid data format for population graph:', resultData);
            return;
        }

        const months = Array.from({length: resultData.monthly_populations.length}, (_, i) => i);
        const totalPopulation = resultData.monthly_populations;
        const sterilized = resultData.monthly_sterilized;
        const reproductive = resultData.monthly_reproductive;
        const kittens = resultData.monthly_kittens;

        // Prepare graph data
        const graphData = {
            traces: [
                {
                    name: 'Total Population',
                    x: months,
                    y: totalPopulation,
                    mode: 'lines',
                    line: { color: '#4F46E5', width: 3 }
                },
                {
                    name: 'Sterilized',
                    x: months,
                    y: sterilized,
                    mode: 'lines',
                    line: { color: '#10B981', width: 2 }
                },
                {
                    name: 'Reproductive',
                    x: months,
                    y: reproductive,
                    mode: 'lines',
                    line: { color: '#EF4444', width: 2 }
                },
                {
                    name: 'Kittens',
                    x: months,
                    y: kittens,
                    mode: 'lines',
                    line: { color: '#F59E0B', width: 2 }
                }
            ],
            layout: {
                title: '',
                xaxis: {
                    title: 'Months',
                    showgrid: true,
                    zeroline: false
                },
                yaxis: {
                    title: 'Number of Cats',
                    showgrid: true,
                    zeroline: false
                },
                showlegend: true,
                legend: {
                    x: 0,
                    y: 1.1,
                    orientation: 'h'
                },
                margin: { t: 20 },
                hovermode: 'x unified'
            },
            config: {
                responsive: true,
                displayModeBar: false
            }
        };

        // Add confidence intervals if available
        if (resultData.monte_carlo_data?.final_population) {
            const { upper, lower } = resultData.monte_carlo_data.final_population;
            const ciUpper = months.map(month => {
                const progress = month / (months.length - 1);
                return totalPopulation[0] + (upper - totalPopulation[0]) * progress;
            });
            const ciLower = months.map(month => {
                const progress = month / (months.length - 1);
                return totalPopulation[0] + (lower - totalPopulation[0]) * progress;
            });

            graphData.traces.push({
                name: '95% Confidence Interval',
                x: [...months, ...months.slice().reverse()],
                y: [...ciUpper, ...ciLower.slice().reverse()],
                fill: 'toself',
                fillcolor: 'rgba(79, 70, 229, 0.1)',
                line: { color: 'transparent' },
                showlegend: true,
                hoverinfo: 'skip'
            });
        }

        const graphElement = document.getElementById('populationGraph');
        if (!graphElement) {
            console.error('Population graph element not found in DOM');
            return;
        }

        // Use memoized plotting
        memoizedPlot(graphData, graphElement)
            .then(() => console.log('Graph plotted successfully'))
            .catch(error => console.error('Error plotting graph:', error));

    } catch (error) {
        console.error('Error in plotPopulationGraph:', error);
        // Show user-friendly error message
        const graphElement = document.getElementById('populationGraph');
        if (graphElement) {
            graphElement.innerHTML = `
                <div class="text-center p-4 text-red-600">
                    <p>Failed to plot graph. Please try again with different parameters.</p>
                    <p class="text-sm mt-2">Error: ${error.message}</p>
                </div>
            `;
        }
    }
}
