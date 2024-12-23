import unittest
import sys
import random
import numpy as np
from simulation import simulatePopulation
from test_suite import TestCatSimulation
import traceback

def run_test(test_name, params):
    """Run a single test and return if it passed."""
    try:
        TestCatSimulation.default_params = {
            'territorySize': 1000,
            'baseFoodCapacity': 0.8,
            'waterAvailability': 0.8,
            'shelterQuality': 0.7,
            'caretakerSupport': 0.6,
            'feedingConsistency': 0.7,
            'peakBreedingMonth': 4,
            **params
        }
        
        # Create test suite and run just this test
        test_case = TestCatSimulation(test_name)
        suite = unittest.TestSuite()
        suite.addTest(test_case)
        
        # Run test silently
        runner = unittest.TextTestRunner(stream=None)
        result = runner.run(suite)
        return len(result.failures) + len(result.errors) == 0
        
    except KeyError as e:
        print(f"\nERROR: Missing or incorrect parameter name: {str(e)}")
        print("Check that all parameter names exactly match those in simulation.py")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error in {test_name}: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)

class ParameterTuner:
    def __init__(self):
        self.test_suite = TestCatSimulation()
        self.test_methods = [method for method in dir(self.test_suite) if method.startswith('test_')]
        self.param_ranges = {
            # Survival rates - optimize for tropical growth
            'adult_survival_rate': (0.95, 0.99),  # Very high survival for growth
            'kitten_survival_rate': (0.85, 0.95),  # Higher kitten survival
            
            # Breeding parameters - optimize for tropical conditions
            'breeding_rate': (0.8, 1.0),          # High breeding rate
            'kittens_per_litter': (3.0, 6.0),     # Normal litter size
            'litters_per_year': (2.0, 4.0),       # Multiple litters possible
            'female_ratio': (0.5, 0.6),           # Slightly more females
            
            # Seasonal effects - minimize for tropical
            'peakBreedingMonth': (3, 5),          # Spring peak
            'seasonalBreedingAmplitude': (0.1, 0.3),  # Low seasonal variation
            
            # Resource parameters
            'baseFoodCapacity': (0.1, 0.9),       # Variable food
            'waterAvailability': (0.3, 0.9),      # Good water
            'shelterQuality': (0.4, 0.9),         # Good shelter
            'caretakerSupport': (0.3, 0.9),       # Variable care
            'feedingConsistency': (0.2, 0.9),     # Variable feeding
            
            # Territory and density
            'territorySize': (1000, 5000),        # Various sizes
            'densityThreshold': (0.2, 0.8),       # Variable density limits
            
            # Environmental stress
            'disease_transmission_rate': (0.1, 0.5),
            'urbanization_impact': (0.1, 0.5),
            'environmental_stress': (0.1, 0.5)
        }

        # Map tests to their most relevant parameters
        self.test_param_map = {
            'test_abandonment_impact': ['adult_survival_rate', 'kitten_survival_rate'],
            'test_basic_simulation': ['adult_survival_rate', 'breeding_rate'],
            'test_breeding_rate': ['breeding_rate', 'kittens_per_litter', 'litters_per_year'],
            'test_carrying_capacity': ['territorySize', 'densityThreshold', 'baseFoodCapacity'],
            'test_comprehensive_carrying_capacity': ['territorySize', 'densityThreshold', 'baseFoodCapacity', 'waterAvailability', 'shelterQuality'],
            'test_density_effects': ['territorySize', 'densityThreshold'],
            'test_disease_transmission': ['disease_transmission_rate', 'adult_survival_rate'],
            'test_environmental_stress': ['environmental_stress', 'adult_survival_rate'],
            'test_feeding_station_impact': ['feedingConsistency', 'baseFoodCapacity'],
            'test_kitten_mortality': ['kitten_survival_rate'],
            'test_long_term_stability': ['adult_survival_rate', 'breeding_rate', 'densityThreshold'],
            'test_mortality_rate': ['adult_survival_rate', 'disease_transmission_rate'],
            'test_population_dynamics': ['breeding_rate', 'adult_survival_rate', 'densityThreshold'],
            'test_resource_availability': ['baseFoodCapacity', 'waterAvailability', 'shelterQuality'],
            'test_resource_competition': ['baseFoodCapacity', 'waterAvailability', 'shelterQuality', 'densityThreshold'],
            'test_seasonal_breeding': ['seasonalBreedingAmplitude', 'peakBreedingMonth'],
            'test_small_sterilized_colony_mortality': ['adult_survival_rate', 'disease_transmission_rate'],
            'test_sterilization_impact': ['breeding_rate', 'female_ratio'],
            'test_sterilization_mortality_equality': ['adult_survival_rate', 'disease_transmission_rate'],
            'test_sterilized_population_mortality': ['adult_survival_rate', 'disease_transmission_rate'],
            'test_territory_size': ['territorySize', 'densityThreshold'],
            'test_tropical_breeding_rate': ['seasonalBreedingAmplitude', 'breeding_rate'],
            'test_tropical_population_growth': ['breeding_rate', 'kittens_per_litter', 'litters_per_year', 'adult_survival_rate', 'kitten_survival_rate', 'female_ratio', 'baseFoodCapacity', 'waterAvailability'],
            'test_urbanization_impact': ['urbanization_impact', 'adult_survival_rate'],
            # Adding environment preset tests
            'test_environment_resource_availability': ['baseFoodCapacity', 'waterAvailability', 'shelterQuality', 'caretakerSupport', 'feedingConsistency'],
            'test_environment_carrying_capacity': ['territorySize', 'densityThreshold', 'baseFoodCapacity', 'waterAvailability', 'shelterQuality'],
            'test_environment_mortality_patterns': ['urbanization_impact', 'disease_transmission_rate', 'environmental_stress']
        }
        
        # Environment-specific parameter ranges
        self.environment_ranges = {
            'urban': {
                'baseFoodCapacity': (0.6, 0.9),     # Higher food availability in urban areas
                'waterAvailability': (0.7, 0.9),     # Good water access
                'shelterQuality': (0.6, 0.8),        # Moderate to good shelter
                'caretakerSupport': (0.5, 0.8),      # Variable caretaker support
                'feedingConsistency': (0.6, 0.9),    # More consistent feeding
                'territorySize': (500, 2000),        # Smaller territories
                'densityThreshold': (1.5, 3.0),      # Higher density tolerance
                'urbanization_impact': (0.3, 0.5),   # Moderate urban impact
                'disease_transmission_rate': (0.2, 0.4),  # Higher disease risk
                'environmental_stress': (0.3, 0.5)    # Moderate environmental stress
            },
            'suburban': {
                'baseFoodCapacity': (0.4, 0.7),      # Moderate food availability
                'waterAvailability': (0.5, 0.8),      # Variable water access
                'shelterQuality': (0.4, 0.7),         # Variable shelter
                'caretakerSupport': (0.3, 0.6),       # Less caretaker support
                'feedingConsistency': (0.4, 0.7),     # Less consistent feeding
                'territorySize': (2000, 5000),        # Larger territories
                'densityThreshold': (1.0, 2.0),       # Moderate density tolerance
                'urbanization_impact': (0.2, 0.4),    # Lower urban impact
                'disease_transmission_rate': (0.1, 0.3),  # Moderate disease risk
                'environmental_stress': (0.2, 0.4)     # Lower environmental stress
            },
            'rural': {
                'baseFoodCapacity': (0.2, 0.5),      # Lower food availability
                'waterAvailability': (0.3, 0.6),      # Limited water access
                'shelterQuality': (0.2, 0.5),         # Basic shelter
                'caretakerSupport': (0.1, 0.4),       # Minimal caretaker support
                'feedingConsistency': (0.2, 0.5),     # Inconsistent feeding
                'territorySize': (5000, 10000),       # Very large territories
                'densityThreshold': (0.5, 1.5),       # Lower density tolerance
                'urbanization_impact': (0.1, 0.3),    # Minimal urban impact
                'disease_transmission_rate': (0.1, 0.2),  # Lower disease risk
                'environmental_stress': (0.1, 0.3)     # Higher environmental stress
            }
        }
        
        # Initialize parameters to midpoint of ranges
        self.current_params = {
            param: (min_val + max_val) / 2
            for param, (min_val, max_val) in self.param_ranges.items()
        }
        
        # Track parameter adjustment history
        self.param_success = {param: 0 for param in self.param_ranges}
        self.param_momentum = {param: 0 for param in self.param_ranges}
        
        self.best_params = None
        self.best_failure_count = float('inf')

    def run_tests(self, params):
        """Run all tests and return number of failures."""
        failures = []
        for test_method in self.test_methods:
            try:
                # Reset any instance variables that might have been modified
                self.test_suite.setUp()
                
                # Run the test
                getattr(self.test_suite, test_method)()
                
            except AssertionError as e:
                # Expected test failures
                failures.append((test_method, str(e)))
            except Exception as e:
                # Unexpected errors - stop immediately
                print(f"\nERROR in {test_method}: {str(e)}")
                print("Stopping tuning due to unexpected error")
                raise  # Re-raise the exception to stop execution
        
        return failures

    def adjust_param(self, param_name, direction, iteration, max_iterations):
        """Adjust a parameter value with adaptive step size and momentum."""
        min_val, max_val = self.param_ranges[param_name]
        current = self.current_params[param_name]
        
        # Adaptive step size - gets smaller as we progress
        progress = iteration / max_iterations
        base_step = (max_val - min_val) * 0.1  # 10% of range
        step = base_step * (1 - 0.8 * progress)  # Reduces to 20% of original step
        
        # Apply momentum if we've had success with this direction
        momentum = self.param_momentum[param_name]
        if momentum * direction > 0:  # Same direction as momentum
            step *= (1 + abs(momentum) * 0.5)  # Increase step up to 50%
            
        if direction > 0:
            new_val = min(max_val, current + step)
        else:
            new_val = max(min_val, current - step)
            
        self.current_params[param_name] = new_val
        
    def tune(self, max_iterations=100):
        """Tune parameters to minimize test failures."""
        iteration = 0
        while iteration < max_iterations:
            try:
                print(f"Iteration {iteration}: ", end='')
                
                # Generate random parameters within ranges
                current_params = {
                    param: random.uniform(range_min, range_max)
                    for param, (range_min, range_max) in self.param_ranges.items()
                }
                
                # Run tests with current parameters
                failures = self.run_tests(current_params)
                
                # Update if this is the best so far
                if len(failures) < self.best_failure_count:
                    self.best_failure_count = len(failures)
                    self.best_params = current_params
                    print(f"\nNew best parameters found with {len(failures)} failing tests:")
                    for param, value in current_params.items():
                        print(f"  {param}: {value}")
                    print("\nFailing tests:")
                    for test_name, error in failures:
                        print(f"  {test_name}: {error}")
                else:
                    print(f"{len(failures)} failing tests")
                
                # Pick a failing test, prioritizing those that have been failing longer
                test = random.choice([test for test, _ in failures])
                
                # Pick parameter based on success history
                test_params = self.test_param_map[test]
                weights = [max(0.1, self.param_success[p]) for p in test_params]
                param = random.choices(test_params, weights=weights)[0]
                
                # Try both directions, tracking success
                old_value = self.current_params[param]
                old_failing = len(failures)
                
                best_direction = 0
                for direction in [1, -1]:
                    self.adjust_param(param, direction, iteration, max_iterations)
                    new_failing = len(self.run_tests(self.current_params))
                    
                    if new_failing < old_failing:
                        best_direction = direction
                        self.param_success[param] += 1
                        # Update momentum in successful direction
                        self.param_momentum[param] = 0.8 * self.param_momentum[param] + 0.2 * direction
                        break
                    else:
                        # Revert and try other direction
                        self.current_params[param] = old_value
                
                if best_direction == 0:
                    # Neither direction helped, reduce momentum
                    self.param_momentum[param] *= 0.5
                    self.param_success[param] = max(0, self.param_success[param] - 0.5)
                    self.current_params[param] = old_value
                
                iteration += 1
                
            except Exception as e:
                print(f"\nStopping tuning due to error: {str(e)}")
                import traceback
                traceback.print_exc()
                break

    def tune_environment(self, environment_type, max_iterations=100):
        """Tune parameters specifically for an environment type."""
        print(f"\nTuning parameters for {environment_type} environment...")
        
        # Use environment-specific parameter ranges
        old_ranges = self.param_ranges
        self.param_ranges = self.environment_ranges[environment_type]
        
        # Track environment-specific best parameters
        env_best_params = None
        env_best_failures = float('inf')
        
        for iteration in range(max_iterations):
            try:
                print(f"Iteration {iteration}: ", end='')
                
                # Generate random parameters within environment-specific ranges
                current_params = {
                    param: random.uniform(range_min, range_max)
                    for param, (range_min, range_max) in self.param_ranges.items()
                }
                
                # Run environment-specific tests
                failures = []
                for test in ['test_environment_resource_availability',
                           'test_environment_carrying_capacity',
                           'test_environment_mortality_patterns']:
                    if not run_test(test, current_params):
                        failures.append(test)
                
                # Update if this is the best so far for this environment
                if len(failures) < env_best_failures:
                    env_best_failures = len(failures)
                    env_best_params = current_params
                    print(f"\nNew best parameters for {environment_type} environment with {len(failures)} failing tests:")
                    for param, value in current_params.items():
                        print(f"  {param}: {value}")
                    print("\nFailing tests:", failures)
                else:
                    print(f"{len(failures)} failing tests")
                
            except Exception as e:
                print(f"\nError in iteration {iteration}: {str(e)}")
                traceback.print_exc()
                continue
        
        # Restore original parameter ranges
        self.param_ranges = old_ranges
        return env_best_params, env_best_failures

if __name__ == '__main__':
    tuner = ParameterTuner()
    
    # Tune parameters for each environment type
    for env_type in ['urban', 'suburban', 'rural']:
        best_params, failures = tuner.tune_environment(env_type)
        
        print(f"\nFinal best parameters for {env_type} environment:")
        for param, value in best_params.items():
            print(f"  {param}: {value}")
        print(f"Number of failing tests: {failures}")
        
    # Run general parameter tuning
    tuner.tune()
