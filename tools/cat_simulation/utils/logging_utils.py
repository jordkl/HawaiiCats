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
        **params,
        **results
    }
    
    # Get logger
    logger = logging.getLogger('calculations')
    
    # Log as CSV row
    if logger.handlers[0].stream.tell() == 0:
        # Write headers if file is empty
        headers = ','.join(log_entry.keys())
        logger.info(headers)
    
    # Write values
    values = ','.join(str(v) for v in log_entry.values())
    logger.info(values)

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
