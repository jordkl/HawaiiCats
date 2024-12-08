# HawaiiCats Population Simulator

A web-based simulation tool for modeling and analyzing cat population dynamics in Hawaii. This project provides a sophisticated Monte Carlo simulation framework to help understand and predict feral cat population trends under various conditions and intervention strategies.

## Features

- Interactive web interface for running cat population simulations
- Monte Carlo simulation capabilities for statistical analysis
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

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Node.js dependencies:
```bash
npm install
```

## Usage

Start the Flask development server:
```bash
python main.py
```

The application will be available at `http://localhost:5001`

## Project Structure

- `main.py` - Main Flask application and API endpoints
- `cat_simulation/` - Core simulation logic and models
- `templates/` - HTML templates for the web interface
- `static/` - Static assets (CSS, JavaScript, images)
- `logs/` - Simulation logs and calculation results
- `flagged_scenarios/` - Storage for notable simulation scenarios

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
