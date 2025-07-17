"""
Exoplanet Handler for managing fictional exoplanets in the Starmap application.
Handles adding new fictional exoplanets to the system.
"""

import csv
import json
import os
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

class ExoplanetHandler:
    """Handles operations for fictional exoplanets"""
    
    def __init__(self, data_path: str = 'data'):
        self.data_path = data_path
        self.exoplanets_file = f'{data_path}/exoplanets.json'
        self.fictional_exoplanets_csv = f'{data_path}/fictional_exoplanets.csv'
    
    def add_fictional_exoplanet(self, exoplanet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new fictional exoplanet to the system
        
        Args:
            exoplanet_data: Dictionary containing exoplanet information with required fields:
                - name: Planet name
                - host_star_id: ID of the host star
                - orbital_period_days: Orbital period in days
                - semi_major_axis_au: Semi-major axis in AU
                And optional fields like mass, radius, temperature, description, etc.
        
        Returns:
            Dict containing success status and exoplanet data
        """
        try:
            # Validate required fields
            required_fields = ['name', 'host_star_id', 'orbital_period_days', 'semi_major_axis_au']
            for field in required_fields:
                if field not in exoplanet_data:
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            # Validate host star exists
            if not self._validate_host_star(exoplanet_data['host_star_id']):
                return {'success': False, 'error': f'Host star with ID {exoplanet_data["host_star_id"]} not found'}
            
            # Create exoplanet entry
            exoplanet_entry = self._create_exoplanet_entry(exoplanet_data)
            
            # Add to JSON file
            self._add_to_json(exoplanet_entry)
            
            # Add to CSV file for fictional exoplanets
            self._add_to_csv(exoplanet_entry)
            
            return {
                'success': True,
                'data': exoplanet_entry,
                'message': f'Fictional exoplanet "{exoplanet_data["name"]}" added successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Error adding fictional exoplanet: {str(e)}'}
    
    def _validate_host_star(self, star_id: int) -> bool:
        """Validate that the host star exists in the system"""
        # Check in stars.json
        stars_file = f'{self.data_path}/stars.json'
        if os.path.exists(stars_file):
            with open(stars_file, 'r') as f:
                stars = json.load(f)
                for star in stars:
                    if star.get('id') == star_id:
                        return True
        
        # Check in fictional_stars.csv
        fictional_stars_file = f'{self.data_path}/fictional_stars.csv'
        if os.path.exists(fictional_stars_file):
            with open(fictional_stars_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row.get('id', 0)) == star_id:
                        return True
        
        return False
    
    def _create_exoplanet_entry(self, exoplanet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete exoplanet entry from input data"""
        # Get host star information
        host_star_info = self._get_host_star_info(exoplanet_data['host_star_id'])
        
        # Calculate planet properties
        equilibrium_temp = self._calculate_equilibrium_temperature(
            exoplanet_data.get('semi_major_axis_au', 1.0),
            host_star_info.get('teff', 5778),  # Default to solar temperature
            host_star_info.get('radius', 1.0)   # Default to solar radius
        )
        
        # Build complete exoplanet entry
        entry = {
            'pl_name': exoplanet_data['name'],
            'pl_letter': exoplanet_data.get('planet_letter', 'b'),
            'hostname': host_star_info.get('proper', f'Star-{exoplanet_data["host_star_id"]}'),
            'star_id': exoplanet_data['host_star_id'],
            'pl_orbper': exoplanet_data['orbital_period_days'],
            'pl_orbsmax': exoplanet_data['semi_major_axis_au'],
            'pl_rade': exoplanet_data.get('radius_earth', None),
            'pl_radj': exoplanet_data.get('radius_jupiter', None),
            'pl_masse': exoplanet_data.get('mass_earth', None),
            'pl_massj': exoplanet_data.get('mass_jupiter', None),
            'pl_orbeccen': exoplanet_data.get('orbital_eccentricity', 0.0),
            'pl_eqt': equilibrium_temp,
            'pl_orbincl': exoplanet_data.get('orbital_inclination', None),
            'discovery_year': exoplanet_data.get('discovery_year', datetime.now().year),
            'discoverymethod': exoplanet_data.get('discovery_method', 'Fictional'),
            'disc_facility': exoplanet_data.get('discovery_facility', 'Starmap Universe'),
            
            # Host star properties
            'ra': host_star_info.get('ra'),
            'dec': host_star_info.get('dec'),
            'sy_dist': host_star_info.get('dist'),
            'sy_vmag': host_star_info.get('mag'),
            'st_teff': host_star_info.get('teff'),
            'st_rad': host_star_info.get('radius'),
            'st_mass': host_star_info.get('mass'),
            'st_spectype': host_star_info.get('spect'),
            
            # Fictional-specific fields
            'fictional_name': exoplanet_data['name'],
            'fictional_description': exoplanet_data.get('description', ''),
            'fictional_type': exoplanet_data.get('planet_type', 'Unknown'),
            'fictional_habitability': exoplanet_data.get('habitability_score', 0.0),
            'fictional_atmosphere': exoplanet_data.get('atmosphere', ''),
            'fictional_surface': exoplanet_data.get('surface_description', ''),
            'fictional_population': exoplanet_data.get('population', 0),
            'fictional_government': exoplanet_data.get('government_type', ''),
            'fictional_created': datetime.now().isoformat(),
            
            # Calculated properties
            'planet_type': self._classify_planet_type(exoplanet_data),
            'habitable_zone_au': self._calculate_habitable_zone(host_star_info),
            'potentially_habitable': self._assess_habitability(exoplanet_data, host_star_info)
        }
        
        return entry
    
    def _get_host_star_info(self, star_id: int) -> Dict[str, Any]:
        """Get host star information from the database"""
        # Check stars.json first
        stars_file = f'{self.data_path}/stars.json'
        if os.path.exists(stars_file):
            with open(stars_file, 'r') as f:
                stars = json.load(f)
                for star in stars:
                    if star.get('id') == star_id:
                        return star
        
        # Check fictional_stars.csv
        fictional_stars_file = f'{self.data_path}/fictional_stars.csv'
        if os.path.exists(fictional_stars_file):
            with open(fictional_stars_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row.get('id', 0)) == star_id:
                        return row
        
        # Return default values if star not found
        return {
            'proper': f'Unknown Star {star_id}',
            'ra': 0.0,
            'dec': 0.0,
            'dist': 10.0,
            'mag': 10.0,
            'teff': 5778,
            'radius': 1.0,
            'mass': 1.0,
            'spect': 'G2V'
        }
    
    def _calculate_equilibrium_temperature(self, semi_major_axis: float, star_temp: float, star_radius: float) -> float:
        """Calculate equilibrium temperature of the planet"""
        try:
            # Simple equilibrium temperature calculation
            # T_eq = T_star * sqrt(R_star / (2 * a))
            import math
            return star_temp * math.sqrt(star_radius / (2 * semi_major_axis))
        except:
            return 273.0  # Default to 0°C
    
    def _classify_planet_type(self, exoplanet_data: Dict[str, Any]) -> str:
        """Classify planet type based on its properties"""
        radius_earth = exoplanet_data.get('radius_earth')
        mass_earth = exoplanet_data.get('mass_earth')
        
        if radius_earth is not None:
            if radius_earth < 1.25:
                return 'Terrestrial'
            elif radius_earth < 2.0:
                return 'Super-Earth'
            elif radius_earth < 4.0:
                return 'Mini-Neptune'
            else:
                return 'Gas Giant'
        elif mass_earth is not None:
            if mass_earth < 2.0:
                return 'Terrestrial'
            elif mass_earth < 10.0:
                return 'Super-Earth'
            elif mass_earth < 50.0:
                return 'Mini-Neptune'
            else:
                return 'Gas Giant'
        else:
            return exoplanet_data.get('planet_type', 'Unknown')
    
    def _calculate_habitable_zone(self, star_info: Dict[str, Any]) -> float:
        """Calculate the habitable zone distance for the star"""
        try:
            # Simple habitable zone calculation based on stellar luminosity
            import math
            star_temp = float(star_info.get('teff', 5778))
            star_radius = float(star_info.get('radius', 1.0))
            
            # Luminosity relative to Sun
            luminosity = (star_radius ** 2) * ((star_temp / 5778) ** 4)
            
            # Habitable zone inner edge (approximate)
            return math.sqrt(luminosity)
        except:
            return 1.0  # Default to 1 AU
    
    def _assess_habitability(self, exoplanet_data: Dict[str, Any], star_info: Dict[str, Any]) -> bool:
        """Assess if the planet is potentially habitable"""
        try:
            semi_major_axis = float(exoplanet_data['semi_major_axis_au'])
            habitable_zone = self._calculate_habitable_zone(star_info)
            
            # Simple habitability check: within 0.5 to 1.5 times habitable zone distance
            return 0.5 * habitable_zone <= semi_major_axis <= 1.5 * habitable_zone
        except:
            return False
    
    def _add_to_json(self, exoplanet_entry: Dict[str, Any]) -> None:
        """Add exoplanet entry to JSON file"""
        exoplanets = []
        
        # Read existing exoplanets if file exists
        if os.path.exists(self.exoplanets_file):
            with open(self.exoplanets_file, 'r') as f:
                exoplanets = json.load(f)
        
        # Add new exoplanet
        exoplanets.append(exoplanet_entry)
        
        # Write back to file
        with open(self.exoplanets_file, 'w') as f:
            json.dump(exoplanets, f, indent=2)
    
    def _add_to_csv(self, exoplanet_entry: Dict[str, Any]) -> None:
        """Add exoplanet entry to CSV file for fictional exoplanets"""
        file_exists = os.path.exists(self.fictional_exoplanets_csv)
        
        with open(self.fictional_exoplanets_csv, 'a', newline='') as f:
            fieldnames = [
                'pl_name', 'pl_letter', 'hostname', 'star_id', 'pl_orbper', 'pl_orbsmax',
                'pl_rade', 'pl_radj', 'pl_masse', 'pl_massj', 'pl_orbeccen', 'pl_eqt',
                'pl_orbincl', 'discovery_year', 'discoverymethod', 'disc_facility',
                'ra', 'dec', 'sy_dist', 'sy_vmag', 'st_teff', 'st_rad', 'st_mass',
                'st_spectype', 'fictional_name', 'fictional_description', 'fictional_type',
                'fictional_habitability', 'fictional_atmosphere', 'fictional_surface',
                'fictional_population', 'fictional_government', 'fictional_created',
                'planet_type', 'habitable_zone_au', 'potentially_habitable'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write exoplanet data
            csv_entry = {k: v for k, v in exoplanet_entry.items() if k in fieldnames}
            writer.writerow(csv_entry)
    
    def get_fictional_exoplanets(self) -> List[Dict[str, Any]]:
        """Get all fictional exoplanets"""
        fictional_exoplanets = []
        
        if os.path.exists(self.fictional_exoplanets_csv):
            with open(self.fictional_exoplanets_csv, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fictional_exoplanets.append(row)
        
        return fictional_exoplanets
    
    def get_exoplanets_by_star(self, star_id: int) -> List[Dict[str, Any]]:
        """Get all exoplanets for a specific star"""
        exoplanets = []
        
        # Check JSON file
        if os.path.exists(self.exoplanets_file):
            with open(self.exoplanets_file, 'r') as f:
                all_exoplanets = json.load(f)
                for planet in all_exoplanets:
                    if planet.get('star_id') == star_id:
                        exoplanets.append(planet)
        
        return exoplanets
    
    def delete_fictional_exoplanet(self, planet_name: str) -> Dict[str, Any]:
        """Delete a fictional exoplanet by name"""
        try:
            # Remove from JSON file
            removed_from_json = False
            if os.path.exists(self.exoplanets_file):
                with open(self.exoplanets_file, 'r') as f:
                    exoplanets = json.load(f)
                
                original_count = len(exoplanets)
                exoplanets = [p for p in exoplanets if p.get('fictional_name') != planet_name]
                
                if len(exoplanets) < original_count:
                    removed_from_json = True
                    with open(self.exoplanets_file, 'w') as f:
                        json.dump(exoplanets, f, indent=2)
            
            # Remove from CSV file
            removed_from_csv = False
            if os.path.exists(self.fictional_exoplanets_csv):
                remaining_exoplanets = []
                
                with open(self.fictional_exoplanets_csv, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('fictional_name') != planet_name:
                            remaining_exoplanets.append(row)
                        else:
                            removed_from_csv = True
                
                if removed_from_csv:
                    with open(self.fictional_exoplanets_csv, 'w', newline='') as f:
                        if remaining_exoplanets:
                            fieldnames = remaining_exoplanets[0].keys()
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(remaining_exoplanets)
            
            if removed_from_json or removed_from_csv:
                return {
                    'success': True,
                    'message': f'Fictional exoplanet "{planet_name}" deleted successfully'
                }
            else:
                return {'success': False, 'error': f'Fictional exoplanet "{planet_name}" not found'}
            
        except Exception as e:
            return {'success': False, 'error': f'Error deleting fictional exoplanet: {str(e)}'}