from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
import json
import os
from firebase_admin import firestore
from .config import DEFAULT_PARAMS

@dataclass
class ColonyReport:
    total_cats: int
    sterilized_cats: int
    kittens_observed: int
    report_date: datetime
    reporter_notes: str
    environmental_factors: Dict[str, float]

@dataclass
class Colony:
    name: str
    size: int
    status: str
    notes: str
    latitude: float
    longitude: float
    timestamp: datetime
    id: Optional[str] = None
    
    # Basic colony information
    current_size: Optional[int] = None
    sterilized_count: Optional[int] = None
    
    # Environmental factors
    water_availability: Optional[float] = None
    shelter_quality: Optional[float] = None
    territory_size: Optional[float] = None
    
    # Caretaker support
    caretaker_support: Optional[float] = None
    feeding_consistency: Optional[float] = None
    base_food_capacity: Optional[float] = None
    food_scaling_factor: Optional[float] = None
    
    # Breeding parameters
    breeding_rate: Optional[float] = None
    kittens_per_litter: Optional[int] = None
    litters_per_year: Optional[int] = None
    seasonal_breeding_amplitude: Optional[float] = None
    peak_breeding_month: Optional[int] = None
    
    # Survival and mortality
    kitten_survival_rate: Optional[float] = None
    adult_survival_rate: Optional[float] = None
    density_mortality_factor: Optional[float] = None
    mortality_threshold: Optional[int] = None
    survival_density_factor: Optional[float] = None
    
    # Risk factors
    urban_risk: Optional[float] = None
    disease_risk: Optional[float] = None
    natural_risk: Optional[float] = None
    
    # Population metrics
    total_cats: Optional[int] = None
    sterilized_cats: Optional[int] = None
    estimated_kittens: Optional[int] = None
    last_report_date: Optional[datetime] = None
    
    # Historical data
    reports: List[ColonyReport] = None

    def __post_init__(self):
        if self.reports is None:
            self.reports = []

    def add_report(self, report: ColonyReport):
        """Add a new report and update colony metrics"""
        self.reports.append(report)
        self.last_report_date = report.report_date
        
        # Update colony metrics based on the latest report
        self.total_cats = report.total_cats
        self.sterilized_cats = report.sterilized_cats
        self.estimated_kittens = report.kittens_observed
        
        # Update environmental factors using exponential moving average
        alpha = 0.7  # Weight for new observations
        for factor, value in report.environmental_factors.items():
            current_value = getattr(self, factor, None)
            if current_value is None:
                setattr(self, factor, value)
            else:
                setattr(self, factor, (alpha * value) + ((1 - alpha) * current_value))

    def to_dict(self):
        base_dict = {
            'id': self.id,
            'name': self.name,
            'size': self.size,
            'status': self.status,
            'notes': self.notes,
            'location': [self.latitude, self.longitude],
            'timestamp': self.timestamp.isoformat(),
            'territory_size': self.territory_size,
            'caretaker_support': self.caretaker_support,
            'feeding_consistency': self.feeding_consistency,
            'urban_risk': self.urban_risk,
            'shelter_quality': self.shelter_quality,
            'food_availability': self.food_availability,
            'water_availability': self.water_availability,
            'total_cats': self.total_cats,
            'sterilized_cats': self.sterilized_cats,
            'estimated_kittens': self.estimated_kittens,
            'last_report_date': self.last_report_date.isoformat() if self.last_report_date else None,
            'reports': [
                {
                    'total_cats': r.total_cats,
                    'sterilized_cats': r.sterilized_cats,
                    'kittens_observed': r.kittens_observed,
                    'report_date': r.report_date.isoformat(),
                    'reporter_notes': r.reporter_notes,
                    'environmental_factors': r.environmental_factors
                }
                for r in self.reports
            ] if self.reports else []
        }
        return {k: v for k, v in base_dict.items() if v is not None}

    @classmethod
    def from_dict(cls, data):
        # Convert reports if they exist
        reports = None
        if 'reports' in data:
            reports = [
                ColonyReport(
                    total_cats=r['total_cats'],
                    sterilized_cats=r['sterilized_cats'],
                    kittens_observed=r['kittens_observed'],
                    report_date=datetime.fromisoformat(r['report_date']),
                    reporter_notes=r['reporter_notes'],
                    environmental_factors=r['environmental_factors']
                )
                for r in data['reports']
            ]

        return cls(
            id=data.get('id'),
            name=data['name'],
            size=data['size'],
            status=data['status'],
            notes=data['notes'],
            latitude=data['location'][0],
            longitude=data['location'][1],
            timestamp=datetime.fromisoformat(data['timestamp']),
            territory_size=data.get('territory_size'),
            caretaker_support=data.get('caretaker_support'),
            feeding_consistency=data.get('feeding_consistency'),
            urban_risk=data.get('urban_risk'),
            shelter_quality=data.get('shelter_quality'),
            food_availability=data.get('food_availability'),
            water_availability=data.get('water_availability'),
            total_cats=data.get('total_cats'),
            sterilized_cats=data.get('sterilized_cats'),
            estimated_kittens=data.get('estimated_kittens'),
            last_report_date=datetime.fromisoformat(data['last_report_date']) if data.get('last_report_date') else None,
            reports=reports
        )

    def get_simulation_params(self):
        """Convert colony data to simulation parameters"""
        params = DEFAULT_PARAMS.copy()
        
        # Update params based on colony data if available
        if self.territory_size is not None:
            params['territory_size'] = self.territory_size
        if self.caretaker_support is not None:
            params['caretaker_support'] = self.caretaker_support
        if self.feeding_consistency is not None:
            params['feeding_consistency'] = self.feeding_consistency
        if self.urban_risk is not None:
            params['urban_risk'] = self.urban_risk
        if self.shelter_quality is not None:
            params['shelter_quality'] = self.shelter_quality
        if self.food_availability is not None:
            params['base_food_capacity'] = self.food_availability
        if self.water_availability is not None:
            params['water_availability'] = self.water_availability
            
        return params

