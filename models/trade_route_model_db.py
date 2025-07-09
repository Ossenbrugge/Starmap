"""
Trade route model using MontyDB
"""

from .base_model_db import BaseModelDB


class TradeRouteModelDB(BaseModelDB):
    """MontyDB-based trade route model"""
    
    def __init__(self):
        super().__init__('trade_routes')
    
    def _initialize_collection(self):
        """Initialize trade route collection with indexes"""
        try:
            self.create_index([("endpoints.from.star_id", 1)])
            self.create_index([("endpoints.to.star_id", 1)])
            self.create_index([("control.controlling_nation", 1)])
            self.create_index([("route_type", 1)])
            self.create_index([("economics.economic_zone", 1)])
        except Exception as e:
            print(f"Warning: Could not create trade route indexes: {e}")
    
    def get_all_trade_routes(self):
        """Get all trade routes with formatted data"""
        routes = self.get_all(sort=[('route_type', 1), ('name', 1)])
        return self._format_routes_for_json(routes)
    
    def get_routes_by_type(self, route_type):
        """Get trade routes by type"""
        routes = self.find({'route_type': route_type}, sort=[('name', 1)])
        return self._format_routes_for_json(routes)
    
    def get_routes_by_nation(self, nation_id):
        """Get trade routes controlled by a specific nation"""
        routes = self.find({'control.controlling_nation': nation_id}, sort=[('route_type', 1)])
        return self._format_routes_for_json(routes)
    
    def get_routes_by_star(self, star_id):
        """Get all trade routes that connect to a specific star"""
        query = {
            '$or': [
                {'endpoints.from.star_id': star_id},
                {'endpoints.to.star_id': star_id}
            ]
        }
        routes = self.find(query, sort=[('route_type', 1)])
        return self._format_routes_for_json(routes)
    
    def get_routes_by_economic_zone(self, economic_zone):
        """Get trade routes by economic zone"""
        routes = self.find({'economics.economic_zone': economic_zone}, sort=[('name', 1)])
        return self._format_routes_for_json(routes)
    
    def get_route_details(self, route_id):
        """Get detailed information for a specific trade route"""
        route = self.get_by_id(route_id)
        if not route:
            return None
        
        # Get star information for endpoints
        stars_collection = self.collection.database.stars
        from_star = stars_collection.find_one({'_id': route['endpoints']['from']['star_id']})
        to_star = stars_collection.find_one({'_id': route['endpoints']['to']['star_id']})
        
        # Get nation information
        nation_data = None
        if route['control'].get('controlling_nation'):
            nations_collection = self.collection.database.nations
            nation = nations_collection.find_one({'_id': route['control']['controlling_nation']})
            if nation:
                nation_data = {
                    'id': nation['_id'],
                    'name': nation['name'],
                    'color': nation['appearance']['color']
                }
        
        # Calculate route distance
        route_distance = self._calculate_route_distance(from_star, to_star)
        
        return {
            'id': route['_id'],
            'name': route['name'],
            'route_type': route['route_type'],
            'established': route['established'],
            'endpoints': {
                'from': {
                    'star_id': route['endpoints']['from']['star_id'],
                    'system': route['endpoints']['from']['system'],
                    'star_data': self._format_star_data(from_star) if from_star else None
                },
                'to': {
                    'star_id': route['endpoints']['to']['star_id'],
                    'system': route['endpoints']['to']['system'],
                    'star_data': self._format_star_data(to_star) if to_star else None
                }
            },
            'logistics': route['logistics'],
            'control': route['control'],
            'economics': route['economics'],
            'description': route['description'],
            'controlling_nation': nation_data,
            'route_distance': route_distance,
            'metadata': route.get('metadata', {})
        }
    
    def search_routes(self, query):
        """Search trade routes by name or description"""
        search_conditions = [
            {'name': {'$regex': query, '$options': 'i'}},
            {'description': {'$regex': query, '$options': 'i'}},
            {'endpoints.from.system': {'$regex': query, '$options': 'i'}},
            {'endpoints.to.system': {'$regex': query, '$options': 'i'}}
        ]
        
        routes = self.find({'$or': search_conditions})
        return self._format_routes_for_json(routes)
    
    def get_route_statistics(self):
        """Get statistics about trade routes"""
        # Route type distribution
        type_pipeline = [
            {'$group': {
                '_id': '$route_type',
                'count': {'$sum': 1},
                'routes': {'$push': '$name'}
            }},
            {'$sort': {'count': -1}}
        ]
        type_distribution = self.aggregate(type_pipeline)
        
        # Nation control distribution
        nation_pipeline = [
            {'$group': {
                '_id': '$control.controlling_nation',
                'routes_controlled': {'$sum': 1},
                'route_types': {'$addToSet': '$route_type'}
            }},
            {'$sort': {'routes_controlled': -1}}
        ]
        nation_control = self.aggregate(nation_pipeline)
        
        # Economic zone distribution
        zone_pipeline = [
            {'$group': {
                '_id': '$economics.economic_zone',
                'routes': {'$sum': 1},
                'nations': {'$addToSet': '$control.controlling_nation'}
            }},
            {'$sort': {'routes': -1}}
        ]
        zone_distribution = self.aggregate(zone_pipeline)
        
        # Security level distribution
        security_pipeline = [
            {'$group': {
                '_id': '$control.security_level',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        security_distribution = self.aggregate(security_pipeline)
        
        return {
            'total_routes': self.count_documents(),
            'type_distribution': type_distribution,
            'nation_control': nation_control,
            'economic_zone_distribution': zone_distribution,
            'security_distribution': security_distribution,
            'establishment_timeline': self._get_establishment_timeline()
        }
    
    def get_trade_network_analysis(self):
        """Analyze the trade network structure"""
        # Get all routes
        all_routes = self.get_all()
        
        # Build network graph
        network_nodes = set()
        network_edges = []
        
        for route in all_routes:
            from_star = route['endpoints']['from']['star_id']
            to_star = route['endpoints']['to']['star_id']
            
            network_nodes.add(from_star)
            network_nodes.add(to_star)
            
            network_edges.append({
                'from': from_star,
                'to': to_star,
                'route_id': route['_id'],
                'route_type': route['route_type'],
                'controlling_nation': route['control'].get('controlling_nation')
            })
        
        # Calculate network metrics
        node_connections = {}
        for node in network_nodes:
            connections = [edge for edge in network_edges if edge['from'] == node or edge['to'] == node]
            node_connections[node] = len(connections)
        
        # Find hub systems (high connectivity)
        hub_systems = sorted(node_connections.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_systems': len(network_nodes),
            'total_connections': len(network_edges),
            'hub_systems': hub_systems,
            'network_density': len(network_edges) / (len(network_nodes) * (len(network_nodes) - 1) / 2) if len(network_nodes) > 1 else 0,
            'nation_networks': self._analyze_nation_networks(network_edges)
        }
    
    def add_trade_route(self, route_data):
        """Add a new trade route to the database"""
        from database.schema import TradeRouteSchema
        
        # Validate route data
        required_fields = ['name', 'from_star_id', 'to_star_id', 'route_type']
        for field in required_fields:
            if field not in route_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create document
        route_doc = TradeRouteSchema.create_document(route_data)
        
        # Insert into database
        result = self.insert_one(route_doc)
        return result.inserted_id
    
    def update_trade_route(self, route_id, update_data):
        """Update an existing trade route"""
        # Build update query
        update_query = {'$set': {}}
        
        # Update allowed fields
        allowed_updates = {
            'description': 'description',
            'security_level': 'control.security_level',
            'frequency': 'logistics.frequency',
            'cargo_types': 'logistics.cargo_types',
            'travel_time_days': 'logistics.travel_time_days'
        }
        
        for field, path in allowed_updates.items():
            if field in update_data:
                update_query['$set'][path] = update_data[field]
        
        if not update_query['$set']:
            return None
        
        return self.update_one({'_id': route_id}, update_query)
    
    def _format_routes_for_json(self, routes):
        """Format routes for JSON response"""
        formatted_routes = []
        
        for route in routes:
            formatted_route = {
                'id': route['_id'],
                'name': route['name'],
                'route_type': route['route_type'],
                'established': route['established'],
                'from_star_id': route['endpoints']['from']['star_id'],
                'to_star_id': route['endpoints']['to']['star_id'],
                'from_system': route['endpoints']['from']['system'],
                'to_system': route['endpoints']['to']['system'],
                'cargo_types': route['logistics'].get('cargo_types', []),
                'travel_time_days': route['logistics'].get('travel_time_days', 0),
                'frequency': route['logistics'].get('frequency', 'Unknown'),
                'controlling_nation': route['control'].get('controlling_nation'),
                'security_level': route['control'].get('security_level', 'Standard'),
                'economic_zone': route['economics'].get('economic_zone'),
                'regions': route['economics'].get('regions', []),
                'description': route['description']
            }
            formatted_routes.append(formatted_route)
        
        return formatted_routes
    
    def _format_star_data(self, star):
        """Format star data for route endpoints"""
        if not star:
            return None
        
        return {
            'id': star['_id'],
            'name': star['names']['primary_name'],
            'coordinates': star['coordinates'],
            'magnitude': star['physical_properties']['magnitude'],
            'nation_id': star['political'].get('nation_id')
        }
    
    def _calculate_route_distance(self, from_star, to_star):
        """Calculate distance between route endpoints"""
        if not from_star or not to_star:
            return None
        
        from_coords = from_star['coordinates']
        to_coords = to_star['coordinates']
        
        import math
        distance_pc = math.sqrt(
            (to_coords['x'] - from_coords['x'])**2 +
            (to_coords['y'] - from_coords['y'])**2 +
            (to_coords['z'] - from_coords['z'])**2
        )
        
        return {
            'parsecs': round(distance_pc, 2),
            'light_years': round(distance_pc * 3.26156, 2)
        }
    
    def _analyze_nation_networks(self, network_edges):
        """Analyze trade networks by controlling nation"""
        nation_networks = {}
        
        for edge in network_edges:
            nation = edge['controlling_nation']
            if nation:
                if nation not in nation_networks:
                    nation_networks[nation] = {
                        'routes': 0,
                        'systems_connected': set(),
                        'route_types': set()
                    }
                
                nation_networks[nation]['routes'] += 1
                nation_networks[nation]['systems_connected'].add(edge['from'])
                nation_networks[nation]['systems_connected'].add(edge['to'])
                nation_networks[nation]['route_types'].add(edge['route_type'])
        
        # Convert sets to lists for JSON serialization
        for nation, data in nation_networks.items():
            data['systems_connected'] = len(data['systems_connected'])
            data['route_types'] = list(data['route_types'])
        
        return nation_networks
    
    def _get_establishment_timeline(self):
        """Get timeline of route establishments"""
        routes = self.get_all(sort=[('established', 1)])
        
        timeline = []
        for route in routes:
            timeline.append({
                'year': route['established'],
                'route': route['name'],
                'type': route['route_type'],
                'nation': route['control'].get('controlling_nation')
            })
        
        return timeline