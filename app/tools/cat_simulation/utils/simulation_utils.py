"""Utility functions for cat population simulation."""
import numpy as np
import logging
import traceback
import json

logger = logging.getLogger('debug')

def validateParams(params):
    """
    Validate simulation parameters.
    
    Args:
        params (dict): Dictionary of simulation parameters
        
    Returns:
        bool: True if parameters are valid, False otherwise
        str: Error message if parameters are invalid, None otherwise
    """
    try:
        required_params = [
            'litterSize',
            'kittenSurvivalRate',
            'adultSurvivalRate',
            'breedingAge',
            'maxAge',
            'baseBreedingRate',
            'seasonalBreedingAmplitude',
            'peakBreedingMonth',
            'baseFoodCapacity',
            'waterAvailability',
            'shelterQuality',
            'territorySize',
            'densityThreshold'
        ]
        
        # Check for required parameters
        for param in required_params:
            if param not in params:
                return False, f"Missing required parameter: {param}"
            
            # Check numeric values
            try:
                value = float(params[param])
                if value < 0:
                    return False, f"Parameter {param} must be non-negative"
            except (ValueError, TypeError):
                return False, f"Parameter {param} must be numeric"
        
        # Validate specific parameter ranges
        validations = [
            ('litterSize', 1.0, 8.0),
            ('kittenSurvivalRate', 0.0, 1.0),
            ('adultSurvivalRate', 0.0, 1.0),
            ('breedingAge', 4, 24),
            ('maxAge', 24, 240),
            ('baseBreedingRate', 0.0, 1.0),
            ('seasonalBreedingAmplitude', 0.0, 1.0),
            ('peakBreedingMonth', 1, 12),
            ('baseFoodCapacity', 0.0, 1.0),
            ('waterAvailability', 0.0, 1.0),
            ('shelterQuality', 0.0, 1.0),
            ('densityThreshold', 0.0, 2.0)
        ]
        
        for param, min_val, max_val in validations:
            value = float(params[param])
            if value < min_val or value > max_val:
                return False, f"Parameter {param} must be between {min_val} and {max_val}"
        
        # Territory size must be positive
        if float(params['territorySize']) <= 0:
            return False, "Territory size must be positive"
            
        return True, None
        
    except Exception as e:
        return False, f"Parameter validation error: {str(e)}"

def calculateSeasonalFactor(month, peakMonth=4, seasonalIntensity=0.4):
    """
    Calculate seasonal breeding factor based on month and intensity.
    
    Args:
        month (int): Current month (1-12)
        peakMonth (int): Peak breeding month (1-12)
        seasonalIntensity (float): Intensity of seasonal effects (0-1)
        
    Returns:
        float: Seasonal breeding factor (0-1)
    """
    try:
        # Convert parameters
        month = int(month) if month is not None else 6
        peakMonth = int(peakMonth) if peakMonth is not None else 4
        seasonalIntensity = float(seasonalIntensity) if seasonalIntensity is not None else 0.4
        
        # Ensure month and peak month are in valid range
        month = max(1, min(12, month))
        peakMonth = max(1, min(12, peakMonth))
        
        # Calculate distance from peak month
        monthDiff = abs(((month - peakMonth + 6) % 12) - 6)
        
        # Base seasonal factor (cosine curve with sharper peaks)
        baseFactor = np.power(0.5 * (1.0 + np.cos(2.0 * np.pi * monthDiff / 12.0)), 1.5)
        
        # Apply intensity with stronger effect
        if seasonalIntensity <= 0.0:
            return 1.0  # No seasonal effects
            
        # Scale factor based on intensity with stronger variation
        scaledFactor = 1.0 - (seasonalIntensity * (1.0 - baseFactor))
        
        # Ensure reasonable bounds with wider range
        return max(0.2, min(1.0, scaledFactor))
        
    except Exception as e:
        logger.error(f"Error in calculateSeasonalFactor: {str(e)}")
        logger.error(traceback.format_exc())
        return 0.7  # Return moderate factor on error

