"""
Nation CRUD Manager
Comprehensive functions for managing nation/political entity data
"""

import sys
import os
from typing import Dict, List, Optional, Union
from datetime import datetime

# Add database path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
from config import get_collection
from schema import NationSchema

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.nation_model_db import NationModelDB


class NationManager:
    """Comprehensive nation data management"""
    
    def __init__(self):
        self.nation_model = NationModelDB()
        self.nations_collection = get_collection('nations')
        self.stars_collection = get_collection('stars')
        self.trade_routes_collection = get_collection('trade_routes')
    
    # CREATE Operations
    def add_nation(self, nation_data: Dict) -> str:
        """Add a new nation to the database"""
        try:
            # Validate required fields
            required_fields = ['name', 'government_type', 'capital_system', 'capital_star_id']
            for field in required_fields:
                if field not in nation_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate nation ID from name if not provided
            if 'nation_id' not in nation_data:
                nation_id = nation_data['name'].lower().replace(' ', '_').replace('-', '_')
            else:
                nation_id = nation_data['nation_id']
            
            # Check if nation ID already exists
            if self.nations_collection.find_one({'_id': nation_id}):
                raise ValueError(f"Nation with ID {nation_id} already exists")
            
            # Validate capital star exists
            if not self.stars_collection.find_one({'_id': nation_data['capital_star_id']}):
                raise ValueError(f"Capital star {nation_data['capital_star_id']} does not exist")
            
            # Set defaults
            nation_data.setdefault('full_name', nation_data['name'])
            nation_data.setdefault('established_year', 2300)
            nation_data.setdefault('color', '#4CAF50')
            nation_data.setdefault('border_color', '#388E3C')
            nation_data.setdefault('description', f"The {nation_data['name']} - a {nation_data['government_type']}")
            nation_data.setdefault('territories', [nation_data['capital_star_id']])
            nation_data.setdefault('specialties', ['Trade', 'Exploration'])
            
            # Create document using schema
            nation_doc = NationSchema.create_document(nation_id, nation_data)
            
            # Insert into database
            result = self.nations_collection.insert_one(nation_doc)
            
            # Update capital star
            self._assign_capital_star(nation_id, nation_data['capital_star_id'])
            
            # Update territory stars
            for star_id in nation_data.get('territories', []):
                if star_id != nation_data['capital_star_id']:
                    self._assign_territory_star(nation_id, star_id)
            
            return nation_id
            
        except Exception as e:
            raise Exception(f"Failed to add nation: {str(e)}")
    
    def create_confederation(self, 
                           name: str,
                           member_systems: List[int],
                           capital_star_id: int,
                           specialties: List[str] = None) -> str:
        """Create a trade confederation"""
        
        if specialties is None:
            specialties = ['Trade', 'Commerce', 'Transportation']
        
        # Get capital star details
        capital_star = self.stars_collection.find_one({'_id': capital_star_id})
        if not capital_star:
            raise ValueError(f"Capital star {capital_star_id} not found")
        
        capital_system = capital_star['names']['primary_name']
        
        nation_data = {
            'name': name,
            'full_name': f"The {name} Confederation",
            'government_type': 'Trade Confederation',
            'capital_system': capital_system,
            'capital_star_id': capital_star_id,
            'capital_planet': 'Trade Hub Prime',
            'established_year': 2350,
            'color': '#4CAF50',
            'border_color': '#388E3C',
            'description': f"A peaceful trading confederation focused on {', '.join(specialties)}",
            'territories': member_systems,
            'specialties': specialties,
            'population': 'Distributed across member worlds',
            'economic_focus': 'Inter-system trade and commerce',
            'political_alignment': 'Neutral Trade Partner',
            'diplomatic_stance': 'Open Commerce'
        }
        
        return self.add_nation(nation_data)
    
    def create_exploration_coalition(self,
                                   name: str,
                                   frontier_systems: List[int],
                                   capital_star_id: int) -> str:
        """Create an exploration coalition"""
        
        # Get capital star details
        capital_star = self.stars_collection.find_one({'_id': capital_star_id})
        if not capital_star:
            raise ValueError(f"Capital star {capital_star_id} not found")
        
        capital_system = capital_star['names']['primary_name']
        
        nation_data = {
            'name': name,
            'full_name': f"The {name} Exploration Coalition",
            'government_type': 'Exploration Coalition',
            'capital_system': capital_system,
            'capital_star_id': capital_star_id,
            'capital_planet': 'Explorer Base Alpha',
            'established_year': 2360,
            'color': '#2196F3',
            'border_color': '#1976D2',
            'description': 'A coalition of explorers and scientists pushing the boundaries of known space',
            'territories': frontier_systems,
            'specialties': ['Exploration', 'Scientific Research', 'Frontier Development', 'Deep Space Survey'],
            'population': 'Mobile exploration fleets and research stations',
            'economic_focus': 'Scientific discovery and frontier development',
            'political_alignment': 'Independent Explorer Alliance',
            'diplomatic_stance': 'Peaceful Scientific Cooperation'
        }
        
        return self.add_nation(nation_data)
    
    # READ Operations
    def get_nation(self, nation_id: str) -> Optional[Dict]:
        """Get a specific nation by ID"""
        return self.nation_model.get_nation_details(nation_id)
    
    def list_nations(self, 
                    government_type: str = None,
                    established_after: int = None,
                    has_territories: bool = None) -> List[Dict]:
        """List nations with optional filters"""
        
        query = {}
        
        if government_type:
            query['government.type'] = government_type
        
        if established_after:
            query['government.established_year'] = {'$gte': established_after}
        
        if has_territories is not None:
            if has_territories:
                query['territories'] = {'$exists': True, '$ne': []}
            else:
                query['$or'] = [
                    {'territories': {'$exists': False}},
                    {'territories': {'$eq': []}}
                ]
        
        nations = list(self.nations_collection.find(query).sort('name', 1))
        return [self._format_nation_summary(nation) for nation in nations]
    
    def search_nations(self, query: str) -> List[Dict]:
        """Search nations by name or description"""
        return self.nation_model.search_nations(query)
    
    def get_nation_territories(self, nation_id: str) -> List[Dict]:
        """Get detailed information about nation's territories"""
        return self.nation_model.get_nation_territories(nation_id)
    
    def get_nation_by_capital(self, capital_star_id: int) -> Optional[Dict]:
        """Find nation by its capital star"""
        return self.nation_model.get_nation_by_capital(capital_star_id)
    
    # UPDATE Operations
    def update_nation(self, nation_id: str, update_data: Dict) -> bool:
        """Update nation information"""
        try:
            # Build update query
            update_query = {'$set': {}}
            
            # Map update fields to database structure
            field_mapping = {
                'description': 'description',
                'economic_focus': 'economy.focus',
                'military_strength': 'military.strength',
                'population': 'economy.population',
                'diplomatic_stance': 'government.diplomatic_stance',
                'political_alignment': 'government.political_alignment',
                'specialties': 'economy.specialties',
                'color': 'appearance.color',
                'border_color': 'appearance.border_color'
            }
            
            for field, db_field in field_mapping.items():
                if field in update_data:
                    update_query['$set'][db_field] = update_data[field]
            
            # Add update timestamp
            update_query['$set']['metadata.updated_at'] = datetime.utcnow()
            
            if not update_query['$set']:
                return False
            
            # Execute update
            result = self.nations_collection.update_one(
                {'_id': nation_id}, 
                update_query
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            raise Exception(f"Failed to update nation {nation_id}: {str(e)}")
    
    def add_territory(self, nation_id: str, star_id: int) -> bool:
        """Add a star system to a nation's territory"""
        try:
            # Validate nation exists
            if not self.nations_collection.find_one({'_id': nation_id}):
                raise ValueError(f"Nation {nation_id} not found")
            
            # Validate star exists
            if not self.stars_collection.find_one({'_id': star_id}):
                raise ValueError(f"Star {star_id} not found")
            
            # Check if star is already controlled by another nation
            current_nation = self.stars_collection.find_one(
                {'_id': star_id, 'political.nation_id': {'$ne': None}}
            )
            if current_nation and current_nation['political']['nation_id'] != nation_id:
                raise ValueError(f"Star {star_id} is already controlled by {current_nation['political']['nation_id']}")
            
            # Add to nation's territories
            self.nations_collection.update_one(
                {'_id': nation_id},
                {'$addToSet': {'territories': star_id}}
            )
            
            # Update star's political data
            self._assign_territory_star(nation_id, star_id)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to add territory {star_id} to nation {nation_id}: {str(e)}")
    
    def remove_territory(self, nation_id: str, star_id: int) -> bool:
        """Remove a star system from a nation's territory"""
        try:
            # Check if it's the capital
            nation = self.nations_collection.find_one({'_id': nation_id})
            if not nation:
                raise ValueError(f"Nation {nation_id} not found")
            
            if nation['capital']['star_id'] == star_id:
                raise ValueError(f"Cannot remove capital star {star_id} from nation {nation_id}")
            
            # Remove from nation's territories
            self.nations_collection.update_one(
                {'_id': nation_id},
                {'$pull': {'territories': star_id}}
            )
            
            # Update star's political data
            self._remove_star_from_nation(star_id)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to remove territory {star_id} from nation {nation_id}: {str(e)}")
    
    def change_capital(self, nation_id: str, new_capital_star_id: int, new_capital_planet: str = None) -> bool:
        """Change a nation's capital"""
        try:
            # Validate new capital star
            capital_star = self.stars_collection.find_one({'_id': new_capital_star_id})
            if not capital_star:
                raise ValueError(f"New capital star {new_capital_star_id} not found")
            
            # Get current nation data
            nation = self.nations_collection.find_one({'_id': nation_id})
            if not nation:
                raise ValueError(f"Nation {nation_id} not found")
            
            old_capital_star_id = nation['capital']['star_id']
            
            # Update nation's capital
            update_data = {
                'capital.star_id': new_capital_star_id,
                'capital.system': capital_star['names']['primary_name']
            }
            
            if new_capital_planet:
                update_data['capital.planet'] = new_capital_planet
            
            self.nations_collection.update_one(
                {'_id': nation_id},
                {'$set': update_data}
            )
            
            # Update old capital star (make it regular territory)
            self._assign_territory_star(nation_id, old_capital_star_id)
            
            # Update new capital star
            self._assign_capital_star(nation_id, new_capital_star_id)
            
            # Ensure new capital is in territories
            self.add_territory(nation_id, new_capital_star_id)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to change capital for nation {nation_id}: {str(e)}")
    
    # DELETE Operations
    def delete_nation(self, nation_id: str, transfer_territories_to: str = None) -> bool:
        """Delete a nation from the database"""
        try:
            # Get nation data
            nation = self.nations_collection.find_one({'_id': nation_id})
            if not nation:
                return False
            
            territories = nation.get('territories', [])
            
            # Handle territories
            if transfer_territories_to:
                # Transfer territories to another nation
                if not self.nations_collection.find_one({'_id': transfer_territories_to}):
                    raise ValueError(f"Target nation {transfer_territories_to} not found")
                
                for star_id in territories:
                    self.add_territory(transfer_territories_to, star_id)
            else:
                # Make territories independent
                for star_id in territories:
                    self._remove_star_from_nation(star_id)
            
            # Remove nation from trade routes
            self.trade_routes_collection.update_many(
                {'control.controlling_nation': nation_id},
                {'$set': {'control.controlling_nation': None}}
            )
            
            # Delete the nation
            result = self.nations_collection.delete_one({'_id': nation_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            raise Exception(f"Failed to delete nation {nation_id}: {str(e)}")
    
    def remove_all_felgenland_nations(self) -> List[str]:
        """Remove all Felgenland Saga nations"""
        try:
            # Define Felgenland Saga nations
            felgenland_nations = [
                'terran_directorate',
                'felgenland_union', 
                'protelani_republic',
                'dorsai_republic',
                'pentothian_trade_conglomerate'
            ]
            
            removed_nations = []
            
            for nation_id in felgenland_nations:
                try:
                    if self.delete_nation(nation_id):
                        removed_nations.append(nation_id)
                except Exception as e:
                    print(f"Warning: Could not remove nation {nation_id}: {e}")
            
            return removed_nations
            
        except Exception as e:
            raise Exception(f"Failed to remove Felgenland nations: {str(e)}")
    
    # UTILITY Functions
    def validate_nation_data(self, nation_data: Dict) -> List[str]:
        """Validate nation data and return list of errors"""
        errors = []
        
        # Check required fields
        required_fields = ['name', 'government_type', 'capital_system', 'capital_star_id']
        for field in required_fields:
            if field not in nation_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate data types
        if 'capital_star_id' in nation_data:
            if not isinstance(nation_data['capital_star_id'], int):
                errors.append("Capital star ID must be an integer")
        
        if 'established_year' in nation_data:
            if not isinstance(nation_data['established_year'], int) or nation_data['established_year'] < 2000:
                errors.append("Established year must be an integer >= 2000")
        
        if 'territories' in nation_data:
            if not isinstance(nation_data['territories'], list):
                errors.append("Territories must be a list of star IDs")
            elif not all(isinstance(t, int) for t in nation_data['territories']):
                errors.append("All territory IDs must be integers")
        
        if 'color' in nation_data:
            if not isinstance(nation_data['color'], str) or not nation_data['color'].startswith('#'):
                errors.append("Color must be a hex color string starting with #")
        
        return errors
    
    def get_nation_statistics(self) -> Dict:
        """Get comprehensive nation statistics"""
        try:
            total_nations = self.nations_collection.count_documents({})
            
            # Government type distribution
            gov_pipeline = [
                {'$group': {
                    '_id': '$government.type',
                    'count': {'$sum': 1},
                    'nations': {'$push': '$name'}
                }},
                {'$sort': {'count': -1}}
            ]
            gov_distribution = list(self.nations_collection.aggregate(gov_pipeline))
            
            # Territory control statistics
            territory_pipeline = [
                {'$project': {
                    'name': 1,
                    'territory_count': {'$size': {'$ifNull': ['$territories', []]}}
                }},
                {'$sort': {'territory_count': -1}}
            ]
            territory_stats = list(self.nations_collection.aggregate(territory_pipeline))
            
            # Establishment timeline
            timeline_pipeline = [
                {'$project': {
                    'name': 1,
                    'established_year': '$government.established_year'
                }},
                {'$sort': {'established_year': 1}}
            ]
            timeline = list(self.nations_collection.aggregate(timeline_pipeline))
            
            # Trade route control
            trade_control = {}
            for nation in self.nations_collection.find({}, {'_id': 1, 'name': 1}):
                route_count = self.trade_routes_collection.count_documents({
                    'control.controlling_nation': nation['_id']
                })
                if route_count > 0:
                    trade_control[nation['name']] = route_count
            
            return {
                'total_nations': total_nations,
                'government_distribution': gov_distribution,
                'territory_statistics': territory_stats,
                'establishment_timeline': timeline,
                'trade_route_control': trade_control,
                'largest_territory': territory_stats[0] if territory_stats else None,
                'oldest_nation': timeline[0] if timeline else None,
                'newest_nation': timeline[-1] if timeline else None
            }
            
        except Exception as e:
            raise Exception(f"Failed to get nation statistics: {str(e)}")
    
    def analyze_territorial_conflicts(self) -> List[Dict]:
        """Analyze potential territorial conflicts"""
        conflicts = []
        
        # Check for stars claimed by multiple nations
        stars_pipeline = [
            {'$match': {'political.nation_id': {'$ne': None}}},
            {'$group': {
                '_id': '$_id',
                'name': {'$first': '$names.primary_name'},
                'nation': {'$first': '$political.nation_id'},
                'importance': {'$first': '$political.strategic_importance'}
            }}
        ]
        controlled_stars = list(self.stars_collection.aggregate(stars_pipeline))
        
        # Check nation territory lists for consistency
        for nation in self.nations_collection.find({}):
            nation_id = nation['_id']
            declared_territories = set(nation.get('territories', []))
            
            # Find stars that claim to be controlled by this nation
            actual_controlled = set()
            for star in controlled_stars:
                if star['nation'] == nation_id:
                    actual_controlled.add(star['_id'])
            
            # Find mismatches
            missing_from_declaration = actual_controlled - declared_territories
            missing_from_control = declared_territories - actual_controlled
            
            if missing_from_declaration or missing_from_control:
                conflicts.append({
                    'nation_id': nation_id,
                    'nation_name': nation['name'],
                    'type': 'territory_mismatch',
                    'missing_from_declaration': list(missing_from_declaration),
                    'missing_from_control': list(missing_from_control)
                })
        
        return conflicts
    
    def fix_territorial_conflicts(self) -> int:
        """Fix territorial conflicts by synchronizing data"""
        conflicts = self.analyze_territorial_conflicts()
        fixes = 0
        
        for conflict in conflicts:
            nation_id = conflict['nation_id']
            
            # Add missing territories to nation declaration
            for star_id in conflict['missing_from_declaration']:
                self.nations_collection.update_one(
                    {'_id': nation_id},
                    {'$addToSet': {'territories': star_id}}
                )
                fixes += 1
            
            # Update star control for missing declarations
            for star_id in conflict['missing_from_control']:
                self._assign_territory_star(nation_id, star_id)
                fixes += 1
        
        return fixes
    
    # Private helper methods
    def _assign_capital_star(self, nation_id: str, star_id: int):
        """Mark a star as a nation's capital"""
        self.stars_collection.update_one(
            {'_id': star_id},
            {'$set': {
                'political.nation_id': nation_id,
                'political.controlled_by': nation_id,
                'political.capital_of': nation_id,
                'political.strategic_importance': 'capital'
            }}
        )
    
    def _assign_territory_star(self, nation_id: str, star_id: int):
        """Mark a star as controlled territory"""
        self.stars_collection.update_one(
            {'_id': star_id},
            {'$set': {
                'political.nation_id': nation_id,
                'political.controlled_by': nation_id,
                'political.strategic_importance': 'territory'
            },
            '$unset': {
                'political.capital_of': ""
            }}
        )
    
    def _remove_star_from_nation(self, star_id: int):
        """Remove nation control from a star"""
        self.stars_collection.update_one(
            {'_id': star_id},
            {'$set': {
                'political.strategic_importance': 'normal'
            },
            '$unset': {
                'political.nation_id': "",
                'political.controlled_by': "",
                'political.capital_of': ""
            }}
        )
    
    def _format_nation_summary(self, nation_doc: Dict) -> Dict:
        """Format nation document for summary display"""
        return {
            'id': nation_doc['_id'],
            'name': nation_doc['name'],
            'full_name': nation_doc['full_name'],
            'government_type': nation_doc['government']['type'],
            'established_year': nation_doc['government']['established_year'],
            'capital_system': nation_doc['capital']['system'],
            'capital_star_id': nation_doc['capital']['star_id'],
            'territory_count': len(nation_doc.get('territories', [])),
            'color': nation_doc['appearance']['color'],
            'specialties': nation_doc['economy'].get('specialties', []),
            'population': nation_doc['economy'].get('population'),
            'description': nation_doc['description']
        }