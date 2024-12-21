"""Utility functions for cat colony simulation calculations."""

import numpy as np
import logging
import traceback

logger = logging.getLogger(__name__)

def calculate_seasonal_factor(month, amplitude=0.2, peak_month=3):
    """Calculate seasonal breeding factor with smoother transitions."""
    try:
        # Shift the peak to occur at the specified month
        shifted_month = (month - peak_month) % 12
        # Create a smoother seasonal curve using a sine wave
        return 1.0 - amplitude * np.cos(2 * np.pi * shifted_month / 12)
    except Exception as e:
        logger.error(f"Error in calculate_seasonal_factor: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_density_impact(current_population, capacity=1000):
    """Calculate density impact with gentler effects."""
    try:
        # Provide a more gradual density impact
        base_factor = 0.9  # Minimum impact is 90% of normal
        variable_factor = 0.1  # Only 10% variation based on density
        
        # Use a gentler logistic curve for population density effects
        density_effect = 1 / (1 + np.exp((current_population - capacity) / (capacity * 0.5)))
        return base_factor + variable_factor * density_effect
    except Exception as e:
        logger.error(f"Error in calculate_density_impact: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_resource_availability(current_population, params):
    """Calculate resource availability with more balanced effects."""
    try:
        # Base resource calculation with dampened effects
        base_resources = min(1.0, (
            params['base_food_capacity'] * 
            params['water_availability'] * 
            params['shelter_quality']
        ) ** 0.5)  # Square root to dampen multiplicative effects
        
        # Calculate population pressure with gentler curve
        population_pressure = np.exp(
            -0.5 * params['food_scaling_factor'] * 
            (current_population / params['territory_size'])
        )
        
        # Calculate support factor with dampened effects
        human_support = min(1.0, (
            params['caretaker_support'] * 
            params['feeding_consistency'] * 
            (1 - 0.5 * params['human_interference'])  # Reduce negative impact
        ) ** 0.5)  # Square root to dampen multiplicative effects
        
        # Combine factors with minimum threshold
        combined_factor = (base_resources * population_pressure * human_support)
        return max(0.7, min(1.0, combined_factor))  # Ensure factor stays between 0.7 and 1.0
    except Exception as e:
        logger.error(f"Error in calculate_resource_availability: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_resource_impact(resource_availability):
    """Calculate the impact of resource availability on population growth."""
    try:
        # Ensure resource availability stays within bounds
        resource_availability = max(0.0, min(1.0, resource_availability))
        
        # Calculate impact with a gentler curve
        # When resources are abundant (1.0), impact is minimal (1.0)
        # When resources are scarce (0.0), impact reduces growth significantly (0.5)
        base_impact = 0.5  # Minimum impact when resources are scarce
        variable_impact = 0.5  # Maximum additional impact from resources
        
        return base_impact + variable_impact * resource_availability
    except Exception as e:
        logger.error(f"Error in calculate_resource_impact: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_monthly_mortality(params, colony):
    """Calculate monthly mortality rates based on risks and environmental factors."""
    try:
        # Base monthly mortality rates with gentler conversion
        base_adult_mortality = 1 - (params['adult_survival_rate'] ** (1/12))
        base_kitten_mortality = 1 - (params['kitten_survival_rate'] ** (1/12))
        
        # Risk factors (multiplicative with dampening)
        total_risk = (params['urban_risk'] + params['disease_risk'] + params['natural_risk']) / 3
        risk_multiplier = 1 + (total_risk * 0.5)  # Reduced impact of risks
        risk_multiplier = min(1.5, risk_multiplier)  # Lower cap for more realistic mortality
        
        # Environmental modifiers with stronger protective effect
        environment_protection = min(1.0, (
            params.get('shelter_quality', 0.8) * 
            params.get('caretaker_support', 0.8) *
            params.get('feeding_consistency', 0.8)
        ) ** 0.2)  # Stronger protective effect
        
        # Final mortality rates with increased environmental protection
        risk_factor = risk_multiplier * (1 - environment_protection * 0.9)  # Increased protection factor
        
        # Ensure minimum and maximum mortality rates
        adult_mortality = max(base_adult_mortality * 0.5, min(0.6, base_adult_mortality * risk_factor))
        kitten_mortality = max(base_kitten_mortality * 0.5, min(0.7, base_kitten_mortality * risk_factor))
        
        return adult_mortality, kitten_mortality
        
    except Exception as e:
        logger.error(f"Error in calculate_monthly_mortality: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_resource_limit(params, current_population):
    """Calculate resource-based population limits and stress factors."""
    try:
        # Calculate maximum sustainable population based on resources
        base_capacity = params['territory_size'] * params['base_food_capacity']
        resource_factor = min(1.0, (
            params['water_availability'] * 
            params['shelter_quality'] * 
            params.get('caretaker_support', 0.8) *
            params.get('feeding_consistency', 0.9)
        ) ** 0.25)  # Fourth root for very dampened effect
        
        max_sustainable = base_capacity * resource_factor
        
        # Calculate stress factor as population approaches capacity
        stress_factor = 1.0
        if current_population > 0:  # Prevent division by zero
            population_ratio = current_population / max_sustainable
            if population_ratio > 1:
                stress_factor = max(0.5, 1 - (0.5 * (population_ratio - 1)))
            elif population_ratio > 0.8:
                stress_factor = 1 - (0.2 * (population_ratio - 0.8))
        
        return stress_factor, max_sustainable
        
    except Exception as e:
        logger.error(f"Error in calculate_resource_limit: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_breeding_success(params, colony, environment_factor):
    """Calculate breeding success rate with environmental and density factors."""
    try:
        # Count total cats and reproductive females
        total_cats = (
            sum(int(float(count)) for count, _ in colony['young_kittens']) +
            sum(int(float(count)) for count, _ in colony['reproductive']) +
            sum(int(float(count)) for count, _ in colony['sterilized'])
        )
        reproductive_females = sum(count for count, _ in colony['reproductive']) * params['female_ratio']
        
        if reproductive_females == 0:
            return 0.0
            
        # Base breeding rate with gentler environmental impact
        effective_rate = params['breeding_rate'] * (0.8 + 0.2 * environment_factor)  # Minimum 80% of base rate
        
        # Density-dependent reduction with higher threshold
        density = total_cats / params['territory_size']
        density_factor = max(0.4, 1 - (density / (params['density_impact_threshold'] * 1.5)))  # Increased threshold by 50%
        
        # Social factors - breeding success increases with moderate colony size
        social_factor = 1.0
        if reproductive_females < 2:
            social_factor = 0.8  # Less reduction for small colonies
        elif reproductive_females > 15:  # Increased threshold from 10 to 15
            social_factor = max(0.7, 1 - (0.02 * (reproductive_females - 15)))  # Gentler reduction
            
        # Combine factors with minimum threshold
        success_rate = effective_rate * density_factor * social_factor
        return max(0.4, min(1.0, success_rate))  # Ensure minimum 40% success rate
    except Exception as e:
        logger.error(f"Error in calculate_breeding_success: {str(e)}")
        logger.error(traceback.format_exc())
        raise
