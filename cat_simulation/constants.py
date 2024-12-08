"""Constants for cat colony simulation."""

DEFAULT_PARAMS = {
    "breeding_rate": 0.85,
    "kittens_per_litter": 4,
    "litters_per_year": 2.5,
    "kitten_survival_rate": 0.7,
    "female_ratio": 0.5,
    "adult_survival_rate": 0.9,
    "kitten_maturity_months": 5,
    "seasonal_breeding_amplitude": 0.2,
    "peak_breeding_month": 3,
    "base_food_capacity": 1.0,
    "food_scaling_factor": 0.9,
    "water_availability": 0.9,
    "shelter_quality": 0.8,
    "urban_risk": 0.1,
    "disease_risk": 0.05,
    "natural_risk": 0.05,
    "caretaker_support": 0.8,
    "feeding_consistency": 0.9,
    "sterilization_cost": 50.0,
    "monthly_abandonment": 0,  # Default to no monthly abandonment
    "abandoned_sterilized_ratio": 0.2,
    "territory_size": 1000,
    "density_impact_threshold": 1.2
}

# Biological constants based on cat physiology
MIN_BREEDING_AGE = 5    # Cats can breed at 5-6 months
MAX_BREEDING_AGE = 84   # Cats can breed up to ~7 years (84 months)
GESTATION_MONTHS = 2    # Cat pregnancy is ~63 days (2 months)
