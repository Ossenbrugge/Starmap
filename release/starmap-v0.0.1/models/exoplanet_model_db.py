"""
MontyDB Exoplanet Model
Handles exoplanet data operations using MontyDB
"""

from typing import List, Dict, Any, Optional
from database.config import get_database
import json
import os

class ExoplanetModelDB:
    """Exoplanet data model using MontyDB"""
    
    def __init__(self):
        self.db = get_database()
        self.exoplanets = self.db.exoplanets
        self.fictional_exoplanets = self.db.fictional_exoplanets
        self._cache = {}
    
    def migrate_from_json(self, data_path: str = 'data'):
        """Migrate exoplanet data from JSON files to MontyDB"""
        print("🔄 Migrating exoplanets to MontyDB...")
        
        try:
            # Clear existing data
            self.exoplanets.delete_many({})
            self.fictional_exoplanets.delete_many({})
            
            # Load real exoplanets from JSON
            exoplanets_file = f'{data_path}/exoplanets.json'
            if os.path.exists(exoplanets_file):
                with open(exoplanets_file, 'r') as f:
                    raw_exoplanets = json.load(f)
                    processed_exoplanets = self._process_exoplanets(raw_exoplanets)
                    if processed_exoplanets:
                        self.exoplanets.insert_many(processed_exoplanets)
                        print(f"✅ Loaded {len(processed_exoplanets)} real exoplanets")
            
            # Add Sol system manually
            sol_system = self._create_sol_system()
            if sol_system:
                self.fictional_exoplanets.insert_many(sol_system)
                print(f"✅ Added Sol system with {len(sol_system)} planets")
            
            # Load fictional exoplanets if CSV exists
            self._load_fictional_exoplanets_csv(data_path)
            
            real_count = self.exoplanets.count_documents({})
            fictional_count = self.fictional_exoplanets.count_documents({})
            print(f"✅ Total exoplanets: {real_count} real + {fictional_count} fictional")
            
        except Exception as e:
            print(f"❌ Error migrating exoplanets: {e}")
            raise
    
    def _process_exoplanets(self, raw_exoplanets: List[Dict]) -> List[Dict]:
        """Process raw JSON exoplanet data into MontyDB format"""
        processed = []
        
        for planet in raw_exoplanets:
            try:
                # Clean metadata to remove MongoDB-specific fields
                metadata = planet.get('metadata', {})
                clean_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, dict) and '$date' in value:
                        # Convert MongoDB date to timestamp
                        clean_metadata[key] = value['$date']
                    else:
                        clean_metadata[key] = value
                
                # Convert the existing format to a cleaner structure
                doc = {
                    '_id': planet['_id'],
                    'name': planet['name'],
                    'letter': planet.get('letter', ''),
                    'host_star': {
                        'name': planet['host_star']['name'],
                        'hip_id': planet['host_star'].get('hip_id'),
                        'hd_id': planet['host_star'].get('hd_id'),
                        'distance_pc': planet['host_star']['distance_pc'],
                        'coordinates': planet['host_star']['coordinates'],
                        'properties': planet['host_star']['properties']
                    },
                    'orbital_properties': planet['orbital_properties'],
                    'physical_properties': planet['physical_properties'],
                    'discovery': planet['discovery'],
                    'habitability': planet['habitability'],
                    'detection_flags': planet['detection_flags'],
                    'metadata': clean_metadata,
                    'is_fictional': False
                }
                
                processed.append(doc)
                
            except Exception as e:
                print(f"Warning: Error processing exoplanet {planet.get('_id', 'unknown')}: {e}")
                continue
        
        return processed
    
    def _create_sol_system(self) -> List[Dict]:
        """Create Sol system planetary data"""
        sol_system = [
            {
                '_id': 'mercury',
                'name': 'Mercury',
                'letter': 'I',
                'star_id': 500000,  # Sol's actual ID in the star database
                'host_star_name': 'Sol',
                'orbital_properties': {
                    'period_days': 87.97,
                    'semi_major_axis_au': 0.387,
                    'eccentricity': 0.206,
                    'inclination_deg': 7.0,
                    'orbital_velocity_km_s': 47.87
                },
                'physical_properties': {
                    'radius_earth': 0.383,
                    'mass_earth': 0.055,
                    'density_g_cm3': 5.427,
                    'surface_gravity_m_s2': 3.7,
                    'escape_velocity_km_s': 4.25,
                    'rotation_period_hours': 1407.6,
                    'axial_tilt_deg': 0.034,
                    'surface_temperature_k': [100, 700],  # min, max
                    'atmosphere': 'Trace (oxygen, sodium, hydrogen, helium, potassium)'
                },
                'discovery': {
                    'year': 'Ancient',
                    'method': 'Visual observation',
                    'facility': 'Naked eye',
                    'known_since': 'Antiquity'
                },
                'habitability': {
                    'potentially_habitable': False,
                    'habitable_zone': False,
                    'planet_type': 'Rocky'
                },
                'moons': 0,
                'is_fictional': False,
                'description': 'The smallest and innermost planet in the Solar System'
            },
            {
                '_id': 'venus',
                'name': 'Venus',
                'letter': 'II',
                'star_id': 500000,
                'host_star_name': 'Sol',
                'orbital_properties': {
                    'period_days': 224.7,
                    'semi_major_axis_au': 0.723,
                    'eccentricity': 0.007,
                    'inclination_deg': 3.4,
                    'orbital_velocity_km_s': 35.02
                },
                'physical_properties': {
                    'radius_earth': 0.949,
                    'mass_earth': 0.815,
                    'density_g_cm3': 5.243,
                    'surface_gravity_m_s2': 8.87,
                    'escape_velocity_km_s': 10.36,
                    'rotation_period_hours': -5832.5,  # retrograde
                    'axial_tilt_deg': 177.4,
                    'surface_temperature_k': [737, 737],  # constant due to thick atmosphere
                    'atmosphere': 'Dense CO₂ (96.5%), nitrogen (3.5%)'
                },
                'discovery': {
                    'year': 'Ancient',
                    'method': 'Visual observation',
                    'facility': 'Naked eye',
                    'known_since': 'Antiquity'
                },
                'habitability': {
                    'potentially_habitable': False,
                    'habitable_zone': False,
                    'planet_type': 'Rocky'
                },
                'moons': 0,
                'is_fictional': False,
                'description': 'The hottest planet in the Solar System with a dense, toxic atmosphere'
            },
            {
                '_id': 'earth',
                'name': 'Earth',
                'letter': 'III',
                'star_id': 500000,
                'host_star_name': 'Sol',
                'orbital_properties': {
                    'period_days': 365.26,
                    'semi_major_axis_au': 1.000,
                    'eccentricity': 0.017,
                    'inclination_deg': 0.0,
                    'orbital_velocity_km_s': 29.78
                },
                'physical_properties': {
                    'radius_earth': 1.000,
                    'mass_earth': 1.000,
                    'density_g_cm3': 5.514,
                    'surface_gravity_m_s2': 9.807,
                    'escape_velocity_km_s': 11.19,
                    'rotation_period_hours': 23.93,
                    'axial_tilt_deg': 23.44,
                    'surface_temperature_k': [184, 330],  # polar to equatorial
                    'atmosphere': 'Nitrogen (78%), oxygen (21%), argon (0.93%)'
                },
                'discovery': {
                    'year': 'N/A',
                    'method': 'Home planet',
                    'facility': 'N/A',
                    'known_since': 'Always'
                },
                'habitability': {
                    'potentially_habitable': True,
                    'habitable_zone': True,
                    'planet_type': 'Rocky'
                },
                'moons': 1,
                'is_fictional': False,
                'description': 'The third planet from the Sun and the only known planet to harbor life'
            },
            {
                '_id': 'mars',
                'name': 'Mars',
                'letter': 'IV',
                'star_id': 500000,
                'host_star_name': 'Sol',
                'orbital_properties': {
                    'period_days': 686.98,
                    'semi_major_axis_au': 1.524,
                    'eccentricity': 0.094,
                    'inclination_deg': 1.85,
                    'orbital_velocity_km_s': 24.07
                },
                'physical_properties': {
                    'radius_earth': 0.532,
                    'mass_earth': 0.107,
                    'density_g_cm3': 3.933,
                    'surface_gravity_m_s2': 3.71,
                    'escape_velocity_km_s': 5.03,
                    'rotation_period_hours': 24.62,
                    'axial_tilt_deg': 25.19,
                    'surface_temperature_k': [130, 308],  # polar to equatorial
                    'atmosphere': 'Thin CO₂ (95.3%), nitrogen (2.7%), argon (1.6%)'
                },
                'discovery': {
                    'year': 'Ancient',
                    'method': 'Visual observation',
                    'facility': 'Naked eye',
                    'known_since': 'Antiquity'
                },
                'habitability': {
                    'potentially_habitable': False,
                    'habitable_zone': False,
                    'planet_type': 'Rocky'
                },
                'moons': 2,
                'is_fictional': False,
                'description': 'The fourth planet from the Sun, known as the Red Planet'
            },
            {
                '_id': 'jupiter',
                'name': 'Jupiter',
                'letter': 'V',
                'star_id': 500000,
                'host_star_name': 'Sol',
                'orbital_properties': {
                    'period_days': 4332.59,
                    'semi_major_axis_au': 5.204,
                    'eccentricity': 0.049,
                    'inclination_deg': 1.31,
                    'orbital_velocity_km_s': 13.07
                },
                'physical_properties': {
                    'radius_earth': 11.21,
                    'mass_earth': 317.8,
                    'density_g_cm3': 1.326,
                    'surface_gravity_m_s2': 24.79,
                    'escape_velocity_km_s': 59.5,
                    'rotation_period_hours': 9.93,
                    'axial_tilt_deg': 3.13,
                    'surface_temperature_k': [108, 152],  # cloud tops
                    'atmosphere': 'Hydrogen (89%), helium (10%), methane, ammonia'
                },
                'discovery': {
                    'year': 'Ancient',
                    'method': 'Visual observation',
                    'facility': 'Naked eye',
                    'known_since': 'Antiquity'
                },
                'habitability': {
                    'potentially_habitable': False,
                    'habitable_zone': False,
                    'planet_type': 'Gas Giant'
                },
                'moons': 95,  # As of 2024
                'is_fictional': False,
                'description': 'The largest planet in the Solar System, a gas giant'
            },
            {
                '_id': 'saturn',
                'name': 'Saturn',
                'letter': 'VI',
                'star_id': 500000,
                'host_star_name': 'Sol',
                'orbital_properties': {
                    'period_days': 10759.22,
                    'semi_major_axis_au': 9.537,
                    'eccentricity': 0.057,
                    'inclination_deg': 2.49,
                    'orbital_velocity_km_s': 9.68
                },
                'physical_properties': {
                    'radius_earth': 9.45,
                    'mass_earth': 95.2,
                    'density_g_cm3': 0.687,  # Less dense than water!
                    'surface_gravity_m_s2': 10.44,
                    'escape_velocity_km_s': 35.5,
                    'rotation_period_hours': 10.66,
                    'axial_tilt_deg': 26.73,
                    'surface_temperature_k': [82, 143],  # cloud tops
                    'atmosphere': 'Hydrogen (96%), helium (3%), methane, ammonia'
                },
                'discovery': {
                    'year': 'Ancient',
                    'method': 'Visual observation',
                    'facility': 'Naked eye',
                    'known_since': 'Antiquity'
                },
                'habitability': {
                    'potentially_habitable': False,
                    'habitable_zone': False,
                    'planet_type': 'Gas Giant'
                },
                'moons': 146,  # As of 2024
                'is_fictional': False,
                'description': 'The sixth planet from the Sun, famous for its prominent ring system'
            },
            {
                '_id': 'uranus',
                'name': 'Uranus',
                'letter': 'VII',
                'star_id': 500000,
                'host_star_name': 'Sol',
                'orbital_properties': {
                    'period_days': 30688.5,
                    'semi_major_axis_au': 19.2,
                    'eccentricity': 0.046,
                    'inclination_deg': 0.77,
                    'orbital_velocity_km_s': 6.80
                },
                'physical_properties': {
                    'radius_earth': 4.01,
                    'mass_earth': 14.5,
                    'density_g_cm3': 1.270,
                    'surface_gravity_m_s2': 8.69,
                    'escape_velocity_km_s': 21.3,
                    'rotation_period_hours': -17.2,  # retrograde
                    'axial_tilt_deg': 97.77,  # Nearly sideways!
                    'surface_temperature_k': [49, 76],  # cloud tops
                    'atmosphere': 'Hydrogen (83%), helium (15%), methane (2%)'
                },
                'discovery': {
                    'year': 1781,
                    'method': 'Telescopic observation',
                    'facility': 'William Herschel telescope',
                    'known_since': '1781'
                },
                'habitability': {
                    'potentially_habitable': False,
                    'habitable_zone': False,
                    'planet_type': 'Ice Giant'
                },
                'moons': 28,
                'is_fictional': False,
                'description': 'The seventh planet from the Sun, an ice giant that rotates on its side'
            },
            {
                '_id': 'neptune',
                'name': 'Neptune',
                'letter': 'VIII',
                'star_id': 500000,
                'host_star_name': 'Sol',
                'orbital_properties': {
                    'period_days': 60182,
                    'semi_major_axis_au': 30.07,
                    'eccentricity': 0.010,
                    'inclination_deg': 1.77,
                    'orbital_velocity_km_s': 5.43
                },
                'physical_properties': {
                    'radius_earth': 3.88,
                    'mass_earth': 17.1,
                    'density_g_cm3': 1.638,
                    'surface_gravity_m_s2': 11.15,
                    'escape_velocity_km_s': 23.5,
                    'rotation_period_hours': 16.1,
                    'axial_tilt_deg': 28.32,
                    'surface_temperature_k': [48, 76],  # cloud tops
                    'atmosphere': 'Hydrogen (80%), helium (19%), methane (1%)'
                },
                'discovery': {
                    'year': 1846,
                    'method': 'Mathematical prediction + telescopic observation',
                    'facility': 'Berlin Observatory',
                    'known_since': '1846'
                },
                'habitability': {
                    'potentially_habitable': False,
                    'habitable_zone': False,
                    'planet_type': 'Ice Giant'
                },
                'moons': 16,
                'is_fictional': False,
                'description': 'The eighth and outermost planet in the Solar System, an ice giant with the fastest winds'
            }
        ]
        
        return sol_system
    
    def _load_fictional_exoplanets_csv(self, data_path: str):
        """Load fictional exoplanets from CSV file (placeholder for future expansion)"""
        # This could load fictional planets from the Felgenland universe
        # For now, we'll leave this as a placeholder
        pass
    
    def get_exoplanets(self, limit: int = 1000) -> List[Dict]:
        """Get real exoplanets"""
        return list(self.exoplanets.find().limit(limit))
    
    def get_fictional_exoplanets(self, limit: int = 1000) -> List[Dict]:
        """Get fictional exoplanets"""
        return list(self.fictional_exoplanets.find().limit(limit))
    
    def get_exoplanets_by_star(self, star_name: str) -> List[Dict]:
        """Get exoplanets for a specific star"""
        real_planets = list(self.exoplanets.find({'host_star.name': star_name}))
        fictional_planets = list(self.fictional_exoplanets.find({'host_star_name': star_name}))
        return real_planets + fictional_planets
    
    def get_exoplanets_by_star_id(self, star_id: int) -> List[Dict]:
        """Get exoplanets for a specific star ID"""
        return list(self.fictional_exoplanets.find({'star_id': star_id}))
    
    def get_habitable_exoplanets(self) -> List[Dict]:
        """Get potentially habitable exoplanets"""
        real_habitable = list(self.exoplanets.find({'habitability.potentially_habitable': 'True'}))
        fictional_habitable = list(self.fictional_exoplanets.find({'habitability.potentially_habitable': True}))
        return real_habitable + fictional_habitable
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cache_size': len(self._cache),
            'total_real_exoplanets': self.exoplanets.count_documents({}),
            'total_fictional_exoplanets': self.fictional_exoplanets.count_documents({})
        }
    
    def clear_cache(self):
        """Clear internal cache"""
        self._cache.clear()