from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from datetime import datetime
from ..models import Colony, Sighting
from .. import db
import os
import requests
import re
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Set up logging to use only StreamHandler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

bp = Blueprint('api', __name__, url_prefix='/api')
firebase_db = firestore.client()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def format_firebase_colony(doc_id, data):
    """Helper function to format Firebase colony data"""
    location = data.get('location', {})
    logger.info(f"Raw colony data from Firebase: {data}")
    formatted = {
        'id': doc_id,
        'name': data.get('name', ''),
        'latitude': location.get('latitude') if location else data.get('latitude'),
        'longitude': location.get('longitude') if location else data.get('longitude'),
        'currentSize': data.get('currentSize') or data.get('current_size') or data.get('size', 0),
        'sterilizedCount': data.get('sterilizedCount') or data.get('sterilized_count', 0),
        # Additional fields stored but not used in frontend
        'waterAvailability': data.get('waterAvailability') or data.get('water_availability'),
        'shelterQuality': data.get('shelterQuality') or data.get('shelter_quality'),
        'territorySize': data.get('territorySize') or data.get('territory_size'),
        'status': data.get('status')
    }
    logger.info(f"Formatted colony data: {formatted}")
    return formatted

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
    if coordinate is None and isinstance(data.get('user_location'), firestore.GeoPoint):
        geopoint = data['user_location']
        coordinate = {
            'latitude': geopoint.latitude,
            'longitude': geopoint.longitude
        }
    
    # Get details if they exist
    details = data.get('details', {})
    
    return {
        'id': doc_id,
        'timestamp': data.get('timestamp'),
        'best_count': data.get('best_count') or details.get('best_count', 0),
        'location_type': data.get('location_type') or details.get('location_type', ''),
        'coordinate': coordinate,
        'visible_cats': data.get('visible_cats') or details.get('visible_cats'),
        'min_count': data.get('min_count') or details.get('min_count'),
        'max_count': data.get('max_count') or details.get('max_count'),
        'movement_level': data.get('movement_level') or details.get('movement_level'),
        'uncertainty_level': data.get('uncertainty_level') or details.get('uncertainty_level'),
        'is_feeding': data.get('is_feeding') or details.get('is_feeding', False),
        'time_spent': data.get('time_spent') or details.get('time_spent'),
        'notes': data.get('notes') or details.get('notes', '')
    }

def is_valid_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def verify_recaptcha(token):
    """Verify reCAPTCHA token"""
    try:
        secret_key = os.environ.get('RECAPTCHA_SECRET_KEY')
        if not secret_key:
            logger.warning("Warning: RECAPTCHA_SECRET_KEY not set")
            return True  # Allow in development
            
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': secret_key,
                'response': token
            }
        )
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        logger.error(f"reCAPTCHA verification error: {e}")
        return False

@bp.before_request
def log_request_info():
    if request.method in ['POST', 'PUT']:
        try:
            # Get the raw request data
            raw_data = request.get_data()
            logger.info(f"Raw request body: {raw_data.decode('utf-8')}")
            
            # Try to parse as JSON
            if request.is_json:
                json_data = request.get_json(force=True)
                logger.info(f"Parsed JSON data: {json_data}")
        except Exception as e:
            logger.error(f"Error logging request: {e}")

