"""Main simulation module for cat population dynamics."""
import numpy as np
import logging
import traceback
import json
import math
from datetime import datetime
import os
import sys
from pathlib import Path
from typing import Dict

# Add utils directory to path
sys.path.append(str(Path(__file__).parent))

from utils.logging_utils import (
    setupLogging,
    logDebug,
    logSimulationStart,
    logSimulationEnd,
    logSimulationError
)
from utils.simulation_utils import (
    calculateSeasonalFactor,
    calculateResourceAvailability,
    calculateCarryingCapacity,
    validateParams
)

from constants import DEFAULT_PARAMS, MIN_BREEDING_AGE, MAX_BREEDING_AGE, GESTATION_MONTHS, TERRITORY_SIZE_RANGES, DENSITY_THRESHOLD_RANGES

logger = logging.getLogger('debug')

def runSimulationWorker(params: Dict, currentSize: int, months: int, 
                         sterilizedCount: int, monthlySterilization: int, monthlyAbandonment: int) -> Dict:
    """Worker function to run a single simulation."""
    try:
        return simulatePopulation(
            params=params,
            currentSize=currentSize,
            months=months,
            sterilizedCount=sterilizedCount,
            monthlySterilization=monthlySterilization,
            monthlyAbandonment=monthlyAbandonment,
            useMonteCarlo=False
        )
    except Exception as e:
        error_msg = f"Simulation failed with error: {str(e)}"
        logSimulationError("worker", error_msg)
        return None

