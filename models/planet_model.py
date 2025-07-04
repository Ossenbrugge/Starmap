from .base_model import BaseModel
from fictional_planets import fictional_planet_systems


class PlanetModel(BaseModel):
    """Model for managing planetary system data"""
    
    def load_data(self):
        """Load planetary system data"""
        # Comprehensive planetary systems with real and theoretical data
        self.data = {
            0: [  # Sol - Our Solar System (complete with all 8 planets)
                {
                    "name": "Mercury", "type": "Terrestrial", "distance_au": 0.387, "mass_earth": 0.0553, 
                    "radius_earth": 0.3829, "orbital_period_days": 87.97, "temperature_k": 440, 
                    "atmosphere": "Virtually none", "discovery_year": "Ancient", "confirmed": True
                },
                {
                    "name": "Venus", "type": "Terrestrial", "distance_au": 0.723, "mass_earth": 0.815,
                    "radius_earth": 0.9499, "orbital_period_days": 224.7, "temperature_k": 737,
                    "atmosphere": "CO2 (96.5%), N2 (3.5%)", "discovery_year": "Ancient", "confirmed": True
                },
                {
                    "name": "Earth", "type": "Terrestrial", "distance_au": 1.0, "mass_earth": 1.0,
                    "radius_earth": 1.0, "orbital_period_days": 365.26, "temperature_k": 288,
                    "atmosphere": "N2 (78%), O2 (21%)", "discovery_year": "N/A", "confirmed": True,
                    "moons": [
                        {
                            "name": "Luna", "type": "Rocky", "mass_earth": 0.0123, "radius_earth": 0.2724,
                            "orbital_distance_km": 384400, "orbital_period_days": 27.3, "temperature_k": 220,
                            "atmosphere": "Virtually none", "description": "Earth's natural satellite"
                        }
                    ]
                },
                {
                    "name": "Mars", "type": "Terrestrial", "distance_au": 1.524, "mass_earth": 0.1074,
                    "radius_earth": 0.5320, "orbital_period_days": 686.98, "temperature_k": 210,
                    "atmosphere": "CO2 (95%), Ar (1.9%)", "discovery_year": "Ancient", "confirmed": True
                },
                {
                    "name": "Jupiter", "type": "Gas Giant", "distance_au": 5.204, "mass_earth": 317.8,
                    "radius_earth": 10.97, "orbital_period_days": 4332.6, "temperature_k": 165,
                    "atmosphere": "H2 (89%), He (10%)", "discovery_year": "Ancient", "confirmed": True
                },
                {
                    "name": "Saturn", "type": "Gas Giant", "distance_au": 9.573, "mass_earth": 95.16,
                    "radius_earth": 9.140, "orbital_period_days": 10759.2, "temperature_k": 134,
                    "atmosphere": "H2 (96%), He (3%)", "discovery_year": "Ancient", "confirmed": True
                },
                {
                    "name": "Uranus", "type": "Ice Giant", "distance_au": 19.165, "mass_earth": 14.54,
                    "radius_earth": 3.981, "orbital_period_days": 30688.5, "temperature_k": 76,
                    "atmosphere": "H2 (83%), He (15%), CH4 (2%)", "discovery_year": "1781", "confirmed": True
                },
                {
                    "name": "Neptune", "type": "Ice Giant", "distance_au": 30.178, "mass_earth": 17.15,
                    "radius_earth": 3.865, "orbital_period_days": 60182, "temperature_k": 72,
                    "atmosphere": "H2 (80%), He (19%), CH4 (1%)", "discovery_year": "1846", "confirmed": True
                }
            ],
            16496: [  # Epsilon Eridani - Real exoplanet system
                {
                    "name": "Epsilon Eridani b", "type": "Gas Giant", "distance_au": 3.4, "mass_earth": 317,
                    "radius_earth": 4.1, "orbital_period_days": 2502, "temperature_k": 120,
                    "atmosphere": "H2, He (estimated)", "discovery_year": "2000", "confirmed": True
                }
            ],
            70666: [  # Proxima Centauri - Real exoplanets
                {
                    "name": "Proxima Centauri b", "type": "Terrestrial", "distance_au": 0.05, "mass_earth": 1.27,
                    "radius_earth": 1.1, "orbital_period_days": 11.2, "temperature_k": 234,
                    "atmosphere": "Unknown", "discovery_year": "2016", "confirmed": True
                },
                {
                    "name": "Proxima Centauri c", "type": "Super-Earth", "distance_au": 1.5, "mass_earth": 6.0,
                    "radius_earth": 1.5, "orbital_period_days": 1928, "temperature_k": 39,
                    "atmosphere": "Unknown", "discovery_year": "2019", "confirmed": True
                },
                {
                    "name": "Proxima Centauri d", "type": "Sub-Earth", "distance_au": 0.029, "mass_earth": 0.26,
                    "radius_earth": 0.81, "orbital_period_days": 5.1, "temperature_k": 350,
                    "atmosphere": "Unknown", "discovery_year": "2022", "confirmed": True
                }
            ],
            32263: [  # Sirius - Hypothetical system for demonstration
                {
                    "name": "Sirius Ab", "type": "Hot Jupiter", "distance_au": 0.1, "mass_earth": 400,
                    "radius_earth": 5.2, "orbital_period_days": 15, "temperature_k": 1200,
                    "atmosphere": "H2, He (theoretical)", "discovery_year": "Future", "confirmed": False
                }
            ],
            71456: [  # Alpha Centauri A - Theoretical planets
                {
                    "name": "Alpha Centauri Ab", "type": "Terrestrial", "distance_au": 1.25, "mass_earth": 1.13,
                    "radius_earth": 1.05, "orbital_period_days": 400, "temperature_k": 250,
                    "atmosphere": "Unknown (theoretical)", "discovery_year": "TBD", "confirmed": False
                }
            ],
            8087: [  # Tau Ceti - Real candidate planets
                {
                    "name": "Tau Ceti e", "type": "Super-Earth", "distance_au": 0.55, "mass_earth": 3.93,
                    "radius_earth": 1.51, "orbital_period_days": 168, "temperature_k": 240,
                    "atmosphere": "Unknown", "discovery_year": "2012", "confirmed": False
                },
                {
                    "name": "Tau Ceti f", "type": "Super-Earth", "distance_au": 1.35, "mass_earth": 3.93,
                    "radius_earth": 1.51, "orbital_period_days": 642, "temperature_k": 150,
                    "atmosphere": "Unknown", "discovery_year": "2012", "confirmed": False
                }
            ]
        }
        
        # Merge with fictional planet systems
        self.data.update(fictional_planet_systems)
    
    def get_planets_for_star(self, star_id):
        """Get planetary system for a specific star"""
        return self.data.get(star_id, [])
    
    def add_planet_to_star(self, star_id, planet_data):
        """Add a new planet to a star system"""
        if star_id not in self.data:
            self.data[star_id] = []
        
        # Validate planet data
        required_fields = ['name', 'type', 'distance_au', 'mass_earth', 'radius_earth', 
                          'orbital_period_days', 'temperature_k', 'atmosphere', 
                          'discovery_year', 'confirmed']
        
        new_planet = {}
        for field in required_fields:
            if field in planet_data:
                if field in ['distance_au', 'mass_earth', 'radius_earth', 
                           'orbital_period_days', 'temperature_k']:
                    new_planet[field] = float(planet_data[field])
                elif field == 'confirmed':
                    new_planet[field] = bool(planet_data[field])
                else:
                    new_planet[field] = planet_data[field]
            else:
                # Set defaults for missing fields
                defaults = {
                    'name': 'Unknown Planet',
                    'type': 'Unknown',
                    'distance_au': 1.0,
                    'mass_earth': 1.0,
                    'radius_earth': 1.0,
                    'orbital_period_days': 365,
                    'temperature_k': 250,
                    'atmosphere': 'Unknown',
                    'discovery_year': 'TBD',
                    'confirmed': False
                }
                new_planet[field] = defaults[field]
        
        self.data[star_id].append(new_planet)
        return new_planet
    
    def get_all_planetary_systems(self):
        """Get all stars with planetary systems"""
        systems = []
        
        for star_id, planets in self.data.items():
            if planets and len(planets) > 0:
                systems.append({
                    'star_id': star_id,
                    'planet_count': len(planets),
                    'confirmed_planets': sum(1 for p in planets if p.get('confirmed', False)),
                    'candidate_planets': sum(1 for p in planets if not p.get('confirmed', False)),
                    'planets': planets
                })
        
        return systems
    
    def get_systems_summary(self):
        """Get summary information about planetary systems"""
        systems = self.get_all_planetary_systems()
        
        return {
            'total_systems': len(systems),
            'total_planets': sum(s['planet_count'] for s in systems),
            'confirmed_planets': sum(s['confirmed_planets'] for s in systems),
            'candidate_planets': sum(s['candidate_planets'] for s in systems),
            'systems': sorted(systems, key=lambda x: x['planet_count'], reverse=True)
        }
    
    def validate_planet_data(self, planet_data):
        """Validate planet data structure"""
        required_fields = ['name', 'type', 'distance_au']
        
        for field in required_fields:
            if field not in planet_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate numeric fields
        numeric_fields = ['distance_au', 'mass_earth', 'radius_earth', 
                         'orbital_period_days', 'temperature_k']
        
        for field in numeric_fields:
            if field in planet_data:
                try:
                    float(planet_data[field])
                except (ValueError, TypeError):
                    raise ValueError(f"Field {field} must be numeric")
        
        return True