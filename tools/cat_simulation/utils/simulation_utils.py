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
        
        # Calculate relative density with more gradual impact
        density_ratio = current_population / carrying_capacity
        
        # Sigmoid curve for density effects
        # Use different curves for under-capacity vs over-capacity
        if density_ratio <= 1.0:
            # Below capacity - very gradual impact
            k = 1.5
            midpoint = 0.8
            impact = 0.2 / (1.0 + np.exp(-k * (density_ratio - midpoint)))
        else:
            # Above capacity - steeper impact but still manageable
            k = 2.0
            midpoint = 1.2
            impact = 0.8 / (1.0 + np.exp(-k * (density_ratio - midpoint)))
        
        # Calculate final density effect (higher is better)
        density_effect = 1.0 - impact
        
        # Ensure reasonable bounds based on density ratio
        if density_ratio > 2.0:
            density_effect = max(0.4, density_effect)  # Severe overcrowding
        elif density_ratio > 1.5:
            density_effect = max(0.5, density_effect)  # Significant overcrowding
        elif density_ratio > 1.0:
            density_effect = max(0.6, density_effect)  # Mild overcrowding
        else:
            density_effect = max(0.7, density_effect)  # Under capacity
        
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
        
        # Base resource factors with stronger impact
        base_food = float(params.get('base_food_capacity', 0.95))
        food_scaling = float(params.get('food_scaling_factor', 0.9))
        water_availability = float(params.get('water_availability', 0.95))
        
        # Calculate population pressure with sharper decline
        population_ratio = current_population / carrying_capacity
        
        # Different scaling for under vs over capacity
        if population_ratio <= 1.0:
            # Under capacity - gradual resource reduction
            resource_pressure = np.power(population_ratio, 1.5)  # Steeper decline
        else:
            # Over capacity - much steeper reduction
            resource_pressure = 1.0 + np.power(population_ratio - 1.0, 2.0)  # Quadratic decline
        
        # Calculate food availability with stronger pressure effect
        food_availability = base_food * np.power(food_scaling, resource_pressure)
        
        # Water availability affects overall survival more directly
        water_factor = water_availability * np.exp(-0.3 * resource_pressure)  # Stronger effect
        
        # Combined availability with stricter thresholds
        availability = min(food_availability, water_factor)
        
        # Set minimum based on population ratio with harsher penalties
        if population_ratio > 2.0:
            min_availability = 0.2  # Severe overcrowding
        elif population_ratio > 1.5:
            min_availability = 0.3  # Significant overcrowding
        elif population_ratio > 1.0:
            min_availability = 0.4  # Mild overcrowding
        else:
            min_availability = 0.5  # Under capacity
        
        return float(max(min_availability, min(1.0, availability)))
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

