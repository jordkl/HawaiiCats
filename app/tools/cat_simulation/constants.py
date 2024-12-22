"""Constants for cat colony simulation."""

DEFAULT_PARAMS = {
    # Population dynamics
    'breeding_rate': 0.85,
    'kittens_per_litter': 4,
    'litters_per_year': 2.5,
    'female_ratio': 0.5,
    'kitten_survival_rate': 0.7,
    'adult_survival_rate': 0.85,
    'kitten_maturity_months': 5,
    
    # Seasonal factors
    'peak_breeding_month': 4,
    'seasonality_strength': 0.3,
    
    # Environmental factors
    'territory_size': 1000,
    'base_food_capacity': 0.9,
    'food_scaling_factor': 0.8,
    'environmental_stress': 0.15,
    
    # Resource factors
    'resource_competition': 0.2,
    'resource_scarcity_impact': 0.25,
    
    # Colony density
    'density_impact_threshold': 1.2,
    'density_stress_rate': 0.15,
    'max_density_impact': 0.5,
    
    # Habitat quality
    'base_habitat_quality': 0.8,
    'urbanization_impact': 0.2,
    'disease_transmission_rate': 0.1,
    
    # Monthly abandonment rate
    'monthly_abandonment': 2.0,
}

# Biological constants
MIN_BREEDING_AGE = 5  # months
MAX_BREEDING_AGE = 84  # months (7 years)
GESTATION_MONTHS = 2  # months

# Territory size ranges (sq meters)
TERRITORY_SIZE_RANGES = {
    'urban': (100, 500),
    'suburban': (500, 2000),
    'rural': (2000, 5000)
}

# Density threshold ranges (cats per sq meter)
DENSITY_THRESHOLD_RANGES = {
    'urban': (0.05, 0.2),
    'suburban': (0.02, 0.1),
    'rural': (0.01, 0.05)
}
