"""Monte Carlo simulation for cat colony population growth."""

import numpy as np
from typing import Dict, List, Tuple
from .simulation import simulate_population
import logging
import time

logger = logging.getLogger(__name__)

def generate_parameter_variation(base_params: Dict, variation_coefficient: float = 0.1) -> Dict:
    """Generate parameter variations for Monte Carlo simulation.
    
    Args:
        base_params: Base parameters to vary
        variation_coefficient: Coefficient of variation (standard deviation / mean)
    
    Returns:
        Dict of parameters with random variations
    """
    varied_params = base_params.copy()
    
    # Parameters to vary (only vary rates and continuous values, not discrete counts)
    variable_params = [
        'breeding_rate',
        'kitten_survival_rate',
        'adult_survival_rate',
        'female_ratio',
        'seasonal_breeding_amplitude',
        'base_food_capacity',
        'food_scaling_factor',
        'water_availability',
        'shelter_quality',
        'urban_risk',
        'disease_risk',
        'natural_risk',
        'caretaker_support',
        'feeding_consistency',
        'human_interference'
    ]
    
    for param in variable_params:
        if param in base_params:
            mean = base_params[param]
            std = mean * variation_coefficient
            # Use truncated normal distribution to keep values in reasonable ranges
            value = np.random.normal(mean, std)
            # Ensure values stay between 0 and 1 for rates
            varied_params[param] = np.clip(value, 0.0, 1.0)
    
    return varied_params

