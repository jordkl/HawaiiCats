import h3
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

class ColonyAnalyzer:
    def __init__(self, h3_resolution: int = 9):
        """
        Initialize colony analyzer with specified H3 resolution.
        
        Args:
            h3_resolution: H3 resolution level (9 ≈ 174m edge-to-edge, 10 ≈ 65m edge-to-edge)
        """
        self.resolution = h3_resolution
    
    def get_hex_index(self, lat: float, lng: float) -> str:
        """Convert latitude/longitude to H3 index."""
        return h3.geo_to_h3(lat, lng, self.resolution)
    
    def get_hex_boundary(self, h3_index: str) -> List[Tuple[float, float]]:
        """Get the boundary coordinates of a hexagon."""
        return h3.h3_to_geo_boundary(h3_index)
    
    def analyze_sightings(self, sightings: List[Dict[str, Any]], 
                         min_sightings: int = 3,
                         min_avg_cats: float = 2.0,
                         min_days_active: int = 14) -> List[Dict[str, Any]]:
        """
        Analyze cat sightings to identify potential colonies.
        
        Args:
            sightings: List of sighting records with lat, lng, visible_cats, etc.
            min_sightings: Minimum number of sightings to consider a colony
            min_avg_cats: Minimum average cats per sighting
            min_days_active: Minimum days between first and last sighting
            
        Returns:
            List of colony data including statistics and boundaries
        """
        hex_stats = self._aggregate_hex_stats(sightings)
        colonies = self._identify_colonies(hex_stats, min_sightings, min_avg_cats, min_days_active)
        return colonies
    
    def _aggregate_hex_stats(self, sightings: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Aggregate statistics for each hexagon."""
        hex_stats = defaultdict(lambda: {
            'cat_count': 0,
            'sighting_count': 0,
            'first_seen': None,
            'last_seen': None,
            'feeding_locations': 0,
            'sightings': []  # Store individual sightings for detailed analysis
        })
        
        for sighting in sightings:
            h3_index = self.get_hex_index(sighting['latitude'], sighting['longitude'])
            stats = hex_stats[h3_index]
            
            # Update counts
            stats['cat_count'] += sighting['visible_cats']
            stats['sighting_count'] += 1
            stats['feeding_locations'] += 1 if sighting.get('is_feeding') else 0
            
            # Update temporal data
            timestamp = datetime.fromisoformat(sighting['timestamp'])
            if not stats['first_seen'] or timestamp < stats['first_seen']:
                stats['first_seen'] = timestamp
            if not stats['last_seen'] or timestamp > stats['last_seen']:
                stats['last_seen'] = timestamp
            
            # Store sighting reference
            stats['sightings'].append(sighting)
        
        return hex_stats
    
    def _identify_colonies(self, hex_stats: Dict[str, Dict[str, Any]], 
                         min_sightings: int,
                         min_avg_cats: float,
                         min_days_active: int) -> List[Dict[str, Any]]:
        """Identify potential colonies based on hexagon statistics."""
        colonies = []
        
        for h3_index, stats in hex_stats.items():
            # Calculate metrics
            avg_cats = stats['cat_count'] / stats['sighting_count'] if stats['sighting_count'] > 0 else 0
            days_active = (stats['last_seen'] - stats['first_seen']).days if stats['first_seen'] else 0
            
            # Check if hexagon meets colony criteria
            if (stats['sighting_count'] >= min_sightings and
                avg_cats >= min_avg_cats and
                days_active >= min_days_active):
                
                # Get hexagon center and boundary
                center = h3.h3_to_geo(h3_index)
                boundary = self.get_hex_boundary(h3_index)
                
                colonies.append({
                    'h3_index': h3_index,
                    'center': {'lat': center[0], 'lng': center[1]},
                    'boundary': [{'lat': lat, 'lng': lng} for lat, lng in boundary],
                    'stats': {
                        'total_cats': stats['cat_count'],
                        'sighting_count': stats['sighting_count'],
                        'avg_cats_per_sighting': avg_cats,
                        'feeding_locations': stats['feeding_locations'],
                        'first_seen': stats['first_seen'].isoformat(),
                        'last_seen': stats['last_seen'].isoformat(),
                        'days_active': days_active
                    }
                })
        
        return colonies
    
    def get_adjacent_colonies(self, h3_index: str) -> List[Dict[str, Any]]:
        """Get statistics for adjacent hexagons."""
        neighbors = h3.k_ring(h3_index, 1)  # Get immediate neighbors
        return [{'h3_index': neighbor,
                'boundary': self.get_hex_boundary(neighbor)}
               for neighbor in neighbors if neighbor != h3_index]
