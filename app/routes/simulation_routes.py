from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from app.tools.cat_simulation import DEFAULT_PARAMS, simulate_population
from app.tools.cat_simulation.monte_carlo import run_monte_carlo
from app.tools.cat_simulation.utils.logging_utils import log_debug
import csv
import io
from datetime import datetime
import os
import traceback
import json

bp = Blueprint('simulation', __name__)

# Set up logging
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)
CALC_FILE = os.path.join(LOGS_DIR, 'calculations.csv')

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

@bp.route("/calculate_population", methods=['POST', 'OPTIONS'])
def calculate_population():
    if request.method == 'OPTIONS':
        response = bp.make_default_options_response()
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        data = request.get_json(force=True)
        log_debug('INFO', f'Received request data: {data}')
        
        if not data:
            return jsonify({'error': 'No data received'}), 400

        # Parse input parameters
        current_size = int(float(data.get('initialColonySize', 10)))
        sterilized_count = int(float(data.get('alreadySterilized', 0)))
        monthly_sterilization = float(data.get('monthlySterilizationRate', 0))
        months = int(data.get('simulationLength', 12))
        sterilization_cost = float(data.get('sterilizationCost', 50))
        use_monte_carlo = bool(data.get('useMonteCarlo', False))
        
        log_debug('INFO', f'Parsed parameters: initialColonySize={current_size}, alreadySterilized={sterilized_count}, monthlySterilizationRate={monthly_sterilization}, simulationLength={months}, sterilizationCost={sterilization_cost}, useMonteCarlo={use_monte_carlo}')
        
        # Validate input
        if current_size < 1:
            return jsonify({'error': 'Current size must be at least 1'}), 400
        
        if sterilized_count > current_size:
            return jsonify({'error': 'Sterilized count cannot exceed current size'}), 400
        
        if sterilized_count < 0:
            return jsonify({'error': 'Sterilized count cannot be negative'}), 400
        
        if monthly_sterilization < 0:
            return jsonify({'error': 'Monthly sterilization cannot be negative'}), 400
        
        if months < 1 or months > 120:
            return jsonify({'error': 'Months must be between 1 and 120'}), 400
        
        if sterilization_cost > 1000:
            return jsonify({'error': 'Sterilization cost cannot exceed $1000'}), 400

        # Initialize params with defaults
        params = DEFAULT_PARAMS.copy()

        # Update with any custom params from the request
        custom_params = data.get('params', {})
        if isinstance(custom_params, dict):
            # Convert all custom params to float
            for key, value in custom_params.items():
                try:
                    custom_params[key] = float(value)
                except (TypeError, ValueError):
                    return jsonify({'error': f'Invalid value for parameter {key}'}), 400
            params.update(custom_params)

        # Add or update top-level parameters with type conversion
        try:
            top_level_params = {
                'territorySize': float(data.get('territorySize', 1000)),
                'densityImpactThreshold': float(data.get('densityImpactThreshold', 1.2)),
                'baseFoodCapacity': float(data.get('baseFoodCapacity', 0.9)),
                'foodScalingFactor': float(data.get('foodScalingFactor', 0.8)),
                'monthlyAbandonment': float(data.get('monthlyAbandonment', 2.0))
            }
            params.update(top_level_params)
        except (TypeError, ValueError) as e:
            return jsonify({'error': f'Invalid value for top-level parameter: {str(e)}'}), 400

        # Ensure all params are float
        for key in params:
            if not isinstance(params[key], (int, float)):
                try:
                    params[key] = float(params[key])
                except (TypeError, ValueError):
                    return jsonify({'error': f'Invalid value for parameter {key}'}), 400

        # Monte Carlo parameters with type conversion
        if use_monte_carlo:
            try:
                log_debug('INFO', 'Setting up Monte Carlo simulation')
                monte_carlo_runs = int(data.get('monteCarloRuns', 500))
                variation_coefficient = min(float(data.get('variationCoefficient', 0.1)), 0.5)  # Cap at 0.5
                
                # Validate Monte Carlo parameters
                if monte_carlo_runs < 1:
                    return jsonify({'error': 'Number of simulations must be at least 1'}), 400
                if variation_coefficient <= 0:
                    return jsonify({'error': 'Variation coefficient must be positive'}), 400
                
                log_debug('INFO', f'Monte Carlo parameters: sims={monte_carlo_runs}, var_coef={variation_coefficient}')
                
                # Add Monte Carlo specific parameters to params
                params.update({
                    'numSimulations': monte_carlo_runs,
                    'variationCoefficient': variation_coefficient,
                    'kittenMaturityMonths': float(params.get('kittenMaturityMonths', 5)),
                    'peakBreedingMonth': int(params.get('peakBreedingMonth', 4)),
                    'densityImpactThreshold': float(params.get('densityImpactThreshold', 1.2)),
                    'baseBreedingSuccess': float(params.get('baseBreedingSuccess', 0.95)),
                    'ageBreedingFactor': float(params.get('ageBreedingFactor', 0.06)),
                    'stressImpact': float(params.get('stressImpact', 0.12))
                })
            except (TypeError, ValueError) as e:
                return jsonify({'error': f'Invalid Monte Carlo parameters: {str(e)}'}), 400

        try:
            if use_monte_carlo:
                log_debug('INFO', 'Running Monte Carlo simulation')
                try:
                    result = run_monte_carlo(
                        params=params,
                        current_size=current_size,
                        months=months,
                        sterilized_count=sterilized_count,
                        monthly_sterilization=monthly_sterilization,
                        num_simulations=monte_carlo_runs
                    )
                except Exception as e:
                    log_debug('ERROR', f'Monte Carlo simulation error: {str(e)}')
                    return jsonify({'error': str(e)}), 500
            else:
                log_debug('INFO', 'Running regular simulation')
                try:
                    result = simulate_population(
                        params=params,
                        current_size=current_size,
                        months=months,
                        sterilized_count=sterilized_count,
                        monthly_sterilization=monthly_sterilization,
                        use_monte_carlo=use_monte_carlo
                    )
                except Exception as e:
                    log_debug('ERROR', f'Simulation error: {str(e)}')
                    return jsonify({'error': str(e)}), 500

            # Calculate costs
            total_sterilizations = result['total_sterilizations']
            total_cost = total_sterilizations * sterilization_cost

            # Prepare data for logging
            log_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'initialColonySize': current_size,
                'alreadySterilized': sterilized_count,
                'monthlySterilizationRate': monthly_sterilization,
                'simulationLength': months,
                'sterilizationCost': sterilization_cost,
                'useMonteCarlo': use_monte_carlo,
                'finalPopulation': result['final_population'],
                'finalSterilized': result['final_sterilized'],
                'totalSterilizations': total_sterilizations,
                'totalCost': total_cost,
                'populationGrowth': result['population_growth'],
                'monthlyPopulations': ','.join(map(str, result['monthly_populations'])),
                'monthlySterilized': ','.join(map(str, result['monthly_sterilized'])),
                'params': json.dumps(params)
            }

            # Add Monte Carlo specific results if applicable
            if use_monte_carlo:
                log_data.update({
                    'numSimulations': params['numSimulations'],
                    'variationCoefficient': params['variationCoefficient'],
                    'confidenceIntervalLower': result.get('confidence_interval_lower', ''),
                    'confidenceIntervalUpper': result.get('confidence_interval_upper', ''),
                    'standardDeviation': result.get('standard_deviation', '')
                })

            # Log the calculation
            try:
                log_debug('INFO', f"Writing calculation data to log file: {CALC_FILE}")
                log_debug('INFO', f"Current working directory: {os.getcwd()}")
                log_debug('INFO', f"Log entry: {log_data}")
                
                # Create logs directory if it doesn't exist
                os.makedirs(os.path.dirname(CALC_FILE), exist_ok=True)

                # Check if file exists and write header if it doesn't
                file_exists = os.path.isfile(CALC_FILE)
                with open(CALC_FILE, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=log_data.keys())
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow(log_data)
                
                log_debug('INFO', "Successfully wrote calculation data to log file")
            except Exception as e:
                log_debug('ERROR', f"Error writing to log file: {str(e)}")
                log_debug('ERROR', traceback.format_exc())
                # Continue execution even if logging fails
                pass

            # Prepare response
            response_data = {
                'success': True,
                'result': {
                    'finalPopulation': result['final_population'],
                    'finalSterilized': result['final_sterilized'],
                    'totalSterilizations': total_sterilizations,
                    'totalCost': total_cost,
                    'populationGrowth': result['population_growth'],
                    'monthlyPopulations': result['monthly_populations'],
                    'monthlySterilized': result['monthly_sterilized'],
                    'monthlyKittens': result['monthly_kittens'],
                    'monthlyReproductive': result['monthly_reproductive'],
                    'totalDeaths': result['total_deaths'],
                    'kittenDeaths': result['kitten_deaths'],
                    'adultDeaths': result['adult_deaths'],
                    'naturalDeaths': result['natural_deaths'],
                    'urbanDeaths': result['urban_deaths'],
                    'diseaseDeaths': result['disease_deaths'],
                    'monthlyDeathsKittens': result['monthly_deaths_kittens'],
                    'monthlyDeathsAdults': result['monthly_deaths_adults'],
                    'monthlyDeathsNatural': result['monthly_deaths_natural'],
                    'monthlyDeathsUrban': result['monthly_deaths_urban'],
                    'monthlyDeathsDisease': result['monthly_deaths_disease'],
                    'monthlyDeathsOther': result['monthly_deaths_other']
                }
            }

            # Add Monte Carlo specific results if applicable
            if use_monte_carlo:
                response_data['result'].update({
                    'confidenceInterval': [
                        result['confidence_interval'][0],
                        result['confidence_interval'][1]
                    ],
                    'standardDeviation': result['standard_deviation'],
                    'allResults': result.get('all_results', None)
                })

            return jsonify(response_data)

        except Exception as e:
            log_debug('ERROR', f'Simulation error: {str(e)}')
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        log_debug('ERROR', f'Unexpected error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@bp.route('/run_parameter_tests', methods=['POST'])
def run_parameter_tests():
    try:
        data = request.get_json()
        results = run_monte_carlo(data)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/download_logs', methods=['GET'])
def download_logs():
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
        log_debug('ERROR', f"Error downloading logs: {str(e)}")
        return jsonify({'error': 'The log download feature is currently unavailable. Please try again later.'}), 500

@bp.route('/flag_scenario', methods=['POST', 'OPTIONS'])
def flag_scenario():
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
        
        # Write the data to a JSON file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

        return jsonify({
            'success': True,
            'message': 'Scenario has been flagged and saved.',
            'filename': filename
        })

    except Exception as e:
        log_debug('ERROR', f'Error in flag_scenario: {str(e)}\n{traceback.format_exc()}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/clear_logs', methods=['POST'])
def clear_logs():
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
        log_debug('ERROR', f"Error clearing logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route("/save_calculation", methods=['POST', 'OPTIONS'])
def save_calculation():
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
        log_debug('ERROR', f'Error saving calculation: {str(e)}\n{traceback.format_exc()}')
        return jsonify({'error': str(e)}), 500
