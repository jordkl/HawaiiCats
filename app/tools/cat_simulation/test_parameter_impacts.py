import unittest
import numpy as np
from simulation import simulatePopulation, calculateCarryingCapacity, calculateResourceAvailability
from statistics import mean, stdev
from scipy import stats
import logging
import time
from typing import Dict, List, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

def run_single_simulation(params: Dict[str, Any], initial_pop: int, months: int) -> Dict[str, Any]:
    """Run a single simulation with given parameters"""
    try:
        result = simulatePopulation(params, initial_pop, months)
        # Convert simulation output to expected format
        return {
            'peak_population': max(m['total'] for m in result['monthlyData']),
            'final_population': result['monthlyData'][-1]['total'],
            'total_births': result['totalBirths'],
            'urban_deaths': result['urbanDeaths'],
            'disease_deaths': result['diseaseDeaths'],
            'natural_deaths': result['naturalDeaths']
        }
    except Exception as e:
        logging.error(f"Simulation failed with params {params}: {str(e)}")
        raise

class TestParameterImpacts(unittest.TestCase):
    def setUp(self):
        """Set up baseline parameters for tests"""
        self.base_params = {
            'territorySize': 1000,
            'densityThreshold': 1.2,
            'baseFoodCapacity': 0.8,
            'waterAvailability': 0.8,
            'shelterQuality': 0.7,
            'caretakerSupport': 0.5,
            'feedingConsistency': 0.7,
            'urbanization_impact': 0.2,
            'disease_transmission_rate': 0.1,
            'environmental_stress': 0.15,
            'adult_survival_rate': 0.85,
            'kitten_survival_rate': 0.7,
            'peakBreedingMonth': 4,
            'seasonalBreedingAmplitude': 0.4
        }
        self.simulation_months = 24  # Run for 2 years
        self.initial_population = 50
        self.num_iterations = 20  # Increased for better statistical significance
        self.confidence_level = 0.95  # For confidence intervals

    def calculate_statistics(self, results: List[Dict[str, Any]], metric: str) -> Dict[str, float]:
        """Calculate comprehensive statistics for a metric"""
        values = [r[metric] for r in results]
        
        mean_val = np.mean(values)
        std_val = np.std(values, ddof=1)
        ci = stats.t.interval(self.confidence_level, len(values)-1,
                            loc=mean_val,
                            scale=stats.sem(values))
        
        return {
            'mean': mean_val,
            'std': std_val,
            'ci_lower': ci[0],
            'ci_upper': ci[1],
            'min': min(values),
            'max': max(values)
        }

    def run_multiple_simulations(self, params: Dict[str, Any], description: str) -> Tuple[Dict[str, Dict[str, float]], float]:
        """Run multiple simulations and return comprehensive statistics"""
        start_time = time.time()
        
        try:
            results = [run_single_simulation(params, self.initial_population, self.simulation_months) 
                      for _ in range(self.num_iterations)]
        except Exception as e:
            logging.error(f"Failed to run simulations for {description}: {str(e)}")
            raise

        metrics = ['peak_population', 'final_population', 'total_births', 
                  'urban_deaths', 'disease_deaths', 'natural_deaths']
        
        stats_results = {metric: self.calculate_statistics(results, metric)
                        for metric in metrics}
        
        execution_time = time.time() - start_time
        
        # Log detailed results
        logging.info(f"\nTest Results for {description} "
                    f"(averaged over {self.num_iterations} runs, {execution_time:.2f}s):")
        for metric, stats in stats_results.items():
            logging.info(f"{metric}: {stats['mean']:.1f} ± {stats['std']:.1f} "
                        f"(95% CI: [{stats['ci_lower']:.1f}, {stats['ci_upper']:.1f}])")
        
        return stats_results, execution_time

    def assert_significant_impact(self, results: List[Tuple[float, Dict[str, Dict[str, float]]]], 
                                metric: str, min_ratio: float = 1.5, 
                                confidence_level: float = 0.95) -> None:
        """Assert that parameter impact is statistically significant"""
        values = [(value, stats[metric]['mean'], stats[metric]['std']) 
                 for value, stats in results]
        
        # Perform t-test between min and max results
        min_result = min(values, key=lambda x: x[1])
        max_result = max(values, key=lambda x: x[1])
        
        t_stat, p_value = stats.ttest_ind_from_stats(
            mean1=min_result[1], std1=min_result[2], nobs1=self.num_iterations,
            mean2=max_result[1], std2=max_result[2], nobs2=self.num_iterations
        )
        
        impact_ratio = max_result[1] / min_result[1] if min_result[1] > 0 else float('inf')
        
        self.assertGreater(impact_ratio, min_ratio,
                          f"Impact ratio {impact_ratio:.2f} not greater than {min_ratio}")
        self.assertLess(p_value, 1 - confidence_level,
                       f"Impact not statistically significant (p={p_value:.3f})")

    def test_basic_parameters(self):
        """Test impact of basic parameters"""
        # Test territory size impact
        logging.info("\nTesting territorySize impact:")
        territory_sizes = [50, 500, 2000, 10000, 100000]  # More extreme range
        results = []
        for size in territory_sizes:
            params = self.base_params.copy()
            params['territorySize'] = size
            stats, _ = self.run_multiple_simulations(params, f"territorySize={size}")
            results.append((size, stats))
        
        # Territory size should significantly affect peak population
        self.assert_significant_impact(results, 'peak_population', min_ratio=1.2)

        # Test density threshold impact
        logging.info("\nTesting densityThreshold impact:")
        density_thresholds = [0.5, 1.0, 2.0, 4.0, 8.0]  # Wider range
        results = []
        for threshold in density_thresholds:
            params = self.base_params.copy()
            params['densityThreshold'] = threshold
            stats, _ = self.run_multiple_simulations(params, f"densityThreshold={threshold}")
            results.append((threshold, stats))
        
        # Density threshold should affect peak population
        self.assert_significant_impact(results, 'peak_population', min_ratio=1.2)

        # Test food capacity impact
        logging.info("\nTesting baseFoodCapacity impact:")
        food_capacities = [0.2, 0.4, 0.8, 1.6, 3.2]  # Wider range
        results = []
        for capacity in food_capacities:
            params = self.base_params.copy()
            params['baseFoodCapacity'] = capacity
            stats, _ = self.run_multiple_simulations(params, f"baseFoodCapacity={capacity}")
            results.append((capacity, stats))
        
        # Food capacity should affect peak population
        self.assert_significant_impact(results, 'peak_population', min_ratio=1.2)

    def test_advanced_parameters(self):
        """Test impact of advanced parameters"""
        # Test urbanization impact
        logging.info("\nTesting urbanization_impact impact:")
        urbanization_impacts = [0.01, 0.05, 0.1, 0.2, 0.4, 0.8]
        results = []
        for impact in urbanization_impacts:
            params = self.base_params.copy()
            params['urbanization_impact'] = impact
            stats, _ = self.run_multiple_simulations(params, f"urbanization_impact={impact}")
            results.append((impact, stats))
        
        # Urbanization should affect urban deaths and peak population
        self.assert_significant_impact(results, 'urban_deaths', min_ratio=1.2)
        self.assert_significant_impact(results, 'peak_population', min_ratio=1.2)

        # Test disease transmission rate impact
        logging.info("\nTesting disease_transmission_rate impact:")
        disease_rates = [0.01, 0.05, 0.1, 0.2, 0.4, 0.8]
        results = []
        for rate in disease_rates:
            params = self.base_params.copy()
            params['disease_transmission_rate'] = rate
            stats, _ = self.run_multiple_simulations(params, f"disease_transmission_rate={rate}")
            results.append((rate, stats))
        
        # Disease rate should affect disease deaths and peak population
        self.assert_significant_impact(results, 'disease_deaths', min_ratio=1.2)
        self.assert_significant_impact(results, 'peak_population', min_ratio=1.2)

        # Test environmental stress impact
        logging.info("\nTesting environmental_stress impact:")
        stress_levels = [0.01, 0.1, 0.4, 0.7, 0.9, 0.99]  # More extreme range
        results = []
        for stress in stress_levels:
            params = self.base_params.copy()
            params['environmental_stress'] = stress
            stats, _ = self.run_multiple_simulations(params, f"environmental_stress={stress}")
            results.append((stress, stats))
        
        # Environmental stress should affect natural deaths
        self.assert_significant_impact(results, 'natural_deaths', min_ratio=1.1)

    def test_parameter_interactions(self):
        """Test interactions between related parameters"""
        # Test resource quality interaction (food + water + shelter)
        poor_resources = self.base_params.copy()
        poor_resources.update({
            'baseFoodCapacity': 0.1,  # Even lower values
            'waterAvailability': 0.1,
            'shelterQuality': 0.1,
            'caretakerSupport': 0.1,
            'feedingConsistency': 0.1
        })
        
        good_resources = self.base_params.copy()
        good_resources.update({
            'baseFoodCapacity': 3.0,  # Even higher values
            'waterAvailability': 1.0,
            'shelterQuality': 1.0,
            'caretakerSupport': 1.0,
            'feedingConsistency': 1.0
        })
        
        poor_results, _ = self.run_multiple_simulations(poor_resources, "Poor Resources")
        good_results, _ = self.run_multiple_simulations(good_resources, "Good Resources")
        
        # Resource quality should have a strong impact on peak population
        poor_peak = poor_results['peak_population']['mean']
        good_peak = good_results['peak_population']['mean']
        ratio = 1.5  # Expected minimum ratio between good and poor resource outcomes
        actual_ratio = good_peak / poor_peak if poor_peak > 0 else float('inf')
        
        self.assertGreater(actual_ratio, ratio,
                          f"Resource quality impact on peak_population insufficient "
                          f"(expected ratio > {ratio}, got {actual_ratio:.2f})")

    def test_population_dynamics(self):
        """Test impact of population dynamics parameters"""
        # Test breeding rate impact
        logging.info("\nTesting breeding_rate impact:")
        breeding_rates = [0.3, 0.5, 0.7, 0.85, 0.95]
        results = []
        for rate in breeding_rates:
            params = self.base_params.copy()
            params['breeding_rate'] = rate
            stats, _ = self.run_multiple_simulations(params, f"breeding_rate={rate}")
            results.append((rate, stats))
        
        self.assert_significant_impact(results, 'total_births', min_ratio=1.2)
        self.assert_significant_impact(results, 'peak_population', min_ratio=1.2)

        # Test kittens per litter impact
        logging.info("\nTesting kittens_per_litter impact:")
        kittens_per_litter = [2, 3, 4, 5, 6]
        results = []
        for kittens in kittens_per_litter:
            params = self.base_params.copy()
            params['kittens_per_litter'] = kittens
            stats, _ = self.run_multiple_simulations(params, f"kittens_per_litter={kittens}")
            results.append((kittens, stats))
        
        self.assert_significant_impact(results, 'total_births', min_ratio=1.2)
        self.assert_significant_impact(results, 'peak_population', min_ratio=1.2)

        # Test litters per year impact
        logging.info("\nTesting litters_per_year impact:")
        litters_per_year = [1.5, 2.0, 2.5, 3.0, 3.5]
        results = []
        for litters in litters_per_year:
            params = self.base_params.copy()
            params['litters_per_year'] = litters
            stats, _ = self.run_multiple_simulations(params, f"litters_per_year={litters}")
            results.append((litters, stats))
        
        self.assert_significant_impact(results, 'total_births', min_ratio=1.2)
        self.assert_significant_impact(results, 'peak_population', min_ratio=1.2)

    def test_seasonal_factors(self):
        """Test impact of seasonal factors"""
        # Test seasonality strength impact
        logging.info("\nTesting seasonality_strength impact:")
        seasonality_strengths = [0.1, 0.3, 0.5, 0.7, 0.9]
        results = []
        for strength in seasonality_strengths:
            params = self.base_params.copy()
            params['seasonality_strength'] = strength
            stats, _ = self.run_multiple_simulations(params, f"seasonality_strength={strength}")
            results.append((strength, stats))
        
        self.assert_significant_impact(results, 'total_births', min_ratio=1.2)

    def test_resource_factors(self):
        """Test impact of resource competition and scarcity"""
        # Test resource competition impact
        logging.info("\nTesting resource_competition impact:")
        competition_levels = [0.1, 0.2, 0.4, 0.6, 0.8]
        results = []
        for level in competition_levels:
            params = self.base_params.copy()
            params['resource_competition'] = level
            stats, _ = self.run_multiple_simulations(params, f"resource_competition={level}")
            results.append((level, stats))
        
        self.assert_significant_impact(results, 'peak_population', min_ratio=1.2)
        self.assert_significant_impact(results, 'natural_deaths', min_ratio=1.2)

        # Test resource scarcity impact
        logging.info("\nTesting resource_scarcity_impact:")
        scarcity_impacts = [0.1, 0.25, 0.4, 0.6, 0.8]
        results = []
        for impact in scarcity_impacts:
            params = self.base_params.copy()
            params['resource_scarcity_impact'] = impact
            stats, _ = self.run_multiple_simulations(params, f"resource_scarcity_impact={impact}")
            results.append((impact, stats))
        
        self.assert_significant_impact(results, 'peak_population', min_ratio=1.2)
        self.assert_significant_impact(results, 'natural_deaths', min_ratio=1.2)

    def test_density_factors(self):
        """Test impact of density-related factors"""
        # Test density stress rate impact
        logging.info("\nTesting density_stress_rate impact:")
        stress_rates = [0.05, 0.15, 0.3, 0.5, 0.7]
        results = []
        for rate in stress_rates:
            params = self.base_params.copy()
            params['density_stress_rate'] = rate
            stats, _ = self.run_multiple_simulations(params, f"density_stress_rate={rate}")
            results.append((rate, stats))
        
        self.assert_significant_impact(results, 'natural_deaths', min_ratio=1.2)

        # Test max density impact
        logging.info("\nTesting max_density_impact:")
        max_impacts = [0.2, 0.4, 0.6, 0.8, 0.95]
        results = []
        for impact in max_impacts:
            params = self.base_params.copy()
            params['max_density_impact'] = impact
            stats, _ = self.run_multiple_simulations(params, f"max_density_impact={impact}")
            results.append((impact, stats))
        
        self.assert_significant_impact(results, 'peak_population', min_ratio=1.2)
        self.assert_significant_impact(results, 'natural_deaths', min_ratio=1.2)

    def test_habitat_quality(self):
        """Test impact of base habitat quality"""
        logging.info("\nTesting base_habitat_quality:")
        quality_levels = [0.2, 0.4, 0.6, 0.8, 0.95]
        results = []
        for quality in quality_levels:
            params = self.base_params.copy()
            params['base_habitat_quality'] = quality
            stats, _ = self.run_multiple_simulations(params, f"base_habitat_quality={quality}")
            results.append((quality, stats))
        
        self.assert_significant_impact(results, 'peak_population', min_ratio=1.2)
        self.assert_significant_impact(results, 'natural_deaths', min_ratio=1.2)

