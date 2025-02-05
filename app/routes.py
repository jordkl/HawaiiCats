from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from .colony_analysis import ColonyAnalyzer
from firebase_admin import storage, db
import uuid
import os

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

@bp.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload an image to Firebase Storage."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if not file:
        return jsonify({'error': 'No file selected'}), 400
        
    # Check if the file is an image
    if not file.content_type.startswith('image/'):
        return jsonify({'error': 'File must be an image'}), 400
        
    try:
        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"sighting_photos/{str(uuid.uuid4())}{file_extension}"
        
        # Get a reference to the storage bucket
        bucket = storage.bucket()
        blob = bucket.blob(unique_filename)
        
        # Upload the file
        blob.upload_from_file(file, content_type=file.content_type)
        
        # Make the file publicly accessible
        blob.make_public()
        
        return jsonify({
            'url': blob.public_url,
            'filename': unique_filename
        })
        
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return jsonify({'error': 'Failed to upload file'}), 500

@bp.route('/api/sightings', methods=['POST'])
def add_sighting():
    """Add a new cat sighting."""
    try:
        data = request.json
        
        # Add H3 index to the sighting data
        h3_index = colony_analyzer.get_hex_index(
            float(data['latitude']),
            float(data['longitude'])
        )
        
        # Prepare sighting data
        sighting_data = {
            'h3_index': h3_index,
            'timestamp': datetime.utcnow().isoformat(),
            'latitude': float(data['latitude']),
            'longitude': float(data['longitude']),
            'locationType': data['locationType'],
            'isFeeding': data.get('isFeeding', False),
            'feedingTime': data.get('feedingTime') if data.get('isFeeding', False) else None,
            'visibleCats': int(data['visibleCats']),
            'earNotchesCount': int(data.get('earNotchesCount', 0)),
            'visibility': data['visibility'],
            'movementLevel': data['movementLevel'],
            'timeSpent': data['timeSpent'],
            'hasProtectedSpecies': data.get('hasProtectedSpecies', False),
            'notes': data.get('notes', ''),
            'photoUrls': data.get('photoUrls', [])
        }
        
        # Save to Firebase Realtime Database
        new_sighting_ref = db.reference('sightings').push(sighting_data)
        
        return jsonify({
            'message': 'Sighting added successfully',
            'h3_index': h3_index,
            'sightingId': new_sighting_ref.key
        })
        
    except Exception as e:
        print(f"Error adding sighting: {str(e)}")
        return jsonify({'error': str(e)}), 500
