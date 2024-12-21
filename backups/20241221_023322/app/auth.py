from functools import wraps
from flask import redirect, url_for, request, session
import firebase_admin
from firebase_admin import auth, credentials
import os

def init_firebase():
    """Initialize Firebase Admin SDK"""
    # Check if Firebase sync is enabled
    if os.getenv('ENABLE_FIREBASE_SYNC', 'false').lower() == 'false':
        print("Firebase sync is disabled")
        return

    try:
        # Check if already initialized
        firebase_admin.get_app()
        print("Firebase Admin SDK already initialized")
    except ValueError:
        print("Initializing Firebase Admin SDK...")
        # Get the path to the service account key file
        cred_path = os.path.join(os.path.dirname(__file__), 'firebase-credentials.json')
        print(f"Looking for credentials at: {cred_path}")
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Firebase credentials file not found at {cred_path}")
        
        # Initialize the app
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully")

def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication if Firebase sync is disabled
        if os.getenv('ENABLE_FIREBASE_SYNC', 'false').lower() == 'false':
            return f(*args, **kwargs)

        # Get the ID token from the session
        id_token = session.get('id_token')
        if not id_token:
            return redirect(url_for('auth.login'))
        
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            # Add the user to the request context
            request.user = decoded_token
            return f(*args, **kwargs)
        except:
            # If token is invalid, redirect to login
            return redirect(url_for('auth.login'))
            
    return decorated_function
