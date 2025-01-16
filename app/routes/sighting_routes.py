from flask import Blueprint, render_template, jsonify, request
from app.tools.sightings.store import get_store

bp = Blueprint('sightings', __name__)

@bp.route('/catmap')
def catmap():
    return render_template('catmap.html')

@bp.route('/submit-sighting')
def submit_sighting():
    return render_template('submit_sighting.html')

@bp.route('/sightings')
def get_sightings():
    try:
        store = get_store()
        sightings = store.get_all_sightings()
        return jsonify(sightings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/sightings', methods=['POST'])
def add_sighting():
    try:
        data = request.get_json()
        store = get_store()
        
        # Add the sighting to the store
        store.add_sighting(data)
        
        # Force a sync with Firebase
        store.sync_with_firebase()
        
        return jsonify({"message": "Sighting added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/sightings/force_sync', methods=['POST'])
def force_sync():
    try:
        store = get_store()
        store.sync_with_firebase()
        return jsonify({"message": "Sync completed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
