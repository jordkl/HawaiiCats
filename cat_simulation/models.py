"""Data models and initialization functions for cat colony simulation."""

import numpy as np
import logging
import traceback

logger = logging.getLogger(__name__)

def initialize_colony_with_ages(total_cats, sterilized, params):
    """Initialize a colony with randomized ages and initial pregnancies.
    Returns: Dictionary with age groups and their counts, and initial pregnant cats"""
    try:
        # Input validation and conversion to integers
        total_cats = int(float(total_cats))
        sterilized = int(float(sterilized))
        
        logger.debug(f"Initializing colony with {total_cats} total cats, {sterilized} sterilized")
        
        if total_cats < 1:
            raise ValueError("total_cats must be a positive number")
        if sterilized < 0:
            raise ValueError("sterilized must be a non-negative number")
        if sterilized > total_cats:
            raise ValueError("sterilized count cannot exceed total cats")
        
        # Initialize basic age structure
        colony = {
            'young_kittens': [],  # [count, age_in_months]
            'reproductive': [],
            'sterilized': []
        }
        
        # Get maturity months parameter early since we need it for both unsterilized and sterilized cats
        maturity_months = int(float(params.get('kitten_maturity_months', 5)))
        if maturity_months < 1:
            raise ValueError("kitten_maturity_months must be at least 1")
            
        logger.debug(f"Using maturity_months={maturity_months}")
        
        # Distribute unsterilized cats across age groups
        unsterilized = total_cats - sterilized
        if unsterilized > 0:
            # Assume about 20% are under maturity age (reduced from 30%)
            kitten_count = max(1, int(unsterilized * 0.2))
            adult_count = unsterilized - kitten_count
            
            logger.debug(f"Distributing {unsterilized} unsterilized cats: {kitten_count} kittens, {adult_count} adults")
            
            # Distribute kittens across 0 to maturity months
            if kitten_count > 0:
                # Use triangular distribution to favor younger kittens
                ages = np.random.triangular(0, 0, maturity_months, kitten_count)
                ages = np.clip(ages, 0, maturity_months - 1).astype(int)  # Ensure ages are within bounds
                age_counts = np.bincount(ages, minlength=maturity_months)  # Ensure minimum length
                logger.debug(f"Kitten age distribution: {dict(enumerate(age_counts))}")
                for age, count in enumerate(age_counts):
                    if count > 0:
                        colony['young_kittens'].append([int(count), int(age)])
            
            # Add reproductive adults with wider age distribution
            if adult_count > 0:
                # Create a more realistic age distribution
                young_adults = int(adult_count * 0.4)
                middle_aged = int(adult_count * 0.3)
                mature = int(adult_count * 0.2)
                senior = adult_count - young_adults - middle_aged - mature
                
                logger.debug(f"Adult distribution: young={young_adults}, middle={middle_aged}, mature={mature}, senior={senior}")
                
                ages = []
                if young_adults > 0:
                    young_ages = np.random.randint(maturity_months, 24, young_adults)
                    logger.debug(f"Young adult ages: {young_ages.tolist()}")
                    ages.extend(young_ages)
                if middle_aged > 0:
                    middle_ages = np.random.randint(24, 48, middle_aged)
                    logger.debug(f"Middle-aged ages: {middle_ages.tolist()}")
                    ages.extend(middle_ages)
                if mature > 0:
                    mature_ages = np.random.randint(48, 72, mature)
                    logger.debug(f"Mature ages: {mature_ages.tolist()}")
                    ages.extend(mature_ages)
                if senior > 0:
                    senior_ages = np.random.randint(72, 96, senior)
                    logger.debug(f"Senior ages: {senior_ages.tolist()}")
                    ages.extend(senior_ages)
                
                if ages:
                    age_counts = np.bincount(ages, minlength=96)
                    logger.debug(f"Adult age counts: {dict([(i,c) for i,c in enumerate(age_counts) if c > 0])}")
                    for age, count in enumerate(age_counts):
                        if count > 0:
                            colony['reproductive'].append([int(count), int(age)])
                else:
                    logger.warning("No adult ages generated despite adult_count > 0")
        
        # Add sterilized cats with similar age distribution
        if sterilized > 0:
            logger.debug(f"Distributing {sterilized} sterilized cats")
            young_adults = int(sterilized * 0.4)
            middle_aged = int(sterilized * 0.3)
            mature = int(sterilized * 0.2)
            senior = sterilized - young_adults - middle_aged - mature
            
            ages = []
            if young_adults > 0:
                ages.extend(np.random.randint(maturity_months, 24, young_adults))
            if middle_aged > 0:
                ages.extend(np.random.randint(24, 48, middle_aged))
            if mature > 0:
                ages.extend(np.random.randint(48, 72, mature))
            if senior > 0:
                ages.extend(np.random.randint(72, 96, senior))
            
            if ages:
                age_counts = np.bincount(ages, minlength=96)
                logger.debug(f"Sterilized age counts: {dict([(i,c) for i,c in enumerate(age_counts) if c > 0])}")
                for age, count in enumerate(age_counts):
                    if count > 0:
                        colony['sterilized'].append([int(count), int(age)])
            else:
                logger.warning("No sterilized ages generated despite sterilized > 0")
        
        # Calculate initial pregnancies (reduced probability)
        female_ratio = float(params.get('female_ratio', 0.5))
        reproductive_count = sum(int(count) for count, _ in colony['reproductive'])
        reproductive_females = int(reproductive_count * female_ratio)
        
        if reproductive_females > 0:
            initial_pregnant = int(reproductive_females * 0.1)
            logger.debug(f"Initial pregnancies: {initial_pregnant} out of {reproductive_females} females")
        else:
            initial_pregnant = 0
            logger.debug("No initial pregnancies (no reproductive females)")
            
        logger.debug(f"Final colony structure: {colony}")
        return colony, initial_pregnant
        
    except Exception as e:
        logger.error(f"Error in colony initialization: {str(e)}")
        logger.error(traceback.format_exc())
        raise ValueError(f"Failed to initialize colony: {str(e)}")
