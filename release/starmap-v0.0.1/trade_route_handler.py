"""
Trade Route Handler for managing fictional trade routes in the Starmap application.
Handles adding new fictional trade routes to the system.
"""

import json
import os
import math
from typing import Dict, Any, List, Optional
from datetime import datetime

class TradeRouteHandler:
    """Handles operations for fictional trade routes"""
    
    def __init__(self, data_path: str = 'data'):
        self.data_path = data_path
        self.trade_routes_file = f'{data_path}/trade_routes.json'
        self.stars_file = f'{data_path}/stars.json'
        self.nations_file = f'{data_path}/nations.json'
    
    def add_fictional_trade_route(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new fictional trade route to the system
        
        Args:
            route_data: Dictionary containing trade route information with required fields:
                - name: Route name
                - from_star_id: Origin star system ID
                - to_star_id: Destination star system ID
                - controlling_nation: Nation ID that controls the route
                - route_type: Type of trade route (e.g., 'Commercial', 'Military', 'Resource')
                And optional fields like cargo types, frequency, security level, etc.
        
        Returns:
            Dict containing success status and route data
        """
        try:
            # Validate required fields
            required_fields = ['name', 'from_star_id', 'to_star_id', 'controlling_nation', 'route_type']
            for field in required_fields:
                if field not in route_data:
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            # Validate star systems exist
            if not self._validate_star_system(route_data['from_star_id']):
                return {'success': False, 'error': f'Origin star system {route_data["from_star_id"]} not found'}
            
            if not self._validate_star_system(route_data['to_star_id']):
                return {'success': False, 'error': f'Destination star system {route_data["to_star_id"]} not found'}
            
            # Validate nation exists
            if not self._validate_nation(route_data['controlling_nation']):
                return {'success': False, 'error': f'Nation "{route_data["controlling_nation"]}" not found'}
            
            # Generate route ID
            route_id = self._generate_route_id(route_data['name'])
            
            # Get system information
            from_system_info = self._get_system_info(route_data['from_star_id'])
            to_system_info = self._get_system_info(route_data['to_star_id'])
            
            # Calculate route properties
            distance = self._calculate_distance(from_system_info, to_system_info)
            travel_time = self._calculate_travel_time(distance, route_data.get('ship_speed', 1.0))
            
            # Create trade route entry
            route_entry = self._create_route_entry(route_data, route_id, from_system_info, to_system_info, distance, travel_time)
            
            # Add to trade routes file
            self._add_to_trade_routes_file(route_entry)
            
            return {
                'success': True,
                'data': route_entry,
                'message': f'Fictional trade route "{route_data["name"]}" added successfully with ID {route_id}'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Error adding fictional trade route: {str(e)}'}
    
    def _validate_star_system(self, star_id: int) -> bool:
        """Validate that a star system exists"""
        # Check in stars.json
        if os.path.exists(self.stars_file):
            with open(self.stars_file, 'r') as f:
                stars = json.load(f)
                for star in stars:
                    if star.get('id') == star_id:
                        return True
        
        # Check in fictional_stars.csv
        fictional_stars_file = f'{self.data_path}/fictional_stars.csv'
        if os.path.exists(fictional_stars_file):
            import csv
            with open(fictional_stars_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        if int(row.get('id', 0)) == star_id:
                            return True
                    except ValueError:
                        continue
        
        return False
    
    def _validate_nation(self, nation_id: str) -> bool:
        """Validate that a nation exists"""
        if os.path.exists(self.nations_file):
            with open(self.nations_file, 'r') as f:
                nations = json.load(f)
                for nation in nations:
                    if nation.get('_id') == nation_id:
                        return True
        return False
    
    def _get_system_info(self, star_id: int) -> Dict[str, Any]:
        """Get system information for a star"""
        # Check stars.json first
        if os.path.exists(self.stars_file):
            with open(self.stars_file, 'r') as f:
                stars = json.load(f)
                for star in stars:
                    if star.get('id') == star_id:
                        return {
                            'star_id': star_id,
                            'system': star.get('proper', f'System-{star_id}'),
                            'x': star.get('x', 0.0),
                            'y': star.get('y', 0.0),
                            'z': star.get('z', 0.0)
                        }
        
        # Check fictional_stars.csv
        fictional_stars_file = f'{self.data_path}/fictional_stars.csv'
        if os.path.exists(fictional_stars_file):
            import csv
            with open(fictional_stars_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        if int(row.get('id', 0)) == star_id:
                            return {
                                'star_id': star_id,
                                'system': row.get('proper', f'System-{star_id}'),
                                'x': float(row.get('x', 0.0)),
                                'y': float(row.get('y', 0.0)),
                                'z': float(row.get('z', 0.0))
                            }
                    except (ValueError, TypeError):
                        continue
        
        # Return default if not found
        return {
            'star_id': star_id,
            'system': f'Unknown System {star_id}',
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    
    def _calculate_distance(self, from_system: Dict[str, Any], to_system: Dict[str, Any]) -> float:
        """Calculate 3D distance between two star systems in parsecs"""
        try:
            dx = to_system['x'] - from_system['x']
            dy = to_system['y'] - from_system['y']
            dz = to_system['z'] - from_system['z']
            return math.sqrt(dx*dx + dy*dy + dz*dz)
        except:
            return 10.0  # Default distance
    
    def _calculate_travel_time(self, distance: float, ship_speed: float = 1.0) -> int:
        """Calculate travel time in days based on distance and ship speed"""
        try:
            # Assume 1 parsec per day at standard speed
            base_speed = 1.0  # parsecs per day
            actual_speed = base_speed * ship_speed
            return max(1, int(distance / actual_speed))
        except:
            return 30  # Default 30 days
    
    def _generate_route_id(self, name: str) -> str:
        """Generate a unique ID for the trade route"""
        # Convert to lowercase and replace spaces with underscores
        import re
        base_id = name.lower().replace(' ', '_').replace('-', '_')
        base_id = re.sub(r'[^a-z0-9_]', '', base_id)
        
        # Check existing routes
        existing_routes = self._load_existing_routes()
        existing_ids = {route.get('_id') for route in existing_routes}
        
        # Find unique ID
        route_id = base_id
        counter = 1
        while route_id in existing_ids:
            route_id = f"{base_id}_{counter}"
            counter += 1
        
        return route_id
    
    def _create_route_entry(self, route_data: Dict[str, Any], route_id: str, 
                           from_system: Dict[str, Any], to_system: Dict[str, Any], 
                           distance: float, travel_time: int) -> Dict[str, Any]:
        """Create a complete trade route entry"""
        current_year = datetime.now().year
        
        # Determine economic zone based on controlling nation
        economic_zone = self._determine_economic_zone(route_data['controlling_nation'])
        
        entry = {
            '_id': route_id,
            'name': route_data['name'],
            'route_type': route_data['route_type'],
            'established': route_data.get('established_year', current_year),
            'endpoints': {
                'from': {
                    'star_id': from_system['star_id'],
                    'system': from_system['system']
                },
                'to': {
                    'star_id': to_system['star_id'],
                    'system': to_system['system']
                }
            },
            'logistics': {
                'cargo_types': route_data.get('cargo_types', ['General Goods']),
                'travel_time_days': travel_time,
                'frequency': route_data.get('frequency', 'Weekly'),
                'capacity': route_data.get('capacity', None),
                'cost_per_unit': route_data.get('cost_per_unit', None)
            },
            'control': {
                'controlling_nation': route_data['controlling_nation'],
                'security_level': route_data.get('security_level', 'Medium'),
                'patrol_frequency': route_data.get('patrol_frequency', None),
                'customs_checkpoints': route_data.get('customs_checkpoints', [])
            },
            'economics': {
                'economic_zone': economic_zone,
                'trade_volume': route_data.get('trade_volume', None),
                'revenue': route_data.get('revenue', None),
                'regions': route_data.get('regions', ['Unknown Region'])
            },
            'description': route_data.get('description', f'Trade route connecting {from_system["system"]} to {to_system["system"]}'),
            'category': route_data.get('category', 'fictional_routes'),
            
            # Calculated properties
            'distance_parsecs': round(distance, 2),
            'route_efficiency': route_data.get('efficiency_rating', 'Standard'),
            
            # Fictional-specific metadata
            'fictional_created': datetime.now().isoformat(),
            'fictional_creator': route_data.get('creator', 'Starmap System'),
            'fictional_danger_level': route_data.get('danger_level', 'Low'),
            'fictional_special_features': route_data.get('special_features', []),
            'fictional_historical_significance': route_data.get('historical_significance', ''),
            'fictional_trade_regulations': route_data.get('trade_regulations', []),
            'fictional_shipping_companies': route_data.get('shipping_companies', []),
            'fictional_route_conditions': route_data.get('route_conditions', 'Standard')
        }
        
        return entry
    
    def _determine_economic_zone(self, nation_id: str) -> str:
        """Determine economic zone based on controlling nation"""
        if os.path.exists(self.nations_file):
            with open(self.nations_file, 'r') as f:
                nations = json.load(f)
                for nation in nations:
                    if nation.get('_id') == nation_id:
                        # Try to determine from existing patterns
                        if 'terran' in nation_id.lower() or 'directorate' in nation_id.lower():
                            return 'Terran Core Economic Zone'
                        elif 'felgenland' in nation_id.lower() or 'protelani' in nation_id.lower() or 'dorsai' in nation_id.lower():
                            return 'Felgenland Free Trade Zone'
                        elif 'neutral' in nation_id.lower() or 'pentothian' in nation_id.lower():
                            return 'Independent'
                        else:
                            return 'Custom Economic Zone'
        
        return 'Independent'
    
    def _load_existing_routes(self) -> List[Dict[str, Any]]:
        """Load existing trade routes from file"""
        if os.path.exists(self.trade_routes_file):
            with open(self.trade_routes_file, 'r') as f:
                return json.load(f)
        return []
    
    def _add_to_trade_routes_file(self, route_entry: Dict[str, Any]) -> None:
        """Add route entry to the trade routes JSON file"""
        routes = self._load_existing_routes()
        routes.append(route_entry)
        
        with open(self.trade_routes_file, 'w') as f:
            json.dump(routes, f, indent=2)
    
    def get_fictional_trade_routes(self) -> List[Dict[str, Any]]:
        """Get all fictional trade routes (those with fictional_created field)"""
        routes = self._load_existing_routes()
        return [route for route in routes if 'fictional_created' in route]
    
    def get_all_trade_routes(self) -> List[Dict[str, Any]]:
        """Get all trade routes"""
        return self._load_existing_routes()
    
    def get_routes_by_nation(self, nation_id: str) -> List[Dict[str, Any]]:
        """Get all trade routes controlled by a specific nation"""
        routes = self._load_existing_routes()
        return [route for route in routes if route.get('control', {}).get('controlling_nation') == nation_id]
    
    def get_routes_by_system(self, star_id: int) -> List[Dict[str, Any]]:
        """Get all trade routes that include a specific star system"""
        routes = self._load_existing_routes()
        system_routes = []
        
        for route in routes:
            endpoints = route.get('endpoints', {})
            if (endpoints.get('from', {}).get('star_id') == star_id or 
                endpoints.get('to', {}).get('star_id') == star_id):
                system_routes.append(route)
        
        return system_routes
    
    def update_trade_route(self, route_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing trade route"""
        try:
            routes = self._load_existing_routes()
            
            for i, route in enumerate(routes):
                if route.get('_id') == route_id:
                    # Update the route data
                    routes[i].update(updates)
                    routes[i]['fictional_updated'] = datetime.now().isoformat()
                    
                    # Save back to file
                    with open(self.trade_routes_file, 'w') as f:
                        json.dump(routes, f, indent=2)
                    
                    return {
                        'success': True,
                        'data': routes[i],
                        'message': f'Trade route "{route_id}" updated successfully'
                    }
            
            return {'success': False, 'error': f'Trade route with ID "{route_id}" not found'}
            
        except Exception as e:
            return {'success': False, 'error': f'Error updating trade route: {str(e)}'}
    
    def delete_trade_route(self, route_id: str) -> Dict[str, Any]:
        """Delete a trade route by ID"""
        try:
            routes = self._load_existing_routes()
            original_count = len(routes)
            
            # Filter out the route to delete
            routes = [route for route in routes if route.get('_id') != route_id]
            
            if len(routes) == original_count:
                return {'success': False, 'error': f'Trade route with ID "{route_id}" not found'}
            
            # Save back to file
            with open(self.trade_routes_file, 'w') as f:
                json.dump(routes, f, indent=2)
            
            return {
                'success': True,
                'message': f'Trade route "{route_id}" deleted successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Error deleting trade route: {str(e)}'}
    
    def validate_route_data(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trade route data without adding it to the system"""
        try:
            # Check required fields
            required_fields = ['name', 'from_star_id', 'to_star_id', 'controlling_nation', 'route_type']
            missing_fields = [field for field in required_fields if field not in route_data]
            
            if missing_fields:
                return {
                    'valid': False,
                    'errors': [f'Missing required field: {field}' for field in missing_fields]
                }
            
            errors = []
            
            # Validate star systems
            if not self._validate_star_system(route_data['from_star_id']):
                errors.append(f'Origin star system {route_data["from_star_id"]} not found')
            
            if not self._validate_star_system(route_data['to_star_id']):
                errors.append(f'Destination star system {route_data["to_star_id"]} not found')
            
            # Validate nation
            if not self._validate_nation(route_data['controlling_nation']):
                errors.append(f'Nation "{route_data["controlling_nation"]}" not found')
            
            # Check for name conflicts
            proposed_id = self._generate_route_id(route_data['name'])
            existing_routes = self._load_existing_routes()
            
            for route in existing_routes:
                if route.get('name') == route_data['name']:
                    errors.append(f'Trade route with name "{route_data["name"]}" already exists')
                    break
            
            if errors:
                return {'valid': False, 'errors': errors}
            
            return {
                'valid': True,
                'proposed_id': proposed_id,
                'message': 'Trade route data is valid'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Validation error: {str(e)}']
            }