from flask import Flask, render_template, request, jsonify, redirect, send_file
from flask_cors import CORS
import logging
import traceback
from cat_simulation import DEFAULT_PARAMS, simulate_population
from cat_simulation.monte_carlo import run_monte_carlo
from cat_simulation.utils.logging_utils import setup_logging, log_debug
import csv
import os
from datetime import datetime
import io
import re

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

# Configure CORS
ALLOWED_ORIGINS = [
    "https://hawaiicats.org",
    "https://hawaiicats.com",
    "http://hawaiicats.com",
    "http://localhost:5001",
    "http://localhost:5000",
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5000",
    "http://192.168.1.169:5001"
]

CORS(app, resources={
    r"/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Set up logging
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')  # Use logs directory in project root
os.makedirs(LOGS_DIR, exist_ok=True)
CALC_FILE = os.path.join(LOGS_DIR, 'calculations.csv')
FLAGGED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flagged_scenarios')  # Directory for flagged scenarios
os.makedirs(FLAGGED_DIR, exist_ok=True)
DEBUG_FILE = os.path.join(LOGS_DIR, 'debug.log')
setup_logging(LOGS_DIR)
logger = logging.getLogger('debug')

# Add CORS headers
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ALLOWED_ORIGINS:
        response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

@app.route('/about')
def about():
    try:
        return render_template('about.html')
    except Exception as e:
        log_debug('ERROR', f"Error in about route: {str(e)}")
        log_debug('ERROR', traceback.format_exc())
        return f"Internal Server Error: {str(e)}", 500

@app.route("/calculate_population", methods=['POST', 'OPTIONS'])
def calculate_population():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
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

        # Run simulation
        try:
            if use_monte_carlo:
                try:
                    summary, all_results = run_monte_carlo(
                        base_params=params,
                        current_size=current_size,
                        months=months,
                        sterilized_count=sterilized_count,
                        monthly_sterilization=monthly_sterilization,
                        num_simulations=num_simulations,
                        variation_coefficient=variation_coefficient
                    )
                    
                    if not summary or not all_results:
                        return jsonify({'error': 'Monte Carlo simulation failed to generate results'}), 500
                    
                    if len(all_results) < num_simulations * 0.5:  # Require at least 50% success rate
                        return jsonify({'error': 'Too few successful Monte Carlo simulations. Try reducing the number of simulations.'}), 500
                        
                    # Use median simulation for visualization
                    result = all_results[len(all_results)//2]  # Middle simulation
                    
                    # Add Monte Carlo summary data
                    result['monte_carlo_data'] = {
                        'final_population': {
                            'lower': float(summary['population']['ci_lower']),
                            'upper': float(summary['population']['ci_upper'])
                        },
                        'sterilization_rate': {
                            'lower': (float(summary['sterilized']['ci_lower']) / float(summary['population']['ci_lower']) * 100) if float(summary['population']['ci_lower']) > 0 else 0,
                            'upper': (float(summary['sterilized']['ci_upper']) / float(summary['population']['ci_upper']) * 100) if float(summary['population']['ci_upper']) > 0 else 0
                        },
                        'population_change': {
                            'lower': float(summary['population']['ci_lower']) - current_size,
                            'upper': float(summary['population']['ci_upper']) - current_size
                        },
                        'mortality': summary['mortality']
                    }
                    
                    result['monte_carlo_summary'] = summary
                    
                except Exception as e:
                    logger.error(f"Monte Carlo simulation error: {str(e)}")
                    logger.error(traceback.format_exc())
                    return jsonify({'error': 'Monte Carlo simulation failed. Try reducing the number of simulations.'}), 500
                
            else:
                result = simulate_population(
                    params=params,
                    current_size=current_size,
                    months=months,
                    sterilized_count=sterilized_count,
                    monthly_sterilization=monthly_sterilization
                )
            
            if result is None:
                log_debug('ERROR', "Empty result from simulate_population")
                return jsonify({'error': 'Calculation failed - empty result'}), 500
                
            log_debug('INFO', f'Simulation result: {result}')
            
            # Ensure all mortality arrays are initialized
            result['monthly_deaths_kittens'] = result.get('monthly_deaths_kittens', [0] * months)
            result['monthly_deaths_adults'] = result.get('monthly_deaths_adults', [0] * months)
            result['monthly_deaths_natural'] = result.get('monthly_deaths_natural', [0] * months)
            result['monthly_deaths_urban'] = result.get('monthly_deaths_urban', [0] * months)
            result['monthly_deaths_disease'] = result.get('monthly_deaths_disease', [0] * months)
            
            # Calculate total deaths
            total_deaths = sum(result['monthly_deaths_natural']) + \
                         sum(result['monthly_deaths_urban']) + \
                         sum(result['monthly_deaths_disease'])
            kitten_deaths = sum(result['monthly_deaths_kittens'])
            adult_deaths = sum(result['monthly_deaths_adults'])
            
            # Add summary statistics
            result['total_deaths'] = total_deaths
            result['kitten_deaths'] = kitten_deaths
            result['adult_deaths'] = adult_deaths
            result['natural_deaths'] = sum(result['monthly_deaths_natural'])
            result['urban_deaths'] = sum(result['monthly_deaths_urban'])
            result['disease_deaths'] = sum(result['monthly_deaths_disease'])
            
            log_debug('INFO', f'Mortality statistics: {result}')
            
            # Log results to CSV
            row_data = {
                # Input parameters
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'current_size': current_size,
                'sterilized_count': sterilized_count,
                'monthly_sterilization': monthly_sterilization,
                'months': months,
                
                # Core breeding parameters
                'breeding_rate': params['breeding_rate'],
                'kittens_per_litter': params['kittens_per_litter'],
                'litters_per_year': params['litters_per_year'],
                'kitten_survival_rate': params['kitten_survival_rate'],
                'female_ratio': params['female_ratio'],
                'adult_survival_rate': params['adult_survival_rate'],
                'kitten_maturity_months': params['kitten_maturity_months'],
                
                # Cost parameters
                'sterilization_cost': params['sterilization_cost'],
                'kitten_discount': '',  # Not used currently
                
                # Seasonal factors
                'seasonal_breeding_amplitude': params['seasonal_breeding_amplitude'],
                'peak_breeding_month': params['peak_breeding_month'],
                
                # Resource factors
                'base_food_capacity': params['base_food_capacity'],
                'food_scaling_factor': params['food_scaling_factor'],
                'water_availability': params['water_availability'],
                'shelter_quality': params['shelter_quality'],
                
                # Environmental risks
                'urban_risk': params['urban_risk'],
                'disease_risk': params['disease_risk'],
                'natural_risk': params['natural_risk'],
                
                # Human interaction factors
                'caretaker_support': params['caretaker_support'],
                'feeding_consistency': params['feeding_consistency'],
                'human_interference': params.get('human_interference', 0.5),
                
                # Colony density factors
                'territory_size': params['territory_size'],
                'density_impact_threshold': params['density_impact_threshold'],
                
                # Abandonment factors
                'monthly_abandonment': params['monthly_abandonment'],
                'abandoned_sterilized_ratio': params['abandoned_sterilized_ratio'],
                
                # Results - Final State
                'final_population': result['final_population'],
                'final_sterilized': result['final_sterilized'],
                'final_reproductive': result['final_reproductive'],
                'final_kittens': result['final_kittens'],
                'total_cost': result['total_cost'],
                'total_deaths': result['total_deaths'],
                'kitten_deaths': result['kitten_deaths'],
                'adult_deaths': result['adult_deaths'],
                'natural_deaths': result['natural_deaths'],
                'urban_deaths': result['urban_deaths'],
                'disease_deaths': result['disease_deaths'],
                
                # Monthly Data Points
                'monthly_populations': str(result['monthly_populations']),
                'monthly_sterilized': str(result['monthly_sterilized']),
                'monthly_reproductive': str(result['monthly_reproductive']),
                'monthly_kittens': str(result['monthly_kittens']),
                'monthly_deaths_kittens': str(result.get('monthly_deaths_kittens', [])),
                'monthly_deaths_adults': str(result.get('monthly_deaths_adults', [])),
                'monthly_deaths_natural': str(result.get('monthly_deaths_natural', [])),
                'monthly_deaths_urban': str(result.get('monthly_deaths_urban', [])),
                'monthly_deaths_disease': str(result.get('monthly_deaths_disease', [])),
                'monthly_deaths_other': str(result.get('monthly_deaths_other', [0] * len(result['monthly_populations']))),
                'monthly_costs': str(result.get('monthly_costs', [])),
                
                # Population Density Metrics
                'average_density': result['average_density'],
                'max_density': result['max_density'],
                'months_over_threshold': result.get('months_over_threshold', '')
            }
            
            try:
                log_debug('INFO', f"Writing calculation data to log file: {CALC_FILE}")
                log_debug('INFO', f"Current working directory: {os.getcwd()}")
                log_debug('INFO', f"Log entry: {row_data}")
                
                # Make sure logs directory exists
                os.makedirs(os.path.dirname(CALC_FILE), exist_ok=True)
                
                # Check if file exists and is empty
                is_new_file = not os.path.exists(CALC_FILE) or os.path.getsize(CALC_FILE) == 0
                
                # Open file in append mode and write data
                with open(CALC_FILE, 'a', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        'timestamp', 'current_size', 'sterilized_count', 'monthly_sterilization', 'months',
                        'breeding_rate', 'kittens_per_litter', 'litters_per_year', 'kitten_survival_rate',
                        'female_ratio', 'adult_survival_rate', 'kitten_maturity_months', 'sterilization_cost',
                        'seasonal_breeding_amplitude', 'peak_breeding_month', 'base_food_capacity',
                        'food_scaling_factor', 'water_availability', 'shelter_quality', 'urban_risk',
                        'disease_risk', 'natural_risk', 'caretaker_support', 'feeding_consistency',
                        'territory_size', 'density_impact_threshold', 'monthly_abandonment',
                        'final_population', 'final_sterilized', 'final_reproductive', 'final_kittens',
                        'total_cost', 'total_deaths', 'kitten_deaths', 'adult_deaths', 'natural_deaths',
                        'urban_deaths', 'disease_deaths', 'monthly_populations', 'monthly_sterilized',
                        'monthly_reproductive', 'monthly_kittens', 'monthly_deaths_kittens', 'monthly_deaths_adults',
                        'monthly_deaths_natural', 'monthly_deaths_urban', 'monthly_deaths_disease',
                        'monthly_deaths_other', 'monthly_costs', 'average_density', 'max_density',
                        'months_over_threshold'
                    ])
                    if is_new_file:
                        log_debug('INFO', "Writing CSV headers")
                        writer.writeheader()
                    writer.writerow(row_data)
                    f.flush()
                    os.fsync(f.fileno())
                
                # Verify the write was successful
                if os.path.exists(CALC_FILE):
                    log_debug('INFO', f"Log file size after write: {os.path.getsize(CALC_FILE)} bytes")
                    with open(CALC_FILE, 'r') as f:
                        lines = f.readlines()
                        log_debug('INFO', f"Log file now contains {len(lines)} lines")
                else:
                    log_debug('ERROR', "Log file does not exist after write attempt!")
            
            except Exception as e:
                log_debug('ERROR', f"Error writing to log file: {str(e)}")
                log_debug('ERROR', f"Current working directory: {os.getcwd()}")
                log_debug('ERROR', traceback.format_exc())
                # Continue with calculation even if logging fails

            # Return simulation results
            response_data = {
                'success': True,
                'result': {
                    'final_population': result['final_population'],
                    'final_sterilized': result['final_sterilized'],
                    'final_reproductive': result['final_reproductive'],
                    'final_kittens': result['final_kittens'],
                    'total_cost': result['total_cost'],
                    'total_deaths': result['total_deaths'],
                    'kitten_deaths': result['kitten_deaths'],
                    'adult_deaths': result['adult_deaths'],
                    'natural_deaths': result['natural_deaths'],
                    'urban_deaths': result['urban_deaths'],
                    'disease_deaths': result['disease_deaths'],
                    
                    # Monthly data as arrays, not strings
                    'monthly_data': result['monthly_populations'],  # Add this for frontend compatibility
                    'monthly_populations': result['monthly_populations'],
                    'monthly_sterilized': result['monthly_sterilized'],
                    'monthly_reproductive': result['monthly_reproductive'],
                    'monthly_kittens': result['monthly_kittens'],
                    'monthly_deaths_kittens': result.get('monthly_deaths_kittens', []),
                    'monthly_deaths_adults': result.get('monthly_deaths_adults', []),
                    'monthly_deaths_natural': result.get('monthly_deaths_natural', []),
                    'monthly_deaths_urban': result.get('monthly_deaths_urban', []),
                    'monthly_deaths_disease': result.get('monthly_deaths_disease', []),
                    'monthly_deaths_other': result.get('monthly_deaths_other', [0] * len(result['monthly_populations'])),
                    'monthly_costs': result.get('monthly_costs', [])
                }
            }
            
            # Add Monte Carlo data if available
            if 'monte_carlo_data' in result:
                response_data['result']['monte_carlo_data'] = result['monte_carlo_data']

            return jsonify(response_data)
        
        except Exception as e:
            log_debug('ERROR', f"Error in population calculation: {str(e)}")
            log_debug('ERROR', traceback.format_exc())
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        log_debug('ERROR', f"Error processing request: {str(e)}")
        log_debug('ERROR', traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/run_parameter_tests', methods=['POST'])
def run_parameter_tests():
    try:
        # Run parameter tests
        csv_filename = simulation.run_parameter_tests()
        return jsonify({'success': True, 'csv_file': csv_filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download_logs', methods=['GET', 'OPTIONS'])
def download_logs():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        filename = request.args.get('filename')
        log_debug('INFO', f"Download logs request received for filename: {filename}")
        log_debug('INFO', f"Current working directory: {os.getcwd()}")
        
        if filename:
            # Handle specific file download
            file_path = os.path.join(LOGS_DIR, filename)
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True)
            else:
                return jsonify({'error': 'File not found'}), 404
        else:
            # Default to calculations.csv
            log_debug('INFO', f"Looking for calculations file at: {CALC_FILE}")
            if os.path.exists(CALC_FILE):
                return send_file(CALC_FILE, as_attachment=True)
            else:
                return jsonify({'error': 'Calculations file not found'}), 404
                
    except Exception as e:
        log_debug('ERROR', f"Error in download_logs: {str(e)}")
        log_debug('ERROR', traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route("/flag_scenario", methods=['POST', 'OPTIONS'])
def flag_scenario():
    """Save a flagged scenario to a dedicated file with timestamp."""
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
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
        flagged_file = os.path.join(FLAGGED_DIR, f'flagged_scenario_{timestamp}.csv')
        
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

@app.route('/clear_logs', methods=['POST', 'OPTIONS'])
def clear_logs():
    """Clear the calculations log file."""
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    try:
        # Create or truncate the calculations file
        with open(CALC_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'current_size', 'sterilized_count', 'monthly_sterilization', 'months',
                           'breeding_rate', 'kittens_per_litter', 'litters_per_year', 'kitten_survival_rate',
                           'female_ratio', 'adult_survival_rate', 'kitten_maturity_months', 'sterilization_cost',
                           'seasonal_breeding_amplitude', 'peak_breeding_month', 'base_food_capacity',
                           'food_scaling_factor', 'water_availability', 'shelter_quality', 'urban_risk',
                           'disease_risk', 'natural_risk', 'caretaker_support', 'feeding_consistency',
                           'territory_size', 'density_impact_threshold', 'monthly_abandonment',
                           'final_population', 'final_sterilized', 'final_reproductive', 'final_kittens',
                           'total_cost', 'total_deaths', 'kitten_deaths', 'adult_deaths', 'natural_deaths',
                           'urban_deaths', 'disease_deaths'])
        return jsonify({'message': 'Logs cleared successfully'})
    except Exception as e:
        log_debug('ERROR', f"Error clearing logs: {str(e)}")
        log_debug('ERROR', traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        log_debug('ERROR', f"Error starting Flask app: {str(e)}")
        log_debug('ERROR', traceback.format_exc())
