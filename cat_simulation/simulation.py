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
from .constants import DEFAULT_PARAMS, MIN_BREEDING_AGE, MAX_BREEDING_AGE, GESTATION_MONTHS

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
        
        # Initialize tracking variables
        total_population = current_size
        sterilized = sterilized_count
        reproductive = total_population - sterilized
        kittens = 0
        unmet_sterilizations = 0  # Track unmet sterilizations
        
        # Initialize lists to track monthly values
        monthly_populations = []
        monthly_sterilized = []
        monthly_reproductive = []
        monthly_kittens = []
        monthly_deaths_natural = []
        monthly_deaths_urban = []
        monthly_deaths_disease = []
        monthly_deaths_kittens = []
        monthly_deaths_adults = []
        monthly_deaths_other = []
        monthly_costs = []
        monthly_densities = []
        
        # Add initial values to monthly tracking
        monthly_populations.append(total_population)
        monthly_sterilized.append(sterilized)
        monthly_reproductive.append(reproductive)
        monthly_kittens.append(kittens)
        monthly_deaths_natural.append(0)
        monthly_deaths_urban.append(0)
        monthly_deaths_disease.append(0)
        monthly_deaths_kittens.append(0)
        monthly_deaths_adults.append(0)
        monthly_deaths_other.append(0)
        monthly_costs.append(0)
        monthly_densities.append(current_size / params.get('territory_size', 1000))
        
        # Initialize colony structure with age distribution
        from .models import initialize_colony_with_ages
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
                sum(int(float(count)) for count, _ in colony['young_kittens']) +
                sum(int(float(count)) for count, _ in colony['reproductive']) +
                sum(int(float(count)) for count, _ in colony['sterilized'])
            )
            
            # Calculate seasonal and environmental factors
            from .utils.simulation_utils import calculate_seasonal_factor
            seasonal_factor = float(calculate_seasonal_factor(
                month % 12,
                float(params['seasonal_breeding_amplitude']),
                int(params['peak_breeding_month'])
            ))
            
            # Calculate resource limits and stress with stronger density effects
            from .utils.simulation_utils import calculate_resource_limit
            stress_factor, max_sustainable = calculate_resource_limit(params, current_population)
            max_sustainable = float(max_sustainable)
            density_effect = float(1.0 / (1.0 + np.exp((float(current_population) - max_sustainable) / (max_sustainable * 0.2))))
            
            # Calculate mortality rates with stronger risk impacts
            from .utils.simulation_utils import calculate_monthly_mortality
            adult_mortality, kitten_mortality = calculate_monthly_mortality(params, colony)
            log_debug('DEBUG', f'Month {month} base adult mortality rate: {adult_mortality}')
            
            # Process deaths
            new_colony = {'young_kittens': [], 'reproductive': [], 'sterilized': [], 'sterilized_kittens': []}
            
            # Process kitten deaths with gentler seasonal variation in survival
            seasonal_kitten_mortality = kitten_mortality * (1.1 - seasonal_factor * 0.2)  # Reduced seasonal impact
            log_debug('DEBUG', f'Month {month} kitten mortality rate: {seasonal_kitten_mortality}')
            
            # Calculate total risk for death cause distribution
            total_risk = float(params.get('natural_risk', 0.05)) + \
                        float(params.get('urban_risk', 0.1)) + \
                        float(params.get('disease_risk', 0.15))
            
            # Ensure minimum risk values
            min_risk = 0.01  # 1% minimum risk for each cause
            natural_risk = max(min_risk, float(params.get('natural_risk', 0.05)))
            urban_risk = max(min_risk, float(params.get('urban_risk', 0.1)))
            disease_risk = max(min_risk, float(params.get('disease_risk', 0.15)))
            total_risk = natural_risk + urban_risk + disease_risk
            
            # Calculate risk ratios with minimum thresholds
            risk_ratios = {
                'natural': natural_risk / total_risk,
                'urban': urban_risk / total_risk,
                'disease': disease_risk / total_risk
            }
            
            log_debug('DEBUG', f'Month {month} risk ratios: Natural={risk_ratios["natural"]:.2f}, Urban={risk_ratios["urban"]:.2f}, Disease={risk_ratios["disease"]:.2f}')
            
            # Process kitten deaths
            for count, age in colony['young_kittens']:
                count = int(float(count))  # Ensure count is an integer
                raw_deaths = float(count) * float(seasonal_kitten_mortality)
                # For small groups, use probabilistic death
                if raw_deaths < 1 and raw_deaths > 0:
                    deaths = 1 if np.random.random() < raw_deaths else 0
                else:
                    deaths = int(round(raw_deaths))
                survivors = max(0, count - deaths)
                
                if survivors > 0:
                    new_colony['young_kittens'].append([survivors, age])
                
                if deaths > 0:
                    month_deaths['kittens'] += deaths
                    # Distribute deaths by cause based on risk ratios with minimum counts
                    natural_deaths = max(1, int(round(deaths * risk_ratios['natural']))) if deaths >= 3 else int(np.random.random() < risk_ratios['natural'])
                    urban_deaths = max(1, int(round(deaths * risk_ratios['urban']))) if deaths >= 3 else int(np.random.random() < risk_ratios['urban'])
                    disease_deaths = deaths - natural_deaths - urban_deaths
                    disease_deaths = max(0, disease_deaths)
                    
                    month_deaths['causes']['natural'] += natural_deaths
                    month_deaths['causes']['urban'] += urban_deaths
                    month_deaths['causes']['disease'] += disease_deaths
                    log_debug('DEBUG', f'Month {month} kitten deaths: {deaths} (Natural: {natural_deaths}, Urban: {urban_deaths}, Disease: {disease_deaths})')

            # Process adult deaths (both reproductive and sterilized)
            for group in ['reproductive', 'sterilized']:
                for count, age in colony[group]:
                    count = int(float(count))  # Ensure count is an integer
                    raw_deaths = float(count) * float(adult_mortality)
                    log_debug('DEBUG', f'Month {month} processing {group} cats: count={count}, age={age}, raw_deaths={raw_deaths}')
                    
                    # For small groups, use probabilistic death
                    if raw_deaths < 1 and raw_deaths > 0:
                        deaths = 1 if np.random.random() < raw_deaths else 0
                    else:
                        deaths = int(round(raw_deaths))
                    survivors = max(0, count - deaths)
                    
                    if survivors > 0:
                        new_colony[group].append([survivors, age])
                    
                    if deaths > 0:
                        month_deaths['adults'] += deaths
                        # Distribute deaths by cause based on risk ratios with minimum counts
                        natural_deaths = max(1, int(round(deaths * risk_ratios['natural']))) if deaths >= 3 else int(np.random.random() < risk_ratios['natural'])
                        urban_deaths = max(1, int(round(deaths * risk_ratios['urban']))) if deaths >= 3 else int(np.random.random() < risk_ratios['urban'])
                        disease_deaths = deaths - natural_deaths - urban_deaths
                        disease_deaths = max(0, disease_deaths)
                        
                        month_deaths['causes']['natural'] += natural_deaths
                        month_deaths['causes']['urban'] += urban_deaths
                        month_deaths['causes']['disease'] += disease_deaths
                        
                        # Log deaths for debugging
                        log_debug('DEBUG', f'Month {month} {group} deaths: {deaths} (Natural: {natural_deaths}, Urban: {urban_deaths}, Disease: {disease_deaths})')
            
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
            
            # Process sterilization with both adults and kittens
            if monthly_sterilization > 0 or unmet_sterilizations > 0:
                # Add any unmet sterilizations from previous month
                total_sterilizations = monthly_sterilization + unmet_sterilizations
                
                # Calculate total cats eligible for sterilization
                total_reproductive = sum(int(float(count)) for count, _ in colony['reproductive'])
                total_kittens = sum(int(float(count)) for count, age in colony['young_kittens'] if int(float(age)) >= MIN_BREEDING_AGE)
                total_eligible = total_reproductive + total_kittens
                
                log_debug('DEBUG', f'Month {month} sterilization stats:')
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
                                        # Sterilize entire group
                                        colony['sterilized_kittens'].append([count, age])
                                        cats_to_sterilize -= count
                                    else:
                                        # Split group
                                        colony['sterilized_kittens'].append([cats_to_sterilize, age])
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
            maturity_age = MIN_BREEDING_AGE  # Use MIN_BREEDING_AGE instead of params value
            
            # Process unsterilized kittens
            for count, age in colony['young_kittens']:
                count = int(float(count))
                age = int(float(age))
                
                # Apply kitten mortality
                kitten_deaths = int(round(float(count) * float(kitten_mortality)))
                survivors = count - kitten_deaths
                
                if survivors > 0:
                    if age >= maturity_age:
                        # When kittens mature, add them to reproductive group
                        colony['reproductive'].append([survivors, maturity_age])
                        matured_count += survivors
                        log_debug('DEBUG', f'Month {month}: {survivors} unsterilized kittens matured at age {maturity_age} months')
                    else:
                        # Keep track of surviving kittens that are still too young
                        new_unsterilized_kittens.append([survivors, age + 1])
                        log_debug('DEBUG', f'Month {month}: {survivors} unsterilized kittens aged to {age + 1} months')
                
                if kitten_deaths > 0:
                    month_deaths['kittens'] += kitten_deaths
                    # Distribute deaths by cause
                    natural_deaths = max(1, int(round(kitten_deaths * risk_ratios['natural']))) if kitten_deaths >= 3 else int(np.random.random() < risk_ratios['natural'])
                    urban_deaths = max(1, int(round(kitten_deaths * risk_ratios['urban']))) if kitten_deaths >= 3 else int(np.random.random() < risk_ratios['urban'])
                    disease_deaths = kitten_deaths - natural_deaths - urban_deaths
                    disease_deaths = max(0, disease_deaths)
                    
                    month_deaths['causes']['natural'] += natural_deaths
                    month_deaths['causes']['urban'] += urban_deaths
                    month_deaths['causes']['disease'] += disease_deaths
            
            # Process sterilized kittens
            for count, age in colony['sterilized_kittens']:
                count = int(float(count))
                age = int(float(age))
                
                # Apply kitten mortality
                kitten_deaths = int(round(float(count) * float(kitten_mortality)))
                survivors = count - kitten_deaths
                
                if survivors > 0:
                    if age >= maturity_age:
                        # When sterilized kittens mature, add them to sterilized group
                        colony['sterilized'].append([survivors, maturity_age])
                        matured_count += survivors
                        log_debug('DEBUG', f'Month {month}: {survivors} sterilized kittens matured at age {maturity_age} months')
                    else:
                        # Keep track of surviving kittens that are still too young
                        new_sterilized_kittens.append([survivors, age + 1])
                        log_debug('DEBUG', f'Month {month}: {survivors} sterilized kittens aged to {age + 1} months')
                
                if kitten_deaths > 0:
                    month_deaths['kittens'] += kitten_deaths
                    # Distribute deaths by cause
                    natural_deaths = max(1, int(round(kitten_deaths * risk_ratios['natural']))) if kitten_deaths >= 3 else int(np.random.random() < risk_ratios['natural'])
                    urban_deaths = max(1, int(round(kitten_deaths * risk_ratios['urban']))) if kitten_deaths >= 3 else int(np.random.random() < risk_ratios['urban'])
                    disease_deaths = kitten_deaths - natural_deaths - urban_deaths
                    disease_deaths = max(0, disease_deaths)
                    
                    month_deaths['causes']['natural'] += natural_deaths
                    month_deaths['causes']['urban'] += urban_deaths
                    month_deaths['causes']['disease'] += disease_deaths
            
            # Update kitten lists
            colony['young_kittens'] = new_unsterilized_kittens
            colony['sterilized_kittens'] = new_sterilized_kittens
            if matured_count > 0:
                log_debug('DEBUG', f'Month {month}: {matured_count} kittens matured into reproductive adults')
            
            # Process breeding with age constraints and pregnancy limits
            if colony['reproductive']:
                # Calculate breeding rate based on litters per year
                # Cats can have 2-3 litters per year, with 2 month gestation
                gestation_months = GESTATION_MONTHS
                monthly_breeding_chance = float(params['breeding_rate'])  # Base chance each month
                
                # Only count females of breeding age
                breeding_females = sum(
                    int(float(count)) * float(params['female_ratio'])
                    for count, age in colony['reproductive']
                    if MIN_BREEDING_AGE <= float(age) <= MAX_BREEDING_AGE
                )
                
                log_debug('DEBUG', f'Month {month}: Breeding chance: {monthly_breeding_chance:.3f}')
                log_debug('DEBUG', f'Month {month}: {breeding_females:.1f} breeding-age females available')
                
                # Calculate available females (not currently pregnant)
                current_pregnancies = float(sum(pregnant_females))
                available_females = float(breeding_females - current_pregnancies)
                
                if available_females > 0:
                    # Combine environmental factors
                    environmental_factor = float((stress_factor + seasonal_factor + density_effect) / 3)
                    
                    # Calculate breeding success using the colony structure and current month
                    from .utils.simulation_utils import calculate_breeding_success
                    breeding_success = calculate_breeding_success(params, colony, environmental_factor, month % 12)
                    
                    # Calculate new pregnancies - each available female has a chance to become pregnant
                    pregnancy_chance = monthly_breeding_chance * breeding_success
                    new_pregnant = int(round(available_females * pregnancy_chance))
                    
                    if new_pregnant > 0:
                        log_debug('DEBUG', f'Month {month}: {new_pregnant} new females became pregnant (success rate: {breeding_success:.2f})')
                        pregnant_females.append(new_pregnant)
            
            # Process births from previous pregnancies
            if pregnant_females and len(pregnant_females) >= gestation_months:
                births = pregnant_females.pop(0)  # Get the oldest pregnancy group
                if births > 0:
                    # Calculate base number of kittens
                    base_litter_size = float(params['kittens_per_litter'])
                    # Adjust for seasonal effects
                    adjusted_litter_size = base_litter_size * (0.8 + 0.4 * seasonal_factor)  # 80-120% of base size
                    # Calculate total kittens born
                    kittens = int(round(float(births) * adjusted_litter_size))
                    
                    log_debug('DEBUG', f'Month {month} births: {births} females giving birth to {kittens} kittens (avg {adjusted_litter_size:.1f} per litter)')
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
            monthly_sterilized.append(sterilized_count + sterilized_kitten_count)
            monthly_reproductive.append(reproductive_count)
            monthly_kittens.append(unsterilized_kitten_count + sterilized_kitten_count)
            monthly_costs.append(month_cost)
            monthly_densities.append(current_population / params.get('territory_size', 1000))
            
            log_debug('DEBUG', f'Month {month} population breakdown:')
            log_debug('DEBUG', f'  Young kittens: {sum(count for count, _ in colony["young_kittens"])}')
            log_debug('DEBUG', f'  Reproductive: {sum(count for count, _ in colony["reproductive"])}')
            log_debug('DEBUG', f'  Sterilized: {sum(count for count, _ in colony["sterilized"])}')
            log_debug('DEBUG', f'  Total population: {current_population}')
            
            # Store death statistics
            monthly_deaths_other.append(0)  # Add other deaths to monthly data
            
            # Calculate density relative to territory
            density = current_population / params['territory_size'] if params['territory_size'] > 0 else float('inf')
            
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
        from .utils.logging_utils import log_calculation_result
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