def simulatePopulation(params, currentSize, months=12, sterilizedCount=0, monthlySterilization=0, monthlyAbandonment=0):
    """
    Simulate cat population dynamics over time.
    
    Args:
        params (dict): Simulation parameters
        currentSize (int): Initial population size
        months (int): Number of months to simulate
        sterilizedCount (int): Initial number of sterilized cats
        monthlySterilization (float): Monthly sterilization rate
        monthlyAbandonment (int): Number of cats abandoned per month
        
    Returns:
        dict: Simulation results including final population and monthly data
    """
    
    try:
        # Log input parameters
        logDebug('DEBUG', f"Input parameters: currentSize={currentSize}, months={months}, sterilizedCount={sterilizedCount}, monthlySterilization={monthlySterilization}, monthlyAbandonment={monthlyAbandonment}")
        logDebug('DEBUG', f"Advanced parameters: {json.dumps(params, indent=2)}")
        
        # Parameter validation
        if not isinstance(params, dict):
            error_msg = f"Invalid params type: {type(params)}. Expected dict."
            logSimulationError("validation", error_msg)
            raise ValueError(error_msg)
            
        # Convert and validate numeric inputs
        try:
            # Log parameter types before conversion
            logDebug('DEBUG', f"Parameter types before conversion: currentSize={type(currentSize)}, months={type(months)}, sterilizedCount={type(sterilizedCount)}, monthlySterilization={type(monthlySterilization)}, monthlyAbandonment={type(monthlyAbandonment)}")
            
            # Convert main parameters
            currentSize = int(float(str(currentSize).strip()))
            months = int(float(str(months).strip()))
            sterilizedCount = int(float(str(sterilizedCount).strip()))
            monthlySterilization = float(str(monthlySterilization).strip())
            monthlyAbandonment = int(float(str(monthlyAbandonment).strip() or '0'))
            
            # Log parameter values after conversion
            logDebug('DEBUG', f"Parameter values after conversion: currentSize={currentSize}, months={months}, sterilizedCount={sterilizedCount}, monthlySterilization={monthlySterilization}, monthlyAbandonment={monthlyAbandonment}")
            
            # Validate parameter ranges
            if currentSize < 1:
                raise ValueError("Current size must be at least 1")
            if months < 1:
                raise ValueError("Months must be at least 1")
            if sterilizedCount < 0:
                raise ValueError("Sterilized count cannot be negative")
            if sterilizedCount > currentSize:
                raise ValueError("Sterilized count cannot exceed current size")
            if monthlySterilization < 0:
                raise ValueError("Monthly sterilization rate cannot be negative")
                
        except (ValueError, TypeError) as e:
            error_msg = f"Parameter validation error: {str(e)}"
            logSimulationError("validation", error_msg)
            raise ValueError(error_msg)

        # Initialize tracking variables
        totalDeaths = 0
        diseaseDeaths = 0
        urbanDeaths = 0
        naturalDeaths = 0
        kittenDeaths = 0
        adultDeaths = 0
        totalBirths = 0
        monthlyData = []  # Track monthly statistics

        # Initial population
        sterilized = sterilizedCount
        unsterilized = currentSize - sterilizedCount

        # Calculate initial resource factor and carrying capacity
        resource_factor = calculateResourceAvailability(
            float(params.get('baseFoodCapacity', '0.8')),
            float(params.get('waterAvailability', '0.8')),
            float(params.get('shelterQuality', '0.7')),
            float(params.get('caretakerSupport', '0.5')),
            float(params.get('feedingConsistency', '0.7'))
        )
        
        carrying_capacity = calculateCarryingCapacity(
            float(params.get('territorySize', '1000')),
            float(params.get('densityThreshold', '1.2')),
            resource_factor
        )
        
        # Record initial state
        monthlyData.append({
            'month': 0,
            'total': sterilized + unsterilized,
            'sterilized': sterilized,
            'unsterilized': unsterilized,
            'births': 0,
            'natural_deaths': 0,
            'disease_deaths': 0,
            'urban_deaths': 0,
            'kitten_deaths': 0,
            'adult_deaths': 0,
            'density_impact': (sterilized + unsterilized) / carrying_capacity if carrying_capacity > 0 else 1.0,
            'resource_factor': resource_factor,
            'carrying_capacity': carrying_capacity
        })

        for month in range(months):
            try:
                # Calculate seasonal factor
                seasonal_factor = calculateSeasonalFactor(
                    month,
                    float(params.get('peakBreedingMonth', '4')),
                    float(params.get('seasonalBreedingAmplitude', '0.8'))
                )

                # Calculate resource factor
                resource_factor = calculateResourceAvailability(
                    float(params.get('baseFoodCapacity', '0.8')),
                    float(params.get('waterAvailability', '0.8')),
                    float(params.get('shelterQuality', '0.7')),
                    float(params.get('caretakerSupport', '0.5')),
                    float(params.get('feedingConsistency', '0.7'))
                )

                # Calculate carrying capacity
                carrying_capacity = calculateCarryingCapacity(
                    float(params.get('territorySize', '1000')),
                    float(params.get('densityThreshold', '1.2')),
                    resource_factor
                )
                
                # Make density impact more gradual for well-supported colonies
                raw_density = (sterilized + unsterilized) / carrying_capacity
                # Start density effects at 100% of capacity and make them stronger
                density_impact = max(0.0, min(1.0, raw_density - 1.0))

                # Log calculations
                logDebug('DEBUG', f"Month {month+1}:")
                logDebug('DEBUG', f"  Seasonal factor: {seasonal_factor}")
                logDebug('DEBUG', f"  Resource factor: {resource_factor}")
                logDebug('DEBUG', f"  Carrying capacity: {carrying_capacity}")
                logDebug('DEBUG', f"  Raw density: {raw_density}")
                logDebug('DEBUG', f"  Density impact: {density_impact}")

                # Calculate base breeding rate with stronger territory effects
                base_breeding_rate = float(params.get('baseBreedingRate', '0.8'))
                litters_per_year = float(params.get('littersPerYear', '2.0'))
                kittens_per_litter = float(params.get('kittensPerLitter', '4.0'))

                # Calculate resource factor with stronger territory size impact
                territory_size = float(params.get('territorySize', '1000'))
                density_threshold = float(params.get('densityThreshold', '0.8'))
                
                # Scale territory capacity based on size more aggressively
                territory_capacity = max(50, int(territory_size * density_threshold * 0.15))  # 1 cat per ~6.67 units
                current_total = sterilized + unsterilized
                current_density = current_total / territory_capacity if territory_capacity > 0 else float('inf')
                
                # Calculate density impact with stronger effect
                density_impact = max(0, min(1, (current_density - 1.0) * 1.5))  # Starts at 100% capacity, stronger slope

                # Calculate resource support with stronger territory dependence
                food_capacity = float(params.get('baseFoodCapacity', '0.7'))
                water_availability = float(params.get('waterAvailability', '0.7'))
                shelter_quality = float(params.get('shelterQuality', '0.7'))
                
                # Scale resource factors based on territory size
                territory_scale = min(1.0, territory_size / 1000.0)  # Normalize to reference size
                resource_factor = (
                    food_capacity * territory_scale +
                    water_availability * territory_scale +
                    shelter_quality * territory_scale
                ) / 3.0

                logDebug('DEBUG', f"  Territory capacity: {territory_capacity}")
                logDebug('DEBUG', f"  Current density: {current_density}")
                logDebug('DEBUG', f"  Density impact: {density_impact}")

                # Calculate mortality based on environmental conditions with stronger random variation
                base_mortality = (1 - float(params.get('adult_survival_rate', '0.92'))) / 12.0
                kitten_mortality = (1 - float(params.get('kitten_survival_rate', '0.85'))) / 12.0
                
                # Add moderate random variation to mortality rates (±30%)
                base_mortality = max(0.005, min(0.15, base_mortality * np.random.uniform(0.7, 1.3)))  # Minimum 0.5% monthly
                kitten_mortality = max(0.008, min(0.2, kitten_mortality * np.random.uniform(0.7, 1.3)))  # Minimum 0.8% monthly
                
                # Calculate environmental impact factors with moderate random variation
                disease_impact = max(0.002, float(params.get('disease_transmission_rate', '0.08')) / 12.0 * np.random.uniform(0.7, 1.3))
                urban_impact = max(0.002, float(params.get('urbanization_impact', '0.15')) / 12.0 * np.random.uniform(0.7, 1.3))
                environmental_impact = max(0.002, float(params.get('environmental_stress', '0.1')) / 12.0 * np.random.uniform(0.7, 1.3))

                # Calculate total mortality rate combining all factors with minimum
                total_mortality_rate = max(0.01, min(0.2, base_mortality + disease_impact + urban_impact))  # At least 1% monthly
                
                # Apply mortality equally to sterilized and unsterilized cats
                # For small populations, use probability-based approach
                def calculate_deaths(population, rate):
                    if population <= 0:
                        return 0
                    # Convert population to integer for range
                    pop = int(population)
                    # For each cat, check if it dies based on mortality rate
                    deaths = sum(1 for _ in range(pop) if np.random.random() < rate)
                    return deaths

                mortality_sterilized = calculate_deaths(sterilized, total_mortality_rate)
                mortality_unsterilized = calculate_deaths(unsterilized, total_mortality_rate)

                # Ensure we don't kill more cats than we have
                mortality_sterilized = min(mortality_sterilized, int(sterilized))
                mortality_unsterilized = min(mortality_unsterilized, int(unsterilized))

                # Additional mortality when over capacity, scaled by resource support
                if density_impact > 0:
                    # Stronger density mortality
                    density_mortality_rate = min(0.2, 0.1 * density_impact * (1 - resource_factor))  # Cap at 20% monthly
                    density_mortality = int((sterilized + unsterilized) * density_mortality_rate * np.random.uniform(0.8, 1.2))
                    mortality_sterilized += int(density_mortality * (sterilized / (sterilized + unsterilized)))
                    mortality_unsterilized += int(density_mortality * (unsterilized / (sterilized + unsterilized)))

                # Track deaths by type (approximate distribution)
                mortality_total = mortality_sterilized + mortality_unsterilized
                
                # Calculate cause of death ratios
                if mortality_total > 0:
                    natural_ratio = base_mortality / total_mortality_rate
                    disease_ratio = disease_impact / total_mortality_rate
                    urban_ratio = urban_impact / total_mortality_rate
                else:
                    natural_ratio = disease_ratio = urban_ratio = 0

                # Distribute deaths by cause
                natural_deaths_sterilized = int(mortality_sterilized * natural_ratio)
                natural_deaths_unsterilized = int(mortality_unsterilized * natural_ratio)
                disease_deaths_sterilized = int(mortality_sterilized * disease_ratio)
                disease_deaths_unsterilized = int(mortality_unsterilized * disease_ratio)
                urban_deaths_sterilized = mortality_sterilized - natural_deaths_sterilized - disease_deaths_sterilized
                urban_deaths_unsterilized = mortality_unsterilized - natural_deaths_unsterilized - disease_deaths_unsterilized

                # Calculate total deaths for this month (mortality already includes disease and urban deaths)
                total_deaths_this_month = mortality_sterilized + mortality_unsterilized

                # Update running totals for death types
                diseaseDeaths += disease_deaths_sterilized + disease_deaths_unsterilized
                urbanDeaths += urban_deaths_sterilized + urban_deaths_unsterilized
                naturalDeaths += natural_deaths_sterilized + natural_deaths_unsterilized
                totalDeaths += total_deaths_this_month  # Add to running total

                # Calculate age-based mortality distribution
                kitten_ratio = 0.3  # 30% of population are kittens
                kitten_population = int((sterilized + unsterilized) * kitten_ratio)
                adult_population = (sterilized + unsterilized) - kitten_population
                
                # Kittens have higher mortality
                kitten_mortality_rate = min(0.95, kitten_mortality * 1.5)  # Cap at 95%
                adult_mortality_rate = total_mortality_rate
                
                # Calculate expected deaths by age
                expected_kitten_deaths = int(kitten_population * kitten_mortality_rate)
                expected_adult_deaths = int(adult_population * adult_mortality_rate)
                
                # Distribute total deaths proportionally between kittens and adults
                total_expected = expected_kitten_deaths + expected_adult_deaths
                if total_expected > 0:
                    kitten_deaths_this_month = int(total_deaths_this_month * (expected_kitten_deaths / total_expected))
                    adult_deaths_this_month = total_deaths_this_month - kitten_deaths_this_month
                else:
                    kitten_deaths_this_month = 0
                    adult_deaths_this_month = total_deaths_this_month
                
                # Update running totals
                kittenDeaths += kitten_deaths_this_month
                adultDeaths += adult_deaths_this_month
                totalDeaths += total_deaths_this_month
                
                # Update population counts
                sterilized = max(0, sterilized - mortality_sterilized)
                unsterilized = max(0, unsterilized - mortality_unsterilized)
                
                # Calculate monthly breeding probability with stronger seasonal effects
                monthly_breeding_prob = (litters_per_year / 12.0) * base_breeding_rate
                
                # Calculate seasonal factor with stronger spring effect
                seasonal_factor = calculateSeasonalFactor(
                    month,
                    float(params.get('peakBreedingMonth', '4')),  # April peak
                    float(params.get('seasonalBreedingAmplitude', '0.9'))  # Increased amplitude
                )
                
                # Apply environmental factors with stronger seasonal influence
                breeding_rate = monthly_breeding_prob * (
                    seasonal_factor * 0.9 + 0.1  # Seasonal factor affects 90% of breeding rate
                ) * (
                    resource_factor * 0.7 + 0.3  # Resource factor affects 70% of breeding rate
                ) * (
                    1 - density_impact * 0.95  # Density impact reduces breeding by up to 95%
                )
                
                # Add moderate random variation (±20%)
                breeding_rate = max(0, min(1, breeding_rate * np.random.uniform(0.8, 1.2)))
                
                # Calculate births
                births_this_month = int(unsterilized * breeding_rate * kittens_per_litter)
                births_this_month = max(0, births_this_month)  # Ensure non-negative
                
                totalBirths += births_this_month
                unsterilized += births_this_month
                
                # Handle monthly sterilizations
                new_sterilizations = min(monthlySterilization, unsterilized)
                sterilized += new_sterilizations
                unsterilized -= new_sterilizations
                
                # Handle monthly abandonments
                unsterilized += monthlyAbandonment
                
                # Store monthly data
                monthlyData.append({
                    'month': month + 1,
                    'total': sterilized + unsterilized,
                    'sterilized': sterilized,
                    'unsterilized': unsterilized,
                    'births': births_this_month,
                    'natural_deaths': mortality_sterilized + mortality_unsterilized,
                    'disease_deaths': disease_deaths_sterilized + disease_deaths_unsterilized,
                    'urban_deaths': urban_deaths_sterilized + urban_deaths_unsterilized,
                    'kitten_deaths': kitten_deaths_this_month,
                    'adult_deaths': adult_deaths_this_month,
                    'density_impact': density_impact,
                    'resource_factor': resource_factor,
                    'carrying_capacity': carrying_capacity
                })

            except Exception as e:
                error_msg = f"Error in month {month}: {str(e)}"
                logSimulationError("monthly_calc", error_msg)
                raise
        
        # Return final results
        return {
            'finalPopulation': sterilized + unsterilized,
            'sterilized': sterilized,
            'unsterilized': unsterilized,
            'totalDeaths': totalDeaths,
            'diseaseDeaths': diseaseDeaths,
            'urbanDeaths': urbanDeaths,
            'naturalDeaths': naturalDeaths,
            'kittenDeaths': kittenDeaths,
            'adultDeaths': adultDeaths,
            'totalBirths': totalBirths,
            'monthlyData': monthlyData  # Changed from monthlyPopulations to monthlyData
        }
        
    except Exception as e:
        error_msg = f"Simulation error: {str(e)}\n{traceback.format_exc()}"
        logSimulationError("unknown", error_msg)
        raise

