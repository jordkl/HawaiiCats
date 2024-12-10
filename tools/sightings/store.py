import json
import os
import time
import threading
import traceback
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import GeoPoint

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
        
        try:
            if not firebase_admin._apps:
                print("Initializing Firebase Admin SDK...")
                cred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'firebase-credentials.json')
                print(f"Looking for credentials at: {cred_path}")
                if not os.path.exists(cred_path):
                    raise FileNotFoundError(f"Firebase credentials file not found at {cred_path}")
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK initialized successfully")
            
            self.db = firestore.client()
            print("Firestore client created successfully")
        except Exception as e:
            print(f"Error initializing Firebase: {str(e)}")
            print(f"Stack trace: {traceback.format_exc()}")
            raise
        
        os.makedirs(data_dir, exist_ok=True)
        
        if not os.path.exists(self.data_file):
            self._save_local_data([])
        
        if not os.path.exists(self.last_sync_file):
            self._save_last_sync_time(datetime.min)
        
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
                # Convert Firestore types to serializable format
                converted_data = self._convert_firestore_data(data)
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
            for sighting in sightings:
                # Safely normalize location with multiple fallbacks
                location = None
                if sighting.get('userLocation'):
                    location = sighting['userLocation']
                elif sighting.get('coordinate'):
                    location = sighting['coordinate']
                
                if location:
                    # Try different possible location property names
                    lat = location.get('_latitude') or location.get('latitude') or location.get('lat')
                    lng = location.get('_longitude') or location.get('longitude') or location.get('lng')
                    
                    if lat is not None and lng is not None:
                        sighting['coordinate'] = {
                            'latitude': float(lat),
                            'longitude': float(lng)
                        }
                    else:
                        # If no valid coordinates found, set coordinate to None
                        sighting['coordinate'] = None
                else:
                    sighting['coordinate'] = None
                
                # Normalize timestamp
                timestamp_obj = sighting.get('timestamp')
                if isinstance(timestamp_obj, dict) and '_timestamp' in timestamp_obj:
                    sighting['timestamp'] = timestamp_obj['_timestamp']
                
                # Remove user-specific information
                sighting.pop('userId', None)
                sighting.pop('userLocation', None)
                sighting.pop('userEmail', None)
                sighting.pop('userName', None)
            
            print(f"Found {len(sightings)} sightings in local storage")
            return sightings
        except Exception as e:
            print(f"Error getting sightings: {str(e)}")
            print(f"Stack trace: {traceback.format_exc()}")
            raise

    def force_sync(self):
        """Force an immediate sync with Firebase"""
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
        while True:
            try:
                print("Starting background sync...")
                self.sync_with_firebase()
                print("Background sync completed successfully")
            except Exception as e:
                print(f"Error during background sync: {str(e)}")
                print(f"Stack trace: {traceback.format_exc()}")
            time.sleep(3600)

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
