from .base_controller import BaseController
from galactic_directions import get_galactic_cardinal_markers, get_galactic_coordinate_grid
from flask import jsonify


class MapController(BaseController):
    """Controller for starmap visualization and coordinate operations"""
    
    def __init__(self, star_model, planet_model, view):
        super().__init__(star_model, view)
        self.planet_model = planet_model
    
    def render_main_page(self):
        """Render the main starmap page"""
        def handler():
            return self.view.render_starmap_page()
        
        return self.handle_request(handler)
    
    def get_galactic_directions(self):
        """Get galactic cardinal direction markers"""
        def handler():
            params = self.get_request_params(
                optional_params={
                    'distance': 50.0,
                    'grid': 'false'
                }
            )
            
            distance = self.parse_float_param(params['distance'], 'distance')
            include_grid = self.parse_bool_param(params['grid'], 'grid')
            
            # Get the cardinal direction markers
            markers = get_galactic_cardinal_markers(distance)
            
            # Optionally include coordinate grid
            grid_data = []
            if include_grid:
                grid_data = get_galactic_coordinate_grid(distance)
            
            response_data = {
                'markers': markers,
                'grid': grid_data,
                'distance': distance,
                'total_markers': len(markers)
            }
            
            return self.view.format_galactic_directions_response(response_data)
        
        return self.handle_request(handler)
    
    def get_map_bounds(self):
        """Get the bounds of the current star data for viewport calculations"""
        def handler():
            all_stars = self.model.get_all()
            
            if all_stars is None or all_stars.empty:
                return self.view.error_response('No star data available')
            
            # Calculate bounds
            bounds = {
                'x_min': float(all_stars['x'].min()),
                'x_max': float(all_stars['x'].max()),
                'y_min': float(all_stars['y'].min()),
                'y_max': float(all_stars['y'].max()),
                'z_min': float(all_stars['z'].min()),
                'z_max': float(all_stars['z'].max())
            }
            
            # Calculate center and span
            center = {
                'x': (bounds['x_min'] + bounds['x_max']) / 2,
                'y': (bounds['y_min'] + bounds['y_max']) / 2,
                'z': (bounds['z_min'] + bounds['z_max']) / 2
            }
            
            span = {
                'x': bounds['x_max'] - bounds['x_min'],
                'y': bounds['y_max'] - bounds['y_min'],
                'z': bounds['z_max'] - bounds['z_min']
            }
            
            response_data = {
                'bounds': bounds,
                'center': center,
                'span': span,
                'total_stars': len(all_stars)
            }
            
            return jsonify(response_data)
        
        return self.handle_request(handler)
    
    def get_star_density_map(self, grid_size=20):
        """Get star density information for heatmap visualization"""
        def handler():
            all_stars = self.model.get_all()
            
            if all_stars is None or all_stars.empty:
                return self.view.error_response('No star data available')
            
            # Calculate bounds
            x_min, x_max = all_stars['x'].min(), all_stars['x'].max()
            y_min, y_max = all_stars['y'].min(), all_stars['y'].max()
            
            # Create grid
            x_step = (x_max - x_min) / grid_size
            y_step = (y_max - y_min) / grid_size
            
            density_grid = []
            
            for i in range(grid_size):
                for j in range(grid_size):
                    x_start = x_min + i * x_step
                    x_end = x_start + x_step
                    y_start = y_min + j * y_step
                    y_end = y_start + y_step
                    
                    # Count stars in this grid cell
                    stars_in_cell = all_stars[
                        (all_stars['x'] >= x_start) & (all_stars['x'] < x_end) &
                        (all_stars['y'] >= y_start) & (all_stars['y'] < y_end)
                    ]
                    
                    density_grid.append({
                        'x_center': x_start + x_step / 2,
                        'y_center': y_start + y_step / 2,
                        'x_range': [x_start, x_end],
                        'y_range': [y_start, y_end],
                        'star_count': len(stars_in_cell),
                        'avg_magnitude': float(stars_in_cell['mag'].mean()) if len(stars_in_cell) > 0 else None
                    })
            
            response_data = {
                'grid_size': grid_size,
                'total_cells': len(density_grid),
                'density_data': density_grid,
                'bounds': {
                    'x_min': x_min, 'x_max': x_max,
                    'y_min': y_min, 'y_max': y_max
                }
            }
            
            return jsonify(response_data)
        
        return self.handle_request(handler)
    
    def get_constellation_boundaries(self):
        """Get constellation boundary data for overlay"""
        def handler():
            all_stars = self.model.get_all()
            
            if all_stars is None or all_stars.empty:
                return self.view.error_response('No star data available')
            
            # Group stars by constellation
            constellations = {}
            
            for _, star in all_stars.iterrows():
                constellation = star.get('constellation_full', star.get('constellation_short', 'Unknown'))
                
                if constellation not in constellations:
                    constellations[constellation] = []
                
                constellations[constellation].append({
                    'x': float(star['x']),
                    'y': float(star['y']),
                    'z': float(star['z']),
                    'name': star.get('primary_name', f"Star {star['id']}"),
                    'magnitude': float(star['mag'])
                })
            
            # Calculate constellation centers and boundaries
            constellation_data = []
            
            for const_name, stars in constellations.items():
                if len(stars) > 0:
                    x_coords = [s['x'] for s in stars]
                    y_coords = [s['y'] for s in stars]
                    z_coords = [s['z'] for s in stars]
                    
                    constellation_data.append({
                        'name': const_name,
                        'star_count': len(stars),
                        'center': {
                            'x': sum(x_coords) / len(x_coords),
                            'y': sum(y_coords) / len(y_coords),
                            'z': sum(z_coords) / len(z_coords)
                        },
                        'bounds': {
                            'x_min': min(x_coords), 'x_max': max(x_coords),
                            'y_min': min(y_coords), 'y_max': max(y_coords),
                            'z_min': min(z_coords), 'z_max': max(z_coords)
                        },
                        'brightest_star': min(stars, key=lambda s: s['magnitude']),
                        'stars': stars
                    })
            
            response_data = {
                'total_constellations': len(constellation_data),
                'constellations': sorted(constellation_data, key=lambda c: c['star_count'], reverse=True)
            }
            
            return jsonify(response_data)
        
        return self.handle_request(handler)
    
    def get_coordinate_system_info(self):
        """Get information about the coordinate system used"""
        def handler():
            info = {
                'coordinate_system': 'Galactic Cartesian',
                'units': 'parsecs',
                'origin': 'Solar System (Sol)',
                'x_axis': 'Galactic longitude 0°, latitude 0°',
                'y_axis': 'Galactic longitude 90°, latitude 0°',
                'z_axis': 'North Galactic Pole',
                'reference_frame': 'J2000.0',
                'data_sources': [
                    'Hipparcos Catalog',
                    'Gaia Data Release',
                    'Fictional star systems'
                ],
                'distance_calculation': '3D Euclidean distance',
                'parsec_to_lightyear': 3.26156,
                'au_per_parsec': 206265
            }
            
            return jsonify(info)
        
        return self.handle_request(handler)
    
    def get_visualization_settings(self):
        """Get recommended visualization settings"""
        def handler():
            all_stars = self.model.get_all()
            
            if all_stars is None or all_stars.empty:
                return self.view.error_response('No star data available')
            
            # Calculate recommended settings based on data
            mag_range = {
                'min': float(all_stars['mag'].min()),
                'max': float(all_stars['mag'].max()),
                'recommended_limit': 6.0  # Naked eye limit
            }
            
            distance_range = {
                'min': float(all_stars['dist'].min()),
                'max': float(all_stars['dist'].max()),
                'recommended_limit': 100.0  # 100 parsecs for good performance
            }
            
            spectral_classes = list(all_stars['spect'].dropna().unique())
            
            settings = {
                'magnitude_range': mag_range,
                'distance_range': distance_range,
                'available_spectral_classes': spectral_classes,
                'recommended_star_count': 1000,
                'color_schemes': {
                    'magnitude': 'Bright to dim stars',
                    'spectral_type': 'Based on stellar temperature',
                    'distance': 'Near to far stars',
                    'political': 'Nation-controlled territories'
                },
                'default_view': {
                    'camera_position': {'x': 1.5, 'y': 1.5, 'z': 1.5},
                    'magnitude_limit': 6.0,
                    'star_count_limit': 1000,
                    'show_grid': True,
                    'show_labels': False
                }
            }
            
            return jsonify(settings)
        
        return self.handle_request(handler)