from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

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

with app.app_context():
    # Add a test sighting in Honolulu
    test_sighting = Sighting(
        latitude=21.3069,
        longitude=-157.8583,
        best_count=3,
        location_type='street',
        timestamp=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    db.session.add(test_sighting)
    db.session.commit()
    
    print("Test sighting added successfully!")
    
    # Verify the sighting was added
    sightings = Sighting.query.all()
    print("\nSightings in database:")
    for s in sightings:
        print(f"ID: {s.id}, Lat: {s.latitude}, Lng: {s.longitude}, Count: {s.best_count}")
