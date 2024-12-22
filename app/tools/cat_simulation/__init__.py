"""Cat population simulation package."""

import os
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

from simulation import simulatePopulation
from constants import DEFAULT_PARAMS, MIN_BREEDING_AGE, MAX_BREEDING_AGE, GESTATION_MONTHS, TERRITORY_SIZE_RANGES, DENSITY_THRESHOLD_RANGES

__all__ = [
    'simulatePopulation',
    'DEFAULT_PARAMS',
    'MIN_BREEDING_AGE',
    'MAX_BREEDING_AGE',
    'GESTATION_MONTHS',
    'TERRITORY_SIZE_RANGES',
    'DENSITY_THRESHOLD_RANGES'
]
