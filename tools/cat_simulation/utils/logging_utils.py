import logging
import os
from datetime import datetime
import psutil
import json

def setup_logging(log_dir='/tmp/hawaiicats_logs'):
    """Set up logging configuration with separate handlers for calculations and debug logs."""
    try:
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Create formatters
        calc_formatter = logging.Formatter('%(message)s')
        debug_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Set up calculation CSV handler
        calc_path = os.path.join(log_dir, 'calculations.csv')
        calc_handler = logging.FileHandler(calc_path)
        calc_handler.setFormatter(calc_formatter)
        calc_handler.setLevel(logging.INFO)
        
        # Set up debug log handler
        debug_path = os.path.join(log_dir, 'debug.log')
        debug_handler = logging.FileHandler(debug_path)
        debug_handler.setFormatter(debug_formatter)
        debug_handler.setLevel(logging.DEBUG)
        
        # Set up console handler for errors
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(debug_formatter)
        console_handler.setLevel(logging.ERROR)  # Only show errors in console
        
        # Create separate loggers
        calc_logger = logging.getLogger('calculations')
        calc_logger.setLevel(logging.INFO)
        calc_logger.addHandler(calc_handler)
        
        debug_logger = logging.getLogger('debug')
        debug_logger.setLevel(logging.DEBUG)
        debug_logger.addHandler(debug_handler)
        debug_logger.addHandler(console_handler)
        
        # Log successful setup
        debug_logger.info(f'Logging initialized successfully in {log_dir}')
        
    except (OSError, IOError) as e:
        # If we can't write to files, set up console-only logging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        console_handler.setLevel(logging.ERROR)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)
        root_logger.error(f'Failed to initialize file logging in {log_dir}: {str(e)}. Falling back to console logging.')

def log_calculation_result(params, results):
    """Log only the calculation parameters and results to the CSV file."""
    # Combine parameters and results
    log_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'current_size': int(float(params.get('current_size', 0))),
        'sterilized_count': int(float(params.get('sterilized_count', 0))),
        'monthly_sterilization': int(float(params.get('monthly_sterilization', 0))),
        'months': int(float(params.get('months', 0))),
        'breeding_rate': float(params.get('breeding_rate', 0.0)),
        'kittens_per_litter': float(params.get('kittens_per_litter', 0.0)),
        'litters_per_year': float(params.get('litters_per_year', 0.0)),
        'kitten_survival_rate': float(params.get('kitten_survival_rate', 0.0)),
        'female_ratio': float(params.get('female_ratio', 0.0)),
        'adult_survival_rate': float(params.get('adult_survival_rate', 0.0)),
        'kitten_maturity_months': int(float(params.get('kitten_maturity_months', 0))),
        'sterilization_cost': float(params.get('sterilization_cost', 0.0)),
        'seasonal_breeding_amplitude': float(params.get('seasonal_breeding_amplitude', 0.0)),
        'peak_breeding_month': int(float(params.get('peak_breeding_month', 0))),
        'base_food_capacity': float(params.get('base_food_capacity', 0.0)),
        'food_scaling_factor': float(params.get('food_scaling_factor', 0.0)),
        'water_availability': float(params.get('water_availability', 0.0)),
        'shelter_quality': float(params.get('shelter_quality', 0.0)),
        'urban_risk': float(params.get('urban_risk', 0.0)),
        'disease_risk': float(params.get('disease_risk', 0.0)),
        'natural_risk': float(params.get('natural_risk', 0.0)),
        'caretaker_support': float(params.get('caretaker_support', 0.0)),
        'feeding_consistency': float(params.get('feeding_consistency', 0.0)),
        'territory_size': float(params.get('territory_size', 0.0)),
        'density_impact_threshold': float(params.get('density_impact_threshold', 0.0)),
        'monthly_abandonment': float(params.get('monthly_abandonment', 0.0))
    }
    
    # Add results with proper type conversion
    if isinstance(results, dict):
        # Handle cumulative deaths
        if 'cumulative_deaths' in results:
            cumulative = results['cumulative_deaths']
            log_entry.update({
                'total_deaths': int(float(cumulative.get('total', 0))),
                'kitten_deaths': int(float(cumulative.get('kittens', 0))),
                'adult_deaths': int(float(cumulative.get('adults', 0))),
                'natural_deaths': int(float(cumulative['by_cause'].get('natural', 0))),
                'urban_deaths': int(float(cumulative['by_cause'].get('urban', 0))),
                'disease_deaths': int(float(cumulative['by_cause'].get('disease', 0)))
            })
        else:
            # Fallback to direct death statistics if cumulative not available
            log_entry.update({
                'total_deaths': int(float(results.get('total_deaths', 0))),
                'kitten_deaths': int(float(results.get('kitten_deaths', 0))),
                'adult_deaths': int(float(results.get('adult_deaths', 0))),
                'natural_deaths': int(float(results.get('natural_deaths', 0))),
                'urban_deaths': int(float(results.get('urban_deaths', 0))),
                'disease_deaths': int(float(results.get('disease_deaths', 0)))
            })
        
        # Add other results
        log_entry.update({
            'final_population': int(float(results.get('final_population', 0))),
            'final_sterilized': int(float(results.get('final_sterilized', 0))),
            'final_reproductive': int(float(results.get('final_reproductive', 0))),
            'final_kittens': int(float(results.get('final_kittens', 0))),
            'total_cost': float(results.get('total_cost', 0.0)),
            'monthly_populations': json.dumps(results.get('monthly_populations', [])),
            'monthly_sterilized': json.dumps(results.get('monthly_sterilized', [])),
            'monthly_reproductive': json.dumps(results.get('monthly_reproductive', [])),
            'monthly_kittens': json.dumps(results.get('monthly_kittens', [])),
            'monthly_deaths_kittens': json.dumps([int(float(x)) for x in results.get('monthly_deaths_kittens', [])]),
            'monthly_deaths_adults': json.dumps([int(float(x)) for x in results.get('monthly_deaths_adults', [])]),
            'monthly_deaths_natural': json.dumps([int(float(x)) for x in results.get('monthly_deaths_natural', [])]),
            'monthly_deaths_urban': json.dumps([int(float(x)) for x in results.get('monthly_deaths_urban', [])]),
            'monthly_deaths_disease': json.dumps([int(float(x)) for x in results.get('monthly_deaths_disease', [])]),
            'monthly_deaths_other': json.dumps([int(float(x)) for x in results.get('monthly_deaths_other', [])]),
            'monthly_costs': json.dumps([float(x) for x in results.get('monthly_costs', [])]),
            'monthly_densities': json.dumps([float(x) for x in results.get('monthly_densities', [])])
        })
    
    # Get logger
    logger = logging.getLogger('calculations')
    
    # Log as CSV row
    if logger.handlers[0].stream.tell() == 0:
        # Write headers if file is empty
        headers = ','.join(log_entry.keys())
        logger.info(headers)
    
    # Write values, ensuring proper escaping of JSON strings
    values = []
    for k, v in log_entry.items():
        if isinstance(v, str) and ('[' in v or '{' in v):  # JSON array or object
            # Properly escape the JSON string and wrap in quotes
            escaped = json.dumps(v)  # This will escape any quotes inside the JSON string
            values.append(escaped)
        else:
            values.append(str(v))
    logger.info(','.join(values))

