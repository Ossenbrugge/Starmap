"""
Trade Route CRUD Manager
Comprehensive functions for managing trade route data
"""

import sys
import os
import math
from typing import Dict, List, Optional, Union
from datetime import datetime

# Add database path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
from config import get_collection
from schema import TradeRouteSchema

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.trade_route_model_db import TradeRouteModelDB


class TradeRouteManager:
    """Comprehensive trade route data management"""
    
    def __init__(self):
        self.trade_route_model = TradeRouteModelDB()
        self.trade_routes_collection = get_collection('trade_routes')
        self.stars_collection = get_collection('stars')
        self.nations_collection = get_collection('nations')
    
    # CREATE Operations
    def add_trade_route(self, route_data: Dict) -> str:
        """Add a new trade route to the database"""
        try:
            # Validate required fields
            required_fields = ['name', 'from_star_id', 'to_star_id', 'route_type']
            for field in required_fields:
                if field not in route_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate route ID from name if not provided
            if 'route_id' not in route_data:
                route_id = route_data['name'].lower().replace(' ', '_').replace('-', '_')
            else:
                route_id = route_data['route_id']
            
            # Check if route ID already exists
            if self.trade_routes_collection.find_one({'_id': route_id}):
                raise ValueError(f"Trade route with ID {route_id} already exists")
            
            # Validate endpoints exist
            from_star = self.stars_collection.find_one({'_id': route_data['from_star_id']})
            to_star = self.stars_collection.find_one({'_id': route_data['to_star_id']})
            
            if not from_star:
                raise ValueError(f"From star {route_data['from_star_id']} does not exist")
            if not to_star:
                raise ValueError(f"To star {route_data['to_star_id']} does not exist")
            
            # Auto-populate system names if not provided
            if 'from_system' not in route_data:
                route_data['from_system'] = from_star['names']['primary_name']
            if 'to_system' not in route_data:
                route_data['to_system'] = to_star['names']['primary_name']
            
            # Set defaults
            route_data.setdefault('established', 2300)
            route_data.setdefault('frequency', 'Weekly')
            route_data.setdefault('security_level', 'Standard')
            route_data.setdefault('cargo_types', ['General Cargo'])
            route_data.setdefault('description', f"Trade route connecting {route_data['from_system']} and {route_data['to_system']}")
            
            # Calculate travel time if not provided
            if 'travel_time_days' not in route_data:
                route_data['travel_time_days'] = self._calculate_travel_time(from_star, to_star)
            
            # Create document using schema
            route_doc = TradeRouteSchema.create_document(route_data)
            route_doc['_id'] = route_id  # Override the generated ID
            
            # Insert into database
            result = self.trade_routes_collection.insert_one(route_doc)
            
            return route_id
            
        except Exception as e:
            raise Exception(f"Failed to add trade route: {str(e)}")
    
    def add_trade_route_batch(self, routes_data: List[Dict]) -> List[str]:
        """Add multiple trade routes in batch"""
        added_routes = []
        errors = []
        
        for i, route_data in enumerate(routes_data):
            try:
                route_id = self.add_trade_route(route_data)
                added_routes.append(route_id)
            except Exception as e:
                errors.append(f"Route {i}: {str(e)}")
        
        if errors:
            print(f"Batch add completed with {len(errors)} errors:")
            for error in errors:
                print(f"  - {error}")
        
        return added_routes
    
    def create_mining_route(self,
                           route_name: str,
                           mining_star_id: int,
                           processing_star_id: int,
                           controlling_nation: str,
                           ore_types: List[str] = None) -> str:
        """Create a specialized mining route"""
        
        if ore_types is None:
            ore_types = ['Raw Materials', 'Processed Metals']
        
        # Get star information
        mining_star = self.stars_collection.find_one({'_id': mining_star_id})
        processing_star = self.stars_collection.find_one({'_id': processing_star_id})
        
        if not mining_star or not processing_star:
            raise ValueError("Both mining and processing stars must exist")
        
        route_data = {
            'name': route_name,
            'from_star_id': mining_star_id,
            'to_star_id': processing_star_id,
            'from_system': mining_star['names']['primary_name'],
            'to_system': processing_star['names']['primary_name'],
            'route_type': 'Mining',
            'controlling_nation': controlling_nation,
            'cargo_types': ore_types + ['Mining Equipment'],
            'frequency': 'Bi-weekly',
            'security_level': 'High',
            'description': f"Mining route transporting {', '.join(ore_types)} from {mining_star['names']['primary_name']} to {processing_star['names']['primary_name']}"
        }
        
        return self.add_trade_route(route_data)
    
    def create_passenger_route(self,
                              route_name: str,
                              departure_star_id: int,
                              destination_star_id: int,
                              controlling_nation: str,
                              service_class: str = 'Standard') -> str:
        """Create a passenger transport route"""
        
        # Get star information
        departure_star = self.stars_collection.find_one({'_id': departure_star_id})
        destination_star = self.stars_collection.find_one({'_id': destination_star_id})
        
        if not departure_star or not destination_star:
            raise ValueError("Both departure and destination stars must exist")
        
        route_data = {
            'name': route_name,
            'from_star_id': departure_star_id,
            'to_star_id': destination_star_id,
            'from_system': departure_star['names']['primary_name'],
            'to_system': destination_star['names']['primary_name'],
            'route_type': 'Passenger',
            'controlling_nation': controlling_nation,
            'cargo_types': ['Passengers', 'Personal Effects', 'Mail'],
            'frequency': 'Daily',
            'security_level': 'Maximum',
            'description': f"{service_class} passenger service between {departure_star['names']['primary_name']} and {destination_star['names']['primary_name']}"
        }
        
        return self.add_trade_route(route_data)
    
    # READ Operations
    def get_trade_route(self, route_id: str) -> Optional[Dict]:
        """Get a specific trade route by ID"""
        return self.trade_route_model.get_route_details(route_id)
    
    def list_trade_routes(self,
                         route_type: str = None,
                         controlling_nation: str = None,
                         security_level: str = None,
                         economic_zone: str = None,
                         connects_star: int = None) -> List[Dict]:
        """List trade routes with optional filters"""
        
        query = {}
        
        if route_type:
            query['route_type'] = route_type
        
        if controlling_nation:
            query['control.controlling_nation'] = controlling_nation
        
        if security_level:
            query['control.security_level'] = security_level
        
        if economic_zone:
            query['economics.economic_zone'] = economic_zone
        
        if connects_star:
            query['$or'] = [
                {'endpoints.from.star_id': connects_star},
                {'endpoints.to.star_id': connects_star}
            ]
        
        routes = list(self.trade_routes_collection.find(query).sort('name', 1))
        return [self._format_route_summary(route) for route in routes]
    
    def search_trade_routes(self, query: str) -> List[Dict]:
        """Search trade routes by name, description, or system names"""
        return self.trade_route_model.search_routes(query)
    
    def get_routes_by_star(self, star_id: int) -> List[Dict]:
        """Get all trade routes that connect to a specific star"""
        return self.trade_route_model.get_routes_by_star(star_id)
    
    def get_routes_by_nation(self, nation_id: str) -> List[Dict]:
        """Get all trade routes controlled by a specific nation"""
        return self.trade_route_model.get_routes_by_nation(nation_id)
    
    def find_route_between_stars(self, star1_id: int, star2_id: int) -> List[Dict]:
        """Find direct routes between two stars"""
        query = {
            '$or': [
                {
                    'endpoints.from.star_id': star1_id,
                    'endpoints.to.star_id': star2_id
                },
                {
                    'endpoints.from.star_id': star2_id,
                    'endpoints.to.star_id': star1_id
                }
            ]
        }
        
        routes = list(self.trade_routes_collection.find(query))
        return [self._format_route_summary(route) for route in routes]
    
    def get_trade_network_analysis(self) -> Dict:
        """Get comprehensive trade network analysis"""
        return self.trade_route_model.get_trade_network_analysis()
    
    # UPDATE Operations
    def update_trade_route(self, route_id: str, update_data: Dict) -> bool:
        """Update trade route information"""
        try:
            # Build update query
            update_query = {'$set': {}}
            
            # Map update fields to database structure
            field_mapping = {
                'description': 'description',
                'security_level': 'control.security_level',
                'frequency': 'logistics.frequency',
                'cargo_types': 'logistics.cargo_types',
                'travel_time_days': 'logistics.travel_time_days',
                'controlling_nation': 'control.controlling_nation',
                'economic_zone': 'economics.economic_zone'
            }
            
            for field, db_field in field_mapping.items():
                if field in update_data:
                    update_query['$set'][db_field] = update_data[field]
            
            # Add update timestamp
            update_query['$set']['metadata.updated_at'] = datetime.utcnow()
            
            if not update_query['$set']:
                return False
            
            # Execute update
            result = self.trade_routes_collection.update_one(
                {'_id': route_id}, 
                update_query
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Failed to update trade route {route_id}: {str(e)}")
    
    def change_route_control(self, route_id: str, new_controlling_nation: str) -> bool:
        """Change which nation controls a trade route"""
        try:
            # Validate new controlling nation exists
            if not self.nations_collection.find_one({'_id': new_controlling_nation}):
                raise ValueError(f"Nation {new_controlling_nation} not found")
            
            result = self.trade_routes_collection.update_one(
                {'_id': route_id},
                {'$set': {
                    'control.controlling_nation': new_controlling_nation,
                    'metadata.updated_at': datetime.utcnow()
                }}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Failed to change control of route {route_id}: {str(e)}")
    
    def update_route_endpoints(self, route_id: str, new_from_star: int = None, new_to_star: int = None) -> bool:
        """Update trade route endpoints"""
        try:
            route = self.trade_routes_collection.find_one({'_id': route_id})
            if not route:
                raise ValueError(f"Route {route_id} not found")
            
            update_data = {}
            
            if new_from_star:
                from_star = self.stars_collection.find_one({'_id': new_from_star})
                if not from_star:
                    raise ValueError(f"From star {new_from_star} not found")
                
                update_data['endpoints.from.star_id'] = new_from_star
                update_data['endpoints.from.system'] = from_star['names']['primary_name']
                
                # Recalculate travel time
                to_star = self.stars_collection.find_one({'_id': route['endpoints']['to']['star_id']})
                if to_star:
                    update_data['logistics.travel_time_days'] = self._calculate_travel_time(from_star, to_star)
            
            if new_to_star:
                to_star = self.stars_collection.find_one({'_id': new_to_star})
                if not to_star:
                    raise ValueError(f"To star {new_to_star} not found")
                
                update_data['endpoints.to.star_id'] = new_to_star
                update_data['endpoints.to.system'] = to_star['names']['primary_name']
                
                # Recalculate travel time if from_star wasn't changed
                if not new_from_star:
                    from_star = self.stars_collection.find_one({'_id': route['endpoints']['from']['star_id']})
                    if from_star:
                        update_data['logistics.travel_time_days'] = self._calculate_travel_time(from_star, to_star)
            
            if not update_data:
                return False
            
            update_data['metadata.updated_at'] = datetime.utcnow()
            
            result = self.trade_routes_collection.update_one(
                {'_id': route_id},
                {'$set': update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Failed to update route endpoints for {route_id}: {str(e)}")
    
    # DELETE Operations
    def delete_trade_route(self, route_id: str) -> bool:
        """Delete a trade route from the database"""
        try:
            result = self.trade_routes_collection.delete_one({'_id': route_id})
            return result.deleted_count > 0
            
        except Exception as e:
            raise Exception(f"Failed to delete trade route {route_id}: {str(e)}")
    
    def delete_routes_by_nation(self, nation_id: str) -> int:
        """Delete all trade routes controlled by a specific nation"""
        try:
            result = self.trade_routes_collection.delete_many({
                'control.controlling_nation': nation_id
            })
            return result.deleted_count
            
        except Exception as e:
            raise Exception(f"Failed to delete routes for nation {nation_id}: {str(e)}")
    
    def delete_routes_by_star(self, star_id: int) -> int:
        """Delete all trade routes connected to a specific star"""
        try:
            result = self.trade_routes_collection.delete_many({
                '$or': [
                    {'endpoints.from.star_id': star_id},
                    {'endpoints.to.star_id': star_id}
                ]
            })
            return result.deleted_count
            
        except Exception as e:
            raise Exception(f"Failed to delete routes for star {star_id}: {str(e)}")
    
    def remove_all_felgenland_routes(self) -> int:
        """Remove all Felgenland Saga trade routes"""
        try:
            # Define Felgenland Saga nations
            felgenland_nations = [
                'terran_directorate',
                'felgenland_union', 
                'protelani_republic',
                'dorsai_republic',
                'pentothian_trade_conglomerate'
            ]
            
            deleted_count = 0
            for nation in felgenland_nations:
                count = self.delete_routes_by_nation(nation)
                deleted_count += count
            
            return deleted_count
            
        except Exception as e:
            raise Exception(f"Failed to remove Felgenland routes: {str(e)}")
    
    # ANALYSIS Functions
    def analyze_trade_network(self) -> Dict:
        """Analyze the trade network structure and efficiency"""
        try:
            # Get all routes
            all_routes = list(self.trade_routes_collection.find())
            
            # Build network graph
            nodes = set()
            edges = []
            route_types = {}
            nation_routes = {}
            
            for route in all_routes:
                from_star = route['endpoints']['from']['star_id']
                to_star = route['endpoints']['to']['star_id']
                
                nodes.add(from_star)
                nodes.add(to_star)
                edges.append((from_star, to_star))
                
                # Track route types
                route_type = route['route_type']
                route_types[route_type] = route_types.get(route_type, 0) + 1
                
                # Track nation control
                nation = route['control'].get('controlling_nation')
                if nation:
                    nation_routes[nation] = nation_routes.get(nation, 0) + 1
            
            # Calculate network metrics
            total_nodes = len(nodes)
            total_edges = len(edges)
            
            # Node connectivity
            node_connections = {}
            for node in nodes:
                connections = sum(1 for edge in edges if node in edge)
                node_connections[node] = connections
            
            # Find hub systems (high connectivity)
            hub_systems = sorted(node_connections.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Calculate network density
            max_possible_edges = total_nodes * (total_nodes - 1) / 2
            network_density = total_edges / max_possible_edges if max_possible_edges > 0 else 0
            
            # Find isolated components
            isolated_nodes = [node for node, connections in node_connections.items() if connections == 0]
            
            return {
                'summary': {
                    'total_systems': total_nodes,
                    'total_routes': total_edges,
                    'network_density': round(network_density, 4),
                    'isolated_systems': len(isolated_nodes)
                },
                'route_type_distribution': route_types,
                'nation_control': nation_routes,
                'hub_systems': [
                    {
                        'star_id': star_id,
                        'connections': connections,
                        'star_name': self._get_star_name(star_id)
                    }
                    for star_id, connections in hub_systems
                ],
                'isolated_systems': [
                    {
                        'star_id': star_id,
                        'star_name': self._get_star_name(star_id)
                    }
                    for star_id in isolated_nodes
                ],
                'efficiency_metrics': self._calculate_efficiency_metrics(all_routes)
            }
            
        except Exception as e:
            raise Exception(f"Failed to analyze trade network: {str(e)}")
    
    def find_shortest_trade_path(self, from_star_id: int, to_star_id: int, max_hops: int = 5) -> List[Dict]:
        """Find the shortest trade path between two stars"""
        try:
            # Build adjacency list
            graph = {}
            route_map = {}
            
            for route in self.trade_routes_collection.find():
                from_id = route['endpoints']['from']['star_id']
                to_id = route['endpoints']['to']['star_id']
                
                # Build bidirectional graph
                if from_id not in graph:
                    graph[from_id] = []
                if to_id not in graph:
                    graph[to_id] = []
                
                graph[from_id].append(to_id)
                graph[to_id].append(from_id)
                
                # Store route information
                route_map[(from_id, to_id)] = route
                route_map[(to_id, from_id)] = route
            
            # BFS to find shortest path
            from collections import deque
            
            queue = deque([(from_star_id, [from_star_id])])
            visited = {from_star_id}
            
            while queue:
                current_star, path = queue.popleft()
                
                if len(path) > max_hops + 1:  # +1 because path includes start
                    continue
                
                if current_star == to_star_id:
                    # Build route information for the path
                    path_routes = []
                    for i in range(len(path) - 1):
                        route_key = (path[i], path[i + 1])
                        if route_key in route_map:
                            route = route_map[route_key]
                            path_routes.append({
                                'route_id': route['_id'],
                                'route_name': route['name'],
                                'from_star': path[i],
                                'to_star': path[i + 1],
                                'from_system': route['endpoints']['from']['system'],
                                'to_system': route['endpoints']['to']['system'],
                                'travel_time_days': route['logistics'].get('travel_time_days', 7)
                            })
                    
                    total_travel_time = sum(r['travel_time_days'] for r in path_routes)
                    
                    return {
                        'path_found': True,
                        'total_hops': len(path) - 1,
                        'total_travel_time_days': total_travel_time,
                        'path': path,
                        'routes': path_routes
                    }
                
                if current_star in graph:
                    for neighbor in graph[current_star]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, path + [neighbor]))
            
            return {
                'path_found': False,
                'message': f"No trade path found between {from_star_id} and {to_star_id} within {max_hops} hops"
            }
            
        except Exception as e:
            raise Exception(f"Failed to find trade path: {str(e)}")
    
    # UTILITY Functions
    def validate_trade_route_data(self, route_data: Dict) -> List[str]:
        """Validate trade route data and return list of errors"""
        errors = []
        
        # Check required fields
        required_fields = ['name', 'from_star_id', 'to_star_id', 'route_type']
        for field in required_fields:
            if field not in route_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate data types
        if 'from_star_id' in route_data and not isinstance(route_data['from_star_id'], int):
            errors.append("From star ID must be an integer")
        
        if 'to_star_id' in route_data and not isinstance(route_data['to_star_id'], int):
            errors.append("To star ID must be an integer")
        
        if 'travel_time_days' in route_data:
            if not isinstance(route_data['travel_time_days'], (int, float)) or route_data['travel_time_days'] <= 0:
                errors.append("Travel time must be a positive number")
        
        if 'established' in route_data:
            if not isinstance(route_data['established'], int) or route_data['established'] < 2000:
                errors.append("Established year must be an integer >= 2000")
        
        # Check for self-loops
        if 'from_star_id' in route_data and 'to_star_id' in route_data:
            if route_data['from_star_id'] == route_data['to_star_id']:
                errors.append("From and to stars cannot be the same")
        
        # Validate cargo types
        if 'cargo_types' in route_data:
            if not isinstance(route_data['cargo_types'], list):
                errors.append("Cargo types must be a list")
            elif not all(isinstance(ct, str) for ct in route_data['cargo_types']):
                errors.append("All cargo types must be strings")
        
        return errors
    
    def get_trade_route_statistics(self) -> Dict:
        """Get comprehensive trade route statistics"""
        return self.trade_route_model.get_route_statistics()
    
    def import_from_json(self, json_file_path: str) -> int:
        """Import trade routes from JSON file"""
        import json
        
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            
            routes_data = []
            
            # Handle different JSON structures
            if 'trade_routes' in data:
                for category, routes in data['trade_routes'].items():
                    if isinstance(routes, list):
                        routes_data.extend(routes)
            elif isinstance(data, list):
                routes_data = data
            else:
                routes_data = [data]
            
            added_routes = self.add_trade_route_batch(routes_data)
            return len(added_routes)
            
        except Exception as e:
            raise Exception(f"Failed to import from JSON: {str(e)}")
    
    # Private helper methods
    def _calculate_travel_time(self, from_star: Dict, to_star: Dict) -> int:
        """Calculate travel time between two stars"""
        try:
            from_coords = from_star['coordinates']
            to_coords = to_star['coordinates']
            
            distance = math.sqrt(
                (to_coords['x'] - from_coords['x']) ** 2 +
                (to_coords['y'] - from_coords['y']) ** 2 +
                (to_coords['z'] - from_coords['z']) ** 2
            )
            
            # Assume 1 parsec per day travel speed (can be adjusted)
            travel_days = max(1, int(distance))
            
            return travel_days
            
        except Exception:
            return 7  # Default 1 week
    
    def _format_route_summary(self, route_doc: Dict) -> Dict:
        """Format route document for summary display"""
        return {
            'id': route_doc['_id'],
            'name': route_doc['name'],
            'route_type': route_doc['route_type'],
            'from_star_id': route_doc['endpoints']['from']['star_id'],
            'to_star_id': route_doc['endpoints']['to']['star_id'],
            'from_system': route_doc['endpoints']['from']['system'],
            'to_system': route_doc['endpoints']['to']['system'],
            'controlling_nation': route_doc['control'].get('controlling_nation'),
            'security_level': route_doc['control'].get('security_level'),
            'frequency': route_doc['logistics'].get('frequency'),
            'travel_time_days': route_doc['logistics'].get('travel_time_days'),
            'cargo_types': route_doc['logistics'].get('cargo_types', []),
            'economic_zone': route_doc['economics'].get('economic_zone'),
            'established': route_doc['established'],
            'description': route_doc['description']
        }
    
    def _get_star_name(self, star_id: int) -> str:
        """Get star name by ID"""
        star = self.stars_collection.find_one({'_id': star_id}, {'names.primary_name': 1})
        return star['names']['primary_name'] if star else f"Star {star_id}"
    
    def _calculate_efficiency_metrics(self, routes: List[Dict]) -> Dict:
        """Calculate trade network efficiency metrics"""
        if not routes:
            return {}
        
        # Average travel time
        travel_times = [r['logistics'].get('travel_time_days', 7) for r in routes]
        avg_travel_time = sum(travel_times) / len(travel_times)
        
        # Security distribution
        security_levels = [r['control'].get('security_level', 'Standard') for r in routes]
        security_dist = {}
        for level in security_levels:
            security_dist[level] = security_dist.get(level, 0) + 1
        
        # Frequency distribution
        frequencies = [r['logistics'].get('frequency', 'Weekly') for r in routes]
        frequency_dist = {}
        for freq in frequencies:
            frequency_dist[freq] = frequency_dist.get(freq, 0) + 1
        
        return {
            'average_travel_time_days': round(avg_travel_time, 2),
            'security_level_distribution': security_dist,
            'frequency_distribution': frequency_dist,
            'total_routes': len(routes)
        }