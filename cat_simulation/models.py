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
        
        # Distribute unsterilized cats across age groups
        unsterilized = total_cats - sterilized
        if unsterilized > 0:
            # Assume about 20% are under maturity age (reduced from 30%)
            kitten_count = max(1, int(unsterilized * 0.2))
            adult_count = unsterilized - kitten_count
            
            # Distribute kittens across 0 to maturity months
            if kitten_count > 0:
                # Use triangular distribution to favor younger kittens
                ages = np.random.triangular(0, 0, maturity_months, kitten_count)
                ages = ages.astype(int)
                age_counts = np.bincount(ages)
                for age, count in enumerate(age_counts):
                    if count > 0:
                        colony['young_kittens'].append([int(count), int(age)])
            
            # Add reproductive adults with wider age distribution
            if adult_count > 0:
                # Create a more realistic age distribution
                # 40% young adults (maturity to 24 months)
                # 30% middle-aged (24 to 48 months)
                # 20% mature (48 to 72 months)
                # 10% senior (72 to 96 months)
                young_adults = int(adult_count * 0.4)
                middle_aged = int(adult_count * 0.3)
                mature = int(adult_count * 0.2)
                senior = adult_count - young_adults - middle_aged - mature  # Remainder to seniors
                
                # Distribute across age ranges
                ages = []
                if young_adults > 0:
                    ages.extend(np.random.randint(maturity_months, 24, young_adults))
                if middle_aged > 0:
                    ages.extend(np.random.randint(24, 48, middle_aged))
                if mature > 0:
                    ages.extend(np.random.randint(48, 72, mature))
                if senior > 0:
                    ages.extend(np.random.randint(72, 96, senior))
                
                age_counts = np.bincount(ages)
                for age, count in enumerate(age_counts):
                    if count > 0:
                        colony['reproductive'].append([int(count), int(age)])
        
        # Add sterilized cats with similar age distribution
        if sterilized > 0:
            # Use the same age distribution for sterilized cats
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
            
            age_counts = np.bincount(ages)
            for age, count in enumerate(age_counts):
                if count > 0:
                    colony['sterilized'].append([int(count), int(age)])
        
        # Calculate initial pregnancies (reduced probability)
        female_ratio = float(params.get('female_ratio', 0.5))
        reproductive_count = sum(int(count) for count, _ in colony['reproductive'])
        reproductive_females = int(reproductive_count * female_ratio)
        
        if reproductive_females > 0:
            # Reduce initial pregnancy rate to 10% (from 20%)
            initial_pregnant = int(reproductive_females * 0.1)
        else:
            initial_pregnant = 0
            
        return colony, initial_pregnant
        
    except Exception as e:
        logger.error(f"Error in colony initialization: {str(e)}")
        logger.error(traceback.format_exc())
        raise ValueError(f"Failed to initialize colony: {str(e)}")
