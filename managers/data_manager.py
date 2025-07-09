"""
Unified Data Manager
Main interface for all CRUD operations and data management
"""

import sys
import os
import json
from typing import Dict, List, Optional, Union
from datetime import datetime

# Import all managers
from star_manager import StarManager
from nation_manager import NationManager
from trade_route_manager import TradeRouteManager
from planetary_system_manager import PlanetarySystemManager
from felgenland_cleanup import FelgenlandCleanup

# Import templates
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from templates.data_templates import (
    StarTemplate, NationTemplate, TradeRouteTemplate, 
    PlanetarySystemTemplate, StellarRegionTemplate, EXAMPLE_TEMPLATES
)


class DataManager:
    """Unified interface for all data management operations"""
    
    def __init__(self):
        self.star_manager = StarManager()
        self.nation_manager = NationManager()
        self.trade_route_manager = TradeRouteManager()
        self.system_manager = PlanetarySystemManager()
        self.cleanup_manager = FelgenlandCleanup()
    
    # =================
    # STAR OPERATIONS
    # =================
    
    def add_star(self, star_data: Dict) -> int:
        """Add a new star to the database"""
        return self.star_manager.add_star(star_data)
    
    def add_star_from_template(self, template_type: str, **kwargs) -> int:
        """Add a star using a template"""
        if template_type == 'basic':
            star_data = StarTemplate.create_basic_star(**kwargs)
        elif template_type == 'fictional':
            star_data = StarTemplate.create_fictional_star(**kwargs)
        else:
            raise ValueError(f"Unknown star template type: {template_type}")
        
        return self.add_star(star_data)
    
    def get_star(self, star_id: int) -> Optional[Dict]:
        """Get star details"""
        return self.star_manager.get_star(star_id)
    
    def search_stars(self, **kwargs) -> List[Dict]:
        """Search stars with various filters"""
        return self.star_manager.search_stars(**kwargs)
    
    def update_star(self, star_id: int, update_data: Dict) -> bool:
        """Update star information"""
        return self.star_manager.update_star(star_id, update_data)
    
    def delete_star(self, star_id: int, force: bool = False) -> bool:
        """Delete a star"""
        return self.star_manager.delete_star(star_id, force)
    
    def get_star_statistics(self) -> Dict:
        """Get star database statistics"""
        return self.star_manager.get_star_statistics()
    
    # =================
    # NATION OPERATIONS
    # =================
    
    def add_nation(self, nation_data: Dict) -> str:
        """Add a new nation to the database"""
        return self.nation_manager.add_nation(nation_data)
    
    def add_nation_from_template(self, template_type: str, **kwargs) -> str:
        """Add a nation using a template"""
        if template_type == 'basic':
            nation_data = NationTemplate.create_nation(**kwargs)
        elif template_type == 'confederation':
            nation_data = NationTemplate.create_trading_confederation(**kwargs)
        elif template_type == 'coalition':
            nation_data = NationTemplate.create_exploration_coalition(**kwargs)
        else:
            raise ValueError(f"Unknown nation template type: {template_type}")
        
        return self.add_nation(nation_data)
    
    def get_nation(self, nation_id: str) -> Optional[Dict]:
        """Get nation details"""
        return self.nation_manager.get_nation(nation_id)
    
    def list_nations(self, **kwargs) -> List[Dict]:
        """List nations with filters"""
        return self.nation_manager.list_nations(**kwargs)
    
    def update_nation(self, nation_id: str, update_data: Dict) -> bool:
        """Update nation information"""
        return self.nation_manager.update_nation(nation_id, update_data)
    
    def add_territory(self, nation_id: str, star_id: int) -> bool:
        """Add territory to a nation"""
        return self.nation_manager.add_territory(nation_id, star_id)
    
    def remove_territory(self, nation_id: str, star_id: int) -> bool:
        """Remove territory from a nation"""
        return self.nation_manager.remove_territory(nation_id, star_id)
    
    def delete_nation(self, nation_id: str, transfer_territories_to: str = None) -> bool:
        """Delete a nation"""
        return self.nation_manager.delete_nation(nation_id, transfer_territories_to)
    
    def get_nation_statistics(self) -> Dict:
        """Get nation statistics"""
        return self.nation_manager.get_nation_statistics()
    
    # =================
    # TRADE ROUTE OPERATIONS
    # =================
    
    def add_trade_route(self, route_data: Dict) -> str:
        """Add a new trade route"""
        return self.trade_route_manager.add_trade_route(route_data)
    
    def add_trade_route_from_template(self, template_type: str, **kwargs) -> str:
        """Add a trade route using a template"""
        if template_type == 'basic':
            route_data = TradeRouteTemplate.create_trade_route(**kwargs)
        elif template_type == 'mining':
            route_data = TradeRouteTemplate.create_mining_route(**kwargs)
        elif template_type == 'passenger':
            route_data = TradeRouteTemplate.create_passenger_route(**kwargs)
        else:
            raise ValueError(f"Unknown trade route template type: {template_type}")
        
        return self.add_trade_route(route_data)
    
    def get_trade_route(self, route_id: str) -> Optional[Dict]:
        """Get trade route details"""
        return self.trade_route_manager.get_trade_route(route_id)
    
    def list_trade_routes(self, **kwargs) -> List[Dict]:
        """List trade routes with filters"""
        return self.trade_route_manager.list_trade_routes(**kwargs)
    
    def update_trade_route(self, route_id: str, update_data: Dict) -> bool:
        """Update trade route information"""
        return self.trade_route_manager.update_trade_route(route_id, update_data)
    
    def delete_trade_route(self, route_id: str) -> bool:
        """Delete a trade route"""
        return self.trade_route_manager.delete_trade_route(route_id)
    
    def get_trade_route_statistics(self) -> Dict:
        """Get trade route statistics"""
        return self.trade_route_manager.get_trade_route_statistics()
    
    def analyze_trade_network(self) -> Dict:
        """Analyze the trade network"""
        return self.trade_route_manager.analyze_trade_network()
    
    # =================
    # PLANETARY SYSTEM OPERATIONS
    # =================
    
    def add_planetary_system(self, system_data: Dict) -> int:
        """Add a new planetary system"""
        return self.system_manager.add_planetary_system(system_data)
    
    def add_planetary_system_from_template(self, template_type: str, **kwargs) -> int:
        """Add a planetary system using a template"""
        if template_type == 'basic':
            system_data = PlanetarySystemTemplate.create_planetary_system(**kwargs)
        elif template_type == 'habitable':
            system_data = self.system_manager.create_habitable_system(**kwargs)
        else:
            raise ValueError(f"Unknown planetary system template type: {template_type}")
        
        return self.add_planetary_system(system_data)
    
    def get_planetary_system(self, star_id: int) -> Optional[Dict]:
        """Get planetary system details"""
        return self.system_manager.get_planetary_system(star_id)
    
    def list_planetary_systems(self, **kwargs) -> List[Dict]:
        """List planetary systems with filters"""
        return self.system_manager.list_planetary_systems(**kwargs)
    
    def add_planet_to_system(self, star_id: int, planet_data: Dict) -> bool:
        """Add a planet to a system"""
        return self.system_manager.add_planet_to_system(star_id, planet_data)
    
    def update_planetary_system(self, star_id: int, update_data: Dict) -> bool:
        """Update planetary system information"""
        return self.system_manager.update_planetary_system(star_id, update_data)
    
    def delete_planetary_system(self, star_id: int) -> bool:
        """Delete a planetary system"""
        return self.system_manager.delete_planetary_system(star_id)
    
    def get_system_statistics(self) -> Dict:
        """Get planetary system statistics"""
        return self.system_manager.get_system_statistics()
    
    # =================
    # CLEANUP OPERATIONS
    # =================
    
    def preview_felgenland_cleanup(self) -> Dict:
        """Preview Felgenland cleanup"""
        return self.cleanup_manager.preview_cleanup()
    
    def remove_felgenland_data(self, confirm: bool = False) -> Dict:
        """Remove all Felgenland Saga data"""
        return self.cleanup_manager.cleanup_all_felgenland_data(confirm)
    
    def selective_felgenland_cleanup(self, **kwargs) -> Dict:
        """Selective Felgenland cleanup"""
        return self.cleanup_manager.selective_cleanup(**kwargs)
    
    def get_felgenland_status(self) -> Dict:
        """Get current Felgenland data status"""
        return self.cleanup_manager.get_cleanup_status()
    
    def backup_felgenland_data(self, backup_file: str = "felgenland_backup.json") -> Dict:
        """Create backup of Felgenland data"""
        return self.cleanup_manager.create_backup(backup_file)
    
    # =================
    # BULK OPERATIONS
    # =================
    
    def bulk_add_stars(self, stars_data: List[Dict]) -> List[int]:
        """Add multiple stars"""
        return self.star_manager.add_star_batch(stars_data)
    
    def bulk_add_trade_routes(self, routes_data: List[Dict]) -> List[str]:
        """Add multiple trade routes"""
        return self.trade_route_manager.add_trade_route_batch(routes_data)
    
    def import_stars_from_csv(self, csv_file: str) -> int:
        """Import stars from CSV file"""
        return self.star_manager.import_from_csv(csv_file)
    
    def import_trade_routes_from_json(self, json_file: str) -> int:
        """Import trade routes from JSON file"""
        return self.trade_route_manager.import_from_json(json_file)
    
    def import_planetary_systems_from_dict(self, systems_dict: Dict) -> int:
        """Import planetary systems from dictionary"""
        return self.system_manager.import_from_python_dict(systems_dict)
    
    # =================
    # TEMPLATE OPERATIONS
    # =================
    
    def get_templates(self) -> Dict:
        """Get all available templates"""
        return EXAMPLE_TEMPLATES
    
    def create_from_template(self, data_type: str, template_type: str, **kwargs) -> Union[int, str]:
        """Create data from template"""
        if data_type == 'star':
            return self.add_star_from_template(template_type, **kwargs)
        elif data_type == 'nation':
            return self.add_nation_from_template(template_type, **kwargs)
        elif data_type == 'trade_route':
            return self.add_trade_route_from_template(template_type, **kwargs)
        elif data_type == 'planetary_system':
            return self.add_planetary_system_from_template(template_type, **kwargs)
        else:
            raise ValueError(f"Unknown data type: {data_type}")
    
    # =================
    # VALIDATION OPERATIONS
    # =================
    
    def validate_star_data(self, star_data: Dict) -> List[str]:
        """Validate star data"""
        return self.star_manager.validate_star_data(star_data)
    
    def validate_nation_data(self, nation_data: Dict) -> List[str]:
        """Validate nation data"""
        return self.nation_manager.validate_nation_data(nation_data)
    
    def validate_trade_route_data(self, route_data: Dict) -> List[str]:
        """Validate trade route data"""
        return self.trade_route_manager.validate_trade_route_data(route_data)
    
    def validate_planet_data(self, planet_data: Dict) -> List[str]:
        """Validate planet data"""
        return self.system_manager.validate_planet_data(planet_data)
    
    # =================
    # ANALYSIS OPERATIONS
    # =================
    
    def get_comprehensive_statistics(self) -> Dict:
        """Get comprehensive statistics for all data types"""
        return {
            'stars': self.get_star_statistics(),
            'nations': self.get_nation_statistics(),
            'trade_routes': self.get_trade_route_statistics(),
            'planetary_systems': self.get_system_statistics(),
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def analyze_galactic_situation(self) -> Dict:
        """Analyze the current galactic political and economic situation"""
        stats = self.get_comprehensive_statistics()
        
        # Calculate key metrics
        total_stars = stats['stars']['total_stars']
        controlled_stars = total_stars - stats['stars']['uncontrolled_stars']
        control_percentage = (controlled_stars / total_stars * 100) if total_stars > 0 else 0
        
        # Find dominant nation
        nation_control = stats['nations']['territory_control']
        dominant_nation = max(nation_control, key=lambda x: x['controlled_systems']) if nation_control else None
        
        # Trade network metrics
        trade_analysis = self.analyze_trade_network()
        
        return {
            'galactic_overview': {
                'total_star_systems': total_stars,
                'controlled_systems': controlled_stars,
                'control_percentage': round(control_percentage, 2),
                'independent_systems': stats['stars']['uncontrolled_stars'],
                'total_nations': stats['nations']['total_nations'],
                'active_trade_routes': stats['trade_routes']['total_routes']
            },
            'dominant_power': {
                'nation': dominant_nation['name'] if dominant_nation else None,
                'controlled_systems': dominant_nation['controlled_systems'] if dominant_nation else 0
            } if dominant_nation else None,
            'trade_network': {
                'total_routes': trade_analysis['summary']['total_routes'],
                'connected_systems': trade_analysis['summary']['total_systems'],
                'network_density': trade_analysis['summary']['network_density'],
                'hub_systems': trade_analysis['hub_systems'][:5]  # Top 5 hubs
            },
            'colonization_status': {
                'total_systems_with_planets': stats['planetary_systems']['total_systems'],
                'systems_with_life': stats['planetary_systems']['systems_with_life'],
                'colonized_systems': stats['planetary_systems']['colonized_systems'],
                'habitability_percentage': stats['planetary_systems']['habitability_percentage']
            },
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    # =================
    # UTILITY OPERATIONS
    # =================
    
    def find_connections(self, star_id: int) -> Dict:
        """Find all connections for a star (nation, trade routes, planets)"""
        connections = {
            'star': self.get_star(star_id),
            'nation': None,
            'trade_routes': [],
            'planetary_system': None
        }
        
        if not connections['star']:
            return {'error': f'Star {star_id} not found'}
        
        # Find nation control
        nation_id = connections['star'].get('nation', {}).get('id')
        if nation_id:
            connections['nation'] = self.get_nation(nation_id)
        
        # Find trade routes
        connections['trade_routes'] = self.trade_route_manager.get_routes_by_star(star_id)
        
        # Find planetary system
        connections['planetary_system'] = self.get_planetary_system(star_id)
        
        return connections
    
    def suggest_expansion_targets(self, nation_id: str, max_distance: float = 25.0) -> List[Dict]:
        """Suggest expansion targets for a nation"""
        nation = self.get_nation(nation_id)
        if not nation:
            return []
        
        # Get nation's current territories
        territories = nation.get('territories', [])
        if not territories:
            return []
        
        # Find uncontrolled stars near nation's territories
        expansion_targets = []
        
        for territory_id in territories:
            nearby_stars = self.star_manager.get_nearest_stars(
                territory_id, max_distance=max_distance, limit=20
            )
            
            for star in nearby_stars:
                # Skip if already controlled
                if star.get('nation_id'):
                    continue
                
                # Check if it's a good expansion target
                target_score = self._calculate_expansion_score(star, nation)
                
                expansion_targets.append({
                    'star_id': star['id'],
                    'name': star['name'],
                    'distance_from_territory': star['distance_from_reference'],
                    'expansion_score': target_score,
                    'reasons': self._get_expansion_reasons(star, nation)
                })
        
        # Remove duplicates and sort by score
        seen = set()
        unique_targets = []
        for target in expansion_targets:
            if target['star_id'] not in seen:
                seen.add(target['star_id'])
                unique_targets.append(target)
        
        return sorted(unique_targets, key=lambda x: x['expansion_score'], reverse=True)[:10]
    
    def export_data(self, data_type: str, output_file: str, format: str = 'json') -> Dict:
        """Export data to file"""
        try:
            if data_type == 'stars':
                if format == 'csv':
                    # Export stars to CSV
                    stats = self.get_star_statistics()
                    # This would need pandas implementation
                    return {'error': 'CSV export not implemented yet'}
                else:
                    data = self.search_stars(limit=10000)
            elif data_type == 'nations':
                data = self.list_nations()
            elif data_type == 'trade_routes':
                data = self.list_trade_routes()
            elif data_type == 'planetary_systems':
                data = self.list_planetary_systems()
            elif data_type == 'all':
                data = {
                    'stars': self.search_stars(limit=10000),
                    'nations': self.list_nations(),
                    'trade_routes': self.list_trade_routes(),
                    'planetary_systems': self.list_planetary_systems(),
                    'exported_at': datetime.utcnow().isoformat()
                }
            else:
                return {'error': f'Unknown data type: {data_type}'}
            
            # Write to file
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            return {
                'success': True,
                'output_file': output_file,
                'data_type': data_type,
                'format': format,
                'record_count': len(data) if isinstance(data, list) else 'multiple'
            }
            
        except Exception as e:
            return {'error': f'Export failed: {str(e)}'}
    
    # Private helper methods
    def _calculate_expansion_score(self, star: Dict, nation: Dict) -> float:
        """Calculate expansion score for a star"""
        score = 0.0
        
        # Brighter stars are more valuable
        magnitude = star.get('magnitude', 10)
        score += max(0, (6 - magnitude) * 0.2)
        
        # Closer stars are easier to control
        distance = star.get('distance_from_reference', 50)
        score += max(0, (50 - distance) * 0.1)
        
        # Stars with planets are more valuable
        if star.get('has_planets'):
            score += 0.5
        
        # High habitability is valuable
        habitability = star.get('habitability_score', 0)
        score += habitability * 0.3
        
        return score
    
    def _get_expansion_reasons(self, star: Dict, nation: Dict) -> List[str]:
        """Get reasons why a star is a good expansion target"""
        reasons = []
        
        if star.get('magnitude', 10) < 6:
            reasons.append('Bright, visible star')
        
        if star.get('habitability_score', 0) > 0.6:
            reasons.append('High habitability potential')
        
        if star.get('has_planets'):
            reasons.append('Has planetary system')
        
        specialties = nation.get('specialties', [])
        if 'Exploration' in specialties:
            reasons.append('Matches exploration specialty')
        
        if 'Mining' in specialties and star.get('spectral_class', '').startswith('M'):
            reasons.append('M-class star suitable for mining')
        
        return reasons


# Convenience functions for easy access
def get_data_manager() -> DataManager:
    """Get a DataManager instance"""
    return DataManager()


def quick_add_star(name: str, x: float, y: float, z: float, magnitude: float, spectral_class: str) -> int:
    """Quick function to add a basic star"""
    dm = DataManager()
    star_data = StarTemplate.create_basic_star(
        star_id=900000 + hash(name) % 100000,  # Generate unique ID
        name=name, x=x, y=y, z=z, magnitude=magnitude, spectral_class=spectral_class
    )
    return dm.add_star(star_data)


def quick_add_nation(name: str, government_type: str, capital_star_id: int) -> str:
    """Quick function to add a basic nation"""
    dm = DataManager()
    nation_data = NationTemplate.create_nation(
        nation_id=name.lower().replace(' ', '_'),
        name=name,
        full_name=f"The {name}",
        government_type=government_type,
        capital_system=f"{name} Prime",
        capital_star_id=capital_star_id,
        capital_planet="Capital World",
        established_year=2350
    )
    return dm.add_nation(nation_data)


def quick_stats() -> Dict:
    """Quick function to get basic statistics"""
    dm = DataManager()
    return dm.get_comprehensive_statistics()