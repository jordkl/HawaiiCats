from datetime import datetime, timedelta
import math
from typing import List, Dict, Optional, Counter
from dataclasses import dataclass
import numpy as np
from sklearn.cluster import DBSCAN
from shapely.geometry import MultiPoint, Polygon, Point

@dataclass
class ColonyBounds:
    center_lat: float
    center_lng: float
    radius_meters: float
    polygon: Optional[Polygon] = None

@dataclass
class ColonyMetrics:
    min_cats: int = 0
    max_cats: int = 0
    behavior_counts: Dict[str, int] = None
    feeding_station_sightings: int = 0
    total_sightings: int = 0
    
    def __post_init__(self):
        if self.behavior_counts is None:
            self.behavior_counts = Counter()
    
    @property
    def dominant_behavior(self) -> str:
        if not self.behavior_counts:
            return "unknown"
        return max(self.behavior_counts.items(), key=lambda x: x[1])[0]
    
    @property
    def has_feeding_station(self) -> bool:
        # Consider it a feeding station if >25% of sightings report feeding
        return self.feeding_station_sightings > (self.total_sightings * 0.25)
    
class Colony:
    def __init__(self, id: str):
        self.id = id
        self.sightings = []
        self.confidence_score = 0.0
        self.bounds = None
        self.last_updated = datetime.now()
        self.first_sighting = None
        self.metrics = ColonyMetrics()
        
    def add_sighting(self, sighting: dict):
        self.sightings.append(sighting)
        self.last_updated = datetime.now()
        if not self.first_sighting:
            self.first_sighting = sighting.get('timestamp')
        self._update_metrics()
        
    def _update_metrics(self):
        metrics = ColonyMetrics()
        metrics.total_sightings = len(self.sightings)
        
        for sighting in self.sightings:
            # Update cat count range
            cat_range = sighting.get('catRange', {})
            min_cats = cat_range.get('min', 0)
            max_cats = cat_range.get('max', 0)
            metrics.min_cats = max(metrics.min_cats, min_cats)
            metrics.max_cats = max(metrics.max_cats, max_cats)
            
            # Update behavior counts
            behavior = sighting.get('behavior', 'unknown')
            metrics.behavior_counts[behavior] += 1
            
            # Update feeding station count
            if sighting.get('beingFed', False):
                metrics.feeding_station_sightings += 1
        
        self.metrics = metrics
        self._calculate_confidence_score()
    
    def _calculate_confidence_score(self):
        # Base confidence from number of sightings (0.0 - 0.4)
        sighting_score = min(len(self.sightings) / 10, 1.0) * 0.4
        
        # Time span score (0.0 - 0.3)
        if len(self.sightings) > 1:
            time_span = (self.last_updated - self.first_sighting).days
            time_score = min(time_span / 30, 1.0) * 0.3
        else:
            time_score = 0.1
        
        # Cat population score (0.0 - 0.2)
        # Higher confidence if we consistently see multiple cats
        pop_score = min(self.metrics.min_cats / 3, 1.0) * 0.2
        
        # Feeding station bonus (0.0 - 0.1)
        feeding_score = 0.1 if self.metrics.has_feeding_station else 0.0
        
        self.confidence_score = sighting_score + time_score + pop_score + feeding_score
        
    @property
    def colony_type(self) -> str:
        """Categorize the colony based on its characteristics"""
        behavior = self.metrics.dominant_behavior
        has_feeding = self.metrics.has_feeding_station
        
        if behavior == 'friendly' and has_feeding:
            return 'managed_colony'
        elif behavior == 'friendly':
            return 'semi_managed_colony'
        elif behavior == 'cautious' and has_feeding:
            return 'feeding_station'
        elif behavior == 'feral':
            return 'feral_colony'
        else:
            return 'potential_colony'
            