def calculateCarryingCapacity(territory_size, density_threshold, resource_factor):
    """Calculate carrying capacity based on territory size and resource availability"""
    try:
        # Cubic scaling with territory size for more dramatic effect
        base_capacity = np.power(territory_size / 1000, 3) * density_threshold * 0.1
        # Quadratic resource multiplier for stronger impact
        resource_multiplier = np.power(resource_factor, 2) * 5  # 5x multiplier
        capacity = base_capacity * resource_multiplier
        return max(10, capacity)  # Minimum capacity of 10
    except Exception as e:
        error_msg = f"Error calculating carrying capacity: {str(e)}"
        logSimulationError("capacity_calc", error_msg)
        raise ValueError(error_msg)

def calculateResourceAvailability(food_capacity, water_availability, shelter_quality, caretaker_support, feeding_consistency):
    """Calculate overall resource availability"""
    try:
        # Cubic scaling for all factors
        food_factor = np.power(food_capacity, 3)
        water_factor = np.power(water_availability, 3)
        shelter_factor = np.power(shelter_quality, 3)
        support_factor = np.power(caretaker_support, 3)
        consistency_factor = np.power(feeding_consistency, 3)
        
        # Calculate weighted average with extreme emphasis on food/water
        resource_factor = (
            food_factor * 0.45 +
            water_factor * 0.45 +
            shelter_factor * 0.06 +
            support_factor * 0.02 +
            consistency_factor * 0.02
        )
        
        return max(0.1, min(1.0, resource_factor))
    except Exception as e:
        error_msg = f"Error calculating resource availability: {str(e)}"
        logSimulationError("resource_calc", error_msg)
        raise ValueError(error_msg)

