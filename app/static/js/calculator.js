// Define calculator version
const CALCULATOR_VERSION = '1.0.0';
window.CALCULATOR_VERSION = CALCULATOR_VERSION;  // Make version globally available

// Determine the base URL based on the current environment
const isLocalhost = ['localhost', '127.0.0.1', '192.168.1.169'].includes(window.location.hostname);
const baseUrl = isLocalhost ? `http://${window.location.host}` : 'https://hawaiicats.org';

// Function to collect advanced parameters from the form
function collectAdvancedParameters() {
    return {
        kittenSurvivalRate: parseFloat(document.getElementById('kittenSurvivalRate')?.value || '0.5'),
        birthRate: parseFloat(document.getElementById('birthRate')?.value || '0.5'),
        naturalDeathRate: parseFloat(document.getElementById('naturalDeathRate')?.value || '0.1'),
        urbanDeathRate: parseFloat(document.getElementById('urbanDeathRate')?.value || '0.1'),
        diseaseDeathRate: parseFloat(document.getElementById('diseaseDeathRate')?.value || '0.1'),
        carryingCapacity: parseFloat(document.getElementById('carryingCapacity')?.value || '1000'),
        densityDependentBirthScale: parseFloat(document.getElementById('densityDependentBirthScale')?.value || '0.5'),
        densityDependentDeathScale: parseFloat(document.getElementById('densityDependentDeathScale')?.value || '0.5')
    };
}

