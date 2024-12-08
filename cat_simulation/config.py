"""Configuration parameters for the cat colony simulation."""

# Core constants
GESTATION_MONTHS = 2  # Cat gestation period is approximately 2 months (63-65 days)

# Enhanced parameters with more dynamic scaling
DEFAULT_PARAMS = {
    # Core breeding parameters
    'breeding_rate': 0.85,
    'kittens_per_litter': 4.0,
    'litters_per_year': 2.5,
    'kitten_survival_rate': 0.7,  # Increased from 0.5 - more realistic survival rate
    'female_ratio': 0.5,
    'adult_survival_rate': 0.85,  # Increased from 0.75 - more realistic for managed colonies
    'kitten_maturity_months': 5,
    'gestation_months': GESTATION_MONTHS,
    
    # Cost parameters
    'sterilization_cost': 50.0,
    
    # Colony density factors
    'territory_size': 100,
    'density_impact_threshold': 1.2,  # Increased to allow for larger colonies
    
    # Seasonal factors
    'seasonal_breeding_amplitude': 0.2,
    'peak_breeding_month': 3,
    
    # Resource factors
    'base_food_capacity': 0.9,    # Increased from 0.8
    'food_scaling_factor': 0.8,   # Reduced to make food less scarce
    'water_availability': 0.9,    # Increased from 0.8
    'shelter_quality': 0.85,      # Increased from 0.7
    
    # Environmental risks
    'urban_risk': 0.03,          # Reduced from 0.05
    'disease_risk': 0.02,        # Reduced from 0.04
    'natural_risk': 0.02,        # Reduced from 0.03
    
    # Human interaction factors
    'caretaker_support': 0.8,    # Increased from 0.6
    'feeding_consistency': 0.85,  # Increased from 0.7
    'human_interference': 0.3,    # Reduced from 0.5 for less negative impact
    
    # Abandonment factors
    'monthly_abandonment': 1,
    'abandoned_sterilized_ratio': 0.2
}
