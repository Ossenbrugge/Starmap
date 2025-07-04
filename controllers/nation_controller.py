from .base_controller import BaseController
from flask import jsonify


class NationController(BaseController):
    """Controller for nation and political overlay operations"""
    
    def __init__(self, nation_model, star_model, view):
        super().__init__(nation_model, view)
        self.star_model = star_model
    
    def get_nations(self):
        """Get all fictional nations"""
        def handler():
            nations_data = self.model.get_nations_summary()
            return self.view.format_nations_response(nations_data)
        
        return self.handle_request(handler)
    
    def get_nation_details(self, nation_id):
        """Get detailed information for a specific nation"""
        def handler():
            nation = self.model.get_nation_by_id(nation_id)
            if not nation:
                return self.view.format_not_found_response('Nation', nation_id)
            
            # Get territory star details
            territory_stars = []
            for star_id in nation.get('territories', []):
                star_details = self.star_model.get_star_details(star_id)
                if star_details:
                    territory_stars.append({
                        'id': star_id,
                        'name': star_details['name'],
                        'fictional_name': star_details['fictional_data'].get('name'),
                        'coordinates': star_details['coordinates'],
                        'distance': star_details['properties']['distance'],
                        'spectral_class': star_details['properties']['spectral_class']
                    })
            
            # Enhance nation data
            enhanced_nation = {
                **nation,
                'territory_stars': territory_stars,
                'territory_count': len(territory_stars)
            }
            
            return self.view.format_nation_details_response(enhanced_nation)
        
        return self.handle_request(handler)
    
    def get_trade_routes(self):
        """Get all trade routes"""
        def handler():
            trade_routes_data = self.model.get_trade_routes_summary()
            return self.view.format_trade_routes_response(trade_routes_data)
        
        return self.handle_request(handler)
    
    def get_nation_trade_routes(self, nation_id):
        """Get trade routes controlled by a specific nation"""
        def handler():
            nation = self.model.get_nation_by_id(nation_id)
            if not nation:
                return self.view.format_not_found_response('Nation', nation_id)
            
            routes = self.model.get_routes_for_nation(nation_id)
            
            # Enhance routes with star information
            enhanced_routes = []
            for route in routes:
                from_star = self.star_model.get_star_details(route['from_star_id'])
                to_star = self.star_model.get_star_details(route['to_star_id'])
                
                if from_star and to_star:
                    enhanced_route = {
                        **route,
                        'from_star_name': from_star['name'],
                        'to_star_name': to_star['name'],
                        'from_star_fictional': from_star['fictional_data'].get('name'),
                        'to_star_fictional': to_star['fictional_data'].get('name')
                    }
                    enhanced_routes.append(enhanced_route)
            
            response_data = {
                'nation_id': nation_id,
                'nation_name': nation['name'],
                'total_routes': len(enhanced_routes),
                'routes': enhanced_routes
            }
            
            return jsonify(response_data)
        
        return self.handle_request(handler)
    
    def get_nation_statistics(self, nation_id):
        """Get detailed statistics for a nation"""
        def handler():
            stats = self.model.get_nation_statistics(nation_id)
            if not stats:
                return self.view.format_not_found_response('Nation', nation_id)
            
            # Enhance with star details
            territory_details = []
            for star_id in stats['territory_systems']:
                star_details = self.star_model.get_star_details(star_id)
                if star_details:
                    territory_details.append({
                        'star_id': star_id,
                        'name': star_details['name'],
                        'fictional_name': star_details['fictional_data'].get('name'),
                        'distance': star_details['properties']['distance'],
                        'spectral_class': star_details['properties']['spectral_class'],
                        'coordinates': star_details['coordinates']
                    })
            
            enhanced_stats = {
                **stats,
                'territory_details': territory_details
            }
            
            return jsonify(enhanced_stats)
        
        return self.handle_request(handler)
    
    def get_political_map_data(self):
        """Get data for political overlay visualization"""
        def handler():
            nations = self.model.get_all_nations()
            
            political_data = {}
            for nation_id, nation in nations.items():
                if nation_id != 'neutral_zone':
                    territory_data = []
                    for star_id in nation.get('territories', []):
                        star_details = self.star_model.get_star_details(star_id)
                        if star_details:
                            territory_data.append({
                                'star_id': star_id,
                                'name': star_details['name'],
                                'coordinates': star_details['coordinates'],
                                'color': nation['color']
                            })
                    
                    political_data[nation_id] = {
                        'name': nation['name'],
                        'color': nation['color'],
                        'government_type': nation['government_type'],
                        'territories': territory_data
                    }
            
            return jsonify({
                'political_data': political_data,
                'total_nations': len(political_data)
            })
        
        return self.handle_request(handler)
    
    def get_nations_by_government_type(self, government_type):
        """Get nations with a specific government type"""
        def handler():
            all_nations = self.model.get_all_nations()
            matching_nations = []
            
            for nation_id, nation in all_nations.items():
                if (nation_id != 'neutral_zone' and 
                    nation.get('government_type', '').lower() == government_type.lower()):
                    
                    # Get territory count
                    territory_count = len(nation.get('territories', []))
                    
                    matching_nations.append({
                        'nation_id': nation_id,
                        'name': nation['name'],
                        'government_type': nation['government_type'],
                        'territory_count': territory_count,
                        'capital_system': nation.get('capital_system'),
                        'population': nation.get('population'),
                        'color': nation['color']
                    })
            
            response_data = {
                'government_type': government_type,
                'total_nations': len(matching_nations),
                'nations': sorted(matching_nations, key=lambda x: x['territory_count'], reverse=True)
            }
            
            return jsonify(response_data)
        
        return self.handle_request(handler)
    
    def get_largest_nations(self, limit=5):
        """Get nations with the most territories"""
        def handler():
            largest_nations = self.model.get_nations_with_most_territory(limit)
            
            # Enhance with additional details
            enhanced_nations = []
            for nation in largest_nations:
                nation_details = self.model.get_nation_by_id(nation['nation_id'])
                if nation_details:
                    enhanced_nation = {
                        **nation,
                        'capital_system': nation_details.get('capital_system'),
                        'population': nation_details.get('population'),
                        'founding_date': nation_details.get('founding_date'),
                        'description': nation_details.get('description')
                    }
                    enhanced_nations.append(enhanced_nation)
            
            response_data = {
                'total_nations_ranked': len(enhanced_nations),
                'largest_nations': enhanced_nations
            }
            
            return jsonify(response_data)
        
        return self.handle_request(handler)
    
    def get_trade_route_between_stars(self, star1_id, star2_id):
        """Find trade route between two specific stars"""
        def handler():
            star1_id_int = self.parse_int_param(star1_id, 'star1_id')
            star2_id_int = self.parse_int_param(star2_id, 'star2_id')
            
            # Check if stars exist
            star1 = self.star_model.get_star_details(star1_id_int)
            star2 = self.star_model.get_star_details(star2_id_int)
            
            if not star1 or not star2:
                return self.view.error_response('One or both stars not found')
            
            # Find trade route
            route = self.model.find_trade_route(star1_id_int, star2_id_int)
            
            if not route:
                return jsonify({
                    'route_found': False,
                    'star1': {'id': star1_id_int, 'name': star1['name']},
                    'star2': {'id': star2_id_int, 'name': star2['name']},
                    'message': 'No direct trade route found between these stars'
                })
            
            response_data = {
                'route_found': True,
                'star1': {'id': star1_id_int, 'name': star1['name']},
                'star2': {'id': star2_id_int, 'name': star2['name']},
                'route': route
            }
            
            return jsonify(response_data)
        
        return self.handle_request(handler)
    
    def get_border_analysis(self):
        """Get analysis of potential border tensions"""
        def handler():
            tensions = self.model.get_border_tensions()
            return jsonify({
                'border_analysis': tensions,
                'total_nations_analyzed': len(tensions)
            })
        
        return self.handle_request(handler)