class ColonyAnalyzer:
    def __init__(self, min_confidence: float = 0.3):
        self.colonies: Dict[str, Colony] = {}
        self.min_confidence = min_confidence
        self.clustering_distances = [50, 100, 200]  # meters - try multiple scales
        self.min_sightings_by_distance = {
            50: 5,    # Need more sightings for tight clusters
            100: 4,   # Medium threshold for medium clusters
            200: 3    # Fewer sightings needed for loose clusters
        }
        
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in meters using Haversine formula"""
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2) * math.sin(delta_lat/2) + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * \
            math.sin(delta_lon/2) * math.sin(delta_lon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def analyze_sightings(self, sightings: List[dict]) -> List[Colony]:
        """Analyze sightings to identify and update colonies using multi-scale clustering"""
        if not sightings:
            return []
            
        # Extract coordinates for clustering
        coordinates = []
        for sighting in sightings:
            coord = sighting.get('coordinate', {})
            if coord.get('latitude') and coord.get('longitude'):
                coordinates.append([coord['latitude'], coord['longitude']])
                
        if not coordinates:
            return []
            
        coords_array = np.array(coordinates)
        all_clusters = []
        
        # Perform clustering at different scales
        for distance in self.clustering_distances:
            epsilon = distance / 111320  # Convert meters to degrees
            min_samples = self.min_sightings_by_distance[distance]
            
            db = DBSCAN(eps=epsilon, min_samples=min_samples, metric='haversine').fit(coords_array)
            labels = db.labels_
            
            # Store clustering results with their scale
            all_clusters.append({
                'labels': labels,
                'distance': distance,
                'min_samples': min_samples
            })
        
        # Reset colonies
        self.colonies = {}
        
        # Process clusters at each scale
        for cluster_info in all_clusters:
            labels = cluster_info['labels']
            distance = cluster_info['distance']
            unique_labels = set(labels)
            
            for label in unique_labels:
                if label == -1:  # Noise points
                    continue
                    
                cluster_points = coords_array[labels == label]
                cluster_sightings = [s for i, s in enumerate(sightings) if i in np.where(labels == label)[0]]
                
                # Skip if these points are already part of a tighter cluster
                if self._points_already_clustered(cluster_points):
                    continue
                
                # Create colony bounds
                points = MultiPoint(cluster_points)
                center = points.centroid
                colony_id = f"colony_{len(self.colonies)}"
                
                if colony_id not in self.colonies:
                    self.colonies[colony_id] = Colony(colony_id)
                    
                colony = self.colonies[colony_id]
                for sighting in cluster_sightings:
                    colony.add_sighting(sighting)
                    
                # Update colony bounds
                colony.bounds = ColonyBounds(
                    center_lat=center.y,
                    center_lng=center.x,
                    radius_meters=self._calculate_cluster_radius(cluster_points, center.y, center.x),
                    polygon=points.convex_hull
                )
                
                # Adjust confidence based on cluster scale
                scale_factor = 1.0 - (self.clustering_distances.index(distance) * 0.2)  # Tighter clusters get higher confidence
                colony.confidence_score *= scale_factor
        
        return [colony for colony in self.colonies.values() if colony.confidence_score >= self.min_confidence]
    
    def _points_already_clustered(self, points: np.ndarray) -> bool:
        """Check if any of these points are already part of an existing colony"""
        if not self.colonies:
            return False
            
        for colony in self.colonies.values():
            if not colony.bounds or not colony.bounds.polygon:
                continue
                
            for point in points:
                point_shapely = Point(point[0], point[1])
                if colony.bounds.polygon.contains(point_shapely):
                    return True
        return False
        
    def _calculate_cluster_radius(self, points: np.ndarray, center_lat: float, center_lng: float) -> float:
        """Calculate the radius that encompasses all points in the cluster"""
        max_distance = 0
        for point in points:
            distance = self._calculate_distance(center_lat, center_lng, point[0], point[1])
            max_distance = max(max_distance, distance)
        return max_distance
