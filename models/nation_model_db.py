"""
Nation model using MontyDB
"""

from .base_model_db import BaseModelDB


class NationModelDB(BaseModelDB):
    """MontyDB-based nation model"""
    
    def __init__(self):
        super().__init__('nations')
    
    def _initialize_collection(self):
        """Initialize nation collection with indexes"""
        try:
            self.create_index([("name", 1)])
            self.create_index([("capital.star_id", 1)])
            self.create_index([("government.type", 1)])
        except Exception as e:
            print(f"Warning: Could not create nation indexes: {e}")
    
    def get_all_nations(self):
        """Get all nations with formatted data"""
        nations = self.get_all(sort=[('name', 1)])
        return self._format_nations_for_json(nations)
    
    def get_nation_details(self, nation_id):
        """Get detailed information for a specific nation"""
        nation = self.get_by_id(nation_id)
        if not nation:
            return None
        
        # Get controlled stars
        stars_collection = self.collection.database.stars
        controlled_stars = list(stars_collection.find(
            {'political.nation_id': nation_id},
            {'_id': 1, 'names.primary_name': 1, 'coordinates': 1, 'political.strategic_importance': 1}
        ))
        
        # Get trade routes
        trade_routes_collection = self.collection.database.trade_routes
        trade_routes = list(trade_routes_collection.find(
            {'control.controlling_nation': nation_id},
            {'_id': 1, 'name': 1, 'route_type': 1, 'endpoints': 1}
        ))
        
        # Calculate territory statistics
        territory_stats = self._calculate_territory_stats(controlled_stars)
        
        return {
            'id': nation['_id'],
            'name': nation['name'],
            'full_name': nation['full_name'],
            'government': nation['government'],
            'capital': nation['capital'],
            'territories': nation.get('territories', []),
            'appearance': nation['appearance'],
            'economy': nation['economy'],
            'military': nation['military'],
            'description': nation['description'],
            'controlled_stars': self._format_controlled_stars(controlled_stars),
            'trade_routes': self._format_trade_routes(trade_routes),
            'statistics': territory_stats,
            'metadata': nation.get('metadata', {})
        }
    
    def get_nation_territories(self, nation_id):
        """Get all star systems controlled by a nation"""
        stars_collection = self.collection.database.stars
        
        territories = list(stars_collection.find(
            {'political.nation_id': nation_id},
            {
                '_id': 1,
                'names.primary_name': 1,
                'coordinates': 1,
                'physical_properties.magnitude': 1,
                'political.strategic_importance': 1,
                'political.capital_of': 1
            }
        ))
        
        return self._format_territories(territories)
    
    def get_nation_trade_routes(self, nation_id):
        """Get all trade routes controlled by a nation"""
        trade_routes_collection = self.collection.database.trade_routes
        
        routes = list(trade_routes_collection.find(
            {'control.controlling_nation': nation_id},
            sort=[('route_type', 1), ('name', 1)]
        ))
        
        return self._format_trade_routes(routes)
    
    def get_nation_by_capital(self, capital_star_id):
        """Get nation by its capital star ID"""
        nation = self.find_one({'capital.star_id': capital_star_id})
        return self._format_nation_for_json(nation) if nation else None
    
    def get_nations_by_government_type(self, government_type):
        """Get nations by government type"""
        nations = self.find({'government.type': government_type})
        return self._format_nations_for_json(nations)
    
    def search_nations(self, query):
        """Search nations by name or description"""
        search_conditions = [
            {'name': {'$regex': query, '$options': 'i'}},
            {'full_name': {'$regex': query, '$options': 'i'}},
            {'description': {'$regex': query, '$options': 'i'}}
        ]
        
        nations = self.find({'$or': search_conditions})
        return self._format_nations_for_json(nations)
    
    def get_nation_statistics(self):
        """Get statistics about all nations"""
        # Government type distribution
        gov_pipeline = [
            {'$group': {
                '_id': '$government.type',
                'count': {'$sum': 1},
                'nations': {'$push': '$name'}
            }},
            {'$sort': {'count': -1}}
        ]
        gov_distribution = self.aggregate(gov_pipeline)
        
        # Territory control statistics
        stars_collection = self.collection.database.stars
        territory_pipeline = [
            {'$match': {'political.nation_id': {'$ne': None}}},
            {'$group': {
                '_id': '$political.nation_id',
                'controlled_systems': {'$sum': 1},
                'capital_systems': {
                    '$sum': {
                        '$cond': [
                            {'$eq': ['$political.strategic_importance', 'capital']},
                            1, 0
                        ]
                    }
                }
            }},
            {'$sort': {'controlled_systems': -1}}
        ]
        territory_stats = list(stars_collection.aggregate(territory_pipeline))
        
        # Trade route control
        trade_routes_collection = self.collection.database.trade_routes
        trade_pipeline = [
            {'$group': {
                '_id': '$control.controlling_nation',
                'routes_controlled': {'$sum': 1},
                'route_types': {'$addToSet': '$route_type'}
            }},
            {'$sort': {'routes_controlled': -1}}
        ]
        trade_stats = list(trade_routes_collection.aggregate(trade_pipeline))
        
        return {
            'total_nations': self.count_documents(),
            'government_distribution': gov_distribution,
            'territory_control': territory_stats,
            'trade_route_control': trade_stats,
            'established_years': self._get_establishment_timeline()
        }
    
    def add_nation(self, nation_data):
        """Add a new nation to the database"""
        from database.schema import NationSchema
        
        # Validate nation data
        required_fields = ['name', 'government_type', 'capital_system', 'capital_star_id']
        for field in required_fields:
            if field not in nation_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Generate nation ID
        nation_id = nation_data['name'].lower().replace(' ', '_').replace('-', '_')
        
        # Create document
        nation_doc = NationSchema.create_document(nation_id, nation_data)
        
        # Insert into database
        result = self.insert_one(nation_doc)
        return result.inserted_id
    
    def update_nation(self, nation_id, update_data):
        """Update an existing nation"""
        # Build update query
        update_query = {'$set': {}}
        
        # Update allowed fields
        allowed_updates = {
            'description': 'description',
            'economic_focus': 'economy.focus',
            'military_strength': 'military.strength',
            'population': 'economy.population',
            'diplomatic_stance': 'government.diplomatic_stance'
        }
        
        for field, path in allowed_updates.items():
            if field in update_data:
                update_query['$set'][path] = update_data[field]
        
        if not update_query['$set']:
            return None
        
        return self.update_one({'_id': nation_id}, update_query)
    
    def add_territory(self, nation_id, star_id):
        """Add a star system to a nation's territory"""
        # Update nation's territories list
        self.update_one(
            {'_id': nation_id},
            {'$addToSet': {'territories': star_id}}
        )
        
        # Update star's political data
        stars_collection = self.collection.database.stars
        stars_collection.update_one(
            {'_id': star_id},
            {'$set': {
                'political.nation_id': nation_id,
                'political.controlled_by': nation_id,
                'political.strategic_importance': 'territory'
            }}
        )
    
    def remove_territory(self, nation_id, star_id):
        """Remove a star system from a nation's territory"""
        # Update nation's territories list
        self.update_one(
            {'_id': nation_id},
            {'$pull': {'territories': star_id}}
        )
        
        # Update star's political data
        stars_collection = self.collection.database.stars
        stars_collection.update_one(
            {'_id': star_id},
            {'$set': {
                'political.nation_id': None,
                'political.controlled_by': None,
                'political.strategic_importance': 'normal'
            }}
        )
    
    def _format_nations_for_json(self, nations):
        """Format nations for JSON response"""
        formatted_nations = []
        
        for nation in nations:
            formatted_nation = self._format_nation_for_json(nation)
            formatted_nations.append(formatted_nation)
        
        return formatted_nations
    
    def _format_nation_for_json(self, nation):
        """Format single nation for JSON response"""
        if not nation:
            return None
        
        return {
            'id': nation['_id'],
            'name': nation['name'],
            'full_name': nation['full_name'],
            'government_type': nation['government']['type'],
            'established_year': nation['government']['established_year'],
            'capital_system': nation['capital']['system'],
            'capital_star_id': nation['capital']['star_id'],
            'capital_planet': nation['capital']['planet'],
            'color': nation['appearance']['color'],
            'border_color': nation['appearance']['border_color'],
            'territories': nation.get('territories', []),
            'specialties': nation['economy'].get('specialties', []),
            'population': nation['economy'].get('population'),
            'economic_focus': nation['economy'].get('focus'),
            'military_strength': nation['military'].get('strength'),
            'political_alignment': nation['government'].get('political_alignment'),
            'diplomatic_stance': nation['government'].get('diplomatic_stance'),
            'description': nation['description']
        }
    
    def _format_controlled_stars(self, stars):
        """Format controlled stars data"""
        formatted_stars = []
        
        for star in stars:
            formatted_star = {
                'id': star['_id'],
                'name': star['names']['primary_name'],
                'coordinates': star['coordinates'],
                'strategic_importance': star['political']['strategic_importance'],
                'is_capital': star['political'].get('capital_of') is not None
            }
            formatted_stars.append(formatted_star)
        
        return formatted_stars
    
    def _format_trade_routes(self, routes):
        """Format trade routes data"""
        formatted_routes = []
        
        for route in routes:
            formatted_route = {
                'id': route['_id'],
                'name': route['name'],
                'route_type': route['route_type'],
                'from_system': route['endpoints']['from']['system'],
                'to_system': route['endpoints']['to']['system'],
                'security_level': route['control']['security_level'],
                'economic_zone': route['economics'].get('economic_zone')
            }
            formatted_routes.append(formatted_route)
        
        return formatted_routes
    
    def _format_territories(self, territories):
        """Format territory data"""
        formatted_territories = []
        
        for territory in territories:
            formatted_territory = {
                'star_id': territory['_id'],
                'name': territory['names']['primary_name'],
                'coordinates': territory['coordinates'],
                'magnitude': territory['physical_properties']['magnitude'],
                'strategic_importance': territory['political']['strategic_importance'],
                'is_capital': territory['political'].get('capital_of') is not None
            }
            formatted_territories.append(formatted_territory)
        
        return formatted_territories
    
    def _calculate_territory_stats(self, controlled_stars):
        """Calculate territory statistics"""
        total_systems = len(controlled_stars)
        capital_systems = sum(1 for star in controlled_stars 
                            if star['political']['strategic_importance'] == 'capital')
        
        # Calculate territory spread
        if controlled_stars:
            x_coords = [star['coordinates']['x'] for star in controlled_stars]
            y_coords = [star['coordinates']['y'] for star in controlled_stars]
            z_coords = [star['coordinates']['z'] for star in controlled_stars]
            
            territory_span = {
                'x_range': [min(x_coords), max(x_coords)],
                'y_range': [min(y_coords), max(y_coords)],
                'z_range': [min(z_coords), max(z_coords)]
            }
        else:
            territory_span = {'x_range': [0, 0], 'y_range': [0, 0], 'z_range': [0, 0]}
        
        return {
            'total_systems': total_systems,
            'capital_systems': capital_systems,
            'territory_systems': total_systems - capital_systems,
            'territory_span': territory_span
        }
    
    def _get_establishment_timeline(self):
        """Get timeline of nation establishments"""
        nations = self.get_all(sort=[('government.established_year', 1)])
        
        timeline = []
        for nation in nations:
            timeline.append({
                'year': nation['government']['established_year'],
                'nation': nation['name'],
                'government_type': nation['government']['type']
            })
        
        return timeline