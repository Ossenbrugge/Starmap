"""
MontyDB Trade Route Model
Handles trade route data operations using MontyDB
"""

from typing import List, Dict, Any, Optional
from database.config import get_database
import json

class TradeRouteModelDB:
    """Trade route data model using MontyDB"""
    
    def __init__(self):
        self.db = get_database()
        self.trade_routes = self.db.trade_routes
        self._cache = {}
    
    def migrate_from_json(self, data_path: str = 'data'):
        """Migrate trade route data from JSON files to MontyDB"""
        print("🔄 Migrating trade routes to MontyDB...")
        
        try:
            # Clear existing data
            self.trade_routes.delete_many({})
            
            # Load trade routes from JSON
            with open(f'{data_path}/trade_routes.json', 'r') as f:
                raw_routes = json.load(f)
                
                # Convert to MontyDB format
                processed_routes = []
                for route in raw_routes:
                    doc = {
                        '_id': route['_id'],
                        'name': route['name'],
                        'route_type': route['route_type'],
                        'endpoints': {
                            'from': {
                                'star_id': route['endpoints']['from']['star_id'],
                                'system': route['endpoints']['from']['system'],
                                'coordinates': route['endpoints']['from'].get('coordinates')
                            },
                            'to': {
                                'star_id': route['endpoints']['to']['star_id'],
                                'system': route['endpoints']['to']['system'],
                                'coordinates': route['endpoints']['to'].get('coordinates')
                            }
                        },
                        'logistics': {
                            'cargo_types': route['logistics']['cargo_types'],
                            'travel_time_days': route['logistics']['travel_time_days'],
                            'frequency': route['logistics']['frequency'],
                            'capacity': route['logistics'].get('capacity'),
                            'cost_per_unit': route['logistics'].get('cost_per_unit')
                        },
                        'control': {
                            'controlling_nation': route['control']['controlling_nation'],
                            'security_level': route['control']['security_level'],
                            'access_restrictions': route['control'].get('access_restrictions', [])
                        },
                        'status': {
                            'operational': route.get('status', {}).get('operational', True),
                            'maintenance_schedule': route.get('status', {}).get('maintenance_schedule'),
                            'last_inspection': route.get('status', {}).get('last_inspection')
                        },
                        'economics': {
                            'trade_volume_annually': route.get('economics', {}).get('trade_volume_annually'),
                            'revenue_annually': route.get('economics', {}).get('revenue_annually'),
                            'profit_margin': route.get('economics', {}).get('profit_margin')
                        },
                        'description': route.get('description', ''),
                        'metadata': {
                            'established_date': route.get('established_date'),
                            'last_updated': route.get('last_updated')
                        }
                    }
                    processed_routes.append(doc)
                
                if processed_routes:
                    self.trade_routes.insert_many(processed_routes)
                
                print(f"✅ Migrated {len(processed_routes)} trade routes to MontyDB")
                
        except Exception as e:
            print(f"❌ Error migrating trade routes: {e}")
            raise
    
    def get_trade_routes(self) -> List[Dict]:
        """Get all trade routes"""
        try:
            routes = []
            for route in self.trade_routes.find():
                routes.append({
                    'id': route['_id'],
                    'name': route['name'],
                    'route_type': route['route_type'],
                    'endpoints': {
                        'from': {
                            'system': route['endpoints']['from']['system'],
                            'star_id': route['endpoints']['from']['star_id']
                        },
                        'to': {
                            'system': route['endpoints']['to']['system'],
                            'star_id': route['endpoints']['to']['star_id']
                        }
                    },
                    'logistics': {
                        'cargo_types': route['logistics']['cargo_types'],
                        'travel_time_days': route['logistics']['travel_time_days'],
                        'frequency': route['logistics']['frequency']
                    },
                    'control': {
                        'controlling_nation': route['control']['controlling_nation'],
                        'security_level': route['control']['security_level']
                    },
                    'operational': route.get('status', {}).get('operational', True),
                    # Keep flat format for backward compatibility
                    'from_system': route['endpoints']['from']['system'],
                    'to_system': route['endpoints']['to']['system'],
                    'from_star_id': route['endpoints']['from']['star_id'],
                    'to_star_id': route['endpoints']['to']['star_id'],
                    'cargo_types': route['logistics']['cargo_types'],
                    'travel_time_days': route['logistics']['travel_time_days'],
                    'frequency': route['logistics']['frequency'],
                    'controlling_nation': route['control']['controlling_nation'],
                    'security_level': route['control']['security_level']
                })
            return routes
        except Exception as e:
            print(f"Error getting trade routes: {e}")
            return []
    
    def get_route_by_id(self, route_id: str) -> Optional[Dict]:
        """Get specific trade route by ID"""
        return self.trade_routes.find_one({'_id': route_id})
    
    def get_routes_by_star(self, star_id: int) -> List[Dict]:
        """Get all trade routes connected to a star"""
        query = {
            '$or': [
                {'endpoints.from.star_id': star_id},
                {'endpoints.to.star_id': star_id}
            ]
        }
        return list(self.trade_routes.find(query))
    
    def get_routes_by_nation(self, nation_id: str) -> List[Dict]:
        """Get all trade routes controlled by a nation"""
        return list(self.trade_routes.find({'control.controlling_nation': nation_id}))
    
    def search_routes(self, query: str, limit: int = 20) -> List[Dict]:
        """Search trade routes by name or description"""
        if not query:
            return []
        
        search_query = {
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}},
                {'endpoints.from.system': {'$regex': query, '$options': 'i'}},
                {'endpoints.to.system': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        return list(self.trade_routes.find(search_query).limit(limit))
    
    def get_trade_network_analysis(self) -> Dict:
        """Get comprehensive trade network analysis"""
        try:
            # Basic statistics
            total_routes = self.trade_routes.count_documents({})
            operational_routes = self.trade_routes.count_documents({'status.operational': True})
            
            # Since MontyDB aggregate is limited, use basic queries
            all_routes = list(self.trade_routes.find())
            
            # Route types distribution
            route_types: dict[str, int] = {}
            for route in all_routes:
                rt = route.get('route_type', 'Unknown')
                route_types[rt] = route_types.get(rt, 0) + 1
            
            # Nation control analysis
            nation_control: dict[str, int] = {}
            for route in all_routes:
                nation = route['control']['controlling_nation']
                nation_control[nation] = nation_control.get(nation, 0) + 1
            
            # Cargo type analysis
            cargo_analysis: dict[str, int] = {}
            for route in all_routes:
                for cargo in route['logistics']['cargo_types']:
                    cargo_analysis[cargo] = cargo_analysis.get(cargo, 0) + 1
            
            # Hub analysis (most connected stars)
            hub_connections: dict[int, int] = {}
            for route in all_routes:
                from_star = route['endpoints']['from']['star_id']
                to_star = route['endpoints']['to']['star_id']
                hub_connections[from_star] = hub_connections.get(from_star, 0) + 1
                hub_connections[to_star] = hub_connections.get(to_star, 0) + 1
            
            # Sort hubs by connection count
            sorted_hubs = sorted(hub_connections.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Travel time statistics
            travel_times = [route['logistics']['travel_time_days'] for route in all_routes 
                           if isinstance(route['logistics']['travel_time_days'], (int, float))]
            
            travel_stats = {}
            if travel_times:
                travel_stats = {
                    'average_days': round(sum(travel_times) / len(travel_times), 2),
                    'minimum_days': min(travel_times),
                    'maximum_days': max(travel_times)
                }
            else:
                travel_stats = {'average_days': 0, 'minimum_days': 0, 'maximum_days': 0}
            
            analysis = {
                'overview': {
                    'total_routes': total_routes,
                    'operational_routes': operational_routes,
                    'maintenance_routes': total_routes - operational_routes,
                    'operational_percentage': round((operational_routes / total_routes * 100), 2) if total_routes > 0 else 0
                },
                'route_types': route_types,
                'nation_control': nation_control,
                'cargo_distribution': cargo_analysis,
                'travel_statistics': travel_stats,
                'hub_analysis': {
                    'top_hubs': [{'star_id': star_id, 'connections': count} for star_id, count in sorted_hubs]
                }
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error getting trade network analysis: {e}")
            return {}
    
    def add_route(self, route_data: Dict) -> bool:
        """Add a new trade route"""
        try:
            self.trade_routes.insert_one(route_data)
            return True
        except Exception as e:
            print(f"Error adding trade route: {e}")
            return False
    
    def update_route(self, route_id: str, updates: Dict) -> bool:
        """Update trade route data"""
        try:
            result = self.trade_routes.update_one({'_id': route_id}, {'$set': updates})
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating trade route: {e}")
            return False
    
    def delete_route(self, route_id: str) -> bool:
        """Delete a trade route"""
        try:
            result = self.trade_routes.delete_one({'_id': route_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting trade route: {e}")
            return False
    
    def clear_cache(self):
        """Clear internal cache"""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cache_size': len(self._cache),
            'total_routes': self.trade_routes.count_documents({})
        }