def calculate_monthly_mortality(params, colony, environment_factor, month=None):
    """Calculate monthly mortality with biologically accurate, age-specific rates."""
    try:
        # Convert annual rates to monthly rates using proper probability
        # Monthly = 1 - (1 - Annual)^(1/12)
        base_adult_annual = 1 - float(params.get('adult_survival_rate', 0.92))
        base_adult_mortality = 1 - (1 - base_adult_annual) ** (1/12)  # Monthly rate
        
        # Kitten mortality varies significantly by age
        # Age-specific annual mortality rates:
        # 0-2 months: 70% annual (higher in first weeks)
        # 2-4 months: 40% annual
        # 4-6 months: 30% annual
        kitten_mortality_by_age = {
            0: 0.25,  # 25% monthly for first month
            1: 0.20,  # 20% monthly for second month
            2: 0.10,  # 10% monthly for months 3-4
            3: 0.10,
            4: 0.07,  # 7% monthly for months 5-6
            5: 0.07
        }
        
        # Environmental impact on mortality
        # More forgiving formula: poor conditions increase mortality less severely
        env_mortality_factor = 1.0 + max(0, (1.0 - environment_factor) * 0.5)
        
        # Seasonal effect on mortality (milder in Hawaii)
        seasonal_mortality = 1.0
        if month is not None:
            # Slight increase in mortality during extreme weather months
            high_mortality_months = [0, 1, 6, 7]  # Jan, Feb, Jul, Aug
            if month in high_mortality_months:
                seasonal_mortality = 1.1  # Only 10% increase in harsh months
        
        # Risk factors from parameters
        urban_risk = float(params.get('urban_risk', 0.15))
        disease_risk = float(params.get('disease_risk', 0.1))
        natural_risk = float(params.get('natural_risk', 0.1))
        
        # Initialize death counts
        deaths = {
            'kittens': 0,
            'adults': 0,
            'total': 0,  # Will be calculated at the end
            'kitten_mortality': 0,  # Will be updated for logging
            'adult_mortality': base_adult_mortality * env_mortality_factor * seasonal_mortality,
            'causes': {
                'natural': 0,
                'urban': 0,
                'disease': 0
            }
        }
        
        # Process kitten deaths with age-specific rates
        for count, age in colony['young_kittens']:
            count = int(float(count))
            if count > 0:
                age = min(int(float(age)), 5)  # Cap at 5 months
                base_rate = kitten_mortality_by_age[age]
                
                # Apply environmental and seasonal factors more gently to older kittens
                age_factor = 1.0 - (age * 0.1)  # Older kittens are less affected
                adjusted_env_factor = 1.0 + (env_mortality_factor - 1.0) * age_factor
                
                mortality_rate = base_rate * adjusted_env_factor * seasonal_mortality
                mortality_rate = min(0.35, mortality_rate)  # Cap monthly mortality at 35%
                
                kitten_deaths = np.random.binomial(count, mortality_rate)
                deaths['kittens'] += kitten_deaths
                
                # Distribute kitten deaths across causes
                if kitten_deaths > 0:
                    # Higher natural mortality for kittens
                    natural_deaths = int(round(kitten_deaths * 0.6))  # 60% natural causes
                    remaining_deaths = kitten_deaths - natural_deaths
                    
                    # Split remaining between urban and disease based on risk ratios
                    total_risk = urban_risk + disease_risk
                    urban_deaths = int(round(remaining_deaths * (urban_risk / total_risk)))
                    disease_deaths = remaining_deaths - urban_deaths  # Ensure we account for all deaths
                    
                    deaths['causes']['natural'] += natural_deaths
                    deaths['causes']['urban'] += urban_deaths
                    deaths['causes']['disease'] += disease_deaths
                
                # Update average kitten mortality for logging
                deaths['kitten_mortality'] = mortality_rate
        
        # Process adult deaths
        adult_cats = sum(int(float(count)) for count, _ in colony['reproductive'])
        adult_cats += sum(int(float(count)) for count, _ in colony['sterilized'])
        
        if adult_cats > 0:
            adult_mortality = deaths['adult_mortality']
            adult_deaths = np.random.binomial(adult_cats, adult_mortality)
            deaths['adults'] += adult_deaths
            
            # Distribute adult deaths across causes
            if adult_deaths > 0:
                # Calculate risk proportions
                total_risk = urban_risk + disease_risk + natural_risk
                
                # Use integer rounding to ensure we account for all deaths
                natural_deaths = int(round(adult_deaths * (natural_risk / total_risk)))
                remaining_deaths = adult_deaths - natural_deaths
                
                # Split remaining deaths between urban and disease
                adjusted_urban_prop = urban_risk / (urban_risk + disease_risk)
                urban_deaths = int(round(remaining_deaths * adjusted_urban_prop))
                disease_deaths = remaining_deaths - urban_deaths  # Ensure we account for all deaths
                
                deaths['causes']['natural'] += natural_deaths
                deaths['causes']['urban'] += urban_deaths
                deaths['causes']['disease'] += disease_deaths
        
        # Calculate total deaths at the end
        deaths['total'] = deaths['kittens'] + deaths['adults']
        
        return deaths
    except Exception as e:
        logger.error(f"Error in calculate_monthly_mortality: {str(e)}")
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

