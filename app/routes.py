from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from .colony_analysis import ColonyAnalyzer

# Initialize blueprint
bp = Blueprint('main', __name__)

# Initialize colony analyzer
colony_analyzer = ColonyAnalyzer(h3_resolution=9)  # ~174m hexagons

@bp.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@bp.route('/colonies')
def colonies():
    """Colony analysis page."""
    return render_template('colonies.html')

@bp.route('/api/sightings', methods=['GET'])
def get_sightings():
    """Get all sightings with optional filtering."""
    # TODO: Implement database query
    sightings = []  # Replace with actual database query
    return jsonify(sightings)

@bp.route('/api/colonies', methods=['GET'])
def get_colonies():
    """Get colony analysis based on sightings."""
    # Get filter parameters
    min_sightings = int(request.args.get('min_sightings', 3))
    min_avg_cats = float(request.args.get('min_avg_cats', 2.0))
    min_days_active = int(request.args.get('min_days_active', 14))
    
    # TODO: Get sightings from database
    sightings = []  # Replace with actual database query
    
    # Analyze colonies
    colonies = colony_analyzer.analyze_sightings(
        sightings,
        min_sightings=min_sightings,
        min_avg_cats=min_avg_cats,
        min_days_active=min_days_active
    )
    
    return jsonify(colonies)

@bp.route('/api/colonies/<h3_index>', methods=['GET'])
def get_colony_details(h3_index):
    """Get detailed information about a specific colony."""
    # Get adjacent hexagons
    adjacent = colony_analyzer.get_adjacent_colonies(h3_index)
    
    # TODO: Get sightings for this hexagon from database
    sightings = []  # Replace with actual database query
    
    # Get colony boundary
    boundary = colony_analyzer.get_hex_boundary(h3_index)
    
    return jsonify({
        'h3_index': h3_index,
        'boundary': [{'lat': lat, 'lng': lng} for lat, lng in boundary],
        'adjacent_hexagons': adjacent,
        'sightings': sightings
    })

@bp.route('/api/sightings', methods=['POST'])
def add_sighting():
    """Add a new cat sighting."""
    data = request.json
    
    # Add H3 index to the sighting data
    h3_index = colony_analyzer.get_hex_index(
        data['latitude'],
        data['longitude']
    )
    data['h3_index'] = h3_index
    data['timestamp'] = datetime.utcnow().isoformat()
    
    # TODO: Save to database
    
    return jsonify({
        'message': 'Sighting added successfully',
        'h3_index': h3_index
    })
