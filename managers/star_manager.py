"""
Star CRUD Manager
Comprehensive functions for managing star data
"""

import sys
import os
import math
from typing import Dict, List, Optional, Union
from datetime import datetime

# Add database path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
from config import get_collection
from schema import StarSchema

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.star_model_db import StarModelDB


class StarManager:
    """Comprehensive star data management"""
    
    def __init__(self):
        self.star_model = StarModelDB()
        self.stars_collection = get_collection('stars')
    
    # CREATE Operations
    def add_star(self, star_data: Dict) -> int:
        """Add a new star to the database"""
        try:
            # Validate required fields
            required_fields = ['id', 'x', 'y', 'z', 'mag', 'spect']
            for field in required_fields:
                if field not in star_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Check if star ID already exists
            if self.stars_collection.find_one({'_id': star_data['id']}):
                raise ValueError(f"Star with ID {star_data['id']} already exists")
            
            # Calculate derived values
            star_data = self._calculate_derived_values(star_data)
            
            # Create document using schema
            star_doc = StarSchema.create_document(star_data)
            
            # Insert into database
            result = self.stars_collection.insert_one(star_doc)
            
            return star_data['id']
            
        except Exception as e:
            raise Exception(f"Failed to add star: {str(e)}")
    
    def add_star_batch(self, stars_data: List[Dict]) -> List[int]:
        """Add multiple stars in batch"""
        added_stars = []
        errors = []
        
        for i, star_data in enumerate(stars_data):
            try:
                star_id = self.add_star(star_data)
                added_stars.append(star_id)
            except Exception as e:
                errors.append(f"Star {i}: {str(e)}")
        
        if errors:
            print(f"Batch add completed with {len(errors)} errors:")
            for error in errors:
                print(f"  - {error}")
        
        return added_stars
    
    def import_from_csv(self, csv_file_path: str) -> int:
        """Import stars from CSV file"""
        import pandas as pd
        
        try:
            df = pd.read_csv(csv_file_path)
            stars_data = df.to_dict('records')
            
            added_stars = self.add_star_batch(stars_data)
            return len(added_stars)
            
        except Exception as e:
            raise Exception(f"Failed to import from CSV: {str(e)}")
    
    # READ Operations
    def get_star(self, star_id: int) -> Optional[Dict]:
        """Get a specific star by ID"""
        return self.star_model.get_star_details(star_id)
    
    def search_stars(self, 
                    query: str = None, 
                    spectral_type: str = None,
                    magnitude_range: tuple = None,
                    coordinate_range: Dict = None,
                    nation_id: str = None,
                    has_planets: bool = None,
                    habitability_min: float = None,
                    limit: int = 100) -> List[Dict]:
        """Advanced star search with multiple filters"""
        
        # Build MongoDB query
        mongo_query = {}
        
        # Text search
        if query:
            mongo_query['$or'] = [
                {'names.primary_name': {'$regex': query, '$options': 'i'}},
                {'names.fictional_name': {'$regex': query, '$options': 'i'}},
                {'names.proper_name': {'$regex': query, '$options': 'i'}}
            ]
        
        # Spectral type filter
        if spectral_type:
            mongo_query['physical_properties.spectral_class'] = {
                '$regex': f'^{spectral_type.upper()}', '$options': 'i'
            }
        
        # Magnitude range
        if magnitude_range:
            min_mag, max_mag = magnitude_range
            mongo_query['physical_properties.magnitude'] = {
                '$gte': min_mag, '$lte': max_mag
            }
        
        # Coordinate range
        if coordinate_range:
            for coord in ['x', 'y', 'z']:
                if coord in coordinate_range:
                    min_val, max_val = coordinate_range[coord]
                    mongo_query[f'coordinates.{coord}'] = {
                        '$gte': min_val, '$lte': max_val
                    }
        
        # Nation control
        if nation_id:
            mongo_query['political.nation_id'] = nation_id
        
        # Habitability
        if habitability_min:
            mongo_query['habitability.score'] = {'$gte': habitability_min}
        
        # Planetary systems
        if has_planets is not None:
            if has_planets:
                # Find stars that have planetary systems
                systems_collection = get_collection('planetary_systems')
                systems_with_planets = list(systems_collection.find(
                    {'total_planets': {'$gt': 0}}, {'_id': 1}
                ))
                star_ids_with_planets = [s['_id'] for s in systems_with_planets]
                mongo_query['_id'] = {'$in': star_ids_with_planets}
            else:
                # Find stars that don't have planetary systems
                systems_collection = get_collection('planetary_systems')
                systems_with_planets = list(systems_collection.find({}, {'_id': 1}))
                star_ids_with_planets = [s['_id'] for s in systems_with_planets]
                mongo_query['_id'] = {'$nin': star_ids_with_planets}
        
        # Execute query
        stars = list(self.stars_collection.find(mongo_query).limit(limit))
        
        # Format results
        return [self._format_star_summary(star) for star in stars]
    
    def get_stars_in_region(self, 
                           x_range: tuple, 
                           y_range: tuple, 
                           z_range: tuple,
                           limit: int = None) -> List[Dict]:
        """Get all stars within specified coordinate ranges"""
        
        query = {
            'coordinates.x': {'$gte': x_range[0], '$lte': x_range[1]},
            'coordinates.y': {'$gte': y_range[0], '$lte': y_range[1]},
            'coordinates.z': {'$gte': z_range[0], '$lte': z_range[1]}
        }
        
        cursor = self.stars_collection.find(query)
        if limit:
            cursor = cursor.limit(limit)
        
        return [self._format_star_summary(star) for star in cursor]
    
    def get_nearest_stars(self, 
                         reference_star_id: int, 
                         max_distance: float = 20.0,
                         limit: int = 10) -> List[Dict]:
        """Find nearest stars to a reference star"""
        
        reference_star = self.stars_collection.find_one({'_id': reference_star_id})
        if not reference_star:
            raise ValueError(f"Reference star {reference_star_id} not found")
        
        ref_coords = reference_star['coordinates']
        ref_x, ref_y, ref_z = ref_coords['x'], ref_coords['y'], ref_coords['z']
        
        # Find stars in a cubic region around the reference
        nearby_stars = self.get_stars_in_region(
            x_range=(ref_x - max_distance, ref_x + max_distance),
            y_range=(ref_y - max_distance, ref_y + max_distance),
            z_range=(ref_z - max_distance, ref_z + max_distance)
        )
        
        # Calculate distances and sort
        stars_with_distance = []
        for star in nearby_stars:
            if star['id'] == reference_star_id:
                continue  # Skip the reference star itself
            
            distance = math.sqrt(
                (star['coordinates']['x'] - ref_x) ** 2 +
                (star['coordinates']['y'] - ref_y) ** 2 +
                (star['coordinates']['z'] - ref_z) ** 2
            )
            
            if distance <= max_distance:
                star['distance_from_reference'] = round(distance, 3)
                stars_with_distance.append(star)
        
        # Sort by distance and limit results
        stars_with_distance.sort(key=lambda x: x['distance_from_reference'])
        return stars_with_distance[:limit]
    
    # UPDATE Operations
    def update_star(self, star_id: int, update_data: Dict) -> bool:
        """Update star information"""
        try:
            # Build update query
            update_query = {'$set': {}}
            
            # Map update fields to database structure
            field_mapping = {
                'fictional_name': 'names.fictional_name',
                'fictional_description': 'names.fictional_description',
                'fictional_source': 'names.fictional_source',
                'nation_id': 'political.nation_id',
                'strategic_importance': 'political.strategic_importance',
                'magnitude': 'physical_properties.magnitude',
                'spectral_class': 'physical_properties.spectral_class',
                'luminosity': 'physical_properties.luminosity'
            }
            
            for field, db_field in field_mapping.items():
                if field in update_data:
                    update_query['$set'][db_field] = update_data[field]
            
            # Add update timestamp
            update_query['$set']['metadata.updated_at'] = datetime.utcnow()
            
            if not update_query['$set']:
                return False
            
            # Execute update
            result = self.stars_collection.update_one(
                {'_id': star_id}, 
                update_query
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Failed to update star {star_id}: {str(e)}")
    
    def update_star_coordinates(self, star_id: int, x: float, y: float, z: float) -> bool:
        """Update star coordinates and recalculate derived values"""
        try:
            # Calculate distance from Sol
            distance = math.sqrt(x**2 + y**2 + z**2)
            
            update_query = {'$set': {
                'coordinates.x': x,
                'coordinates.y': y,
                'coordinates.z': z,
                'coordinates.dist': distance,
                'metadata.updated_at': datetime.utcnow()
            }}
            
            result = self.stars_collection.update_one({'_id': star_id}, update_query)
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Failed to update coordinates for star {star_id}: {str(e)}")
    
    def assign_to_nation(self, star_id: int, nation_id: str, strategic_importance: str = 'territory') -> bool:
        """Assign a star to a nation's control"""
        try:
            # Update star's political data
            star_update = self.update_star(star_id, {
                'nation_id': nation_id,
                'strategic_importance': strategic_importance
            })
            
            # Update nation's territory list
            nations_collection = get_collection('nations')
            nations_collection.update_one(
                {'_id': nation_id},
                {'$addToSet': {'territories': star_id}}
            )
            
            return star_update
            
        except Exception as e:
            raise Exception(f"Failed to assign star {star_id} to nation {nation_id}: {str(e)}")
    
    def remove_from_nation(self, star_id: int) -> bool:
        """Remove a star from nation control"""
        try:
            # Get current nation assignment
            star = self.stars_collection.find_one({'_id': star_id})
            if not star:
                return False
            
            current_nation = star.get('political', {}).get('nation_id')
            
            # Update star's political data
            star_update = self.update_star(star_id, {
                'nation_id': None,
                'strategic_importance': 'normal'
            })
            
            # Remove from nation's territory list
            if current_nation:
                nations_collection = get_collection('nations')
                nations_collection.update_one(
                    {'_id': current_nation},
                    {'$pull': {'territories': star_id}}
                )
            
            return star_update
            
        except Exception as e:
            raise Exception(f"Failed to remove star {star_id} from nation control: {str(e)}")
    
    # DELETE Operations
    def delete_star(self, star_id: int, force: bool = False) -> bool:
        """Delete a star from the database"""
        try:
            # Check for dependencies
            if not force:
                dependencies = self._check_star_dependencies(star_id)
                if dependencies:
                    raise Exception(f"Cannot delete star {star_id}. Dependencies: {dependencies}")
            
            # Remove from nation territories
            self.remove_from_nation(star_id)
            
            # Remove trade routes
            self._remove_star_trade_routes(star_id)
            
            # Remove planetary system
            systems_collection = get_collection('planetary_systems')
            systems_collection.delete_one({'_id': star_id})
            
            # Delete the star
            result = self.stars_collection.delete_one({'_id': star_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            raise Exception(f"Failed to delete star {star_id}: {str(e)}")
    
    def delete_fictional_stars(self) -> int:
        """Delete all fictional stars (non-real catalog stars)"""
        try:
            # Find fictional stars (those with fictional_name or high IDs)
            fictional_query = {
                '$or': [
                    {'names.fictional_name': {'$ne': None}},
                    {'_id': {'$gte': 500000}}  # Assume fictional stars have high IDs
                ]
            }
            
            fictional_stars = list(self.stars_collection.find(fictional_query, {'_id': 1}))
            
            deleted_count = 0
            for star in fictional_stars:
                try:
                    if self.delete_star(star['_id'], force=True):
                        deleted_count += 1
                except Exception as e:
                    print(f"Warning: Could not delete fictional star {star['_id']}: {e}")
            
            return deleted_count
            
        except Exception as e:
            raise Exception(f"Failed to delete fictional stars: {str(e)}")
    
    # UTILITY Functions
    def validate_star_data(self, star_data: Dict) -> List[str]:
        """Validate star data and return list of errors"""
        errors = []
        
        # Check required fields
        required_fields = ['id', 'x', 'y', 'z', 'mag', 'spect']
        for field in required_fields:
            if field not in star_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate data types and ranges
        if 'id' in star_data:
            if not isinstance(star_data['id'], int) or star_data['id'] < 0:
                errors.append("ID must be a positive integer")
        
        if 'mag' in star_data:
            if not isinstance(star_data['mag'], (int, float)) or star_data['mag'] < -30 or star_data['mag'] > 30:
                errors.append("Magnitude must be a number between -30 and 30")
        
        for coord in ['x', 'y', 'z']:
            if coord in star_data:
                if not isinstance(star_data[coord], (int, float)):
                    errors.append(f"Coordinate {coord} must be a number")
        
        if 'spect' in star_data:
            if not isinstance(star_data['spect'], str) or len(star_data['spect']) == 0:
                errors.append("Spectral class must be a non-empty string")
        
        return errors
    
    def get_star_statistics(self) -> Dict:
        """Get comprehensive star database statistics"""
        try:
            total_stars = self.stars_collection.count_documents({})
            
            # Spectral class distribution
            spectral_pipeline = [
                {'$group': {
                    '_id': {'$substr': ['$physical_properties.spectral_class', 0, 1]},
                    'count': {'$sum': 1}
                }},
                {'$sort': {'_id': 1}}
            ]
            spectral_dist = list(self.stars_collection.aggregate(spectral_pipeline))
            
            # Nation control distribution
            nation_pipeline = [
                {'$group': {
                    '_id': '$political.nation_id',
                    'count': {'$sum': 1}
                }},
                {'$sort': {'count': -1}}
            ]
            nation_dist = list(self.stars_collection.aggregate(nation_pipeline))
            
            # Fictional vs real stars
            fictional_count = self.stars_collection.count_documents({
                'names.fictional_name': {'$ne': None}
            })
            
            # Distance distribution
            distance_pipeline = [
                {'$bucket': {
                    'groupBy': '$coordinates.dist',
                    'boundaries': [0, 10, 25, 50, 100, 250, 500, 1000],
                    'default': 'other',
                    'output': {'count': {'$sum': 1}}
                }}
            ]
            distance_dist = list(self.stars_collection.aggregate(distance_pipeline))
            
            return {
                'total_stars': total_stars,
                'fictional_stars': fictional_count,
                'real_stars': total_stars - fictional_count,
                'spectral_distribution': {item['_id']: item['count'] for item in spectral_dist},
                'nation_distribution': {item['_id']: item['count'] for item in nation_dist if item['_id']},
                'uncontrolled_stars': next((item['count'] for item in nation_dist if item['_id'] is None), 0),
                'distance_distribution': distance_dist
            }
            
        except Exception as e:
            raise Exception(f"Failed to get star statistics: {str(e)}")
    
    # Private helper methods
    def _calculate_derived_values(self, star_data: Dict) -> Dict:
        """Calculate derived values from basic star data"""
        # Calculate distance if not provided
        if 'dist' not in star_data:
            x, y, z = star_data['x'], star_data['y'], star_data['z']
            star_data['dist'] = math.sqrt(x**2 + y**2 + z**2)
        
        # Calculate absolute magnitude if not provided
        if 'absmag' not in star_data:
            distance_parsecs = star_data['dist']
            if distance_parsecs > 0:
                star_data['absmag'] = star_data['mag'] - 5 * (math.log10(distance_parsecs) - 1)
            else:
                star_data['absmag'] = star_data['mag']
        
        # Estimate luminosity from spectral class if not provided
        if 'lum' not in star_data:
            star_data['lum'] = self._estimate_luminosity(star_data.get('spect', 'G2V'))
        
        return star_data
    
    def _estimate_luminosity(self, spectral_class: str) -> float:
        """Estimate luminosity from spectral class"""
        luminosity_map = {
            'O': 30000, 'B': 1000, 'A': 25, 'F': 3,
            'G': 1, 'K': 0.4, 'M': 0.04, 'L': 0.001, 'T': 0.0001
        }
        
        if spectral_class and len(spectral_class) > 0:
            main_class = spectral_class[0].upper()
            return luminosity_map.get(main_class, 1.0)
        
        return 1.0
    
    def _format_star_summary(self, star_doc: Dict) -> Dict:
        """Format star document for summary display"""
        return {
            'id': star_doc['_id'],
            'name': star_doc['names']['primary_name'],
            'fictional_name': star_doc['names'].get('fictional_name'),
            'coordinates': star_doc['coordinates'],
            'magnitude': star_doc['physical_properties']['magnitude'],
            'spectral_class': star_doc['physical_properties']['spectral_class'],
            'nation_id': star_doc['political'].get('nation_id'),
            'strategic_importance': star_doc['political'].get('strategic_importance'),
            'habitability_score': star_doc['habitability']['score'],
            'has_planets': False  # Will be filled by caller if needed
        }
    
    def _check_star_dependencies(self, star_id: int) -> List[str]:
        """Check what depends on this star"""
        dependencies = []
        
        # Check if it's a nation capital
        nations_collection = get_collection('nations')
        capital_nation = nations_collection.find_one({'capital.star_id': star_id})
        if capital_nation:
            dependencies.append(f"Capital of {capital_nation['name']}")
        
        # Check trade routes
        trade_routes_collection = get_collection('trade_routes')
        routes = trade_routes_collection.find({
            '$or': [
                {'endpoints.from.star_id': star_id},
                {'endpoints.to.star_id': star_id}
            ]
        })
        route_count = len(list(routes))
        if route_count > 0:
            dependencies.append(f"Connected to {route_count} trade routes")
        
        return dependencies
    
    def _remove_star_trade_routes(self, star_id: int):
        """Remove all trade routes connected to a star"""
        trade_routes_collection = get_collection('trade_routes')
        trade_routes_collection.delete_many({
            '$or': [
                {'endpoints.from.star_id': star_id},
                {'endpoints.to.star_id': star_id}
            ]
        })