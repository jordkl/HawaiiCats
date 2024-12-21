"""Main simulation logic for cat colony population growth."""

import numpy as np
import logging
import traceback
import time
from datetime import datetime
from .utils.logging_utils import (
    log_debug,
    log_simulation_start,
    log_simulation_end,
    log_simulation_error
)
from .utils.simulation_utils import (
    calculate_seasonal_factor,
    calculate_carrying_capacity,
    calculate_density_impact,
    calculate_resource_availability,
    calculate_monthly_mortality
)
from .constants import DEFAULT_PARAMS, MIN_BREEDING_AGE, MAX_BREEDING_AGE, GESTATION_MONTHS, TERRITORY_SIZE_RANGES, DENSITY_THRESHOLD_RANGES

logger = logging.getLogger('debug')

def simulate_population(params, current_size=100, months=12, sterilized_count=0, monthly_sterilization=0, use_monte_carlo=False, monte_carlo_runs=50):
    """
    Calculate population growth with enhanced environmental factors.
    
    Args:
        params (dict): Dictionary of simulation parameters
        current_size (int): Current population size
        months (int): Number of months to simulate
        sterilized_count (int): Initial number of sterilized cats
        monthly_sterilization (int): Number of cats sterilized per month
        use_monte_carlo (bool): Whether to run Monte Carlo simulation
        monte_carlo_runs (int): Number of Monte Carlo runs if use_monte_carlo is True
        
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
        monte_carlo_runs = int(monte_carlo_runs) if use_monte_carlo else 1
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
        
        # Initialize tracking arrays
        monthly_populations = []
        monthly_sterilized = []
        monthly_reproductive = []
        monthly_kittens = []
        monthly_costs = []
        monthly_densities = []
        monthly_deaths_kittens = []
        monthly_deaths_adults = []
        monthly_deaths_natural = []
        monthly_deaths_urban = []
        monthly_deaths_disease = []
        monthly_deaths_other = []
        
        # Initialize other tracking variables
        unmet_sterilizations = 0  # Track unmet sterilizations
        
        # Add initial values to monthly tracking
        total_population = current_size  # Initialize total population
        monthly_populations.append(total_population)
        monthly_sterilized.append(sterilized_count)
        monthly_reproductive.append(total_population - sterilized_count)
        monthly_kittens.append(0)  # No kittens at start
        monthly_deaths_kittens.append(0)
        monthly_deaths_adults.append(0)
        monthly_deaths_natural.append(0)
        monthly_deaths_urban.append(0)
        monthly_deaths_disease.append(0)
        monthly_deaths_other.append(0)
        monthly_costs.append(0)
        monthly_densities.append(total_population / calculate_carrying_capacity(params))
        
        # Initialize colony structure with age distribution
        from .models import initialize_colony_with_ages
        colony, initial_pregnant = initialize_colony_with_ages(current_size, sterilized_count, params)
        
        # Add sterilized_kittens list to colony structure
        colony['sterilized_kittens'] = []
        
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
        for current_month in range(months):
            month_cost = 0.0
            month_deaths = {
                'kittens': 0,
                'adults': 0,
                'causes': {'natural': 0, 'urban': 0, 'disease': 0}
            }
            
            # Calculate current population with explicit type conversion
            current_population = int(
                sum((int(float(count)) for count, _ in colony.get('young_kittens', [])), 0) +
                sum((int(float(count)) for count, _ in colony.get('reproductive', [])), 0) +
                sum((int(float(count)) for count, _ in colony.get('sterilized', [])), 0)
            )
            
            # Calculate total sterilized population for tracking
            current_sterilized = sum((int(float(count)) for count, _ in colony.get('sterilized', [])), 0)
            monthly_sterilized.append(current_sterilized)
            
            # Calculate environmental factors
            from .utils.simulation_utils import (
                calculate_seasonal_factor,
                calculate_density_impact,
                calculate_resource_availability
            )
            
            # Calculate carrying capacity for this environment
            carrying_capacity = calculate_carrying_capacity(params)
            
            # Calculate seasonal factor
            seasonal_factor = calculate_seasonal_factor(
                current_month % 12,
                float(params['seasonal_breeding_amplitude']),
                int(params['peak_breeding_month'])
            )
            
            # Calculate density and resource effects
            density_effect = calculate_density_impact(current_population, params)
            resource_availability = calculate_resource_availability(current_population, params)
            
            # Combined environmental factor
            environment_factor = (
                0.4 * density_effect +      # Density has major impact
                0.4 * resource_availability + # Resources have major impact
                0.2 * seasonal_factor        # Season has minor impact
            )
            
            # Track density for monitoring
            monthly_densities.append(current_population / calculate_carrying_capacity(params))
            
            # Calculate mortality rates with stronger risk impacts
            from .utils.simulation_utils import calculate_monthly_mortality
            deaths = calculate_monthly_mortality(params, colony, environment_factor, current_month)
            
            log_debug('DEBUG', f'Month {current_month} deaths calculation:')
            log_debug('DEBUG', f'  Environment factor: {environment_factor:.3f}')
            log_debug('DEBUG', f'  Density effect: {density_effect:.3f}')
            log_debug('DEBUG', f'  Resource availability: {resource_availability:.3f}')
            log_debug('DEBUG', f'  Seasonal factor: {seasonal_factor:.3f}')
            
            # Process kitten deaths first
            remaining_kitten_deaths = deaths['kittens']
            new_young_kittens = []
            monthly_deaths_kittens.append(0)  # Initialize for this month
            monthly_deaths_adults.append(0)   # Initialize for this month
            
            for count, age in colony['young_kittens']:
                count = int(float(count))
                if count > 0 and remaining_kitten_deaths > 0:
                    # Calculate deaths for this age group
                    group_deaths = min(count, remaining_kitten_deaths)
                    remaining_kitten_deaths -= group_deaths
                    count -= group_deaths
                    
                    # Update monthly tracking
                    monthly_deaths_kittens[-1] += group_deaths
                
                if count > 0:
                    new_young_kittens.append((count, age))
            
            colony['young_kittens'] = new_young_kittens
            
            # Process adult deaths proportionally between reproductive and sterilized
            remaining_adult_deaths = deaths['adults']
            if remaining_adult_deaths > 0:
                total_adults = (
                    sum(int(float(count)) for count, _ in colony['reproductive']) +
                    sum(int(float(count)) for count, _ in colony['sterilized'])
                )
                
                if total_adults > 0:
                    # Process reproductive adults
                    new_reproductive = []
                    reproductive_total = sum(int(float(count)) for count, _ in colony['reproductive'])
                    if reproductive_total > 0:
                        reproductive_deaths = int(remaining_adult_deaths * (reproductive_total / total_adults))
                        remaining_deaths = reproductive_deaths
                        
                        for count, age in colony['reproductive']:
                            count = int(float(count))
                            if count > 0 and remaining_deaths > 0:
                                group_deaths = min(count, remaining_deaths)
                                remaining_deaths -= group_deaths
                                count -= group_deaths
                                monthly_deaths_adults[-1] += group_deaths
                            
                            if count > 0:
                                new_reproductive.append((count, age))
                        
                        colony['reproductive'] = new_reproductive
                    
                    # Process sterilized adults
                    new_sterilized = []
                    sterilized_total = sum(int(float(count)) for count, _ in colony['sterilized'])
                    if sterilized_total > 0:
                        sterilized_deaths = remaining_adult_deaths - (reproductive_deaths if 'reproductive_deaths' in locals() else 0)
                        remaining_deaths = sterilized_deaths
                        
                        for count, age in colony['sterilized']:
                            count = int(float(count))
                            if count > 0 and remaining_deaths > 0:
                                group_deaths = min(count, remaining_deaths)
                                remaining_deaths -= group_deaths
                                count -= group_deaths
                                monthly_deaths_adults[-1] += group_deaths
                            
                            if count > 0:
                                new_sterilized.append((count, age))
                        
                        colony['sterilized'] = new_sterilized
            
            # Process deaths by cause
            for cause, count in deaths.get('causes', {}).items():
                if cause == 'natural':
                    monthly_deaths_natural.append(count)
                elif cause == 'urban':
                    monthly_deaths_urban.append(count)
                elif cause == 'disease':
                    monthly_deaths_disease.append(count)
                else:
                    monthly_deaths_other.append(0)  # Initialize other causes
            
            # Update cumulative death counts
            cumulative_deaths['total'] += deaths.get('kittens', 0) + deaths.get('adults', 0)
            cumulative_deaths['kittens'] += deaths.get('kittens', 0)
            cumulative_deaths['adults'] += deaths.get('adults', 0)
            cumulative_deaths['by_cause']['natural'] += deaths.get('causes', {}).get('natural', 0)
            cumulative_deaths['by_cause']['urban'] += deaths.get('causes', {}).get('urban', 0)
            cumulative_deaths['by_cause']['disease'] += deaths.get('causes', {}).get('disease', 0)
            
            # Log death statistics
            log_debug('DEBUG', f'Month {current_month} deaths:')
            log_debug('DEBUG', f'  Kittens: {monthly_deaths_kittens[-1]}')
            log_debug('DEBUG', f'  Adults: {monthly_deaths_adults[-1]}')
            
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
                        log_debug('DEBUG', f'Month {current_month}: Added {abandoned_adults} abandoned adults')
                    
                    # Add abandoned kittens
                    if abandoned_kittens > 0:
                        colony['young_kittens'].append([abandoned_kittens, 2])  # Assume average age of 2 months
                        log_debug('DEBUG', f'Month {current_month}: Added {abandoned_kittens} abandoned kittens')
            
            # Process sterilization with both adults and kittens
            if monthly_sterilization > 0 or unmet_sterilizations > 0:
                # Add any unmet sterilizations from previous month
                total_sterilizations = monthly_sterilization + unmet_sterilizations
                
                # Calculate total cats eligible for sterilization
                total_reproductive = sum(int(float(count)) for count, _ in colony['reproductive'])
                total_kittens = sum(int(float(count)) for count, age in colony['young_kittens'] if int(float(age)) >= MIN_BREEDING_AGE)
                total_eligible = total_reproductive + total_kittens
                
                log_debug('DEBUG', f'Month {current_month} sterilization stats:')
                log_debug('DEBUG', f'  Target sterilizations: {total_sterilizations} (monthly: {monthly_sterilization}, carried over: {unmet_sterilizations})')
                log_debug('DEBUG', f'  Eligible cats: {total_eligible} (reproductive: {total_reproductive}, kittens: {total_kittens})')
                
                # Track how many sterilizations we couldn't perform
                unmet_sterilizations = max(0, total_sterilizations - total_eligible)
                if unmet_sterilizations > 0:
                    log_debug('DEBUG', f'  Could not perform {unmet_sterilizations} sterilizations due to lack of eligible cats')
                
                if total_eligible > 0:
                    # Distribute sterilizations proportionally between adults and kittens
                    adult_ratio = total_reproductive / total_eligible
                    kitten_ratio = total_kittens / total_eligible
                    
                    # Calculate actual sterilizations (limited by eligible cats)
                    actual_sterilizations = min(total_sterilizations, total_eligible)
                    adult_sterilizations = int(round(actual_sterilizations * adult_ratio))
                    kitten_sterilizations = actual_sterilizations - adult_sterilizations
                    
                    log_debug('DEBUG', f'  Performing {actual_sterilizations} sterilizations:')
                    log_debug('DEBUG', f'    Adults: {adult_sterilizations} ({adult_ratio:.1%} of eligible)')
                    log_debug('DEBUG', f'    Kittens: {kitten_sterilizations} ({kitten_ratio:.1%} of eligible)')
                    
                    # Process adult sterilizations
                    if adult_sterilizations > 0 and total_reproductive > 0:
                        remaining_reproductive = []
                        cats_to_sterilize = adult_sterilizations
                        
                        for count, age in colony['reproductive']:
                            count = int(float(count))
                            if cats_to_sterilize > 0:
                                if count <= cats_to_sterilize:
                                    # Sterilize entire group
                                    colony['sterilized'].append([count, age])
                                    cats_to_sterilize -= count
                                else:
                                    # Split group
                                    colony['sterilized'].append([cats_to_sterilize, age])
                                    remaining_reproductive.append([count - cats_to_sterilize, age])
                                    cats_to_sterilize = 0
                            else:
                                remaining_reproductive.append([count, age])
                        
                        colony['reproductive'] = remaining_reproductive
                    
                    # Process kitten sterilizations
                    if kitten_sterilizations > 0 and total_kittens > 0:
                        remaining_kittens = []
                        cats_to_sterilize = kitten_sterilizations
                        
                        for count, age in colony['young_kittens']:
                            count = int(float(count))
                            age = int(float(age))
                            
                            if age >= MIN_BREEDING_AGE:
                                if cats_to_sterilize > 0:
                                    if count <= cats_to_sterilize:
                                        # Sterilize entire group and move to sterilized
                                        colony['sterilized'].append([count, age])
                                        cats_to_sterilize -= count
                                    else:
                                        # Split group
                                        colony['sterilized'].append([cats_to_sterilize, age])
                                        remaining_kittens.append([count - cats_to_sterilize, age])
                                        cats_to_sterilize = 0
                                else:
                                    remaining_kittens.append([count, age])
                            else:
                                # Too young to sterilize
                                remaining_kittens.append([count, age])
                        
                        colony['young_kittens'] = remaining_kittens
            
            # Process kitten maturity
            new_unsterilized_kittens = []
            new_sterilized_kittens = []
            matured_count = 0
            maturity_age = int(params.get('maturity_age', 6))
            
            # Process unsterilized kittens
            for count, age in colony['young_kittens']:
                count = int(float(count))
                age = int(float(age))
                
                if count <= 0:
                    continue
                
                # Age check for maturity
                if age >= maturity_age:
                    # When kittens mature, add them to reproductive group
                    colony['reproductive'].append([count, maturity_age])
                    matured_count += count
                    log_debug('DEBUG', f'Month {current_month}: {count} unsterilized kittens matured at age {maturity_age} months')
                else:
                    # Keep track of surviving kittens that are still too young
                    new_unsterilized_kittens.append([count, age + 1])
                    log_debug('DEBUG', f'Month {current_month}: {count} unsterilized kittens aged to {age + 1} months')
            
            colony['young_kittens'] = new_unsterilized_kittens
            
            # Process sterilized kittens
            new_sterilized_kittens = []
            
            if 'sterilized_kittens' in colony:
                for count, age in colony['sterilized_kittens']:
                    count = int(float(count))
                    age = int(float(age))
                    
                    if count <= 0:
                        continue
                    
                    # Age check for maturity
                    if age >= maturity_age:
                        # When sterilized kittens mature, add them to sterilized group
                        colony['sterilized'].append([count, maturity_age])
                        matured_count += count
                        log_debug('DEBUG', f'Month {current_month}: {count} sterilized kittens matured at age {maturity_age} months')
                    else:
                        # Keep track of surviving kittens that are still too young
                        new_sterilized_kittens.append([count, age + 1])
                        log_debug('DEBUG', f'Month {current_month}: {count} sterilized kittens aged to {age + 1} months')
            
            colony['sterilized_kittens'] = new_sterilized_kittens
            
            if matured_count > 0:
                log_debug('DEBUG', f'Month {current_month}: {matured_count} kittens matured')
            
            # Process breeding with age constraints and pregnancy limits
            if colony['reproductive']:
                # Calculate breeding rate based on litters per year
                # Cats can have 2-3 litters per year, with 2 month gestation
                gestation_months = GESTATION_MONTHS
                
                # Base monthly breeding chance from yearly litters
                litters_per_year = float(params['litters_per_year'])
                monthly_breeding_chance = min(0.95, litters_per_year / (12 - GESTATION_MONTHS))
                
                # Only count females of breeding age
                breeding_females = sum(
                    int(float(count)) * float(params['female_ratio'])
                    for count, age in colony['reproductive']
                    if MIN_BREEDING_AGE <= float(age) <= MAX_BREEDING_AGE
                )
                
                log_debug('DEBUG', f'Month {current_month}: Base breeding chance: {monthly_breeding_chance:.3f}')
                log_debug('DEBUG', f'Month {current_month}: {breeding_females:.1f} breeding-age females available')
                
                # Calculate available females (not currently pregnant)
                current_pregnancies = float(sum(pregnant_females))
                available_females = max(0, breeding_females - current_pregnancies)
                
                if available_females > 0:
                    # Calculate breeding success with more resilient rates
                    from .utils.simulation_utils import calculate_breeding_success
                    breeding_success = calculate_breeding_success(params, colony, environment_factor, current_month % 12)
                    
                    # Enhanced breeding chance calculation - more sensitive to parameters
                    base_chance = monthly_breeding_chance * breeding_success
                    
                    # Small colony bonus - gentler scaling
                    if breeding_females < 5:
                        base_chance = min(0.95, base_chance * 1.5)  # 50% bonus for very small colonies
                    elif breeding_females < 10:
                        base_chance = min(0.95, base_chance * 1.25)  # 25% bonus for small colonies
                        
                    # Minimum breeding chance scales with parameters
                    min_chance = 0.1 * (1.0 + float(params.get('breeding_rate', 0.85)))
                    pregnancy_chance = max(min_chance, base_chance)
                    
                    # Calculate new pregnancies with enhanced success
                    new_pregnant = np.random.binomial(int(available_females), pregnancy_chance)
                    
                    # Small chance of pregnancy in good conditions
                    if new_pregnant == 0 and available_females >= 1:
                        if breeding_success > 0.6 or breeding_females < 5:  # Stricter conditions
                            if np.random.random() < pregnancy_chance:  # No bonus multiplier
                                new_pregnant = 1
                    if new_pregnant > 0:
                        log_debug('DEBUG', f'Month {current_month}: {new_pregnant} new females became pregnant (chance: {pregnancy_chance:.2f})')
                        pregnant_females.append(new_pregnant)
            
            # Process births from previous pregnancies
            if pregnant_females and len(pregnant_females) >= GESTATION_MONTHS:
                births = pregnant_females.pop(0)  # Get the oldest pregnancy group
                if births > 0:
                    # Calculate base number of kittens
                    base_litter_size = float(params['kittens_per_litter'])
                    
                    # Seasonal effect on litter size - more pronounced
                    season_bonus = 1.0
                    if current_month % 12 in [2, 3, 4, 8, 9, 10]:  # Peak months
                        season_bonus = 1.3
                    elif current_month % 12 in [5, 6, 7]:  # Moderate months
                        season_bonus = 1.15
                    
                    # Resource quality affects litter size (more impact)
                    resource_bonus = 0.7 + (0.6 * environment_factor)  # Wider range from 0.7 to 1.3
                    
                    # Calculate final litter size
                    adjusted_litter_size = base_litter_size * season_bonus * resource_bonus
                    
                    # Dynamic litter size bounds based on base size
                    min_litter = max(1, round(base_litter_size * 0.6))  # Can be smaller in poor conditions
                    max_litter = min(8, round(base_litter_size * 1.4))  # Can be larger in good conditions
                    adjusted_litter_size = max(min_litter, min(max_litter, adjusted_litter_size))
                    
                    # Add small random variation
                    variation = np.random.normal(0, 0.15)  # Slightly more variation (15%)
                    final_litter_size = max(min_litter, min(max_litter, adjusted_litter_size * (1 + variation)))
                    
                    # Calculate total kittens born
                    kittens = int(round(float(births) * final_litter_size))
                    
                    log_debug('DEBUG', f'Month {current_month} births: {births} females giving birth to {kittens} kittens (avg {final_litter_size:.1f} per litter)')
                    if kittens > 0:
                        colony['young_kittens'].append([kittens, 0])
                        log_debug('DEBUG', f'Added {kittens} new kittens to colony')
            
            # Age all cats by one month
            for category in ['reproductive', 'sterilized']:
                colony[category] = [[count, age + 1] for count, age in colony[category]]
            
            # Recalculate current population after all monthly changes
            reproductive_count = sum(int(float(count)) for count, _ in colony['reproductive'])
            sterilized_count = sum(int(float(count)) for count, _ in colony['sterilized'])
            unsterilized_kitten_count = sum(int(float(count)) for count, _ in colony['young_kittens'])
            sterilized_kitten_count = sum(int(float(count)) for count, _ in colony['sterilized_kittens'])
            
            current_population = reproductive_count + sterilized_count + unsterilized_kitten_count + sterilized_kitten_count
            
            # Update monthly tracking arrays
            monthly_populations.append(current_population)
            monthly_reproductive.append(reproductive_count)
            monthly_kittens.append(unsterilized_kitten_count + sterilized_kitten_count)
            monthly_costs.append(month_cost)
            monthly_densities.append(current_population / calculate_carrying_capacity(params))
            
            log_debug('DEBUG', f'Month {current_month} population breakdown:')
            log_debug('DEBUG', f'  Young kittens: {sum(count for count, _ in colony["young_kittens"])}')
            log_debug('DEBUG', f'  Reproductive: {sum(count for count, _ in colony["reproductive"])}')
            log_debug('DEBUG', f'  Sterilized: {sum(count for count, _ in colony["sterilized"])}')
            log_debug('DEBUG', f'  Total population: {current_population}')
            log_debug('DEBUG', f'  Deaths this month:')
            log_debug('DEBUG', f'    Kittens: {month_deaths.get("kittens", 0)}')
            log_debug('DEBUG', f'    Adults: {month_deaths.get("adults", 0)}')
            log_debug('DEBUG', f'    Natural: {month_deaths.get("causes", {}).get("natural", 0)}')
            log_debug('DEBUG', f'    Urban: {month_deaths.get("causes", {}).get("urban", 0)}')
            log_debug('DEBUG', f'    Disease: {month_deaths.get("causes", {}).get("disease", 0)}')
            
            # Calculate density relative to territory
            density = current_population / params['territory_size'] if params['territory_size'] > 0 else float('inf')
            
        duration = time.time() - start_time
        log_simulation_end(simulation_id, duration, monthly_populations[-1])
        
        # Prepare results with death statistics
        final_population = monthly_populations[-1]
        results = {
            'final_population': final_population,
            'final_sterilized': monthly_sterilized[-1],
            'final_reproductive': monthly_reproductive[-1],
            'final_kittens': monthly_kittens[-1],
            'total_cost': total_cost,
            'total_sterilizations': monthly_sterilization * months,
            'population_growth': final_population - current_size,
            'total_deaths': sum(monthly_deaths_kittens) + sum(monthly_deaths_adults),  # Calculate from monthly data
            'kitten_deaths': sum(monthly_deaths_kittens),
            'adult_deaths': sum(monthly_deaths_adults),
            'natural_deaths': sum(monthly_deaths_natural),
            'urban_deaths': sum(monthly_deaths_urban),
            'disease_deaths': sum(monthly_deaths_disease),
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

        # Create calculation parameters dictionary
        calculation_params = {
            'current_size': current_size,
            'sterilized_count': sterilized_count,
            'monthly_sterilization': monthly_sterilization,
            'months': months,
            **params  # Include all simulation parameters
        }

        # Only log if not running in test mode
        if not params.get('test_mode', False):
            from .utils.logging_utils import log_calculation_result
            log_calculation_result(calculation_params, results)
        
        if use_monte_carlo:
            # Initialize arrays for Monte Carlo results
            all_results = []
            for run in range(monte_carlo_runs):
                run_result = simulate_population(
                    params=params,
                    current_size=current_size,
                    months=months,
                    sterilized_count=sterilized_count,
                    monthly_sterilization=monthly_sterilization,
                    use_monte_carlo=False
                )
                if run_result is not None:
                    all_results.append(run_result)

            if not all_results:
                log_simulation_error(simulation_id, "All Monte Carlo simulations failed")
                return None

            # Calculate averages and standard deviations
            monte_carlo_summary = {}
            
            # Process numeric fields
            numeric_fields = [
                'final_population', 'final_sterilized', 'final_reproductive',
                'final_kittens', 'total_cost', 'total_deaths', 'kitten_deaths',
                'adult_deaths', 'natural_deaths', 'urban_deaths', 'disease_deaths'
            ]
            
            for field in numeric_fields:
                values = [float(r[field]) for r in all_results if field in r]
                if values:
                    monte_carlo_summary[field] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values)
                    }

            # Process monthly arrays
            monthly_fields = [
                'monthly_populations', 'monthly_sterilized', 'monthly_reproductive',
                'monthly_kittens', 'monthly_deaths_kittens', 'monthly_deaths_adults',
                'monthly_deaths_natural', 'monthly_deaths_urban', 'monthly_deaths_disease'
            ]

            for field in monthly_fields:
                if field in all_results[0]:
                    arrays = [r[field] for r in all_results]
                    if arrays:
                        arr = np.array(arrays)
                        monte_carlo_summary[field] = {
                            'mean': np.mean(arr, axis=0).tolist(),
                            'std': np.std(arr, axis=0).tolist(),
                            'min': np.min(arr, axis=0).tolist(),
                            'max': np.max(arr, axis=0).tolist()
                        }

            # Use median simulation for base result
            median_idx = len(all_results) // 2
            result = all_results[median_idx]
            result['monte_carlo_summary'] = monte_carlo_summary
            result['monte_carlo_runs'] = monte_carlo_runs
            
            return result
        
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
