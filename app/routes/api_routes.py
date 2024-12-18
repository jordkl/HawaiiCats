from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from datetime import datetime
from ..models import Colony, Sighting
from .. import db

bp = Blueprint('api', __name__, url_prefix='/api')
firebase_db = firestore.client()

def format_firebase_colony(doc_id, data):
    """Helper function to format Firebase colony data"""
    location = data.get('location', {})
    return {
        'id': doc_id,
        'name': data.get('name', ''),
        'latitude': location.get('latitude') if location else data.get('latitude'),
        'longitude': location.get('longitude') if location else data.get('longitude'),
        'current_size': data.get('current_size') or data.get('size', 0),
        'sterilized_count': data.get('sterilized_count', 0),
        # Additional fields stored but not used in frontend
        'water_availability': data.get('water_availability'),
        'shelter_quality': data.get('shelter_quality'),
        'territory_size': data.get('territory_size'),
        'status': data.get('status')
    }

def format_firebase_sighting(doc_id, data):
    """Helper function to format Firebase sighting data"""
    coordinate = None
    
    # Handle GeoPoint coordinate
    if isinstance(data.get('coordinate'), firestore.GeoPoint):
        geopoint = data['coordinate']
        coordinate = {
            'latitude': geopoint.latitude,
            'longitude': geopoint.longitude
        }
    
    # Handle user location if coordinate is not available
    if coordinate is None and isinstance(data.get('userLocation'), firestore.GeoPoint):
        geopoint = data['userLocation']
        coordinate = {
            'latitude': geopoint.latitude,
            'longitude': geopoint.longitude
        }
    
    # Get details if they exist
    details = data.get('details', {})
    
    return {
        'id': doc_id,
        'timestamp': data.get('timestamp'),
        'best_count': data.get('bestCount') or details.get('bestCount', 0),
        'location_type': data.get('locationType') or details.get('locationType', ''),
        'coordinate': coordinate,
        'visible_cats': data.get('visibleCats') or details.get('visibleCats'),
        'min_count': data.get('minCount') or details.get('minCount'),
        'max_count': data.get('maxCount') or details.get('maxCount'),
        'movement_level': data.get('movementLevel') or details.get('movementLevel'),
        'uncertainty_level': data.get('uncertaintyLevel') or details.get('uncertaintyLevel'),
        'is_feeding': data.get('isFeeding') or details.get('isFeeding', False),
        'time_spent': data.get('timeSpent') or details.get('timeSpent'),
        'notes': data.get('notes') or details.get('notes', '')
    }

