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
            # Assume about 30% are under maturity age
            kitten_count = max(1, int(unsterilized * 0.3))
            adult_count = unsterilized - kitten_count
            
            # Distribute kittens across 0 to maturity months
            if kitten_count > 0:
                ages = np.random.randint(0, maturity_months, kitten_count)
                age_counts = np.bincount(ages)
                for age, count in enumerate(age_counts):
                    if count > 0:
                        colony['young_kittens'].append([int(count), int(age)])
            
            # Add reproductive adults
            if adult_count > 0:
                # Distribute adults across age ranges (12-month spans)
                adult_ages = np.random.randint(maturity_months, maturity_months + 36, adult_count)
                age_counts = np.bincount(adult_ages - maturity_months)
                for age, count in enumerate(age_counts):
                    if count > 0:
                        colony['reproductive'].append([int(count), int(age + maturity_months)])
        
        # Add sterilized cats
        if sterilized > 0:
            # Distribute sterilized cats across age ranges
            sterilized_ages = np.random.randint(maturity_months, maturity_months + 48, sterilized)
            age_counts = np.bincount(sterilized_ages - maturity_months)
            for age, count in enumerate(age_counts):
                if count > 0:
                    colony['sterilized'].append([int(count), int(age + maturity_months)])
        
        # Calculate initial pregnancies - ensure float operations before converting to int
        female_ratio = float(params.get('female_ratio', 0.5))
        reproductive_count = sum(int(count) for count, _ in colony['reproductive'])
        reproductive_females = int(reproductive_count * female_ratio)
        
        if reproductive_females > 0:
            # About 20% of reproductive females might be pregnant initially
            initial_pregnant = int(reproductive_females * 0.2)
        else:
            initial_pregnant = 0
            
        return colony, initial_pregnant
        
    except Exception as e:
        logger.error(f"Error in colony initialization: {str(e)}")
        logger.error(traceback.format_exc())
        raise ValueError(f"Failed to initialize colony: {str(e)}")
