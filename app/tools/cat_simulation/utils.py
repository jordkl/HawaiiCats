"""Utility functions for cat population simulation."""

import logging
import math
import numpy as np

from .simulation_utils import (
    calculateCarryingCapacity,
    calculateResourceAvailability as simResourceAvailability
)

logger = logging.getLogger(__name__)

def calculateSeasonalFactor(month, amplitude=0.2, peakMonth=3):
    """Calculate seasonal breeding factor based on month."""
    try:
        # Normalize month to [0, 11]
        month = month % 12
        # Calculate seasonal factor using sine wave
        return 1.0 + amplitude * math.sin(2 * math.pi * (month - peakMonth) / 12)
    except Exception as e:
        logger.error(f"Error in calculateSeasonalFactor: {str(e)}")
        return 1.0

def calculateDensityImpact(currentPopulation, capacity=1000):
    """Calculate impact of population density on breeding."""
    try:
        if capacity <= 0:
            return 0.0
        density = currentPopulation / capacity
        # Use logistic function to model density impact
        return 1.0 / (1.0 + math.exp(2 * (density - 1)))
    except Exception as e:
        logger.error(f"Error in calculateDensityImpact: {str(e)}")
        return 0.5

def calculateResourceAvailability(currentPopulation, params):
    """Calculate resource availability factor."""
    try:
        # Extract parameters with defaults
        baseResources = params.get('baseResources', 1.0)
        resourceVariability = params.get('resourceVariability', 0.1)
        urbanEnvironment = params.get('urbanEnvironment', 0.5)
        
        # Calculate base availability
        availability = baseResources
        
        # Add random variation
        variation = np.random.normal(0, resourceVariability)
        availability *= (1 + variation)
        
        # Urban environment provides more consistent resources
        if urbanEnvironment > 0.5:
            availability = availability * 0.8 + 0.2
        
        # Ensure availability is between 0 and 1
        availability = max(0.0, min(1.0, availability))
        
        return availability
        
    except Exception as e:
        logger.error(f"Error in calculateResourceAvailability: {str(e)}")
        return 0.5

def calculateResourceImpact(resourceAvailability):
    """Calculate impact of resource availability on population."""
    try:
        # Resource impact follows a sigmoid curve
        if resourceAvailability <= 0:
            return 0.0
        elif resourceAvailability >= 1:
            return 1.0
        else:
            # Sigmoid function centered at 0.5
            x = (resourceAvailability - 0.5) * 10  # Scale factor of 10
            return 1.0 / (1.0 + math.exp(-x))
    except Exception as e:
        logger.error(f"Error in calculateResourceImpact: {str(e)}")
        return 0.5

def calculateMonthlyMortality(params, colony):
    """Calculate monthly mortality rate based on various factors."""
    try:
        # Get carrying capacity
        carryingCapacity = calculateCarryingCapacity(params)
        
        # Extract parameters
        urbanRisk = params.get('urbanRisk', 0.1)
        diseaseRisk = params.get('diseaseRisk', 0.05)
        naturalRisk = params.get('naturalRisk', 0.08)
        
        # Base mortality rate
        baseMortality = naturalRisk
        
        # Add urban-related mortality
        urbanFactor = params.get('urbanEnvironment', 0.5)
        baseMortality += urbanRisk * urbanFactor
        
        # Disease risk increases with population density
        populationDensity = colony.total_cats / carryingCapacity if carryingCapacity > 0 else 1.0
        diseaseMortality = diseaseRisk * (1.0 + math.log(populationDensity + 1))
        
        # Combine mortality factors
        totalMortality = baseMortality + diseaseMortality
        
        # Cap at reasonable maximum
        return min(totalMortality, 0.5)
        
    except Exception as e:
        logger.error(f"Error in calculateMonthlyMortality: {str(e)}")
        return 0.1

def calculateBreedingSuccess(params, colony, environmentFactor):
    """Calculate breeding success rate based on various factors."""
    try:
        # Extract parameters
        baseBreedingRate = params.get('breedingRate', 0.3)
        minBreedingAge = params.get('earlyBreedingAge', 6)
        peakBreedingAge = params.get('peakBreedingAge', 24)
        
        # Calculate age-based breeding success
        breedingAgeRange = peakBreedingAge - minBreedingAge
        if breedingAgeRange <= 0:
            return 0.0
            
        # Get breeding population
        breedingPopulation = sum(1 for cat in colony.cats 
                               if minBreedingAge <= cat.age <= peakBreedingAge 
                               and not cat.sterilized)
        
        if breedingPopulation == 0:
            return 0.0
            
        # Calculate success rate
        successRate = baseBreedingRate * environmentFactor
        
        # Apply density-dependent effects
        densityFactor = calculateDensityImpact(colony.total_cats, params.get('carryingCapacity', 1000))
        successRate *= densityFactor
        
        return min(successRate, 1.0)
        
    except Exception as e:
        logger.error(f"Error in calculateBreedingSuccess: {str(e)}")
        return 0.0
