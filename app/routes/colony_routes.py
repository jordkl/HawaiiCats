from flask import Blueprint, jsonify, request
from tools.cat_simulation.colony import Colony, ColonyManager

bp = Blueprint('colony', __name__)

@bp.route('/colonies', methods=['GET'])
def get_colonies():
    try:
        colonies = ColonyManager.get_all_colonies()
        return jsonify(colonies)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/colonies', methods=['POST'])
def add_colony():
    try:
        data = request.get_json()
        colony = Colony(
            name=data.get('name'),
            location=data.get('location'),
            population=data.get('population'),
            status=data.get('status'),
            notes=data.get('notes')
        )
        ColonyManager.add_colony(colony)
        return jsonify({"message": "Colony added successfully", "colony": colony.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/colonies/<colony_id>', methods=['GET'])
def get_colony(colony_id):
    try:
        colony = ColonyManager.get_colony(colony_id)
        return jsonify(colony.to_dict() if colony else {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/colonies/<colony_id>', methods=['PUT'])
def update_colony(colony_id):
    try:
        data = request.get_json()
        colony = Colony(
            id=colony_id,
            name=data.get('name'),
            location=data.get('location'),
            population=data.get('population'),
            status=data.get('status'),
            notes=data.get('notes')
        )
        ColonyManager.update_colony(colony)
        return jsonify({"message": "Colony updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/colonies/<colony_id>', methods=['DELETE'])
def delete_colony(colony_id):
    try:
        ColonyManager.delete_colony(colony_id)
        return jsonify({"message": "Colony deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
