"""
Planetary System CRUD Manager
Comprehensive functions for managing planetary system data
"""

import sys
import os
from typing import Dict, List, Optional, Union
from datetime import datetime

# Add database path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
from config import get_collection
from schema import PlanetarySystemSchema

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class PlanetarySystemManager:
    """Comprehensive planetary system data management"""
    
    def __init__(self):
        self.systems_collection = get_collection('planetary_systems')
        self.stars_collection = get_collection('stars')
    
    # CREATE Operations
    def add_planetary_system(self, system_data: Dict) -> int:
        """Add a new planetary system to the database"""
        try:
            # Validate required fields
            if 'star_id' not in system_data:
                raise ValueError("Missing required field: star_id")
            
            star_id = system_data['star_id']
            
            # Check if system already exists
            if self.systems_collection.find_one({'_id': star_id}):
                raise ValueError(f"Planetary system for star {star_id} already exists")
            
            # Validate star exists
            star = self.stars_collection.find_one({'_id': star_id})
            if not star:
                raise ValueError(f"Star {star_id} does not exist")
            
            # Set defaults
            system_data.setdefault('system_name', star['names']['primary_name'] + ' System')
            system_data.setdefault('planets', [])
            system_data.setdefault('description', f"Planetary system around {star['names']['primary_name']}")
            
            # Calculate system properties
            planets = system_data.get('planets', [])
            system_data['total_planets'] = len(planets)
            system_data['habitable_worlds'] = [p for p in planets if p.get('has_life', False)]
            system_data['has_life'] = len(system_data['habitable_worlds']) > 0
            system_data['colonized'] = any(p.get('inhabited', False) for p in planets)
            system_data['total_population'] = sum(p.get('population', 0) for p in planets)
            
            # Create document using schema
            system_doc = PlanetarySystemSchema.create_document(star_id, system_data)
            
            # Insert into database
            result = self.systems_collection.insert_one(system_doc)
            
            return star_id
            
        except Exception as e:
            raise Exception(f"Failed to add planetary system: {str(e)}")
    
    def add_planet_to_system(self, star_id: int, planet_data: Dict) -> bool:
        """Add a planet to an existing system"""
        try:
            # Validate required planet fields
            required_fields = ['name', 'type', 'distance_au']
            for field in required_fields:
                if field not in planet_data:
                    raise ValueError(f"Missing required planet field: {field}")
            
            # Set planet defaults
            planet_data.setdefault('mass_earth', 1.0)
            planet_data.setdefault('radius_earth', 1.0)
            planet_data.setdefault('temperature_k', 288)
            planet_data.setdefault('atmosphere', 'Unknown')
            planet_data.setdefault('has_life', False)
            planet_data.setdefault('inhabited', False)
            planet_data.setdefault('population', 0)
            planet_data.setdefault('discovery_year', '2300')
            planet_data.setdefault('confirmed', True)
            
            # Calculate orbital period if not provided
            if 'orbital_period_days' not in planet_data:
                # Kepler's third law (simplified)
                planet_data['orbital_period_days'] = (planet_data['distance_au'] ** 1.5) * 365.25
            
            # Add planet to system
            result = self.systems_collection.update_one(
                {'_id': star_id},
                {
                    '$push': {'planets': planet_data},
                    '$set': {'metadata.updated_at': datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                # Recalculate system properties
                self._recalculate_system_properties(star_id)
                return True
            
            return False
            
        except Exception as e:
            raise Exception(f"Failed to add planet to system {star_id}: {str(e)}")
    
    def create_habitable_system(self,
                               star_id: int,
                               system_name: str = None,
                               num_planets: int = 3,
                               habitable_planet_name: str = "New Eden") -> int:
        """Create a system with a habitable world"""
        
        star = self.stars_collection.find_one({'_id': star_id})
        if not star:
            raise ValueError(f"Star {star_id} not found")
        
        if system_name is None:
            system_name = star['names']['primary_name'] + ' System'
        
        # Create a basic multi-planet system with one habitable world
        planets = []
        
        # Inner rocky planet (too hot)
        if num_planets >= 2:
            planets.append({
                'name': 'Scorcher',
                'type': 'Hot Terrestrial',
                'distance_au': 0.4,
                'mass_earth': 0.8,
                'radius_earth': 0.9,
                'orbital_period_days': 73,
                'temperature_k': 600,
                'atmosphere': 'CO2, traces of SO2',
                'has_life': False,
                'inhabited': False,
                'population': 0
            })
        
        # Habitable world
        planets.append({
            'name': habitable_planet_name,
            'type': 'Habitable Terrestrial',
            'distance_au': 1.2,
            'mass_earth': 1.1,
            'radius_earth': 1.05,
            'orbital_period_days': 481,
            'temperature_k': 285,
            'atmosphere': 'N2 (78%), O2 (21%), CO2 (400ppm)',
            'has_life': True,
            'inhabited': False,  # Can be colonized later
            'population': 0,
            'habitability_score': 0.9,
            'surface_water': True,
            'magnetic_field': True
        })
        
        # Outer gas giant (if requested)
        if num_planets >= 3:
            planets.append({
                'name': 'Guardian',
                'type': 'Gas Giant',
                'distance_au': 5.2,
                'mass_earth': 318,
                'radius_earth': 11.2,
                'orbital_period_days': 4333,
                'temperature_k': 120,
                'atmosphere': 'H2, He (Jupiter-like)',
                'has_life': False,
                'inhabited': False,
                'population': 0,
                'moon_count': 16,
                'ring_system': True
            })
        
        system_data = {
            'star_id': star_id,
            'system_name': system_name,
            'planets': planets,
            'description': f"A promising system with {len([p for p in planets if p.get('has_life')])} habitable world(s)",
            'system_age_billion_years': 4.5,
            'metallicity': 0.0,
            'exploration_level': 'Surveyed'
        }
        
        return self.add_planetary_system(system_data)
    
    # READ Operations
    def get_planetary_system(self, star_id: int) -> Optional[Dict]:
        """Get a complete planetary system by star ID"""
        system = self.systems_collection.find_one({'_id': star_id})
        if not system:
            return None
        
        # Get star information
        star = self.stars_collection.find_one({'_id': star_id})
        if star:
            system['star_data'] = {
                'id': star['_id'],
                'name': star['names']['primary_name'],
                'spectral_class': star['physical_properties']['spectral_class'],
                'magnitude': star['physical_properties']['magnitude'],
                'coordinates': star['coordinates']
            }
        
        return system
    
    def list_planetary_systems(self,
                              has_life: bool = None,
                              colonized: bool = None,
                              min_planets: int = None,
                              max_planets: int = None) -> List[Dict]:
        """List planetary systems with optional filters"""
        
        query = {}
        
        if has_life is not None:
            query['has_life'] = has_life
        
        if colonized is not None:
            query['colonized'] = colonized
        
        if min_planets is not None:
            query['total_planets'] = {'$gte': min_planets}
        
        if max_planets is not None:
            if 'total_planets' in query:
                query['total_planets']['$lte'] = max_planets
            else:
                query['total_planets'] = {'$lte': max_planets}
        
        systems = list(self.systems_collection.find(query).sort('system_name', 1))
        return [self._format_system_summary(system) for system in systems]
    
    def get_habitable_systems(self, min_habitability: float = 0.5) -> List[Dict]:
        """Get systems with habitable worlds"""
        # Find systems with life
        systems = list(self.systems_collection.find({'has_life': True}))
        
        habitable_systems = []
        for system in systems:
            # Check for planets with high habitability
            for planet in system.get('planets', []):
                habitability = planet.get('habitability_score', 0.0)
                if habitability >= min_habitability:
                    habitable_systems.append(self._format_system_summary(system))
                    break
        
        return habitable_systems
    
    def get_colonized_systems(self) -> List[Dict]:
        """Get all colonized systems"""
        systems = list(self.systems_collection.find({'colonized': True}))
        return [self._format_system_summary(system) for system in systems]
    
    def search_systems(self, query: str) -> List[Dict]:
        """Search systems by name or description"""
        search_query = {
            '$or': [
                {'system_name': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}},
                {'planets.name': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        systems = list(self.systems_collection.find(search_query))
        return [self._format_system_summary(system) for system in systems]
    
    def get_planet_details(self, star_id: int, planet_name: str) -> Optional[Dict]:
        """Get detailed information about a specific planet"""
        system = self.systems_collection.find_one({'_id': star_id})
        if not system:
            return None
        
        for planet in system.get('planets', []):
            if planet['name'].lower() == planet_name.lower():
                # Enhance planet data with calculated values
                enhanced_planet = planet.copy()
                enhanced_planet['system_name'] = system['system_name']
                enhanced_planet['star_id'] = star_id
                
                # Calculate additional properties
                if 'surface_gravity' not in enhanced_planet:
                    mass = enhanced_planet.get('mass_earth', 1.0)
                    radius = enhanced_planet.get('radius_earth', 1.0)
                    enhanced_planet['surface_gravity'] = mass / (radius ** 2)
                
                if 'escape_velocity' not in enhanced_planet:
                    mass = enhanced_planet.get('mass_earth', 1.0)
                    radius = enhanced_planet.get('radius_earth', 1.0)
                    enhanced_planet['escape_velocity'] = 11.2 * (mass / radius) ** 0.5
                
                return enhanced_planet
        
        return None
    
    # UPDATE Operations
    def update_planetary_system(self, star_id: int, update_data: Dict) -> bool:
        """Update planetary system information"""
        try:
            # Build update query
            update_query = {'$set': {}}
            
            # Map update fields
            allowed_fields = [
                'system_name', 'description', 'system_age_billion_years',
                'metallicity', 'exploration_level'
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    update_query['$set'][field] = update_data[field]
            
            # Add update timestamp
            update_query['$set']['metadata.updated_at'] = datetime.utcnow()
            
            if not update_query['$set']:
                return False
            
            # Execute update
            result = self.systems_collection.update_one(
                {'_id': star_id}, 
                update_query
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Failed to update planetary system {star_id}: {str(e)}")
    
    def update_planet(self, star_id: int, planet_name: str, update_data: Dict) -> bool:
        """Update a specific planet in a system"""
        try:
            # Build update query for array element
            update_query = {'$set': {}}
            
            # Find the planet index
            system = self.systems_collection.find_one({'_id': star_id})
            if not system:
                return False
            
            planet_index = None
            for i, planet in enumerate(system.get('planets', [])):
                if planet['name'].lower() == planet_name.lower():
                    planet_index = i
                    break
            
            if planet_index is None:
                raise ValueError(f"Planet {planet_name} not found in system {star_id}")
            
            # Map update fields to array element
            allowed_fields = [
                'population', 'inhabited', 'atmosphere', 'temperature_k',
                'has_life', 'habitability_score', 'description'
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    update_query['$set'][f'planets.{planet_index}.{field}'] = update_data[field]
            
            # Add update timestamp
            update_query['$set']['metadata.updated_at'] = datetime.utcnow()
            
            if not update_query['$set']:
                return False
            
            # Execute update
            result = self.systems_collection.update_one(
                {'_id': star_id}, 
                update_query
            )
            
            if result.modified_count > 0:
                # Recalculate system properties
                self._recalculate_system_properties(star_id)
                return True
            
            return False
            
        except Exception as e:
            raise Exception(f"Failed to update planet {planet_name} in system {star_id}: {str(e)}")
    
    def colonize_planet(self, star_id: int, planet_name: str, population: int = 1000000) -> bool:
        """Mark a planet as colonized with initial population"""
        return self.update_planet(star_id, planet_name, {
            'inhabited': True,
            'population': population,
            'colonization_date': datetime.utcnow().year
        })
    
    def terraform_planet(self, star_id: int, planet_name: str, new_atmosphere: str = None) -> bool:
        """Terraform a planet to make it more habitable"""
        update_data = {
            'has_life': True,
            'terraformed': True,
            'terraforming_date': datetime.utcnow().year
        }
        
        if new_atmosphere:
            update_data['atmosphere'] = new_atmosphere
        
        # Improve habitability score
        planet = self.get_planet_details(star_id, planet_name)
        if planet:
            current_habitability = planet.get('habitability_score', 0.3)
            update_data['habitability_score'] = min(0.9, current_habitability + 0.4)
        
        return self.update_planet(star_id, planet_name, update_data)
    
    # DELETE Operations
    def delete_planetary_system(self, star_id: int) -> bool:
        """Delete a planetary system from the database"""
        try:
            result = self.systems_collection.delete_one({'_id': star_id})
            return result.deleted_count > 0
            
        except Exception as e:
            raise Exception(f"Failed to delete planetary system {star_id}: {str(e)}")
    
    def remove_planet_from_system(self, star_id: int, planet_name: str) -> bool:
        """Remove a planet from a system"""
        try:
            result = self.systems_collection.update_one(
                {'_id': star_id},
                {
                    '$pull': {'planets': {'name': planet_name}},
                    '$set': {'metadata.updated_at': datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                # Recalculate system properties
                self._recalculate_system_properties(star_id)
                return True
            
            return False
            
        except Exception as e:
            raise Exception(f"Failed to remove planet {planet_name} from system {star_id}: {str(e)}")
    
    def remove_all_felgenland_systems(self) -> int:
        """Remove all Felgenland Saga planetary systems"""
        try:
            # Define star IDs associated with Felgenland nations
            felgenland_star_ids = [0, 71456, 71453, 70666, 53879, 118720, 48941, 32263, 999999]
            
            deleted_count = 0
            for star_id in felgenland_star_ids:
                try:
                    if self.delete_planetary_system(star_id):
                        deleted_count += 1
                except Exception as e:
                    print(f"Warning: Could not remove system {star_id}: {e}")
            
            return deleted_count
            
        except Exception as e:
            raise Exception(f"Failed to remove Felgenland systems: {str(e)}")
    
    # UTILITY Functions
    def validate_planet_data(self, planet_data: Dict) -> List[str]:
        """Validate planet data and return list of errors"""
        errors = []
        
        # Check required fields
        required_fields = ['name', 'type', 'distance_au']
        for field in required_fields:
            if field not in planet_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate data types and ranges
        if 'distance_au' in planet_data:
            if not isinstance(planet_data['distance_au'], (int, float)) or planet_data['distance_au'] <= 0:
                errors.append("Distance AU must be a positive number")
        
        if 'mass_earth' in planet_data:
            if not isinstance(planet_data['mass_earth'], (int, float)) or planet_data['mass_earth'] <= 0:
                errors.append("Mass (Earth units) must be a positive number")
        
        if 'radius_earth' in planet_data:
            if not isinstance(planet_data['radius_earth'], (int, float)) or planet_data['radius_earth'] <= 0:
                errors.append("Radius (Earth units) must be a positive number")
        
        if 'temperature_k' in planet_data:
            if not isinstance(planet_data['temperature_k'], (int, float)) or planet_data['temperature_k'] < 0:
                errors.append("Temperature must be a non-negative number in Kelvin")
        
        if 'population' in planet_data:
            if not isinstance(planet_data['population'], int) or planet_data['population'] < 0:
                errors.append("Population must be a non-negative integer")
        
        return errors
    
    def get_system_statistics(self) -> Dict:
        """Get comprehensive planetary system statistics"""
        try:
            total_systems = self.systems_collection.count_documents({})
            
            # Systems with life
            systems_with_life = self.systems_collection.count_documents({'has_life': True})
            
            # Colonized systems
            colonized_systems = self.systems_collection.count_documents({'colonized': True})
            
            # Planet count distribution
            planet_pipeline = [
                {'$group': {
                    '_id': '$total_planets',
                    'count': {'$sum': 1}
                }},
                {'$sort': {'_id': 1}}
            ]
            planet_distribution = list(self.systems_collection.aggregate(planet_pipeline))
            
            # Population statistics
            population_pipeline = [
                {'$match': {'colonized': True}},
                {'$group': {
                    '_id': None,
                    'total_population': {'$sum': '$total_population'},
                    'avg_population': {'$avg': '$total_population'},
                    'max_population': {'$max': '$total_population'}
                }}
            ]
            population_stats = list(self.systems_collection.aggregate(population_pipeline))
            
            # System age distribution
            age_pipeline = [
                {'$bucket': {
                    'groupBy': '$system_age_billion_years',
                    'boundaries': [0, 1, 3, 5, 8, 13],
                    'default': 'unknown',
                    'output': {'count': {'$sum': 1}}
                }}
            ]
            age_distribution = list(self.systems_collection.aggregate(age_pipeline))
            
            return {
                'total_systems': total_systems,
                'systems_with_life': systems_with_life,
                'colonized_systems': colonized_systems,
                'planet_count_distribution': {str(item['_id']): item['count'] for item in planet_distribution},
                'population_statistics': population_stats[0] if population_stats else {},
                'age_distribution': age_distribution,
                'habitability_percentage': round((systems_with_life / total_systems * 100), 2) if total_systems > 0 else 0,
                'colonization_percentage': round((colonized_systems / total_systems * 100), 2) if total_systems > 0 else 0
            }
            
        except Exception as e:
            raise Exception(f"Failed to get system statistics: {str(e)}")
    
    def analyze_habitability(self) -> Dict:
        """Analyze habitability across all systems"""
        try:
            # Get all systems with planets
            systems = list(self.systems_collection.find({'total_planets': {'$gt': 0}}))
            
            habitability_data = {
                'excellent': [],  # habitability >= 0.8
                'good': [],       # habitability >= 0.6
                'marginal': [],   # habitability >= 0.4
                'poor': []        # habitability < 0.4
            }
            
            planet_types = {}
            atmospheric_types = {}
            
            for system in systems:
                for planet in system.get('planets', []):
                    # Track planet types
                    ptype = planet.get('type', 'Unknown')
                    planet_types[ptype] = planet_types.get(ptype, 0) + 1
                    
                    # Track atmospheric types
                    atmosphere = planet.get('atmosphere', 'Unknown')
                    atmospheric_types[atmosphere] = atmospheric_types.get(atmosphere, 0) + 1
                    
                    # Categorize by habitability
                    habitability = planet.get('habitability_score', 0.0)
                    planet_info = {
                        'system_name': system['system_name'],
                        'planet_name': planet['name'],
                        'star_id': system['_id'],
                        'habitability_score': habitability,
                        'has_life': planet.get('has_life', False),
                        'inhabited': planet.get('inhabited', False)
                    }
                    
                    if habitability >= 0.8:
                        habitability_data['excellent'].append(planet_info)
                    elif habitability >= 0.6:
                        habitability_data['good'].append(planet_info)
                    elif habitability >= 0.4:
                        habitability_data['marginal'].append(planet_info)
                    else:
                        habitability_data['poor'].append(planet_info)
            
            return {
                'habitability_categories': {
                    'excellent': len(habitability_data['excellent']),
                    'good': len(habitability_data['good']),
                    'marginal': len(habitability_data['marginal']),
                    'poor': len(habitability_data['poor'])
                },
                'top_habitable_worlds': habitability_data['excellent'][:10],
                'planet_type_distribution': planet_types,
                'atmospheric_distribution': atmospheric_types,
                'colonization_candidates': [
                    p for p in habitability_data['excellent'] + habitability_data['good']
                    if not p['inhabited'] and p['habitability_score'] >= 0.7
                ]
            }
            
        except Exception as e:
            raise Exception(f"Failed to analyze habitability: {str(e)}")
    
    def import_from_python_dict(self, systems_dict: Dict) -> int:
        """Import planetary systems from Python dictionary"""
        try:
            added_count = 0
            
            for star_id, planets_list in systems_dict.items():
                try:
                    # Convert star_id to int if it's a string
                    star_id = int(star_id)
                    
                    system_data = {
                        'star_id': star_id,
                        'planets': planets_list if isinstance(planets_list, list) else [planets_list]
                    }
                    
                    self.add_planetary_system(system_data)
                    added_count += 1
                    
                except Exception as e:
                    print(f"Warning: Could not import system {star_id}: {e}")
            
            return added_count
            
        except Exception as e:
            raise Exception(f"Failed to import from Python dict: {str(e)}")
    
    # Private helper methods
    def _recalculate_system_properties(self, star_id: int):
        """Recalculate system-wide properties after planet changes"""
        system = self.systems_collection.find_one({'_id': star_id})
        if not system:
            return
        
        planets = system.get('planets', [])
        
        # Recalculate properties
        properties = {
            'total_planets': len(planets),
            'habitable_worlds': [p for p in planets if p.get('has_life', False)],
            'has_life': any(p.get('has_life', False) for p in planets),
            'colonized': any(p.get('inhabited', False) for p in planets),
            'total_population': sum(p.get('population', 0) for p in planets),
            'metadata.updated_at': datetime.utcnow()
        }
        
        # Update system
        self.systems_collection.update_one(
            {'_id': star_id},
            {'$set': properties}
        )
    
    def _format_system_summary(self, system_doc: Dict) -> Dict:
        """Format system document for summary display"""
        return {
            'star_id': system_doc['_id'],
            'system_name': system_doc['system_name'],
            'total_planets': system_doc['total_planets'],
            'has_life': system_doc['has_life'],
            'colonized': system_doc['colonized'],
            'total_population': system_doc.get('total_population', 0),
            'habitable_worlds_count': len(system_doc.get('habitable_worlds', [])),
            'exploration_level': system_doc.get('exploration_level', 'Unknown'),
            'description': system_doc['description'],
            'planets': [
                {
                    'name': p['name'],
                    'type': p['type'],
                    'has_life': p.get('has_life', False),
                    'inhabited': p.get('inhabited', False),
                    'population': p.get('population', 0),
                    'habitability_score': p.get('habitability_score', 0.0)
                }
                for p in system_doc.get('planets', [])
            ]
        }