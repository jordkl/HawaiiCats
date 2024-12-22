# Hawaii Cats Population Simulator

A web-based simulation tool for modeling and analyzing cat population dynamics in Hawaii. This project provides a sophisticated simulation framework to help understand and predict feral cat population trends under various conditions and intervention strategies.

## Features

- Advanced population dynamics modeling
- Seasonal breeding patterns
- Environmental impact factors
- Resource availability modeling
- Colony density effects
- Detailed population statistics and graphs
- Data export capabilities
- Interactive web interface for running cat population simulations
- Parameter testing and sensitivity analysis
- Scenario flagging for notable simulation cases
- Detailed logging and data export functionality
- CORS-enabled API endpoints for integration with hawaiicats.org

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/HawaiiCats.git
cd HawaiiCats
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install Node.js dependencies:
```bash
npm install
```

5. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
FLASK_APP=wsgi:app
FLASK_ENV=development
DISABLE_FIREBASE=true  # Set to false if you have Firebase credentials
```

If you want to use Firebase authentication:
1. Create a Firebase project and download the service account credentials
2. Save the credentials as `firebase-credentials.json` in the `app` directory
3. Set `DISABLE_FIREBASE=false` in your `.env` file

## Development

### Running Locally
```bash
# Start the Flask development server
python wsgi.py
```
The application will be available at `http://localhost:5001`

### Production Deployment
The application uses gunicorn and nginx in production. The deployment configuration is handled by:
- `hard-deploy.sh`: Sets up directories and permissions
- `/etc/systemd/system/gunicorn.service`: Gunicorn service configuration
- `/etc/nginx/sites-available/default`: Nginx configuration
- `/etc/gunicorn.d/gunicorn.py`: Gunicorn configuration

## Usage

Start the Flask development server:
```bash
python main.py
```

The application will be available at `http://localhost:5001`

## Project Structure

- `app/` - Main Flask application
  - `routes/` - API endpoints and route handlers
  - `templates/` - HTML templates for the web interface
  - `static/` - Static assets (CSS, JavaScript, images)
- `tools/` - Core functionality modules
  - `cat_simulation/` - Core simulation logic and models
  - `colony_analyzer/` - Colony analysis tools
  - `sightings/` - Cat sighting data management
- `config/` - Application configuration
- `deployment/` - Deployment scripts and configurations
- `logs/` - Simulation logs and calculation results
- `flagged_scenarios/` - Storage for notable simulation scenarios
- `scripts/` - Utility scripts
- `tests/` - Test suite

## Dependencies

### Python Dependencies
- Flask 2.3.3
- Flask-CORS 5.0.0
- H3 3.7.6
- NumPy 1.24.3
- Pandas 2.0.3
- psutil ≥5.9.0
- gevent 23.9.1

### Node.js Dependencies
- See `package.json` for frontend dependencies

## API Endpoints

- `/` - Home page
- `/calculator` - Population calculator interface
- `/about` - About page
- `/calculate` - Run population simulation
- `/parameter-tests` - Run parameter sensitivity tests
- `/download-logs` - Export simulation logs
- `/flag-scenario` - Flag notable scenarios
- `/clear-logs` - Clear calculation logs

## Deployment

### Local Development
1. Make changes locally
2. Test using the local development server at `http://localhost:5001`
3. Commit and push changes to GitHub:
```bash
git add .
git commit -m "Description of changes"
git push origin main
```

### Using the Deployment Script

The repository includes a deployment script (`deploy.sh`) that automates the process of updating and configuring the application on the production server. This script:

1. Pulls the latest changes from GitHub
2. Sets correct file permissions
3. Updates Nginx and Gunicorn configurations
4. Restarts necessary services

To use the deployment script:

1. Make the script executable:
```bash
chmod +x deploy.sh
```

2. Run the script with sudo:
```bash
sudo ./deploy.sh
```

Note: The deployment script should only be used on the production server. It requires sudo privileges to modify system configurations and restart services.

### Production Deployment
The production site is hosted at [hawaiicats.org](https://hawaiicats.org). 

Production deployment requires proper authentication and access credentials. Contact the repository owner for deployment access and instructions.

**Note:** Always test changes thoroughly in the local environment before requesting a production deployment.

## Parameter Relationships and Weights

The simulation uses a complex network of interrelated parameters to model cat population dynamics. Here's how they influence each other:

### Territory and Density Parameters (High Impact)
- `territory_size` (Weight: 1.0) - Base parameter that directly affects carrying capacity
  - Influences: density impact, resource availability, stress factors
  - Non-linear scaling: smaller territories have exponentially lower carrying capacity
  - Formula: carrying_capacity = territory_size * base_cats_per_unit * (territory_size/1000)^0.8

### Breeding Parameters (High Impact)
- `breeding_rate` (Weight: 0.85) - Base breeding probability
- `seasonal_breeding_amplitude` (Weight: 0.2) - Seasonal variation in breeding
- `female_ratio` (Weight: 0.5) - Population gender balance
Combined Effect = breeding_rate * seasonal_factor * (1 - density_impact)

### Survival Parameters (Medium-High Impact)
- `kitten_survival_rate` (Weight: 0.7) - Base survival rate for kittens
- `adult_survival_rate` (Weight: 0.9) - Base survival rate for adults
Actual survival rates are modified by:
  - Resource availability (0.4x - 1.0x multiplier)
  - Territory stress (0.6x - 1.0x multiplier)
  - Population density (0.5x - 1.0x multiplier)

### Environmental Risk Factors (Medium Impact)
- `urban_risk` (Weight: 0.15) - Risk from urban environment
- `disease_risk` (Weight: 0.10) - Risk of disease spread
- `natural_risk` (Weight: 0.10) - Natural predation/environmental risks
Combined Risk = 1.0 + (sum of risks) * competition_factor

### Resource Parameters (Medium Impact)
- `base_food_capacity` (Weight: 0.9) - Base food availability
- `food_scaling_factor` (Weight: 0.8) - How food scales with population
- `water_availability` (Weight: 0.9) - Water resource factor
- `shelter_quality` (Weight: 0.8) - Shelter availability
Resource Stress = base_stress * (1 + overpopulation_ratio)

### Support Parameters (Low-Medium Impact)
- `caretaker_support` (Weight: 0.8) - Human intervention level
- `feeding_consistency` (Weight: 0.9) - Regular feeding impact
Support Effect = 1.0 + support_factor * (1 - density_stress)

### Intervention Parameters (Variable Impact)
- `monthly_sterilization` - Direct population control
- `sterilization_cost` - Economic factor
Impact varies based on:
  - Population size
  - Territory capacity
  - Implementation timing

### Parameter Interactions
1. Territory Size → Density → Resource Availability
   - Larger territories support higher populations but with diminishing returns
   - Density effects become more pronounced in smaller territories

2. Resource Availability → Breeding Success → Population Growth
   - Resources affect breeding success non-linearly
   - High resource stress reduces breeding success exponentially

3. Population Density → Competition → Mortality
   - Higher density increases competition
   - Competition increases mortality rates exponentially above carrying capacity

4. Environmental Risks → Mortality → Population Control
   - Risks compound with density stress
   - Urban areas have different risk profiles than rural areas

These relationships create a dynamic system where changes in one parameter can have cascading effects throughout the population model. The simulation uses these weighted relationships to provide realistic predictions of cat population dynamics under various conditions.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is proprietary software. All rights reserved.

## Contact

For questions or support, please visit [hawaiicats.org](https://hawaiicats.org)
