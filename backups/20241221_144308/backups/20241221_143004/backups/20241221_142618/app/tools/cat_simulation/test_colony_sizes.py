"""Test script to simulate different colony environments."""
import json
from datetime import datetime
import pandas as pd

def run_colony_simulation(initial_size, params, months=24):
    """Run simulation for a specific colony size."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate initial population distribution (60% reproductive, 40% kittens)
    reproductive_count = int(initial_size * 0.6)
    kitten_count = initial_size - reproductive_count
    
    # Create data for CSV
    data = {
        'timestamp': timestamp,
        'current_size': initial_size,
        'sterilized_count': 0,
        'monthly_sterilization': 0,
        'months': months,
        'sterilization_cost': 50.0,
        'use_monte_carlo': False,
        'final_population': None,  # Will be filled by simulation
        'final_sterilized': 0,
        'total_sterilizations': 0,
        'total_cost': 0.0,
        'population_growth': None,  # Will be filled by simulation
        'monthly_populations': None,  # Will be filled by simulation
        'monthly_sterilized': ','.join(['0'] * (months + 1)),
        'params': json.dumps(params)
    }
    
    # Write to CSV
    df = pd.DataFrame([data])
    df.to_csv('/Users/jordanlerma/Documents/GitHub/HawaiiCats/app/static/img/calculations.csv', 
              mode='a', header=False, index=False)

def main():
    # Base parameters
    base_params = {
        'breeding_rate': 0.85,
        'kittens_per_litter': 4.0,
        'litters_per_year': 2.5,
        'kitten_survival_rate': 0.75,
        'female_ratio': 0.5,
        'adult_survival_rate': 0.9,
        'kitten_maturity_months': 6.0,
        'seasonal_breeding_amplitude': 0.1,
        'peak_breeding_month': 5,
        'base_food_capacity': 0.9,
        'food_scaling_factor': 0.8,
        'water_availability': 0.8,
        'shelter_quality': 0.8,
        'urban_risk': 0.15,
        'disease_risk': 0.1,
        'natural_risk': 0.1,
        'caretaker_support': 1.0,
        'feeding_consistency': 0.8,
        'territory_size': 1000.0,
        'density_impact_threshold': 1.2
    }
    
    # Test different initial colony sizes
    colony_sizes = [10, 25, 50, 75, 100, 150, 200]
    
    # Different simulation lengths
    simulation_lengths = [12, 24, 36, 48, 60]  # 1-5 years
    
    # Environment variations
    environments = [
        {
            'name': 'Urban High-Resource',
            'params': {
                **base_params,
                'urban_risk': 0.2,
                'food_scaling_factor': 0.9,
                'water_availability': 0.9,
                'caretaker_support': 1.2,
                'territory_size': 800.0
            }
        },
        {
            'name': 'Urban Low-Resource',
            'params': {
                **base_params,
                'urban_risk': 0.2,
                'food_scaling_factor': 0.6,
                'water_availability': 0.6,
                'caretaker_support': 0.8,
                'territory_size': 800.0
            }
        },
        {
            'name': 'Rural High-Resource',
            'params': {
                **base_params,
                'urban_risk': 0.1,
                'food_scaling_factor': 0.8,
                'water_availability': 0.9,
                'caretaker_support': 1.0,
                'territory_size': 2000.0
            }
        },
        {
            'name': 'Rural Low-Resource',
            'params': {
                **base_params,
                'urban_risk': 0.1,
                'food_scaling_factor': 0.5,
                'water_availability': 0.7,
                'caretaker_support': 0.6,
                'territory_size': 2000.0
            }
        },
        {
            'name': 'Extreme Growth',
            'params': {
                **base_params,
                'breeding_rate': 0.95,
                'kittens_per_litter': 5.0,
                'litters_per_year': 3.0,
                'kitten_survival_rate': 0.85,
                'adult_survival_rate': 0.95,
                'food_scaling_factor': 1.0,
                'water_availability': 1.0,
                'caretaker_support': 1.5,
                'territory_size': 3000.0
            }
        },
        {
            'name': 'Resource Limited',
            'params': {
                **base_params,
                'food_scaling_factor': 0.4,
                'water_availability': 0.5,
                'territory_size': 500.0,
                'density_impact_threshold': 0.8
            }
        },
        {
            'name': 'High Risk Environment',
            'params': {
                **base_params,
                'urban_risk': 0.3,
                'disease_risk': 0.2,
                'natural_risk': 0.2,
                'kitten_survival_rate': 0.6,
                'adult_survival_rate': 0.8
            }
        }
    ]
    
    # Run simulations for each environment, colony size, and simulation length
    for env in environments:
        print(f"\nTesting {env['name']} environment...")
        for size in colony_sizes:
            for months in simulation_lengths:
                print(f"  Running simulation: {size} cats, {months} months")
                run_colony_simulation(size, env['params'], months)

if __name__ == '__main__':
    main()
