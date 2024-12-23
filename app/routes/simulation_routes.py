from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from app.tools.cat_simulation import DEFAULT_PARAMS, simulatePopulation
from app.tools.cat_simulation.utils.logging_utils import logDebug, logSimulationError, logCalculationResult
import csv
import io
from datetime import datetime
import os
import traceback
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)
CALC_FILE = os.path.join(LOGS_DIR, 'calculations.csv')

bp = Blueprint('simulation', __name__)

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/calculator')
def calculator():
    show_download = current_app.config.get('SHOW_DOWNLOAD_BUTTON', False)
    show_clear = current_app.config.get('SHOW_CLEAR_RESULTS_BUTTON', False)
    show_test = current_app.config.get('SHOW_TEST_PARAMETERS_BUTTON', False)
    
    return render_template('calculator.html',
                         show_download_button=show_download,
                         show_clear_results_button=show_clear,
                         show_test_parameters_button=show_test)

@bp.route("/calculatePopulation", methods=['POST'])
def calculatePopulation():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Log received data with types
        logDebug('DEBUG', f"Received data types: {json.dumps({k: str(type(v)) for k, v in data.items()}, indent=2)}")
        logDebug('DEBUG', f"Received data values: {json.dumps(data, indent=2)}")

        # Extract basic parameters
        try:
            # Get raw values first
            raw_current_size = data.get('initialColonySize', '100')
            raw_months = data.get('simulationLength', '12')
            raw_sterilized = data.get('alreadySterilized', '0')
            raw_monthly = data.get('monthlySterilizationRate', '0')
            raw_abandonment = data.get('monthlyAbandonment', '0')
            
            # Log raw values and their types
            logDebug('DEBUG', f"Raw values: current_size=({type(raw_current_size)}) {raw_current_size}, "
                              f"months=({type(raw_months)}) {raw_months}, "
                              f"sterilized=({type(raw_sterilized)}) {raw_sterilized}, "
                              f"monthly=({type(raw_monthly)}) {raw_monthly}, "
                              f"abandonment=({type(raw_abandonment)}) {raw_abandonment}")
            
            # Convert to strings, handling lists if necessary
            current_size = str(raw_current_size[0] if isinstance(raw_current_size, list) else raw_current_size).strip()
            months = str(raw_months[0] if isinstance(raw_months, list) else raw_months).strip()
            sterilized_count = str(raw_sterilized[0] if isinstance(raw_sterilized, list) else raw_sterilized).strip()
            monthly_sterilization = str(raw_monthly[0] if isinstance(raw_monthly, list) else raw_monthly).strip()
            monthly_abandonment = str(raw_abandonment[0] if isinstance(raw_abandonment, list) else raw_abandonment).strip()

            # Log extracted and converted parameters
            logDebug('DEBUG', f"Converted parameters: current_size={current_size}, months={months}, "
                              f"sterilized_count={sterilized_count}, monthly_sterilization={monthly_sterilization}, "
                              f"monthly_abandonment={monthly_abandonment}")

        except Exception as e:
            error_msg = f"Error extracting basic parameters: {str(e)}\nTraceback: {traceback.format_exc()}"
            logSimulationError('parameter_extraction', error_msg)
            return jsonify({'error': error_msg}), 400

        # Get advanced parameters and convert to snake_case
        params = data.get('params', {})
        snake_case_params = {}
        
        # Parameter mapping with default values
        param_mapping = {
            'territorySize': ('territory_size', '1000'),
            'densityImpactThreshold': ('density_impact_threshold', '1.2'),
            'breedingRate': ('breeding_rate', '0.85'),
            'kittensPerLitter': ('kittens_per_litter', '4'),
            'littersPerYear': ('litters_per_year', '2.5'),
            'kittenSurvivalRate': ('kitten_survival_rate', '0.7'),
            'adultSurvivalRate': ('adult_survival_rate', '0.85'),
            'femaleRatio': ('female_ratio', '0.5'),
            'kittenMaturityMonths': ('kitten_maturity_months', '5'),
            'peakBreedingMonth': ('peak_breeding_month', '4'),
            'seasonalityStrength': ('seasonality_strength', '0.3'),
            'baseFoodCapacity': ('base_food_capacity', '0.9'),
            'foodScalingFactor': ('food_scaling_factor', '0.8'),
            'environmentalStress': ('environmental_stress', '0.15'),
            'resourceCompetition': ('resource_competition', '0.2'),
            'resourceScarcityImpact': ('resource_scarcity_impact', '0.25'),
            'densityStressRate': ('density_stress_rate', '0.15'),
            'maxDensityImpact': ('max_density_impact', '0.5'),
            'baseHabitatQuality': ('base_habitat_quality', '0.8'),
            'urbanizationImpact': ('urbanization_impact', '0.2'),
            'diseaseTransmissionRate': ('disease_transmission_rate', '0.1'),
            'monthlyAbandonment': ('monthly_abandonment', '2.0'),
            'caretakerSupport': ('caretaker_support', '0.5'),
            'feedingConsistency': ('feeding_consistency', '0.9'),
            'foodCostPerCat': ('food_cost_per_cat', '15.0')
        }
        
        # Process each parameter
        for camel_case, (snake_case, default) in param_mapping.items():
            raw_value = params.get(camel_case, default)
            # Handle list values
            if isinstance(raw_value, list):
                raw_value = raw_value[0] if raw_value else default
            snake_case_params[snake_case] = str(raw_value).strip()

        # Add sterilization cost directly from request data
        sterilization_cost = data.get('sterilizationCost', 50.0)
        snake_case_params['sterilization_cost_per_cat'] = str(sterilization_cost)

        # Log converted parameters
        logDebug('DEBUG', f"Converted advanced parameters: {json.dumps(snake_case_params, indent=2)}")

        # Run simulation
        try:
            result = simulatePopulation(
                params=snake_case_params,
                currentSize=current_size,
                months=months,
                sterilizedCount=sterilized_count,
                monthlySterilization=monthly_sterilization,
                monthlyAbandonment=monthly_abandonment
            )

            if result is None:
                raise ValueError("Simulation failed to produce results")

            # Log the calculation
            logCalculationResult(snake_case_params, result)

            # Extract monthly data
            monthly_data = result['monthlyData']
            totalPopulation = [month['total'] for month in monthly_data]
            sterilizedPopulation = [month['sterilized'] for month in monthly_data]
            unsterilizedPopulation = [month['unsterilized'] for month in monthly_data]

            # Calculate population change
            initial_population = monthly_data[0]['total'] if monthly_data else 0
            final_population = monthly_data[-1]['total'] if monthly_data else 0
            population_change = final_population - initial_population

            # Prepare response data
            response_data = {
                'success': True,
                'result': {
                    'finalPopulation': result['finalPopulation'],
                    'populationChange': population_change,
                    'sterilizationRate': result.get('sterilizationRate', 0),
                    'totalCost': result.get('totalCosts', 0),
                    'costBreakdown': result.get('costBreakdown', {}),
                    'totalDeaths': result.get('totalDeaths', 0),
                    'kittenDeaths': result.get('kittenDeaths', 0),
                    'adultDeaths': result.get('adultDeaths', 0),
                    'mortalityRate': result.get('mortalityRate', 0),
                    'naturalDeaths': result.get('naturalDeaths', 0),
                    'urbanDeaths': result.get('urbanDeaths', 0),
                    'diseaseDeaths': result.get('diseaseDeaths', 0),
                    'months': list(range(int(months) + 1)),
                    'totalPopulation': totalPopulation,
                    'sterilizedPopulation': sterilizedPopulation,
                    'unsterilizedPopulation': unsterilizedPopulation
                },
                'message': 'Calculation completed successfully'
            }

            return jsonify(response_data)

        except Exception as e:
            logSimulationError('unknown', str(e))
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        logSimulationError('unknown', str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/runParameterTests', methods=['POST'])
def runParameterTests():
    try:
        data = request.get_json()
        results = runParameterTests(data)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/downloadLogs', methods=['GET'])
def downloadLogs():
    """Download the calculation logs as a CSV file."""
    try:
        if not os.path.exists(CALC_FILE):
            return jsonify({'error': 'No logs found'}), 404

        # Read the CSV file
        with open(CALC_FILE, 'r', newline='') as f:
            csv_data = f.read()

        # Create the response with CSV data
        response = current_app.response_class(csv_data, mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=cat_colony_calculations.csv'
        
        return response
        
    except Exception as e:
        logger.error(f"Error downloading logs: {str(e)}")
        return jsonify({'error': 'The log download feature is currently unavailable. Please try again later.'}), 500

@bp.route('/flagScenario', methods=['POST', 'OPTIONS'])
def flagScenario():
    """Save a flagged scenario to a dedicated file with timestamp."""
    if request.method == 'OPTIONS':
        response = bp.make_default_options_response()
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400

        # Get the current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create a unique filename for this flagged scenario
        filename = f'flagged_scenario_{timestamp}.json'
        filepath = os.path.join(LOGS_DIR, filename)

        # Add metadata
        data['timestamp'] = timestamp
        data['ipAddress'] = request.remote_addr
        data['userAgent'] = request.headers.get('User-Agent', '')
        data['environment'] = current_app.config.get('ENV', 'production')
        data['calculatorVersion'] = data.get('version', '1.0.0')
        
        # Handle basic input parameters
        if 'inputs' in data:
            inputs = data['inputs']
            # Map frontend parameter names to backend names
            param_map = {
                'currentSize': 'initialColonySize',
                'sterilizedCount': 'alreadySterilized',
                'monthlysterilization': 'monthlySterilizationRate',
                'months': 'simulationLength'
            }
            # Convert empty strings to default values for basic parameters
            basic_params = {
                'currentSize': '10',
                'sterilizedCount': '0',
                'monthlysterilization': '1',
                'months': '12'
            }
            for frontend_key, default in basic_params.items():
                if frontend_key in inputs:
                    if not inputs[frontend_key] or inputs[frontend_key] == '':
                        inputs[frontend_key] = default
                    # If we have simulation results, prefer those values
                    backend_key = param_map.get(frontend_key)
                    if backend_key and 'simulationResults' in data:
                        sim_value = data['simulationResults'].get(backend_key)
                        if sim_value is not None and str(sim_value).strip():
                            inputs[frontend_key] = str(sim_value)
        
        # Ensure simulation results are properly captured
        if 'results' in data:
            results = data['results']
            # Convert empty strings to None for better JSON representation
            for key in results:
                if isinstance(results[key], str) and not results[key]:
                    results[key] = None
                elif isinstance(results[key], list) and not results[key]:
                    results[key] = []
            
            # Try to get simulation data from window.simulationResults if available
            if 'simulationResults' in data:
                sim_results = data['simulationResults']
                if isinstance(sim_results, dict):
                    # Population arrays from monthly data
                    monthly_data = sim_results.get('monthlyData', [])
                    results['monthlyData'] = [
                        {
                            'month': month['month'],
                            'total': month['total'],
                            'sterilized': month['sterilized'],
                            'unsterilized': month['unsterilized'],
                            'births': month['births'],
                            'natural_deaths': month['natural_deaths'],
                            'disease_deaths': month['disease_deaths'],
                            'urban_deaths': month['urban_deaths'],
                            'kitten_deaths': month['kitten_deaths'],
                            'adult_deaths': month['adult_deaths'],
                            'density_impact': month['density_impact'],
                            'resource_factor': month['resource_factor'],
                            'carrying_capacity': month['carrying_capacity']
                        }
                        for month in monthly_data
                    ] if monthly_data else []
                    
                    # Death statistics
                    results['naturalDeaths'] = int(sim_results.get('naturalDeaths', 0))
                    results['diseaseDeaths'] = int(sim_results.get('diseaseDeaths', 0))
                    results['urbanDeaths'] = int(sim_results.get('urbanDeaths', 0))
                    results['densityDeaths'] = int(sim_results.get('densityDeaths', 0))
            
            # Add any missing fields with appropriate default values
            expected_fields = {
                'finalPopulation': None,
                'populationChange': 0,
                'sterilizationRate': None,
                'totalCost': None,
                'totalDeaths': None,
                'kittenDeaths': None,
                'adultDeaths': None,
                'mortalityRate': None,
                'monthlyData': [],
                'monthlyDeaths': [],
                'monthlyBirths': [],
                'naturalDeaths': 0,
                'diseaseDeaths': 0,
                'urbanDeaths': 0,
                'densityDeaths': 0,
                'sterilizedPopulation': [],
                'unsterilizedPopulation': []
            }
            for field, default_value in expected_fields.items():
                if field not in results:
                    results[field] = default_value
        
        # Write the data to a JSON file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

        return jsonify({
            'success': True,
            'message': 'Scenario has been flagged and saved.',
            'filename': filename
        })

    except Exception as e:
        logger.error(f'Error in flagScenario: {str(e)}\n{traceback.format_exc()}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/clearLogs', methods=['POST'])
def clearLogs():
    try:
        if os.path.exists(CALC_FILE):
            # Keep the header row and delete the rest
            with open(CALC_FILE, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader)  # Get the header row
            
            with open(CALC_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)  # Write back only the header row
            
            return jsonify({'success': True, 'message': 'Logs cleared successfully'})
        return jsonify({'success': False, 'message': 'No logs found to clear'})
    except Exception as e:
        logger.error(f"Error clearing logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route("/saveCalculation", methods=['POST', 'OPTIONS'])
def saveCalculation():
    if request.method == 'OPTIONS':
        response = bp.make_default_options_response()
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        data = request.get_json(force=True)
        result = data.get('data', {})
        append = data.get('append', False)
        
        if not result:
            return jsonify({'error': 'No data received'}), 400

        # Create calculations.csv if it doesn't exist
        if not os.path.exists(CALC_FILE) or not append:
            with open(CALC_FILE, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=result.keys())
                writer.writeheader()

        # Append the result to calculations.csv
        with open(CALC_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=result.keys())
            writer.writerow(result)

        return jsonify({'message': 'Results saved successfully'})

    except Exception as e:
        logger.error(f'Error saving calculation: {str(e)}\n{traceback.format_exc()}')
        return jsonify({'error': str(e)}), 500
