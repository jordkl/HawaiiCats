import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# Firebase Configuration
FIREBASE_CONFIG = {
    'apiKey': os.getenv('FIREBASE_API_KEY'),
    'projectId': os.getenv('FIREBASE_PROJECT_ID'),
    'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
    'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
}

# Application Configuration
DEBUG = True
HOST = '0.0.0.0'
PORT = 5001

# Logging Configuration
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'app', 'static')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'app', 'templates')