@bp.route('/sightings', methods=['GET', 'POST'])
def sightings():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Create SQLAlchemy record
            sighting = Sighting(
                latitude=data['latitude'],
                longitude=data['longitude'],
                best_count=data.get('bestCount'),
                location_type=data.get('locationType')
            )
            db.session.add(sighting)
            db.session.commit()
            
            # Sync to Firebase using GeoPoint for coordinates
            firebase_data = {
                'coordinate': firestore.GeoPoint(float(sighting.latitude), float(sighting.longitude)),
                'bestCount': sighting.best_count,
                'locationType': sighting.location_type,
                'timestamp': datetime.utcnow(),
                'details': {
                    'bestCount': sighting.best_count,
                    'locationType': sighting.location_type,
                    'isFeeding': False,
                    'timeSpent': 'quick',
                    'uncertaintyLevel': 'medium',
                    'movementLevel': 'low',
                    'notes': '',
                    'visibleCats': sighting.best_count,
                    'minCount': max(0, sighting.best_count - 3),
                    'maxCount': sighting.best_count + 3
                }
            }
            firebase_db.collection('sightings').add(firebase_data)
            
            return jsonify({
                'id': sighting.id,
                'timestamp': sighting.timestamp.isoformat(),
                'best_count': sighting.best_count,
                'location_type': sighting.location_type,
                'coordinate': {
                    'latitude': sighting.latitude,
                    'longitude': sighting.longitude
                }
            }), 201
        except Exception as e:
            print(f"Error creating sighting: {e}")
            return jsonify({'error': str(e)}), 500
    
    try:
        # Get Firebase sightings
        sightings = []
        firebase_docs = firebase_db.collection('sightings').stream()
        for doc in firebase_docs:
            sightings.append(format_firebase_sighting(doc.id, doc.to_dict()))
        
        # Add local sightings
        for s in Sighting.query.all():
            sightings.append({
                'id': s.id,
                'timestamp': s.timestamp.isoformat() if s.timestamp else None,
                'best_count': s.best_count,
                'location_type': s.location_type,
                'coordinate': {
                    'latitude': s.latitude,
                    'longitude': s.longitude
                }
            })
        
        return jsonify(sightings)
    except Exception as e:
        print(f"Error fetching sightings: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/colonies', methods=['GET', 'POST'])
def colonies():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Create SQLAlchemy record
            colony = Colony(
                name=data['name'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                current_size=data['current_size'],
                sterilized_count=data['sterilized_count']
            )
            db.session.add(colony)
            db.session.commit()
            
            # Sync to Firebase
            firebase_data = {
                'name': colony.name,
                'location': {
                    'latitude': colony.latitude,
                    'longitude': colony.longitude
                },
                'current_size': colony.current_size,
                'size': colony.current_size,  # For backward compatibility
                'sterilized_count': colony.sterilized_count,
                'monthly_sterilization_rate': data.get('monthly_sterilization_rate', 0),
                'breeding_rate': data.get('breeding_rate', 0.85),
                'kittens_per_litter': data.get('kittens_per_litter', 4),
                'litters_per_year': data.get('litters_per_year', 2.5),
                'kitten_survival_rate': data.get('kitten_survival_rate', 0.75),
                'adult_survival_rate': data.get('adult_survival_rate', 0.85),
                'water_availability': data.get('water_availability', 0.8),
                'shelter_quality': data.get('shelter_quality', 0.7),
                'territory_size': data.get('territory_size', 500),
                'urban_risk': data.get('urban_risk', 0.15),
                'disease_risk': data.get('disease_risk', 0.1),
                'caretaker_support': data.get('caretaker_support', 0.8),
                'feeding_consistency': data.get('feeding_consistency', 0.8),
                'status': 'active',
                'timestamp': datetime.utcnow(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            firebase_db.collection('colonies').add(firebase_data)
            
            return jsonify({
                'id': colony.id,
                'name': colony.name,
                'latitude': colony.latitude,
                'longitude': colony.longitude,
                'current_size': colony.current_size,
                'sterilized_count': colony.sterilized_count,
                'monthly_sterilization_rate': data.get('monthly_sterilization_rate', 0),
                'breeding_rate': data.get('breeding_rate', 0.85),
                'kittens_per_litter': data.get('kittens_per_litter', 4),
                'litters_per_year': data.get('litters_per_year', 2.5),
                'kitten_survival_rate': data.get('kitten_survival_rate', 0.75),
                'adult_survival_rate': data.get('adult_survival_rate', 0.85),
                'water_availability': data.get('water_availability', 0.8),
                'shelter_quality': data.get('shelter_quality', 0.7),
                'territory_size': data.get('territory_size', 500),
                'urban_risk': data.get('urban_risk', 0.15),
                'disease_risk': data.get('disease_risk', 0.1),
                'caretaker_support': data.get('caretaker_support', 0.8),
                'feeding_consistency': data.get('feeding_consistency', 0.8)
            }), 201
        except Exception as e:
            print(f"Error creating colony: {e}")
            return jsonify({'error': str(e)}), 500
    
    try:
        # Get Firebase colonies
        colonies = []
        firebase_docs = firebase_db.collection('colonies').stream()
        for doc in firebase_docs:
            colonies.append(format_firebase_colony(doc.id, doc.to_dict()))
        
        # Add local colonies
        for c in Colony.query.all():
            colonies.append({
                'id': c.id,
                'name': c.name,
                'latitude': c.latitude,
                'longitude': c.longitude,
                'current_size': c.current_size,
                'sterilized_count': c.sterilized_count
            })
        
        return jsonify(colonies)
    except Exception as e:
        print(f"Error fetching colonies: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/colonies/<colony_id>', methods=['PUT'])
def update_firebase_colony(colony_id):
    try:
        data = request.get_json()
        
        # Update Firebase
        firebase_data = {
            'name': data['name'],
            'location': {
                'latitude': data['latitude'],
                'longitude': data['longitude']
            },
            'current_size': data['current_size'],
            'size': data['current_size'],  # For backward compatibility
            'sterilized_count': data['sterilized_count'],
            'monthly_sterilization_rate': data.get('monthly_sterilization_rate', 0),
            'breeding_rate': data.get('breeding_rate', 0.85),
            'kittens_per_litter': data.get('kittens_per_litter', 4),
            'litters_per_year': data.get('litters_per_year', 2.5),
            'kitten_survival_rate': data.get('kitten_survival_rate', 0.75),
            'adult_survival_rate': data.get('adult_survival_rate', 0.85),
            'water_availability': data.get('water_availability', 0.8),
            'shelter_quality': data.get('shelter_quality', 0.7),
            'territory_size': data.get('territory_size', 500),
            'urban_risk': data.get('urban_risk', 0.15),
            'disease_risk': data.get('disease_risk', 0.1),
            'caretaker_support': data.get('caretaker_support', 0.8),
            'feeding_consistency': data.get('feeding_consistency', 0.8),
            'updated_at': datetime.utcnow()
        }
        
        # Update the Firebase document directly using the ID
        colony_ref = firebase_db.collection('colonies').document(colony_id)
        colony_ref.update(firebase_data)
        
        return jsonify({
            'id': colony_id,
            'name': data['name'],
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'current_size': data['current_size'],
            'sterilized_count': data['sterilized_count']
        })
    except Exception as e:
        print(f"Error updating Firebase colony: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/colonies/<int:colony_id>', methods=['PUT'])
def update_colony(colony_id):
    try:
        data = request.get_json()
        colony = Colony.query.get(colony_id)
        
        if not colony:
            return jsonify({'error': 'Colony not found'}), 404
        
        # Update SQLAlchemy record
        colony.name = data['name']
        colony.current_size = data['current_size']
        colony.sterilized_count = data['sterilized_count']
        colony.latitude = data['latitude']
        colony.longitude = data['longitude']
        db.session.commit()
        
        # Update Firebase
        firebase_data = {
            'name': colony.name,
            'location': {
                'latitude': colony.latitude,
                'longitude': colony.longitude
            },
            'current_size': colony.current_size,
            'size': colony.current_size,  # For backward compatibility
            'sterilized_count': colony.sterilized_count,
            'monthly_sterilization_rate': data.get('monthly_sterilization_rate', 0),
            'breeding_rate': data.get('breeding_rate', 0.85),
            'kittens_per_litter': data.get('kittens_per_litter', 4),
            'litters_per_year': data.get('litters_per_year', 2.5),
            'kitten_survival_rate': data.get('kitten_survival_rate', 0.75),
            'adult_survival_rate': data.get('adult_survival_rate', 0.85),
            'water_availability': data.get('water_availability', 0.8),
            'shelter_quality': data.get('shelter_quality', 0.7),
            'territory_size': data.get('territory_size', 500),
            'urban_risk': data.get('urban_risk', 0.15),
            'disease_risk': data.get('disease_risk', 0.1),
            'caretaker_support': data.get('caretaker_support', 0.8),
            'feeding_consistency': data.get('feeding_consistency', 0.8),
            'updated_at': datetime.utcnow()
        }
        
        # Find and update the Firebase document
        colony_ref = None
        docs = firebase_db.collection('colonies').stream()
        for doc in docs:
            doc_data = doc.to_dict()
            if (doc_data.get('name') == colony.name and 
                doc_data.get('location', {}).get('latitude') == colony.latitude and
                doc_data.get('location', {}).get('longitude') == colony.longitude):
                colony_ref = doc.reference
                break
        
        if colony_ref:
            colony_ref.update(firebase_data)
        else:
            # If no matching document found, create a new one
            firebase_db.collection('colonies').add(firebase_data)
        
        return jsonify({
            'id': colony.id,
            'name': colony.name,
            'latitude': colony.latitude,
            'longitude': colony.longitude,
            'current_size': colony.current_size,
            'sterilized_count': colony.sterilized_count,
            'monthly_sterilization_rate': data.get('monthly_sterilization_rate', 0),
            'breeding_rate': data.get('breeding_rate', 0.85),
            'kittens_per_litter': data.get('kittens_per_litter', 4),
            'litters_per_year': data.get('litters_per_year', 2.5),
            'kitten_survival_rate': data.get('kitten_survival_rate', 0.75),
            'adult_survival_rate': data.get('adult_survival_rate', 0.85),
            'water_availability': data.get('water_availability', 0.8),
            'shelter_quality': data.get('shelter_quality', 0.7),
            'territory_size': data.get('territory_size', 500),
            'urban_risk': data.get('urban_risk', 0.15),
            'disease_risk': data.get('disease_risk', 0.1),
            'caretaker_support': data.get('caretaker_support', 0.8),
            'feeding_consistency': data.get('feeding_consistency', 0.8)
        })
    except Exception as e:
        print(f"Error updating colony: {e}")
        return jsonify({'error': str(e)}), 500
