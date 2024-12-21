"""Analysis script for territory size and density effects on cat population."""

import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from simulation import simulate_population

def run_density_tests():
    """Run a series of tests varying territory size and density impact parameters."""
    
    # Base configuration
    base_config = {
        "months": 24,
        "current_size": 50,  # Start with a moderate population
        "sterilized_count": 0,
        "monthly_sterilization": 5,
        "params": {
            "breeding_rate": 0.85,
            "kittens_per_litter": 4,
            "litters_per_year": 2.5,
            "kitten_survival_rate": 0.7,
            "adult_survival_rate": 0.85,
            "female_ratio": 0.5,
            "kitten_maturity_months": 6,
            "sterilization_cost": 50,
            "seasonal_breeding_amplitude": 0.3,
            "peak_breeding_month": 5,
            "water_availability": 0.8,
            "food_scaling_factor": 0.8,
            "urban_risk": 0.15,
            "disease_risk": 0.1,
            "natural_risk": 0.1,
            "caretaker_support": 1.0,
            "feeding_consistency": 0.8
        }
    }

    # Test scenarios
    scenarios = [
        {
            "name": "Small Territory High Density",
            "territory_size": 500,
            "density_impact_threshold": 0.8
        },
        {
            "name": "Small Territory Low Density",
            "territory_size": 500,
            "density_impact_threshold": 1.5
        },
        {
            "name": "Medium Territory High Density",
            "territory_size": 1000,
            "density_impact_threshold": 0.8
        },
        {
            "name": "Medium Territory Low Density",
            "territory_size": 1000,
            "density_impact_threshold": 1.5
        },
        {
            "name": "Large Territory High Density",
            "territory_size": 2000,
            "density_impact_threshold": 0.8
        },
        {
            "name": "Large Territory Low Density",
            "territory_size": 2000,
            "density_impact_threshold": 1.5
        },
        {
            "name": "Very Large Territory High Density",
            "territory_size": 5000,
            "density_impact_threshold": 0.8
        },
        {
            "name": "Very Large Territory Low Density",
            "territory_size": 5000,
            "density_impact_threshold": 1.5
        },
        {
            "name": "Extreme Territory High Density",
            "territory_size": 10000,
            "density_impact_threshold": 0.8
        },
        {
            "name": "Extreme Territory Low Density",
            "territory_size": 10000,
            "density_impact_threshold": 1.5
        }
    ]

    results = []
    
    # Run simulations
    for scenario in scenarios:
        print(f"\nRunning scenario: {scenario['name']}")
        
        # Create config for this scenario
        config = base_config.copy()
        config["params"] = base_config["params"].copy()
        config["params"]["territory_size"] = scenario["territory_size"]
        config["params"]["density_impact_threshold"] = scenario["density_impact_threshold"]
        
        # Run simulation
        result = simulate_population(
            current_size=config["current_size"],
            sterilized_count=config["sterilized_count"],
            monthly_sterilization=config["monthly_sterilization"],
            months=config["months"],
            params=config["params"]
        )
        
        if result:
            # Extract key metrics
            metrics = {
                "name": scenario["name"],
                "territory_size": scenario["territory_size"],
                "density_impact_threshold": scenario["density_impact_threshold"],
                "initial_density": config["current_size"] / scenario["territory_size"],
                "final_population": result["final_state"]["total"],
                "final_density": result["final_state"]["total"] / scenario["territory_size"],
                "total_deaths": result["deaths"]["total"],
                "disease_deaths": result["deaths"]["disease"],
                "natural_deaths": result["deaths"]["natural"],
                "population_growth": result["final_state"]["total"] - config["current_size"]
            }
            results.append(metrics)
            
            print(f"Final population: {metrics['final_population']}")
            print(f"Population growth: {metrics['population_growth']}")
            print(f"Final density: {metrics['final_density']:.2f} cats per unit area")

    return results

def plot_results(results):
    """Create visualizations of the test results."""
    df = pd.DataFrame(results)
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'density_analysis')
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Plot 1: Territory Size vs Final Population
    plt.figure(figsize=(12, 6))
    for threshold in df['density_impact_threshold'].unique():
        data = df[df['density_impact_threshold'] == threshold]
        plt.plot(data['territory_size'], data['final_population'], 
                marker='o', label=f'Density Threshold: {threshold}')
    
    plt.xlabel('Territory Size')
    plt.ylabel('Final Population')
    plt.title('Territory Size vs Final Population')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, f'territory_vs_population_{timestamp}.png'))
    plt.close()
    
    # Plot 2: Initial vs Final Density
    plt.figure(figsize=(12, 6))
    for threshold in df['density_impact_threshold'].unique():
        data = df[df['density_impact_threshold'] == threshold]
        plt.scatter(data['initial_density'], data['final_density'],
                   label=f'Density Threshold: {threshold}')
    
    plt.xlabel('Initial Density (cats per unit area)')
    plt.ylabel('Final Density (cats per unit area)')
    plt.title('Initial vs Final Population Density')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, f'density_comparison_{timestamp}.png'))
    plt.close()
    
    # Plot 3: Death Distribution
    plt.figure(figsize=(12, 6))
    df_plot = df.set_index('name')
    df_plot[['disease_deaths', 'natural_deaths']].plot(kind='bar', stacked=True)
    plt.title('Death Distribution by Scenario')
    plt.xlabel('Scenario')
    plt.ylabel('Number of Deaths')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'death_distribution_{timestamp}.png'))
    plt.close()
    
    # Save results to CSV
    df.to_csv(os.path.join(output_dir, f'density_analysis_{timestamp}.csv'), index=False)
    
    return os.path.join(output_dir, f'density_analysis_{timestamp}.csv')

if __name__ == "__main__":
    print("Running density and territory size analysis...")
    results = run_density_tests()
    if results:
        output_file = plot_results(results)
        print(f"\nAnalysis complete. Results saved to: {output_file}")
        print("\nKey findings:")
        df = pd.DataFrame(results)
        print("\nAverage metrics by territory size:")
        print(df.groupby('territory_size')[['final_population', 'final_density', 'total_deaths']].mean())
        print("\nAverage metrics by density threshold:")
        print(df.groupby('density_impact_threshold')[['final_population', 'final_density', 'total_deaths']].mean())