def calculate_breeding_success(params, colony, environment_factor, current_month=None):
    """Calculate breeding success with realistic biological constraints."""
    try:
        # Base breeding rate (monthly chance of a female becoming pregnant)
        annual_breeding_rate = float(params.get('breeding_rate', 0.85))
        litters_per_year = float(params.get('litters_per_year', 2.5))
        
        # Convert annual breeding rate to monthly with stronger seasonality
        base_monthly_rate = (annual_breeding_rate * litters_per_year) / 12
        
        # Seasonal adjustment (much stronger effect)
        seasonal_bonus = 1.0
        if current_month is not None:
            amplitude = float(params.get('seasonal_breeding_amplitude', 0.2))
            peak_month = int(params.get('peak_breeding_month', 3))
            
            # Calculate months from peak
            months_from_peak = abs((current_month - peak_month + 6) % 12 - 6)
            
            # Stronger seasonal variation
            seasonal_bonus = 1.0 + amplitude * (1.0 - months_from_peak / 6.0)
        
        # Environmental impact on breeding (more sensitive)
        # Below 0.5 environment factor severely impacts breeding
        if environment_factor < 0.5:
            environment_bonus = 0.3 + (0.4 * environment_factor)  # Severe reduction
        else:
            environment_bonus = 0.5 + (0.5 * environment_factor)  # More gradual above 0.5
        
        # Calculate breeding rate with all factors
        breeding_rate = base_monthly_rate * seasonal_bonus * environment_bonus
        
        # Population density effects
        total_cats = (
            sum(int(float(count)) for count, _ in colony['young_kittens']) +
            sum(int(float(count)) for count, _ in colony['reproductive']) +
            sum(int(float(count)) for count, _ in colony['sterilized'])
        )
        
        # Density calculations based on territory
        territory_size = float(params.get('territory_size', 1000))
        cats_per_hectare = total_cats / (territory_size / 10000)
        density_threshold = float(params.get('density_impact_threshold', 0.5))
        
        # Density impact with sharper thresholds
        if cats_per_hectare > (density_threshold * 2):
            breeding_rate *= 0.5  # Severe reduction at high density
        elif cats_per_hectare > density_threshold:
            breeding_rate *= 0.7  # Moderate reduction
        elif cats_per_hectare < (density_threshold * 0.5):
            breeding_rate *= 1.2  # Bonus for very low density
        
        # Additional factors
        food_capacity = float(params.get('base_food_capacity', 0.9))
        if food_capacity < 0.6:  # Strong impact of poor food availability
            breeding_rate *= 0.6
        elif food_capacity < 0.8:
            breeding_rate *= 0.8
        
        # Ensure reasonable bounds with wider range
        breeding_rate = min(0.4, max(0.02, breeding_rate))  # Between 2% and 40% monthly
        
        return float(breeding_rate)
        
    except Exception as e:
        logger.error(f"Error in calculate_breeding_success: {str(e)}")
        logger.error(traceback.format_exc())
        return 0.15  # Reasonable fallback rate

def calculate_carrying_capacity(params):
    """Calculate the total sustainable population based on environmental parameters."""
    try:
        # Base territory calculations
        territory_size = float(params.get('territory_size', 1000))  # in square meters
        base_cats_per_hectare = float(params.get('cats_per_acre', 2.5)) * 2.47  # Convert to hectares
        
        # Resource quality factors with stronger impact
        food_capacity = float(params.get('base_food_capacity', 0.9))
        food_scaling = float(params.get('food_scaling_factor', 0.8))
        water_availability = float(params.get('water_availability', 0.8))
        shelter_quality = float(params.get('shelter_quality', 0.7))
        
        # Calculate base capacity from territory
        hectares = territory_size / 10000  # Convert to hectares
        base_capacity = hectares * base_cats_per_hectare
        
        # Resource quality multiplier (more sensitive to poor conditions)
        resource_multiplier = np.power(
            (food_capacity * food_scaling * water_availability * shelter_quality),
            1.5  # Stronger effect of poor resources
        )
        
        # Human support factors
        caretaker_support = float(params.get('caretaker_support', 0.6))
        feeding_consistency = float(params.get('feeding_consistency', 0.7))
        
        # Human support multiplier (more impact)
        human_multiplier = 0.5 + (0.5 * np.sqrt(caretaker_support * feeding_consistency))
        
        # Risk factors with greater weight
        urban_risk = float(params.get('urban_risk', 0.15))
        disease_risk = float(params.get('disease_risk', 0.1))
        natural_risk = float(params.get('natural_risk', 0.1))
        
        # Risk impact (more severe)
        risk_multiplier = 1.0 - (urban_risk + disease_risk + natural_risk)
        risk_multiplier = np.power(max(0.1, risk_multiplier), 1.5)  # Stronger effect of risks
        
        # Calculate final capacity with all factors
        carrying_capacity = base_capacity * resource_multiplier * human_multiplier * risk_multiplier
        
        # Ensure minimum viable population
        min_viable = 5.0  # Minimum viable population
        carrying_capacity = max(min_viable, carrying_capacity)
        
        return float(carrying_capacity)
        
    except Exception as e:
        logger.error(f"Error in calculate_carrying_capacity: {str(e)}")
        logger.error(traceback.format_exc())
        return 50.0  # Reasonable fallback capacity
