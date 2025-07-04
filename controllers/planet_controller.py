from .base_controller import BaseController
from flask import jsonify


class PlanetController(BaseController):
    """Controller for planet and planetary system operations"""
    
    def __init__(self, planet_model, star_model, view):
        super().__init__(planet_model, view)
        self.star_model = star_model
    
    def add_planet(self):
        """Add a new planet to a star system"""
        def handler():
            params = self.get_request_params(
                required_params=['star_id', 'planet']
            )
            
            star_id = self.parse_int_param(params['star_id'], 'star_id')
            planet_data = params['planet']
            
            if not isinstance(planet_data, dict):
                raise ValueError('Planet data must be a dictionary')
            
            # Validate planet data
            self.model.validate_planet_data(planet_data)
            
            # Check if star exists
            star_details = self.star_model.get_star_details(star_id)
            if not star_details:
                return self.view.format_not_found_response('Star', star_id)
            
            # Add planet to the system
            new_planet = self.model.add_planet_to_star(star_id, planet_data)
            
            # Get updated planet count
            planets = self.model.get_planets_for_star(star_id)
            
            return self.view.format_planet_add_response(
                True, 
                star_details['name'], 
                new_planet['name'], 
                len(planets)
            )
        
        return self.handle_request(handler)
    
    def get_planetary_systems(self):
        """Get all stars with planetary systems"""
        def handler():
            # Get systems summary from model
            systems_data = self.model.get_systems_summary()
            
            # Enhance with star data
            enhanced_systems = []
            for system in systems_data['systems']:
                star_id = system['star_id']
                star_details = self.star_model.get_star_details(star_id)
                
                if star_details:
                    enhanced_system = {
                        'id': star_id,
                        'name': star_details['name'],
                        'constellation': star_details.get('constellation_full', 
                                                        star_details.get('constellation', '')),
                        'distance': star_details['properties']['distance'],
                        'planet_count': system['planet_count'],
                        'confirmed_planets': system['confirmed_planets'],
                        'candidate_planets': system['candidate_planets']
                    }
                    enhanced_systems.append(enhanced_system)
            
            response_data = {
                'total_systems': systems_data['total_systems'],
                'systems': sorted(enhanced_systems, key=lambda x: x['planet_count'], reverse=True)
            }
            
            return self.view.format_planetary_systems_response(response_data)
        
        return self.handle_request(handler)
    
    def get_star_system(self, star_id):
        """Get planetary system for a specific star"""
        def handler():
            star_id_int = self.parse_int_param(star_id, 'star_id')
            
            # Get star details
            star_details = self.star_model.get_star_details(star_id_int)
            if not star_details:
                return self.view.format_not_found_response('Star', star_id)
            
            # Get planets for this star
            planets = self.model.get_planets_for_star(star_id_int)
            
            # Add planets to star details
            star_details['planets'] = planets
            
            return self.view.format_star_details_response(star_details)
        
        return self.handle_request(handler)
    
    def get_systems_by_planet_type(self, planet_type):
        """Get systems containing planets of a specific type"""
        def handler():
            all_systems = self.model.get_all_planetary_systems()
            matching_systems = []
            
            for system in all_systems:
                star_id = system['star_id']
                planets = system['planets']
                
                # Check if any planet matches the type
                matching_planets = [p for p in planets if p.get('type', '').lower() == planet_type.lower()]
                
                if matching_planets:
                    star_details = self.star_model.get_star_details(star_id)
                    if star_details:
                        matching_systems.append({
                            'star_id': star_id,
                            'star_name': star_details['name'],
                            'constellation': star_details.get('constellation_full', ''),
                            'distance': star_details['properties']['distance'],
                            'matching_planets': len(matching_planets),
                            'total_planets': len(planets),
                            'planets_of_type': [self.view.format_planet_data(p) for p in matching_planets]
                        })
            
            response_data = {
                'planet_type': planet_type,
                'total_systems': len(matching_systems),
                'systems': sorted(matching_systems, key=lambda x: x['matching_planets'], reverse=True)
            }
            
            return jsonify(response_data)
        
        return self.handle_request(handler)
    
    def get_habitable_planets(self):
        """Get planets in habitable zones"""
        def handler():
            all_systems = self.model.get_all_planetary_systems()
            habitable_planets = []
            
            for system in all_systems:
                star_id = system['star_id']
                planets = system['planets']
                
                star_details = self.star_model.get_star_details(star_id)
                if not star_details:
                    continue
                
                # Calculate habitable zone (simplified)
                # Assumes solar-type star habitable zone is 0.95-1.37 AU
                star_luminosity = star_details['properties'].get('luminosity', 1.0)
                hz_inner = 0.95 * (star_luminosity ** 0.5)
                hz_outer = 1.37 * (star_luminosity ** 0.5)
                
                for planet in planets:
                    distance_au = planet.get('distance_au', 0)
                    if hz_inner <= distance_au <= hz_outer:
                        habitable_planets.append({
                            'star_id': star_id,
                            'star_name': star_details['name'],
                            'constellation': star_details.get('constellation_full', ''),
                            'star_distance': star_details['properties']['distance'],
                            'planet': self.view.format_planet_data(planet),
                            'habitable_zone': {
                                'inner_au': round(hz_inner, 3),
                                'outer_au': round(hz_outer, 3),
                                'planet_position': round(distance_au, 3)
                            }
                        })
            
            response_data = {
                'total_habitable_planets': len(habitable_planets),
                'planets': sorted(habitable_planets, key=lambda x: x['star_distance'])
            }
            
            return jsonify(response_data)
        
        return self.handle_request(handler)
    
    def get_confirmed_exoplanets(self):
        """Get only confirmed exoplanets"""
        def handler():
            all_systems = self.model.get_all_planetary_systems()
            confirmed_planets = []
            
            for system in all_systems:
                star_id = system['star_id']
                planets = system['planets']
                
                star_details = self.star_model.get_star_details(star_id)
                if not star_details:
                    continue
                
                confirmed = [p for p in planets if p.get('confirmed', False)]
                
                if confirmed:
                    confirmed_planets.append({
                        'star_id': star_id,
                        'star_name': star_details['name'],
                        'constellation': star_details.get('constellation_full', ''),
                        'distance': star_details['properties']['distance'],
                        'confirmed_planet_count': len(confirmed),
                        'total_planet_count': len(planets),
                        'confirmed_planets': [self.view.format_planet_data(p) for p in confirmed]
                    })
            
            response_data = {
                'total_systems_with_confirmed': len(confirmed_planets),
                'total_confirmed_planets': sum(s['confirmed_planet_count'] for s in confirmed_planets),
                'systems': sorted(confirmed_planets, key=lambda x: x['confirmed_planet_count'], reverse=True)
            }
            
            return jsonify(response_data)
        
        return self.handle_request(handler)
    
    def get_planet_statistics(self):
        """Get statistics about all planets"""
        def handler():
            systems_summary = self.model.get_systems_summary()
            all_systems = self.model.get_all_planetary_systems()
            
            # Count planets by type
            planet_types = {}
            discovery_years = {}
            size_distribution = {'sub_earth': 0, 'earth_like': 0, 'super_earth': 0, 'giant': 0}
            
            for system in all_systems:
                for planet in system['planets']:
                    # Count by type
                    ptype = planet.get('type', 'Unknown')
                    planet_types[ptype] = planet_types.get(ptype, 0) + 1
                    
                    # Count by discovery year
                    year = planet.get('discovery_year', 'Unknown')
                    discovery_years[year] = discovery_years.get(year, 0) + 1
                    
                    # Size distribution
                    radius = planet.get('radius_earth', 1.0)
                    if radius < 0.8:
                        size_distribution['sub_earth'] += 1
                    elif radius <= 1.25:
                        size_distribution['earth_like'] += 1
                    elif radius <= 2.0:
                        size_distribution['super_earth'] += 1
                    else:
                        size_distribution['giant'] += 1
            
            response_data = {
                'total_systems': systems_summary['total_systems'],
                'total_planets': systems_summary['total_planets'],
                'confirmed_planets': systems_summary['confirmed_planets'],
                'candidate_planets': systems_summary['candidate_planets'],
                'planet_types': planet_types,
                'discovery_years': discovery_years,
                'size_distribution': size_distribution
            }
            
            return jsonify(response_data)
        
        return self.handle_request(handler)