"""Monte Carlo simulation for cat colony population growth."""

import numpy as np
from typing import Dict, List, Tuple
from .simulation import simulate_population
import logging
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
import multiprocessing

logger = logging.getLogger(__name__)

def generate_parameter_variations(base_params: Dict, num_simulations: int, variation_coefficient: float = 0.1) -> List[Dict]:
    """Generate parameter variations for multiple simulations at once."""
    # Parameters to vary
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
    
    varied_params_list = []
    
    # Create parameter variations using vectorized operations
    for param in variable_params:
        if param in base_params:
            mean = base_params[param]
            std = mean * variation_coefficient
            # Generate all variations at once using numpy
            variations = np.random.normal(mean, std, num_simulations)
            # Clip values between 0 and 1 for rates
            variations = np.clip(variations, 0.0, 1.0)
            
            # Add variations to each parameter set
            for i in range(num_simulations):
                if i >= len(varied_params_list):
                    varied_params_list.append(base_params.copy())
                varied_params_list[i][param] = float(variations[i])
    
    return varied_params_list

def run_simulation_worker(params: Dict, current_size: int, months: int, 
                         sterilized_count: int, monthly_sterilization: int) -> Dict:
    """Worker function to run a single simulation."""
    try:
        return simulate_population(
            params=params,
            current_size=current_size,
            months=months,
            sterilized_count=sterilized_count,
            monthly_sterilization=monthly_sterilization
        )
    except Exception as e:
        logger.warning(f"Simulation failed with error: {str(e)}")
        return None

