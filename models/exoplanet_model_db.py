"""
Exoplanet model using MontyDB
"""

from datetime import datetime
from .base_model_db import BaseModelDB


class ExoplanetModelDB(BaseModelDB):
    """MontyDB-based exoplanet model"""
    
    def __init__(self):
        super().__init__('exoplanets')
        self._cache = {}
    
    def _initialize_collection(self):
        """Initialize exoplanet collection with indexes"""
        try:
            self.create_index([("host_star.name", 1)])
            self.create_index([("host_star.hip_id", 1)])
            self.create_index([("discovery.year", 1)])
            self.create_index([("habitability.potentially_habitable", 1)])
            self.create_index([("physical_properties.radius_earth", 1)])
            self.create_index([("orbital_properties.period_days", 1)])
        except Exception as e:
            print(f"Warning: Could not create exoplanet indexes: {e}")
    
    def get_planets_by_host_star(self, host_name):
        """Get all planets for a specific host star"""
        cache_key = f"host_{host_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        query = {'host_star.name': host_name}
        planets = self.find(query, sort=[('letter', 1)])
        
        formatted_planets = []
        for planet in planets:
            formatted_planet = self._format_planet_for_json(planet)
            formatted_planets.append(formatted_planet)
        
        self._cache[cache_key] = formatted_planets
        return formatted_planets
    
    def get_planets_by_hip_id(self, hip_id):
        """Get all planets for a host star by HIP ID"""
        if not hip_id:
            return []
        
        cache_key = f"hip_{hip_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        query = {'host_star.hip_id': float(hip_id)}
        planets = self.find(query, sort=[('letter', 1)])
        
        formatted_planets = []
        for planet in planets:
            formatted_planet = self._format_planet_for_json(planet)
            formatted_planets.append(formatted_planet)
        
        self._cache[cache_key] = formatted_planets
        return formatted_planets
    
    def get_habitable_planets(self, limit=None):
        """Get potentially habitable planets"""
        query = {'habitability.potentially_habitable': True}
        sort = [('discovery.year', -1)]
        
        planets = self.find(query, limit=limit, sort=sort)
        return [self._format_planet_for_json(planet) for planet in planets]
    
    def get_recent_discoveries(self, since_year=2020, limit=50):
        """Get recently discovered planets"""
        query = {'discovery.year': {'$gte': since_year}}
        sort = [('discovery.year', -1), ('name', 1)]
        
        planets = self.find(query, limit=limit, sort=sort)
        return [self._format_planet_for_json(planet) for planet in planets]
    
    def get_planets_by_discovery_method(self, method, limit=None):
        """Get planets discovered by a specific method"""
        query = {'discovery.method': method}
        sort = [('discovery.year', -1)]
        
        planets = self.find(query, limit=limit, sort=sort)
        return [self._format_planet_for_json(planet) for planet in planets]
    
    def get_system_statistics(self):
        """Get statistics about planetary systems"""
        total_planets = self.count_documents()
        
        # Count confirmed planets
        confirmed_count = self.count_documents({'metadata.confirmed': True})
        
        # Count potentially habitable planets
        habitable_count = self.count_documents({'habitability.potentially_habitable': True})
        
        # Count by discovery method (simplified for MontyDB)
        methods = {}
        all_planets = self.find({}, projection={'discovery.method': 1})
        for planet in all_planets:
            method = planet.get('discovery', {}).get('method', 'Unknown')
            methods[method] = methods.get(method, 0) + 1
        
        # Get host star statistics
        unique_hosts = set()
        all_planets = self.find({}, projection={'host_star.name': 1})
        for planet in all_planets:
            host_name = planet.get('host_star', {}).get('name')
            if host_name:
                unique_hosts.add(host_name)
        
        return {
            'total_planets': total_planets,
            'confirmed_planets': confirmed_count,
            'potentially_habitable': habitable_count,
            'unique_host_stars': len(unique_hosts),
            'discovery_methods': [{'method': k, 'count': v} for k, v in methods.items()],
            'collection_info': {
                'indexes': len(self.collection.list_indexes()) if hasattr(self.collection, 'list_indexes') else 0,
                'cache_size': len(self._cache)
            }
        }
    
    def search_planets(self, query_term, limit=50):
        """Search planets by name or host star"""
        # Simple text search for MontyDB compatibility
        results = []
        
        # Search by planet name
        name_matches = self.find({
            'name': {'$regex': query_term, '$options': 'i'}
        }, limit=limit//2)
        
        # Search by host star name
        host_matches = self.find({
            'host_star.name': {'$regex': query_term, '$options': 'i'}
        }, limit=limit//2)
        
        # Combine and deduplicate results
        seen_ids = set()
        for planet in list(name_matches) + list(host_matches):
            if planet['_id'] not in seen_ids:
                results.append(self._format_planet_for_json(planet))
                seen_ids.add(planet['_id'])
                if len(results) >= limit:
                    break
        
        return results
    
    def _format_planet_for_json(self, planet):
        """Convert planet document to JSON-serializable format"""
        return {
            'id': planet['_id'],
            'name': planet['name'],
            'letter': planet.get('letter', ''),
            'host_star': planet.get('host_star', {}),
            'orbital_period_days': planet.get('orbital_properties', {}).get('period_days'),
            'semi_major_axis_au': planet.get('orbital_properties', {}).get('semi_major_axis_au'),
            'eccentricity': planet.get('orbital_properties', {}).get('eccentricity'),
            'radius_earth': planet.get('physical_properties', {}).get('radius_earth'),
            'radius_jupiter': planet.get('physical_properties', {}).get('radius_jupiter'),
            'mass_earth': planet.get('physical_properties', {}).get('mass_earth'),
            'mass_jupiter': planet.get('physical_properties', {}).get('mass_jupiter'),
            'equilibrium_temperature_k': planet.get('physical_properties', {}).get('equilibrium_temperature_k'),
            'insolation_earth': planet.get('physical_properties', {}).get('insolation_earth'),
            'discovery_year': planet.get('discovery', {}).get('year'),
            'discovery_method': planet.get('discovery', {}).get('method'),
            'discovery_facility': planet.get('discovery', {}).get('facility'),
            'potentially_habitable': planet.get('habitability', {}).get('potentially_habitable', False),
            'planet_type': planet.get('habitability', {}).get('planet_type', 'Unknown'),
            'confirmed': planet.get('metadata', {}).get('confirmed', False),
            'detection_methods': {
                'transit': planet.get('detection_flags', {}).get('transit', False),
                'radial_velocity': planet.get('detection_flags', {}).get('radial_velocity', False),
                'astrometry': planet.get('detection_flags', {}).get('astrometry', False),
                'imaging': planet.get('detection_flags', {}).get('imaging', False),
                'microlensing': planet.get('detection_flags', {}).get('microlensing', False)
            }
        }
    
    def clear_cache(self):
        """Clear the model cache"""
        self._cache.clear()