def calculateResourceAvailability(baseFood, waterAvailability, shelterQuality, caretakerSupport, feedingConsistency):
    """
    Calculate resource availability factor based on various inputs.
    
    Args:
        baseFood (float): Base food availability (0-1)
        waterAvailability (float): Water availability (0-1)
        shelterQuality (float): Quality of shelter (0-1)
        caretakerSupport (float): Support from caretakers (0-1)
        feedingConsistency (float): Consistency of feeding (0-1)
        
    Returns:
        float: Resource availability factor (0-1)
    """
    try:
        # Convert parameters to float
        baseFood = float(baseFood) if baseFood is not None else 0.8
        waterAvailability = float(waterAvailability) if waterAvailability is not None else 0.8
        shelterQuality = float(shelterQuality) if shelterQuality is not None else 0.7
        caretakerSupport = float(caretakerSupport) if caretakerSupport is not None else 0.5
        feedingConsistency = float(feedingConsistency) if feedingConsistency is not None else 0.7
        
        # Food and water are critical - use geometric mean
        survivalResources = np.power(baseFood * waterAvailability, 0.5)
        
        # Shelter and support are important but less critical
        supportResources = (0.7 * shelterQuality + 0.3 * caretakerSupport)
        
        # Feeding consistency affects resource stability
        stabilityFactor = 0.8 + 0.2 * feedingConsistency
        
        # Calculate final availability with stronger impact of poor conditions
        rawAvailability = (
            0.5 * np.power(survivalResources, 1.5) +  # Stronger impact of survival resources
            0.3 * supportResources +
            0.2 * stabilityFactor
        )
        
        # Apply sigmoid function to create steeper dropoff in poor conditions
        scaledAvailability = 1.0 / (1.0 + np.exp(-8.0 * (rawAvailability - 0.5)))
        
        # Ensure reasonable bounds with wider range for poor conditions
        return max(0.1, min(1.0, scaledAvailability))
        
    except Exception as e:
        logger.error(f"Error in calculateResourceAvailability: {str(e)}")
        logger.error(traceback.format_exc())
        return 0.5  # Return moderate availability on error

def calculateCarryingCapacity(territorySize, densityThreshold, resourceFactor):
    """
    Calculate carrying capacity based on territory size and resources.
    
    Args:
        territorySize (float): Size of territory in square meters
        densityThreshold (float): Cats per square meter threshold
        resourceFactor (float): Resource availability factor (0-1)
        
    Returns:
        float: Carrying capacity (number of cats)
    """
    try:
        # Convert parameters to float
        territorySize = float(territorySize) if territorySize is not None else 1000.0
        densityThreshold = float(densityThreshold) if densityThreshold is not None else 1.2
        resourceFactor = float(resourceFactor) if resourceFactor is not None else 0.8

        # Base capacity from territory size
        baseCapacity = territorySize * densityThreshold * 0.5  # Reduced base capacity multiplier
        
        # Resource factor has strong impact on capacity
        resourceMultiplier = 0.3 + (0.7 * resourceFactor)  # More impact from resources
        
        # Calculate final capacity
        capacity = baseCapacity * resourceMultiplier
        
        # Ensure minimum viable population size
        return max(10.0, capacity)  # Lower minimum capacity
        
    except Exception as e:
        logger.error(f"Error in calculateCarryingCapacity: {str(e)}")
        logger.error(traceback.format_exc())
        return 20.0  # Return lower capacity on error

def calculateDensityImpact(currentSize, carryingCapacity, densityImpactThreshold=0.8):
    """
    Calculate impact of population density on population dynamics.
    
    Args:
        currentSize (int): Current population size
        carryingCapacity (float): Carrying capacity of the environment
        densityImpactThreshold (float): Threshold at which density effects become significant
        
    Returns:
        float: Density impact factor (0-1)
    """
    try:
        # Convert parameters
        currentSize = float(currentSize)
        carryingCapacity = float(carryingCapacity)
        densityImpactThreshold = float(densityImpactThreshold)
        
        # Calculate density ratio
        densityRatio = currentSize / carryingCapacity if carryingCapacity > 0 else float('inf')
        
        # No impact below threshold
        if densityRatio < densityImpactThreshold:
            return 0.0
            
        # Exponential impact above threshold
        impact = min(1.0, (densityRatio - densityImpactThreshold) ** 2)
        
        # Stronger impact when significantly over capacity
        if densityRatio > 1.5:
            impact = min(1.0, impact * 1.5)
            
        return impact
        
    except Exception as e:
        logger.error(f"Error in calculateDensityImpact: {str(e)}")
        logger.error(traceback.format_exc())
        return 0.5  # Return moderate impact on error

