"""Comprehensive test suite for cat population simulation."""
import unittest
from datetime import datetime
import numpy as np
import json
import os
import sys
from typing import Dict, List, Tuple
from statistics import mean, stdev
from simulation import simulatePopulation

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cat_simulation.constants import DEFAULT_PARAMS
from test_parameter_impacts import TestEnvironmentPresets

class TestCatSimulation(TestEnvironmentPresets):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize base parameters
        self.base_params = {
            'baseFoodCapacity': 0.5,
            'waterAvailability': 0.6,
            'shelterQuality': 0.5,
            'caretakerSupport': 0.5,
            'feedingConsistency': 0.6,
            'territorySize': 3500,
            'densityThreshold': 1.5,
            'urbanization_impact': 0.3,
            'disease_transmission_rate': 0.2,
            'environmental_stress': 0.3
        }
        
        # Set number of iterations for tests
        self.num_iterations = 100
        
        # Set initial population and simulation months
        self.initial_population = 100
        self.simulation_months = 12

        # Initialize environment presets
        self.environment_presets = {
            'urban': {
                'params': {
                    'baseFoodCapacity': 1.0,
                    'waterAvailability': 1.0,
                    'shelterQuality': 0.9,
                    'caretakerSupport': 0.9,
                    'feedingConsistency': 1.0,
                    'territorySize': 2000,
                    'densityThreshold': 3.0,
                    'urbanization_impact': 0.4,
                    'disease_transmission_rate': 0.3,
                    'environmental_stress': 0.4,
                    'resourceMultiplier': 2.0,
                    'carryingCapacityBase': 300
                },
                'expected': {
                    'resource_range': (0.6, 0.9),
                    'carrying_capacity_range': (250, 350),
                    'mortality_types': {
                        'urban': (0.3, 0.5),
                        'disease': (0.2, 0.4),
                        'natural': (0.2, 0.4)
                    }
                }
            },
            'suburban': {
                'params': {
                    'baseFoodCapacity': 0.8,
                    'waterAvailability': 0.8,
                    'shelterQuality': 0.7,
                    'caretakerSupport': 0.7,
                    'feedingConsistency': 0.8,
                    'territorySize': 4000,
                    'densityThreshold': 2.0,
                    'urbanization_impact': 0.3,
                    'disease_transmission_rate': 0.2,
                    'environmental_stress': 0.3,
                    'resourceMultiplier': 1.5,
                    'carryingCapacityBase': 200
                },
                'expected': {
                    'resource_range': (0.4, 0.7),
                    'carrying_capacity_range': (150, 250),
                    'mortality_types': {
                        'urban': (0.2, 0.4),
                        'disease': (0.15, 0.35),
                        'natural': (0.3, 0.5)
                    }
                }
            },
            'rural': {
                'params': {
                    'baseFoodCapacity': 0.6,
                    'waterAvailability': 0.6,
                    'shelterQuality': 0.5,
                    'caretakerSupport': 0.5,
                    'feedingConsistency': 0.6,
                    'territorySize': 8000,
                    'densityThreshold': 1.0,
                    'urbanization_impact': 0.2,
                    'disease_transmission_rate': 0.15,
                    'environmental_stress': 0.25,
                    'resourceMultiplier': 1.0,
                    'carryingCapacityBase': 100
                },
                'expected': {
                    'resource_range': (0.2, 0.5),
                    'carrying_capacity_range': (50, 150),
                    'mortality_types': {
                        'urban': (0.1, 0.3),
                        'disease': (0.1, 0.3),
                        'natural': (0.4, 0.6)
                    }
                }
            }
        }
        
        # Define parameter ranges
        self.param_ranges = {
            # Basic Parameters
            'monthly_abandonment': (0, 5),  # Reduced from (0, 50)
            'monthly_sterilization': (0, 10),  # Reduced from (0, 100)
            
            # Mortality Risk Factors
            'urbanization_impact': (0.0, 0.1),  # Reduced from (0.0, 0.5)
            'disease_transmission_rate': (0.0, 0.1),
            'natural_risk': (0.0, 0.1),
            'density_mortality_factor': (0.0, 0.5),  # Reduced from (0.0, 2.0)
            'mortality_threshold': (20, 50),  # Adjusted range
            
            # Environmental Factors
            'water_availability': (0.5, 1.0),  # Increased minimum
            'shelter_quality': (0.5, 1.0),
            'caretaker_support': (0.2, 1.0),  # Increased minimum
            'feeding_consistency': (0.5, 1.0),
            'territory_size': (500, 5000),  # Adjusted range
            'base_food_capacity': (0.5, 1.0),  # Increased minimum
            'food_scaling_factor': (0.5, 1.5),
            
            # Survival Rates
            'kitten_survival_rate': (0.7, 0.9),  # Increased minimum
            'adult_survival_rate': (0.8, 0.95),  # Increased minimum
            'survival_density_factor': (0.0, 0.3),  # Reduced from (0.0, 1.0)
            
            # Breeding Parameters
            'breeding_rate': (0.85, 0.95),  # Higher range for tropical climate
            'kittens_per_litter': (4, 6),  # Increased range for tropical climate
            'litters_per_year': (2.5, 3.0),  # More frequent litters
            'seasonal_breeding_amplitude': (0.05, 0.15),  # Reduced seasonality
            'peak_breeding_month': (1, 12)  # Less important in tropical climate
        }
        
        # Create results directory if it doesn't exist
        self.results_dir = os.path.join(os.path.dirname(__file__), 'test_results')
        os.makedirs(self.results_dir, exist_ok=True)

    def detect_cycles(self, monthly_data: List[float]) -> bool:
        """Detect if population shows cyclical behavior."""
        if len(monthly_data) < 24:  # Need at least 2 years of data
            return False
            
        # Calculate monthly growth rates
        growth_rates = [
            (monthly_data[i] - monthly_data[i-1]) / monthly_data[i-1] if monthly_data[i-1] > 0 else 0
            for i in range(1, len(monthly_data))
        ]
            
        # Calculate moving average to smooth out noise
        window = 3  # Smaller window for growth rates
        ma = np.convolve(growth_rates, np.ones(window)/window, mode='valid')
        
        # Find peaks and troughs in growth rate
        peaks = []
        troughs = []
        for i in range(1, len(ma)-1):
            if ma[i-1] < ma[i] and ma[i] > ma[i+1]:
                peaks.append(i)
            elif ma[i-1] > ma[i] and ma[i] < ma[i+1]:
                troughs.append(i)
                
        # Need at least 2 peaks and 1 trough, or 2 troughs and 1 peak
        if len(peaks) >= 2 and len(troughs) >= 1 or len(troughs) >= 2 and len(peaks) >= 1:
            # Check peak-to-peak or trough-to-trough distances
            if len(peaks) >= 2:
                peak_distances = [peaks[i+1] - peaks[i] for i in range(len(peaks)-1)]
                avg_distance = mean(peak_distances)
                return 4 <= avg_distance <= 12  # Growth rate cycles are shorter
            else:
                trough_distances = [troughs[i+1] - troughs[i] for i in range(len(troughs)-1)]
                avg_distance = mean(trough_distances)
                return 4 <= avg_distance <= 12
            
        return False

    def run_simulation_with_params(self, params, runs=1):
        """Run simulation with given parameters multiple times."""
        results = []
        for _ in range(runs):
            result = simulatePopulation(
                params,
                self.initial_population,
                self.simulation_months
            )
            results.append(result)
        return results

    def calculate_statistics(self, results: List[Dict]) -> Dict:
        """Calculate mean and standard deviation for key metrics."""
        metrics = [
            'finalPopulation', 'totalDeaths', 'kittenDeaths', 'adultDeaths',
            'naturalDeaths', 'urbanDeaths', 'diseaseDeaths'
        ]
        
        stats = {}
        for metric in metrics:
            if metric in results[0]:  # Only process metrics that exist
                values = [r[metric] for r in results]
                stats[f'{metric}_mean'] = mean(values)
                if len(values) > 1:
                    stats[f'{metric}_stdev'] = stdev(values)
        
        # Process monthly arrays
        if 'monthlyData' in results[0]:
            monthly_values = list(zip(*[[m['total'] for m in r['monthlyData']] for r in results]))
            stats['monthly_mean'] = [mean(month) for month in monthly_values]
            if len(results) > 1:
                stats['monthly_stdev'] = [stdev(month) for month in monthly_values]
            
            # Check for cyclical behavior
            stats['is_cyclical'] = self.detect_cycles(stats['monthly_mean'])
            
            # Calculate growth rate volatility
            monthly_growth = np.diff(stats['monthly_mean']) / stats['monthly_mean'][:-1]
            stats['growth_volatility'] = np.std(monthly_growth)
            
        return stats

    def assertGreaterWithTolerance(self, a, b, msg=None):
        """Assert that a is greater than b, with tolerance for random variation."""
        self.assertGreater(a, b * (1 - self.tolerance), msg)

    def assertLessWithTolerance(self, a, b, msg=None):
        """Assert that a is less than b, with tolerance for random variation."""
        self.assertLess(a, b * (1 + self.tolerance), msg)

    def log_results(self, scenario_name: str, params: Dict, stats: Dict):
        """Log test results to a JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{scenario_name}_{timestamp}.json'
        filepath = os.path.join(self.results_dir, filename)
        
        data = {
            'scenario': scenario_name,
            'parameters': params,
            'statistics': stats,
            'test_config': {
                'num_runs': self.num_iterations,
                'months': self.simulation_months,
                'initial_size': self.initial_population
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def calculateCarryingCapacity(self, territory_size, density_threshold, resource_factor):
        """Calculate carrying capacity based on territory size and resources."""
        base_capacity = territory_size * density_threshold
        return int(base_capacity * resource_factor)

    def calculateResourceAvailability(self, food_capacity, water_availability, shelter_quality, human_care, feeding_stations):
        """Calculate overall resource availability factor."""
        # Base resources from natural environment
        natural_resources = (food_capacity + water_availability + shelter_quality) / 3.0
        
        # Human support factor
        human_support = (human_care + feeding_stations) / 2.0
        
        # Combine natural and human resources with higher weight on natural
        total_resources = (0.7 * natural_resources + 0.3 * human_support)
        
        # Ensure result is between 0 and 1
        return max(0.0, min(1.0, total_resources))

    def test_basic_simulation(self):
        """Test basic simulation functionality."""
        # Test with default parameters
        results = self.run_simulation_with_params(DEFAULT_PARAMS)
        self.assertIsNotNone(results[0])
        self.assertGreater(results[0]['finalPopulation'], 0)
        
        # Test with minimal population
        result = simulatePopulation(DEFAULT_PARAMS, 1, 12)
        self.assertGreaterEqual(result['finalPopulation'], 0)

    def test_sterilization_impact(self):
        """Test impact of sterilization on population."""
        # Test without sterilization
        no_steril_params = DEFAULT_PARAMS.copy()
        no_steril_params.update({
            'breeding_rate': 0.9,
            'seasonal_breeding_amplitude': 0.5,  # Strong seasonal effect
            'kittens_per_litter': 4.0,
            'litters_per_year': 2.5,
            'mortality_rate': 0.1,
            'carrying_capacity': 1000,
            'sterilization_rate': 0.0,
            'monthly_sterilization': 0,
            'disease_transmission_rate': 0.1,  # Keep other risks low
            'urbanization_impact': 0.1,
            'environmental_stress': 0.1
        })
        
        # Run simulation without sterilization
        initial_pop = 100
        no_steril_result = simulatePopulation(no_steril_params, initial_pop, 24)
        no_steril_pop = no_steril_result['finalPopulation']
        
        # Test with very high sterilization
        steril_params = no_steril_params.copy()
        steril_params.update({
            'sterilization_rate': 0.8,  # Very high sterilization rate
            'monthly_sterilization': 20  # Aggressive sterilization program
        })
        
        # Run simulation with sterilization, starting with some sterilized cats
        initial_sterilized = int(initial_pop * 0.5)  # Start with 50% sterilized
        steril_result = simulatePopulation(
            steril_params,
            initial_pop,
            24,
            sterilizedCount=initial_sterilized
        )
        steril_pop = steril_result['finalPopulation']
        
        # Sterilized population should be smaller
        self.assertLess(steril_pop, no_steril_pop,
                       "Sterilization should reduce population growth")
        
        # Check population growth rates
        no_steril_growth = (no_steril_pop - initial_pop) / 24
        steril_growth = (steril_pop - initial_pop) / 24
        
        self.assertGreater(no_steril_growth, steril_growth,
                          "Non-sterilized population should grow faster")

    def test_extreme_scenarios(self):
        """Test maximum and minimum parameter scenarios."""
        scenarios = {
            'all_minimum': {k: v[0] for k, v in self.param_ranges.items()},
            'all_maximum': {k: v[1] for k, v in self.param_ranges.items()}
        }
        
        for scenario_name, params in scenarios.items():
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(scenario_name, params, stats)

    def test_parameter_sensitivity(self):
        """Test sensitivity of each parameter individually."""
        base_params = DEFAULT_PARAMS.copy()
        
        for param_name, (min_val, max_val) in self.param_ranges.items():
            # Test minimum value
            test_params = base_params.copy()
            test_params[param_name] = min_val
            results = self.run_simulation_with_params(test_params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'{param_name}_minimum', test_params, stats)
            
            # Test maximum value
            test_params = base_params.copy()
            test_params[param_name] = max_val
            results = self.run_simulation_with_params(test_params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'{param_name}_maximum', test_params, stats)
            
            # Test middle value
            test_params = base_params.copy()
            test_params[param_name] = (min_val + max_val) / 2
            results = self.run_simulation_with_params(test_params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'{param_name}_middle', test_params, stats)

    def test_mortality_risk_factors(self):
        """Test the impact of mortality risk factors."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'initial_size': 20,  # Start with larger population
            'months': 60,
            'sterilization_rate': 0
        })
        
        # Test urban risk
        for risk in [0.0, 0.2, 0.4]:  # Increased risk levels
            params = base_params.copy()
            params['urbanization_impact'] = risk
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            
            # Verify urban risk causes deaths
            if risk > 0:
                self.assertGreaterWithTolerance(stats['urbanDeaths_mean'], 0,
                                 f"Urban risk {risk} should cause urban deaths")
        
        # Test disease risk
        for risk in [0.0, 0.2, 0.4]:  # Increased risk levels
            params = base_params.copy()
            params['disease_transmission_rate'] = risk
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            
            # Verify disease risk causes deaths
            if risk > 0:
                self.assertGreaterWithTolerance(stats['diseaseDeaths_mean'], 0,
                                 f"Disease risk {risk} should cause disease deaths")
        
        # Test density mortality
        for factor in [0.0, 0.25, 0.5]:
            params = base_params.copy()
            params['density_mortality_factor'] = factor
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            
            # Verify density mortality causes deaths in dense populations
            if factor > 0:
                self.assertGreaterWithTolerance(stats['totalDeaths_mean'], 0,
                                 f"Density factor {factor} should increase deaths")

    def test_environmental_factors(self):
        """Test the impact of environmental factors."""
        base_params = DEFAULT_PARAMS.copy()
        
        # Test water availability
        for level in [0.5, 0.75, 1.0]:
            params = base_params.copy()
            params['water_availability'] = level
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'water_availability_{level}', params, stats)
        
        # Test shelter quality
        for quality in [0.5, 0.75, 1.0]:
            params = base_params.copy()
            params['shelter_quality'] = quality
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'shelter_quality_{quality}', params, stats)
        
        # Test caretaker support
        for support in [0.2, 0.5, 1.0]:
            params = base_params.copy()
            params['caretaker_support'] = support
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'caretaker_support_{support}', params, stats)
        
        # Test feeding consistency
        for consistency in [0.5, 0.75, 1.0]:
            params = base_params.copy()
            params['feeding_consistency'] = consistency
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'feeding_consistency_{consistency}', params, stats)

    def test_survival_rates(self):
        """Test the impact of survival rates."""
        base_params = DEFAULT_PARAMS.copy()
        
        # Test kitten survival rate
        for rate in [0.7, 0.8, 0.9]:
            params = base_params.copy()
            params['kitten_survival_rate'] = rate
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'kitten_survival_{rate}', params, stats)
            
            # Verify higher survival rates lead to fewer kitten deaths
            if rate > 0.7:
                self.assertLessWithTolerance(stats['kittenDeaths_mean'], stats['totalDeaths_mean'],
                              f"Kitten survival rate {rate} should reduce kitten deaths")
        
        # Test adult survival rate
        for rate in [0.8, 0.9, 0.95]:
            params = base_params.copy()
            params['adult_survival_rate'] = rate
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'adult_survival_{rate}', params, stats)
            
            # Verify higher survival rates lead to fewer adult deaths
            if rate > 0.8:
                self.assertLessWithTolerance(stats['adultDeaths_mean'], stats['totalDeaths_mean'],
                              f"Adult survival rate {rate} should reduce adult deaths")

    def test_breeding_parameters(self):
        """Test the impact of breeding parameters."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,  # Longer time to see breeding effects
            'kitten_survival_rate': 0.8,  # Higher survival for clear breeding impact
            'adult_survival_rate': 0.9,
            'initial_size': 50  # Start with a smaller population
        })
        
        previous_final_pop = 0
        # Test breeding rate
        for rate in [0.3, 0.5, 0.8]:
            params = base_params.copy()
            params['breeding_rate'] = rate
            params['sterilization_rate'] = 0  # No sterilization to see breeding effects
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'breeding_rate_{rate}', params, stats)
            
            # Verify higher breeding rates lead to larger populations
            if previous_final_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_final_pop,
                                 f"Breeding rate {rate} should lead to larger population than previous rate")
            previous_final_pop = stats['finalPopulation_mean']
        
        # Test kittens per litter
        for kittens in [2.0, 4.0, 6.0]:
            params = base_params.copy()
            params['kittens_per_litter'] = kittens
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'kittens_per_litter_{kittens}', params, stats)
        
        # Test litters per year
        for litters in [1.0, 2.0, 3.0]:
            params = base_params.copy()
            params['litters_per_year'] = litters
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'litters_per_year_{litters}', params, stats)
        
        # Test seasonal breeding
        for amplitude in [0.1, 0.3, 0.5]:
            params = base_params.copy()
            params['seasonal_breeding_amplitude'] = amplitude
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'seasonal_amplitude_{amplitude}', params, stats)
            
            # Verify seasonal breeding creates population fluctuations
            if amplitude > 0 and 'monthly_mean' in stats:
                monthly_values = stats['monthly_mean']
                self.assertGreaterWithTolerance(max(monthly_values) - min(monthly_values), 0,
                                 f"Seasonal amplitude {amplitude} should cause population fluctuations")

    def test_long_term_stability(self):
        """Test population stability over a long time period (5 years)."""
        params = DEFAULT_PARAMS.copy()
        params.update({
            'breeding_rate': 0.8,
            'mortality_rate': 0.2,
            'carrying_capacity': 100,
            'food_availability': 0.5,  # Limited food
            'shelter_quality': 0.5,  # Limited shelter
            'disease_transmission_rate': 0.2,  # Moderate disease pressure
            'natural_risk': 0.1  # Some natural risks
        })
        
        result = simulatePopulation(
            params,
            10,
            60
        )
        
        stats = self.calculate_statistics([result])
        
        # Population should stabilize around carrying capacity
        self.assertLessWithTolerance(result['finalPopulation'], params['carrying_capacity'],
                                   "Population shouldn't explode")
        
        # Check for stability in later months
        late_pops = [month['total'] for month in result['monthlyData'][-12:]]  # Last year
        pop_variance = stdev(late_pops) / mean(late_pops)  # Coefficient of variation
        self.assertLess(pop_variance, 0.2, "Population should be relatively stable")

    def test_seasonal_effects(self):
        """Test seasonal breeding patterns."""
        # Base parameters with moderate territory and resources
        params = {
            'territorySize': 1000,
            'densityThreshold': 0.8,
            'baseFoodCapacity': 0.7,
            'waterAvailability': 0.7,
            'shelterQuality': 0.7,
            'seasonalBreedingAmplitude': 0.8,  # Stronger seasonal variation
            'peakBreedingMonth': 4  # Peak in spring
        }
        
        # Run simulations for different seasons
        spring_result = simulatePopulation(params, 100, 12)  # Run for a full year
        params['peakBreedingMonth'] = 1  # Set peak to winter
        winter_result = simulatePopulation(params, 100, 12)  # Run for a full year
        
        # Calculate growth rates for spring months (March-May) and winter months (Dec-Feb)
        spring_growth = []
        winter_growth = []
        
        for i in range(1, len(spring_result['monthlyData'])):
            month = i % 12
            growth = (spring_result['monthlyData'][i]['total'] - spring_result['monthlyData'][i-1]['total'])
            if 2 <= month <= 4:  # March-May
                spring_growth.append(growth)
            elif month == 11 or month <= 1:  # Dec-Feb
                winter_growth.append(growth)
                
        # Spring should show higher average population growth
        spring_avg = sum(spring_growth) / len(spring_growth) if spring_growth else 0
        winter_avg = sum(winter_growth) / len(winter_growth) if winter_growth else 0
        self.assertGreater(spring_avg, winter_avg,
                          "Spring should show higher population growth than winter")

    def test_tropical_breeding_rate(self):
        """Test that breeding occurs year-round with minimal seasonal variation."""
        # Parameters for tropical environment
        params = {
            'territorySize': 2000,  # Large territory
            'densityThreshold': 0.8,
            'baseFoodCapacity': 0.9,  # Good resources
            'waterAvailability': 0.9,
            'shelterQuality': 0.8,
            'seasonalBreedingAmplitude': 0.2,  # Low seasonal variation
            'peakBreedingMonth': 6  # Mid-year peak
        }
        
        # Run simulation for 24 months to see seasonal patterns
        result = simulatePopulation(params, 100, 24)
        monthly_pops = result['monthlyData']
        
        # Calculate monthly growth rates
        growth_rates = []
        for i in range(1, len(monthly_pops)):
            if monthly_pops[i-1]['total'] > 0:
                growth_rate = (monthly_pops[i]['total'] - monthly_pops[i-1]['total']) / monthly_pops[i-1]['total']
                growth_rates.append(growth_rate)
        
        # Calculate coefficient of variation
        if growth_rates:
            mean_growth = sum(growth_rates) / len(growth_rates)
            if mean_growth != 0:
                variance = sum((x - mean_growth) ** 2 for x in growth_rates) / len(growth_rates)
                cv = (variance ** 0.5) / abs(mean_growth)
            else:
                cv = float('inf')
        else:
            cv = float('inf')
        
        # Verify minimal seasonal variation
        self.assertLess(cv, 1.0, "Breeding should show minimal seasonal variation")
        
        # Verify positive growth overall
        self.assertGreater(result['finalPopulation'], 100,
                          "Population should grow in tropical conditions")

    def test_tropical_population_growth(self):
        """Test population growth characteristics in tropical climate."""
        # Parameters for optimal tropical growth
        params = {
            'territorySize': 2000,
            'densityThreshold': 0.8,
            'baseFoodCapacity': 0.9,
            'waterAvailability': 0.9,
            'shelterQuality': 0.8,
            'seasonalBreedingAmplitude': 0.2,
            'peakBreedingMonth': 6,
            'breedingRate': 0.8,
            'kittensPerLitter': 4,
            'littersPerYear': 2.5
        }
        
        # Run simulation
        result = simulatePopulation(params, 50, 24)
        monthly_pops = result['monthlyData']
        
        # Calculate growth rate over the simulation
        if len(monthly_pops) > 1:
            total_growth = (monthly_pops[-1]['total'] - monthly_pops[0]['total']) / monthly_pops[0]['total']
            months = len(monthly_pops) - 1
            avg_monthly_growth = total_growth / months
            
            # Verify reasonable growth rate
            self.assertGreater(avg_monthly_growth, 0.05,
                             "Should have moderate positive growth")
            self.assertGreater(result['finalPopulation'], 75,
                             "Population should increase significantly")

    def test_resource_competition(self):
        """Test that population is limited by resources rather than seasonal factors."""
        # Base parameters with limited resources
        base_params = {
            'baseFoodCapacity': 0.4,
            'waterAvailability': 0.4,
            'shelterQuality': 0.4,
            'caretakerSupport': 0.3,
            'feedingConsistency': 0.3,
            'territorySize': 1000.0,
            'densityThreshold': 0.8
        }
        
        # Parameters with abundant resources
        high_params = base_params.copy()
        high_params.update({
            'baseFoodCapacity': 0.9,
            'waterAvailability': 0.9,
            'shelterQuality': 0.9,
            'caretakerSupport': 0.8,
            'feedingConsistency': 0.8
        })
        
        # Run simulation
        base_result = simulatePopulation(base_params, 100, 24)
        high_result = simulatePopulation(high_params, 100, 24)
        
        # Population should be significantly higher with better resources
        # Adjust threshold for stricter carrying capacity
        self.assertGreater(high_result['finalPopulation'], base_result['finalPopulation'] * 1.3,
                          "Population should be significantly higher with better resources")
        
        # Check mortality rates instead of specific death types
        self.assertGreater(base_result['totalDeaths'] / base_result['finalPopulation'],
                          high_result['totalDeaths'] / high_result['finalPopulation'],
                          "Should see higher mortality rate with limited resources")

    def test_comprehensive_carrying_capacity(self):
        """Test how different factors affect carrying capacity and population limits."""
        # Base scenario with good conditions
        good_params = {
            'territorySize': 2000.0,
            'densityThreshold': 0.8,
            'baseFoodCapacity': 0.9,
            'waterAvailability': 0.9,
            'shelterQuality': 0.8,
            'caretakerSupport': 0.7,
            'feedingConsistency': 0.8
        }
        
        # Run base scenario
        good_result = simulatePopulation(good_params, 200, 12)
        good_pop = good_result['finalPopulation']
        
        # Test smaller territory
        small_territory_params = good_params.copy()
        small_territory_params['territorySize'] = 1000.0
        small_territory_result = simulatePopulation(small_territory_params, 200, 12)
        
        # Test poor resources
        poor_resources_params = good_params.copy()
        poor_resources_params.update({
            'baseFoodCapacity': 0.4,
            'waterAvailability': 0.4,
            'shelterQuality': 0.3,
            'caretakerSupport': 0.2,
            'feedingConsistency': 0.3
        })
        poor_resources_result = simulatePopulation(poor_resources_params, 200, 12)
        
        # Test high density
        high_density_params = good_params.copy()
        high_density_params['densityThreshold'] = 1.5
        high_density_result = simulatePopulation(high_density_params, 200, 12)
        
        # Assertions with updated expectations for stricter carrying capacity
        self.assertLess(small_territory_result['finalPopulation'], good_pop * 0.7,
                       "Smaller territory should support fewer cats")
        self.assertLess(poor_resources_result['finalPopulation'], good_pop * 0.6,
                       "Poor resources should significantly limit population")
        self.assertGreater(high_density_result['finalPopulation'], good_pop,
                          "Higher density threshold should allow larger population")

    def test_resource_competition(self):
        """Test that population is limited by resources rather than seasonal factors."""
        # Base parameters with limited resources
        base_params = {
            'baseFoodCapacity': 0.4,
            'waterAvailability': 0.4,
            'shelterQuality': 0.4,
            'caretakerSupport': 0.3,
            'feedingConsistency': 0.3,
            'territorySize': 1000.0,
            'densityThreshold': 0.8
        }
        
        # Parameters with abundant resources
        high_params = base_params.copy()
        high_params.update({
            'baseFoodCapacity': 0.9,
            'waterAvailability': 0.9,
            'shelterQuality': 0.9,
            'caretakerSupport': 0.8,
            'feedingConsistency': 0.8
        })
        
        # Run simulation
        base_result = simulatePopulation(base_params, 100, 24)
        high_result = simulatePopulation(high_params, 100, 24)
        
        # Population should be significantly higher with better resources
        # Adjust threshold for stricter carrying capacity
        self.assertGreater(high_result['finalPopulation'], base_result['finalPopulation'] * 1.3,
                          "Population should be significantly higher with better resources")
        
        # Check mortality rates instead of specific death types
        self.assertGreater(base_result['totalDeaths'] / base_result['finalPopulation'],
                          high_result['totalDeaths'] / high_result['finalPopulation'],
                          "Should see higher mortality rate with limited resources")

    def test_abandonment_impact(self):
        """Test the impact of different abandonment rates on population dynamics."""
        previous_final_pop = 0
        for rate in [0, 2, 5, 10]:  # Increased abandonment rates
            params = DEFAULT_PARAMS.copy()
            params['monthly_abandonment'] = rate
            
            results = self.run_simulation_with_params(params)
            stats = self.calculate_statistics(results)
            self.log_results(f'monthly_abandonment_{rate}', params, stats)
            
            # Verify that higher abandonment rates lead to larger populations
            if previous_final_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_final_pop,
                                 f"Population with abandonment rate {rate} should be higher than previous rate")
            previous_final_pop = stats['finalPopulation_mean']

    def test_monthly_abandonment(self):
        """Test that monthly abandonment increases population."""
        params = DEFAULT_PARAMS.copy()
        initial_size = 10
        months = 12
        
        # Run simulation without abandonment
        result_no_abandonment = simulatePopulation(
            params=params,
            currentSize=initial_size,
            months=months,
            monthlyAbandonment=0
        )
        
        # Run simulation with abandonment
        result_with_abandonment = simulatePopulation(
            params=params,
            currentSize=initial_size,
            months=months,
            monthlyAbandonment=5  # 5 cats abandoned per month
        )
        
        # The population with abandonment should be higher
        expected_min_difference = 5 * months  # At minimum, should include all abandoned cats
        actual_difference = (result_with_abandonment['finalPopulation'] - 
                           result_no_abandonment['finalPopulation'])
        
        self.assertGreater(
            actual_difference,
            expected_min_difference * 0.8,  # Allow for some mortality of abandoned cats
            f"Monthly abandonment of 5 cats should increase final population by at least {expected_min_difference * 0.8} cats"
        )

    def test_monthly_sterilization(self):
        """Test the impact of monthly sterilization parameter."""
        previous_pop = 0
        for rate in [0, 5, 10, 20]:  # Increased sterilization rates
            params = DEFAULT_PARAMS.copy()
            params['monthly_sterilization'] = rate
            
            results = self.run_simulation_with_params(params)
            stats = self.calculate_statistics(results)
            self.log_results(f'monthly_sterilization_{rate}', params, stats)
            
            if rate > 0:
                self.assertLessWithTolerance(stats['finalPopulation_mean'], previous_pop,
                              f"Higher sterilization rate {rate} should lead to smaller population")
            previous_pop = stats['finalPopulation_mean']

    def test_urban_risk(self):
        """Test the impact of urban risk parameter."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 12,
            'initial_size': 100,
            'sterilization_rate': 0
        })
        
        risk_levels = [0.0, 0.05, 0.1]
        previous_deaths = 0
        
        for risk in risk_levels:
            params = base_params.copy()
            params['urbanization_impact'] = risk  # Changed from 'urban_risk'
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'urban_risk_{risk}', params, stats)
            
            if risk > 0:
                self.assertGreaterWithTolerance(stats['urbanDeaths_mean'], previous_deaths,
                                 f"Higher urban risk {risk} should lead to more urban deaths")
            previous_deaths = stats['urbanDeaths_mean']

    def test_disease_risk(self):
        """Test the impact of disease risk parameter."""
        # Base scenario
        base_params = {
            'disease_transmission_rate': 0.2,
            'territory_size': 1000,
            'base_food_capacity': 0.8,
            'water_availability': 0.8
        }
        base_result = simulatePopulation(base_params, 200, 12)
        base_deaths = base_result['diseaseDeaths']
        
        # High disease risk scenario
        high_risk_params = base_params.copy()
        high_risk_params['disease_transmission_rate'] = 0.8
        high_risk_result = simulatePopulation(high_risk_params, 200, 12)
        
        # Compare relative death rates rather than absolute numbers
        base_death_rate = base_deaths / base_result['finalPopulation'] if base_result['finalPopulation'] > 0 else 0
        high_death_rate = high_risk_result['diseaseDeaths'] / high_risk_result['finalPopulation'] if high_risk_result['finalPopulation'] > 0 else 0
        
        self.assertGreater(high_death_rate, base_death_rate,
                          "Higher disease risk should lead to higher disease death rate")

    def test_natural_risk(self):
        """Test the impact of natural risk parameter."""
        # Base scenario
        base_params = {
            'environmental_stress': 0.2,
            'territory_size': 1000,
            'base_food_capacity': 0.8,
            'water_availability': 0.8
        }
        base_result = simulatePopulation(base_params, 200, 12)
        base_deaths = base_result['naturalDeaths']
        
        # High environmental risk scenario
        high_risk_params = base_params.copy()
        high_risk_params['environmental_stress'] = 0.8
        high_risk_result = simulatePopulation(high_risk_params, 200, 12)
        
        # Compare relative death rates rather than absolute numbers
        base_death_rate = base_deaths / base_result['finalPopulation'] if base_result['finalPopulation'] > 0 else 0
        high_death_rate = high_risk_result['naturalDeaths'] / high_risk_result['finalPopulation'] if high_risk_result['finalPopulation'] > 0 else 0
        
        self.assertGreater(high_death_rate, base_death_rate,
                          "Higher environmental stress should lead to higher natural death rate")
        
        # Verify that we actually have natural deaths
        self.assertGreater(base_deaths, 0, "Should have some natural deaths in base scenario")
        self.assertGreater(high_risk_result['naturalDeaths'], 0, "Should have some natural deaths in high risk scenario")

    def test_density_mortality_factor(self):
        """Test the impact of density mortality factor."""
        previous_deaths = 0
        for factor in [0.0, 0.25, 0.5]:  # Increased density factors
            params = DEFAULT_PARAMS.copy()
            params.update({
                'density_mortality_factor': factor,
                'initial_size': 500  # Start with larger population
            })
            
            results = self.run_simulation_with_params(params)
            stats = self.calculate_statistics(results)
            self.log_results(f'density_mortality_{factor}', params, stats)
            
            if factor > 0:
                self.assertGreaterWithTolerance(stats['totalDeaths_mean'], previous_deaths,
                                 f"Higher density factor {factor} should lead to more deaths")
            previous_deaths = stats['totalDeaths_mean']

    def test_mortality_threshold(self):
        """Test the impact of mortality threshold."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 200,
            'sterilization_rate': 0,
            'territory_size': 1000,
            'density_mortality_factor': 0.8  # High density mortality
        })
        
        thresholds = [20, 30, 40, 50]
        previous_deaths = float('inf')  # Initialize with infinity
        
        for threshold in thresholds:
            params = base_params.copy()
            params['mortality_threshold'] = threshold
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'mortality_threshold_{threshold}', params, stats)
            
            if threshold > 20:
                self.assertLessWithTolerance(stats['totalDeaths_mean'], previous_deaths,
                              f"Higher mortality threshold {threshold} should lead to fewer deaths")
            previous_deaths = stats['totalDeaths_mean']

    def test_water_availability(self):
        """Test the impact of water availability."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 100,
            'sterilization_rate': 0
        })
        
        levels = [0.5, 0.75, 1.0]
        previous_pop = 0
        
        for level in levels:
            params = base_params.copy()
            params['water_availability'] = level
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'water_availability_{level}', params, stats)
            
            if previous_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_pop,
                                 f"Higher water availability {level} should support larger population")
            previous_pop = stats['finalPopulation_mean']

    def test_shelter_quality(self):
        """Test the impact of shelter quality."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 100,
            'sterilization_rate': 0
        })
        
        qualities = [0.5, 0.75, 1.0]
        previous_pop = 0
        
        for quality in qualities:
            params = base_params.copy()
            params['shelter_quality'] = quality
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'shelter_quality_{quality}', params, stats)
            
            if previous_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_pop,
                                 f"Higher shelter quality {quality} should support larger population")
            previous_pop = stats['finalPopulation_mean']

    def test_caretaker_support(self):
        """Test the impact of caretaker support."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 100,
            'sterilization_rate': 0
        })
        
        support_levels = [0.2, 0.5, 1.0]
        previous_pop = 0
        
        for level in support_levels:
            params = base_params.copy()
            params['caretaker_support'] = level
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'caretaker_support_{level}', params, stats)
            
            if previous_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_pop,
                                 f"Higher caretaker support {level} should support larger population")
            previous_pop = stats['finalPopulation_mean']

    def test_feeding_consistency(self):
        """Test the impact of feeding consistency."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 100,
            'sterilization_rate': 0
        })
        
        consistencies = [0.5, 0.75, 1.0]
        previous_pop = 0
        
        for consistency in consistencies:
            params = base_params.copy()
            params['feeding_consistency'] = consistency
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'feeding_consistency_{consistency}', params, stats)
            
            if previous_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_pop,
                                 f"Higher feeding consistency {consistency} should support larger population")
            previous_pop = stats['finalPopulation_mean']

    def test_territory_size(self):
        """Test the impact of territory size."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 100,
            'sterilization_rate': 0
        })
        
        sizes = [500, 2000, 5000]
        previous_pop = 0
        
        for size in sizes:
            params = base_params.copy()
            params['territory_size'] = size
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'territory_size_{size}', params, stats)
            
            if previous_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_pop,
                                 f"Larger territory {size} should support larger population")
            previous_pop = stats['finalPopulation_mean']

    def test_base_food_capacity(self):
        """Test the impact of base food capacity."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 100,
            'sterilization_rate': 0
        })
        
        capacities = [0.5, 0.75, 1.0]
        previous_pop = 0
        
        for capacity in capacities:
            params = base_params.copy()
            params['base_food_capacity'] = capacity
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'base_food_capacity_{capacity}', params, stats)
            
            if previous_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_pop,
                                 f"Higher food capacity {capacity} should support larger population")
            previous_pop = stats['finalPopulation_mean']

    def test_food_scaling_factor(self):
        """Test the impact of food scaling factor."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 100,
            'sterilization_rate': 0
        })
        
        factors = [0.5, 1.0, 1.5]
        previous_pop = 0
        
        for factor in factors:
            params = base_params.copy()
            params['food_scaling_factor'] = factor
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'food_scaling_factor_{factor}', params, stats)
            
            if previous_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_pop,
                                 f"Higher food scaling {factor} should support larger population")
            previous_pop = stats['finalPopulation_mean']

    def test_kitten_survival_rate(self):
        """Test the impact of kitten survival rate."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 100,
            'sterilization_rate': 0,
            'breeding_rate': 0.8  # High breeding rate to see survival impact
        })
        
        rates = [0.7, 0.8, 0.9]
        previous_pop = 0
        
        for rate in rates:
            params = base_params.copy()
            params['kitten_survival_rate'] = rate
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'kitten_survival_{rate}', params, stats)
            
            if previous_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_pop,
                                 f"Higher kitten survival {rate} should lead to larger population")
            previous_pop = stats['finalPopulation_mean']

    def test_adult_survival_rate(self):
        """Test the impact of adult survival rate."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 100,
            'sterilization_rate': 0
        })
        
        rates = [0.8, 0.9, 0.95]
        previous_pop = 0
        
        for rate in rates:
            params = base_params.copy()
            params['adult_survival_rate'] = rate
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'adult_survival_{rate}', params, stats)
            
            if previous_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_pop,
                                 f"Higher adult survival {rate} should lead to larger population")
            previous_pop = stats['finalPopulation_mean']

    def test_survival_density_factor(self):
        """Test the impact of survival density factor."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 200,  # Start with larger population
            'sterilization_rate': 0,
            'territory_size': 1000  # Small territory to increase density
        })
        
        factors = [0.0, 0.15, 0.3]
        previous_deaths = 0
        
        for factor in factors:
            params = base_params.copy()
            params['survival_density_factor'] = factor
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'survival_density_{factor}', params, stats)
            
            if factor > 0:
                self.assertGreaterWithTolerance(stats['totalDeaths_mean'], previous_deaths,
                                 f"Higher survival density factor {factor} should lead to more deaths in dense populations")
            previous_deaths = stats['totalDeaths_mean']

    def test_breeding_rate(self):
        """Test the impact of breeding rate."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 50,
            'sterilization_rate': 0,
            'kitten_survival_rate': 0.8,
            'adult_survival_rate': 0.9
        })
        
        rates = [0.3, 0.5, 0.8]
        previous_pop = 0
        
        for rate in rates:
            params = base_params.copy()
            params['breeding_rate'] = rate
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'breeding_rate_{rate}', params, stats)
            
            if previous_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_pop,
                                 f"Higher breeding rate {rate} should lead to larger population")
            previous_pop = stats['finalPopulation_mean']

    def test_kittens_per_litter(self):
        """Test the impact of kittens per litter."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 50,
            'sterilization_rate': 0,
            'breeding_rate': 0.8,
            'kitten_survival_rate': 0.8
        })
        
        litter_sizes = [2.0, 4.0, 6.0]
        previous_pop = 0
        
        for size in litter_sizes:
            params = base_params.copy()
            params['kittens_per_litter'] = size
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'kittens_per_litter_{size}', params, stats)
            
            if previous_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_pop,
                                 f"More kittens per litter {size} should lead to larger population")
            previous_pop = stats['finalPopulation_mean']

    def test_litters_per_year(self):
        """Test the impact of litters per year."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 50,
            'sterilization_rate': 0,
            'breeding_rate': 0.8,
            'kitten_survival_rate': 0.8
        })
        
        litters = [1.0, 2.0, 3.0]
        previous_pop = 0
        
        for num_litters in litters:
            params = base_params.copy()
            params['litters_per_year'] = num_litters
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            self.log_results(f'litters_per_year_{num_litters}', params, stats)
            
            if previous_pop > 0:
                self.assertGreaterWithTolerance(stats['finalPopulation_mean'], previous_pop,
                                 f"More litters per year {num_litters} should lead to larger population")
            previous_pop = stats['finalPopulation_mean']

    def test_seasonal_breeding_amplitude(self):
        """Test the impact of seasonal breeding amplitude."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 100,
            'sterilization_rate': 0,
            'breeding_rate': 0.8
        })
        
        amplitudes = [0.1, 0.3, 0.5]
        previous_variation = 0
        
        for amplitude in amplitudes:
            params = base_params.copy()
            params['seasonal_breeding_amplitude'] = amplitude
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            monthly_stats = stats.get('monthly_stats', {})
            
            # Calculate population variation
            if monthly_stats:
                variation = max(monthly_stats) - min(monthly_stats)
                if amplitude > 0:
                    self.assertGreaterWithTolerance(variation, previous_variation,
                                     f"Higher amplitude {amplitude} should cause more population variation")
                previous_variation = variation
            
            self.log_results(f'seasonal_amplitude_{amplitude}', params, stats)

    def test_peak_breeding_month(self):
        """Test the impact of peak breeding month."""
        base_params = DEFAULT_PARAMS.copy()
        base_params.update({
            'months': 24,
            'initial_size': 100,
            'sterilization_rate': 0,
            'breeding_rate': 0.8,
            'seasonal_breeding_amplitude': 0.5  # Strong seasonal effect
        })
        
        peak_months = [3, 6, 9]  # Different peak months
        
        for month in peak_months:
            params = base_params.copy()
            params['peak_breeding_month'] = month
            results = self.run_simulation_with_params(params, self.num_iterations)
            stats = self.calculate_statistics(results)
            monthly_stats = stats.get('monthly_stats', {})
            
            if monthly_stats:
                # Find month with maximum population
                max_month = max(range(len(monthly_stats)), key=lambda i: monthly_stats[i])
                # Peak should occur a few months after breeding peak
                expected_peak = (month + 2) % 12 or 12  # Adjust for December
                self.assertAlmostEqual(max_month % 12 or 12, expected_peak, delta=2,
                                     msg=f"Population peak should occur ~2 months after breeding peak month {month}")
            
            self.log_results(f'peak_breeding_month_{month}', params, stats)

    def test_carrying_capacity(self):
        """Test carrying capacity calculations with various inputs"""
        test_cases = [
            # Test territory size impact
            (1000, 1.2, 0.8, "medium territory"),
            (10000, 1.2, 0.8, "large territory"),
            (100, 1.2, 0.8, "small territory"),
            
            # Test density threshold impact
            (1000, 0.5, 0.8, "low density"),
            (1000, 3.0, 0.8, "high density"),
            
            # Test resource factor impact
            (1000, 1.2, 0.2, "poor resources"),
            (1000, 1.2, 1.0, "excellent resources"),
            
            # Test extreme combinations
            (10000, 3.0, 1.0, "optimal conditions"),
            (100, 0.5, 0.2, "worst conditions")
        ]
        
        for territory, density, resources, case_name in test_cases:
            capacity = self.calculateCarryingCapacity(territory, density, resources)
            self.assertGreater(capacity, 0, f"{case_name}: Capacity should be positive")
            if case_name == "optimal conditions":
                self.assertGreater(capacity, 1000, f"{case_name}: Should support large population")
            if case_name == "worst conditions":
                self.assertLess(capacity, 100, f"{case_name}: Should limit population")

    def test_resource_availability(self):
        """Test resource availability calculations"""
        test_cases = [
            # Test food impact
            (1.0, 0.8, 0.8, 0.8, 0.8, "high food"),
            (0.2, 0.8, 0.8, 0.8, 0.8, "low food"),
            
            # Test water impact
            (0.8, 1.0, 0.8, 0.8, 0.8, "high water"),
            (0.8, 0.2, 0.8, 0.8, 0.8, "low water"),
            
            # Test shelter impact
            (0.8, 0.8, 1.0, 0.8, 0.8, "high shelter"),
            (0.8, 0.8, 0.2, 0.8, 0.8, "low shelter"),
            
            # Test caretaker impact
            (0.8, 0.8, 0.8, 1.0, 0.8, "high support"),
            (0.8, 0.8, 0.8, 0.2, 0.8, "low support"),
            
            # Test feeding consistency
            (0.8, 0.8, 0.8, 0.8, 1.0, "consistent feeding"),
            (0.8, 0.8, 0.8, 0.8, 0.2, "inconsistent feeding"),
            
            # Test combinations
            (1.0, 1.0, 1.0, 1.0, 1.0, "optimal resources"),
            (0.2, 0.2, 0.2, 0.2, 0.2, "poor resources")
        ]
        
        for food, water, shelter, care, feeding, case_name in test_cases:
            resources = self.calculateResourceAvailability(food, water, shelter, care, feeding)
            self.assertGreaterEqual(resources, 0.1, f"{case_name}: Resources should not be below minimum")
            self.assertLessEqual(resources, 1.0, f"{case_name}: Resources should not exceed maximum")
            if case_name == "optimal resources":
                self.assertGreater(resources, 0.8, f"{case_name}: Should indicate excellent conditions")
            if case_name == "poor resources":
                self.assertLess(resources, 0.5, f"{case_name}: Should indicate poor conditions")

    def test_population_dynamics(self):
        """Test population dynamics under various scenarios"""
        test_scenarios = [
            # Test basic colony growth
            ({}, 10, 12, 0, 0, 0, "natural growth"),
            
            # Test sterilization impact
            ({}, 20, 12, 10, 2, 0, "active sterilization"),
            
            # Test abandonment impact
            ({}, 15, 12, 0, 0, 2, "with abandonment"),
            
            # Test territory size impact
            ({'territorySize': 10000}, 50, 12, 0, 0, 0, "large territory"),
            ({'territorySize': 100}, 50, 12, 0, 0, 0, "small territory"),
            
            # Test density impact
            ({'densityThreshold': 3.0}, 100, 12, 0, 0, 0, "high density allowed"),
            ({'densityThreshold': 0.5}, 100, 12, 0, 0, 0, "low density allowed"),
            
            # Test resource impact
            ({
                'baseFoodCapacity': 1.0,
                'waterAvailability': 1.0,
                'shelterQuality': 1.0,
                'caretakerSupport': 1.0,
                'feedingConsistency': 1.0
            }, 50, 12, 0, 0, 0, "excellent resources"),
            
            ({
                'baseFoodCapacity': 0.2,
                'waterAvailability': 0.2,
                'shelterQuality': 0.2,
                'caretakerSupport': 0.2,
                'feedingConsistency': 0.2
            }, 50, 12, 0, 0, 0, "poor resources"),
            
            # Test environmental risks
            ({
                'urbanization_impact': 0.5,
                'disease_transmission_rate': 0.3,
                'environmental_stress': 0.4
            }, 50, 12, 0, 0, 0, "high risk environment"),
            
            # Test seasonal effects
            ({
                'peakBreedingMonth': 4,
                'seasonalBreedingAmplitude': 0.8
            }, 30, 24, 0, 0, 0, "strong seasonal breeding"),
            
            # Test complex scenarios
            ({
                'territorySize': 10000,
                'densityThreshold': 3.0,
                'baseFoodCapacity': 1.0,
                'waterAvailability': 1.0,
                'shelterQuality': 1.0,
                'caretakerSupport': 1.0,
                'feedingConsistency': 1.0,
                'urbanization_impact': 0.1,
                'disease_transmission_rate': 0.05,
                'environmental_stress': 0.05
            }, 100, 24, 20, 5, 1, "optimal managed colony"),
            
            ({
                'territorySize': 100,
                'densityThreshold': 0.5,
                'baseFoodCapacity': 0.2,
                'waterAvailability': 0.2,
                'shelterQuality': 0.2,
                'caretakerSupport': 0.2,
                'feedingConsistency': 0.2,
                'urbanization_impact': 0.5,
                'disease_transmission_rate': 0.3,
                'environmental_stress': 0.4
            }, 100, 24, 0, 0, 0, "challenging environment")
        ]
        
        for params_override, size, months, sterilized, monthly_sterilization, abandonment, case_name in test_scenarios:
            params = self.default_params.copy()
            params.update(params_override)
            
            result = simulatePopulation(
                params, size, months, sterilized, 
                monthly_sterilization, abandonment
            )
            
            self.assertIsNotNone(result, f"{case_name}: Simulation should not fail")
            self.assertIn('finalPopulation', result, f"{case_name}: Should include final population")
            self.assertIn('monthlyData', result, f"{case_name}: Should include monthly data")
            
            # Specific assertions for each scenario
            if case_name == "natural growth":
                self.assertGreater(result['finalPopulation'], size, 
                    "Natural growth should increase population")
                
            elif case_name == "active sterilization":
                sterilized_cats = result['monthlyData'][-1].get('sterilized', 0)
                self.assertGreater(sterilized_cats, sterilized,
                    "Sterilization program should increase sterilized population")
                
            elif case_name == "with abandonment":
                self.assertGreater(result['finalPopulation'], size,
                    "Population should account for abandoned cats")
                
            elif case_name == "large territory":
                self.assertGreater(result['finalPopulation'], 50,
                    "Large territory should support larger population")
                
            elif case_name == "small territory":
                self.assertLess(result['finalPopulation'], 100,
                    "Small territory should limit population")
                
            elif case_name == "optimal managed colony":
                self.assertGreater(result['finalPopulation'], 0,
                    "Optimal conditions should maintain healthy population")
                self.assertLess(result['finalPopulation'], 1000,
                    "Population should still be controlled")
                
            elif case_name == "challenging environment":
                self.assertLess(result['finalPopulation'], size,
                    "Challenging environment should reduce population")

    def test_large_colony_stability(self):
        """Test that large initial colonies don't collapse too quickly."""
        params = {
            'territorySize': 1000,
            'densityThreshold': 1.2,
            'baseFoodCapacity': 0.8,
            'waterAvailability': 0.8,
            'shelterQuality': 0.7,
            'caretakerSupport': 0.6,
            'feedingConsistency': 0.7,
            'adult_survival_rate': 0.85,
            'kitten_survival_rate': 0.7,
            'disease_transmission_rate': 0.1,
            'urbanization_impact': 0.2,
            'environmental_stress': 0.15
        }
        
        # Run simulation with large initial population
        result = simulatePopulation(params, 250, 12)
        
        # Get population over time
        monthly_totals = [month['total'] for month in result['monthlyData']]
        
        # Calculate rate of population decline
        max_monthly_decline = 0
        for i in range(1, len(monthly_totals)):
            decline = (monthly_totals[i-1] - monthly_totals[i]) / monthly_totals[i-1]
            max_monthly_decline = max(max_monthly_decline, decline)
        
        # Population shouldn't decline by more than 30% in any given month
        self.assertLess(max_monthly_decline, 0.3, 
                       "Large colony population declined too rapidly")
        
        # Final population should be at least 25% of initial
        self.assertGreater(monthly_totals[-1], monthly_totals[0] * 0.25,
                          "Large colony population collapsed too severely")

    def test_sterilization_mortality_equality(self):
        """Test that sterilized and unsterilized cats have equal mortality rates."""
        # Run two simulations with different sterilization rates but same total population
        base_params = {
            'territorySize': 1000,
            'densityThreshold': 0.8,
            'baseFoodCapacity': 0.7,
            'waterAvailability': 0.7,
            'shelterQuality': 0.7,
            'adult_survival_rate': 0.85,  # Fixed survival rate
            'disease_transmission_rate': 0.1,
            'urbanization_impact': 0.1,
            'environmental_stress': 0.1
        }

        # First simulation: No sterilization
        no_steril_result = simulatePopulation(
            base_params,
            currentSize=100,
            months=12,
            sterilizedCount=0,
            monthlySterilization=0
        )

        # Second simulation: All cats sterilized
        all_steril_result = simulatePopulation(
            base_params,
            currentSize=100,
            months=12,
            sterilizedCount=100,  # All cats sterilized
            monthlySterilization=0
        )

        # Calculate death rates over the simulation period
        def calculate_death_rate(result):
            total_deaths = sum(
                month['total'] - month_prev['total'] + births
                for month, month_prev, births in zip(
                    result['monthlyData'][1:],
                    result['monthlyData'][:-1],
                    [month.get('births', 0) for month in result['monthlyData'][1:]]
                )
                if month['total'] - month_prev['total'] + births < 0  # Only count decreases
            )
            initial_pop = result['monthlyData'][0]['total']
            return abs(total_deaths) / initial_pop if initial_pop > 0 else 0

        no_steril_death_rate = calculate_death_rate(no_steril_result)
        all_steril_death_rate = calculate_death_rate(all_steril_result)

        # Death rates should be within 5% of each other
        death_rate_diff = abs(no_steril_death_rate - all_steril_death_rate)
        avg_death_rate = (no_steril_death_rate + all_steril_death_rate) / 2

        self.assertLess(
            death_rate_diff,
            avg_death_rate * 0.05,  # 5% tolerance
            f"Death rates should be similar regardless of sterilization. "
            f"No sterilization: {no_steril_death_rate:.3f}, "
            f"All sterilized: {all_steril_death_rate:.3f}"
        )

        # Also verify monthly death counts are similar
        monthly_death_diff = [
            abs((m1['total'] - m1_prev['total']) - (m2['total'] - m2_prev['total']))
            for m1, m1_prev, m2, m2_prev in zip(
                no_steril_result['monthlyData'][1:],
                no_steril_result['monthlyData'][:-1],
                all_steril_result['monthlyData'][1:],
                all_steril_result['monthlyData'][:-1]
            )
        ]

        avg_monthly_diff = sum(monthly_death_diff) / len(monthly_death_diff)
        self.assertLess(
            avg_monthly_diff,
            5,  # Allow for small random variations
            "Monthly death counts should be similar between sterilized and unsterilized populations"
        )

    def test_sterilized_population_mortality(self):
        """Test that mortality still occurs in a fully sterilized population with no abandonment."""
        params = {
            'territorySize': 1000,
            'densityThreshold': 0.8,
            'baseFoodCapacity': 0.7,
            'waterAvailability': 0.7,
            'shelterQuality': 0.7,
            'adult_survival_rate': 0.92,  # Even with high survival rate
            'disease_transmission_rate': 0.1,
            'urbanization_impact': 0.1,
            'environmental_stress': 0.1
        }

        # Run simulation with fully sterilized population and no abandonment
        result = simulatePopulation(
            params,
            currentSize=100,
            months=12,
            sterilizedCount=100,  # All cats sterilized
            monthlySterilization=0,  # No new sterilizations needed
            monthlyAbandonment=0  # No abandonment
        )

        # Track population changes
        monthly_deaths = []
        for i in range(1, len(result['monthlyData'])):
            prev_month = result['monthlyData'][i-1]
            curr_month = result['monthlyData'][i]
            # Since all cats are sterilized and no abandonment, any decrease is due to deaths
            if curr_month['total'] < prev_month['total']:
                monthly_deaths.append(prev_month['total'] - curr_month['total'])

        # There should be at least some months with deaths
        self.assertGreater(
            len(monthly_deaths),
            0,
            "No deaths occurred in fully sterilized population"
        )

        # Calculate death rate
        total_deaths = sum(monthly_deaths)
        initial_population = result['monthlyData'][0]['total']
        death_rate = total_deaths / initial_population

        # Death rate should be reasonable (between 5% and 30% annually)
        self.assertGreater(
            death_rate,
            0.05,
            f"Death rate too low ({death_rate:.2%}) for sterilized population"
        )
        self.assertLess(
            death_rate,
            0.30,
            f"Death rate too high ({death_rate:.2%}) for sterilized population"
        )

        # Verify that sterilized count matches deaths
        total_sterilized_decrease = (
            result['monthlyData'][0]['sterilized'] -
            result['monthlyData'][-1]['sterilized']
        )
        self.assertEqual(
            total_deaths,
            total_sterilized_decrease,
            "Sterilized population decrease should match total deaths"
        )

    def test_small_sterilized_colony_mortality(self):
        """Test that a small, fully sterilized colony still experiences deaths over time."""
        params = {
            'territorySize': 1000,
            'densityThreshold': 0.8,
            'baseFoodCapacity': 0.7,
            'waterAvailability': 0.7,
            'shelterQuality': 0.7,
            'adult_survival_rate': 0.92,
            'disease_transmission_rate': 0.1,
            'urbanization_impact': 0.1,
            'environmental_stress': 0.1
        }

        # Run simulation with small fully sterilized population
        result = simulatePopulation(
            params,
            currentSize=10,  # Small colony
            months=60,  # Long duration
            sterilizedCount=10,  # All cats sterilized
            monthlySterilization=0,
            monthlyAbandonment=0  # No abandonment
        )

        # Count months with deaths
        months_with_deaths = 0
        total_deaths = 0
        prev_total = result['monthlyData'][0]['total']
        
        for month in result['monthlyData'][1:]:
            if month['total'] < prev_total:
                months_with_deaths += 1
                total_deaths += (prev_total - month['total'])
            prev_total = month['total']

        # Should have deaths in at least 10% of months (6 out of 60 months)
        self.assertGreater(
            months_with_deaths,
            5,
            f"Too few months with deaths ({months_with_deaths} out of 60) in small sterilized colony"
        )

        # Should have at least 2 deaths over 5 years (minimum mortality)
        self.assertGreater(
            total_deaths,
            1,
            f"Too few total deaths ({total_deaths}) over 60 months in small sterilized colony"
        )

        # Check final population
        final_population = result['monthlyData'][-1]['total']
        self.assertLess(
            final_population,
            10,  # Should have fewer cats than initial
            f"No mortality observed in small sterilized colony over 60 months"
        )

        # Verify sterilized count matches total throughout simulation
        for month in result['monthlyData']:
            self.assertEqual(
                month['total'],
                month['sterilized'],
                "Sterilized count should match total population"
            )

    def test_environment_presets(self):
        """Test that each environment preset produces expected outcomes."""
        
        # Test configurations for each environment
        environment_tests = {
            'forest': {
                'params': {
                    'territory': 8000,
                    'density': 0.5,
                    'baseFoodCapacity': 0.6,
                    'foodScalingFactor': 0.5,
                    'environmentalStress': 0.2,
                    'resourceCompetition': 0.4,
                    'resourceScarcityImpact': 0.4,
                    'baseHabitatQuality': 0.9,
                    'urbanizationImpact': 0.1,
                    'diseaseTransmissionRate': 0.4,
                    'monthlyAbandonment': 1
                },
                'expectations': {
                    'mortality_distribution': {
                        'urban_deaths': (0, 0.1),     # Very low urban deaths
                        'disease_deaths': (0.3, 0.5),  # High disease deaths from wildlife
                        'natural_deaths': (0.2, 0.4)   # Moderate natural deaths
                    },
                    'reproduction_rate': (0.7, 0.9),   # Good reproduction due to space
                    'food_availability': (0.5, 0.7),   # Moderate natural food sources
                    'population_density': (0.3, 0.6)   # Low density due to large territory
                }
            },
            'street': {
                'params': {
                    'territory': 1000,
                    'density': 1.5,
                    'baseFoodCapacity': 0.3,
                    'foodScalingFactor': 0.3,
                    'environmentalStress': 0.5,
                    'resourceCompetition': 0.6,
                    'resourceScarcityImpact': 0.6,
                    'baseHabitatQuality': 0.3,
                    'urbanizationImpact': 0.8,
                    'diseaseTransmissionRate': 0.4,
                    'monthlyAbandonment': 4
                },
                'expectations': {
                    'mortality_distribution': {
                        'urban_deaths': (0.4, 0.6),    # High traffic deaths
                        'disease_deaths': (0.2, 0.4),   # Moderate-high disease
                        'natural_deaths': (0.2, 0.3)    # Moderate natural deaths
                    },
                    'reproduction_rate': (0.4, 0.6),    # Lower reproduction due to stress
                    'food_availability': (0.2, 0.4),    # Poor food sources
                    'population_density': (1.2, 1.8)    # High density in small area
                }
            },
            'residential': {
                'params': {
                    'territory': 2000,
                    'density': 1.2,
                    'baseFoodCapacity': 0.8,
                    'foodScalingFactor': 0.7,
                    'environmentalStress': 0.2,
                    'resourceCompetition': 0.3,
                    'resourceScarcityImpact': 0.3,
                    'baseHabitatQuality': 0.7,
                    'urbanizationImpact': 0.4,
                    'diseaseTransmissionRate': 0.15,
                    'monthlyAbandonment': 3
                },
                'expectations': {
                    'mortality_distribution': {
                        'urban_deaths': (0.2, 0.3),    # Moderate traffic deaths
                        'disease_deaths': (0.1, 0.2),   # Low disease due to care
                        'natural_deaths': (0.1, 0.2)    # Low natural deaths
                    },
                    'reproduction_rate': (0.6, 0.8),    # Good reproduction
                    'food_availability': (0.7, 0.9),    # Good food from residents
                    'population_density': (1.0, 1.4)    # Moderate-high density
                }
            },
            'beach': {
                'params': {
                    'territory': 4000,
                    'density': 0.7,
                    'baseFoodCapacity': 0.5,
                    'foodScalingFactor': 0.5,
                    'environmentalStress': 0.3,
                    'resourceCompetition': 0.4,
                    'resourceScarcityImpact': 0.4,
                    'baseHabitatQuality': 0.5,
                    'urbanizationImpact': 0.3,
                    'diseaseTransmissionRate': 0.3,
                    'monthlyAbandonment': 2
                },
                'expectations': {
                    'mortality_distribution': {
                        'urban_deaths': (0.1, 0.2),    # Low traffic deaths
                        'disease_deaths': (0.2, 0.4),   # Moderate disease from exposure
                        'natural_deaths': (0.3, 0.5)    # Higher natural deaths from elements
                    },
                    'reproduction_rate': (0.5, 0.7),    # Moderate reproduction
                    'food_availability': (0.4, 0.6),    # Moderate food from tourists/fishing
                    'population_density': (0.5, 0.8)    # Moderate density
                }
            }
        }

        for env_name, test_config in environment_tests.items():
            with self.subTest(environment=env_name):
                # Run simulation with environment parameters
                results = simulatePopulation(test_config['params'], 20, 24)  # 20 cats, 24 months
                
                # Test mortality distribution
                total_deaths = (results['urbanDeaths'] + results['diseaseDeaths'] + 
                              results['naturalDeaths'])
                if total_deaths > 0:
                    urban_ratio = results['urbanDeaths'] / total_deaths
                    disease_ratio = results['diseaseDeaths'] / total_deaths
                    natural_ratio = results['naturalDeaths'] / total_deaths
                    
                    exp = test_config['expectations']['mortality_distribution']
                    self.assertGreaterEqual(urban_ratio, exp['urban_deaths'][0])
                    self.assertLessEqual(urban_ratio, exp['urban_deaths'][1])
                    self.assertGreaterEqual(disease_ratio, exp['disease_deaths'][0])
                    self.assertLessEqual(disease_ratio, exp['disease_deaths'][1])
                    self.assertGreaterEqual(natural_ratio, exp['natural_deaths'][0])
                    self.assertLessEqual(natural_ratio, exp['natural_deaths'][1])
                
                # Test reproduction rate
                exp = test_config['expectations']['reproduction_rate']
                reproduction_rate = results['totalBirths'] / (results['monthlyData'][0]['total'] * 24)
                self.assertGreaterEqual(reproduction_rate, exp[0])
                self.assertLessEqual(reproduction_rate, exp[1])
                
                # Test food availability
                exp = test_config['expectations']['food_availability']
                avg_food = mean([m.get('foodAvailability', 0) for m in results['monthlyData']])
                self.assertGreaterEqual(avg_food, exp[0])
                self.assertLessEqual(avg_food, exp[1])
                
                # Test population density
                exp = test_config['expectations']['population_density']
                final_density = results['monthlyData'][-1]['total'] / test_config['params']['territory']
                self.assertGreaterEqual(final_density, exp[0])
                self.assertLessEqual(final_density, exp[1])

if __name__ == '__main__':
    unittest.main()
