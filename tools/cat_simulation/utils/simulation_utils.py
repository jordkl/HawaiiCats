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
    """Calculate monthly mortality rates with improved biological realism and territory effects."""
    try:
        # Convert annual mortality rates to monthly
        # For adult survival rate of 0.75 (25% annual mortality), monthly rate is about 0.024
        # For kitten survival rate of 0.55 (45% annual mortality), monthly rate is about 0.05
        base_adult_mortality = -np.log(0.75) / 12  # Monthly rate from annual 25% mortality
        base_kitten_mortality = -np.log(0.55) / 12  # Monthly rate from annual 45% mortality
        
        logger.info(f"Base mortality rates - Adult: {base_adult_mortality:.4f}, Kitten: {base_kitten_mortality:.4f}")
        
        # Calculate total population and unsterilized males
        total_cats = (
            sum(int(float(count)) for count, _ in colony['young_kittens']) +
            sum(int(float(count)) for count, _ in colony['reproductive']) +
            sum(int(float(count)) for count, _ in colony['sterilized']) +
            sum(int(float(count)) for count, _ in colony.get('sterilized_kittens', []))  # Include sterilized kittens
        )
        
        if total_cats == 0:
            return 0.0, 0.0  # No mortality if no cats
        
        logger.info(f"Total population: {total_cats}")
        
        # Calculate unsterilized males (affects kitten mortality)
        reproductive_cats = sum(int(float(count)) for count, _ in colony['reproductive'])
        unsterilized_males = reproductive_cats * (1 - float(params.get('female_ratio', 0.5)))
        male_aggression = float(params.get('male_aggression_factor', 0.3))  # Increased from 0.2
        
        logger.info(f"Reproductive cats: {reproductive_cats}, Unsterilized males: {unsterilized_males:.1f}")
        
        # Territory and density calculations
        territory_size = float(params.get('territory_size', 500))
        cats_per_acre = float(params.get('cats_per_acre', 2.0))  # Reduced from 2.5
        territory_scaling = float(params.get('territory_scaling_factor', 0.4))  # Increased from 0.3
        max_sustainable = territory_size * cats_per_acre
        
        # Calculate density effect with stronger territory influence
        density = total_cats / max(1, territory_size)
        density_threshold = float(params.get('density_impact_threshold', 0.4))  # Reduced from 0.5
        density_mortality = float(params.get('density_mortality_factor', 0.35))  # Increased from 0.25
        territory_competition = float(params.get('territory_competition_factor', 0.3))  # Increased from 0.2
        
        logger.info(f"Territory metrics - Size: {territory_size}, Density: {density:.2f}, Max sustainable: {max_sustainable}")
        
        # Exponential density effect when population exceeds territory capacity
        overpopulation_ratio = total_cats / max(1, max_sustainable)
        density_factor = 1.0 + (density_mortality * (
            np.exp(max(0, (density / density_threshold - 1))) - 1
        ))
        
        logger.info(f"Density impact - Overpopulation ratio: {overpopulation_ratio:.2f}, Density factor: {density_factor:.2f}")
        
        # Territory competition effect (increases with population density)
        competition_factor = 1.0 + (territory_competition * (
            np.exp(max(0, (overpopulation_ratio - 1)) * territory_scaling) - 1
        ))
        
        logger.info(f"Competition factor: {competition_factor:.2f}")
        
        # Environmental Factors
        shelter_quality = float(params.get('shelter_quality', 0.6))
        caretaker_support = float(params.get('caretaker_support', 0.6))
        feeding_consistency = float(params.get('feeding_consistency', 0.7))
        water_availability = float(params.get('water_availability', 0.8))
        
        # Resource stress increases with territory overcrowding
        base_resource_stress = (
            0.3 * (1 - feeding_consistency) +
            0.2 * (1 - water_availability) +
            0.3 * (1 - shelter_quality) +
            0.2 * (1 - caretaker_support)
        )
        resource_stress = base_resource_stress * (1 + max(0, overpopulation_ratio - 1))
        
        logger.info(f"Resource stress: {resource_stress:.2f}")
        
        # Risk factors with territory scaling
        urban_risk = float(params.get('urban_risk', 0.15))
        disease_risk = float(params.get('disease_risk', 0.1)) * competition_factor
        natural_risk = float(params.get('natural_risk', 0.1))
        
        # Risk multiplier increases with territory competition
        risk_multiplier = 1.0 + (urban_risk + disease_risk + natural_risk) * competition_factor
        
        logger.info(f"Risk multiplier: {risk_multiplier:.2f}")
        
        # Calculate final mortality rates with increased territory influence
        adult_mortality = min(0.99, max(0.001,  # Ensure mortality is between 0.1% and 99%
            base_adult_mortality *
            risk_multiplier *
            (density_factor ** 1.2) *  # Increased from 1.0
            (competition_factor ** 1.3) *  # Increased from 1.0
            (1.0 + 1.5 * resource_stress)  # Increased from 1.0
        ))
        
        # Kitten mortality with stronger territory effects
        male_aggression_impact = 1.0 + (male_aggression * unsterilized_males / max(1, total_cats))
        kitten_mortality = min(0.99, max(0.001,  # Ensure mortality is between 0.1% and 99%
            base_kitten_mortality *
            risk_multiplier *
            (density_factor ** 2.0) *  # Increased from 1.8
            (competition_factor ** 1.8) *  # Increased from 1.5
            (1.0 + 2.5 * resource_stress) *  # Increased from 2.0
            male_aggression_impact
        ))
        
        logger.info(f"Final mortality rates - Adult: {adult_mortality:.4f}, Kitten: {kitten_mortality:.4f}")
        
        return float(adult_mortality), float(kitten_mortality)
        
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

