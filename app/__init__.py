from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    # Get the absolute path to the app directory and project root
    app_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(app_dir)
    
    # Load environment variables from .env.local using absolute path
    env_path = os.path.join(project_root, '.env.local')
    load_dotenv(env_path)

    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app_dir, 'database.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)

    # Initialize Firebase Admin SDK if not already initialized
    try:
        firebase_admin.get_app()
    except ValueError:
        cred_path = os.path.join(project_root, 'tools', 'sightings', 'firebase-credentials.json')
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Firebase credentials file not found at {cred_path}")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

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

    # Set secret key for sessions
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev')

    # Configure CORS
    CORS(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Register blueprints
    from .routes.main_routes import bp as main_bp
    from .routes.colony_routes import bp as colony_bp
    from .routes.sighting_routes import bp as sighting_bp
    from .routes.auth_routes import bp as auth_bp
    from .routes.api_routes import bp as api_bp
    from .routes.simulation_routes import bp as simulation_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(colony_bp)
    app.register_blueprint(sighting_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(simulation_bp)

    return app
