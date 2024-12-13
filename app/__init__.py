from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

def create_app():
    # Load environment variables from .env.local
    load_dotenv('.env.local')

    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Add Firebase configuration to Flask app
    app.config['FIREBASE_API_KEY'] = os.getenv('FIREBASE_API_KEY')
    app.config['FIREBASE_PROJECT_ID'] = os.getenv('FIREBASE_PROJECT_ID')
    app.config['FIREBASE_AUTH_DOMAIN'] = os.getenv('FIREBASE_AUTH_DOMAIN')
    app.config['FIREBASE_STORAGE_BUCKET'] = os.getenv('FIREBASE_STORAGE_BUCKET')
    app.config['FIREBASE_MESSAGING_SENDER_ID'] = os.getenv('FIREBASE_MESSAGING_SENDER_ID')

    # Load button visibility settings
    app.config['SHOW_DOWNLOAD_BUTTON'] = os.getenv('SHOW_DOWNLOAD_BUTTON', 'false').lower() == 'true'
    app.config['SHOW_CLEAR_RESULTS_BUTTON'] = os.getenv('SHOW_CLEAR_RESULTS_BUTTON', 'false').lower() == 'true'
    app.config['SHOW_TEST_PARAMETERS_BUTTON'] = os.getenv('SHOW_TEST_PARAMETERS_BUTTON', 'false').lower() == 'true'

    # Configure CORS
    CORS(app)

    # Import and register blueprints
    from app.routes import simulation_routes, colony_routes, sighting_routes
    app.register_blueprint(simulation_routes.bp)
    app.register_blueprint(colony_routes.bp)
    app.register_blueprint(sighting_routes.bp)

    return app
