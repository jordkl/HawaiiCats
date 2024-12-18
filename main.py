from app import create_app
from tools.cat_simulation.utils.logging_utils import setup_logging
from tools.sightings.store import init_store
from app.auth import init_firebase
import logging
import traceback
from dotenv import load_dotenv
import os

# Initialize logging
setup_logging()

# Initialize the sightings store
init_store()

# Load environment variables from .env.local
load_dotenv('.env.local')

# Initialize Firebase Admin SDK
init_firebase()

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
