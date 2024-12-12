"""Constants for cat colony simulation."""

DEFAULT_PARAMS = {
    "breeding_rate": 0.85,
    "kittens_per_litter": 4,
    "litters_per_year": 2.5,
    "kitten_survival_rate": 0.8,
    "female_ratio": 0.5,
    "adult_survival_rate": 0.92,
    "kitten_maturity_months": 5,
    "seasonal_breeding_amplitude": 0.15,
    "peak_breeding_month": 3,
    "base_food_capacity": 0.95,
    "food_scaling_factor": 0.9,
    "water_availability": 0.95,
    "shelter_quality": 0.85,
    "urban_risk": 0.08,
    "disease_risk": 0.04,
    "natural_risk": 0.04,
    "caretaker_support": 1.0,
    "feeding_consistency": 0.95,
    "sterilization_cost": 50.0,
    "monthly_abandonment": 0,  
    "abandoned_sterilized_ratio": 0.2,
    "territory_size": 1000,
    "density_impact_threshold": 1.3
}

# Biological constants based on cat physiology
MIN_BREEDING_AGE = 5    
MAX_BREEDING_AGE = 84   
GESTATION_MONTHS = 2    

# Territory size in square meters
TERRITORY_SIZE_RANGES = {
    'min': 100,    
    'max': 100000, 
    'default': 1000,
    'description': 'Territory size in square meters. Examples: 100 (small parking lot), 500 (restaurant back area), ' +
                  '1000 (small park), 5000 (large park), 20000 (small forest), 100000 (large forest/nature reserve)'
}

# Density impact threshold (cats per 100 square meters)
DENSITY_THRESHOLD_RANGES = {
    'min': 0.2,    
    'max': 5.0,    
    'default': 1.2,
    'description': 'Cats per 100 square meters where density effects begin. Examples: 0.2 (rural/forest), ' +
                  '1.0 (suburban), 2.0 (urban), 5.0 (dense urban with abundant resources)'
}
