import json
import os
import math
from .base_model import BaseModel


class StellarRegionModel(BaseModel):
    """Model for managing stellar regions data and operations"""
    
    def load_data(self):
        """Load stellar regions data from JSON file"""
        try:
            data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'stellar_regions.json')
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.data = data.get('regions', [])
            self.metadata = data.get('metadata', {})
            print(f"✅ Stellar regions loaded: {len(self.data)} regions")
            
        except FileNotFoundError:
            print("Warning: stellar_regions.json not found, using empty data")
            self.data = []
            self.metadata = {}
        except json.JSONDecodeError as e:
            print(f"Error parsing stellar_regions.json: {e}")
            self.data = []
            self.metadata = {}
    
    def get_all_regions(self):
        """Get all stellar regions"""
        return self.data
    
    def get_region_by_name(self, name):
        """Get a specific region by name"""
        for region in self.data:
            if region['name'].lower() == name.lower():
                return region
        return None
    
    def get_regions_summary(self):
        """Get summary information about stellar regions"""
        if not self.data:
            return {
                'total_regions': 0,
                'total_population': 0,
                'regions': []
            }
        
        # Calculate total population (parse numbers from population strings)
        total_population = 0
        for region in self.data:
            pop_str = region.get('population', '0')
            # Extract numeric values from population strings like "18+ billion"
            if 'billion' in pop_str.lower():
                num = float(pop_str.split()[0].replace('+', '').replace(',', ''))
                total_population += num
            elif 'million' in pop_str.lower():
                num = float(pop_str.split()[0].replace('+', '').replace(',', ''))
                total_population += num / 1000  # Convert to billions
        
        return {
            'total_regions': len(self.data),
            'total_population': f"{total_population:.1f}+ billion",
            'metadata': self.metadata,
            'regions': sorted(self.data, key=lambda x: x.get('established', 0))
        }
    
    def get_regions_for_visualization(self):
        """Get regions formatted for 3D visualization"""
        visualization_data = []
        
        for region in self.data:
            # Convert color from RGB array to hex string
            color_rgb = region.get('color', [128, 128, 128])
            color_hex = f"#{color_rgb[0]:02x}{color_rgb[1]:02x}{color_rgb[2]:02x}"
            
            viz_region = {
                'name': region['name'],
                'description': region.get('description', ''),
                'center_point': region['center_point'],
                'longitude_range': region['longitude_range'],
                'latitude_range': region['latitude_range'],
                'distance_range': region['distance_range'],
                'diameter': region.get('diameter', 50),
                'color': color_hex,
                'color_rgb': color_rgb,
                'established': region.get('established'),
                'population': region.get('population'),
                'significance': region.get('significance', '')
            }
            visualization_data.append(viz_region)
        
        return visualization_data
    
    def point_in_region(self, x, y, z, region_name):
        """Check if a 3D point falls within a specific region"""
        region = self.get_region_by_name(region_name)
        if not region:
            return False
        
        # Convert Cartesian coordinates to spherical (galactic coordinates)
        distance = math.sqrt(x*x + y*y + z*z)
        
        # Check distance range
        dist_min, dist_max = region['distance_range']
        if distance < dist_min or distance > dist_max:
            return False
        
        # Convert to galactic longitude and latitude
        if distance == 0:
            return region_name == "Human Core"  # Sol is always in Human Core
        
        # Galactic longitude (0-360 degrees)
        longitude = math.degrees(math.atan2(y, x))
        if longitude < 0:
            longitude += 360
        
        # Galactic latitude (-90 to +90 degrees)
        latitude = math.degrees(math.asin(z / distance))
        
        # Check longitude range
        lon_min, lon_max = region['longitude_range']
        if lon_min <= lon_max:
            # Normal range (e.g., 60-120)
            if longitude < lon_min or longitude > lon_max:
                return False
        else:
            # Wrapped range (e.g., 300-60 wraps around 0)
            if longitude < lon_min and longitude > lon_max:
                return False
        
        # Check latitude range
        lat_min, lat_max = region['latitude_range']
        if latitude < lat_min or latitude > lat_max:
            return False
        
        return True
    
    def get_region_for_star(self, x, y, z):
        """Get the region that contains a given star position"""
        for region in self.data:
            if self.point_in_region(x, y, z, region['name']):
                return region
        return None
    
    def generate_region_boundaries(self, region_name, resolution=20):
        """Generate 3D boundary points for a region (for visualization)"""
        region = self.get_region_by_name(region_name)
        if not region:
            return []
        
        lon_min, lon_max = region['longitude_range']
        lat_min, lat_max = region['latitude_range']
        dist_min, dist_max = region['distance_range']
        
        boundary_points = []
        
        # Generate boundary at minimum and maximum distances
        for distance in [dist_min, dist_max]:
            for i in range(resolution):
                # Longitude sweep at constant latitude
                for lat in [lat_min, lat_max]:
                    lon = lon_min + (lon_max - lon_min) * i / (resolution - 1)
                    if lon_min > lon_max:  # Handle wraparound
                        if i < resolution // 2:
                            lon = lon_min + (360 - lon_min) * i / (resolution // 2 - 1)
                        else:
                            lon = 0 + lon_max * (i - resolution // 2) / (resolution // 2 - 1)
                    
                    # Convert to Cartesian
                    lon_rad = math.radians(lon)
                    lat_rad = math.radians(lat)
                    
                    x = distance * math.cos(lat_rad) * math.cos(lon_rad)
                    y = distance * math.cos(lat_rad) * math.sin(lon_rad)
                    z = distance * math.sin(lat_rad)
                    
                    boundary_points.append([x, y, z])
                
                # Latitude sweep at constant longitude
                for lon in [lon_min, lon_max]:
                    lat = lat_min + (lat_max - lat_min) * i / (resolution - 1)
                    
                    # Convert to Cartesian
                    lon_rad = math.radians(lon)
                    lat_rad = math.radians(lat)
                    
                    x = distance * math.cos(lat_rad) * math.cos(lon_rad)
                    y = distance * math.cos(lat_rad) * math.sin(lon_rad)
                    z = distance * math.sin(lat_rad)
                    
                    boundary_points.append([x, y, z])
        
        return boundary_points