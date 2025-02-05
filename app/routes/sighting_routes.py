from flask import Blueprint, render_template, jsonify, request
from app.tools.sightings.store import get_store
from app.tools.storage.firebase_storage import get_storage_manager
from werkzeug.utils import secure_filename
import os
from datetime import datetime

bp = Blueprint('sightings', __name__)

@bp.route('/catmap')
def catmap():
    return render_template('catmap.html')

@bp.route('/submit-sighting')
def submit_sighting():
    return render_template('submit_sighting.html')

@bp.route('/api/sightings', methods=['GET'])
def get_sightings():
    try:
        store = get_store()
        sightings = store.get_all_sightings()
        print("DEBUG: Sightings being sent to frontend:", sightings)
        return jsonify(sightings)
    except Exception as e:
        print(f"Error in get_sightings route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle image upload to Firebase Storage"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'error': 'No file selected'}), 400
            
        # Check if the file is an allowed image type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not '.' in file.filename or \
           file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'error': 'Invalid file type'}), 400
            
        print(f"Processing file upload: {file.filename}")
        # Get the storage manager and upload the file
        storage_manager = get_storage_manager()
        print("Got storage manager")
        
        try:
            result = storage_manager.upload_image(file, content_type=file.content_type)
            print(f"Upload successful: {result}")
            return jsonify(result)
        except Exception as upload_error:
            print(f"Upload error: {str(upload_error)}")
            return jsonify({'error': str(upload_error)}), 500
        
    except Exception as e:
        print(f"Error in upload_file route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/sightings', methods=['POST'])
def add_sighting():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        store = get_store()
        
        # Ensure required fields are present and valid
        if not data.get('latitude') or not data.get('longitude'):
            return jsonify({"error": "Missing or invalid coordinates"}), 400
            
        if not data.get('locationType'):
            return jsonify({"error": "Missing location type"}), 400
        
        # Process and validate the data
        try:
            sighting_data = {
                'latitude': float(data['latitude']),
                'longitude': float(data['longitude']),
                'locationType': data['locationType'],
                'visibleCats': int(data.get('visibleCats', 0)),
                'earNotchesCount': int(data.get('earNotchesCount', 0)),
                'isFeeding': bool(data.get('isFeeding', False)),
                'feedingTime': data.get('feedingTime'),
                'hasProtectedSpecies': bool(data.get('hasProtectedSpecies', False)),
                'visibility': data.get('visibility'),
                'movementLevel': data.get('movementLevel'),
                'timeSpent': data.get('timeSpent'),
                'notes': data.get('notes', ''),
                'photoUrls': data.get('photoUrls', []),
                'timestamp': data.get('timestamp') or datetime.utcnow().isoformat()
            }
        except (ValueError, TypeError) as e:
            return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
        
        # Add the sighting to the store
        sighting_id = store.add_sighting(sighting_data)
        
        # Force a sync with Firebase
        store.force_sync()
        
        return jsonify({
            "message": "Sighting added successfully",
            "id": sighting_id
        }), 201
    except Exception as e:
        print(f"Error adding sighting: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/sightings/force_sync', methods=['POST'])
def force_sync():
    try:
        store = get_store()
        store.sync_with_firebase()
        return jsonify({"message": "Sync completed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