def calculate_breeding_success(params, colony, environment_factor, current_month=None):
    """Calculate breeding success rate with enhanced reproduction for Hawaii."""
    try:
        # Calculate total population and reproductive females
        total_cats = (
            sum(int(float(count)) for count, _ in colony['young_kittens']) +
            sum(int(float(count)) for count, _ in colony['reproductive']) +
            sum(int(float(count)) for count, _ in colony['sterilized']) +
            sum(int(float(count)) for count, _ in colony.get('sterilized_kittens', []))
        )
        reproductive_females = sum(count for count, _ in colony['reproductive']) * float(params.get('female_ratio', 0.5))
        
        if reproductive_females == 0:
            return 0.0
            
        # Environmental impact with higher base rate for Hawaii
        effective_rate = float(params.get('breeding_rate', 0.85)) * (0.9 + 0.1 * environment_factor)
        
        # Density-dependent effects with higher thresholds for Hawaii
        territory_size = float(params.get('territory_size', 50))  # Default to 50 instead of 1000
        density = total_cats / territory_size if territory_size > 0 else float('inf')
        density_threshold = float(params.get('density_impact_threshold', 1.2))
        density_factor = max(0.7, 1.0 - (density / (density_threshold * 2.0)))  # Increased minimum and threshold
        
        # Social factors optimized for Hawaii colonies
        social_factor = 1.0
        if reproductive_females < 2:
            social_factor = 0.9  # Less reduction for small colonies
        elif reproductive_females > 20:  # Higher threshold
            social_factor = max(0.8, 1.0 - (0.01 * (reproductive_females - 20)))
        
        # Seasonal adjustment (reduced effect for Hawaii)
        seasonal_amplitude = float(params.get('seasonal_breeding_amplitude', 0.1))  # Reduced default amplitude
        peak_month = int(params.get('peak_breeding_month', 3))
        
        # Use simulation month instead of real-world month
        if current_month is None:
            current_month = peak_month  # Default to peak month if not provided
        month_in_cycle = current_month % 12
        
        seasonal_factor = 1.0 - seasonal_amplitude * abs(((month_in_cycle - peak_month + 6) % 12) - 6) / 6.0
        
        # Combine all factors with higher minimum threshold
        success_rate = effective_rate * density_factor * social_factor * seasonal_factor
        return float(max(0.6, min(1.0, success_rate)))  # Increased minimum success rate
        
    except Exception as e:
        logger.error(f"Error in calculate_breeding_success: {str(e)}")
        logger.error(traceback.format_exc())
        raise
