from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from tools.cat_simulation import DEFAULT_PARAMS, simulate_population
from tools.cat_simulation.monte_carlo import run_monte_carlo
from tools.cat_simulation.utils.logging_utils import log_debug
import csv
import io
from datetime import datetime
import os
import traceback

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
    return render_template('calculator.html')

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

        # Parse and validate basic parameters
        try:
            current_size = int(float(data.get('current_size', 10)))
            sterilized_count = int(float(data.get('sterilized_count', 0)))
            monthly_sterilization = int(float(data.get('monthly_sterilization', 0)))
            months = int(float(data.get('months', 12)))
            sterilization_cost = float(data.get('sterilization_cost', 50.0))
            
            # Basic validation
            if current_size < 1:
                return jsonify({'error': 'Current size must be at least 1'}), 400
            if sterilized_count < 0:
                return jsonify({'error': 'Sterilized count cannot be negative'}), 400
            if sterilized_count > current_size:
                return jsonify({'error': 'Sterilized count cannot exceed current size'}), 400
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
                    'territory_size': float(data.get('territory_size', 1000)),
                    'density_impact_threshold': float(data.get('density_impact_threshold', 1.2)),
                    'base_food_capacity': float(data.get('base_food_capacity', 0.9)),
                    'food_scaling_factor': float(data.get('food_scaling_factor', 0.8)),
                    'monthly_abandonment': float(data.get('monthly_abandonment', 2.0))
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
            try:
                use_monte_carlo = bool(data.get('use_monte_carlo', False))
                if use_monte_carlo:
                    num_simulations = min(int(float(data.get('num_simulations', 100))), 1000)  # Cap at 1000
                    variation_coefficient = min(float(data.get('variation_coefficient', 0.1)), 0.5)  # Cap at 0.5
                    
                    # Validate Monte Carlo parameters
                    if num_simulations < 1:
                        return jsonify({'error': 'Number of simulations must be at least 1'}), 400
                    if variation_coefficient <= 0:
                        return jsonify({'error': 'Variation coefficient must be positive'}), 400
                    
                    # Add Monte Carlo specific parameters to params
                    params.update({
                        'num_simulations': num_simulations,
                        'variation_coefficient': variation_coefficient,
                        'kitten_maturity_months': float(params.get('kitten_maturity_months', 5)),
                        'peak_breeding_month': int(params.get('peak_breeding_month', 4)),
                        'density_impact_threshold': float(params.get('density_impact_threshold', 1.2)),
                        'base_breeding_success': float(params.get('base_breeding_success', 0.95)),
                        'age_breeding_factor': float(params.get('age_breeding_factor', 0.06)),
                        'stress_impact': float(params.get('stress_impact', 0.12))
                    })
            except (TypeError, ValueError) as e:
                return jsonify({'error': f'Invalid Monte Carlo parameters: {str(e)}'}), 400

        except (TypeError, ValueError) as e:
            return jsonify({'error': f'Invalid parameter value: {str(e)}'}), 400

        try:
            if use_monte_carlo:
                try:
                    summary, all_results = run_monte_carlo(
                        base_params=params,
                        current_size=current_size,
                        sterilized_count=sterilized_count,
                        monthly_sterilization=monthly_sterilization,
                        months=months,
                        num_simulations=num_simulations,
                        variation_coefficient=variation_coefficient
                    )
                    # Convert Monte Carlo summary to match regular simulation format
                    result = {
                        'final_population': summary['population']['mean'],
                        'final_sterilized': summary['sterilized']['mean'],
                        'total_sterilizations': monthly_sterilization * months,
                        'total_cost': summary['cost']['mean'],
                        'population_growth': summary['population']['mean'] - current_size,
                        'monthly_populations': [stat['mean'] for stat in summary['monthly_stats']],
                        'monthly_sterilized': [stat['sterilized_mean'] for stat in summary['monthly_stats']],
                        'monthly_reproductive': [stat['reproductive_mean'] for stat in summary['monthly_stats']],
                        'monthly_kittens': [stat['kittens_mean'] for stat in summary['monthly_stats']],
                        'confidence_interval': [
                            summary['population']['ci_lower'],
                            summary['population']['ci_upper']
                        ],
                        'standard_deviation': summary['population']['std'],
                        # Add mortality statistics
                        'total_deaths': summary['mortality']['total']['mean'],
                        'kitten_deaths': summary['mortality']['kittens']['mean'],
                        'adult_deaths': summary['mortality']['adults']['mean'],
                        'natural_deaths': summary['mortality'].get('natural', {}).get('mean', 0),
                        'urban_deaths': summary['mortality'].get('urban', {}).get('mean', 0),
                        'disease_deaths': summary['mortality'].get('disease', {}).get('mean', 0),
                        'monthly_deaths_kittens': [],  # Placeholder for monthly stats
                        'monthly_deaths_adults': [],   # Placeholder for monthly stats
                        'monthly_deaths_natural': [],  # Placeholder for monthly stats
                        'monthly_deaths_urban': [],    # Placeholder for monthly stats
                        'monthly_deaths_disease': [],  # Placeholder for monthly stats
                        'monthly_deaths_other': []     # Placeholder for monthly stats
                    }
                except Exception as e:
                    log_debug('ERROR', f"Error in Monte Carlo simulation: {str(e)}")
                    log_debug('ERROR', traceback.format_exc())
                    return jsonify({'error': str(e)}), 500
            else:
                result = simulate_population(
                    params=params,
                    current_size=current_size,
                    sterilized_count=sterilized_count,
                    monthly_sterilization=monthly_sterilization,
                    months=months
                )

            # Calculate costs
            total_sterilizations = result['total_sterilizations']
            total_cost = total_sterilizations * sterilization_cost

            # Prepare data for logging
            row_data = {
                # Input parameters
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'current_size': current_size,
                'sterilized_count': sterilized_count,
                'monthly_sterilization': monthly_sterilization,
                'months': months,
                'sterilization_cost': sterilization_cost,
                'use_monte_carlo': use_monte_carlo,
                
                # Results
                'final_population': result['final_population'],
                'final_sterilized': result['final_sterilized'],
                'total_sterilizations': total_sterilizations,
                'total_cost': total_cost,
                'population_growth': result['population_growth'],
                'monthly_populations': ','.join(map(str, result['monthly_populations'])),
                'monthly_sterilized': ','.join(map(str, result['monthly_sterilized'])),
                
                # Parameters used
                'params': str(params)
            }

            # Add Monte Carlo specific results if applicable
            if use_monte_carlo:
                row_data.update({
                    'num_simulations': params['num_simulations'],
                    'variation_coefficient': params['variation_coefficient'],
                    'confidence_interval_lower': result.get('confidence_interval_lower', ''),
                    'confidence_interval_upper': result.get('confidence_interval_upper', ''),
                    'standard_deviation': result.get('standard_deviation', '')
                })

            # Log the calculation
            try:
                log_debug('INFO', f"Writing calculation data to log file: {CALC_FILE}")
                log_debug('INFO', f"Current working directory: {os.getcwd()}")
                log_debug('INFO', f"Log entry: {row_data}")
                
                # Create logs directory if it doesn't exist
                os.makedirs(os.path.dirname(CALC_FILE), exist_ok=True)

                # Check if file exists and write header if it doesn't
                file_exists = os.path.isfile(CALC_FILE)
                with open(CALC_FILE, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=row_data.keys())
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow(row_data)
                
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
                    'final_population': result['final_population'],
                    'final_sterilized': result['final_sterilized'],
                    'total_sterilizations': total_sterilizations,
                    'total_cost': total_cost,
                    'population_growth': result['population_growth'],
                    'monthly_populations': result['monthly_populations'],
                    'monthly_sterilized': result['monthly_sterilized'],
                    'monthly_kittens': result['monthly_kittens'],
                    'monthly_reproductive': result['monthly_reproductive'],
                    'total_deaths': result['total_deaths'],
                    'kitten_deaths': result['kitten_deaths'],
                    'adult_deaths': result['adult_deaths'],
                    'natural_deaths': result['natural_deaths'],
                    'urban_deaths': result['urban_deaths'],
                    'disease_deaths': result['disease_deaths'],
                    'monthly_deaths_kittens': result['monthly_deaths_kittens'],
                    'monthly_deaths_adults': result['monthly_deaths_adults'],
                    'monthly_deaths_natural': result['monthly_deaths_natural'],
                    'monthly_deaths_urban': result['monthly_deaths_urban'],
                    'monthly_deaths_disease': result['monthly_deaths_disease'],
                    'monthly_deaths_other': result['monthly_deaths_other']
                }
            }

            # Add Monte Carlo specific results if applicable
            if use_monte_carlo:
                response_data['result'].update({
                    'confidence_interval': [
                        result['confidence_interval'][0],
                        result['confidence_interval'][1]
                    ],
                    'standard_deviation': result['standard_deviation'],
                    'all_results': all_results if 'all_results' in locals() else None
                })

            return jsonify(response_data)

        except Exception as e:
            log_debug('ERROR', f"Error in population calculation: {str(e)}")
            log_debug('ERROR', traceback.format_exc())
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        log_debug('ERROR', f"Error processing request: {str(e)}")
        log_debug('ERROR', traceback.format_exc())
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
        data = request.get_json(force=True)
        if not data or 'userNote' not in data:
            return jsonify({'error': 'No user note provided'}), 400
            
        user_note = data['userNote'].strip()
        if not user_note:
            return jsonify({'error': 'User note cannot be empty'}), 400

        # Read the last calculation and headers from CALC_FILE
        headers = None
        last_calculation = None
        try:
            with open(CALC_FILE, 'r', newline='') as f:
                reader = csv.reader(f)
                headers = next(reader)  # Get header row
                for row in reader:
                    last_calculation = row
        except Exception as e:
            return jsonify({'error': 'No calculations found to flag'}), 404

        if not last_calculation or not headers:
            return jsonify({'error': 'No calculations found to flag'}), 404

        # Generate timestamp and filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        flagged_dir = os.path.join(os.path.dirname(CALC_FILE), 'flagged_scenarios')
        os.makedirs(flagged_dir, exist_ok=True)
        flagged_file = os.path.join(flagged_dir, f'flagged_scenario_{timestamp}.csv')
        
        with open(flagged_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write headers including the new ones
            all_headers = headers + ['user_note', 'flag_timestamp']
            writer.writerow(all_headers)
            
            # Add the note and current timestamp to the calculation
            flagged_row = last_calculation + [user_note, timestamp]
            writer.writerow(flagged_row)
            
        log_debug('INFO', f'Flagged scenario saved with note: {user_note} to file: {flagged_file}')
        return jsonify({'success': True})
        
    except Exception as e:
        log_debug('ERROR', f"Error in flag_scenario: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

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
