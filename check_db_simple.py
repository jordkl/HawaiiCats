from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app_dir = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app_dir, 'app', 'database.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Sighting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    best_count = db.Column(db.Integer)
    location_type = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)

class Colony(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    current_size = db.Column(db.Integer, nullable=False)
    sterilized_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

with app.app_context():
    print("\nSightings in database:")
    sightings = Sighting.query.all()
    for s in sightings:
        print(f"ID: {s.id}, Lat: {s.latitude}, Lng: {s.longitude}, Count: {s.best_count}")
        
    print("\nColonies in database:")
    colonies = Colony.query.all()
    for c in colonies:
        print(f"ID: {c.id}, Name: {c.name}, Lat: {c.latitude}, Lng: {c.longitude}")
