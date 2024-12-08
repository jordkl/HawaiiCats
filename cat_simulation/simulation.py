"""Main simulation logic for cat colony population growth."""

import numpy as np
import logging
import traceback
import math
from .utils.simulation_utils import (
    calculate_seasonal_factor,
    calculate_density_impact,
    calculate_resource_impact,
    calculate_resource_availability,
    calculate_monthly_mortality,
    calculate_resource_limit,
    calculate_breeding_success
)
from .models import initialize_colony_with_ages
from .utils.logging_utils import (
    setup_logging,
    log_calculation_result,
    log_debug,
    log_simulation_start,
    log_simulation_end,
    log_simulation_error
)
from .constants import DEFAULT_PARAMS, MIN_BREEDING_AGE, MAX_BREEDING_AGE
import time
from datetime import datetime

# Set up logging
setup_logging()

logger = logging.getLogger('debug')

def simulate_population(params, current_size=100, months=12, sterilized_count=0, monthly_sterilization=0):
    """
    Calculate population growth with enhanced environmental factors.
    
    Args:
        params (dict): Dictionary of simulation parameters
        current_size (int): Current population size
        months (int): Number of months to simulate
        sterilized_count (int): Initial number of sterilized cats
        monthly_sterilization (int): Number of cats sterilized per month
        
    Returns:
        dict: Simulation results including population over time and other metrics
    """
    start_time = time.time()
    simulation_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if not isinstance(params, dict):
        log_simulation_error(simulation_id, "Invalid input parameters: params must be a dictionary")
        return None
        
    # Convert all numeric inputs to appropriate types
    try:
        current_size = int(float(current_size))
        months = int(float(months))
        sterilized_count = int(float(sterilized_count))
        monthly_sterilization = int(float(monthly_sterilization))
    except (ValueError, TypeError) as e:
        log_simulation_error(simulation_id, f"Error converting input parameters: {str(e)}")
        return None
        
    if current_size < 1:
        log_simulation_error(simulation_id, "Invalid input parameters: current_size must be a positive number")
        return None
    if months < 1:
        log_simulation_error(simulation_id, "Invalid input parameters: months must be a positive number")
        return None
    if sterilized_count < 0:
        log_simulation_error(simulation_id, "Invalid input parameters: sterilized_count must be a non-negative number")
        return None
    if monthly_sterilization < 0:
        log_simulation_error(simulation_id, "Invalid input parameters: monthly_sterilization must be a non-negative number")
        return None
        
    try:
        log_simulation_start(simulation_id, current_size)
        
        monthly_data = []
        monthly_populations = [current_size]
        monthly_sterilized = [sterilized_count]
        monthly_reproductive = [current_size - sterilized_count]
        monthly_kittens = [0]
        monthly_deaths_natural = [0]
        monthly_deaths_urban = [0]
        monthly_deaths_disease = [0]
        monthly_deaths_kittens = [0]
        monthly_deaths_adults = [0]
        monthly_deaths_other = [0]
        monthly_costs = []
        monthly_densities = []
        
        # Initialize colony structure with age distribution
        colony, initial_pregnant = initialize_colony_with_ages(current_size, sterilized_count, params)
        
        # Track total costs and deaths
        total_cost = 0.0
        cumulative_deaths = {
            'total': 0,
            'kittens': 0,
            'adults': 0,
            'by_cause': {
                'natural': 0,
                'urban': 0,
                'disease': 0
            }
        }

        # Initialize pregnancy tracking
        pregnant_females = [initial_pregnant] if initial_pregnant > 0 else []
        
        # Simulate each month
        for month in range(months):
            month_cost = 0.0
            month_deaths = {
                'kittens': 0,
                'adults': 0,
                'causes': {'natural': 0, 'urban': 0, 'disease': 0}
            }
            
            # Calculate current population with explicit type conversion
            current_population = int(
                sum(int(count) for count, _ in colony['young_kittens']) +
                sum(int(count) for count, _ in colony['reproductive']) +
                sum(int(count) for count, _ in colony['sterilized'])
            )
            
            # Calculate seasonal and environmental factors
            seasonal_factor = float(calculate_seasonal_factor(
                month % 12,
                float(params['seasonal_breeding_amplitude']),
                int(params['peak_breeding_month'])
            ))
            
            # Calculate resource limits and stress with stronger density effects
            stress_factor, max_sustainable = calculate_resource_limit(params, current_population)
            max_sustainable = float(max_sustainable)
            density_effect = float(1.0 / (1.0 + np.exp((float(current_population) - max_sustainable) / (max_sustainable * 0.2))))
            
            # Calculate mortality rates with stronger risk impacts
            adult_mortality, kitten_mortality = calculate_monthly_mortality(params, colony)
            
            # Process deaths
            new_colony = {'young_kittens': [], 'reproductive': [], 'sterilized': []}
            
            # Process kitten deaths with gentler seasonal variation in survival
            seasonal_kitten_mortality = kitten_mortality * (1.1 - seasonal_factor * 0.2)  # Reduced seasonal impact
            log_debug('DEBUG', f'Month {month} kitten mortality rate: {seasonal_kitten_mortality}')
            
            # Calculate total risk for death cause distribution
            total_risk = float(params.get('natural_risk', 0.05)) + \
                        float(params.get('urban_risk', 0.1)) + \
                        float(params.get('disease_risk', 0.15))
            
            if total_risk > 0:
                risk_ratios = {
                    'natural': float(params.get('natural_risk', 0.05)) / total_risk,
                    'urban': float(params.get('urban_risk', 0.1)) / total_risk,
                    'disease': float(params.get('disease_risk', 0.15)) / total_risk
                }
            else:
                risk_ratios = {'natural': 1/3, 'urban': 1/3, 'disease': 1/3}  # Equal distribution if no risks specified
            
            # Process kitten deaths
            for count, age in colony['young_kittens']:
                count = int(float(count))  # Ensure count is an integer
                deaths = int(round(float(count) * float(seasonal_kitten_mortality)))  # Ensure deaths is an integer
                survivors = count - deaths
                if survivors > 0:
                    new_colony['young_kittens'].append([survivors, age])
                
                if deaths > 0:
                    month_deaths['kittens'] += deaths
                    # Distribute deaths by cause based on risk ratios
                    natural_deaths = int(round(deaths * risk_ratios['natural']))
                    urban_deaths = int(round(deaths * risk_ratios['urban']))
                    disease_deaths = deaths - natural_deaths - urban_deaths  # Remainder to avoid rounding errors
                    
                    month_deaths['causes']['natural'] += natural_deaths
                    month_deaths['causes']['urban'] += urban_deaths
                    month_deaths['causes']['disease'] += disease_deaths

            # Process adult deaths (both reproductive and sterilized)
            for group in ['reproductive', 'sterilized']:
                for count, age in colony[group]:
                    deaths = round(float(count) * float(adult_mortality))
                    survivors = count - deaths
                    if survivors > 0:
                        new_colony[group].append([survivors, age])
                    
                    if deaths > 0:
                        month_deaths['adults'] += deaths
                        # Distribute deaths by cause based on risk ratios
                        natural_deaths = round(deaths * risk_ratios['natural'])
                        urban_deaths = round(deaths * risk_ratios['urban'])
                        disease_deaths = deaths - natural_deaths - urban_deaths  # Remainder to avoid rounding errors
                        
                        month_deaths['causes']['natural'] += natural_deaths
                        month_deaths['causes']['urban'] += urban_deaths
                        month_deaths['causes']['disease'] += disease_deaths

            # Update monthly death statistics
            monthly_deaths_natural.append(month_deaths['causes']['natural'])
            monthly_deaths_urban.append(month_deaths['causes']['urban'])
            monthly_deaths_disease.append(month_deaths['causes']['disease'])
            monthly_deaths_kittens.append(month_deaths['kittens'])
            monthly_deaths_adults.append(month_deaths['adults'])
            
            # Update cumulative deaths
            cumulative_deaths['total'] += month_deaths['kittens'] + month_deaths['adults']
            cumulative_deaths['kittens'] += month_deaths['kittens']
            cumulative_deaths['adults'] += month_deaths['adults']
            cumulative_deaths['by_cause']['natural'] += month_deaths['causes']['natural']
            cumulative_deaths['by_cause']['urban'] += month_deaths['causes']['urban']
            cumulative_deaths['by_cause']['disease'] += month_deaths['causes']['disease']
            
            # Record monthly deaths
            log_debug('DEBUG', f'Month {month} deaths: {month_deaths}')
            log_debug('DEBUG', f'Cumulative deaths: {cumulative_deaths}')
            
            colony = new_colony
            
            # Process monthly abandonment additions
            monthly_abandonment = float(params.get('monthly_abandonment', 0))
            if monthly_abandonment > 0:
                # Calculate number of abandoned cats this month
                abandoned_cats = int(round(monthly_abandonment))
                if abandoned_cats > 0:
                    # Assume abandoned cats are mostly adults, with some kittens
                    adult_ratio = 0.7  # 70% adults, 30% kittens
                    abandoned_adults = int(round(abandoned_cats * adult_ratio))
                    abandoned_kittens = abandoned_cats - abandoned_adults
                    
                    # Add abandoned adults to reproductive population
                    if abandoned_adults > 0:
                        colony['reproductive'].append([abandoned_adults, 12])  # Assume average age of 12 months
                        log_debug('DEBUG', f'Month {month}: Added {abandoned_adults} abandoned adults')
                    
                    # Add abandoned kittens
                    if abandoned_kittens > 0:
                        colony['young_kittens'].append([abandoned_kittens, 2])  # Assume average age of 2 months
                        log_debug('DEBUG', f'Month {month}: Added {abandoned_kittens} abandoned kittens')
            
            # Recalculate current population after abandonment
            current_population = int(
                sum(int(count) for count, _ in colony['young_kittens']) +
                sum(int(count) for count, _ in colony['reproductive']) +
                sum(int(count) for count, _ in colony['sterilized'])
            )
            
            # Process breeding with age constraints and pregnancy limits
            if colony['reproductive']:
                # Calculate monthly breeding rate from annual rate - adjusted to be more realistic
                monthly_breeding_rate = float(params['breeding_rate'] * params['litters_per_year']) / 8.0  # Changed from 12.0 to 8.0
                
                # Only count females of breeding age
                breeding_females = sum(
                    int(float(count)) * float(params['female_ratio'])
                    for count, age in colony['reproductive']
                    if MIN_BREEDING_AGE <= float(age) <= MAX_BREEDING_AGE
                )
                
                log_debug('DEBUG', f'Month {month}: Monthly breeding rate: {monthly_breeding_rate:.3f}')
                log_debug('DEBUG', f'Month {month}: {breeding_females:.1f} breeding-age females available')
                
                # Calculate maximum simultaneous pregnancies (adjusted for monthly rate)
                max_pregnancies = float(breeding_females * monthly_breeding_rate * 1.2)  # Added 20% buffer
                current_pregnancies = float(sum(pregnant_females))
                
                if current_pregnancies < max_pregnancies:
                    # Calculate available females for new pregnancies
                    available_females = float(breeding_females * (1 - current_pregnancies / breeding_females))
                    
                    # Combine environmental factors more gently
                    environmental_factor = float((stress_factor + seasonal_factor + density_effect) / 3)
                    
                    # Calculate breeding success using the colony structure
                    breeding_success = calculate_breeding_success(params, colony, environmental_factor)
                    
                    # Calculate new pregnancies
                    new_pregnant = int(round(min(
                        available_females * breeding_success * monthly_breeding_rate,
                        max_pregnancies - current_pregnancies
                    )))
                    
                    if new_pregnant > 0:
                        log_debug('DEBUG', f'Month {month}: {new_pregnant} new females became pregnant (success rate: {breeding_success:.2f})')
                        pregnant_females.append(new_pregnant)
            
            # Process births from previous pregnancies
            gestation_months = int(float(params.get('gestation_months', 2)))  # Default to 2 months if not specified
            if pregnant_females and len(pregnant_females) >= gestation_months:  # Check if enough time has passed
                births = int(float(pregnant_females.pop(0)))
                if births > 0:
                    kittens = int(math.ceil(float(births) * float(params['kittens_per_litter']) * float(seasonal_factor)))
                    log_debug('DEBUG', f'Month {month} births: {births} females giving birth to {kittens} kittens')
                    if kittens > 0:
                        colony['young_kittens'].append([kittens, 0])
                        log_debug('DEBUG', f'Added {kittens} new kittens to colony')
            
            # Process kitten maturity
            new_kittens = []
            matured_count = 0
            for count, age in colony['young_kittens']:
                count = int(float(count))
                age = int(float(age))
                if age >= int(float(params['kitten_maturity_months'])):
                    colony['reproductive'].append([count, age])
                    matured_count += count
                else:
                    new_kittens.append([count, age + 1])
            colony['young_kittens'] = new_kittens
            if matured_count > 0:
                log_debug('DEBUG', f'Month {month}: {matured_count} kittens matured into reproductive adults')
            
            # Process sterilizations with colony size impact
            if monthly_sterilization > 0 and colony['reproductive']:
                # More realistic trapping success for small colonies
                success_rate = 0.85  # 85% success rate for TNR efforts
                availability_factor = 0.8  # Increased from 0.7
                
                # Modified colony size factor - more effective for small colonies
                colony_size_factor = 1.0 if current_population <= 20 else 1.0 / (1.0 + (current_population - 20) / 20)
                
                # Use ceiling to ensure at least 1 sterilization when requested
                effective_sterilization = math.ceil(float(monthly_sterilization) * float(success_rate) * float(availability_factor) * float(colony_size_factor))
                
                if effective_sterilization > 0:
                    # Prioritize breeding-age cats for sterilization
                    breeding_age_cats = [
                        (count, age) for count, age in colony['reproductive']
                        if MIN_BREEDING_AGE <= age <= MAX_BREEDING_AGE
                    ]
                    
                    if breeding_age_cats:
                        total_breeding = sum(count for count, _ in breeding_age_cats)
                        remaining = effective_sterilization
                        month_sterilized = 0  # Track actual sterilizations this month
                        
                        for i, (count, age) in enumerate(breeding_age_cats):
                            if remaining <= 0:
                                break
                                
                            sterilized = min(count, remaining)
                            remaining -= sterilized
                            month_sterilized += sterilized
                            
                            # Update reproductive and sterilized counts
                            breeding_age_cats[i] = (count - sterilized, age)
                            colony['sterilized'].append([sterilized, age])
                        
                        # Add cost based on actual sterilizations performed
                        month_cost = month_sterilized * params['sterilization_cost']
                        total_cost += month_cost
            
            # Age all cats by one month
            for category in ['reproductive', 'sterilized']:
                colony[category] = [[count, age + 1] for count, age in colony[category]]
            
            # Recalculate current population after all monthly changes
            current_population = (
                sum(count for count, _ in colony['young_kittens']) +
                sum(count for count, _ in colony['reproductive']) +
                sum(count for count, _ in colony['sterilized'])
            )
            
            log_debug('DEBUG', f'Month {month} population breakdown:')
            log_debug('DEBUG', f'  Young kittens: {sum(count for count, _ in colony["young_kittens"])}')
            log_debug('DEBUG', f'  Reproductive: {sum(count for count, _ in colony["reproductive"])}')
            log_debug('DEBUG', f'  Sterilized: {sum(count for count, _ in colony["sterilized"])}')
            log_debug('DEBUG', f'  Total population: {current_population}')
            
            # Store monthly statistics
            monthly_populations.append(current_population)
            monthly_sterilized.append(sum(count for count, _ in colony['sterilized']))
            monthly_reproductive.append(sum(count for count, _ in colony['reproductive']))
            monthly_kittens.append(sum(count for count, _ in colony['young_kittens']))
            
            # Store death statistics
            monthly_deaths_other.append(0)  # Add other deaths to monthly data
            monthly_costs.append(month_cost)
            
            # Calculate density relative to territory
            density = current_population / params['territory_size'] if params['territory_size'] > 0 else float('inf')
            monthly_densities.append(density)
            
        duration = time.time() - start_time
        log_simulation_end(simulation_id, duration, monthly_populations[-1])
        
        # Prepare results
        results = {
            'final_population': monthly_populations[-1],
            'final_sterilized': monthly_sterilized[-1],
            'final_reproductive': monthly_reproductive[-1],
            'final_kittens': monthly_kittens[-1],
            'total_cost': total_cost,
            'total_deaths': cumulative_deaths['total'],
            'kitten_deaths': cumulative_deaths['kittens'],
            'adult_deaths': cumulative_deaths['adults'],
            'natural_deaths': cumulative_deaths['by_cause']['natural'],
            'urban_deaths': cumulative_deaths['by_cause']['urban'],
            'disease_deaths': cumulative_deaths['by_cause']['disease'],
            'monthly_populations': monthly_populations,
            'monthly_sterilized': monthly_sterilized,
            'monthly_reproductive': monthly_reproductive,
            'monthly_kittens': monthly_kittens,
            'monthly_deaths_kittens': monthly_deaths_kittens,
            'monthly_deaths_adults': monthly_deaths_adults,
            'monthly_deaths_natural': monthly_deaths_natural,
            'monthly_deaths_urban': monthly_deaths_urban,
            'monthly_deaths_disease': monthly_deaths_disease,
            'monthly_deaths_other': monthly_deaths_other,
            'monthly_costs': monthly_costs,
            'average_density': sum(monthly_densities) / len(monthly_densities),
            'max_density': max(monthly_densities),
            'months_over_threshold': sum(1 for d in monthly_densities if d > params['density_impact_threshold'])
        }

        # Log calculation parameters and results to CSV
        calculation_params = {
            'current_size': current_size,
            'sterilized_count': sterilized_count,
            'monthly_sterilization': monthly_sterilization,
            'months': months,
            **params  # Include all simulation parameters
        }
        log_calculation_result(calculation_params, results)
        
        return results
            
    except Exception as e:
        log_simulation_error(simulation_id, f"Fatal error: {str(e)}")
        logger.error(f"Error in simulate_population: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def run_parameter_tests():
    """Run a series of parameter tests to validate model behavior."""
    base_params = {
        "breeding_rate": 0.98,
        "kittens_per_litter": 5,
        "litters_per_year": 3.5,
        "kitten_survival_rate": 0.85,
        "female_ratio": 0.5,
        "adult_survival_rate": 0.95,
        "seasonal_breeding_amplitude": 0.1,
        "peak_breeding_month": 4,
        "territory_size": 1000,
        "density_impact_threshold": 1.5,
        "base_resources": 0.95,
        "resource_variability": 0.1,
        "urban_environment": 0.7,
        "urban_risk": 0.03,
        "disease_risk": 0.03,
        "natural_risk": 0.02,
        "carrying_capacity": 1500,
        "base_breeding_success": 0.95,
        "age_breeding_factor": 0.06,
        "stress_impact": 0.12,
        "early_breeding_age": 5,
        "peak_breeding_age": 36,
        "kitten_maturity_months": 5  # Age at which kittens become adults
    }

    test_scenarios = [
        # Baseline test
        {
            "name": "Baseline Hawaii",
            "params": base_params.copy(),
            "initial_colony": 50,
            "months": 24
        },
        
        # Breeding rate tests
        {
            "name": "Low Breeding Rate",
            "params": {**base_params, "breeding_rate": 0.70},
            "initial_colony": 50,
            "months": 24,
            "expected": "slower_growth"
        },
        {
            "name": "High Breeding Rate",
            "params": {**base_params, "breeding_rate": 1.0},
            "initial_colony": 50,
            "months": 24,
            "expected": "faster_growth"
        },
        
        # Litter size tests
        {
            "name": "Small Litters",
            "params": {**base_params, "kittens_per_litter": 3},
            "initial_colony": 50,
            "months": 24,
            "expected": "smaller_population"
        },
        {
            "name": "Large Litters",
            "params": {**base_params, "kittens_per_litter": 6},
            "initial_colony": 50,
            "months": 24,
            "expected": "larger_population"
        },
        
        # Litters per year tests
        {
            "name": "Few Litters Per Year",
            "params": {**base_params, "litters_per_year": 2.0},
            "initial_colony": 50,
            "months": 24,
            "expected": "slower_growth"
        },
        {
            "name": "Many Litters Per Year",
            "params": {**base_params, "litters_per_year": 4.0},
            "initial_colony": 50,
            "months": 24,
            "expected": "faster_growth"
        },
        
        # Survival rate tests
        {
            "name": "Low Kitten Survival",
            "params": {**base_params, "kitten_survival_rate": 0.6},
            "initial_colony": 50,
            "months": 24,
            "expected": "high_kitten_mortality"
        },
        {
            "name": "Low Adult Survival",
            "params": {**base_params, "adult_survival_rate": 0.7},
            "initial_colony": 50,
            "months": 24,
            "expected": "high_adult_mortality"
        },
        
        # Resource tests
        {
            "name": "Resource Scarcity",
            "params": {**base_params, "base_resources": 0.5, "resource_variability": 0.3},
            "initial_colony": 50,
            "months": 24,
            "expected": "resource_limited_growth"
        },
        {
            "name": "Abundant Resources",
            "params": {**base_params, "base_resources": 1.0, "resource_variability": 0.05},
            "initial_colony": 50,
            "months": 24,
            "expected": "resource_unlimited_growth"
        },
        
        # Urban environment tests
        {
            "name": "Rural Environment",
            "params": {**base_params, "urban_environment": 0.2, "urban_risk": 0.05},
            "initial_colony": 50,
            "months": 24,
            "expected": "lower_density_tolerance"
        },
        {
            "name": "Urban Environment",
            "params": {**base_params, "urban_environment": 0.9, "urban_risk": 0.02},
            "initial_colony": 50,
            "months": 24,
            "expected": "higher_density_tolerance"
        },
        
        # Age-related breeding tests
        {
            "name": "Late Breeding Age",
            "params": {**base_params, "early_breeding_age": 8, "peak_breeding_age": 30},
            "initial_colony": 50,
            "months": 24,
            "expected": "delayed_growth"
        },
        {
            "name": "Early Breeding Age",
            "params": {**base_params, "early_breeding_age": 4, "peak_breeding_age": 40},
            "initial_colony": 50,
            "months": 24,
            "expected": "accelerated_growth"
        },
        
        # Density impact tests
        {
            "name": "High Density Sensitivity",
            "params": {**base_params, "density_impact_threshold": 1.0, "carrying_capacity": 1000},
            "initial_colony": 50,
            "months": 24,
            "expected": "strong_density_effects"
        },
        {
            "name": "Low Density Sensitivity",
            "params": {**base_params, "density_impact_threshold": 2.0, "carrying_capacity": 2000},
            "initial_colony": 50,
            "months": 24,
            "expected": "weak_density_effects"
        },
        
        # Seasonal effects tests
        {
            "name": "Strong Seasonality",
            "params": {**base_params, "seasonal_breeding_amplitude": 0.3},
            "initial_colony": 50,
            "months": 24,
            "expected": "seasonal_variation"
        },
        {
            "name": "No Seasonality",
            "params": {**base_params, "seasonal_breeding_amplitude": 0.0},
            "initial_colony": 50,
            "months": 24,
            "expected": "constant_breeding"
        },
        
        # Disease risk tests
        {
            "name": "High Disease Risk",
            "params": {**base_params, "disease_risk": 0.15, "density_impact_threshold": 1.2},
            "initial_colony": 50,
            "months": 24,
            "expected": "disease_limited"
        },
        {
            "name": "No Disease Risk",
            "params": {**base_params, "disease_risk": 0.0},
            "initial_colony": 50,
            "months": 24,
            "expected": "no_disease_deaths"
        }
    ]
    
    results = []
    for scenario in test_scenarios:
        try:
            result = simulate_population(
                scenario["params"],
                scenario["initial_colony"],
                scenario["months"]
            )
            
            if result:
                # Calculate growth metrics
                population_series = result["monthly_populations"]
                max_population = max(population_series)
                final_population = population_series[-1]
                
                # Calculate growth rates for different periods
                early_growth = sum([(population_series[i+1] - population_series[i]) / max(1, population_series[i])
                                  for i in range(min(6, len(population_series)-1))]) / 6
                
                late_growth = sum([(population_series[i+1] - population_series[i]) / max(1, population_series[i])
                                 for i in range(max(0, len(population_series)-7), len(population_series)-1)]) / 6
                
                # Calculate mortality metrics
                kitten_mortality_rate = result["kitten_deaths"] / max(1, result["total_deaths"]) if result["total_deaths"] > 0 else 0
                disease_mortality_rate = result["disease_deaths"] / max(1, result["total_deaths"]) if result["total_deaths"] > 0 else 0
                
                results.append({
                    "scenario": scenario["name"],
                    "expected_behavior": scenario.get("expected", "not_specified"),
                    "initial_population": scenario["initial_colony"],
                    "final_population": final_population,
                    "max_population": max_population,
                    "early_growth_rate": early_growth,
                    "late_growth_rate": late_growth,
                    "total_deaths": result["total_deaths"],
                    "kitten_mortality_rate": kitten_mortality_rate,
                    "disease_mortality_rate": disease_mortality_rate,
                    "months_simulated": scenario["months"]
                })
                
                # Log detailed analysis
                logger.info(f"\nScenario: {scenario['name']}")
                logger.info(f"Expected behavior: {scenario.get('expected', 'not_specified')}")
                logger.info(f"Final population: {final_population}")
                logger.info(f"Early growth rate: {early_growth:.3f}")
                logger.info(f"Late growth rate: {late_growth:.3f}")
                logger.info(f"Kitten mortality rate: {kitten_mortality_rate:.3f}")
                logger.info(f"Disease mortality rate: {disease_mortality_rate:.3f}")
            
        except Exception as e:
            logger.error(f"Error in scenario {scenario['name']}: {str(e)}")
            logger.error(traceback.format_exc())
            continue
    
    return results
