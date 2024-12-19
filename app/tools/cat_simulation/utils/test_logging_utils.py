"""Test-specific logging utilities."""
import logging
import os
from datetime import datetime

def setup_test_logging():
    """Set up logging configuration specifically for tests."""
    # Create a console handler for test output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    console_handler.setLevel(logging.INFO)
    
    # Create test logger
    test_logger = logging.getLogger('test')
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(console_handler)
    
    return test_logger

def log_test_result(params, results):
    """Log test results without writing to file."""
    logger = logging.getLogger('test')
    
    try:
        # Log basic simulation parameters
        logger.info(f"Test Parameters: Population={params.get('current_size')}, "
                   f"Months={params.get('months')}, "
                   f"Sterilized={params.get('sterilized_count')}")
        
        # Log key results
        if isinstance(results, dict):
            logger.info(f"Results: Final Population={results.get('final_population')}, "
                       f"Final Sterilized={results.get('final_sterilized')}, "
                       f"Total Deaths={results.get('total_deaths')}")
    except Exception as e:
        logger.error(f"Error logging test results: {str(e)}")
