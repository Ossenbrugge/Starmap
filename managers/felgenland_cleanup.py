"""
Felgenland Saga Data Cleanup
Functions to remove all Felgenland Saga-related data from the database
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

# Add database path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
from config import get_collection

# Import managers
from star_manager import StarManager
from nation_manager import NationManager
from trade_route_manager import TradeRouteManager
from planetary_system_manager import PlanetarySystemManager


class FelgenlandCleanup:
    """Complete cleanup of Felgenland Saga data"""
    
    def __init__(self):
        self.star_manager = StarManager()
        self.nation_manager = NationManager()
        self.trade_route_manager = TradeRouteManager()
        self.system_manager = PlanetarySystemManager()
        
        # Define Felgenland Saga data identifiers
        self.felgenland_nations = [
            'terran_directorate',
            'felgenland_union',
            'protelani_republic',
            'dorsai_republic',
            'pentothian_trade_conglomerate'
        ]
        
        self.felgenland_stars = [
            0,        # Sol
            71456,    # Alpha Centauri A
            71453,    # Alpha Centauri B
            70666,    # Proxima Centauri
            53879,    # Lalande 21185
            118720,   # Wolf 359
            48941,    # Holsten Tor (Stahlburgh)
            32263,    # Sirius
            999999    # Tiefe-Grenze Tor
        ]
        
        self.cleanup_log = []
    
    def cleanup_all_felgenland_data(self, confirm: bool = False) -> Dict:
        """Remove all Felgenland Saga data from the database"""
        
        if not confirm:
            return {
                'error': 'Cleanup not confirmed. Set confirm=True to proceed.',
                'warning': 'This will permanently delete all Felgenland Saga data including:'
                          ' nations, trade routes, planetary systems, and fictional star data.'
            }
        
        try:
            cleanup_results = {
                'start_time': datetime.utcnow(),
                'nations_removed': 0,
                'trade_routes_removed': 0,
                'planetary_systems_removed': 0,
                'fictional_stars_cleaned': 0,
                'errors': [],
                'warnings': []
            }
            
            self.cleanup_log.append("Starting Felgenland Saga cleanup...")
            
            # Step 1: Remove trade routes
            try:
                routes_removed = self.trade_route_manager.remove_all_felgenland_routes()
                cleanup_results['trade_routes_removed'] = routes_removed
                self.cleanup_log.append(f"Removed {routes_removed} trade routes")
            except Exception as e:
                cleanup_results['errors'].append(f"Trade route cleanup failed: {str(e)}")
            
            # Step 2: Remove nations
            try:
                nations_removed = self.nation_manager.remove_all_felgenland_nations()
                cleanup_results['nations_removed'] = len(nations_removed)
                self.cleanup_log.append(f"Removed nations: {', '.join(nations_removed)}")
            except Exception as e:
                cleanup_results['errors'].append(f"Nation cleanup failed: {str(e)}")
            
            # Step 3: Remove planetary systems
            try:
                systems_removed = self.system_manager.remove_all_felgenland_systems()
                cleanup_results['planetary_systems_removed'] = systems_removed
                self.cleanup_log.append(f"Removed {systems_removed} planetary systems")
            except Exception as e:
                cleanup_results['errors'].append(f"Planetary system cleanup failed: {str(e)}")
            
            # Step 4: Clean fictional star data
            try:
                fictional_cleaned = self._clean_fictional_star_data()
                cleanup_results['fictional_stars_cleaned'] = fictional_cleaned
                self.cleanup_log.append(f"Cleaned fictional data from {fictional_cleaned} stars")
            except Exception as e:
                cleanup_results['errors'].append(f"Fictional star cleanup failed: {str(e)}")
            
            # Step 5: Remove specific fictional stars
            try:
                fictional_stars_removed = self._remove_fictional_stars()
                cleanup_results['fictional_stars_removed'] = fictional_stars_removed
                self.cleanup_log.append(f"Removed {fictional_stars_removed} fictional stars")
            except Exception as e:
                cleanup_results['errors'].append(f"Fictional star removal failed: {str(e)}")
            
            cleanup_results['end_time'] = datetime.utcnow()
            cleanup_results['duration'] = (cleanup_results['end_time'] - cleanup_results['start_time']).total_seconds()
            cleanup_results['success'] = len(cleanup_results['errors']) == 0
            cleanup_results['cleanup_log'] = self.cleanup_log
            
            # Final verification
            verification = self._verify_cleanup()
            cleanup_results['verification'] = verification
            
            return cleanup_results
            
        except Exception as e:
            return {
                'error': f"Cleanup failed: {str(e)}",
                'cleanup_log': self.cleanup_log
            }
    
    def preview_cleanup(self) -> Dict:
        """Preview what would be removed without actually deleting anything"""
        preview = {
            'nations_to_remove': [],
            'trade_routes_to_remove': [],
            'planetary_systems_to_remove': [],
            'stars_to_modify': [],
            'fictional_stars_to_remove': []
        }
        
        try:
            # Preview nations
            for nation_id in self.felgenland_nations:
                nation = self.nation_manager.get_nation(nation_id)
                if nation:
                    preview['nations_to_remove'].append({
                        'id': nation_id,
                        'name': nation['name'],
                        'territories': len(nation.get('territories', [])),
                        'trade_routes': len(nation.get('trade_routes', []))
                    })
            
            # Preview trade routes
            for nation_id in self.felgenland_nations:
                routes = self.trade_route_manager.get_routes_by_nation(nation_id)
                for route in routes:
                    preview['trade_routes_to_remove'].append({
                        'id': route['id'],
                        'name': route['name'],
                        'route_type': route['route_type'],
                        'controlling_nation': route['controlling_nation']
                    })
            
            # Preview planetary systems
            for star_id in self.felgenland_stars:
                system = self.system_manager.get_planetary_system(star_id)
                if system:
                    preview['planetary_systems_to_remove'].append({
                        'star_id': star_id,
                        'system_name': system['system_name'],
                        'total_planets': system['total_planets'],
                        'has_life': system['has_life']
                    })
            
            # Preview stars with fictional data
            stars_collection = get_collection('stars')
            fictional_stars = list(stars_collection.find({
                'names.fictional_name': {'$ne': None}
            }, {'_id': 1, 'names.primary_name': 1, 'names.fictional_name': 1}))
            
            for star in fictional_stars:
                preview['stars_to_modify'].append({
                    'star_id': star['_id'],
                    'name': star['names']['primary_name'],
                    'fictional_name': star['names']['fictional_name']
                })
            
            # Preview fictional stars to remove completely
            for star_id in [999999]:  # Tiefe-Grenze Tor and other fully fictional stars
                star = self.star_manager.get_star(star_id)
                if star:
                    preview['fictional_stars_to_remove'].append({
                        'star_id': star_id,
                        'name': star['name'],
                        'fictional_name': star.get('fictional_name')
                    })
            
            return preview
            
        except Exception as e:
            return {'error': f"Preview failed: {str(e)}"}
    
    def selective_cleanup(self, 
                         remove_nations: bool = True,
                         remove_trade_routes: bool = True,
                         remove_planetary_systems: bool = True,
                         clean_fictional_data: bool = True,
                         remove_fictional_stars: bool = False) -> Dict:
        """Selective cleanup allowing user to choose what to remove"""
        
        results = {
            'operations': [],
            'errors': [],
            'summary': {}
        }
        
        try:
            if remove_trade_routes:
                try:
                    routes_removed = self.trade_route_manager.remove_all_felgenland_routes()
                    results['operations'].append(f"Removed {routes_removed} trade routes")
                    results['summary']['trade_routes_removed'] = routes_removed
                except Exception as e:
                    results['errors'].append(f"Trade route cleanup failed: {str(e)}")
            
            if remove_nations:
                try:
                    nations_removed = self.nation_manager.remove_all_felgenland_nations()
                    results['operations'].append(f"Removed {len(nations_removed)} nations: {', '.join(nations_removed)}")
                    results['summary']['nations_removed'] = len(nations_removed)
                except Exception as e:
                    results['errors'].append(f"Nation cleanup failed: {str(e)}")
            
            if remove_planetary_systems:
                try:
                    systems_removed = self.system_manager.remove_all_felgenland_systems()
                    results['operations'].append(f"Removed {systems_removed} planetary systems")
                    results['summary']['planetary_systems_removed'] = systems_removed
                except Exception as e:
                    results['errors'].append(f"Planetary system cleanup failed: {str(e)}")
            
            if clean_fictional_data:
                try:
                    fictional_cleaned = self._clean_fictional_star_data()
                    results['operations'].append(f"Cleaned fictional data from {fictional_cleaned} stars")
                    results['summary']['fictional_stars_cleaned'] = fictional_cleaned
                except Exception as e:
                    results['errors'].append(f"Fictional star cleanup failed: {str(e)}")
            
            if remove_fictional_stars:
                try:
                    fictional_removed = self._remove_fictional_stars()
                    results['operations'].append(f"Removed {fictional_removed} fictional stars")
                    results['summary']['fictional_stars_removed'] = fictional_removed
                except Exception as e:
                    results['errors'].append(f"Fictional star removal failed: {str(e)}")
            
            results['success'] = len(results['errors']) == 0
            return results
            
        except Exception as e:
            results['errors'].append(f"Selective cleanup failed: {str(e)}")
            return results
    
    def restore_backup(self, backup_file: str) -> Dict:
        """Restore data from backup file (if available)"""
        try:
            import json
            
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            restored = {
                'nations': 0,
                'trade_routes': 0,
                'planetary_systems': 0,
                'stars': 0,
                'errors': []
            }
            
            # Restore nations
            if 'nations' in backup_data:
                for nation_data in backup_data['nations']:
                    try:
                        self.nation_manager.add_nation(nation_data)
                        restored['nations'] += 1
                    except Exception as e:
                        restored['errors'].append(f"Nation restore failed: {str(e)}")
            
            # Restore trade routes
            if 'trade_routes' in backup_data:
                for route_data in backup_data['trade_routes']:
                    try:
                        self.trade_route_manager.add_trade_route(route_data)
                        restored['trade_routes'] += 1
                    except Exception as e:
                        restored['errors'].append(f"Trade route restore failed: {str(e)}")
            
            # Restore planetary systems
            if 'planetary_systems' in backup_data:
                for system_data in backup_data['planetary_systems']:
                    try:
                        self.system_manager.add_planetary_system(system_data)
                        restored['planetary_systems'] += 1
                    except Exception as e:
                        restored['errors'].append(f"Planetary system restore failed: {str(e)}")
            
            # Restore stars
            if 'stars' in backup_data:
                for star_data in backup_data['stars']:
                    try:
                        self.star_manager.add_star(star_data)
                        restored['stars'] += 1
                    except Exception as e:
                        restored['errors'].append(f"Star restore failed: {str(e)}")
            
            return restored
            
        except Exception as e:
            return {'error': f"Backup restore failed: {str(e)}"}
    
    def create_backup(self, backup_file: str) -> Dict:
        """Create backup of Felgenland data before cleanup"""
        try:
            import json
            
            backup_data = {
                'created_at': datetime.utcnow().isoformat(),
                'nations': [],
                'trade_routes': [],
                'planetary_systems': [],
                'fictional_stars': []
            }
            
            # Backup nations
            for nation_id in self.felgenland_nations:
                nation = self.nation_manager.get_nation(nation_id)
                if nation:
                    backup_data['nations'].append(nation)
            
            # Backup trade routes
            for nation_id in self.felgenland_nations:
                routes = self.trade_route_manager.get_routes_by_nation(nation_id)
                backup_data['trade_routes'].extend(routes)
            
            # Backup planetary systems
            for star_id in self.felgenland_stars:
                system = self.system_manager.get_planetary_system(star_id)
                if system:
                    backup_data['planetary_systems'].append(system)
            
            # Backup fictional stars
            stars_collection = get_collection('stars')
            fictional_stars = list(stars_collection.find({
                'names.fictional_name': {'$ne': None}
            }))
            backup_data['fictional_stars'] = fictional_stars
            
            # Write backup file
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            return {
                'success': True,
                'backup_file': backup_file,
                'nations_backed_up': len(backup_data['nations']),
                'trade_routes_backed_up': len(backup_data['trade_routes']),
                'planetary_systems_backed_up': len(backup_data['planetary_systems']),
                'fictional_stars_backed_up': len(backup_data['fictional_stars'])
            }
            
        except Exception as e:
            return {'error': f"Backup creation failed: {str(e)}"}
    
    # Private helper methods
    def _clean_fictional_star_data(self) -> int:
        """Remove fictional names and descriptions from stars"""
        try:
            stars_collection = get_collection('stars')
            
            # Remove fictional data from all stars
            result = stars_collection.update_many(
                {},
                {
                    '$unset': {
                        'names.fictional_name': "",
                        'names.fictional_source': "",
                        'names.fictional_description': ""
                    },
                    '$set': {
                        'metadata.updated_at': datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count
            
        except Exception as e:
            raise Exception(f"Failed to clean fictional star data: {str(e)}")
    
    def _remove_fictional_stars(self) -> int:
        """Remove completely fictional stars (not based on real catalog data)"""
        try:
            # Remove Tiefe-Grenze Tor and other fully fictional stars
            fictional_star_ids = [999999]  # Add more fictional star IDs as needed
            
            removed_count = 0
            for star_id in fictional_star_ids:
                try:
                    if self.star_manager.delete_star(star_id, force=True):
                        removed_count += 1
                except Exception as e:
                    self.cleanup_log.append(f"Warning: Could not remove fictional star {star_id}: {e}")
            
            return removed_count
            
        except Exception as e:
            raise Exception(f"Failed to remove fictional stars: {str(e)}")
    
    def _verify_cleanup(self) -> Dict:
        """Verify that cleanup was successful"""
        verification = {
            'remaining_nations': 0,
            'remaining_trade_routes': 0,
            'remaining_planetary_systems': 0,
            'remaining_fictional_data': 0,
            'warnings': []
        }
        
        try:
            # Check for remaining nations
            for nation_id in self.felgenland_nations:
                if self.nation_manager.get_nation(nation_id):
                    verification['remaining_nations'] += 1
                    verification['warnings'].append(f"Nation {nation_id} still exists")
            
            # Check for remaining trade routes
            for nation_id in self.felgenland_nations:
                routes = self.trade_route_manager.get_routes_by_nation(nation_id)
                if routes:
                    verification['remaining_trade_routes'] += len(routes)
                    verification['warnings'].append(f"Nation {nation_id} still has {len(routes)} trade routes")
            
            # Check for remaining planetary systems
            for star_id in self.felgenland_stars:
                if self.system_manager.get_planetary_system(star_id):
                    verification['remaining_planetary_systems'] += 1
                    verification['warnings'].append(f"Planetary system {star_id} still exists")
            
            # Check for remaining fictional data
            stars_collection = get_collection('stars')
            fictional_count = stars_collection.count_documents({
                'names.fictional_name': {'$ne': None}
            })
            verification['remaining_fictional_data'] = fictional_count
            
            if fictional_count > 0:
                verification['warnings'].append(f"{fictional_count} stars still have fictional data")
            
            verification['cleanup_successful'] = (
                verification['remaining_nations'] == 0 and
                verification['remaining_trade_routes'] == 0 and
                verification['remaining_planetary_systems'] == 0 and
                verification['remaining_fictional_data'] == 0
            )
            
            return verification
            
        except Exception as e:
            verification['error'] = f"Verification failed: {str(e)}"
            return verification
    
    def get_cleanup_status(self) -> Dict:
        """Get current status of Felgenland data in database"""
        try:
            status = {
                'nations_present': [],
                'trade_routes_count': 0,
                'planetary_systems_count': 0,
                'fictional_stars_count': 0,
                'controlled_stars_count': 0
            }
            
            # Check nations
            for nation_id in self.felgenland_nations:
                nation = self.nation_manager.get_nation(nation_id)
                if nation:
                    status['nations_present'].append({
                        'id': nation_id,
                        'name': nation['name'],
                        'territories': len(nation.get('territories', []))
                    })
            
            # Count trade routes
            for nation_id in self.felgenland_nations:
                routes = self.trade_route_manager.get_routes_by_nation(nation_id)
                status['trade_routes_count'] += len(routes)
            
            # Count planetary systems
            for star_id in self.felgenland_stars:
                if self.system_manager.get_planetary_system(star_id):
                    status['planetary_systems_count'] += 1
            
            # Count fictional stars
            stars_collection = get_collection('stars')
            status['fictional_stars_count'] = stars_collection.count_documents({
                'names.fictional_name': {'$ne': None}
            })
            
            # Count controlled stars
            status['controlled_stars_count'] = stars_collection.count_documents({
                'political.nation_id': {'$in': self.felgenland_nations}
            })
            
            status['has_felgenland_data'] = (
                len(status['nations_present']) > 0 or
                status['trade_routes_count'] > 0 or
                status['planetary_systems_count'] > 0 or
                status['fictional_stars_count'] > 0
            )
            
            return status
            
        except Exception as e:
            return {'error': f"Status check failed: {str(e)}"}


# Convenience functions for easy access
def preview_felgenland_cleanup() -> Dict:
    """Quick preview of what would be cleaned up"""
    cleanup = FelgenlandCleanup()
    return cleanup.preview_cleanup()


def remove_all_felgenland_data(confirm: bool = False) -> Dict:
    """Remove all Felgenland Saga data"""
    cleanup = FelgenlandCleanup()
    return cleanup.cleanup_all_felgenland_data(confirm=confirm)


def get_felgenland_status() -> Dict:
    """Get current status of Felgenland data"""
    cleanup = FelgenlandCleanup()
    return cleanup.get_cleanup_status()


def backup_felgenland_data(backup_file: str = "felgenland_backup.json") -> Dict:
    """Create backup of Felgenland data"""
    cleanup = FelgenlandCleanup()
    return cleanup.create_backup(backup_file)