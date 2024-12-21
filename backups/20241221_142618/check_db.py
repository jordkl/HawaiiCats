from app import create_app, db
from app.models import Sighting, Colony

def check_db():
    app = create_app()
    with app.app_context():
        sightings = Sighting.query.all()
        colonies = Colony.query.all()
        
        print("\nSightings in database:")
        for s in sightings:
            print(f"ID: {s.id}, Lat: {s.latitude}, Lng: {s.longitude}, Count: {s.best_count}")
            
        print("\nColonies in database:")
        for c in colonies:
            print(f"ID: {c.id}, Name: {c.name}, Lat: {c.latitude}, Lng: {c.longitude}")

if __name__ == '__main__':
    check_db()