@bp.route('/sightings', methods=['GET', 'POST'])
def sightings():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Create SQLAlchemy record
            sighting = Sighting(
                latitude=data['latitude'],
                longitude=data['longitude'],
                best_count=data.get('best_count'),
                location_type=data.get('location_type')
            )
            db.session.add(sighting)
            db.session.commit()
            
            # Sync to Firebase using GeoPoint for coordinates
            firebase_data = {
                'coordinate': firestore.GeoPoint(float(sighting.latitude), float(sighting.longitude)),
                'best_count': sighting.best_count,
                'location_type': sighting.location_type,
                'timestamp': datetime.utcnow(),
                'details': {
                    'best_count': sighting.best_count,
                    'location_type': sighting.location_type,
                    'is_feeding': False,
                    'time_spent': 'quick',
                    'uncertainty_level': 'medium',
                    'movement_level': 'low',
                    'notes': '',
                    'visible_cats': sighting.best_count,
                    'min_count': max(0, sighting.best_count - 3),
                    'max_count': sighting.best_count + 3
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
            logger.error(f"Error creating sighting: {e}")
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
        logger.error(f"Error fetching sightings: {e}")
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
                current_size=data['currentSize'],
                sterilized_count=data['sterilizedCount']
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
                'currentSize': colony.current_size,
                'sterilizedCount': colony.sterilized_count,
                'monthlysterilizationRate': data.get('monthlysterilizationRate', 0),
                'breedingRate': data.get('breedingRate', 0.85),
                'kittensPerLitter': data.get('kittensPerLitter', 4),
                'littersPerYear': data.get('littersPerYear', 2.5),
                'kittenSurvivalRate': data.get('kittenSurvivalRate', 0.75),
                'adultSurvivalRate': data.get('adultSurvivalRate', 0.85),
                'waterAvailability': data.get('waterAvailability', 0.8),
                'shelterQuality': data.get('shelterQuality', 0.7),
                'territorySize': data.get('territorySize', 500),
                'urbanRisk': data.get('urbanRisk', 0.15),
                'diseaseRisk': data.get('diseaseRisk', 0.1),
                'caretakerSupport': data.get('caretakerSupport', 0.8),
                'feedingConsistency': data.get('feedingConsistency', 0.8),
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
                'currentSize': colony.current_size,
                'sterilizedCount': colony.sterilized_count,
                'monthlysterilizationRate': data.get('monthlysterilizationRate', 0),
                'breedingRate': data.get('breedingRate', 0.85),
                'kittensPerLitter': data.get('kittensPerLitter', 4),
                'littersPerYear': data.get('littersPerYear', 2.5),
                'kittenSurvivalRate': data.get('kittenSurvivalRate', 0.75),
                'adultSurvivalRate': data.get('adultSurvivalRate', 0.85),
                'waterAvailability': data.get('waterAvailability', 0.8),
                'shelterQuality': data.get('shelterQuality', 0.7),
                'territorySize': data.get('territorySize', 500),
                'urbanRisk': data.get('urbanRisk', 0.15),
                'diseaseRisk': data.get('diseaseRisk', 0.1),
                'caretakerSupport': data.get('caretakerSupport', 0.8),
                'feedingConsistency': data.get('feedingConsistency', 0.8)
            }), 201
        except Exception as e:
            logger.error(f"Error creating colony: {e}")
            return jsonify({'error': str(e)}), 500
    
    if request.method == 'GET':
        try:
            # Get Firebase colonies
            colonies = []
            logger.info("Fetching colonies from Firebase...")
            firebase_docs = firebase_db.collection('colonies').stream()
            
            for doc in firebase_docs:
                doc_dict = doc.to_dict()
                logger.info(f"Raw Firebase doc {doc.id}: {doc_dict}")
                try:
                    formatted = format_firebase_colony(doc.id, doc_dict)
                    logger.info(f"Formatted colony: {formatted}")
                    colonies.append(formatted)
                except Exception as e:
                    logger.error(f"Error formatting colony {doc.id}: {e}")
            
            # Add local colonies
            logger.info("Fetching local colonies...")
            local_colonies = Colony.query.all()
            for c in local_colonies:
                try:
                    local_colony = {
                        'id': c.id,
                        'name': c.name,
                        'latitude': c.latitude,
                        'longitude': c.longitude,
                        'currentSize': c.current_size,
                        'sterilizedCount': c.sterilized_count
                    }
                    logger.info(f"Adding local colony: {local_colony}")
                    colonies.append(local_colony)
                except Exception as e:
                    logger.error(f"Error adding local colony {c.id}: {e}")
            
            logger.info(f"Total colonies to return: {len(colonies)}")
            return jsonify(colonies)
        except Exception as e:
            logger.error(f"Error in /colonies GET: {e}")
            return jsonify({'error': str(e)}), 500

