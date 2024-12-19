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
    """Calculate the impact of population density with realistic biological constraints."""
    try:
        current_population = float(current_population)
        carrying_capacity = calculate_carrying_capacity(params)
        
        # Calculate relative density
        density_ratio = current_population / carrying_capacity
        density_threshold = float(params.get('density_impact_threshold', 1.0))
        
        # Adjust density ratio by threshold - now with stronger threshold effect
        adjusted_ratio = density_ratio / density_threshold
        
        # Use a sigmoid curve for smooth transitions with more pronounced effects
        if adjusted_ratio <= 1.0:
            # Below threshold - much stronger boost at low density
            k = 1.5  # Gentler slope for more gradual effect
            midpoint = 0.5
            impact = 0.1 / (1.0 + np.exp(-k * (adjusted_ratio - midpoint)))
        else:
            # Above threshold - more gradual decline
            k = 2.0  # Gentler slope above threshold
            midpoint = 1.5
            impact = 0.4 / (1.0 + np.exp(-k * (adjusted_ratio - midpoint)))
        
        # Calculate final density effect (higher is better)
        density_effect = 1.0 - impact
        
        # Ensure reasonable bounds based on adjusted ratio with more lenient thresholds
        if adjusted_ratio > 2.0:
            density_effect = max(0.5, density_effect)  # Less severe overcrowding
        elif adjusted_ratio > 1.5:
            density_effect = max(0.7, density_effect)  # More gradual overcrowding
        elif adjusted_ratio > 1.0:
            density_effect = max(0.8, density_effect)  # Mild overcrowding
        else:
            density_effect = max(0.9, density_effect)  # Under capacity
        
        return float(density_effect)
    except Exception as e:
        logger.error(f"Error in calculate_density_impact: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_resource_availability(current_population, params):
    """Calculate resource availability based on carrying capacity and current population."""
    try:
        current_population = float(current_population)
        carrying_capacity = calculate_carrying_capacity(params)
        
        # Base resource factors with stronger scaling
        base_food = float(params.get('base_food_capacity', 0.95))
        food_scaling = float(params.get('food_scaling_factor', 0.9))
        water_availability = float(params.get('water_availability', 0.95))
        
        # Calculate population pressure with more gradual decline
        population_ratio = current_population / carrying_capacity
        
        # Different scaling for under vs over capacity
        if population_ratio <= 1.0:
            # Under capacity - very gradual resource reduction
            resource_pressure = np.power(population_ratio, 1.2)  # More gradual decline
        else:
            # Over capacity - more gradual reduction
            resource_pressure = 1.0 + np.power(population_ratio - 1.0, 1.5)  # More gradual decline
        
        # Calculate food availability with stronger base food effect
        food_availability = np.power(base_food, 1.5) * np.power(food_scaling, resource_pressure)
        
        # Water availability affects overall survival more gradually
        water_factor = water_availability * np.exp(-0.2 * resource_pressure)  # More gradual effect
        
        # Combined availability with more lenient thresholds
        availability = min(food_availability, water_factor)
        
        # Set minimum based on population ratio with more gradual penalties
        if population_ratio > 2.0:
            min_availability = 0.3  # Less severe overcrowding
        elif population_ratio > 1.5:
            min_availability = 0.4  # More gradual overcrowding
        elif population_ratio > 1.0:
            min_availability = 0.5  # Mild overcrowding
        else:
            min_availability = 0.6  # Under capacity
        
        return float(max(min_availability, min(1.0, availability)))
    except Exception as e:
        logger.error(f"Error in calculate_resource_availability: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_monthly_mortality(params, colony, environment_factor, month=None):
    """Calculate monthly mortality with biologically accurate, age-specific rates."""
    try:
        # Calculate total cats first
        total_cats = (
            sum(int(float(count)) for count, _ in colony['young_kittens']) +
            sum(int(float(count)) for count, _ in colony['reproductive']) +
            sum(int(float(count)) for count, _ in colony['sterilized'])
        )
        
        if total_cats == 0:
            return {
                'kittens': 0, 
                'adults': 0,
                'causes': {'natural': 0, 'urban': 0, 'disease': 0}
            }

        # Base mortality rates (monthly) - reduced rates for better survival
        base_kitten_mortality = min(0.95, max(0.01, float(params.get('kitten_mortality_rate', 0.04)) * 0.8))  # Reduced amplification
        base_adult_mortality = min(0.95, max(0.005, float(params.get('adult_mortality_rate', 0.015)) * 0.7))   # Reduced amplification
        base_senior_mortality = min(0.95, max(0.01, float(params.get('senior_mortality_rate', 0.025)) * 0.7))  # Reduced amplification
        
        # Environmental stress increases mortality (gentler impact)
        stress_factor = min(1.5, max(1.0, 1.0 + (0.5 * (1.0 - environment_factor))))  # Reduced multiplier
        
        # Seasonal effects on mortality (gentler)
        if month is not None:
            winter_months = [11, 0, 1]  # Nov, Dec, Jan
            if month in winter_months:
                seasonal_factor = 1.1  # 10% increase in winter
            else:
                seasonal_factor = 1.0
        else:
            seasonal_factor = 1.0
            
        # Calculate carrying capacity and density effects (gentler impact)
        carrying_capacity = max(1, calculate_carrying_capacity(params))
        density_impact_threshold = float(params.get('density_impact_threshold', 1.0))
        if total_cats > carrying_capacity * density_impact_threshold:
            excess_ratio = (total_cats - carrying_capacity * density_impact_threshold) / carrying_capacity
            density_factor = min(1.3, max(1.0, 1.0 + (0.2 * excess_ratio)))  # Gentler density impact
        else:
            density_factor = 1.0
        
        # Get risk factors (gentler impact)
        urban_risk = min(0.95, max(0.005, float(params.get('urban_risk', 0.01)) * 0.8))  # Reduced amplification
        disease_rate = min(0.95, max(0.005, float(params.get('disease_rate', 0.05)) * 0.8))  # Reduced amplification
        natural_risk = min(0.95, max(0.005, float(params.get('natural_risk', 0.01)) * 0.7))  # Reduced amplification
        
        deaths = {
            'kittens': 0, 
            'adults': 0,
            'causes': {'natural': 0, 'urban': 0, 'disease': 0}
        }
        
        def bound_probability(p):
            """Ensure probability is between 0 and 1"""
            return min(0.95, max(0.01, float(p)))
        
        # Process young kittens with more pronounced effects
        for count, age in colony['young_kittens']:
            count = int(float(count))
            if count <= 0:
                continue
                
            # Base mortality from natural causes (amplified impacts)
            natural_mortality = bound_probability(
                base_kitten_mortality * 
                stress_factor *  # Full stress impact
                seasonal_factor *  # Full seasonal impact
                density_factor  # Full density impact
            )
            natural_deaths = np.random.binomial(count, natural_mortality)
            deaths['causes']['natural'] += natural_deaths
            
            # Urban-related deaths (more sensitive)
            remaining = count - natural_deaths
            urban_deaths = 0  # Initialize urban_deaths
            if remaining > 0:
                urban_mortality = bound_probability(urban_risk * 1.2)  # Higher urban risk for kittens
                urban_deaths = np.random.binomial(remaining, urban_mortality)
                deaths['causes']['urban'] += urban_deaths
                remaining -= urban_deaths
            
            # Disease deaths (more sensitive)
            disease_deaths = 0  # Initialize disease_deaths
            if remaining > 0:
                disease_mortality = bound_probability(disease_rate * 1.3)  # Higher disease risk for kittens
                disease_deaths = np.random.binomial(remaining, disease_mortality)
                deaths['causes']['disease'] += disease_deaths
            
            deaths['kittens'] += natural_deaths + urban_deaths + disease_deaths
        
        # Process adults with more pronounced effects
        for group in ['reproductive', 'sterilized']:
            for count, age in colony[group]:
                count = int(float(count))
                if count <= 0:
                    continue
                
                # Determine base rate by age
                age = float(age)
                if age >= 7.0:  # Senior cats
                    base_rate = base_senior_mortality
                else:
                    base_rate = base_adult_mortality
                
                # Natural deaths with amplified impacts
                natural_mortality = bound_probability(
                    base_rate * 
                    stress_factor *  # Full stress impact
                    seasonal_factor *  # Full seasonal impact
                    density_factor  # Full density impact
                )
                natural_deaths = np.random.binomial(count, natural_mortality)
                deaths['causes']['natural'] += natural_deaths
                
                # Urban-related deaths
                remaining = count - natural_deaths
                urban_deaths = 0  # Initialize urban_deaths
                if remaining > 0:
                    urban_mortality = bound_probability(urban_risk)
                    urban_deaths = np.random.binomial(remaining, urban_mortality)
                    deaths['causes']['urban'] += urban_deaths
                    remaining -= urban_deaths
                
                # Disease deaths
                disease_deaths = 0  # Initialize disease_deaths
                if remaining > 0:
                    disease_mortality = bound_probability(disease_rate)
                    disease_deaths = np.random.binomial(remaining, disease_mortality)
                    deaths['causes']['disease'] += disease_deaths
                
                deaths['adults'] += natural_deaths + urban_deaths + disease_deaths
        
        return deaths
    except Exception as e:
        logger.error(f"Error in calculate_monthly_mortality: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_resource_impact(resource_availability):
    """Calculate the impact of resource availability on population growth."""
    try:
        # More nuanced non-linear response to resource availability
        # Use a sigmoid-like curve for smoother transitions
        k = 2.0  # Controls the steepness of the transition
        midpoint = 0.5  # Point of inflection
        
        # Transform resource_availability using sigmoid function
        impact = 1.0 / (1.0 + np.exp(-k * (resource_availability - midpoint)))
        
        # Scale the impact to be between 0.2 and 1.0
        # This ensures even severe resource constraints don't completely halt population growth
        scaled_impact = 0.2 + (0.8 * impact)
        
        return float(scaled_impact)
    except Exception as e:
        logger.error(f"Error in calculate_resource_impact: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_breeding_success(params, colony, environment_factor, current_month=None):
    """Calculate breeding success with realistic biological constraints."""
    try:
        # Base breeding rate with stronger scaling
        annual_breeding_rate = min(0.95, max(0.3, float(params.get('breeding_rate', 0.85))))  # Increased min rate
        litters_per_year = min(4.0, max(2.0, float(params.get('litters_per_year', 2.5))))  # Increased min litters
        environmental_stress = min(0.6, max(0.01, float(params.get('environmental_stress', 0.1))))  # Reduced max stress
        
        # Convert annual breeding rate to monthly with stronger scaling
        base_monthly_rate = annual_breeding_rate / 12.0  # Monthly conversion
        base_monthly_rate = min(0.95, base_monthly_rate * 5.0)  # Increased multiplier for more growth
        
        # Apply environmental stress to breeding rate (gentler impact)
        stress_factor = max(0.7, 1.0 - environmental_stress)  # Less impact on breeding
        base_monthly_rate *= stress_factor
        
        # Adjust for multiple litters with stronger effect
        litter_factor = min(3.0, 1.0 + (litters_per_year - 1.0) * 0.5)  # Stronger litter bonus
        base_monthly_rate *= litter_factor
        
        # Seasonal adjustment with moderate variation
        seasonal_bonus = 1.0
        if current_month is not None:
            amplitude = min(0.8, max(0.3, float(params.get('seasonal_breeding_amplitude', 0.25))))  # Increased seasonal effect
            peak_month = int(params.get('peak_breeding_month', 3))
            months_from_peak = abs((current_month - peak_month + 6) % 12 - 6)
            seasonal_bonus = 1.0 + amplitude * (1.0 - months_from_peak / 6.0)  # Stronger seasonal effect
        
        # Food capacity with balanced impact
        food_capacity = min(0.95, max(0.5, float(params.get('base_food_capacity', 0.95))))  # Increased min capacity
        environment_bonus = min(2.0, food_capacity * 2.0)  # Stronger food bonus
        
        # Calculate breeding rate with all factors
        breeding_rate = base_monthly_rate * seasonal_bonus * environment_bonus
        
        # Territory size effects with moderate impact
        territory_size = max(100, float(params.get('territory_size', 1000)))
        total_cats = (
            sum(int(float(count)) for count, _ in colony['young_kittens']) +
            sum(int(float(count)) for count, _ in colony['reproductive']) +
            sum(int(float(count)) for count, _ in colony['sterilized'])
        )
        
        # Calculate density with moderate territory effect
        cats_per_hectare = total_cats / (territory_size * 0.0001)
        density_threshold = max(0.1, float(params.get('density_impact_threshold', 0.5)))
        
        # Density impact with balanced scaling
        density_ratio = cats_per_hectare / density_threshold
        if density_ratio > 1.0:
            # More balanced decline based on threshold
            breeding_rate *= max(0.6, 1.0 - 0.1 * (density_ratio - 1.0))  # Gentler density penalty
        else:
            # Moderate boost at low density
            boost_factor = min(2.0, 1.0 + 0.4 * (1.0 - density_ratio))  # Stronger low-density bonus
            breeding_rate *= boost_factor
        
        # Environmental stress reduces maximum breeding rate moderately
        max_breeding_rate = min(0.95, 1.0 - environmental_stress * 0.2)  # Reduced stress impact
        
        # Ensure reasonable bounds with stress-adjusted maximum
        breeding_rate = min(max_breeding_rate, max(0.1, breeding_rate))  # Increased min rate
        
        return float(breeding_rate)
    except Exception as e:
        logger.error(f"Error in calculate_breeding_success: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_resource_limit(params, current_population):
    """Calculate resource-based population limits and stress factors."""
    try:
        # Extract and validate parameters
        territory_size = float(params.get('territory_size', 1000))
        base_food = float(params.get('base_food_capacity', 0.95))  # Updated default
        food_scaling = float(params.get('food_scaling_factor', 0.9))  # Updated default
        
        # Calculate base carrying capacity based on territory size
        # Even more forgiving territory scaling
        base_cats_per_unit = 5.0  # Further increased base density
        size_factor = np.power(territory_size / 1000, 0.5)  # Even more gradual scaling
        carrying_capacity = territory_size * base_cats_per_unit * size_factor
        
        # Calculate current population density relative to territory
        density = current_population / territory_size
        
        # Calculate food availability with very gradual territory dependence
        territory_factor = min(2.0, territory_size / 1000)  # Scale up to 2x for larger territory
        base_food = float(params.get('base_food_capacity', 0.95)) * territory_factor
        food_scaling = float(params.get('food_scaling_factor', 0.9)) * territory_factor
        food_availability = base_food * np.power(food_scaling, density / (4 * base_cats_per_unit))  # Increased denominator
        
        # Calculate stress factor based on population density
        # Much more forgiving effect in smaller territories
        density_ratio = current_population / carrying_capacity
        stress_factor = 1.0 + np.power(max(0, density_ratio - 1.5), 1.1) * (1.1 - size_factor)  # More forgiving
        
        return float(stress_factor), float(carrying_capacity)
    except Exception as e:
        logger.error(f"Error in calculate_resource_limit: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculate_immigration(params, current_population):
    """Calculate monthly immigration rate with balanced effects."""
    try:
        territory_size = float(params.get('territory_size', 1000))
        hectares = territory_size / 10000
        optimal_density = 3.0
        carrying_capacity = optimal_density * hectares
        
        # Moderate base immigration rate
        base_rate = 0.06  # Reduced from 0.08
        urban_factor = float(params.get('urban_environment', 0.7))
        
        # More balanced urban and caretaker effects
        caretaker_support = float(params.get('caretaker_support', 1.0))
        immigration_modifier = 1.0 + (0.2 * urban_factor) + (0.15 * (caretaker_support - 1.0))  # Reduced impacts
        
        # More gradual density-dependent decline
        density_factor = max(0, 1.0 - np.power(current_population / carrying_capacity, 1.2))  # Reduced from 1.5
        
        # Calculate monthly immigrants
        monthly_immigrants = int(carrying_capacity * base_rate * immigration_modifier * density_factor)
        
        # Moderate random variation
        variation = np.random.normal(0, 0.15)  # Reduced from 0.2
        monthly_immigrants = int(monthly_immigrants * (1 + variation))
        
        return max(0, monthly_immigrants)
    except Exception as e:
        logger.error(f"Error in calculate_immigration: {str(e)}")
        logger.error(traceback.format_exc())
        return 0

def calculate_carrying_capacity(params):
    """Calculate the total sustainable population based on environmental parameters."""
    try:
        # Base territory calculations
        territory_size = float(params.get('territory_size', 1000))  # in square meters
        base_cats_per_hectare = 25.0  # Base density for feral cats in urban/suburban areas
        
        # Calculate base capacity from territory
        hectares = territory_size / 10000  # Convert to hectares
        base_capacity = hectares * base_cats_per_hectare
        
        # Resource quality factors with stronger impact
        food_capacity = float(params.get('base_food_capacity', 0.9))
        food_scaling = float(params.get('food_scaling_factor', 0.8))
        water_availability = float(params.get('water_availability', 0.8))
        shelter_quality = float(params.get('shelter_quality', 0.7))
        
        # Resource quality multiplier (more sensitive)
        resource_multiplier = np.power(
            (food_capacity * food_scaling * water_availability * shelter_quality),
            1.2  # Gentler effect of resources
        )
        
        # Human support factors
        caretaker_support = float(params.get('caretaker_support', 0.6))
        feeding_consistency = float(params.get('feeding_consistency', 0.7))
        
        # Human support multiplier (more impact)
        human_multiplier = 0.6 + (0.4 * np.sqrt(caretaker_support * feeding_consistency))
        
        # Risk factors with reduced weight
        urban_risk = float(params.get('urban_risk', 0.15))
        disease_risk = float(params.get('disease_risk', 0.1))
        natural_risk = float(params.get('natural_risk', 0.1))
        
        # Risk impact (gentler effect)
        risk_multiplier = 1.0 - (0.7 * (urban_risk + disease_risk + natural_risk))
        risk_multiplier = max(0.3, risk_multiplier)  # Ensure minimum multiplier
        
        # Calculate final capacity with all factors
        carrying_capacity = base_capacity * resource_multiplier * human_multiplier * risk_multiplier
        
        # Ensure minimum viable population
        min_viable = max(5.0, hectares * 2.0)  # Scale minimum with territory size
        carrying_capacity = max(min_viable, carrying_capacity)
        
        return float(carrying_capacity)
        
    except Exception as e:
        logger.error(f"Error in calculate_carrying_capacity: {str(e)}")
        logger.error(traceback.format_exc())
        return 50.0  # Reasonable fallback capacity

def calculate_resource_limit(params, current_population):
    """Calculate resource-based population limits and stress factors."""
    try:
        # Extract and validate parameters
        territory_size = float(params.get('territory_size', 1000))
        base_food = float(params.get('base_food_capacity', 0.95))  # Updated default
        food_scaling = float(params.get('food_scaling_factor', 0.9))  # Updated default
        
        # Calculate base carrying capacity based on territory size
        # Even more forgiving territory scaling
        base_cats_per_unit = 5.0  # Further increased base density
        size_factor = np.power(territory_size / 1000, 0.5)  # Even more gradual scaling
        carrying_capacity = territory_size * base_cats_per_unit * size_factor
        
        # Calculate current population density relative to territory
        density = current_population / territory_size
        
        # Calculate food availability with very gradual territory dependence
        territory_factor = min(2.0, territory_size / 1000)  # Scale up to 2x for larger territory
        base_food = float(params.get('base_food_capacity', 0.95)) * territory_factor
        food_scaling = float(params.get('food_scaling_factor', 0.9)) * territory_factor
        food_availability = base_food * np.power(food_scaling, density / (4 * base_cats_per_unit))  # Increased denominator
        
        # Calculate stress factor based on population density
        # Much more forgiving effect in smaller territories
        density_ratio = current_population / carrying_capacity
        stress_factor = 1.0 + np.power(max(0, density_ratio - 1.5), 1.1) * (1.1 - size_factor)  # More forgiving
        
        return float(stress_factor), float(carrying_capacity)
    except Exception as e:
        logger.error(f"Error in calculate_resource_limit: {str(e)}")
        logger.error(traceback.format_exc())
        raise
