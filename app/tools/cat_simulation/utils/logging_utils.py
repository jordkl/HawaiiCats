"""Logging utilities for cat population simulation."""

import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger('debug')

def setupLogging() -> None:
    """Set up logging configuration."""
    try:
        # Create logs directory if it doesn't exist
        logsDir = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(logsDir):
            os.makedirs(logsDir)
            
        # Configure debug logger
        debugLogger = logging.getLogger('debug')
        debugLogger.setLevel(logging.DEBUG)
        
        # Create debug file handler
        debugHandler = logging.FileHandler(os.path.join(logsDir, 'debug.log'))
        debugHandler.setLevel(logging.DEBUG)
        
        # Create formatters and add them to the handlers
        debugFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        debugHandler.setFormatter(debugFormatter)
        
        # Add handlers to the loggers
        debugLogger.addHandler(debugHandler)
        
        # Configure error logger
        errorLogger = logging.getLogger('error')
        errorLogger.setLevel(logging.ERROR)
        
        # Create error file handler
        errorHandler = logging.FileHandler(os.path.join(logsDir, 'error.log'))
        errorHandler.setLevel(logging.ERROR)
        
        # Create error formatter
        errorFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        errorHandler.setFormatter(errorFormatter)
        
        # Add handler to error logger
        errorLogger.addHandler(errorHandler)
        
        # Configure console handler for both loggers
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.INFO)
        consoleFormatter = logging.Formatter('%(levelname)s - %(message)s')
        consoleHandler.setFormatter(consoleFormatter)
        
        debugLogger.addHandler(consoleHandler)
        errorLogger.addHandler(consoleHandler)
        
    except Exception as e:
        print(f"Error setting up logging: {str(e)}")
        raise

def logCalculationResult(params: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Log calculation parameters and results."""
    try:
        logData = {
            'timestamp': datetime.now().isoformat(),
            'parameters': params,
            'results': result
        }
        
        # Create a list of values in a consistent order
        values = [
            logData['timestamp'],
            json.dumps(params),
            json.dumps(result)
        ]
        
        logger.info(','.join(values))
        
    except Exception as e:
        logger.error(f"Error logging calculation result: {str(e)}")

def logDebug(level: str, message: str, simulationId: Optional[str] = None) -> None:
    """Log a debug message with optional simulation ID context."""
    try:
        if simulationId:
            message = f"[Simulation {simulationId}] {message}"
        
        if level.upper() == 'DEBUG':
            logger.debug(message)
        elif level.upper() == 'INFO':
            logger.info(message)
        elif level.upper() == 'WARNING':
            logger.warning(message)
        elif level.upper() == 'ERROR':
            logger.error(message)
        else:
            logger.debug(message)
            
    except Exception as e:
        logger.error(f"Error logging debug message: {str(e)}")

def logSimulationStart(simulationId: str, params: Dict[str, Any], months: Optional[int] = None) -> None:
    """Log the start of a simulation with parameters."""
    try:
        logData = {
            'simulationId': simulationId,
            'startTime': datetime.now().isoformat(),
            'params': params
        }
        if months is not None:
            logData['months'] = months
            
        logDebug('INFO', f"Starting simulation {simulationId}", simulationId)
        logDebug('DEBUG', f"Parameters: {json.dumps(logData)}", simulationId)
        
    except Exception as e:
        logger.error(f"Error logging simulation start: {str(e)}")

def logSimulationEnd(simulationId: str, duration: float, finalPop: int, success: bool = True) -> None:
    """Log the end of a simulation with results."""
    try:
        logData = {
            'simulationId': simulationId,
            'endTime': datetime.now().isoformat(),
            'duration': duration,
            'finalPopulation': finalPop,
            'success': success
        }
        
        logDebug('INFO', f"Simulation {simulationId} completed in {duration:.2f}s", simulationId)
        logDebug('DEBUG', f"Results: {json.dumps(logData)}", simulationId)
        
    except Exception as e:
        logger.error(f"Error logging simulation end: {str(e)}")

def logSimulationError(simulationId: str, errorMsg: str, phase: str = 'unknown') -> None:
    """Log a simulation error with context."""
    try:
        logData = {
            'simulationId': simulationId,
            'timestamp': datetime.now().isoformat(),
            'phase': phase,
            'error': errorMsg
        }
        
        logDebug('ERROR', f"Error in phase {phase}: {errorMsg}", simulationId)
        logDebug('DEBUG', f"Error context: {json.dumps(logData)}", simulationId)
        
    except Exception as e:
        logger.error(f"Error logging simulation error: {str(e)}")

def logResourceUsage(simulationId: str, phase: str, memoryUsage: float, cpuTime: float) -> None:
    """Log resource usage statistics for a simulation phase."""
    try:
        logData = {
            'simulationId': simulationId,
            'timestamp': datetime.now().isoformat(),
            'phase': phase,
            'memoryUsageMB': memoryUsage,
            'cpuTimeSeconds': cpuTime
        }
        
        logDebug('DEBUG', f"Resource usage in {phase}: {json.dumps(logData)}", simulationId)
        
    except Exception as e:
        logger.error(f"Error logging resource usage: {str(e)}")