class TestEnvironmentPresets(unittest.TestCase):
    """Test suite for validating environment preset parameters and their impacts."""
    
    def setUp(self):
        """Set up baseline parameters for environment tests"""
        self.base_params = {
            'territorySize': 1000,
            'densityThreshold': 1.2,
            'baseFoodCapacity': 0.8,
            'waterAvailability': 0.8,
            'shelterQuality': 0.7,
            'caretakerSupport': 0.5,
            'feedingConsistency': 0.7,
            'urbanization_impact': 0.2,
            'disease_transmission_rate': 0.1,
            'environmental_stress': 0.15,
            'adult_survival_rate': 0.85,
            'kitten_survival_rate': 0.7
        }
        
        # Define environment presets with expected characteristics
        self.environment_presets = {
            'urban': {
                'params': {
                    'baseFoodCapacity': 0.6,
                    'waterAvailability': 0.5,
                    'shelterQuality': 0.4,
                    'caretakerSupport': 0.3,
                    'feedingConsistency': 0.4,
                    'urbanization_impact': 0.8,
                    'disease_transmission_rate': 0.3,
                    'environmental_stress': 0.7
                },
                'expected': {
                    'resource_range': (0.3, 0.5),  # Expected resource availability range
                    'mortality_types': {
                        'urban': (0.4, 0.6),       # Expected proportion of urban deaths
                        'disease': (0.2, 0.4),     # Expected proportion of disease deaths
                        'natural': (0.1, 0.3)      # Expected proportion of natural deaths
                    },
                    'carrying_capacity_range': (100, 300)  # Expected carrying capacity range
                }
            },
            'forest': {
                'params': {
                    'baseFoodCapacity': 0.7,
                    'waterAvailability': 0.8,
                    'shelterQuality': 0.8,
                    'caretakerSupport': 0.1,
                    'feedingConsistency': 0.2,
                    'urbanization_impact': 0.1,
                    'disease_transmission_rate': 0.2,
                    'environmental_stress': 0.3
                },
                'expected': {
                    'resource_range': (0.6, 0.8),
                    'mortality_types': {
                        'urban': (0.05, 0.15),
                        'disease': (0.15, 0.35),
                        'natural': (0.5, 0.7)
                    },
                    'carrying_capacity_range': (400, 600)
                }
            },
            'beach': {
                'params': {
                    'baseFoodCapacity': 0.5,
                    'waterAvailability': 0.9,
                    'shelterQuality': 0.5,
                    'caretakerSupport': 0.2,
                    'feedingConsistency': 0.3,
                    'urbanization_impact': 0.3,
                    'disease_transmission_rate': 0.15,
                    'environmental_stress': 0.4
                },
                'expected': {
                    'resource_range': (0.4, 0.6),
                    'mortality_types': {
                        'urban': (0.2, 0.4),
                        'disease': (0.1, 0.3),
                        'natural': (0.4, 0.6)
                    },
                    'carrying_capacity_range': (200, 400)
                }
            },
            'residential': {
                'params': {
                    'baseFoodCapacity': 0.7,
                    'waterAvailability': 0.6,
                    'shelterQuality': 0.6,
                    'caretakerSupport': 0.7,
                    'feedingConsistency': 0.8,
                    'urbanization_impact': 0.4,
                    'disease_transmission_rate': 0.2,
                    'environmental_stress': 0.3
                },
                'expected': {
                    'resource_range': (0.6, 0.8),
                    'mortality_types': {
                        'urban': (0.2, 0.4),
                        'disease': (0.15, 0.35),
                        'natural': (0.3, 0.5)
                    },
                    'carrying_capacity_range': (300, 500)
                }
            }
        }
        
        self.simulation_months = 24
        self.initial_population = 50
        self.num_iterations = 10

    def test_environment_resource_availability(self):
        """Test that each environment has appropriate resource availability."""
        for env_name, env_data in self.environment_presets.items():
            params = self.base_params.copy()
            params.update(env_data['params'])
            
            resource_availability = calculateResourceAvailability(
                params['baseFoodCapacity'],
                params['waterAvailability'],
                params['shelterQuality'],
                params['caretakerSupport'],
                params['feedingConsistency']
            )
            
            expected_min, expected_max = env_data['expected']['resource_range']
            self.assertGreaterEqual(
                resource_availability, expected_min,
                f"{env_name} environment: Resource availability {resource_availability} below expected minimum {expected_min}"
            )
            self.assertLessEqual(
                resource_availability, expected_max,
                f"{env_name} environment: Resource availability {resource_availability} above expected maximum {expected_max}"
            )

    def test_environment_carrying_capacity(self):
        """Test that each environment supports appropriate carrying capacity."""
        for env_name, env_data in self.environment_presets.items():
            params = self.base_params.copy()
            params.update(env_data['params'])
            
            # Calculate resource factor first
            resource_factor = calculateResourceAvailability(
                params['baseFoodCapacity'],
                params['waterAvailability'],
                params['shelterQuality'],
                params['caretakerSupport'],
                params['feedingConsistency']
            )
            
            carrying_capacity = calculateCarryingCapacity(
                params['territorySize'],
                params['densityThreshold'],
                resource_factor
            )
            
            expected_min, expected_max = env_data['expected']['carrying_capacity_range']
            self.assertGreaterEqual(
                carrying_capacity, expected_min,
                f"{env_name} environment: Carrying capacity {carrying_capacity} below expected minimum {expected_min}"
            )
            self.assertLessEqual(
                carrying_capacity, expected_max,
                f"{env_name} environment: Carrying capacity {carrying_capacity} above expected maximum {expected_max}"
            )

    def test_environment_mortality_patterns(self):
        """Test that each environment shows expected patterns of mortality."""
        for env_name, env_data in self.environment_presets.items():
            params = self.base_params.copy()
            params.update(env_data['params'])
            
            # Run multiple simulations to get average mortality patterns
            total_deaths = {'urban': 0, 'disease': 0, 'natural': 0}
            
            for _ in range(self.num_iterations):
                result = simulatePopulation(params, self.initial_population, self.simulation_months)
                total_deaths['urban'] += result['urbanDeaths']
                total_deaths['disease'] += result['diseaseDeaths']
                total_deaths['natural'] += result['naturalDeaths']
            
            # Calculate proportions
            total_all_deaths = sum(total_deaths.values())
            if total_all_deaths > 0:
                death_proportions = {
                    cause: deaths / total_all_deaths
                    for cause, deaths in total_deaths.items()
                }
                
                # Check each mortality type is within expected range
                for cause, (expected_min, expected_max) in env_data['expected']['mortality_types'].items():
                    proportion = death_proportions[cause]
                    self.assertGreaterEqual(
                        proportion, expected_min,
                        f"{env_name} environment: {cause} death proportion {proportion:.2f} below expected minimum {expected_min}"
                    )
                    self.assertLessEqual(
                        proportion, expected_max,
                        f"{env_name} environment: {cause} death proportion {proportion:.2f} above expected maximum {expected_max}"
                    )

if __name__ == '__main__':
    unittest.main()
