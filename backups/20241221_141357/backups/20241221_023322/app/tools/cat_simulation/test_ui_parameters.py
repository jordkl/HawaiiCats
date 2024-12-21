"""Test script to verify UI parameter effects on population growth."""
import unittest
from tools.cat_simulation.constants import DEFAULT_PARAMS
from tools.cat_simulation.simulation import simulate_population
from tools.cat_simulation.utils.test_logging_utils import setup_test_logging, log_test_result
import numpy as np

class TestUIParameterEffects(unittest.TestCase):
    def setUp(self):
        """Set up base test parameters."""
        # Set up logging for tests
        from tools.cat_simulation.utils.logging_utils import setup_logging
        setup_logging()
        
        self.base_params = {
            'initial_population': 50,
            'simulation_months': 24,
            'initial_sterilized': 0,
            'breeding_rate': 0.85,
            'kittens_per_litter': 4,
            'litters_per_year': 2.5,
            'kitten_survival_rate': 0.75,
            'adult_survival_rate': 0.85,
            'monthly_sterilization_rate': 0,
            'base_food_capacity': 0.95,
            'territory_size': 10000,
            'density_impact_threshold': 1.0,
            'urban_mortality_rate': 0.08,
            'disease_mortality_rate': 0.04,
            'environmental_stress': 0.1,
            'seasonal_breeding_amplitude': 0.15,
            'peak_breeding_month': 3,
            'female_ratio': 0.5,  
            'kitten_maturity_months': 5,  
            'food_scaling_factor': 0.9,  
            'water_availability': 0.95,  
            'shelter_quality': 0.85,  
            'caretaker_support': 1.0,  
            'feeding_consistency': 0.95  
        }
        self.base_colony_size = 50
        self.months = 24
        self.sterilized_count = 0
        self.monthly_sterilization = 0
        self.logger = setup_test_logging()

    def simulate_with_params(self, params, num_runs=10):
        """Run multiple simulations with given parameters and return mean results."""
        results = []
        for _ in range(num_runs):
            result = simulate_population(
                params=params,
                current_size=self.base_colony_size,
                months=self.months,
                sterilized_count=self.sterilized_count,
                monthly_sterilization=self.monthly_sterilization
            )
            results.append(result)
        
        # Calculate mean values
        mean_result = {
            'final_population': sum(r['final_population'] for r in results) / num_runs,
            'final_sterilized': sum(r['final_sterilized'] for r in results) / num_runs,
            'total_deaths': sum(r['total_deaths'] for r in results) / num_runs,
            'monthly_populations': [
                sum(r['monthly_populations'][i] for r in results) / num_runs
                for i in range(len(results[0]['monthly_populations']))
            ]
        }
        
        # Log the individual results for analysis
        self.logger.info(f"Individual runs: {[r['final_population'] for r in results]}")
        self.logger.info(f"Mean result: {mean_result['final_population']:.1f}")
        self.logger.info(f"Standard deviation: {np.std([r['final_population'] for r in results]):.1f}")
        
        return mean_result

    def test_survival_rates_effect(self):
        """Test that higher survival rates lead to larger population."""
        num_runs = 20  # More runs for better statistical significance
        
        # Run with low survival rates
        low_survival_params = self.base_params.copy()
        low_survival_params['kitten_survival_rate'] = 0.3
        low_survival_params['adult_survival_rate'] = 0.5
        low_result = self.simulate_with_params(low_survival_params, num_runs)
        
        # Run with high survival rates
        high_survival_params = self.base_params.copy()
        high_survival_params['kitten_survival_rate'] = 0.9
        high_survival_params['adult_survival_rate'] = 0.95
        high_result = self.simulate_with_params(high_survival_params, num_runs)
        
        self.assertGreater(
            high_result['final_population'],
            low_result['final_population'],
            f"Higher survival rates should result in larger final population. "
            f"High: {high_result['final_population']:.1f}, Low: {low_result['final_population']:.1f}"
        )

    def test_breeding_rate_effect(self):
        """Test that higher breeding rate leads to faster population growth."""
        num_runs = 20
        
        # Run with low breeding rate
        low_breeding_params = self.base_params.copy()
        low_breeding_params['breeding_rate'] = 0.4
        low_result = self.simulate_with_params(low_breeding_params, num_runs)
        
        # Run with high breeding rate
        high_breeding_params = self.base_params.copy()
        high_breeding_params['breeding_rate'] = 0.9
        high_result = self.simulate_with_params(high_breeding_params, num_runs)
        
        self.assertGreater(
            high_result['final_population'],
            low_result['final_population'],
            f"Higher breeding rate should result in larger population. "
            f"High: {high_result['final_population']:.1f}, Low: {low_result['final_population']:.1f}"
        )

    def test_territory_size_effect(self):
        """Test that larger territory size supports larger population."""
        num_runs = 20
        
        # Run with small territory (0.5 hectares = 5000 sq meters)
        small_territory_params = self.base_params.copy()
        small_territory_params.update({
            'territory_size': 5000,
            'breeding_rate': 0.6,  # Use moderate breeding rate
            'density_impact_threshold': 2.0  # Higher threshold to reduce density effects
        })
        small_result = self.simulate_with_params(small_territory_params, num_runs)
        
        # Run with large territory (2 hectares = 20000 sq meters)
        large_territory_params = self.base_params.copy()
        large_territory_params.update({
            'territory_size': 20000,
            'breeding_rate': 0.6,  # Same breeding rate
            'density_impact_threshold': 2.0  # Same threshold
        })
        large_result = self.simulate_with_params(large_territory_params, num_runs)
        
        self.assertGreater(
            large_result['final_population'],
            small_result['final_population'],
            f"Larger territory should support larger final population. "
            f"Large: {large_result['final_population']:.1f}, Small: {small_result['final_population']:.1f}"
        )

    def test_density_impact_threshold_effect(self):
        """Test that higher density impact threshold allows larger population."""
        num_runs = 20
        
        # Run with low density threshold
        low_density_params = self.base_params.copy()
        low_density_params['density_impact_threshold'] = 0.5
        low_result = self.simulate_with_params(low_density_params, num_runs)
        
        # Run with high density threshold
        high_density_params = self.base_params.copy()
        high_density_params['density_impact_threshold'] = 1.5
        high_result = self.simulate_with_params(high_density_params, num_runs)
        
        self.assertGreater(
            high_result['final_population'],
            low_result['final_population'],
            f"Higher density threshold should allow larger final population. "
            f"High: {high_result['final_population']:.1f}, Low: {low_result['final_population']:.1f}"
        )

    def test_disease_impact_effect(self):
        """Test that disease impact affects population growth."""
        num_runs = 20
        
        # Run with low disease impact
        low_disease_params = self.base_params.copy()
        low_disease_params.update({
            'disease_mortality_rate': 0.05,
            'territory_size': 20000,
            'density_impact_threshold': 3.0
        })
        low_result = self.simulate_with_params(low_disease_params, num_runs)
        
        # Run with high disease impact
        high_disease_params = self.base_params.copy()
        high_disease_params.update({
            'disease_mortality_rate': 0.2,
            'territory_size': 20000,
            'density_impact_threshold': 3.0
        })
        high_result = self.simulate_with_params(high_disease_params, num_runs)
        
        self.assertGreater(
            low_result['final_population'],
            high_result['final_population'],
            f"Higher disease mortality should result in smaller population. "
            f"Low disease: {low_result['final_population']:.1f}, High disease: {high_result['final_population']:.1f}"
        )
        self.assertGreater(
            high_result['total_deaths'],
            low_result['total_deaths'],
            f"Higher disease rate should result in more deaths. "
            f"High disease deaths: {high_result['total_deaths']:.1f}, Low disease deaths: {low_result['total_deaths']:.1f}"
        )

    def test_food_capacity_effect(self):
        """Test that food capacity affects population growth."""
        num_runs = 20
        
        # Run with high food capacity
        high_food_params = self.base_params.copy()
        high_food_params.update({
            'base_food_capacity': 1.0,
            'territory_size': 20000,
            'density_impact_threshold': 3.0
        })
        high_result = self.simulate_with_params(high_food_params, num_runs)
        
        # Run with low food capacity
        low_food_params = self.base_params.copy()
        low_food_params.update({
            'base_food_capacity': 0.5,
            'territory_size': 20000,
            'density_impact_threshold': 3.0
        })
        low_result = self.simulate_with_params(low_food_params, num_runs)
        
        self.assertGreater(
            high_result['final_population'],
            low_result['final_population'],
            f"Higher food capacity should support larger population. "
            f"High food: {high_result['final_population']:.1f}, Low food: {low_result['final_population']:.1f}"
        )

    def test_kitten_mortality_effect(self):
        """Test that kitten mortality has significant impact on population growth."""
        num_runs = 20
        
        # Run with high kitten survival
        high_survival_params = self.base_params.copy()
        high_survival_params.update({
            'kitten_survival_rate': 0.9,
            'territory_size': 20000,
            'density_impact_threshold': 3.0,
            'base_food_capacity': 1.0
        })
        high_result = self.simulate_with_params(high_survival_params, num_runs)
        
        # Run with low kitten survival
        low_survival_params = self.base_params.copy()
        low_survival_params.update({
            'kitten_survival_rate': 0.4,
            'territory_size': 20000,
            'density_impact_threshold': 3.0,
            'base_food_capacity': 1.0
        })
        low_result = self.simulate_with_params(low_survival_params, num_runs)
        
        self.assertGreater(
            high_result['final_population'],
            low_result['final_population'] * 1.5,  # Should be significantly higher
            f"Higher kitten survival should lead to much larger population. "
            f"High survival: {high_result['final_population']:.1f}, Low survival * 1.5: {low_result['final_population'] * 1.5:.1f}"
        )

    def test_litters_per_year_effect(self):
        """Test that more litters per year leads to faster population growth."""
        num_runs = 20
        
        # Run with fewer litters
        low_litter_params = self.base_params.copy()
        low_litter_params.update({
            'litters_per_year': 1.5,
            'territory_size': 50000,  # Large territory
            'density_impact_threshold': 5.0,  # High threshold
            'base_food_capacity': 1.0
        })
        low_result = self.simulate_with_params(low_litter_params, num_runs)
        
        # Run with more litters
        high_litter_params = self.base_params.copy()
        high_litter_params.update({
            'litters_per_year': 3.0,
            'territory_size': 50000,
            'density_impact_threshold': 5.0,
            'base_food_capacity': 1.0
        })
        high_result = self.simulate_with_params(high_litter_params, num_runs)
        
        self.assertGreater(
            high_result['final_population'],
            low_result['final_population'],
            f"More litters per year should result in larger population. "
            f"High litters: {high_result['final_population']:.1f}, Low litters: {low_result['final_population']:.1f}"
        )

    def test_sterilization_effect(self):
        """Test that higher sterilization rate reduces population growth."""
        num_runs = 20
        
        # Run with no sterilization
        self.sterilized_count = 0
        self.monthly_sterilization = 0
        no_sterilization_params = self.base_params.copy()
        no_sterilization_params.update({
            'territory_size': 20000,  # Large territory
            'density_impact_threshold': 3.0,  # Higher threshold
            'base_food_capacity': 1.0  # Maximum food capacity
        })
        no_sterilization_result = self.simulate_with_params(no_sterilization_params, num_runs)

        # Run with active sterilization program
        self.sterilized_count = 10  # Start with some sterilized cats
        self.monthly_sterilization = 5  # Sterilize 5 cats per month
        with_sterilization_params = self.base_params.copy()
        with_sterilization_params.update({
            'territory_size': 20000,  # Same territory size
            'density_impact_threshold': 3.0,  # Same threshold
            'base_food_capacity': 1.0  # Maximum food capacity
        })
        with_sterilization_result = self.simulate_with_params(with_sterilization_params, num_runs)

        self.assertGreater(
            no_sterilization_result['final_population'],
            with_sterilization_result['final_population'],
            f"Sterilization should reduce population growth. "
            f"No sterilization: {no_sterilization_result['final_population']:.1f}, With sterilization: {with_sterilization_result['final_population']:.1f}"
        )

    def test_monthly_population_curve(self):
        """Test that monthly population data shows expected growth pattern."""
        num_runs = 20
        result = self.simulate_with_params(self.base_params, num_runs)

        # Check that monthly data exists and has correct length
        self.assertIsNotNone(result['monthly_populations'])
        self.assertEqual(
            len(result['monthly_populations']),
            self.months + 1,  # +1 because it includes initial population
            "Monthly population data should match simulation months"
        )

        # Check that population generally increases (allowing for some fluctuation)
        initial_pop = result['monthly_populations'][0]
        final_pop = result['monthly_populations'][-1]
        self.assertGreater(
            final_pop,
            initial_pop,
            f"Population should generally increase over time with default parameters. "
            f"Initial: {initial_pop:.1f}, Final: {final_pop:.1f}"
        )

    def test_environmental_stress_effect(self):
        """Test that environmental stress affects population growth."""
        num_runs = 20
        
        # Run with low environmental stress
        low_stress_params = self.base_params.copy()
        low_stress_params.update({
            'environmental_stress': 0.1,
            'territory_size': 20000,
            'density_impact_threshold': 3.0
        })
        low_result = self.simulate_with_params(low_stress_params, num_runs)

        # Run with high environmental stress
        high_stress_params = self.base_params.copy()
        high_stress_params.update({
            'environmental_stress': 0.4,
            'territory_size': 20000,
            'density_impact_threshold': 3.0
        })
        high_result = self.simulate_with_params(high_stress_params, num_runs)

        self.assertGreater(
            low_result['final_population'],
            high_result['final_population'],
            f"Higher environmental stress should result in smaller population. "
            f"Low stress: {low_result['final_population']:.1f}, High stress: {high_result['final_population']:.1f}"
        )

    def test_age_specific_mortality(self):
        """Test that age-specific mortality rates affect population structure."""
        num_runs = 20
        
        # Run with balanced mortality rates
        balanced_params = self.base_params.copy()
        balanced_params.update({
            'kitten_mortality_rate': 0.2,
            'adult_mortality_rate': 0.2,
            'senior_mortality_rate': 0.3,
            'territory_size': 20000
        })
        balanced_result = self.simulate_with_params(balanced_params, num_runs)

        # Run with higher adult mortality
        high_adult_mortality_params = self.base_params.copy()
        high_adult_mortality_params.update({
            'kitten_mortality_rate': 0.2,
            'adult_mortality_rate': 0.4,
            'senior_mortality_rate': 0.3,
            'territory_size': 20000
        })
        high_mortality_result = self.simulate_with_params(high_adult_mortality_params, num_runs)

        self.assertGreater(
            balanced_result['final_population'],
            high_mortality_result['final_population'],
            f"Higher adult mortality should result in smaller population. "
            f"Balanced mortality: {balanced_result['final_population']:.1f}, High adult mortality: {high_mortality_result['final_population']:.1f}"
        )

    def test_seasonal_breeding_effect(self):
        """Test that seasonal breeding patterns affect population growth."""
        num_runs = 20
        
        # Run with minimal seasonality
        low_seasonal_params = self.base_params.copy()
        low_seasonal_params.update({
            'seasonal_breeding_amplitude': 0.1,
            'territory_size': 20000,
            'density_impact_threshold': 3.0
        })
        low_result = self.simulate_with_params(low_seasonal_params, num_runs)

        # Run with strong seasonality
        high_seasonal_params = self.base_params.copy()
        high_seasonal_params.update({
            'seasonal_breeding_amplitude': 0.4,
            'territory_size': 20000,
            'density_impact_threshold': 3.0
        })
        high_result = self.simulate_with_params(high_seasonal_params, num_runs)

        # Population with stronger seasonality should show more variance
        low_variance = np.var(low_result['monthly_populations'])
        high_variance = np.var(high_result['monthly_populations'])
        
        self.assertGreater(
            high_variance,
            low_variance,
            f"Stronger seasonality should result in more variable population sizes. "
            f"Low seasonality variance: {low_variance:.1f}, High seasonality variance: {high_variance:.1f}"
        )

    def test_urban_hazard_effect(self):
        """Test that urban hazards affect mortality rates."""
        num_runs = 20
        
        # Run with low urban hazards
        low_hazard_params = self.base_params.copy()
        low_hazard_params.update({
            'urban_mortality_rate': 0.05,
            'territory_size': 20000,
            'density_impact_threshold': 3.0
        })
        low_result = self.simulate_with_params(low_hazard_params, num_runs)

        # Run with high urban hazards
        high_hazard_params = self.base_params.copy()
        high_hazard_params.update({
            'urban_mortality_rate': 0.2,
            'territory_size': 20000,
            'density_impact_threshold': 3.0
        })
        high_result = self.simulate_with_params(high_hazard_params, num_runs)

        self.assertGreater(
            low_result['final_population'],
            high_result['final_population'],
            f"Higher urban hazards should result in smaller population. "
            f"Low hazards: {low_result['final_population']:.1f}, High hazards: {high_result['final_population']:.1f}"
        )

if __name__ == '__main__':
    unittest.main()
