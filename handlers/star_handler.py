"""
Star Handler for managing fictional stars in the Starmap application.
Handles adding new fictional stars to the system.
"""

import csv
import json
import os
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

class StarHandler:
    """Handles operations for fictional stars"""
    
    def __init__(self, data_path: str = 'data'):
        self.data_path = data_path
        self.fictional_stars_file = f'{data_path}/fictional_stars.csv'
        self.stars_file = f'{data_path}/stars.json'
    
    def add_fictional_star(self, star_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new fictional star to the system
        
        Args:
            star_data: Dictionary containing star information with required fields:
                - name: Star name
                - ra: Right ascension 
                - dec: Declination
                - dist: Distance in parsecs
                - mag: Apparent magnitude
                - spect: Spectral type
                And optional fields like description, fictional properties, etc.
        
        Returns:
            Dict containing success status and star data with assigned ID
        """
        try:
            # Validate required fields
            required_fields = ['name', 'ra', 'dec', 'dist', 'mag', 'spect']
            for field in required_fields:
                if field not in star_data:
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            # Generate unique fictional star ID
            fictional_id = self._generate_fictional_id()
            
            # Create star entry
            star_entry = self._create_star_entry(star_data, fictional_id)
            
            # Add to CSV file
            self._append_to_csv(star_entry)
            
            # Add to JSON cache (if exists)
            self._update_json_cache(star_entry)
            
            return {
                'success': True,
                'data': star_entry,
                'message': f'Fictional star "{star_data["name"]}" added successfully with ID {fictional_id}'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Error adding fictional star: {str(e)}'}
    
    def _generate_fictional_id(self) -> int:
        """Generate a unique ID for fictional stars (starting from 999999 and going down)"""
        existing_ids = set()
        
        # Check existing fictional stars
        if os.path.exists(self.fictional_stars_file):
            with open(self.fictional_stars_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['id']:
                        existing_ids.add(int(row['id']))
        
        # Start from 999999 and find the next available ID going down
        fictional_id = 999999
        while fictional_id in existing_ids:
            fictional_id -= 1
            
        return fictional_id
    
    def _create_star_entry(self, star_data: Dict[str, Any], fictional_id: int) -> Dict[str, Any]:
        """Create a complete star entry from input data"""
        # Calculate 3D coordinates from RA/Dec/Distance
        import math
        
        ra_rad = math.radians(star_data['ra'])
        dec_rad = math.radians(star_data['dec'])
        dist = star_data['dist']
        
        x = dist * math.cos(dec_rad) * math.cos(ra_rad)
        y = dist * math.cos(dec_rad) * math.sin(ra_rad)
        z = dist * math.sin(dec_rad)
        
        # Create UUID
        star_uuid = f"HD_{fictional_id}-fictional-star-{star_data['name'].lower().replace(' ', '-')}"
        
        # Build complete star entry
        entry = {
            'id': fictional_id,
            'hip': '',
            'hd': f'{fictional_id}.0',
            'hr': '',
            'gl': '',
            'bf': f'HD {fictional_id}',
            'proper': star_data['name'],
            'ra': star_data['ra'],
            'dec': star_data['dec'],
            'dist': star_data['dist'],
            'pmra': star_data.get('pmra', 0.0),
            'pmdec': star_data.get('pmdec', 0.0),
            'rv': star_data.get('rv', 0.0),
            'mag': star_data['mag'],
            'absmag': self._calculate_absolute_magnitude(star_data['mag'], star_data['dist']),
            'spect': star_data['spect'],
            'ci': star_data.get('ci', 0.0),
            'x': round(x, 6),
            'y': round(y, 6),
            'z': round(z, 6),
            'vx': star_data.get('vx', 0.0),
            'vy': star_data.get('vy', 0.0),
            'vz': star_data.get('vz', 0.0),
            'rarad': ra_rad,
            'decrad': dec_rad,
            'pmrarad': star_data.get('pmrarad', 0.0),
            'pmdecrad': star_data.get('pmdecrad', 0.0),
            'bayer': star_data.get('bayer', ''),
            'flam': star_data.get('flam', ''),
            'con': star_data.get('con', ''),
            'comp': 1,
            'comp_primary': fictional_id,
            'base': '',
            'lum': star_data.get('lum', 1.0),
            'var': star_data.get('var', ''),
            'var_min': star_data.get('var_min', ''),
            'var_max': star_data.get('var_max', ''),
            'UUID': star_uuid
        }
        
        # Add fictional-specific fields
        entry['fictional_name'] = star_data['name']
        entry['fictional_description'] = star_data.get('description', '')
        entry['fictional_created'] = datetime.now().isoformat()
        
        return entry
    
    def _calculate_absolute_magnitude(self, apparent_mag: float, distance_pc: float) -> float:
        """Calculate absolute magnitude from apparent magnitude and distance"""
        import math
        return apparent_mag - 5 * (math.log10(distance_pc) - 1)
    
    def _append_to_csv(self, star_entry: Dict[str, Any]) -> None:
        """Append star entry to CSV file"""
        file_exists = os.path.exists(self.fictional_stars_file)
        
        with open(self.fictional_stars_file, 'a', newline='') as f:
            fieldnames = [
                'id', 'hip', 'hd', 'hr', 'gl', 'bf', 'proper', 'ra', 'dec', 'dist',
                'pmra', 'pmdec', 'rv', 'mag', 'absmag', 'spect', 'ci', 'x', 'y', 'z',
                'vx', 'vy', 'vz', 'rarad', 'decrad', 'pmrarad', 'pmdecrad', 'bayer',
                'flam', 'con', 'comp', 'comp_primary', 'base', 'lum', 'var', 'var_min',
                'var_max', 'UUID'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write star data
            csv_entry = {k: v for k, v in star_entry.items() if k in fieldnames}
            writer.writerow(csv_entry)
    
    def _update_json_cache(self, star_entry: Dict[str, Any]) -> None:
        """Update the JSON stars cache if it exists"""
        if os.path.exists(self.stars_file):
            try:
                with open(self.stars_file, 'r') as f:
                    stars_data = json.load(f)
                
                # Add the new star
                stars_data.append(star_entry)
                
                # Write back to file
                with open(self.stars_file, 'w') as f:
                    json.dump(stars_data, f, indent=2)
                    
            except Exception as e:
                print(f"Warning: Could not update JSON cache: {e}")
    
    def get_fictional_stars(self) -> list:
        """Get all fictional stars"""
        fictional_stars = []
        
        if os.path.exists(self.fictional_stars_file):
            with open(self.fictional_stars_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fictional_stars.append(row)
        
        return fictional_stars
    
    def delete_fictional_star(self, star_id: int) -> Dict[str, Any]:
        """Delete a fictional star by ID"""
        try:
            if not os.path.exists(self.fictional_stars_file):
                return {'success': False, 'error': 'No fictional stars file found'}
            
            # Read all stars except the one to delete
            remaining_stars = []
            star_found = False
            
            with open(self.fictional_stars_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['id']) == star_id:
                        star_found = True
                    else:
                        remaining_stars.append(row)
            
            if not star_found:
                return {'success': False, 'error': f'Fictional star with ID {star_id} not found'}
            
            # Rewrite the file without the deleted star
            with open(self.fictional_stars_file, 'w', newline='') as f:
                if remaining_stars:
                    fieldnames = remaining_stars[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(remaining_stars)
            
            return {
                'success': True,
                'message': f'Fictional star with ID {star_id} deleted successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Error deleting fictional star: {str(e)}'}