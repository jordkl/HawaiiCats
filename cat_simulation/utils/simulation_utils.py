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
        # Base mortality rates (annual rates converted to monthly)
        # 15% annual mortality = ~1.3% monthly for adults
        # 25% annual mortality = ~2.1% monthly for kittens
        base_adult_mortality = 0.013  # Monthly base rate
        base_kitten_mortality = 0.021  # Monthly base rate for kittens
        
        # Calculate total population
        total_cats = (
            sum(int(float(count)) for count, _ in colony['young_kittens']) +
            sum(int(float(count)) for count, _ in colony['reproductive']) +
            sum(int(float(count)) for count, _ in colony['sterilized'])
        )
        
        # Environmental Factors - each scaled from 0 to 1
        shelter_quality = float(params.get('shelter_quality', 0.8))
        caretaker_support = float(params.get('caretaker_support', 0.8))
        feeding_consistency = float(params.get('feeding_consistency', 0.8))
        water_availability = float(params.get('water_availability', 0.9))
        
        # Calculate environmental stress
        # More balanced weights and stronger impact
        resource_stress = (
            0.3 * (1 - feeding_consistency) +   # Food stress (30%)
            0.2 * (1 - water_availability) +    # Water stress (20%)
            0.3 * (1 - shelter_quality) +       # Shelter stress (30%)
            0.2 * (1 - caretaker_support)       # Care stress (20%)
        )
        
        # Risk factors with base rates
        urban_risk = float(params.get('urban_risk', 0.05))
        disease_risk = float(params.get('disease_risk', 0.05))
        natural_risk = float(params.get('natural_risk', 0.05))
        
        # Calculate risk impacts with stronger environmental effects
        # Poor conditions double the impact of risks
        risk_multiplier = 1.0 + (urban_risk + disease_risk + natural_risk) * (2.0 - min(1.0, (
            shelter_quality +
            caretaker_support +
            feeding_consistency +
            water_availability
        ) / 4))
        
        # Density impact calculation
        territory_size = float(params.get('territory_size', 1000))
        density = total_cats / territory_size
        
        # Density effect is stronger with poor environmental conditions
        # Poor conditions effectively reduce the carrying capacity
        density_factor = 1.0 + density * (1.0 + resource_stress)
        density_factor = min(2.0, density_factor)  # Cap at 100% increase
        
        # Age-based mortality
        # Older cats are more affected by poor conditions
        age_factors = []
        for group in ['reproductive', 'sterilized']:
            for _, age in colony[group]:
                age = float(age)
                if age > 84:  # Cats over 7 years
                    base_factor = 1.5
                elif age > 60:  # Cats over 5 years
                    base_factor = 1.3
                elif age > 36:  # Cats over 3 years
                    base_factor = 1.15
                else:
                    base_factor = 1.0
                # Poor conditions affect older cats more
                age_factors.append(base_factor * (1.0 + 0.5 * resource_stress))
        
        avg_age_factor = np.mean(age_factors) if age_factors else 1.0
        
        # Calculate final mortality rates
        # Base rate increased by:
        # 1. Risk multiplier (up to 3x in very poor conditions)
        # 2. Density factor (up to 2x in overcrowded conditions)
        # 3. Age factor (up to 2.25x for old cats in poor conditions)
        # 4. Direct environmental stress (up to 2x in poor conditions)
        
        # Adult mortality
        adult_mortality = (
            base_adult_mortality *
            risk_multiplier *
            density_factor *
            avg_age_factor *
            (1.0 + resource_stress)
        )
        
        # Kitten mortality (more sensitive to conditions)
        kitten_mortality = (
            base_kitten_mortality *
            risk_multiplier *
            density_factor *
            (1.0 + 1.5 * resource_stress)  # 50% more sensitive
        )
        
        # Cap mortality rates at reasonable maximums
        # Max 20% monthly mortality for adults (92% annual)
        # Max 30% monthly mortality for kittens (98% annual)
        adult_mortality = min(0.20, adult_mortality)
        kitten_mortality = min(0.30, kitten_mortality)
        
        # Ensure minimum mortality rates
        # Min 1% monthly for adults (11% annual)
        # Min 1.5% monthly for kittens (17% annual)
        adult_mortality = max(0.01, adult_mortality)
        kitten_mortality = max(0.015, kitten_mortality)
        
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
            sum(int(float(count)) for count, _ in colony['sterilized'])
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