def log_debug(level, message, simulation_id=None):
    """Log debug information to debug.log file."""
    logger = logging.getLogger('debug')
    
    if simulation_id:
        message = f"[{simulation_id}] {message}"
    
    if level == 'DEBUG':
        logger.debug(message)
    elif level == 'INFO':
        logger.info(message)
    elif level == 'WARNING':
        logger.warning(message)
    elif level == 'ERROR':
        logger.error(message)
    elif level == 'CRITICAL':
        logger.critical(message)

def log_simulation_start(simulation_id, params, months=None):
    """Log simulation start with parameters and initial resource usage.
    
    Args:
        simulation_id: Unique identifier for the simulation
        params: Dictionary of simulation parameters or initial population size
        months: Optional number of months to simulate
    """
    logger = logging.getLogger('debug')
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    if isinstance(params, dict):
        params_str = json.dumps(params)
    else:
        params_str = f"Initial population: {params}, Months: {months}"
    
    logger.info(f"Starting simulation {simulation_id}")
    logger.debug(f"Parameters: {params_str}")
    logger.debug(f"Initial memory usage: {initial_memory:.2f} MB")

def log_simulation_end(simulation_id, duration, final_pop, success=True):
    """Log simulation completion with performance metrics."""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    log_data = {
        'duration_seconds': duration,
        'final_population': final_pop,
        'success': success,
        'resources': {
            'memory_used_mb': memory_info.rss / (1024 * 1024),
            'cpu_percent': process.cpu_percent()
        }
    }
    
    log_debug('INFO', f"Simulation {simulation_id} completed in {duration:.2f}s", simulation_id)
    log_debug('DEBUG', f"Results: {json.dumps(log_data)}", simulation_id)

def log_simulation_error(simulation_id, error_msg, phase='unknown'):
    """Log simulation errors with context."""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    log_data = {
        'phase': phase,
        'error': error_msg,
        'resources': {
            'memory_used_mb': memory_info.rss / (1024 * 1024),
            'cpu_percent': process.cpu_percent()
        }
    }
    
    log_debug('ERROR', f"Error in phase {phase}: {error_msg}", simulation_id)
    log_debug('DEBUG', f"Error context: {json.dumps(log_data)}", simulation_id)

def log_resource_usage(simulation_id, phase):
    """Log current resource usage during simulation."""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    log_data = {
        'phase': phase,
        'resources': {
            'memory_used_mb': memory_info.rss / (1024 * 1024),
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent()
        }
    }
    
    log_debug('DEBUG', f"Resource usage in {phase}: {json.dumps(log_data)}", simulation_id)
