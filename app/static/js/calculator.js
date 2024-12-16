// Define calculator version
const CALCULATOR_VERSION = '1.0.0';
window.CALCULATOR_VERSION = CALCULATOR_VERSION;  // Make version globally available

// Determine the base URL based on the current environment
const isLocalhost = ['localhost', '127.0.0.1', '192.168.1.169'].includes(window.location.hostname);
const baseUrl = isLocalhost ? `http://${window.location.host}` : 'https://hawaiicats.org';

// Function to collect advanced parameters from the form
function collectAdvancedParameters() {
    return {
        kitten_survival_rate: parseFloat(document.getElementById('kittenSurvivalRate')?.value || '0.5'),
        birth_rate: parseFloat(document.getElementById('birthRate')?.value || '0.5'),
        natural_death_rate: parseFloat(document.getElementById('naturalDeathRate')?.value || '0.1'),
        urban_death_rate: parseFloat(document.getElementById('urbanDeathRate')?.value || '0.1'),
        disease_death_rate: parseFloat(document.getElementById('diseaseDeathRate')?.value || '0.1'),
        carrying_capacity: parseFloat(document.getElementById('carryingCapacity')?.value || '1000'),
        density_dependent_birth_scale: parseFloat(document.getElementById('densityDependentBirthScale')?.value || '0.5'),
        density_dependent_death_scale: parseFloat(document.getElementById('densityDependentDeathScale')?.value || '0.5')
    };
}

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
        
        console.log('Starting calculation with Monte Carlo:', useMonteCarlo);
        
        // Show Monte Carlo loading indicator if Monte Carlo is enabled
        const monteCarloLoading = document.getElementById('monteCarloLoading');
        if (useMonteCarlo && monteCarloLoading) {
            monteCarloLoading.classList.add('active');
            console.log('Showing Monte Carlo loading indicator');
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
        if (useMonteCarlo) {
            console.log('Adding Monte Carlo parameters');
            data.num_simulations = validateInput(document.getElementById('numSimulations')?.value || '500', 'Number of Simulations', 100, 1000);
            data.variation_coefficient = validateInput(document.getElementById('variationCoefficient')?.value || '0.2', 'Variation Coefficient', 0, 1);
            console.log('Monte Carlo parameters:', { 
                numSimulations: data.num_simulations, 
                variationCoefficient: data.variation_coefficient,
                useMonteCarlo: data.use_monte_carlo
            });
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

        console.log('Sending data to server:', JSON.stringify(data, null, 2));

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
            console.log('Raw response:', responseText);
            result = JSON.parse(responseText);
        } catch (e) {
            console.error('Error parsing response:', e);
            throw new Error('Invalid response from server');
        }

        if (!result) {
            throw new Error('Empty response from server');
        }

        console.log('Received result from server:', JSON.stringify(result, null, 2));
        
        // Ensure we have the correct data structure
        if (useMonteCarlo) {
            if (!result.result || !result.result.confidence_interval || !result.result.standard_deviation) {
                console.warn('Monte Carlo simulation was requested but data is missing:', result);
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
        if (calculateButton) {
            calculateButton.disabled = false;
            calculateButton.textContent = 'Calculate';
        }
        
        // Hide Monte Carlo loading indicator
        const monteCarloLoading = document.getElementById('monteCarloLoading');
        if (monteCarloLoading) {
            monteCarloLoading.classList.remove('active');
        }
    }
}

async function displayResults(data) {
    try {
        console.log('Starting displayResults with data:', JSON.stringify(data, null, 2));
        
        // Hide placeholder and show results section
        const placeholderSection = document.getElementById('placeholderSection');
        const resultsSection = document.getElementById('resultsSection');
        
        if (placeholderSection) {
            placeholderSection.classList.add('hidden');
        }
        if (resultsSection) {
            resultsSection.classList.remove('hidden');
        }
        
        // Extract the actual result data, handling both direct results and nested results
        const resultData = data.result?.result || data.result || data;
        console.log('Extracted result data:', JSON.stringify(resultData, null, 2));
        
        // Helper function to format numbers with commas and currency
        function formatNumber(value, isCurrency = false) {
            if (typeof value !== 'number') {
                value = parseFloat(value) || 0;
            }
            const formatted = value.toLocaleString('en-US', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            });
            return isCurrency ? `$${formatted}` : formatted;
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

        // Process mortality data
        console.log('Processing mortality data...');
        const totalDeaths = resultData.total_deaths;
        const kittenDeaths = resultData.kitten_deaths;
        const adultDeaths = resultData.adult_deaths;
        const mortalityRate = ((totalDeaths / (resultData.final_population + totalDeaths)) * 100).toFixed(1);
        const naturalDeaths = resultData.natural_deaths;
        const urbanDeaths = resultData.urban_deaths;
        const diseaseDeaths = resultData.disease_deaths;

        // Update mortality statistics
        safeSetContent('totalDeaths', formatNumber(totalDeaths));
        safeSetContent('kittenDeaths', formatNumber(kittenDeaths));
        safeSetContent('adultDeaths', formatNumber(adultDeaths));
        safeSetContent('mortalityRate', `${mortalityRate}%`);
        safeSetContent('naturalDeaths', formatNumber(naturalDeaths));
        safeSetContent('urbanDeaths', formatNumber(urbanDeaths));
        safeSetContent('diseaseDeaths', formatNumber(diseaseDeaths));

        // Update basic statistics
        safeSetContent('finalPopulation', formatNumber(resultData.final_population));
        safeSetContent('populationChange', formatNumber(resultData.population_growth));
        safeSetContent('sterilizationRate', `${((resultData.final_sterilized / resultData.final_population) * 100).toFixed(1)}%`);
        safeSetContent('totalCost', formatNumber(resultData.total_cost, true));

        // Update graphs
        await plotPopulationGraph(resultData);
        
        console.log('displayResults completed successfully');
    } catch (error) {
        console.error('Error in displayResults:', error);
        alert('Error displaying results: ' + error.message);
    }
}

async function plotPopulationGraph(data) {
    try {
        const canvas = document.getElementById('populationChart');
        if (!canvas) {
            console.error('Population chart canvas not found');
            return;
        }
        
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error('Could not get 2D context from canvas');
            return;
        }
        
        const resultData = data.result?.result || data.result || data;
        
        // Clear any existing chart
        if (window.populationChart && typeof window.populationChart.destroy === 'function') {
            window.populationChart.destroy();
            window.populationChart = null;
        }

        // Generate months array for x-axis
        const months = Array.from({length: resultData.monthly_populations.length}, (_, i) => i);

        // Create datasets array starting with the main population line
        const datasets = [];

        // If we have Monte Carlo results, calculate confidence intervals
        if (resultData.all_results && resultData.all_results.length > 0) {
            // Calculate mean and bounds for each month
            const numMonths = resultData.all_results[0].monthly_populations.length;
            const meanPopulations = new Array(numMonths).fill(0);
            const lowerBounds = new Array(numMonths).fill(0);
            const upperBounds = new Array(numMonths).fill(0);

            // Calculate means
            for (let month = 0; month < numMonths; month++) {
                const monthValues = resultData.all_results.map(r => r.monthly_populations[month]);
                meanPopulations[month] = monthValues.reduce((a, b) => a + b, 0) / monthValues.length;
                
                // Calculate 95% confidence interval
                const sortedValues = monthValues.sort((a, b) => a - b);
                const lowerIndex = Math.floor(sortedValues.length * 0.025);
                const upperIndex = Math.floor(sortedValues.length * 0.975);
                lowerBounds[month] = sortedValues[lowerIndex];
                upperBounds[month] = sortedValues[upperIndex];
            }

            // Add shaded area between bounds
            datasets.push({
                label: '95% Confidence Interval',
                data: upperBounds,
                borderColor: 'rgba(79, 70, 229, 0)',
                backgroundColor: 'rgba(79, 70, 229, 0.2)',
                fill: '+1',
                tension: 0.4,
                pointRadius: 0
            });

            datasets.push({
                label: 'Lower Bound',
                data: lowerBounds,
                borderColor: 'rgba(79, 70, 229, 0.5)',
                borderWidth: 1,
                borderDash: [5, 5],
                fill: false,
                tension: 0.4,
                pointRadius: 0
            });

            // Add mean line
            datasets.push({
                label: 'Mean Population',
                data: meanPopulations,
                borderColor: 'rgb(79, 70, 229)',
                borderWidth: 2,
                fill: false,
                tension: 0.4
            });

        } else {
            // Regular single simulation datasets
            datasets.push({
                label: 'Total Population',
                data: resultData.monthly_populations,
                borderColor: 'rgb(79, 70, 229)',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            });
        }

        // Add sterilized population line if available
        if (resultData.monthly_sterilized) {
            datasets.push({
                label: 'Sterilized',
                data: resultData.monthly_sterilized,
                borderColor: 'rgb(16, 185, 129)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            });
        }

        // Add reproductive population line if available
        if (resultData.monthly_reproductive) {
            datasets.push({
                label: 'Reproductive',
                data: resultData.monthly_reproductive,
                borderColor: 'rgb(244, 63, 94)',
                backgroundColor: 'rgba(244, 63, 94, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            });
        }

        // Create new chart
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
                    title: {
                        display: true,
                        text: 'Population Over Time'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Months'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Population'
                        },
                        beginAtZero: true
                    }
                }
            }
        });

        console.log('Population chart created successfully');
    } catch (error) {
        console.error('Error plotting population graph:', error);
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
    
    // Initialize Monte Carlo toggle
    const monteCarloToggle = document.getElementById('useMonteCarlo');
    if (monteCarloToggle) {
        monteCarloToggle.addEventListener('change', function(e) {
            const monteCarloParams = document.getElementById('monteCarloParams');
            if (e.target.checked) {
                monteCarloParams.style.display = 'block';
                console.log('Monte Carlo simulation enabled');
            } else {
                monteCarloParams.style.display = 'none';
                console.log('Monte Carlo simulation disabled');
            }
        });
    }
    
    // Initialize Monte Carlo parameter sliders if they exist
    const numSimulations = document.getElementById('numSimulations');
    const variationCoefficient = document.getElementById('variationCoefficient');
    
    if (numSimulations) {
        numSimulations.addEventListener('input', function(e) {
            const valueDisplay = document.getElementById('numSimulationsValue');
            if (valueDisplay) {
                valueDisplay.textContent = e.target.value;
            }
        });
    }
    
    if (variationCoefficient) {
        variationCoefficient.addEventListener('input', function(e) {
            const valueDisplay = document.getElementById('variationCoefficientValue');
            if (valueDisplay) {
                valueDisplay.textContent = e.target.value;
            }
        });
    }
    
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