def calculateBreedingSuccess(seasonalFactor, resourceFactor, densityImpact, baseBreedingRate=0.85):
    """
    Calculate breeding success rate based on environmental factors.
    
    Args:
        seasonalFactor (float): Seasonal breeding factor (0-1)
        resourceFactor (float): Resource availability factor (0-1)
        densityImpact (float): Impact of population density (0-1)
        baseBreedingRate (float): Base breeding success rate (0-1)
        
    Returns:
        float: Breeding success rate (0-1)
    """
    try:
        # Convert parameters to float
        seasonalFactor = float(seasonalFactor) if seasonalFactor is not None else 0.5
        resourceFactor = float(resourceFactor) if resourceFactor is not None else 0.8
        densityImpact = float(densityImpact) if densityImpact is not None else 0.2
        baseBreedingRate = float(baseBreedingRate) if baseBreedingRate is not None else 0.85

        # Strong seasonal effect (higher range)
        seasonalEffect = 0.8 + (1.2 * seasonalFactor)  # Range: 0.8-2.0
        
        # Resource availability has major impact (higher range)
        resourceEffect = 0.8 + (1.0 * resourceFactor)  # Range: 0.8-1.8
        
        # Density impact reduces breeding success (less severe reduction)
        densityEffect = 1.0 - (densityImpact * 0.3)  # Range: 0.7-1.0
        
        # Calculate breeding success with higher base rate and stronger effects
        breedingSuccess = (
            baseBreedingRate *
            seasonalEffect *
            resourceEffect *
            densityEffect
        )
        
        # Ensure result is between 0 and 1 with higher minimum
        return max(0.1, min(1.0, breedingSuccess))
        
    except Exception as e:
        logger.error(f"Error in calculateBreedingSuccess: {str(e)}")
        logger.error(traceback.format_exc())
        return 0.5  # Return moderate breeding success on error

def calculateMonthlyMortality(urbanRisk, diseaseRisk, naturalRisk, densityImpact, resourceFactor):
    """
    Calculate monthly mortality rate based on various risk factors.
    
    Args:
        urbanRisk (float): Risk from urban environment (0-1)
        diseaseRisk (float): Risk from diseases (0-1)
        naturalRisk (float): Natural mortality risk (0-1)
        densityImpact (float): Impact of population density (0-1)
        resourceFactor (float): Resource availability factor (0-1)
        
    Returns:
        float: Monthly mortality rate (0-1)
    """
    try:
        # Convert parameters to float
        urbanRisk = float(urbanRisk) if urbanRisk is not None else 0.15
        diseaseRisk = float(diseaseRisk) if diseaseRisk is not None else 0.1
        naturalRisk = float(naturalRisk) if naturalRisk is not None else 0.1
        densityImpact = float(densityImpact) if densityImpact is not None else 0.2
        resourceFactor = float(resourceFactor) if resourceFactor is not None else 0.8

        # Base mortality rate (reduced)
        baseMortality = 0.03  # 3% base monthly mortality
        
        # Urban risk has moderate impact
        urbanEffect = 1.0 + (urbanRisk * 0.3)  # Max 30% increase
        
        # Disease risk has significant impact at high density
        diseaseEffect = 1.0 + (diseaseRisk * densityImpact * 0.5)  # Max 50% increase
        
        # Natural risk varies with resource availability
        naturalEffect = 1.0 + (naturalRisk * (1.0 - resourceFactor) * 0.4)  # Max 40% increase
        
        # Resource scarcity increases mortality
        resourceEffect = 1.0 + ((1.0 - resourceFactor) * 0.3)  # Max 30% increase
        
        # High density increases mortality
        densityEffect = 1.0 + (densityImpact * 0.4)  # Max 40% increase
        
        # Calculate total mortality rate
        mortalityRate = (
            baseMortality *
            urbanEffect *
            diseaseEffect *
            naturalEffect *
            resourceEffect *
            densityEffect
        )
        
        # Ensure reasonable bounds
        return max(0.01, min(0.15, mortalityRate))  # 1-15% monthly mortality
        
    except Exception as e:
        logger.error(f"Error in calculateMortalityRate: {str(e)}")
        logger.error(traceback.format_exc())
        return 0.05  # Return moderate mortality rate on error

