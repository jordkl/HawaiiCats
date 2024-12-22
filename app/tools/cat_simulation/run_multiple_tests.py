import unittest
import sys
import statistics
from test_biological_factors import TestBiologicalFactors
from test_simulation import TestCatSimulation
from test_sterilization import TestSterilization

def run_test_multiple_times(test_case, test_method_name, iterations=10):
    """Run a specific test multiple times and collect results."""
    results = []
    for i in range(iterations):
        suite = unittest.TestSuite()
        test = test_case(test_method_name)
        suite.addTest(test)
        
        runner = unittest.TextTestRunner(stream=None)
        result = runner.run(suite)
        
        results.append(result.wasSuccessful())
    
    success_rate = (sum(results) / len(results)) * 100
    return success_rate

def main():
    # Test cases to run
    test_cases = [
        (TestBiologicalFactors, [
            'test_breeding_rate_extremes',
            'test_carrying_capacity_convergence',
            'test_density_dependent_mortality',
            'test_kitten_mortality_factors',
            'test_litter_size_distribution',
            'test_resource_competition',
            'test_seasonal_breeding_intensity',
            'test_severe_scenarios'
        ]),
        (TestCatSimulation, [
            'testBreedingRateExtremes',
            'testCarryingCapacityConvergence',
            'testDensityDependentEffects',
            'testEnvironmentalFactors',
            'testNoSterilization',
            'testResourceCompetition',
            'testSeasonalBreeding'
        ]),
        (TestSterilization, [
            'test_full_initial_sterilization',
            'test_gradual_sterilization',
            'test_mixed_sterilization',
            'test_no_sterilization'
        ])
    ]

    iterations = 10
    print(f"\nRunning each test {iterations} times...")
    
    for test_case, test_methods in test_cases:
        print(f"\n{test_case.__name__}:")
        for test_method in test_methods:
            success_rate = run_test_multiple_times(test_case, test_method, iterations)
            print(f"{test_method}: {success_rate:.1f}% success rate")

if __name__ == '__main__':
    main()