def run_monte_carlo(
    base_params: Dict,
    current_size: int,
    months: int,
    sterilized_count: int = 0,
    monthly_sterilization: int = 0,
    num_simulations: int = 5,
    variation_coefficient: float = 0.05
) -> Tuple[Dict, List[Dict]]:
    """Run Monte Carlo simulation of colony growth.
    
    Args:
        base_params: Base parameters for simulation
        current_size: Initial colony size
        months: Number of months to simulate
        sterilized_count: Initial number of sterilized cats
        monthly_sterilization: Monthly sterilization rate
        num_simulations: Number of Monte Carlo simulations to run
        variation_coefficient: Coefficient of variation for parameters
    
    Returns:
        Tuple of (summary statistics, list of all simulation results)
    """
    all_results = []
    final_populations = []
    final_sterilized = []
    total_costs = []
    total_deaths = []
    kitten_deaths = []
    adult_deaths = []
    deaths_by_cause = {
        'natural': [],
        'urban': [],
        'disease': []
    }
    
    try:
        # Validate input parameters
        if num_simulations < 1:
            raise ValueError("Number of simulations must be at least 1")
        if variation_coefficient < 0:
            raise ValueError("Variation coefficient must be non-negative")
            
        successful_simulations = 0
        max_attempts = num_simulations * 2  # Allow up to double attempts to get valid results
        attempt = 0
        
        while successful_simulations < num_simulations and attempt < max_attempts:
            attempt += 1
            try:
                # Generate parameter variations
                params = generate_parameter_variation(base_params, variation_coefficient)
                
                # Add delay between simulations
                if attempt > 1:
                    time.sleep(1)  # 1 second delay between simulations
                
                # Run simulation with varied parameters
                result = simulate_population(
                    params=params,
                    current_size=current_size,
                    months=months,
                    sterilized_count=sterilized_count,
                    monthly_sterilization=monthly_sterilization
                )
                
                if not result:
                    logger.warning(f"Simulation {attempt} produced no result")
                    continue
                
                # Validate result structure
                required_keys = ['final_population', 'final_sterilized', 'total_cost']
                if not all(key in result for key in required_keys):
                    logger.warning(f"Simulation {attempt} missing required keys")
                    continue
                
                # Extract key metrics
                all_results.append(result)
                final_populations.append(result['final_population'])
                final_sterilized.append(result['final_sterilized'])
                total_costs.append(result['total_cost'])
                
                # Extract mortality statistics with safe fallbacks
                total_deaths.append(sum(result.get('monthly_deaths_natural', [0])) + 
                                 sum(result.get('monthly_deaths_urban', [0])) + 
                                 sum(result.get('monthly_deaths_disease', [0])))
                kitten_deaths.append(sum(result.get('monthly_deaths_kittens', [0])))
                adult_deaths.append(sum(result.get('monthly_deaths_adults', [0])))
                deaths_by_cause['natural'].append(sum(result.get('monthly_deaths_natural', [0])))
                deaths_by_cause['urban'].append(sum(result.get('monthly_deaths_urban', [0])))
                deaths_by_cause['disease'].append(sum(result.get('monthly_deaths_disease', [0])))
                
                successful_simulations += 1
                
            except Exception as e:
                logger.warning(f"Error in simulation {attempt}: {str(e)}")
                continue
        
        if successful_simulations < num_simulations * 0.5:  # Require at least 50% success rate
            raise ValueError(f"Too few successful simulations: {successful_simulations}/{num_simulations}")
            
        if not all_results:
            raise ValueError("No valid simulation results generated")
        
        # Calculate summary statistics
        summary = {
            'population': {
                'mean': np.mean(final_populations),
                'median': np.median(final_populations),
                'std': np.std(final_populations),
                'ci_lower': np.percentile(final_populations, 2.5),
                'ci_upper': np.percentile(final_populations, 97.5)
            },
            'sterilized': {
                'mean': np.mean(final_sterilized),
                'median': np.median(final_sterilized),
                'std': np.std(final_sterilized),
                'ci_lower': np.percentile(final_sterilized, 2.5),
                'ci_upper': np.percentile(final_sterilized, 97.5)
            },
            'cost': {
                'mean': np.mean(total_costs),
                'median': np.median(total_costs),
                'std': np.std(total_costs),
                'ci_lower': np.percentile(total_costs, 2.5),
                'ci_upper': np.percentile(total_costs, 97.5)
            },
            'mortality': {
                'total': {
                    'mean': np.mean(total_deaths),
                    'median': np.median(total_deaths),
                    'std': np.std(total_deaths),
                    'ci_lower': np.percentile(total_deaths, 2.5),
                    'ci_upper': np.percentile(total_deaths, 97.5)
                },
                'kittens': {
                    'mean': np.mean(kitten_deaths),
                    'median': np.median(kitten_deaths),
                    'std': np.std(kitten_deaths),
                    'ci_lower': np.percentile(kitten_deaths, 2.5),
                    'ci_upper': np.percentile(kitten_deaths, 97.5)
                },
                'adults': {
                    'mean': np.mean(adult_deaths),
                    'median': np.median(adult_deaths),
                    'std': np.std(adult_deaths),
                    'ci_lower': np.percentile(adult_deaths, 2.5),
                    'ci_upper': np.percentile(adult_deaths, 97.5)
                },
                'by_cause': {
                    'natural': {
                        'mean': np.mean(deaths_by_cause['natural']),
                        'median': np.median(deaths_by_cause['natural']),
                        'std': np.std(deaths_by_cause['natural']),
                        'ci_lower': np.percentile(deaths_by_cause['natural'], 2.5),
                        'ci_upper': np.percentile(deaths_by_cause['natural'], 97.5)
                    },
                    'urban': {
                        'mean': np.mean(deaths_by_cause['urban']),
                        'median': np.median(deaths_by_cause['urban']),
                        'std': np.std(deaths_by_cause['urban']),
                        'ci_lower': np.percentile(deaths_by_cause['urban'], 2.5),
                        'ci_upper': np.percentile(deaths_by_cause['urban'], 97.5)
                    },
                    'disease': {
                        'mean': np.mean(deaths_by_cause['disease']),
                        'median': np.median(deaths_by_cause['disease']),
                        'std': np.std(deaths_by_cause['disease']),
                        'ci_lower': np.percentile(deaths_by_cause['disease'], 2.5),
                        'ci_upper': np.percentile(deaths_by_cause['disease'], 97.5)
                    }
                }
            }
        }
        
        return summary, all_results
    
    except Exception as e:
        logger.error(f"Error in Monte Carlo simulation: {str(e)}")
        raise
