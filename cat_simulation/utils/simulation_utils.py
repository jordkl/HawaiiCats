"""Utility functions for cat colony simulation calculations."""

import numpy as np
import logging
import traceback
from datetime import datetime

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
        # Convert survival rates to monthly probabilities
        base_adult_mortality = 1.0 - np.power(float(params.get('adult_survival_rate', 0.95)), 1.0/12)
        base_kitten_mortality = 1.0 - np.power(float(params.get('kitten_survival_rate', 0.85)), 1.0/12)
        
        # Combine risks multiplicatively with dampening
        risk_multiplier = (1 + float(params.get('urban_risk', 0.03))) * \
                         (1 + float(params.get('disease_risk', 0.03))) * \
                         (1 + float(params.get('natural_risk', 0.02)))
        risk_multiplier = min(1.5, risk_multiplier)  # Cap maximum risk
        
        # Calculate environmental protection with smoother scaling
        protection = min(1.0, (
            float(params.get('shelter_quality', 0.8)) * 
            float(params.get('caretaker_support', 0.8)) * 
            float(params.get('feeding_consistency', 0.8))
        ) ** 0.3)  # Cube root for gentler scaling
        
        # Calculate density-dependent disease risk
        total_cats = sum(int(float(count)) for group in colony.values() for count, _ in group)
        density_factor = min(1.5, 1.0 + total_cats / float(params.get('territory_size', 1000)))
        
        # Apply all factors with proper bounds
        adult_mortality = base_adult_mortality * risk_multiplier * (1 - protection * 0.8) * density_factor
        kitten_mortality = base_kitten_mortality * risk_multiplier * (1 - protection * 0.7) * density_factor
        
        # Ensure reasonable bounds
        return float(min(0.3, adult_mortality)), float(min(0.4, kitten_mortality))
    except Exception as e:
        logger.error(f"Error in calculate_monthly_mortality: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_resource_limit(params, current_population):
    """Calculate resource-based population limits and stress factors."""
    try:
        # Calculate base capacity from territory and food
        base_capacity = float(params.get('territory_size', 1000)) * \
                       float(params.get('base_food_capacity', 0.95))
        
        # Calculate resource factor with dampened multiplicative effects
        resource_factor = min(1.0, (
            float(params.get('water_availability', 0.9)) * 
            float(params.get('shelter_quality', 0.85)) * 
            float(params.get('caretaker_support', 0.8)) * 
            float(params.get('feeding_consistency', 0.85))
        ) ** 0.25)  # Fourth root for gentler scaling
        
        # Calculate maximum sustainable population
        max_sustainable = base_capacity * resource_factor
        
        # Calculate stress factor with smoother transition
        if current_population > 0:
            density_ratio = float(current_population) / max_sustainable
            if density_ratio > 1.2:  # Higher threshold for stress onset
                stress_factor = max(0.6, 1.0 / (1.0 + np.exp((density_ratio - 1.5) / 0.3)))
            elif density_ratio > 0.8:  # Earlier but gentler stress onset
                stress_factor = 1.0 - (0.2 * (density_ratio - 0.8))
            else:
                stress_factor = 1.0
        else:
            stress_factor = 1.0
        
        return float(stress_factor), float(max(current_population * 0.5, max_sustainable))
    except Exception as e:
        logger.error(f"Error in calculate_resource_limit: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_breeding_success(params, colony, environment_factor):
    """Calculate breeding success rate with enhanced reproduction for Hawaii."""
    try:
        # Base parameters with safe conversion
        breeding_rate = float(params.get('breeding_rate', 0.85))
        female_ratio = float(params.get('female_ratio', 0.5))
        
        # Count reproductive population
        total_cats = sum(count for group in colony.values() for count, _ in group)
        reproductive_females = sum(count for count, _ in colony['reproductive']) * female_ratio
        
        if reproductive_females == 0:
            return 0.0
            
        # Environmental impact with higher minimum for Hawaii
        effective_rate = breeding_rate * (0.85 + 0.15 * environment_factor)
        
        # Density-dependent effects with higher thresholds for Hawaii
        density = total_cats / float(params.get('territory_size', 1000))
        density_factor = max(0.5, 1.0 - (density / (float(params.get('density_impact_threshold', 1.2)) * 1.5)))
        
        # Social factors optimized for Hawaii colonies
        social_factor = 1.0
        if reproductive_females < 2:
            social_factor = 0.85  # Less reduction for small colonies
        elif reproductive_females > 15:  # Higher threshold
            social_factor = max(0.75, 1.0 - (0.015 * (reproductive_females - 15)))
        
        # Seasonal adjustment (reduced effect for Hawaii)
        seasonal_amplitude = float(params.get('seasonal_breeding_amplitude', 0.2))
        peak_month = int(params.get('peak_breeding_month', 3))
        current_month = datetime.now().month
        seasonal_factor = 1.0 - seasonal_amplitude * abs(((current_month - peak_month + 6) % 12) - 6) / 6.0
        
        # Combine all factors with minimum threshold
        success_rate = effective_rate * density_factor * social_factor * seasonal_factor
        return float(max(0.4, min(1.0, success_rate)))  # Ensure reasonable bounds
        
    except Exception as e:
        logger.error(f"Error in calculate_breeding_success: {str(e)}")
        logger.error(traceback.format_exc())
        raise
