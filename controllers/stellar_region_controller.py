from .base_controller import BaseController


class StellarRegionController(BaseController):
    """Controller for stellar region operations"""
    
    def get_stellar_regions(self):
        """Get all stellar regions for overlay visualization"""
        def handler():
            # Get regions data from model
            regions_data = self.model.get_regions_for_visualization()
            
            return self.view.format_stellar_regions_response(regions_data)
        
        return self.handle_request(handler)
    
    def get_stellar_regions_summary(self):
        """Get summary information about stellar regions"""
        def handler():
            summary_data = self.model.get_regions_summary()
            
            return self.view.format_stellar_regions_summary_response(summary_data)
        
        return self.handle_request(handler)
    
    def get_stellar_region_details(self, region_name):
        """Get detailed information for a specific stellar region"""
        def handler():
            # Get region details from model
            region_details = self.model.get_region_by_name(region_name)
            
            if not region_details:
                return self.view.format_not_found_response('Stellar Region', region_name)
            
            return self.view.format_stellar_region_details_response(region_details)
        
        return self.handle_request(handler)
    
    def get_region_boundaries(self, region_name):
        """Get 3D boundary points for a stellar region"""
        def handler():
            params = self.get_request_params(
                optional_params={
                    'resolution': 20
                }
            )
            
            resolution = self.parse_int_param(params['resolution'], 'resolution')
            
            # Get boundary points from model
            boundary_points = self.model.generate_region_boundaries(region_name, resolution)
            
            if not boundary_points:
                return self.view.format_not_found_response('Stellar Region', region_name)
            
            return self.view.format_region_boundaries_response(region_name, boundary_points)
        
        return self.handle_request(handler)
    
    def check_star_region(self):
        """Check which region contains a given star position"""
        def handler():
            params = self.get_request_params(
                required_params=['x', 'y', 'z']
            )
            
            x = self.parse_float_param(params['x'], 'x')
            y = self.parse_float_param(params['y'], 'y') 
            z = self.parse_float_param(params['z'], 'z')
            
            # Find region containing this position
            region = self.model.get_region_for_star(x, y, z)
            
            if region:
                return self.view.format_star_region_response(region, x, y, z)
            else:
                return self.view.format_star_region_response(None, x, y, z)
        
        return self.handle_request(handler)