def calculateResourceImpact(resourceAvailability):
    """Calculate the impact of resource availability on population growth."""
    try:
        # Convert parameter to float if needed
        resourceAvailability = float(resourceAvailability) if isinstance(resourceAvailability, (int, float, str)) else 0.8
        
        # More nuanced non-linear response to resource availability
        # Use a sigmoid-like curve for smoother transitions
        k = 2.0  
        midpoint = 0.5  
        
        # Transform resourceAvailability using sigmoid function
        impact = 1.0 / (1.0 + np.exp(-k * (resourceAvailability - midpoint)))
        
        # Scale the impact to be between 0.2 and 1.0
        # This ensures even severe resource constraints don't completely halt population growth
        scaledImpact = 0.2 + (0.8 * impact)
        
        return float(scaledImpact)
    except Exception as e:
        logger.error(f"Error in calculateResourceImpact: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def calculateImmigration(params, currentPopulation):
    """Calculate monthly immigration rate with balanced effects."""
    try:
        # Convert parameters to float if needed
        territorySize = float(params.get('territorySize', 1000))
        hectares = territorySize / 10000
        optimalDensity = 3.0
        carryingCapacity = optimalDensity * hectares
        
        # Moderate base immigration rate
        baseRate = 0.06  
        urbanFactor = float(params.get('urbanEnvironment', 0.7))
        
        # More balanced urban and caretaker effects
        caretakerSupport = float(params.get('caretakerSupport', 1.0))
        immigrationModifier = 1.0 + (0.2 * urbanFactor) + (0.15 * (caretakerSupport - 1.0))  
        
        # More gradual density-dependent decline
        densityFactor = max(0, 1.0 - np.power(currentPopulation / carryingCapacity, 1.2))  
        
        # Calculate monthly immigrants
        monthlyImmigrants = int(carryingCapacity * baseRate * immigrationModifier * densityFactor)
        
        # Moderate random variation
        variation = np.random.normal(0, 0.15)  
        monthlyImmigrants = int(monthlyImmigrants * (1 + variation))
        
        return max(0, monthlyImmigrants)
    except Exception as e:
        logger.error(f"Error in calculateImmigration: {str(e)}")
        logger.error(traceback.format_exc())
        return 0

def boundProbability(p):
    """Ensure probability is between 0 and 1"""
    return min(0.95, max(0.001, float(p)))  

def calculateMortalityRate(params, ageMonths, environmentFactor, month):
    """
    Calculate mortality rate based on age and environmental factors.
    
    Args:
        params (dict): Parameters for mortality rates
        ageMonths (int): Age of cat in months
        environmentFactor (float): Environmental factor (0-1)
        month (int): Current month (0-11)
        
    Returns:
        float: Mortality rate (0-1)
    """
    try:
        # Get base mortality rates
        if ageMonths < 6:  # Kitten
            baseRate = 1.0 - float(params.get('kittenSurvivalRate', 0.7))
        elif ageMonths < 72:  # Adult
            baseRate = 1.0 - float(params.get('adultSurvivalRate', 0.85))
        else:  # Senior
            baseRate = 1.0 - float(params.get('seniorSurvivalRate', 0.7))

        # Urban hazards have stronger impact
        urbanRate = float(params.get('urbanMortalityRate', 0.1))
        urbanFactor = 1.0 + (urbanRate * 2.5)  
        
        # Environmental stress has moderate effect on mortality
        envStress = max(1.0, 1.5 - environmentFactor)  
        
        # Disease impact increases with poor environmental conditions
        diseaseRate = float(params.get('diseaseMortalityRate', 0.1))
        diseaseFactor = 1.0 + (diseaseRate * 3.0 * (2.0 - environmentFactor))  
        
        # Calculate final mortality rate with increased urban sensitivity
        mortalityRate = (baseRate + diseaseRate) * urbanFactor * envStress
        
        # Ensure reasonable bounds
        return min(0.95, max(0.01, mortalityRate))
    except Exception as e:
        logger.error(f"Error in calculateMortalityRate: {str(e)}")
        logger.error(traceback.format_exc())
        return 0.05  

def calculateLitterSize(breedingSuccess, resourceFactor, seasonalFactor):
    """
    Calculate litter size based on breeding success and environmental factors.
    
    Args:
        breedingSuccess (float): Breeding success rate (0-1)
        resourceFactor (float): Resource availability factor (0-1)
        seasonalFactor (float): Seasonal breeding factor (0-1)
        
    Returns:
        int: Number of kittens in litter
    """
    try:
        # Convert parameters to float
        breedingSuccess = float(breedingSuccess) if breedingSuccess is not None else 0.5
        resourceFactor = float(resourceFactor) if resourceFactor is not None else 0.8
        seasonalFactor = float(seasonalFactor) if seasonalFactor is not None else 0.8

        # Base litter size calculation
        baseLitterSize = 4.0  # Average litter size for feral cats
        
        # Resource factor affects litter size
        resourceEffect = 0.7 + (0.6 * resourceFactor)  # Higher minimum effect
        
        # Seasonal factor has moderate impact
        seasonalEffect = 0.8 + (0.4 * seasonalFactor)  # Higher minimum effect
        
        # Breeding success influences size
        successEffect = 0.6 + (0.8 * breedingSuccess)  # Higher impact from success
        
        # Calculate final litter size
        litterSize = (
            baseLitterSize *
            resourceEffect *
            seasonalEffect *
            successEffect
        )
        
        # Round to nearest integer with minimum of 1
        return max(1, round(litterSize))
        
    except Exception as e:
        logger.error(f"Error in calculateLitterSize: {str(e)}")
        logger.error(traceback.format_exc())
        return 3  # Return average litter size on error
