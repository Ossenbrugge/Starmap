from .base_model import BaseModel
from fictional_nations import fictional_nations
from trade_routes import get_all_trade_routes


class NationModel(BaseModel):
    """Model for managing fictional nation and trade route data"""
    
    def load_data(self):
        """Load nation data from fictional_nations module"""
        self.data = fictional_nations.copy()
        self.trade_routes = get_all_trade_routes()
    
    def get_all_nations(self):
        """Get all fictional nations"""
        return self.data
    
    def get_nation_by_id(self, nation_id):
        """Get nation details by ID"""
        return self.data.get(nation_id)
    
    def get_nation_territories(self, nation_id):
        """Get star territories for a specific nation"""
        nation = self.get_nation_by_id(nation_id)
        if nation:
            return nation.get('territories', [])
        return []
    
    def get_nations_summary(self):
        """Get summary of all nations"""
        return {
            'nations': self.data,
            'total_nations': len(self.data),
            'total_territories': sum(len(nation.get('territories', [])) 
                                   for nation in self.data.values()),
            'government_types': list(set(nation.get('government_type', 'Unknown') 
                                       for nation in self.data.values()))
        }
    
    def get_trade_routes(self):
        """Get all trade routes data"""
        return self.trade_routes
    
    def get_trade_routes_summary(self):
        """Get summary of trade routes"""
        all_routes = []
        for route_group, routes in self.trade_routes.items():
            all_routes.extend(routes)
        
        return {
            'trade_routes': self.trade_routes,
            'total_route_groups': len(self.trade_routes),
            'total_routes': len(all_routes),
            'route_types': list(set(route.get('route_type', 'Unknown') 
                                  for route in all_routes)),
            'controlling_nations': list(set(route.get('controlling_nation', 'None') 
                                          for route in all_routes 
                                          if route.get('controlling_nation')))
        }
    
    def get_routes_for_nation(self, nation_id):
        """Get all trade routes controlled by a specific nation"""
        nation_routes = []
        
        for route_group, routes in self.trade_routes.items():
            for route in routes:
                if route.get('controlling_nation') == nation_id:
                    nation_routes.append({
                        'group': route_group,
                        **route
                    })
        
        return nation_routes
    
    def get_star_nation_info(self, star_id):
        """Get nation information for a star"""
        for nation_id, nation in self.data.items():
            if star_id in nation.get('territories', []):
                return {
                    'id': nation_id,
                    'name': nation['name'],
                    'color': nation['color'],
                    'government_type': nation['government_type'],
                    'capital_system': nation.get('capital_system'),
                    'population': nation.get('population'),
                    'description': nation.get('description')
                }
        
        # Return neutral zone if not found
        return {
            'id': 'neutral_zone',
            'name': 'Neutral Zone',
            'color': '#808080',
            'government_type': 'None'
        }
    
    def get_nation_statistics(self, nation_id):
        """Get detailed statistics for a nation"""
        nation = self.get_nation_by_id(nation_id)
        if not nation:
            return None
        
        territories = nation.get('territories', [])
        routes = self.get_routes_for_nation(nation_id)
        
        # Calculate route statistics
        route_types = {}
        total_trade_value = 0
        
        for route in routes:
            route_type = route.get('route_type', 'Unknown')
            route_types[route_type] = route_types.get(route_type, 0) + 1
            
            # Estimate trade value based on route type and frequency
            if route.get('frequency'):
                if 'daily' in route['frequency'].lower():
                    total_trade_value += 365
                elif 'weekly' in route['frequency'].lower():
                    total_trade_value += 52
                elif 'monthly' in route['frequency'].lower():
                    total_trade_value += 12
        
        return {
            'nation_id': nation_id,
            'name': nation['name'],
            'government_type': nation['government_type'],
            'territory_count': len(territories),
            'territory_systems': territories,
            'trade_route_count': len(routes),
            'trade_routes_by_type': route_types,
            'estimated_annual_trade_frequency': total_trade_value,
            'capital_system': nation.get('capital_system'),
            'population': nation.get('population'),
            'founding_date': nation.get('founding_date'),
            'description': nation.get('description')
        }
    
    def find_trade_route(self, from_star_id, to_star_id):
        """Find trade route between two stars"""
        for route_group, routes in self.trade_routes.items():
            for route in routes:
                if ((route.get('from_star_id') == from_star_id and 
                     route.get('to_star_id') == to_star_id) or
                    (route.get('from_star_id') == to_star_id and 
                     route.get('to_star_id') == from_star_id)):
                    return {
                        'group': route_group,
                        **route
                    }
        return None
    
    def get_nations_with_most_territory(self, limit=5):
        """Get nations with the most star systems"""
        nation_territories = []
        
        for nation_id, nation in self.data.items():
            if nation_id != 'neutral_zone':
                territory_count = len(nation.get('territories', []))
                if territory_count > 0:
                    nation_territories.append({
                        'nation_id': nation_id,
                        'name': nation['name'],
                        'territory_count': territory_count,
                        'government_type': nation['government_type'],
                        'color': nation['color']
                    })
        
        # Sort by territory count and return top nations
        nation_territories.sort(key=lambda x: x['territory_count'], reverse=True)
        return nation_territories[:limit]
    
    def get_border_tensions(self):
        """Analyze potential border tensions between nations"""
        # This would require star coordinate data to determine adjacency
        # For now, return a placeholder structure
        tensions = []
        
        for nation_id, nation in self.data.items():
            if nation_id != 'neutral_zone' and len(nation.get('territories', [])) > 1:
                # Find nations with overlapping or adjacent territories
                # This is a simplified example - real implementation would need
                # coordinate analysis
                tensions.append({
                    'nation_id': nation_id,
                    'nation_name': nation['name'],
                    'territory_count': len(nation.get('territories', [])),
                    'government_type': nation['government_type'],
                    'potential_conflicts': []  # Would be populated with actual analysis
                })
        
        return tensions