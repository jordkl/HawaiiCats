from flask import Blueprint, jsonify, request
from app.tools.cat_simulation.colony import Colony, ColonyManager
from datetime import datetime
import firebase_admin
from firebase_admin import firestore
import traceback

bp = Blueprint('colony', __name__, url_prefix='/api')

@bp.route('/colonies', methods=['GET'])
def get_colonies():
    try:
        db = firestore.client()
        colonies = []
        for doc in db.collection('colonies').stream():
            colony_data = doc.to_dict()
            colony_data['id'] = doc.id
            
            # Extract location data to top level
            if 'location' in colony_data:
                colony_data['latitude'] = colony_data['location'].get('latitude', 0)
                colony_data['longitude'] = colony_data['location'].get('longitude', 0)
                
            colonies.append(colony_data)
        return jsonify(colonies)
    except Exception as e:
        print("Error getting colonies:", str(e))
        return jsonify({"error": str(e)}), 500

@bp.route('/colonies', methods=['POST'])
def add_colony():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug print
        
        # Initialize Firestore DB
        db = firestore.client()
        
        # Create colony data dictionary
        colony_data = {
            # Basic colony data
            'name': data.get('name'),
            'currentSize': data.get('currentSize', 0),
            'sterilized_count': data.get('sterilized_count', 0),
            'monthly_sterilization_rate': data.get('monthly_sterilization_rate', 0),
            'notes': data.get('notes', ''),
            'status': 'active',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            
            # Location data
            'location': {
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude')
            },
            
            # Environmental factors
            'water_availability': data.get('water_availability', 0.8),
            'shelter_quality': data.get('shelter_quality', 0.7),
            'territory_size': data.get('territory_size', 500),
            
            # Breeding parameters
            'breeding_rate': data.get('breeding_rate', 0.85),
            'kittens_per_litter': data.get('kittens_per_litter', 4),
            'litters_per_year': data.get('litters_per_year', 2.5),
            'kitten_survival_rate': data.get('kitten_survival_rate', 0.75),
            'adult_survival_rate': data.get('adult_survival_rate', 0.85),
            
            # Risk factors
            'urban_risk': data.get('urban_risk', 0.15),
            'disease_risk': data.get('disease_risk', 0.1),
            
            # Support factors
            'caretaker_support': data.get('caretaker_support', 0.8),
            'feeding_consistency': data.get('feeding_consistency', 0.8)
        }
        
        # Add to Firestore
        doc_ref = db.collection('colonies').document()
        doc_ref.set(colony_data)
        
        # Return the created colony with ID and flattened location
        response_data = colony_data.copy()
        response_data['id'] = doc_ref.id
        response_data['latitude'] = colony_data['location']['latitude']
        response_data['longitude'] = colony_data['location']['longitude']
        
        return jsonify(response_data)
        
    except Exception as e:
        print("Error adding colony:", str(e))
        return jsonify({"error": str(e)}), 500

@bp.route('/colonies/<colony_id>', methods=['GET'])
def get_colony(colony_id):
    try:
        db = firestore.client()
        colony_ref = db.collection('colonies').document(colony_id)
        colony_data = colony_ref.get().to_dict()
        colony_data['id'] = colony_id
        return jsonify(colony_data)
    except Exception as e:
        print("Error getting colony:", str(e))
        return jsonify({"error": str(e)}), 500

@bp.route('/colonies/<colony_id>', methods=['PUT'])
def update_colony(colony_id):
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'currentSize']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get colony manager instance
        colony_manager = ColonyManager()
        
        # Update timestamp
        data['updated_at'] = datetime.utcnow()
        
        # Handle location data
        if 'latitude' in data and 'longitude' in data:
            data['location'] = {
                'latitude': float(data['latitude']),
                'longitude': float(data['longitude'])
            }
            # Remove top-level lat/lng as they're now in location
            data.pop('latitude', None)
            data.pop('longitude', None)
        
        try:
            # Update colony in both cache and Firestore
            updated_colony = colony_manager.update_colony(colony_id, data)
            if not updated_colony:
                return jsonify({'error': 'Colony not found'}), 404
                
            # Get the colony data and add location to top level
            colony_data = updated_colony.to_dict()
            colony_data['id'] = colony_id
            
            if 'location' in colony_data:
                colony_data['latitude'] = colony_data['location'].get('latitude', 0)
                colony_data['longitude'] = colony_data['location'].get('longitude', 0)
                
            return jsonify(colony_data)
            
        except Exception as e:
            print(f"Error in colony manager: {str(e)}")
            return jsonify({'error': 'Failed to update colony'}), 500
        
    except Exception as e:
        print("Error updating colony:", str(e))
        traceback.print_exc()  # Print full traceback for debugging
        return jsonify({"error": str(e)}), 500

@bp.route('/colonies/<colony_id>', methods=['DELETE'])
def delete_colony(colony_id):
    try:
        db = firestore.client()
        colony_ref = db.collection('colonies').document(colony_id)
        colony_ref.delete()
        return jsonify({"message": "Colony deleted successfully"})
    except Exception as e:
        print("Error deleting colony:", str(e))
        return jsonify({"error": str(e)}), 500
