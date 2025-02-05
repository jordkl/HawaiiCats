import json
import os
import time
import threading
import traceback
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import GeoPoint
from config.settings import ENABLE_FIREBASE_SYNC

class FirebaseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, GeoPoint):
            return {
                'latitude': obj.latitude,
                'longitude': obj.longitude
            }
        if isinstance(obj, datetime):
            return {'_timestamp': obj.isoformat(), '_type': 'datetime'}
        return super().default(obj)

class CatSightingsStore:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.data_file = os.path.join(data_dir, 'sightings.json')
        self.last_sync_file = os.path.join(data_dir, 'last_sync.txt')
        self.lock = threading.Lock()
        
        if ENABLE_FIREBASE_SYNC:
            try:
                if not firebase_admin._apps:
                    print("Initializing Firebase Admin SDK...")
                    cred_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'firebase-credentials.json')
                    print(f"Looking for credentials at: {cred_path}")
                    if not os.path.exists(cred_path):
                        print(f"Warning: Firebase credentials not found at {cred_path}. Disabling Firebase sync.")
                        self.db = None
                        return
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    print("Firebase Admin SDK initialized successfully")
                
                self.db = firestore.client()
                print("Firestore client created successfully")
            except Exception as e:
                print(f"Warning: Error initializing Firebase: {str(e)}")
                print(f"Stack trace: {traceback.format_exc()}")
                print("Continuing without Firebase sync")
                self.db = None
        else:
            print("Firebase sync is disabled")
            self.db = None

        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)

        # Initialize empty data if file doesn't exist
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)

        if not os.path.exists(self.last_sync_file):
            self._save_last_sync_time(datetime.min)
        
        if ENABLE_FIREBASE_SYNC and self.db is not None:
            self.sync_thread = threading.Thread(target=self._background_sync, daemon=True)
            self.sync_thread.start()
    
    def _save_local_data(self, data):
        with self.lock:
            with open(self.data_file, 'w') as f:
                converted_data = self._convert_firestore_data(data)
                json.dump(converted_data, f, cls=FirebaseEncoder, indent=2)
                print("Local data saved successfully")
    
    def _load_local_data(self):
        with self.lock:
            try:
                with open(self.data_file, 'r') as f:
                    self.local_data = json.load(f)
                    print("Local data loaded successfully")
            except FileNotFoundError:
                print("No local data file found, starting with empty dataset")
                self.local_data = []
            except json.JSONDecodeError as e:
                print(f"Error loading local data: {str(e)}")
                self.local_data = []
            return self.local_data
    
    def _convert_firestore_data(self, data):
        """Convert Firestore data types to serializable format"""
        if isinstance(data, dict):
            return {k: self._convert_firestore_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_firestore_data(item) for item in data]
        elif isinstance(data, GeoPoint):
            return {
                'latitude': data.latitude,
                'longitude': data.longitude
            }
        elif isinstance(data, datetime):
            return {'_timestamp': data.isoformat(), '_type': 'datetime'}
        return data

    def sync_with_firebase(self):
        """Synchronize local data with Firebase"""
        if not ENABLE_FIREBASE_SYNC or self.db is None:
            print("Firebase sync is disabled, skipping sync")
            return

        try:
            print("Starting Firebase sync...")
            last_sync = self._load_last_sync_time()
            print(f"Last sync time: {last_sync}")
            
            # Get all existing sighting IDs before sync
            local_data = self._load_local_data()
            local_ids = {item['id'] for item in local_data}
            
            # Get all current sightings from Firestore
            print("Fetching all current sightings from Firestore...")
            current_docs = self.db.collection('sightings').get()
            current_ids = {doc.id for doc in current_docs}
            
            # Find deleted sightings
            deleted_ids = local_ids - current_ids
            if deleted_ids:
                print(f"Found {len(deleted_ids)} deleted sightings")
            
            # Update local data
            local_data_dict = {item['id']: item for item in local_data if item['id'] not in deleted_ids}
            
            # Update with current data
            for doc in current_docs:
                data = doc.to_dict()
                data['id'] = doc.id
                print(f"DEBUG: Raw Firestore data for {doc.id}:")
                print(data)
                # Convert Firestore types to serializable format
                converted_data = self._convert_firestore_data(data)
                print(f"DEBUG: Converted data for {doc.id}:")
                print(converted_data)
                local_data_dict[doc.id] = converted_data
            
            new_local_data = list(local_data_dict.values())
            self._save_local_data(new_local_data)
            self._save_last_sync_time(datetime.now())
            print(f"Sync completed successfully. Saved {len(new_local_data)} sightings. Removed {len(deleted_ids)} deleted sightings.")
            
        except Exception as e:
            print(f"Error during sync: {str(e)}")
            print(f"Stack trace: {traceback.format_exc()}")
            raise

    def get_all_sightings(self):
        """Get all sightings from local storage"""
        try:
            print("Getting all sightings from local storage...")
            sightings = self._load_local_data()
            
            # Normalize location data and remove user information
            normalized_sightings = []
            for sighting in sightings:
                print(f"DEBUG: Processing sighting {sighting.get('id')}:")
                print("Before normalization:", sighting)
                
                # Create a new dict for the normalized sighting
                normalized = {}
                
                # Copy basic fields with defaults
                normalized['id'] = sighting.get('id')
                normalized['timestamp'] = sighting.get('timestamp')
                normalized['visibleCats'] = int(sighting.get('visibleCats', 0))
                normalized['earNotchesCount'] = int(sighting.get('earNotchesCount', 0))
                normalized['locationType'] = sighting.get('locationType', 'Not specified')
                normalized['visibility'] = sighting.get('visibility', 'Not specified')
                normalized['movementLevel'] = sighting.get('movementLevel', 'Not specified')
                normalized['timeSpent'] = sighting.get('timeSpent', 'Not specified')
                normalized['notes'] = sighting.get('notes', '')
                normalized['isFeeding'] = bool(sighting.get('isFeeding', False))
                normalized['hasProtectedSpecies'] = bool(sighting.get('hasProtectedSpecies', False))
                normalized['photoUrls'] = list(sighting.get('photoUrls', []))
                normalized['feedingTime'] = sighting.get('feedingTime')
                normalized['submitterName'] = sighting.get('submitterName', '')
                normalized['submitterEmail'] = sighting.get('submitterEmail', '')
                
                # Handle coordinate
                location = sighting.get('coordinate')
                if location:
                    lat = location.get('_latitude') or location.get('latitude') or location.get('lat')
                    lng = location.get('_longitude') or location.get('longitude') or location.get('lng')
                    
                    if lat is not None and lng is not None:
                        try:
                            lat = float(lat)
                            lng = float(lng)
                            if -90 <= lat <= 90 and -180 <= lng <= 180:
                                normalized['coordinate'] = {
                                    'latitude': lat,
                                    'longitude': lng
                                }
                            else:
                                normalized['coordinate'] = None
                        except (ValueError, TypeError):
                            normalized['coordinate'] = None
                    else:
                        normalized['coordinate'] = None
                else:
                    normalized['coordinate'] = None
                
                print("After normalization:", normalized)
                normalized_sightings.append(normalized)
            
            print(f"Found {len(normalized_sightings)} sightings in local storage")
            return normalized_sightings
            
        except Exception as e:
            print(f"Error getting sightings: {str(e)}")
            print(f"Stack trace: {traceback.format_exc()}")
            raise

    def add_sighting(self, sighting_data):
        """Add a new sighting to the store"""
        try:
            # Generate a unique ID for the sighting
            sighting_id = f"sighting_{int(time.time() * 1000)}"
            sighting_data['id'] = sighting_id
            
            # Add timestamp if not present
            if 'timestamp' not in sighting_data:
                sighting_data['timestamp'] = datetime.now().isoformat()
            
            # Create coordinate GeoPoint from latitude/longitude
            if 'latitude' in sighting_data and 'longitude' in sighting_data:
                sighting_data['coordinate'] = {
                    'latitude': float(sighting_data['latitude']),
                    'longitude': float(sighting_data['longitude'])
                }
                # Remove individual lat/lng fields to avoid duplication
                sighting_data.pop('latitude', None)
                sighting_data.pop('longitude', None)
            
            # Ensure numeric fields are properly typed
            sighting_data['visibleCats'] = int(sighting_data.get('visibleCats', 0))
            sighting_data['earNotchesCount'] = int(sighting_data.get('earNotchesCount', 0))
            
            # Ensure boolean fields are properly typed
            sighting_data['isFeeding'] = bool(sighting_data.get('isFeeding', False))
            sighting_data['hasProtectedSpecies'] = bool(sighting_data.get('hasProtectedSpecies', False))
            
            # Ensure arrays are properly initialized
            sighting_data['photoUrls'] = list(sighting_data.get('photoUrls', []))
            
            # Ensure submitter fields are properly typed
            sighting_data['submitterName'] = str(sighting_data.get('submitterName', ''))
            sighting_data['submitterEmail'] = str(sighting_data.get('submitterEmail', ''))
            
            # Load current data
            local_data = self._load_local_data()
            
            # Add new sighting
            local_data.append(sighting_data)
            
            # Save to local storage
            self._save_local_data(local_data)
            
            # If Firebase is enabled, add to Firestore
            if ENABLE_FIREBASE_SYNC and self.db is not None:
                firestore_data = sighting_data.copy()
                
                # Convert coordinate to GeoPoint for Firestore
                if 'coordinate' in firestore_data:
                    coord = firestore_data['coordinate']
                    firestore_data['coordinate'] = GeoPoint(
                        coord['latitude'],
                        coord['longitude']
                    )
                
                # Add to Firestore
                self.db.collection('sightings').document(sighting_id).set(firestore_data)
            
            return sighting_id
        except Exception as e:
            print(f"Error adding sighting: {str(e)}")
            print(f"Stack trace: {traceback.format_exc()}")
            raise

    def force_sync(self):
        """Force an immediate sync with Firebase"""
        if ENABLE_FIREBASE_SYNC and self.db is not None:
            self.sync_with_firebase()

    def _save_last_sync_time(self, sync_time):
        with open(self.last_sync_file, 'w') as f:
            f.write(sync_time.isoformat())
    
    def _load_last_sync_time(self):
        try:
            with open(self.last_sync_file, 'r') as f:
                return datetime.fromisoformat(f.read().strip())
        except (ValueError, FileNotFoundError) as e:
            print(f"Error loading last sync time: {str(e)}")
            return datetime.min
    
    def _background_sync(self):
        """Background thread for periodic Firebase sync"""
        print("Starting background sync...")
        while True:
            try:
                if ENABLE_FIREBASE_SYNC and self.db is not None:
                    print("Starting Firebase sync...")
                    self.sync_with_firebase()
                time.sleep(60)  # Sync every minute
            except Exception as e:
                print(f"Error during background sync: {str(e)}")
                print(f"Stack trace: {traceback.format_exc()}")
                time.sleep(60)  # Still wait before retrying

# Global instance
_store = None

def init_store(data_dir='data'):
    """Initialize the global store instance"""
    global _store
    if _store is None:
        # Use absolute path for data directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(base_dir, data_dir)
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        _store = CatSightingsStore(data_dir)
    return _store

def get_store():
    if _store is None:
        raise RuntimeError("Store not initialized. Call init_store() first.")
    return _store
