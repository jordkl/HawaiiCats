"""Cat population simulation package."""

from .simulation import simulate_population
from .constants import DEFAULT_PARAMS
from .utils.simulation_utils import (
    calculate_seasonal_factor,
    calculate_density_impact,
    calculate_resource_impact,
    calculate_resource_availability,
    calculate_monthly_mortality,
    calculate_resource_limit,
    calculate_breeding_success
)

__all__ = [
    'simulate_population',
    'DEFAULT_PARAMS',
    'calculate_seasonal_factor',
    'calculate_density_impact',
    'calculate_resource_impact',
    'calculate_resource_availability',
    'calculate_monthly_mortality',
    'calculate_resource_limit',
    'calculate_breeding_success'
]