class ColonyManager:
    def __init__(self):
        self.db = firestore.client()
        self.colonies_ref = self.db.collection('colonies')

    def update_colony(self, colony_id: str, data: dict):
        """Update a colony in both Firestore and cache."""
        try:
            # Get the colony reference
            colony_ref = self.colonies_ref.document(colony_id)
            colony_doc = colony_ref.get()
            
            if not colony_doc.exists:
                return None
                
            # Update in Firestore
            colony_ref.update(data)
            
            # Get the updated document
            updated_doc = colony_ref.get()
            return updated_doc
            
        except Exception as e:
            print(f"Error updating colony {colony_id}: {str(e)}")
            raise e

    def get_colony(self, colony_id: str):
        """Get a colony by ID from Firestore."""
        try:
            colony_ref = self.colonies_ref.document(colony_id)
            colony_doc = colony_ref.get()
            
            if not colony_doc.exists:
                return None
                
            return colony_doc
            
        except Exception as e:
            print(f"Error getting colony {colony_id}: {str(e)}")
            return None

    def get_colonies(self):
        """Get all colonies from Firestore."""
        try:
            colonies = []
            for doc in self.colonies_ref.stream():
                colony_data = doc.to_dict()
                colony_data['id'] = doc.id
                colonies.append(colony_data)
            return colonies
        except Exception as e:
            print(f"Error getting colonies: {str(e)}")
            return []

    def add_colony(self, colony: Colony) -> Colony:
        """Add a new colony"""
        try:
            # Generate a simple ID if none exists
            if not colony.id:
                colony.id = str(len(self.get_colonies()) + 1)
            
            # Add to Firestore
            self.colonies_ref.document(colony.id).set(colony.to_dict())
            return colony
        except Exception as e:
            print(f"Error adding colony: {str(e)}")
            raise e

    def delete_colony(self, colony_id: str) -> bool:
        """Delete a colony"""
        try:
            # Delete from Firestore
            self.colonies_ref.document(colony_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting colony {colony_id}: {str(e)}")
            return False
