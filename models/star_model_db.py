"""
Star model using MontyDB
"""

import math
from datetime import datetime
from .base_model_db import BaseModelDB


class StarModelDB(BaseModelDB):
    """MontyDB-based star model with enhanced querying capabilities"""
    
    def __init__(self):
        super().__init__('stars')
        self._filtered_cache = {}
        self._search_cache = {}
    
    def _initialize_collection(self):
        """Initialize star collection with indexes"""
        # Create indexes for common queries
        try:
            self.create_index([("coordinates.x", 1), ("coordinates.y", 1), ("coordinates.z", 1)])
            self.create_index([("physical_properties.magnitude", 1)])
            self.create_index([("physical_properties.spectral_class", 1)])
            self.create_index([("names.primary_name", 1)])
            self.create_index([("names.fictional_name", 1)])
            self.create_index([("political.nation_id", 1)])
            self.create_index([("habitability.category", 1)])
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")
    
    def get_stars_for_display(self, mag_limit=6.0, count_limit=1000, spectral_filter=None):
        """Get stars suitable for display with filtering and sorting"""
        # Build query
        query = {}
        
        # Magnitude filter with special handling for fictional/nation stars
        if mag_limit is not None:
            query = {
                '$or': [
                    {'physical_properties.magnitude': {'$lte': mag_limit}},
                    {'names.fictional_name': {'$exists': True, '$ne': None}},
                    {'political.nation_id': {'$exists': True, '$ne': None}}
                ]
            }
        
        # Spectral class filter
        if spectral_filter:
            spectral_query = {
                'physical_properties.spectral_class': {
                    '$regex': f'^{spectral_filter.upper()}',
                    '$options': 'i'
                }
            }
            
            if query:
                query = {'$and': [query, spectral_query]}
            else:
                query = spectral_query
        
        # Sort by priority: nation stars first, then by magnitude
        pipeline = [
            {'$match': query},
            {'$addFields': {
                'display_priority': {
                    '$cond': {
                        'if': {'$ne': ['$political.nation_id', None]},
                        'then': 0,
                        'else': 1
                    }
                }
            }},
            {'$sort': {'display_priority': 1, 'physical_properties.magnitude': 1}},
            {'$limit': count_limit}
        ]
        
        stars = self.aggregate(pipeline)
        return self._format_stars_for_json(stars)
    
    def get_star_details(self, star_id):
        """Get detailed information for a specific star"""
        star = self.get_by_id(star_id)
        if not star:
            return None
        
        # Get nation details if star is controlled
        nation_data = None
        if star.get('political', {}).get('nation_id'):
            nation_collection = self.collection.database.nations
            nation = nation_collection.find_one({'_id': star['political']['nation_id']})
            if nation:
                nation_data = {
                    'id': nation['_id'],
                    'name': nation['name'],
                    'color': nation['appearance']['color'],
                    'government_type': nation['government']['type'],
                    'capital_system': nation['capital']['system'],
                    'population': nation['economy'].get('population'),
                    'description': nation['description']
                }
        
        # Get planetary system data
        planetary_system = None
        systems_collection = self.collection.database.planetary_systems
        system = systems_collection.find_one({'_id': star_id})
        if system:
            planetary_system = {
                'planets': system.get('planets', []),
                'habitable_worlds': system.get('habitable_worlds', []),
                'total_planets': system.get('total_planets', 0),
                'has_life': system.get('has_life', False),
                'colonized': system.get('colonized', False)
            }
        
        return {
            'id': star['_id'],
            'name': star['names']['primary_name'],
            'all_names': star['names'].get('all_names', []),
            'catalog_ids': star['names'].get('catalog_ids', []),
            'designation_type': star['names'].get('designation_type', 'catalog'),
            'constellation': star['classification'].get('constellation', ''),
            'constellation_full': star['classification'].get('constellation_full', ''),
            'coordinates': star['coordinates'],
            'properties': star['physical_properties'],
            'motion': star['motion'],
            'fictional_data': {
                'name': star['names'].get('fictional_name'),
                'source': star['names'].get('fictional_source'),
                'description': star['names'].get('fictional_description')
            },
            'habitability': star['habitability'],
            'nation': nation_data,
            'planetary_system': planetary_system,
            'classification': star['classification']
        }
    
    def search_stars(self, query, spectral_type=None, limit=50):
        """Search stars by name, identifier, or spectral type"""
        if not query and not spectral_type:
            return []
        
        # Build search query
        search_conditions = []
        
        if query:
            # Search in multiple name fields
            name_regex = {'$regex': query, '$options': 'i'}
            search_conditions.extend([
                {'names.primary_name': name_regex},
                {'names.proper_name': name_regex},
                {'names.fictional_name': name_regex},
                {'names.all_names': {'$elemMatch': name_regex}}
            ])
        
        if spectral_type:
            search_conditions.append({
                'physical_properties.spectral_class': {
                    '$regex': f'^{spectral_type.upper()}',
                    '$options': 'i'
                }
            })
        
        # Combine conditions
        if len(search_conditions) == 1:
            search_query = search_conditions[0]
        elif query and spectral_type:
            # Both query and spectral type - use AND
            search_query = {'$and': [
                {'$or': search_conditions[:-1]},  # Name searches
                search_conditions[-1]  # Spectral type search
            ]}
        else:
            # Multiple name searches - use OR
            search_query = {'$or': search_conditions}
        
        stars = self.find(search_query, limit=limit, sort=[('physical_properties.magnitude', 1)])
        return self._format_search_results(stars)
    
    def calculate_distance(self, star1_id, star2_id):
        """Calculate distance between two stars"""
        star1 = self.get_by_id(star1_id)
        star2 = self.get_by_id(star2_id)
        
        if not star1 or not star2:
            return None
        
        # Extract coordinates
        coords1 = star1['coordinates']
        coords2 = star2['coordinates']
        
        x1, y1, z1 = coords1['x'], coords1['y'], coords1['z']
        x2, y2, z2 = coords2['x'], coords2['y'], coords2['z']
        
        # Calculate 3D distance
        distance_parsecs = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
        distance_light_years = distance_parsecs * 3.26156
        
        # Calculate distances from Sol
        sol_distance_1_pc = math.sqrt(x1**2 + y1**2 + z1**2)
        sol_distance_2_pc = math.sqrt(x2**2 + y2**2 + z2**2)
        
        return {
            'star1': {
                'id': star1_id,
                'name': star1['names']['primary_name'],
                'distance_from_sol_pc': round(sol_distance_1_pc, 4),
                'distance_from_sol_ly': round(sol_distance_1_pc * 3.26156, 4)
            },
            'star2': {
                'id': star2_id,
                'name': star2['names']['primary_name'],
                'distance_from_sol_pc': round(sol_distance_2_pc, 4),
                'distance_from_sol_ly': round(sol_distance_2_pc * 3.26156, 4)
            },
            'distance_between': {
                'parsecs': round(distance_parsecs, 4),
                'light_years': round(distance_light_years, 4),
                'astronomical_units': round(distance_parsecs * 206265, 0),
                'kilometers': round(distance_light_years * 9.461e12, 0)
            }
        }
    
    def get_spectral_types(self):
        """Get list of available spectral types"""
        pipeline = [
            {'$group': {
                '_id': '$physical_properties.spectral_class',
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        spectral_data = self.aggregate(pipeline)
        
        # Categorize by main spectral class
        main_types = {}
        for item in spectral_data:
            spect = item['_id']
            if spect and len(spect) > 0:
                main_class = spect[0].upper()
                if main_class in ['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L', 'T', 'Y']:
                    if main_class not in main_types:
                        main_types[main_class] = []
                    main_types[main_class].append({
                        'type': spect,
                        'count': item['count']
                    })
        
        return {
            'main_types': main_types,
            'total_types': len(spectral_data),
            'description': {
                'O': 'Blue giants - Very hot, massive stars',
                'B': 'Blue-white stars - Hot, massive stars',
                'A': 'White stars - Hot stars with strong hydrogen lines',
                'F': 'Yellow-white stars - Slightly hotter than Sun',
                'G': 'Yellow stars - Sun-like stars',
                'K': 'Orange stars - Cooler than Sun',
                'M': 'Red stars - Cool, low-mass stars',
                'L': 'Brown dwarfs - Very cool objects',
                'T': 'Methane brown dwarfs - Ultra-cool objects'
            }
        }
    
    def get_stars_by_region(self, region_name, limit=None):
        """Get stars within a specific stellar region"""
        # Get region boundaries
        regions_collection = self.collection.database.stellar_regions
        region = regions_collection.find_one({'_id': region_name.replace(' ', '_').lower()})
        
        if not region:
            return []
        
        boundaries = region['boundaries']
        
        # Build coordinate query
        query = {
            'coordinates.x': {
                '$gte': boundaries['x_range'][0],
                '$lte': boundaries['x_range'][1]
            },
            'coordinates.y': {
                '$gte': boundaries['y_range'][0],
                '$lte': boundaries['y_range'][1]
            },
            'coordinates.z': {
                '$gte': boundaries['z_range'][0],
                '$lte': boundaries['z_range'][1]
            }
        }
        
        sort = [('physical_properties.magnitude', 1)]
        stars = self.find(query, limit=limit, sort=sort)
        
        return self._format_stars_for_json(stars)
    
    def get_stars_by_nation(self, nation_id, limit=None):
        """Get all stars controlled by a specific nation"""
        query = {'political.nation_id': nation_id}
        sort = [('political.strategic_importance', 1), ('physical_properties.magnitude', 1)]
        
        stars = self.find(query, limit=limit, sort=sort)
        return self._format_stars_for_json(stars)
    
    def get_habitable_stars(self, min_score=0.5, limit=None):
        """Get stars with good habitability scores"""
        query = {'habitability.score': {'$gte': min_score}}
        sort = [('habitability.score', -1)]
        
        stars = self.find(query, limit=limit, sort=sort)
        return self._format_stars_for_json(stars)
    
    def get_stats(self):
        """Get database statistics"""
        total_stars = self.count_documents()
        
        # Get spectral class distribution
        spectral_pipeline = [
            {'$group': {
                '_id': {'$substr': ['$physical_properties.spectral_class', 0, 1]},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        spectral_dist = self.aggregate(spectral_pipeline)
        
        # Get nation distribution
        nation_pipeline = [
            {'$group': {
                '_id': '$political.nation_id',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        nation_dist = self.aggregate(nation_pipeline)
        
        # Get habitability distribution
        habitability_pipeline = [
            {'$group': {
                '_id': '$habitability.category',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        habitability_dist = self.aggregate(habitability_pipeline)
        
        return {
            'total_stars': total_stars,
            'spectral_distribution': spectral_dist,
            'nation_distribution': nation_dist,
            'habitability_distribution': habitability_dist,
            'collection_info': {
                'indexes': len(self.collection.list_indexes()),
                'cache_stats': self.get_cache_stats()
            }
        }
    
    def _format_stars_for_json(self, stars):
        """Convert star documents to JSON-serializable format"""
        formatted_stars = []
        
        for star in stars:
            formatted_star = {
                'id': star['_id'],
                'name': star['names']['primary_name'],
                'all_names': star['names'].get('all_names', []),
                'catalog_ids': star['names'].get('catalog_ids', []),
                'designation_type': star['names'].get('designation_type', 'catalog'),
                'constellation': star['classification'].get('constellation', ''),
                'constellation_full': star['classification'].get('constellation_full', ''),
                'x': star['coordinates']['x'],
                'y': star['coordinates']['y'],
                'z': star['coordinates']['z'],
                'mag': star['physical_properties']['magnitude'],
                'spect': star['physical_properties']['spectral_class'],
                'dist': star['coordinates']['dist'],
                'fictional_name': star['names'].get('fictional_name'),
                'fictional_source': star['names'].get('fictional_source'),
                'fictional_description': star['names'].get('fictional_description'),
                'nation': self._get_nation_data(star.get('political', {}).get('nation_id')),
                'planets': []  # Will be populated separately if needed
            }
            formatted_stars.append(formatted_star)
        
        return formatted_stars
    
    def _format_search_results(self, stars):
        """Format search results for API response"""
        search_results = []
        
        for star in stars:
            result = {
                'id': star['_id'],
                'name': star['names']['primary_name'],
                'all_names': star['names'].get('all_names', []),
                'designation_type': star['names'].get('designation_type', 'catalog'),
                'constellation': star['classification'].get('constellation_full', ''),
                'magnitude': star['physical_properties']['magnitude'],
                'distance': star['coordinates']['dist'],
                'spectral_class': star['physical_properties']['spectral_class'],
                'coordinates': star['coordinates'],
                'fictional_name': star['names'].get('fictional_name'),
                'fictional_source': star['names'].get('fictional_source')
            }
            search_results.append(result)
        
        return search_results
    
    def _get_nation_data(self, nation_id):
        """Get nation data for a star (cached)"""
        if not nation_id:
            return None
        
        cache_key = f"nation_{nation_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        nations_collection = self.collection.database.nations
        nation = nations_collection.find_one({'_id': nation_id})
        
        if nation:
            nation_data = {
                'id': nation_id,
                'name': nation['name'],
                'color': nation['appearance']['color'],
                'government_type': nation['government']['type']
            }
            self._cache[cache_key] = nation_data
            return nation_data
        
        return None
    
    def add_star(self, star_data):
        """Add a new star to the database"""
        from database.schema import StarSchema
        
        # Validate star data
        required_fields = ['id', 'x', 'y', 'z', 'mag', 'spect']
        for field in required_fields:
            if field not in star_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create document
        star_doc = StarSchema.create_document(star_data)
        
        # Insert into database
        result = self.insert_one(star_doc)
        return result.inserted_id
    
    def update_star(self, star_id, update_data):
        """Update an existing star"""
        # Build update query
        update_query = {'$set': {}}
        
        # Update allowed fields
        if 'fictional_name' in update_data:
            update_query['$set']['names.fictional_name'] = update_data['fictional_name']
        if 'fictional_description' in update_data:
            update_query['$set']['names.fictional_description'] = update_data['fictional_description']
        if 'nation_id' in update_data:
            update_query['$set']['political.nation_id'] = update_data['nation_id']
        
        if not update_query['$set']:
            return None
        
        return self.update_one({'_id': star_id}, update_query)
    
    def clear_cache(self):
        """Clear all cached data"""
        super().clear_cache()
        self._filtered_cache.clear()
        self._search_cache.clear()
    
    def get_cache_stats(self):
        """Get cache statistics"""
        base_stats = super().get_cache_stats()
        base_stats.update({
            'filtered_cache_entries': len(self._filtered_cache),
            'search_cache_entries': len(self._search_cache)
        })
        return base_stats