def run_monte_carlo(
    base_params: Dict,
    current_size: int,
    months: int,
    sterilized_count: int = 0,
    monthly_sterilization: int = 0,
    num_simulations: int = 5,
    variation_coefficient: float = 0.05
) -> Tuple[Dict, List[Dict]]:
    """Run Monte Carlo simulation of colony growth using parallel processing."""
    
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
    
    # Initialize arrays to store monthly populations for all simulations
    monthly_populations = [[] for _ in range(months + 1)]  # +1 for initial month
    monthly_sterilized = [[] for _ in range(months + 1)]
    monthly_reproductive = [[] for _ in range(months + 1)]
    monthly_kittens = [[] for _ in range(months + 1)]
    
    try:
        # Validate input parameters
        if num_simulations < 1:
            raise ValueError("Number of simulations must be at least 1")
        if variation_coefficient < 0:
            raise ValueError("Variation coefficient must be non-negative")
        
        # Generate all parameter variations at once
        param_variations = generate_parameter_variations(
            base_params, num_simulations, variation_coefficient
        )
        
        # Create a partial function with fixed arguments
        worker_func = partial(
            run_simulation_worker,
            current_size=current_size,
            months=months,
            sterilized_count=sterilized_count,
            monthly_sterilization=monthly_sterilization
        )
        
        # Use ProcessPoolExecutor for parallel processing
        num_workers = max(1, multiprocessing.cpu_count() - 1)  # Leave one CPU free
        successful_simulations = 0
        
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            # Submit all simulations
            future_to_params = {
                executor.submit(worker_func, params): params 
                for params in param_variations
            }
            
            # Process results as they complete
            for future in as_completed(future_to_params):
                result = future.result()
                
                if not result:
                    continue
                
                # Extract key metrics
                all_results.append(result)
                final_populations.append(result['final_population'])
                final_sterilized.append(result['final_sterilized'])
                total_costs.append(result['total_cost'])
                
                # Store monthly populations for this simulation
                for month, pop in enumerate(result['monthly_populations']):
                    if month < len(monthly_populations):  # Ensure we don't exceed array bounds
                        monthly_populations[month].append(pop)
                
                # Store monthly sterilized counts
                for month, count in enumerate(result['monthly_sterilized']):
                    if month < len(monthly_sterilized):
                        monthly_sterilized[month].append(count)
                
                # Store monthly reproductive counts
                for month, count in enumerate(result['monthly_reproductive']):
                    if month < len(monthly_reproductive):
                        monthly_reproductive[month].append(count)
                
                # Store monthly kitten counts
                for month, count in enumerate(result['monthly_kittens']):
                    if month < len(monthly_kittens):
                        monthly_kittens[month].append(count)
                
                # Extract mortality statistics
                total_deaths.append(sum(result.get('monthly_deaths_natural', [0])) + 
                                 sum(result.get('monthly_deaths_urban', [0])) + 
                                 sum(result.get('monthly_deaths_disease', [0])))
                kitten_deaths.append(sum(result.get('monthly_deaths_kittens', [0])))
                adult_deaths.append(sum(result.get('monthly_deaths_adults', [0])))
                deaths_by_cause['natural'].append(sum(result.get('monthly_deaths_natural', [0])))
                deaths_by_cause['urban'].append(sum(result.get('monthly_deaths_urban', [0])))
                deaths_by_cause['disease'].append(sum(result.get('monthly_deaths_disease', [0])))
                
                successful_simulations += 1
        
        if successful_simulations < num_simulations * 0.5:  # Require at least 50% success rate
            raise ValueError(f"Too few successful simulations: {successful_simulations}/{num_simulations}")
        
        if not all_results:
            raise ValueError("No valid simulation results generated")
        
        # Convert lists to numpy arrays for faster calculations
        final_populations = np.array(final_populations)
        final_sterilized = np.array(final_sterilized)
        total_costs = np.array(total_costs)
        total_deaths = np.array(total_deaths)
        kitten_deaths = np.array(kitten_deaths)
        adult_deaths = np.array(adult_deaths)
        
        # Calculate monthly statistics
        monthly_stats = []
        for month in range(months + 1):
            if month < len(monthly_populations) and monthly_populations[month]:
                month_pops = np.array(monthly_populations[month])
                monthly_stats.append({
                    'mean': float(np.mean(month_pops)),
                    'median': float(np.median(month_pops)),
                    'std': float(np.std(month_pops)),
                    'ci_lower': float(np.percentile(month_pops, 2.5)),
                    'ci_upper': float(np.percentile(month_pops, 97.5))
                })
            else:
                # Add placeholder stats if no data for this month
                monthly_stats.append({
                    'mean': 0.0,
                    'median': 0.0,
                    'std': 0.0,
                    'ci_lower': 0.0,
                    'ci_upper': 0.0
                })
        
        # Calculate summary statistics using numpy
        summary = {
            'population': {
                'mean': float(np.mean(final_populations)),
                'median': float(np.median(final_populations)),
                'std': float(np.std(final_populations)),
                'ci_lower': float(np.percentile(final_populations, 2.5)),
                'ci_upper': float(np.percentile(final_populations, 97.5))
            },
            'sterilized': {
                'mean': float(np.mean(final_sterilized)),
                'median': float(np.median(final_sterilized)),
                'std': float(np.std(final_sterilized)),
                'ci_lower': float(np.percentile(final_sterilized, 2.5)),
                'ci_upper': float(np.percentile(final_sterilized, 97.5))
            },
            'cost': {
                'mean': float(np.mean(total_costs)),
                'median': float(np.median(total_costs)),
                'std': float(np.std(total_costs)),
                'ci_lower': float(np.percentile(total_costs, 2.5)),
                'ci_upper': float(np.percentile(total_costs, 97.5))
            },
            'mortality': {
                'total': {
                    'mean': float(np.mean(total_deaths)),
                    'median': float(np.median(total_deaths)),
                    'std': float(np.std(total_deaths)),
                    'ci_lower': float(np.percentile(total_deaths, 2.5)),
                    'ci_upper': float(np.percentile(total_deaths, 97.5))
                },
                'kittens': {
                    'mean': float(np.mean(kitten_deaths)),
                    'median': float(np.median(kitten_deaths)),
                    'std': float(np.std(kitten_deaths)),
                    'ci_lower': float(np.percentile(kitten_deaths, 2.5)),
                    'ci_upper': float(np.percentile(kitten_deaths, 97.5))
                },
                'adults': {
                    'mean': float(np.mean(adult_deaths)),
                    'median': float(np.median(adult_deaths)),
                    'std': float(np.std(adult_deaths)),
                    'ci_lower': float(np.percentile(adult_deaths, 2.5)),
                    'ci_upper': float(np.percentile(adult_deaths, 97.5))
                }
            },
            'monthly_stats': monthly_stats
        }
        
        return summary, all_results
        
    except Exception as e:
        logger.error(f"Monte Carlo simulation failed: {str(e)}")
        raise
