from .base_controller import BaseController


class StarController(BaseController):
    """Controller for star-related operations"""
    
    def get_stars(self):
        """Get stars for display with optional filtering"""
        def handler():
            # Get optional parameters
            params = self.get_request_params(
                optional_params={
                    'mag_limit': 6.0,
                    'count_limit': 1000
                }
            )
            
            mag_limit = self.parse_float_param(params['mag_limit'], 'mag_limit')
            count_limit = self.parse_int_param(params['count_limit'], 'count_limit')
            
            # Get stars from model
            stars_data = self.model.get_stars_for_display(mag_limit, count_limit)
            
            return self.view.format_stars_response(stars_data)
        
        return self.handle_request(handler)
    
    def get_star_details(self, star_id):
        """Get detailed information for a specific star"""
        def handler():
            star_id_int = self.parse_int_param(star_id, 'star_id')
            
            # Get star details from model
            star_details = self.model.get_star_details(star_id_int)
            
            if not star_details:
                return self.view.format_not_found_response('Star', star_id)
            
            return self.view.format_star_details_response(star_details)
        
        return self.handle_request(handler)
    
    def search_stars(self):
        """Search stars by name, identifier, or spectral type"""
        def handler():
            params = self.get_request_params(
                optional_params={
                    'q': '',
                    'spectral': '',
                    'limit': 50
                }
            )
            
            query = params['q'].strip()
            spectral_type = params['spectral'].strip()
            limit = self.parse_int_param(params['limit'], 'limit')
            
            if not query and not spectral_type:
                return self.view.error_response('No search query or spectral type provided')
            
            # Search stars using model
            results = self.model.search_stars(query, spectral_type)
            
            return self.view.format_search_response(results, query, spectral_type, limit)
        
        return self.handle_request(handler)
    
    def calculate_distance(self):
        """Calculate distance between two stars"""
        def handler():
            params = self.get_request_params(
                required_params=['star1', 'star2']
            )
            
            star1_id = self.parse_int_param(params['star1'], 'star1')
            star2_id = self.parse_int_param(params['star2'], 'star2')
            
            # Calculate distance using model
            distance_data = self.model.calculate_distance(star1_id, star2_id)
            
            if not distance_data:
                return self.view.error_response('One or both stars not found')
            
            return self.view.format_distance_response(distance_data)
        
        return self.handle_request(handler)
    
    def get_spectral_types(self):
        """Get list of available spectral types"""
        def handler():
            spectral_data = self.model.get_spectral_types()
            return self.view.format_spectral_types_response(spectral_data)
        
        return self.handle_request(handler)
    
    def export_csv(self):
        """Export bright stars as CSV"""
        def handler():
            params = self.get_request_params(
                optional_params={
                    'mag_limit': 6.0,
                    'count_limit': 100
                }
            )
            
            mag_limit = self.parse_float_param(params['mag_limit'], 'mag_limit')
            count_limit = self.parse_int_param(params['count_limit'], 'count_limit')
            
            # Get export data from model
            export_data = self.model.get_bright_stars_for_export(mag_limit, count_limit)
            
            return self.view.format_csv_export_response(export_data)
        
        return self.handle_request(handler)
    
    def filter_by_magnitude(self, mag_min=None, mag_max=None):
        """Filter stars by magnitude range"""
        def handler():
            # Get current stars and apply magnitude filter
            all_stars = self.model.get_all()
            
            if all_stars is None or all_stars.empty:
                return self.view.error_response('No star data available')
            
            filtered_stars = all_stars.copy()
            
            if mag_min is not None:
                filtered_stars = filtered_stars[filtered_stars['mag'] >= mag_min]
            
            if mag_max is not None:
                filtered_stars = filtered_stars[filtered_stars['mag'] <= mag_max]
            
            # Format for JSON response
            formatted_stars = self.model._format_stars_for_json(filtered_stars)
            
            return self.view.format_stars_response(formatted_stars)
        
        return self.handle_request(handler)
    
    def filter_by_distance(self, dist_min=None, dist_max=None):
        """Filter stars by distance range"""
        def handler():
            # Get current stars and apply distance filter
            all_stars = self.model.get_all()
            
            if all_stars is None or all_stars.empty:
                return self.view.error_response('No star data available')
            
            filtered_stars = all_stars.copy()
            
            if dist_min is not None:
                filtered_stars = filtered_stars[filtered_stars['dist'] >= dist_min]
            
            if dist_max is not None:
                filtered_stars = filtered_stars[filtered_stars['dist'] <= dist_max]
            
            # Format for JSON response
            formatted_stars = self.model._format_stars_for_json(filtered_stars)
            
            return self.view.format_stars_response(formatted_stars)
        
        return self.handle_request(handler)
    
    def get_stars_by_constellation(self, constellation):
        """Get stars in a specific constellation"""
        def handler():
            all_stars = self.model.get_all()
            
            if all_stars is None or all_stars.empty:
                return self.view.error_response('No star data available')
            
            # Filter by constellation (both short and full names)
            constellation_stars = all_stars[
                (all_stars['constellation_short'].str.contains(constellation, case=False, na=False)) |
                (all_stars['constellation_full'].str.contains(constellation, case=False, na=False))
            ]
            
            # Format for JSON response
            formatted_stars = self.model._format_stars_for_json(constellation_stars)
            
            return self.view.format_stars_response(formatted_stars)
        
        return self.handle_request(handler)
    
    def get_nearest_stars(self, count=10):
        """Get the nearest stars to Sol"""
        def handler():
            all_stars = self.model.get_all()
            
            if all_stars is None or all_stars.empty:
                return self.view.error_response('No star data available')
            
            # Sort by distance and get nearest stars
            nearest_stars = all_stars.nsmallest(count, 'dist')
            
            # Format for JSON response
            formatted_stars = self.model._format_stars_for_json(nearest_stars)
            
            return self.view.format_stars_response(formatted_stars)
        
        return self.handle_request(handler)
    
    def get_brightest_stars(self, count=10):
        """Get the brightest stars (lowest magnitude)"""
        def handler():
            all_stars = self.model.get_all()
            
            if all_stars is None or all_stars.empty:
                return self.view.error_response('No star data available')
            
            # Sort by magnitude (lower is brighter) and get brightest stars
            brightest_stars = all_stars.nsmallest(count, 'mag')
            
            # Format for JSON response
            formatted_stars = self.model._format_stars_for_json(brightest_stars)
            
            return self.view.format_stars_response(formatted_stars)
        
        return self.handle_request(handler)