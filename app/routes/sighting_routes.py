from flask import Blueprint, render_template, jsonify
from tools.sightings.store import get_store

bp = Blueprint('sightings', __name__)

@bp.route('/catmap')
def catmap():
    return render_template('catmap.html')

@bp.route('/sightings')
def get_sightings():
    try:
        store = get_store()
        sightings = store.get_all_sightings()
        return jsonify(sightings)
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
