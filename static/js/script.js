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
    const inputs = {
        currentSize: document.getElementById('currentSize')?.value || '',
        sterilizedCount: document.getElementById('sterilizedCount')?.value || '',
        monthlysterilization: document.getElementById('monthlysterilization')?.value || '',
        sterilizationCost: document.getElementById('sterilizationCost')?.value || '',
        months: document.getElementById('months')?.value || ''
    };

    // If advanced mode is enabled, get advanced parameters
    if (document.getElementById('advancedMode')?.checked) {
        Object.assign(inputs, {
            monthlyAbandonment: document.getElementById('monthlyAbandonment')?.value || '',
            abandonedSterilizedRatio: document.getElementById('abandonedSterilizedRatio')?.value || '',
            breedingRate: document.getElementById('breedingRate')?.value || '',
            kittensPerLitter: document.getElementById('kittensPerLitter')?.value || '',
            littersPerYear: document.getElementById('littersPerYear')?.value || '',
            kittenSurvivalRate: document.getElementById('kittenSurvivalRate')?.value || '',
            kittenMaturityMonths: document.getElementById('kittenMaturityMonths')?.value || '',
            baseFoodCapacity: document.getElementById('baseFoodCapacity')?.value || '',
            caretakerSupport: document.getElementById('caretakerSupport')?.value || ''
        });
    }

    // Get the results from the page, with null checks
    const results = {
        populationDetails: document.getElementById('populationDetails')?.innerText || 'No calculation performed',
        costAnalysis: document.getElementById('costAnalysis')?.innerText || 'No calculation performed',
        mortalityStatistics: document.getElementById('mortalityStatistics')?.innerText || 'No calculation performed'
    };

    return {
        inputs: inputs,
        results: results,
        timestamp: new Date().toISOString(),
        advancedMode: document.getElementById('advancedMode')?.checked || false
    };
}

// Function to flag scenario
function flagScenario() {
    // Check if a calculation has been performed
    const resultsSection = document.getElementById('resultsSection');
    if (!resultsSection || resultsSection.classList.contains('hidden')) {
        alert('Please run a calculation before flagging a scenario.');
        return;
    }

    // Prompt user for notes
    const userNote = prompt('Please describe what you noticed was wrong or interesting about this scenario:');
    if (userNote === null) {  // User clicked Cancel
        return;
    }

    const scenarioData = collectScenarioData();
    scenarioData.userNote = userNote;  // Add the user's note to the data
    
    // Use production URL
    const baseUrl = 'https://hawaiicats.org';

    // Send data to backend
    fetch(`${baseUrl}/flag_scenario`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(scenarioData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Scenario has been flagged and saved!');
        } else {
            alert('Error saving scenario: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to flag scenario. Please try again.');
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
    logContent += `\nPopulation Details:\n${scenarioData.results.populationDetails}\n`;
    logContent += `\nCost Analysis:\n${scenarioData.results.costAnalysis}\n`;
    logContent += `\nMortality Statistics:\n${scenarioData.results.mortalityStatistics}\n`;

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
