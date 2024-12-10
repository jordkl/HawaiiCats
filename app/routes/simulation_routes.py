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
                        'standard_deviation': summary['population']['std']
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
                    'monthly_reproductive': result['monthly_reproductive']
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

@bp.route('/download_logs')
def download_logs():
    try:
        # ... (log download logic)
        return send_file(
            io.BytesIO(csv_data.encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'cat_calculations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    except Exception as e:
        return str(e), 500

@bp.route('/flag_scenario', methods=['POST'])
def flag_scenario():
    try:
        # ... (scenario flagging logic)
        return jsonify({"message": "Scenario flagged successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/clear_logs', methods=['POST'])
def clear_logs():
    try:
        # ... (log clearing logic)
        return jsonify({"message": "Logs cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
