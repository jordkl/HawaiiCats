from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
import json
import os
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
    
    # Colony characteristics
    territory_size: Optional[float] = None
    caretaker_support: Optional[float] = None
    feeding_consistency: Optional[float] = None
    
    # Environmental factors
    urban_risk: Optional[float] = None
    shelter_quality: Optional[float] = None
    food_availability: Optional[float] = None
    water_availability: Optional[float] = None
    
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
    def __init__(self, data_file):
        self.data_file = data_file
        self._ensure_data_file()
        
    def _ensure_data_file(self):
        """Create the data file if it doesn't exist"""
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            self._save_colonies([])
    
    def _load_colonies(self) -> List[Colony]:
        """Load colonies from the JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                return [Colony.from_dict(colony_data) for colony_data in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_colonies(self, colonies: List[Colony]):
        """Save colonies to the JSON file"""
        data = [colony.to_dict() for colony in colonies]
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_colony(self, colony: Colony) -> Colony:
        """Add a new colony"""
        colonies = self._load_colonies()
        
        # Generate a simple ID if none exists
        if not colony.id:
            colony.id = str(len(colonies) + 1)
        
        colonies.append(colony)
        self._save_colonies(colonies)
        return colony

    def get_colonies(self) -> List[Colony]:
        """Get all colonies"""
        return self._load_colonies()

    def get_colony(self, colony_id: str) -> Optional[Colony]:
        """Get a specific colony by ID"""
        colonies = self._load_colonies()
        for colony in colonies:
            if colony.id == colony_id:
                return colony
        return None

    def update_colony(self, colony_id: str, updated_colony: Colony) -> Optional[Colony]:
        """Update an existing colony"""
        colonies = self._load_colonies()
        for i, colony in enumerate(colonies):
            if colony.id == colony_id:
                updated_colony.id = colony_id
                colonies[i] = updated_colony
                self._save_colonies(colonies)
                return updated_colony
        return None

    def delete_colony(self, colony_id: str) -> bool:
        """Delete a colony"""
        colonies = self._load_colonies()
        initial_length = len(colonies)
        colonies = [c for c in colonies if c.id != colony_id]
        if len(colonies) < initial_length:
            self._save_colonies(colonies)
            return True
        return False