def runParameterTests():
    """Run a series of parameter tests to validate model behavior."""
    baseParams = {
        "breedingRate": 0.98,
        "kittensPerLitter": 5,
        "littersPerYear": 3.5,
        "kittenSurvivalRate": 0.85,
        "femaleRatio": 0.5,
        "adultSurvivalRate": 0.95,
        "seasonalBreedingAmplitude": 0.1,
        "peakBreedingMonth": 4,
        "territorySize": 1000,
        "densityImpactThreshold": 1.5,
        "baseResources": 0.95,
        "resourceVariability": 0.1,
        "urbanEnvironment": 0.7,
        "urbanRisk": 0.03,
        "diseaseRisk": 0.03,
        "naturalRisk": 0.02,
        "carryingCapacity": 1500,
        "baseBreedingSuccess": 0.95,
        "ageBreedingFactor": 0.06,
        "stressImpact": 0.12,
        "earlyBreedingAge": 5,
        "peakBreedingAge": 36,
        "kittenMaturityMonths": 5  # Age at which kittens become adults
    }

    testScenarios = [
        # Baseline test
        {
            "name": "Baseline Hawaii",
            "params": baseParams.copy(),
            "initialColony": 50,
            "months": 24
        },
        
        # Breeding rate tests
        {
            "name": "Low Breeding Rate",
            "params": {**baseParams, "breedingRate": 0.70},
            "initialColony": 50,
            "months": 24,
            "expected": "slower_growth"
        },
        {
            "name": "High Breeding Rate",
            "params": {**baseParams, "breedingRate": 1.0},
            "initialColony": 50,
            "months": 24,
            "expected": "faster_growth"
        },
        
        # Litter size tests
        {
            "name": "Small Litters",
            "params": {**baseParams, "kittensPerLitter": 3},
            "initialColony": 50,
            "months": 24,
            "expected": "smaller_population"
        },
        {
            "name": "Large Litters",
            "params": {**baseParams, "kittensPerLitter": 6},
            "initialColony": 50,
            "months": 24,
            "expected": "larger_population"
        },
        
        # Litters per year tests
        {
            "name": "Few Litters Per Year",
            "params": {**baseParams, "littersPerYear": 2.0},
            "initialColony": 50,
            "months": 24,
            "expected": "slower_growth"
        },
        {
            "name": "Many Litters Per Year",
            "params": {**baseParams, "littersPerYear": 4.0},
            "initialColony": 50,
            "months": 24,
            "expected": "faster_growth"
        },
        
        # Survival rate tests
        {
            "name": "Low Kitten Survival",
            "params": {**baseParams, "kittenSurvivalRate": 0.6},
            "initialColony": 50,
            "months": 24,
            "expected": "high_kitten_mortality"
        },
        {
            "name": "Low Adult Survival",
            "params": {**baseParams, "adultSurvivalRate": 0.7},
            "initialColony": 50,
            "months": 24,
            "expected": "high_adult_mortality"
        },
        
        # Resource tests
        {
            "name": "Resource Scarcity",
            "params": {**baseParams, "baseResources": 0.5, "resourceVariability": 0.3},
            "initialColony": 50,
            "months": 24,
            "expected": "resource_limited_growth"
        },
        {
            "name": "Abundant Resources",
            "params": {**baseParams, "baseResources": 1.0, "resourceVariability": 0.05},
            "initialColony": 50,
            "months": 24,
            "expected": "resource_unlimited_growth"
        },
        
        # Urban environment tests
        {
            "name": "Rural Environment",
            "params": {**baseParams, "urbanEnvironment": 0.2, "urbanRisk": 0.05},
            "initialColony": 50,
            "months": 24,
            "expected": "lower_density_tolerance"
        },
        {
            "name": "Urban Environment",
            "params": {**baseParams, "urbanEnvironment": 0.9, "urbanRisk": 0.02},
            "initialColony": 50,
            "months": 24,
            "expected": "higher_density_tolerance"
        },
        
        # Age-related breeding tests
        {
            "name": "Late Breeding Age",
            "params": {**baseParams, "earlyBreedingAge": 8, "peakBreedingAge": 30},
            "initialColony": 50,
            "months": 24,
            "expected": "delayed_growth"
        },
        {
            "name": "Early Breeding Age",
            "params": {**baseParams, "earlyBreedingAge": 4, "peakBreedingAge": 40},
            "initialColony": 50,
            "months": 24,
            "expected": "accelerated_growth"
        },
        
        # Density impact tests
        {
            "name": "High Density Sensitivity",
            "params": {**baseParams, "densityImpactThreshold": 1.0, "carryingCapacity": 1000},
            "initialColony": 50,
            "months": 24,
            "expected": "strong_density_effects"
        },
        {
            "name": "Low Density Sensitivity",
            "params": {**baseParams, "densityImpactThreshold": 2.0, "carryingCapacity": 2000},
            "initialColony": 50,
            "months": 24,
            "expected": "weak_density_effects"
        },
        
        # Seasonal effects tests
        {
            "name": "Strong Seasonality",
            "params": {**baseParams, "seasonalBreedingAmplitude": 0.3},
            "initialColony": 50,
            "months": 24,
            "expected": "seasonal_variation"
        },
        {
            "name": "No Seasonality",
            "params": {**baseParams, "seasonalBreedingAmplitude": 0.0},
            "initialColony": 50,
            "months": 24,
            "expected": "constant_breeding"
        },
        
        # Disease risk tests
        {
            "name": "High Disease Risk",
            "params": {**baseParams, "diseaseRisk": 0.15, "densityImpactThreshold": 1.2},
            "initialColony": 50,
            "months": 24,
            "expected": "disease_limited"
        },
        {
            "name": "No Disease Risk",
            "params": {**baseParams, "diseaseRisk": 0.0},
            "initialColony": 50,
            "months": 24,
            "expected": "no_disease_deaths"
        }
    ]
    
    results = []
    for scenario in testScenarios:
        try:
            result = simulatePopulation(
                scenario["params"],
                scenario["initialColony"],
                scenario["months"]
            )
            
            if result:
                # Calculate growth metrics
                population_series = result["monthlyData"]
                max_population = max(population_series)
                final_population = population_series[-1]
                
                # Calculate growth rates for different periods
                early_growth = sum([(population_series[i+1] - population_series[i]) / max(1, population_series[i])
                                  for i in range(min(6, len(population_series)-1))]) / 6
                
                late_growth = sum([(population_series[i+1] - population_series[i]) / max(1, population_series[i])
                                 for i in range(max(0, len(population_series)-7), len(population_series)-1)]) / 6
                
                # Calculate mortality metrics
                kitten_mortality_rate = result["kittenDeaths"] / max(1, result["totalDeaths"]) if result["totalDeaths"] > 0 else 0
                disease_mortality_rate = result["diseaseDeaths"] / max(1, result["totalDeaths"]) if result["totalDeaths"] > 0 else 0
                
                results.append({
                    "scenario": scenario["name"],
                    "expectedBehavior": scenario.get("expected", "not_specified"),
                    "initialPopulation": scenario["initialColony"],
                    "finalPopulation": final_population,
                    "maxPopulation": max_population,
                    "earlyGrowthRate": early_growth,
                    "lateGrowthRate": late_growth,
                    "totalDeaths": result["totalDeaths"],
                    "kittenMortalityRate": kitten_mortality_rate,
                    "diseaseMortalityRate": disease_mortality_rate,
                    "monthsSimulated": scenario["months"]
                })
                
                # Log detailed analysis
                logDebug('INFO', f"\nScenario: {scenario['name']}")
                logDebug('INFO', f"Expected behavior: {scenario.get('expected', 'not_specified')}")
                logDebug('INFO', f"Final population: {final_population}")
                logDebug('INFO', f"Early growth rate: {early_growth:.3f}")
                logDebug('INFO', f"Late growth rate: {late_growth:.3f}")
                logDebug('INFO', f"Kitten mortality rate: {kitten_mortality_rate:.3f}")
                logDebug('INFO', f"Disease mortality rate: {disease_mortality_rate:.3f}")
            
        except Exception as e:
            logDebug('ERROR', f"Error in scenario {scenario['name']}: {str(e)}")
            logDebug('ERROR', traceback.format_exc())
            continue
    
    return results
