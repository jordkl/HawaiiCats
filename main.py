from app import create_app
from app.tools.cat_simulation.utils.logging_utils import setup_logging
from app.tools.sightings.store import init_store
from app.auth import init_firebase
import logging
import traceback
from dotenv import load_dotenv
import os

# Initialize logging
setup_logging()

# Initialize the sightings store
init_store()

# Load environment variables from .env.local if it exists, otherwise try .env
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
else:
    load_dotenv('.env')

# Initialize Firebase Admin SDK
try:
    init_firebase()
except Exception as e:
    logging.warning(f"Failed to initialize Firebase: {str(e)}")
    logging.warning("Continuing without Firebase authentication...")

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        logging.error(f"Error starting server: {str(e)}")
        logging.error(traceback.format_exc())
