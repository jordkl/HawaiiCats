"""Utility functions for cat colony simulation calculations."""

import numpy as np
import logging
import traceback

logger = logging.getLogger(__name__)

def calculate_seasonal_factor(month, amplitude=0.1, peak_month=3):
    """Calculate seasonal breeding factor with minimal seasonal variation for Hawaii."""
    try:
        month = int(month)
        amplitude = float(amplitude)
        peak_month = int(peak_month)
        
        # Shift the peak to occur at the specified month
        shifted_month = (month - peak_month) % 12
        
        # Use a gentler cosine wave for Hawaii's minimal seasonality
        # Reduce amplitude impact and add higher base level
        base_level = 0.95  # High base level for year-round breeding
        seasonal_variation = amplitude * np.cos(2 * np.pi * shifted_month / 12)
        
        return float(base_level - seasonal_variation)
    except Exception as e:
        logger.error(f"Error in calculate_seasonal_factor: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_density_impact(current_population, params):
    """Calculate the impact of population density with Hawaii-specific adaptations."""
    try:
        current_population = float(current_population)
        territory_size = float(params.get('territory_size', 1000))
        impact_threshold = float(params.get('density_impact_threshold', 1.5))
        urban_factor = float(params.get('urban_environment', 0.7))  # Higher value = more urban
        
        # Calculate density relative to territory
        density = current_population / territory_size
        
        # Adjust impact threshold based on environment type
        # Urban areas can support higher densities
        adjusted_threshold = impact_threshold * (1 + 0.5 * urban_factor)
        
        # Use configurable sigmoid curve with environment-based steepness
        k = 4.0 * (1 - 0.3 * urban_factor)  # Gentler curve in urban areas
        midpoint = territory_size * adjusted_threshold / 2
        impact = 1.0 / (1.0 + np.exp(k * (density - midpoint)))
        
        # Higher minimum breeding potential in urban areas
        min_potential = 0.3 + (0.2 * urban_factor)
        return float(max(min_potential, impact))
    except Exception as e:
        logger.error(f"Error in calculate_density_impact: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_resource_availability(current_population, params):
    """Calculate resource availability with more balanced effects."""
    try:
        current_population = float(current_population)
        base_resources = float(params.get('base_resources', 0.95))  # Higher base resources for Hawaii
        resource_variability = float(params.get('resource_variability', 0.1))  # Lower variability
        carrying_capacity = float(params.get('carrying_capacity', 1500))  # Higher carrying capacity
        
        # Reduced random variation for stable climate
        resource_level = base_resources * (1.0 + np.random.uniform(-resource_variability/3, resource_variability/3))
        
        # Gentler population pressure curve for Hawaii's conditions
        population_ratio = current_population / carrying_capacity
        pressure = 1.0 / (1.0 + np.exp(-1.5 * (population_ratio - 1.0)))  # Reduced steepness
        
        # Combine factors with higher minimum threshold
        availability = float(resource_level * (1.0 - 0.6 * pressure))  # Max 60% reduction
        return float(max(0.4, min(1.0, availability)))  # Minimum 40% resources
    except Exception as e:
        logger.error(f"Error in calculate_resource_availability: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_resource_impact(resource_availability):
    """Calculate the impact of resource availability on population growth."""
    try:
        # Non-linear response to resource availability
        impact = np.power(resource_availability, 1.5)  # Steeper decline at low resources
        return max(0.1, min(1.0, impact))  # Ensure result is between 0.1 and 1.0
    except Exception as e:
        logger.error(f"Error in calculate_resource_impact: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_monthly_mortality(params, colony):
    """Calculate monthly mortality rates with improved biological realism."""
    try:
        # Convert survival rates to monthly probabilities - using more optimistic rates for Hawaii
        base_adult_mortality = 1.0 - np.power(float(params.get('adult_survival_rate', 0.95)), 1.0/12)  # Increased base survival
        base_kitten_mortality = 1.0 - np.power(float(params.get('kitten_survival_rate', 0.85)), 1.0/12)  # Increased kitten survival
        
        # Risk factors - reduced for Hawaii's conditions
        urban_risk = float(params.get('urban_risk', 0.03))  # Reduced urban risk
        disease_risk = float(params.get('disease_risk', 0.03))  # Reduced disease risk due to climate
        natural_risk = float(params.get('natural_risk', 0.02))  # Minimal natural risks
        
        # Calculate density-dependent disease risk with gentler scaling
        total_cats = sum(int(float(count)) for group in colony.values() for count, _ in group)
        density_factor = min(2.0, 1.0 + total_cats / float(params.get('territory_size', 1000)))  # Reduced max impact
        disease_mortality = disease_risk * density_factor
        
        # Combine mortality factors with lower caps for Hawaii
        adult_mortality = min(0.3, base_adult_mortality + urban_risk + disease_mortality + natural_risk)  # Lower cap
        kitten_mortality = min(0.4, base_kitten_mortality + 0.5*urban_risk + disease_mortality + natural_risk)  # Lower cap
        
        return float(adult_mortality), float(kitten_mortality)
    except Exception as e:
        logger.error(f"Error in calculate_monthly_mortality: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_resource_limit(params, current_population):
    """Calculate resource-based population limits and stress factors."""
    try:
        base_capacity = params.get('carrying_capacity', 1000)
        resource_stress = params.get('resource_stress_factor', 0.2)
        
        # Calculate current resource stress
        population_ratio = current_population / base_capacity
        stress_factor = 1.0 / (1.0 + np.exp(-resource_stress * (population_ratio - 1)))
        
        # Calculate adjusted capacity
        adjusted_capacity = base_capacity * (1 - stress_factor)
        
        # Return both stress_factor and adjusted capacity
        return stress_factor, max(current_population * 0.5, adjusted_capacity)  # Ensure minimum viable population
    except Exception as e:
        logger.error(f"Error in calculate_resource_limit: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_breeding_success(params, colony, environment_factor):
    """Calculate breeding success rate with enhanced reproduction for Hawaii."""
    try:
        base_success = float(params.get('base_breeding_success', 0.95))  # Very high base success
        age_factor = float(params.get('age_breeding_factor', 0.06))  # Minimal age impact
        stress_impact = float(params.get('stress_impact', 0.12))  # Very low stress impact
        early_breeding = float(params.get('early_breeding_age', 5))  # Earlier breeding age
        peak_breeding = float(params.get('peak_breeding_age', 36))  # Extended peak breeding
        
        success_rates = []
        for age in colony:
            try:
                age = float(str(age).strip())
                
                # Enhanced age-dependent breeding success
                if age < early_breeding:
                    # Gradual increase to breeding age
                    age_success = base_success * (age / early_breeding) * 0.8
                elif age <= peak_breeding:
                    # Extended prime breeding period with minimal decline
                    relative_age = (age - early_breeding) / (peak_breeding - early_breeding)
                    age_success = base_success * (1.0 - age_factor * relative_age * relative_age)
                else:
                    # Gentler decline after peak breeding age
                    relative_age = (age - peak_breeding) / 24  # 24 months decline period
                    age_success = base_success * (1.0 - age_factor * relative_age)
                
                # Environmental impact with higher minimum
                env_success = age_success * max(0.8, environment_factor)
                
                # Reduced stress impact for Hawaii
                stress_modifier = 1.0 - (stress_impact * (1.0 - environment_factor))
                final_success = env_success * stress_modifier
                
                # Higher minimum success rate
                success_rates.append(max(0.3, min(1.0, final_success)))
            except (ValueError, TypeError) as e:
                logging.error(f"Error processing age value: {age} in breeding success calculation")
                logging.error(str(e))
                success_rates.append(base_success * environment_factor)
        
        return success_rates
    except Exception as e:
        logger.error(f"Error in calculate_breeding_success: {str(e)}")
        logger.error(traceback.format_exc())
        raise
