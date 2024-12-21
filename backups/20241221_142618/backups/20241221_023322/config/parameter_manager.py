import json
import os
from typing import Dict, Any

class ParameterManager:
    def __init__(self, params_file: str = None):
        """Initialize the parameter manager with an optional custom parameters file."""
        if params_file is None:
            params_file = os.path.join(os.path.dirname(__file__), 'parameters.json')
        self.params_file = params_file
        self.params = self._load_parameters()

    def _load_parameters(self) -> Dict[str, Any]:
        """Load parameters from the JSON file."""
        try:
            with open(self.params_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Parameters file not found: {self.params_file}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in parameters file: {self.params_file}")

    def get_all_parameters(self) -> Dict[str, Any]:
        """Get all parameters as a flattened dictionary."""
        flattened = {}
        for category, params in self.params.items():
            flattened.update(params)
        return flattened

    def get_category_parameters(self, category: str) -> Dict[str, Any]:
        """Get parameters for a specific category."""
        return self.params.get(category, {})

    def update_parameter(self, category: str, param_name: str, value: float) -> None:
        """Update a specific parameter value."""
        if category not in self.params:
            raise ValueError(f"Category not found: {category}")
        if param_name not in self.params[category]:
            raise ValueError(f"Parameter not found in {category}: {param_name}")
        
        self.params[category][param_name] = float(value)

    def save_parameters(self) -> None:
        """Save current parameters back to the JSON file."""
        with open(self.params_file, 'w') as f:
            json.dump(self.params, f, indent=4)

    def update_from_web(self, params: Dict[str, Any]) -> None:
        """Update parameters from web interface input.
        
        Args:
            params: Dictionary of parameters from web interface
        """
        param_mapping = {
            'breeding_rate': ('breeding', 'breeding_rate'),
            'kittens_per_litter': ('breeding', 'kittens_per_litter'),
            'litters_per_year': ('breeding', 'litters_per_year'),
            'kitten_survival_rate': ('breeding', 'kitten_survival_rate'),
            'female_ratio': ('breeding', 'female_ratio'),
            'adult_survival_rate': ('breeding', 'adult_survival_rate'),
            'kitten_maturity_months': ('breeding', 'kitten_maturity_months'),
            'seasonal_breeding_amplitude': ('breeding', 'seasonal_breeding_amplitude'),
            'peak_breeding_month': ('breeding', 'peak_breeding_month'),
            'water_availability': ('environmental', 'water_availability'),
            'shelter_quality': ('environmental', 'shelter_quality'),
            'urban_risk': ('environmental', 'urban_risk'),
            'disease_risk': ('environmental', 'disease_risk'),
            'natural_risk': ('environmental', 'natural_risk'),
            'territory_size': ('environmental', 'territory_size'),
            'density_impact_threshold': ('environmental', 'density_impact_threshold'),
            'caretaker_support': ('human_factors', 'caretaker_support'),
            'feeding_consistency': ('human_factors', 'feeding_consistency'),
            'human_interference': ('human_factors', 'human_interference'),
            'monthly_abandonment': ('human_factors', 'monthly_abandonment'),
            'abandoned_sterilized_ratio': ('human_factors', 'abandoned_sterilized_ratio'),
            'sterilization_cost': ('costs', 'sterilization_cost')
        }

        for param_name, value in params.items():
            if param_name in param_mapping:
                category, param = param_mapping[param_name]
                try:
                    self.update_parameter(category, param, float(value))
                except (ValueError, TypeError) as e:
                    print(f"Error updating parameter {param_name}: {str(e)}")
        
        # Save the updated parameters
        self.save_parameters()

    def reset_to_defaults(self) -> None:
        """Reset parameters to their default values."""
        default_params = {
            "breeding": {
                "breeding_rate": 0.7,
                "kittens_per_litter": 4,
                "litters_per_year": 2,
                "female_ratio": 0.5,
                "kitten_survival_rate": 0.7,
                "adult_survival_rate": 0.8,
                "kitten_maturity_months": 6,
                "seasonal_breeding_amplitude": 0.3,
                "peak_breeding_month": 5
            },
            "environmental": {
                "water_availability": 0.8,
                "shelter_quality": 0.7,
                "urban_risk": 0.1,
                "disease_risk": 0.1,
                "natural_risk": 0.1,
                "territory_size": 1000,
                "density_impact_threshold": 1.2
            },
            "human_factors": {
                "caretaker_support": 1.0,
                "feeding_consistency": 0.8,
                "human_interference": 0.5,
                "monthly_abandonment": 0.1,
                "abandoned_sterilized_ratio": 0.2
            },
            "costs": {
                "sterilization_cost": 50
            }
        }
        self.params = default_params
        self.save_parameters()

# Create a default instance
default_manager = ParameterManager()