// Remove duplicate toggleAdvancedMode function since it's already in script.js

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
    const colonySizeInput = document.getElementById('initialColonySize');
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
            document.getElementById('territorySize').value = presetData.territory;
            document.getElementById('territorySizeCustom').value = presetData.territory;
            document.getElementById('densityThreshold').value = presetData.density;
            document.getElementById('densityThresholdCustom').value = presetData.density;
            document.getElementById('presetInfo').textContent = presetData.description;
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
    document.getElementById('territorySize').addEventListener('change', function(e) {
        document.getElementById('territorySizeCustom').value = e.target.value;
    });

    document.getElementById('densityThreshold').addEventListener('change', function(e) {
        document.getElementById('densityThresholdCustom').value = e.target.value;
    });

    // Update select inputs when custom values change
    document.getElementById('territorySizeCustom').addEventListener('input', function(e) {
        const select = document.getElementById('territorySize');
        select.value = Array.from(select.options).find(opt => opt.value === e.target.value)?.value || '';
    });

    document.getElementById('densityThresholdCustom').addEventListener('input', function(e) {
        const select = document.getElementById('densityThreshold');
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
        const initialColonySize = parseInt(document.getElementById('initialColonySize').value);
        const alreadySterilized = parseInt(document.getElementById('alreadySterilized').value);
        const monthlySterilizationRate = parseInt(document.getElementById('monthlySterilizationRate').value);
        const simulationLength = parseInt(document.getElementById('simulationLength').value);
        const sterilizationCost = parseFloat(document.getElementById('sterilizationCost').value);
        const useMonteCarloCheckbox = document.getElementById('useMonteCarlo')?.checked || false;

        // Validate input
        if (isNaN(initialColonySize) || initialColonySize < 1) {
            throw new Error('Colony size must be at least 1');
        }

        // Prepare request data
        const data = {
            initialColonySize: initialColonySize,
            alreadySterilized: alreadySterilized,
            monthlySterilizationRate: monthlySterilizationRate,
            simulationLength: simulationLength,
            sterilizationCost: sterilizationCost,
            useMonteCarlo: useMonteCarloCheckbox,
            monthlyAbandonment: validateInput(document.getElementById('monthlyAbandonment')?.value || '2', 'Monthly Abandonment', 0, 50),
        };

        // Add Monte Carlo specific parameters if enabled
        if (useMonteCarlo) {
            console.log('Adding Monte Carlo parameters');
            data.monteCarloRuns = validateInput(document.getElementById('numSimulations')?.value || '500', 'Number of Simulations', 100, 1000);
            data.variationCoefficient = validateInput(document.getElementById('variationCoefficient')?.value || '0.2', 'Variation Coefficient', 0, 1);
            console.log('Monte Carlo parameters:', { 
                monteCarloRuns: data.monteCarloRuns, 
                variationCoefficient: data.variationCoefficient,
                useMonteCarlo: data.useMonteCarlo
            });
        }

        // Validate dependencies between parameters
        if (alreadySterilized > initialColonySize) {
            throw new Error('Sterilized count cannot exceed colony size');
        }

        // Update max sterilization before collecting data
        updateMaxSterilization();
        
        // Get advanced parameters if in advanced mode
        if (isAdvanced) {
            data.params = collectAdvancedParameters();
        }

        console.log('Sending data to server:', JSON.stringify(data, null, 2));

        try {
            console.log('Making fetch request to:', `${baseUrl}/calculate_population`);
            const response = await fetch(`${baseUrl}/calculate_population`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
                timeout: 30000  // 30 second timeout
            });
            console.log('Received response status:', response.status);

            if (!response.ok) {
                let errorMessage = `Server error (${response.status})`;
                try {
                    const errorData = await response.text();
                    console.log('Error response data:', errorData);
                    if (errorData.startsWith('{')) {
                        const jsonError = JSON.parse(errorData);
                        errorMessage = jsonError.error || errorMessage;
                    } else if (errorData.includes('<')) {
                        errorMessage = `Server error (${response.status}). Please try again with fewer simulations or a shorter time period.`;
                    }
                    console.error('Detailed error:', {
                        status: response.status,
                        statusText: response.statusText,
                        errorData: errorData
                    });
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
                console.error('Error parsing response:', {
                    error: e,
                    stack: e.stack
                });
                throw new Error('Invalid response from server');
            }

            if (!result) {
                console.error('Empty result received from server');
                throw new Error('Empty response from server');
            }

            console.log('Received result from server:', JSON.stringify(result, null, 2));
            
            // Ensure we have the correct data structure
            if (useMonteCarlo) {
                if (!result.result || !result.result.confidenceInterval || !result.result.standardDeviation) {
                    console.warn('Monte Carlo simulation was requested but data is missing:', result);
                    throw new Error('Monte Carlo simulation failed. Please try again with fewer simulations.');
                }
                
                // Validate the Monte Carlo data structure
                const monteCarloResult = result.result;
                if (!monteCarloResult.finalPopulation || !monteCarloResult.monthlyPopulations || 
                    !monteCarloResult.monthlySterilized || !monteCarloResult.monthlyKittens) {
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
        const totalDeaths = resultData.totalDeaths;
        const kittenDeaths = resultData.kittenDeaths;
        const adultDeaths = resultData.adultDeaths;
        const mortalityRate = ((totalDeaths / (resultData.finalPopulation + totalDeaths)) * 100).toFixed(1);
        const naturalDeaths = resultData.naturalDeaths;
        const urbanDeaths = resultData.urbanDeaths;
        const diseaseDeaths = resultData.diseaseDeaths;

        // Update mortality statistics
        safeSetContent('totalDeaths', formatNumber(totalDeaths));
        safeSetContent('kittenDeaths', formatNumber(kittenDeaths));
        safeSetContent('adultDeaths', formatNumber(adultDeaths));
        safeSetContent('mortalityRate', `${mortalityRate}%`);
        safeSetContent('naturalDeaths', formatNumber(naturalDeaths));
        safeSetContent('urbanDeaths', formatNumber(urbanDeaths));
        safeSetContent('diseaseDeaths', formatNumber(diseaseDeaths));

        // Update basic statistics
        safeSetContent('finalPopulation', formatNumber(resultData.finalPopulation));
        safeSetContent('populationChange', formatNumber(resultData.populationGrowth));
        safeSetContent('sterilizationRate', `${((resultData.finalSterilized / resultData.finalPopulation) * 100).toFixed(1)}%`);
        safeSetContent('totalCost', formatNumber(resultData.totalCost, true));

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

        // Generate months array for x-axis based on actual data length
        const months = Array.from({length: resultData.monthlyPopulations.length}, (_, i) => i);

        // Create datasets array starting with the main population line
        const datasets = [];

        // If we have Monte Carlo results, calculate confidence intervals
        if (resultData.allResults && resultData.allResults.length > 0) {
            // Calculate mean and bounds for each month
            const numMonths = resultData.allResults[0].monthlyPopulations.length;
            const meanPopulations = new Array(numMonths).fill(0);
            const lowerBounds = new Array(numMonths).fill(0);
            const upperBounds = new Array(numMonths).fill(0);

            // Calculate means
            for (let month = 0; month < numMonths; month++) {
                const monthValues = resultData.allResults.map(r => r.monthlyPopulations[month]);
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
                data: resultData.monthlyPopulations,
                borderColor: 'rgb(79, 70, 229)',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            });
        }

        // Add sterilized population line if available
        if (resultData.monthlySterilized) {
            datasets.push({
                label: 'Sterilized',
                data: resultData.monthlySterilized,
                borderColor: 'rgb(16, 185, 129)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            });
        }

        // Add reproductive population line if available
        if (resultData.monthlyReproductive) {
            datasets.push({
                label: 'Reproductive',
                data: resultData.monthlyReproductive,
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
            initialColonySize: 50,
            alreadySterilized: 0,
            monthlySterilizationRate: 0,
            useMonteCarlo: true,
            monteCarloRuns: 50,
            params: {
                breedingRate: 0.85,
                kittensPerLitter: 4,
                littersPerYear: 2.5,
                femaleRatio: 0.5,
                kittenSurvivalRate: 0.75,
                adultSurvivalRate: 0.90,
                kittenMaturityMonths: 6,
                seasonalBreedingAmplitude: 0.1,
                peakBreedingMonth: 5,
                baseFoodCapacity: 0.9,
                foodScalingFactor: 0.8,
                waterAvailability: 0.8,
                urbanRisk: 0.15,
                diseaseRisk: 0.1,
                naturalRisk: 0.1,
                caretakerSupport: 1.0,
                feedingConsistency: 0.8,
                territorySize: 1000,
                densityImpactThreshold: 1.2
            }
        };

        // Parameter ranges for testing
        const parameterRanges = {
            breedingRate: { min: 0.3, max: 1.0, step: 0.1, name: "Breeding Rate" },
            kittensPerLitter: { min: 1, max: 6, step: 1, name: "Kittens per Litter" },
            littersPerYear: { min: 1, max: 4, step: 0.5, name: "Litters per Year" },
            femaleRatio: { min: 0.3, max: 0.7, step: 0.1, name: "Female Ratio" },
            kittenSurvivalRate: { min: 0.4, max: 0.9, step: 0.1, name: "Kitten Survival Rate" },
            adultSurvivalRate: { min: 0.6, max: 0.95, step: 0.05, name: "Adult Survival Rate" },
            kittenMaturityMonths: { min: 4, max: 8, step: 1, name: "Kitten Maturity Months" },
            baseFoodCapacity: { min: 0.4, max: 1.0, step: 0.1, name: "Base Food Capacity" },
            foodScalingFactor: { min: 0.4, max: 1.0, step: 0.1, name: "Food Scaling Factor" },
            waterAvailability: { min: 0.4, max: 1.0, step: 0.1, name: "Water Availability" },
            urbanRisk: { min: 0.05, max: 0.3, step: 0.05, name: "Urban Risk" },
            diseaseRisk: { min: 0.05, max: 0.3, step: 0.05, name: "Disease Risk" },
            naturalRisk: { min: 0.05, max: 0.3, step: 0.05, name: "Natural Risk" },
            territorySize: { min: 200, max: 5000, step: 600, name: "Territory Size" },
            densityImpactThreshold: { min: 0.5, max: 2.0, step: 0.3, name: "Density Impact Threshold" }
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
                testName: test.name,
                parameter: test.parameter,
                value: test.value,
                finalPopulation: data.finalPopulation,
                populationGrowth: data.populationGrowth,
                totalDeaths: data.totalDeaths,
                kittenDeaths: data.kittenDeaths,
                adultDeaths: data.adultDeaths,
                naturalDeaths: data.naturalDeaths,
                urbanDeaths: data.urbanDeaths,
                diseaseDeaths: data.diseaseDeaths
            };

            if (data.monteCarloSummary) {
                result.populationMean = data.monteCarloSummary.finalPopulation.mean;
                result.populationStd = data.monteCarloSummary.finalPopulation.std;
                result.deathsMean = data.monteCarloSummary.totalDeaths.mean;
                result.deathsStd = data.monteCarloSummary.totalDeaths.std;
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
    safeSetContent('finalPopulation', '---');
    safeSetContent('populationChange', '---');
    safeSetContent('sterilizationRate', '---');
    safeSetContent('totalCost', '---');

    // Show initial message in the graph container
    const graphContainer = document.getElementById('populationGraph');
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
        
        Plotly.newPlot('populationGraph', [], layout);
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
