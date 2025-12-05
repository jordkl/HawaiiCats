# Hawaii Cats Population Calculator - Technical Documentation

**Version:** 1.0.0  
**Last Updated:** December 5, 2025  
**URL:** https://hawaiicats.org/calculator

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Basic Parameters](#basic-parameters)
4. [Advanced Parameters](#advanced-parameters)
   - [Population Dynamics](#population-dynamics)
   - [Seasonal Factors](#seasonal-factors)
   - [Environmental Factors](#environmental-factors)
   - [Resource Factors](#resource-factors)
   - [Colony Density](#colony-density)
   - [Habitat Quality](#habitat-quality)
5. [Environment Presets](#environment-presets)
6. [Cost Calculations](#cost-calculations)
7. [Simulation Algorithm](#simulation-algorithm)
8. [Output Metrics](#output-metrics)
9. [Known Issues & Improvements](#known-issues--improvements)

---

## Overview

The Hawaii Cats Population Calculator is a web-based simulation tool for modeling feral cat population dynamics. It uses a monthly time-step simulation to project population growth, mortality, and associated costs under various environmental conditions and intervention strategies (primarily TNR - Trap-Neuter-Return).

### Key Features
- Monthly population projections over 1-60 months
- Sterilization impact modeling
- Environmental preset configurations
- Cost estimation (food + sterilization)
- Mortality tracking by cause (natural, urban, disease)
- Interactive population graphs

---

## Architecture

### Frontend
- **Template:** `app/templates/calculator.html`
- **JavaScript:** `app/static/js/calculator.js`
- **Styling:** TailwindCSS with custom CSS variables
- **Charting:** Chart.js

### Backend
- **Route:** `/calculatePopulation` (POST)
- **Handler:** `app/routes/simulation_routes.py`
- **Core Logic:** `app/tools/cat_simulation/simulation.py`
- **Utilities:** `app/tools/cat_simulation/utils/simulation_utils.py`
- **Constants:** `app/tools/cat_simulation/constants.py`

### Data Flow
```
User Input → calculator.js → /calculatePopulation API → simulation.py → JSON Response → Chart.js Display
```

---

## Basic Parameters

These parameters are always visible in the sidebar.

| Parameter | ID | Range | Default | Unit | Description |
|-----------|-----|-------|---------|------|-------------|
| **Initial Colony Size** | `initialColonySize` | 1-250 | 10 | cats | Starting population of the colony |
| **Already Sterilized** | `alreadySterilized` | 0-[colony size] | 0 | cats | Number of cats already sterilized at simulation start |
| **Monthly Sterilization Rate** | `monthlySterilizationRate` | 0-[unsterilized count] | 1 | cats/month | Number of cats sterilized each month |
| **Sterilization Cost** | `sterilizationCost` | 0+ | 50 | USD/cat | Cost per sterilization procedure |
| **Simulation Length** | `simulationLength` | 1-60 | 12 | months | Duration of the simulation |

### Impact on Population

- **Initial Colony Size:** Directly sets starting population. Larger colonies have more breeding potential but also face density-dependent constraints.
- **Already Sterilized:** Reduces the breeding pool immediately. Sterilized cats still consume resources and count toward density.
- **Monthly Sterilization Rate:** Primary intervention lever. Higher rates reduce breeding population faster, leading to population decline over time.
- **Simulation Length:** Longer simulations show compounding effects of breeding/sterilization.

---

## Advanced Parameters

Accessible by toggling "Advanced Mode" in the sidebar.

### Population Dynamics

| Parameter | ID | Range | Default | Description | Impact |
|-----------|-----|-------|---------|-------------|--------|
| **Monthly Abandonment** | `monthlyAbandonment` | 0-50 | 0 | Cats abandoned per month | Adds unsterilized cats monthly, counteracting sterilization efforts |
| **Kitten Survival Rate** | `kittenSurvivalRate` | 0.1-0.9 | 0.8 | Annual survival rate for kittens | Lower values = higher kitten mortality, slower population growth |
| **Adult Survival Rate** | `adultSurvivalRate` | 0.2-0.95 | 0.92 | Annual survival rate for adults | Lower values = higher adult mortality, population decline |
| **Breeding Rate** | `breedingRate` | 0-1 | 0.85 | Probability of successful breeding | Multiplier on birth calculations |
| **Kittens Per Litter** | `kittensPerLitter` | 1-8 | 4 | Average litter size | Direct multiplier on births |
| **Litters Per Year** | `littersPerYear` | 1-4 | 2.5 | Average litters per female per year | Affects monthly breeding probability |
| **Female Ratio** | `femaleRatio` | 0.3-0.7 | 0.5 | Proportion of females in population | Higher = more breeding potential |
| **Kitten Maturity** | `kittenMaturityMonths` | 4-8 | 5 | Months until kittens can breed | Affects generation time |

#### Breeding Formula
```python
monthly_breeding_prob = (litters_per_year / 12.0) * base_breeding_rate
births = unsterilized * breeding_rate * kittens_per_litter * seasonal_factor * resource_factor * (1 - density_impact)
```

#### Mortality Formula
```python
base_mortality = (1 - adult_survival_rate) / 12.0  # Convert annual to monthly
kitten_mortality = (1 - kitten_survival_rate) / 12.0
total_mortality_rate = base_mortality + disease_impact + urban_impact
```

---

### Seasonal Factors

| Parameter | ID | Range | Default | Description | Impact |
|-----------|-----|-------|---------|-------------|--------|
| **Seasonal Breeding Amplitude** | `seasonalBreedingAmplitude` | 0-0.5 | 0.2 | Magnitude of seasonal variation | 0 = no seasonality, 0.5 = strong seasonal peaks |
| **Peak Breeding Month** | `peakBreedingMonth` | 1-12 | 3 (March) | Month with highest breeding activity | Shifts the breeding cycle |

#### Seasonal Factor Calculation
```python
# Cosine curve with configurable peak
monthDiff = abs(((month - peakMonth + 6) % 12) - 6)
baseFactor = (0.5 * (1.0 + cos(2π * monthDiff / 12)))^1.5
seasonalFactor = 1.0 - (amplitude * (1.0 - baseFactor))
# Returns 0.2-1.0 range
```

**Note:** Hawaii has mild seasonality, so default amplitude is low (0.2). Spring months (March-April) typically see increased breeding activity.

---

### Environmental Factors

| Parameter | ID | Range | Default | Description | Impact |
|-----------|-----|-------|---------|-------------|--------|
| **Urban Risk** | `urbanRisk` | 0-0.5 | 0.08 | Risk from traffic, hazards | Increases urban-related deaths |
| **Disease Risk** | `diseaseRisk` | 0-0.5 | 0.04 | Risk of disease outbreaks | Increases disease-related deaths |
| **Natural Risk** | `naturalRisk` | 0-0.5 | 0.04 | Risk from predators, weather | Increases natural deaths |

#### Environmental Risk Formula
```python
disease_impact = disease_risk / 12.0 * random(0.7, 1.3)
urban_impact = urbanization_impact / 12.0 * random(0.7, 1.3)
environmental_impact = environmental_stress / 12.0 * random(0.7, 1.3)
```

**Note:** These parameters are defined in the template but the simulation primarily uses `urbanization_impact`, `disease_transmission_rate`, and `environmental_stress` from the advanced params.

---

### Resource Factors

| Parameter | ID | Range | Default | Description | Impact |
|-----------|-----|-------|---------|-------------|--------|
| **Food Cost Per Cat** | `foodCostPerCat` | 0-50 | 15 | Monthly food cost per cat (USD) | Affects total cost calculation |
| **Base Food Capacity** | `baseFoodCapacity` | 0-2 | 0.95 | Natural food availability | Higher = better survival, more breeding |
| **Food Scaling Factor** | `foodScalingFactor` | 0.5-1 | 0.9 | How food scales with population | Lower = faster resource depletion |
| **Feedings Per Week** | `caretakerSupport` | 0-21 | 3 | Times colony is fed weekly | 0 = no feeding costs; higher = better survival |
| **Feeding Consistency** | `feedingConsistency` | 0-1 | 0.9 | Reliability of feeding schedule | Affects resource stability |

#### Resource Availability Formula
```python
survivalResources = (0.7 * baseFood + 0.3 * waterAvailability)
supportResources = (0.6 * shelterQuality + 0.4 * caretakerSupport)
stabilityFactor = 0.95 + 0.05 * feedingConsistency
rawAvailability = 0.6 * survivalResources + 0.3 * supportResources + 0.1 * stabilityFactor
resourceFactor = sigmoid(rawAvailability)  # Returns 0.5-1.0
```

#### Food Cost Formula
```python
if feedings_per_week == 0:
    monthly_food_cost = 0
else:
    feeding_level = min(feedings_per_week / 14.0, 1.5)
    food_multiplier = (2.0 - base_food_capacity) * (2.0 - food_scaling) * (2.0 - feeding_consistency)
    monthly_food_cost = population * base_food_cost * food_multiplier * feeding_level
```

---

### Colony Density

| Parameter | ID | Range | Default | Description | Impact |
|-----------|-----|-------|---------|-------------|--------|
| **Territory Size** | `territorySize` | 100-100,000 | 1000 | Area in square meters | Larger = higher carrying capacity |
| **Environment Density** | `densityThreshold` | 0.2-5.0 | 1.2 | Cats per 100m² threshold | Higher = more cats supported per area |

#### Carrying Capacity Formula
```python
territory_capacity = max(50, territory_size * density_threshold * 0.15)
current_density = population / territory_capacity
density_impact = max(0, min(1, (current_density - 1.0) * 1.5))
```

#### Density Impact on Population
- **Below capacity (density_impact = 0):** Normal breeding and survival
- **At capacity (density_impact starts):** Breeding reduced by up to 95%
- **Over capacity:** Additional mortality from competition

```python
# Density mortality when over capacity
if density_impact > 0:
    density_mortality_rate = min(0.2, 0.1 * density_impact * (1 - resource_factor))
```

---

### Habitat Quality

| Parameter | ID | Range | Default | Description | Impact |
|-----------|-----|-------|---------|-------------|--------|
| **Water Availability** | `waterAvailability` | 0-1 | 0.95 | Access to water sources | Critical for survival |
| **Shelter Quality** | `shelterQuality` | 0-1 | 0.85 | Quality of shelter/hiding spots | Affects survival and breeding |

These parameters feed into the resource availability calculation with water being weighted heavily (45% of resource factor).

---

## Environment Presets

Pre-configured parameter sets for common colony environments.

| Preset | Territory | Density | Food Cap | Urban Impact | Disease Rate | Abandonment |
|--------|-----------|---------|----------|--------------|--------------|-------------|
| **Residential** | 2000m² | 1.2 | 0.8 | 0.4 | 0.15 | 3/month |
| **Street/Alley** | 1000m² | 1.5 | 0.3 | 0.8 | 0.4 | 4/month |
| **Public Park** | 5000m² | 0.8 | 0.5 | 0.2 | 0.2 | 2/month |
| **Industrial** | 3000m² | 1.0 | 0.6 | 0.6 | 0.3 | 2/month |
| **Parking Lot** | 1500m² | 1.3 | 0.4 | 0.7 | 0.3 | 2/month |
| **Forest/Nature** | 8000m² | 0.5 | 0.6 | 0.1 | 0.4 | 1/month |
| **Beach Area** | 4000m² | 0.7 | 0.5 | 0.3 | 0.3 | 2/month |

### Preset Selection Behavior
- Selecting a preset immediately triggers a calculation
- Manually changing any parameter removes the "active" state from preset buttons
- Default preset on page load: **Residential**

---

## Cost Calculations

### Total Cost Components

```python
total_costs = food_costs + sterilization_costs
```

### Food Costs
- Only calculated if `feedings_per_week > 0`
- Scales with population size
- Modified by resource efficiency parameters

### Sterilization Costs
```python
monthly_sterilization_cost = new_sterilizations * sterilization_cost_per_cat
```

### Removed Cost Categories
The following were previously in the code but are now disabled:
- Medical costs
- Shelter costs  
- Emergency costs

---

## Simulation Algorithm

### Monthly Loop Process

```
For each month:
1. Calculate seasonal factor (breeding modifier)
2. Calculate resource availability
3. Calculate carrying capacity
4. Calculate density impact
5. Apply mortality:
   - Base mortality (age-based)
   - Disease mortality
   - Urban mortality
   - Density-dependent mortality (if over capacity)
6. Calculate births:
   - Only from unsterilized females
   - Modified by seasonal, resource, and density factors
7. Apply sterilizations (move cats from unsterilized to sterilized)
8. Add abandoned cats (to unsterilized pool)
9. Calculate monthly costs
10. Record monthly statistics
```

### Stochastic Elements
The simulation includes random variation (±20-30%) on:
- Mortality rates
- Disease/urban/environmental impacts
- Breeding rates

This means running the same parameters twice may produce slightly different results.

---

## Output Metrics

### Primary Results

| Metric | Description |
|--------|-------------|
| **Final Population** | Total cats at end of simulation |
| **Population Change** | Difference from initial population |
| **Sterilization Rate** | Percentage of population sterilized |
| **Total Cost** | Sum of food + sterilization costs |

### Mortality Statistics

| Metric | Description |
|--------|-------------|
| **Total Deaths** | All deaths during simulation |
| **Kitten Deaths** | Deaths of cats < 6 months old (estimated 30% of population) |
| **Adult Deaths** | Deaths of cats ≥ 6 months old |
| **Mortality Rate** | Deaths as percentage of population |
| **Natural Deaths** | Deaths from age/natural causes |
| **Urban Deaths** | Deaths from traffic/urban hazards |
| **Disease Deaths** | Deaths from illness |

### Graph Data
- **Total Population:** Monthly population count
- **Sterilized Population:** Monthly sterilized count
- X-axis: Months (0 to simulation length)

---

## Known Issues & Improvements

### Bugs / Issues

#### 1. **Double-counting of totalDeaths**
**Location:** `simulation.py` lines 334 and 361
```python
totalDeaths += total_deaths_this_month  # Line 334
# ... later ...
totalDeaths += total_deaths_this_month  # Line 361 - DUPLICATE
```
**Impact:** Total deaths may be reported as ~2x actual value.
**Fix:** Remove the duplicate addition on line 361.

---

#### 2. **Inconsistent Parameter Naming**
**Issue:** Parameters use different naming conventions between frontend and backend:
- Frontend: `camelCase` (e.g., `baseFoodCapacity`)
- Backend: `snake_case` (e.g., `base_food_capacity`)
- Some parameters have mismatched names entirely

**Examples:**
- `seasonalBreedingAmplitude` (frontend) vs `seasonality_strength` (constants)
- `densityThreshold` (frontend) vs `density_impact_threshold` (backend)

**Impact:** Some advanced parameters may not be properly passed to the simulation.

---

#### 3. **Unused Parameters**
Several parameters defined in templates are not used in simulation:
- `urbanRisk`, `diseaseRisk`, `naturalRisk` (environmental_factors.html)
- `resourceCompetition`, `resourceScarcityImpact` (defined but not used)
- `densityStressRate`, `maxDensityImpact` (defined but not used)

---

#### 4. **Carrying Capacity Calculation Inconsistency**
**Issue:** Two different `calculateCarryingCapacity` functions exist:
1. In `simulation.py` (lines 498-510) - uses cubic scaling
2. In `simulation_utils.py` (lines 172-207) - uses linear scaling with high minimum (300)

The simulation imports from `simulation_utils.py` but also defines its own version.

---

#### 5. **Resource Factor Calculation Redundancy**
**Issue:** `calculateResourceAvailability` is defined in both:
- `simulation.py` (lines 512-535)
- `simulation_utils.py` (lines 123-170)

Different implementations may cause confusion.

---

#### 6. **Kitten/Adult Death Distribution**
**Issue:** The simulation assumes 30% of population are kittens (`kitten_ratio = 0.3`) as a constant, rather than tracking actual age distribution.

**Impact:** Kitten vs adult death statistics are estimates, not actual tracked values.

---

### Suggested Improvements

#### High Priority

1. **Fix totalDeaths double-counting bug**
   - Remove duplicate `totalDeaths += total_deaths_this_month` on line 361

2. **Standardize parameter naming**
   - Create a single parameter mapping file
   - Use consistent naming throughout

3. **Add parameter validation on frontend**
   - Validate ranges before sending to backend
   - Show user-friendly error messages

#### Medium Priority

4. **Implement actual age tracking**
   - Track individual cat ages or age cohorts
   - More accurate kitten/adult mortality

5. **Add Monte Carlo mode**
   - Run multiple simulations
   - Show confidence intervals on results

6. **Consolidate utility functions**
   - Remove duplicate function definitions
   - Single source of truth for calculations

7. **Add cost breakdown display**
   - Show food vs sterilization costs separately in UI
   - Monthly cost chart

#### Low Priority

8. **Add export functionality**
   - Export simulation results to CSV
   - Export parameters for reproducibility

9. **Add comparison mode**
   - Compare two scenarios side-by-side
   - Show impact of different intervention strategies

10. **Improve mobile responsiveness**
    - Sidebar collapses on mobile
    - Touch-friendly sliders

---

## API Reference

### POST /calculatePopulation

**Request Body:**
```json
{
  "initialColonySize": 10,
  "alreadySterilized": 0,
  "monthlySterilizationRate": 1,
  "simulationLength": 12,
  "sterilizationCost": 50,
  "monthlyAbandonment": 0,
  "params": {
    "breedingRate": 0.85,
    "kittensPerLitter": 4,
    "littersPerYear": 2.5,
    "kittenSurvivalRate": 0.7,
    "adultSurvivalRate": 0.85,
    "femaleRatio": 0.5,
    "kittenMaturityMonths": 5,
    "peakBreedingMonth": 4,
    "seasonalityStrength": 0.3,
    "territorySize": 1000,
    "baseFoodCapacity": 0.9,
    "foodScalingFactor": 0.8,
    "caretakerSupport": 0.5,
    "feedingConsistency": 0.9,
    "foodCostPerCat": 15.0,
    "densityImpactThreshold": 1.2,
    "baseHabitatQuality": 0.8,
    "urbanizationImpact": 0.2,
    "diseaseTransmissionRate": 0.1,
    "monthlyAbandonment": 2.0
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "finalPopulation": 45,
    "populationChange": 35,
    "sterilizationRate": 0.27,
    "totalCost": 1250.50,
    "costBreakdown": {
      "food": 650.50,
      "sterilization": 600.00
    },
    "totalDeaths": 8,
    "kittenDeaths": 3,
    "adultDeaths": 5,
    "mortalityRate": 0.18,
    "naturalDeaths": 4,
    "urbanDeaths": 2,
    "diseaseDeaths": 2,
    "months": [0, 1, 2, ...],
    "totalPopulation": [10, 12, 15, ...],
    "sterilizedPopulation": [0, 1, 2, ...],
    "unsterilizedPopulation": [10, 11, 13, ...]
  },
  "message": "Calculation completed successfully"
}
```

---

## File Reference

| File | Purpose |
|------|---------|
| `app/templates/calculator.html` | Main calculator page template |
| `app/templates/components/parameters.html` | Basic parameters component |
| `app/templates/components/population_dynamics.html` | Population dynamics parameters |
| `app/templates/components/seasonal_factors.html` | Seasonal parameters |
| `app/templates/components/environmental_factors.html` | Environmental risk parameters |
| `app/templates/components/resource_factors.html` | Resource/food parameters |
| `app/templates/components/colony_density.html` | Territory/density parameters |
| `app/templates/components/habitat_quality.html` | Water/shelter parameters |
| `app/templates/components/results.html` | Results display component |
| `app/static/js/calculator.js` | Frontend logic and API calls |
| `app/routes/simulation_routes.py` | Backend API endpoints |
| `app/tools/cat_simulation/simulation.py` | Core simulation logic |
| `app/tools/cat_simulation/constants.py` | Default parameter values |
| `app/tools/cat_simulation/utils/simulation_utils.py` | Utility calculation functions |

---

*Documentation generated for Hawaii Cats Population Calculator v1.0.0*