@bp.route('/colonies/<string:colony_id>', methods=['PUT'])
def update_colony(colony_id):
    try:
        logger.info(f"Received PUT request for colony {colony_id}")
        
        # Log raw request data
        data = request.get_json()
        logger.info(f"Raw request data type: {type(data)}")
        logger.info(f"Raw request data keys: {data.keys() if data else None}")
        logger.info(f"Raw request data: {data}")
        
        if not data:
            logger.error("No data provided in request")
            return jsonify({'error': 'No data provided'}), 400

        # Get the colony from Firebase
        colony_ref = firebase_db.collection('colonies').document(colony_id)
        colony_doc = colony_ref.get()
        
        if not colony_doc.exists:
            logger.error(f"Colony {colony_id} not found")
            return jsonify({'error': 'Colony not found'}), 404

        current_colony = colony_doc.to_dict()
        logger.info(f"Current colony data: {current_colony}")

        # Validate required fields
        if not data.get('name'):
            logger.error("Colony name is required but not provided")
            return jsonify({'error': 'Missing required field: name'}), 400
        
        # Validate numeric fields
        try:
            # Log the population-related fields we receive
            logger.info(f"Checking population fields in data: {data}")
            
            # Get currentSize from request data
            current_size = data.get('currentSize')
            if current_size is None:
                logger.error("Population size not found in request data")
                return jsonify({'error': 'Missing required field: currentSize'}), 400
            
            try:
                current_size = int(current_size)
                logger.info(f"Successfully converted population size to int: {current_size}")
            except (ValueError, TypeError) as e:
                logger.error(f"Failed to convert population size to int: {e}")
                return jsonify({'error': f'Invalid population size value: {current_size}'}), 400
            
            sterilized_count = int(data.get('sterilizedCount', 0))
            logger.info(f"Final values - current_size: {current_size}, sterilized_count: {sterilized_count}")
            
            if current_size < 0 or sterilized_count < 0:
                logger.error(f"Invalid negative values - current_size: {current_size}, sterilized_count: {sterilized_count}")
                return jsonify({'error': 'Population and sterilized count must be non-negative'}), 400
            if sterilized_count > current_size:
                logger.error(f"Sterilized count ({sterilized_count}) greater than current size ({current_size})")
                return jsonify({'error': 'Sterilized count cannot be greater than total population'}), 400
        except ValueError as e:
            logger.error(f"Error converting numeric values: {e}")
            return jsonify({'error': 'Invalid numeric values provided'}), 400
        
        # Prepare Firebase data
        firebase_data = {
            'name': data['name'],
            'location': {
                'latitude': float(data['latitude']),
                'longitude': float(data['longitude'])
            },
            'currentSize': current_size,  # Use only one field name
            'sterilizedCount': sterilized_count,
            'notes': data.get('notes', ''),
            'monthlysterilizationRate': float(data.get('monthlysterilizationRate', 0)),
            'breedingRate': float(data.get('breedingRate', 0.85)),
            'kittensPerLitter': float(data.get('kittensPerLitter', 4)),
            'littersPerYear': float(data.get('littersPerYear', 2.5)),
            'kittenSurvivalRate': float(data.get('kittenSurvivalRate', 0.75)),
            'adultSurvivalRate': float(data.get('adultSurvivalRate', 0.85)),
            'waterAvailability': float(data.get('waterAvailability', 0.8)),
            'shelterQuality': float(data.get('shelterQuality', 0.7)),
            'territorySize': int(data.get('territorySize', 500)),
            'urbanRisk': float(data.get('urbanRisk', 0.15)),
            'diseaseRisk': float(data.get('diseaseRisk', 0.1)),
            'caretakerSupport': float(data.get('caretakerSupport', 0.8)),
            'feedingConsistency': float(data.get('feedingConsistency', 0.8)),
            'updated_at': datetime.utcnow()
        }
        
        logger.info(f"Prepared Firebase data: {firebase_data}")
        
        # Update Firebase
        colony_ref.update(firebase_data)
        logger.info("Successfully updated Firebase")
        
        # Return the updated data
        response_data = {
            'id': colony_id,
            **firebase_data
        }
        logger.info(f"Sending response: {response_data}")
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error updating colony: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@bp.route('/submit-beta', methods=['POST'])
@limiter.limit("5 per hour")  # Limit to 5 submissions per hour per IP
def submit_beta_form():
    """Handle HubSpot beta form submission with spam protection"""
    try:
        data = request.json
        logger.info(f"Received form data: {data}")
        
        # Basic validation
        if not all(data.get(field) for field in ['firstname', 'lastname', 'email']):
            logger.info(f"Missing required fields. Received fields: {data.keys()}")
            return jsonify({
                "success": False,
                "message": "All fields are required"
            }), 400
            
        # Email validation
        if not is_valid_email(data['email']):
            logger.info(f"Invalid email format: {data['email']}")
            return jsonify({
                "success": False,
                "message": "Invalid email format"
            }), 400
            
        # reCAPTCHA verification
        recaptcha_token = request.headers.get('X-Recaptcha-Token')
        logger.info(f"reCAPTCHA token present: {bool(recaptcha_token)}")
        if not recaptcha_token or not verify_recaptcha(recaptcha_token):
            logger.info("reCAPTCHA verification failed")
            return jsonify({
                "success": False,
                "message": "Invalid reCAPTCHA"
            }), 400
            
        # HubSpot API configuration from environment variables
        portal_id = os.environ.get('HUBSPOT_PORTAL_ID')
        form_id = os.environ.get('HUBSPOT_FORM_ID')
        access_token = os.environ.get('HUBSPOT_ACCESS_TOKEN')
        
        logger.info(f"HubSpot Configuration - Portal ID: {portal_id}, Form ID: {form_id}, Token present: {bool(access_token)}")
        
        if not all([portal_id, form_id, access_token]):
            missing = []
            if not portal_id: missing.append('HUBSPOT_PORTAL_ID')
            if not form_id: missing.append('HUBSPOT_FORM_ID')
            if not access_token: missing.append('HUBSPOT_ACCESS_TOKEN')
            error_msg = f"Missing HubSpot configuration: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Prepare the submission data
        submission = {
            "fields": [
                {
                    "name": "firstname",
                    "value": data.get('firstname')[:50]  # Limit length
                },
                {
                    "name": "lastname",
                    "value": data.get('lastname')[:50]  # Limit length
                },
                {
                    "name": "email",
                    "value": data.get('email')[:100]  # Limit length
                }
            ],
            "context": {
                "pageUri": request.headers.get('Referer'),
                "pageName": "Hawaii Cats Beta Signup",
                "ipAddress": request.headers.get('X-Forwarded-For', request.remote_addr)
            }
        }
        
        logger.info(f"Submitting to HubSpot with portal_id={portal_id}, form_id={form_id}")
        logger.info(f"Submission data: {submission}")
        
        # Submit to HubSpot
        try:
            response = requests.post(
                f"https://api.hsforms.com/submissions/v3/integration/submit/{portal_id}/{form_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=submission,
                timeout=10  # Add timeout to prevent hanging
            )
            
            logger.info(f"HubSpot Response Status: {response.status_code}")
            logger.info(f"HubSpot Response Headers: {dict(response.headers)}")
            logger.info(f"HubSpot Response Body: {response.text}")
            
            if not response.ok:
                error_body = response.json() if response.text else "No error details available"
                logger.error(f"HubSpot Error Details: {error_body}")
                raise requests.exceptions.RequestException(f"HubSpot API error: {error_body}")
                
            response.raise_for_status()
            return jsonify({"success": True, "message": "Form submitted successfully"})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HubSpot API Error: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {dict(e.response.headers)}")
                logger.error(f"Response content: {e.response.text}")
            raise
                
        except Exception as e:
            logger.error(f"Server Error: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "message": "Error submitting form to HubSpot"
            }), 500
    except ValueError as e:
        logger.error(f"Configuration Error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Server configuration error"
        }), 500
    except requests.exceptions.RequestException as e:
        logger.error(f"HubSpot API Error: {str(e)}")
        logger.error(f"Response content: {e.response.text if hasattr(e, 'response') else 'No response content'}")
        return jsonify({
            "success": False,
            "message": "Error submitting form to HubSpot"
        }), 500
    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Server error processing form submission"
        }), 500
