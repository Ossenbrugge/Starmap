from flask import render_template, jsonify, request
from .base_view import BaseView
import gzip
import json


class ApiView(BaseView):
    """View class for API responses"""
    
    def render_starmap_page(self):
        """Render the main starmap page"""
        try:
            return render_template('starmap.html')
        except Exception as e:
            return self._render_error_page(str(e))
    
    def _render_error_page(self, error_message):
        """Render an error page when template loading fails"""
        import os
        return f"""
        <html>
        <head><title>Starmap - Error</title></head>
        <body>
            <h1>Template Error</h1>
            <p>Error: {error_message}</p>
            <p>Working directory: {os.getcwd()}</p>
            <p>Templates directory exists: {os.path.exists('templates')}</p>
            <p>Template file exists: {os.path.exists('templates/starmap.html')}</p>
        </body>
        </html>
        """
    
    def format_stars_response(self, stars_data):
        """Format stars data for API response with optional compression"""
        if not stars_data:
            return self.error_response("No star data available")
        
        formatted_stars = []
        for star in stars_data:
            formatted_star = self.format_star_data(star)
            if formatted_star:
                formatted_stars.append(formatted_star)
        
        return self._create_response(formatted_stars)
    
    def _create_response(self, data):
        """Create JSON response"""
        return jsonify(data)
    
    def format_star_details_response(self, star_details):
        """Format detailed star information for API response"""
        if not star_details:
            return self.error_response("Star not found", 404)
        
        return jsonify(star_details)
    
    def format_search_response(self, results, query, spectral_filter=None, limit=50):
        """Format search results for API response"""
        total_results = len(results)
        limited_results = results[:limit] if len(results) > limit else results
        
        response_data = {
            'query': query,
            'spectral_filter': spectral_filter,
            'count': len(limited_results),
            'total_matching': total_results,
            'results': limited_results
        }
        
        return jsonify(response_data)
    
    def format_distance_response(self, distance_data):
        """Format distance calculation response"""
        if not distance_data:
            return self.error_response("Distance calculation failed")
        
        return jsonify(distance_data)
    
    def format_planet_add_response(self, success, star_name, planet_name, planet_count):
        """Format planet addition response"""
        if success:
            return jsonify({
                'success': True,
                'message': f'Added planet {planet_name} to {star_name}',
                'planet_count': planet_count
            })
        else:
            return self.error_response("Failed to add planet")
    
    def format_spectral_types_response(self, spectral_data):
        """Format spectral types data for API response"""
        return jsonify(spectral_data)
    
    def format_planetary_systems_response(self, systems_data):
        """Format planetary systems data for API response"""
        return jsonify(systems_data)
    
    def format_nations_response(self, nations_data):
        """Format nations data for API response"""
        return jsonify(nations_data)
    
    def format_trade_routes_response(self, trade_routes_data):
        """Format trade routes data for API response"""
        return jsonify(trade_routes_data)
    
    def format_nation_details_response(self, nation_details):
        """Format detailed nation information for API response"""
        if not nation_details:
            return self.error_response("Nation not found", 404)
        
        return jsonify(nation_details)
    
    def format_galactic_directions_response(self, directions_data):
        """Format galactic directions data for API response"""
        return jsonify(directions_data)
    
    def format_stellar_regions_response(self, regions_data):
        """Format stellar regions data for API response"""
        return jsonify({
            'success': True,
            'total_regions': len(regions_data),
            'regions': regions_data
        })
    
    def format_stellar_regions_summary_response(self, summary_data):
        """Format stellar regions summary for API response"""
        return jsonify(summary_data)
    
    def format_stellar_region_details_response(self, region_details):
        """Format detailed stellar region information for API response"""
        if not region_details:
            return self.error_response("Stellar region not found", 404)
        
        return jsonify(region_details)
    
    def format_region_boundaries_response(self, region_name, boundary_points):
        """Format region boundary points for API response"""
        return jsonify({
            'region_name': region_name,
            'boundary_points': boundary_points,
            'point_count': len(boundary_points)
        })
    
    def format_star_region_response(self, region, x, y, z):
        """Format star region check response"""
        if region:
            return jsonify({
                'found': True,
                'region': region,
                'coordinates': {'x': x, 'y': y, 'z': z}
            })
        else:
            return jsonify({
                'found': False,
                'region': None,
                'coordinates': {'x': x, 'y': y, 'z': z},
                'message': 'No stellar region found for this position'
            })
    
    def format_csv_export_response(self, csv_data, filename='starmap_export.csv'):
        """Format CSV export response"""
        if csv_data is None or csv_data.empty:
            return self.error_response("No data available for export")
        
        csv_content = csv_data.to_csv(index=False)
        return self.csv_response(csv_content, filename)
    
    def format_validation_error_response(self, validation_errors):
        """Format validation error response"""
        return self.error_response(f"Validation failed: {validation_errors}", 400)
    
    def format_not_found_response(self, resource_type, resource_id):
        """Format not found error response"""
        return self.error_response(f"{resource_type} with ID {resource_id} not found", 404)
    
    def format_server_error_response(self, error_message):
        """Format server error response"""
        return self.error_response(f"Server error: {error_message}", 500)


class TemplateView(BaseView):
    """View class for template rendering"""
    
    def render_starmap(self):
        """Render the main starmap template"""
        return render_template('starmap.html')
    
    def render_controls(self):
        """Render the controls window template"""
        return render_template('controls.html')
    
    def render_stardata(self):
        """Render the star data window template"""
        return render_template('stardata.html')
    
    def render_template(self, template_name):
        """Generic template rendering method"""
        return render_template(template_name)
    
    def render_error(self, error_message, status_code=500):
        """Render an error template"""
        # For now, return a simple error page
        # In a full implementation, this would render an error template
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Starmap - Error {status_code}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .error {{ color: #d32f2f; }}
                .details {{ background: #f5f5f5; padding: 20px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1 class="error">Error {status_code}</h1>
            <div class="details">
                <p>{error_message}</p>
            </div>
            <p><a href="/">Return to Starmap</a></p>
        </body>
        </html>
        """
        return error_html, status_code