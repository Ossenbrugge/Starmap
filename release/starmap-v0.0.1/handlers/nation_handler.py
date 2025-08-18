"""
Nation Handler for managing fictional nations in the Starmap application.
Handles adding new fictional nations to the system.
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

class NationHandler:
    """Handles operations for fictional nations"""
    
    def __init__(self, data_path: str = 'data'):
        self.data_path = data_path
        self.nations_file = f'{data_path}/nations.json'
    
    def add_fictional_nation(self, nation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new fictional nation to the system
        
        Args:
            nation_data: Dictionary containing nation information with required fields:
                - name: Nation name
                - full_name: Full official name
                - government_type: Type of government
                - capital_system: Name of capital system
                - capital_star_id: Star ID of capital system
                - territories: List of star IDs controlled by the nation
                And optional fields like description, economy, military, etc.
        
        Returns:
            Dict containing success status and nation data
        """
        try:
            # Validate required fields
            required_fields = ['name', 'full_name', 'government_type', 'capital_system', 'capital_star_id']
            for field in required_fields:
                if field not in nation_data:
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            # Generate nation ID from name
            nation_id = self._generate_nation_id(nation_data['name'])
            
            # Validate territories
            territories = nation_data.get('territories', [nation_data['capital_star_id']])
            if not self._validate_territories(territories):
                return {'success': False, 'error': 'One or more territory star IDs are invalid'}
            
            # Create nation entry
            nation_entry = self._create_nation_entry(nation_data, nation_id)
            
            # Add to nations file
            self._add_to_nations_file(nation_entry)
            
            return {
                'success': True,
                'data': nation_entry,
                'message': f'Fictional nation "{nation_data["name"]}" added successfully with ID {nation_id}'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Error adding fictional nation: {str(e)}'}
    
    def _generate_nation_id(self, name: str) -> str:
        """Generate a unique ID for the nation based on its name"""
        # Convert to lowercase and replace spaces with underscores
        base_id = name.lower().replace(' ', '_').replace('-', '_')
        
        # Remove special characters
        import re
        base_id = re.sub(r'[^a-z0-9_]', '', base_id)
        
        # Check if ID already exists
        existing_nations = self._load_existing_nations()
        existing_ids = {nation.get('_id') for nation in existing_nations}
        
        nation_id = base_id
        counter = 1
        while nation_id in existing_ids:
            nation_id = f"{base_id}_{counter}"
            counter += 1
        
        return nation_id
    
    def _validate_territories(self, territories: List[int]) -> bool:
        """Validate that all territory star IDs exist in the system"""
        # Check in stars.json
        stars_file = f'{self.data_path}/stars.json'
        valid_star_ids = set()
        
        if os.path.exists(stars_file):
            with open(stars_file, 'r') as f:
                stars = json.load(f)
                for star in stars:
                    valid_star_ids.add(star.get('id'))
        
        # Check in fictional_stars.csv
        fictional_stars_file = f'{self.data_path}/fictional_stars.csv'
        if os.path.exists(fictional_stars_file):
            import csv
            with open(fictional_stars_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        valid_star_ids.add(int(row.get('id', 0)))
                    except ValueError:
                        continue
        
        # Check if all territories are valid
        for territory in territories:
            if territory not in valid_star_ids:
                return False
        
        return True
    
    def _create_nation_entry(self, nation_data: Dict[str, Any], nation_id: str) -> Dict[str, Any]:
        """Create a complete nation entry from input data"""
        current_year = datetime.now().year
        
        # Build complete nation entry
        entry = {
            '_id': nation_id,
            'name': nation_data['name'],
            'full_name': nation_data['full_name'],
            'government': {
                'type': nation_data['government_type'],
                'established_year': nation_data.get('established_year', current_year),
                'political_alignment': nation_data.get('political_alignment', 'Neutral'),
                'diplomatic_stance': nation_data.get('diplomatic_stance', 'Neutral toward all powers')
            },
            'capital': {
                'system': nation_data['capital_system'],
                'star_id': nation_data['capital_star_id'],
                'planet': nation_data.get('capital_planet', 'Primary World')
            },
            'territories': nation_data.get('territories', [nation_data['capital_star_id']]),
            'appearance': {
                'color': nation_data.get('primary_color', '#808080'),
                'border_color': nation_data.get('border_color', '#606060')
            },
            'economy': {
                'focus': nation_data.get('economic_focus', 'Diversified economy'),
                'specialties': nation_data.get('economic_specialties', ['Trade', 'Manufacturing']),
                'population': nation_data.get('population', 'Population data unavailable'),
                'gdp': nation_data.get('gdp', None),
                'trade_volume': nation_data.get('trade_volume', None)
            },
            'military': {
                'strength': nation_data.get('military_strength', 'Standard Defense Forces'),
                'doctrine': nation_data.get('military_doctrine', None),
                'fleet_size': nation_data.get('fleet_size', None)
            },
            'description': nation_data.get('description', f'A fictional nation in the Starmap universe.'),
            
            # Fictional-specific metadata
            'fictional_created': datetime.now().isoformat(),
            'fictional_creator': nation_data.get('creator', 'Starmap System'),
            'fictional_category': nation_data.get('category', 'custom_nation'),
            'fictional_culture': nation_data.get('culture_description', ''),
            'fictional_history': nation_data.get('history', ''),
            'fictional_technology_level': nation_data.get('technology_level', 'Standard'),
            'fictional_society_type': nation_data.get('society_type', 'Mixed'),
            'fictional_relations': nation_data.get('diplomatic_relations', {}),
            'fictional_special_traits': nation_data.get('special_traits', [])
        }
        
        return entry
    
    def _load_existing_nations(self) -> List[Dict[str, Any]]:
        """Load existing nations from the nations file"""
        if os.path.exists(self.nations_file):
            with open(self.nations_file, 'r') as f:
                return json.load(f)
        return []
    
    def _add_to_nations_file(self, nation_entry: Dict[str, Any]) -> None:
        """Add nation entry to the nations JSON file"""
        nations = self._load_existing_nations()
        nations.append(nation_entry)
        
        with open(self.nations_file, 'w') as f:
            json.dump(nations, f, indent=2)
    
    def get_fictional_nations(self) -> List[Dict[str, Any]]:
        """Get all fictional nations (those with fictional_created field)"""
        nations = self._load_existing_nations()
        return [nation for nation in nations if 'fictional_created' in nation]
    
    def get_all_nations(self) -> List[Dict[str, Any]]:
        """Get all nations"""
        return self._load_existing_nations()
    
    def get_nation_by_id(self, nation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific nation by its ID"""
        nations = self._load_existing_nations()
        for nation in nations:
            if nation.get('_id') == nation_id:
                return nation
        return None
    
    def update_nation(self, nation_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing nation"""
        try:
            nations = self._load_existing_nations()
            
            for i, nation in enumerate(nations):
                if nation.get('_id') == nation_id:
                    # Update the nation data
                    nations[i].update(updates)
                    nations[i]['fictional_updated'] = datetime.now().isoformat()
                    
                    # Save back to file
                    with open(self.nations_file, 'w') as f:
                        json.dump(nations, f, indent=2)
                    
                    return {
                        'success': True,
                        'data': nations[i],
                        'message': f'Nation "{nation_id}" updated successfully'
                    }
            
            return {'success': False, 'error': f'Nation with ID "{nation_id}" not found'}
            
        except Exception as e:
            return {'success': False, 'error': f'Error updating nation: {str(e)}'}
    
    def delete_nation(self, nation_id: str) -> Dict[str, Any]:
        """Delete a nation by ID"""
        try:
            nations = self._load_existing_nations()
            original_count = len(nations)
            
            # Filter out the nation to delete
            nations = [nation for nation in nations if nation.get('_id') != nation_id]
            
            if len(nations) == original_count:
                return {'success': False, 'error': f'Nation with ID "{nation_id}" not found'}
            
            # Save back to file
            with open(self.nations_file, 'w') as f:
                json.dump(nations, f, indent=2)
            
            return {
                'success': True,
                'message': f'Nation "{nation_id}" deleted successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Error deleting nation: {str(e)}'}
    
    def get_nations_by_territory(self, star_id: int) -> List[Dict[str, Any]]:
        """Get all nations that control a specific star system"""
        nations = self._load_existing_nations()
        controlling_nations = []
        
        for nation in nations:
            territories = nation.get('territories', [])
            if star_id in territories:
                controlling_nations.append(nation)
        
        return controlling_nations
    
    def validate_nation_data(self, nation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate nation data without adding it to the system"""
        try:
            # Check required fields
            required_fields = ['name', 'full_name', 'government_type', 'capital_system', 'capital_star_id']
            missing_fields = [field for field in required_fields if field not in nation_data]
            
            if missing_fields:
                return {
                    'valid': False,
                    'errors': [f'Missing required field: {field}' for field in missing_fields]
                }
            
            # Check territory validation
            territories = nation_data.get('territories', [nation_data['capital_star_id']])
            if not self._validate_territories(territories):
                return {
                    'valid': False,
                    'errors': ['One or more territory star IDs are invalid']
                }
            
            # Check for name conflicts
            proposed_id = self._generate_nation_id(nation_data['name'])
            existing_nations = self._load_existing_nations()
            
            for nation in existing_nations:
                if nation.get('name') == nation_data['name']:
                    return {
                        'valid': False,
                        'errors': [f'Nation with name "{nation_data["name"]}" already exists']
                    }
            
            return {
                'valid': True,
                'proposed_id': proposed_id,
                'message': 'Nation data is valid'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Validation error: {str(e)}']
            }