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
            'sterilized': [],
            'sterilized_kittens': []  # Added sterilized_kittens category
        }
        
        # Get maturity months parameter early since we need it for both unsterilized and sterilized cats
        maturity_months = int(float(params.get('kitten_maturity_months', 5)))
        if maturity_months < 1:
            raise ValueError("kitten_maturity_months must be at least 1")
            
        logger.debug(f"Using maturity_months={maturity_months}")
        
        # Distribute unsterilized cats across age groups
        unsterilized = total_cats - sterilized
        if unsterilized > 0:
            # For very small colonies, ensure at least one reproductive adult
            if unsterilized == 1:
                colony['reproductive'].append([1, maturity_months])
            else:
                # Assume about 20% are under maturity age (reduced from 30%)
                kitten_count = max(1, int(unsterilized * 0.2)) if unsterilized > 2 else 0
                adult_count = unsterilized - kitten_count
                
                logger.debug(f"Distributing {unsterilized} unsterilized cats: {kitten_count} kittens, {adult_count} adults")
                
                # Distribute kittens across 0 to maturity months
                if kitten_count > 0:
                    # For very small numbers, just put them at random ages
                    if kitten_count <= 3:
                        for _ in range(kitten_count):
                            age = np.random.randint(0, maturity_months)
                            colony['young_kittens'].append([1, age])
                    else:
                        # Use triangular distribution for larger numbers
                        ages = np.random.triangular(0, 0, maturity_months, kitten_count)
                        ages = np.clip(ages, 0, maturity_months - 1).astype(int)
                        age_counts = np.bincount(ages, minlength=maturity_months)
                        for age, count in enumerate(age_counts):
                            if count > 0:
                                colony['young_kittens'].append([int(count), int(age)])
                
                # Add reproductive adults with wider age distribution
                if adult_count > 0:
                    # For very small numbers, distribute evenly
                    if adult_count <= 3:
                        age_ranges = [(maturity_months, 24), (24, 48), (48, 72)]
                        for i in range(adult_count):
                            min_age, max_age = age_ranges[i % len(age_ranges)]
                            age = np.random.randint(min_age, max_age)
                            colony['reproductive'].append([1, age])
                    else:
                        # Create a more realistic age distribution for larger numbers
                        young_adults = max(1, int(adult_count * 0.4))
                        middle_aged = max(1, int(adult_count * 0.3))
                        mature = max(1, int(adult_count * 0.2))
                        senior = max(0, adult_count - young_adults - middle_aged - mature)
                        
                        logger.debug(f"Adult distribution: young={young_adults}, middle={middle_aged}, mature={mature}, senior={senior}")
                        
                        # Add each age group separately
                        if young_adults > 0:
                            age = np.random.randint(maturity_months, 24)
                            colony['reproductive'].append([young_adults, age])
                        if middle_aged > 0:
                            age = np.random.randint(24, 48)
                            colony['reproductive'].append([middle_aged, age])
                        if mature > 0:
                            age = np.random.randint(48, 72)
                            colony['reproductive'].append([mature, age])
                        if senior > 0:
                            age = np.random.randint(72, 96)
                            colony['reproductive'].append([senior, age])
        
        # Handle sterilized cats
        if sterilized > 0:
            # Similar age distribution for sterilized cats
            if sterilized <= 3:
                # For very small numbers, distribute evenly
                age_ranges = [(maturity_months, 24), (24, 48), (48, 72)]
                for i in range(sterilized):
                    min_age, max_age = age_ranges[i % len(age_ranges)]
                    age = np.random.randint(min_age, max_age)
                    colony['sterilized'].append([1, age])
            else:
                # Use similar distribution as reproductive cats
                young_adults = max(1, int(sterilized * 0.4))
                middle_aged = max(1, int(sterilized * 0.3))
                mature = max(1, int(sterilized * 0.2))
                senior = max(0, sterilized - young_adults - middle_aged - mature)
                
                if young_adults > 0:
                    age = np.random.randint(maturity_months, 24)
                    colony['sterilized'].append([young_adults, age])
                if middle_aged > 0:
                    age = np.random.randint(24, 48)
                    colony['sterilized'].append([middle_aged, age])
                if mature > 0:
                    age = np.random.randint(48, 72)
                    colony['sterilized'].append([mature, age])
                if senior > 0:
                    age = np.random.randint(72, 96)
                    colony['sterilized'].append([senior, age])
        
        # Calculate initial pregnancies (20% of reproductive females)
        initial_pregnant = 0
        if colony['reproductive']:
            reproductive_females = sum(count for count, _ in colony['reproductive']) * params.get('female_ratio', 0.5)
            initial_pregnant = int(reproductive_females * 0.2)
            
        logger.debug(f"Initialized colony structure: {colony}")
        logger.debug(f"Initial pregnant females: {initial_pregnant}")
        
        return colony, initial_pregnant
        
    except Exception as e:
        logger.error(f"Error in colony initialization: {str(e)}")
        logger.error(traceback.format_exc())
        raise ValueError(f"Failed to initialize colony: {str(e)}")
