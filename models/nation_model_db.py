"""
MontyDB Nation Model
Handles nation data operations using MontyDB
"""

from typing import List, Dict, Any, Optional
from database.config import get_database
import json

class NationModelDB:
    """Nation data model using MontyDB"""
    
    def __init__(self):
        self.db = get_database()
        self.nations = self.db.nations
        self._cache = {}
    
    def migrate_from_json(self, data_path: str = 'data'):
        """Migrate nation data from JSON files to MontyDB"""
        print("🔄 Migrating nations to MontyDB...")
        
        try:
            # Clear existing data
            self.nations.delete_many({})
            
            # Load nations from JSON
            with open(f'{data_path}/nations.json', 'r') as f:
                raw_nations = json.load(f)
                
                # Convert to MontyDB format
                processed_nations = []
                for nation in raw_nations:
                    doc = {
                        '_id': nation['_id'],
                        'name': nation['name'],
                        'full_name': nation['full_name'],
                        'government': {
                            'type': nation['government']['type'],
                            'established_year': nation['government'].get('established_year'),
                            'leadership': nation['government'].get('leadership')
                        },
                        'capital': {
                            'system': nation['capital']['system'],
                            'star_id': nation['capital']['star_id'],
                            'planet': nation['capital'].get('planet')
                        },
                        'territories': nation.get('territories', []),
                        'appearance': {
                            'color': nation['appearance']['color'],
                            'border_color': nation['appearance']['border_color']
                        },
                        'economy': {
                            'focus': nation['economy'].get('focus'),
                            'specialties': nation['economy'].get('specialties', []),
                            'population': nation['economy'].get('population'),
                            'gdp': nation['economy'].get('gdp'),
                            'trade_volume': nation['economy'].get('trade_volume')
                        },
                        'military': {
                            'strength': nation.get('military', {}).get('strength'),
                            'fleet_size': nation.get('military', {}).get('fleet_size'),
                            'technology_level': nation.get('military', {}).get('technology_level')
                        },
                        'description': nation.get('description', ''),
                        'relations': nation.get('relations', {}),
                        'metadata': {
                            'created_date': nation.get('created_date'),
                            'last_updated': nation.get('last_updated')
                        }
                    }
                    processed_nations.append(doc)
                
                if processed_nations:
                    self.nations.insert_many(processed_nations)
                
                print(f"✅ Migrated {len(processed_nations)} nations to MontyDB")
                
        except Exception as e:
            print(f"❌ Error migrating nations: {e}")
            raise
    
    def get_nations(self) -> List[Dict]:
        """Get all nations with optimized format"""
        try:
            nations = []
            for nation in self.nations.find():
                nations.append({
                    'id': nation['_id'],
                    'name': nation['name'],
                    'full_name': nation['full_name'],
                    'government_type': nation['government']['type'],
                    'capital_system': nation['capital']['system'],
                    'capital_star_id': nation['capital']['star_id'],
                    'color': nation['appearance']['color'],
                    'border_color': nation['appearance']['border_color'],
                    'description': nation.get('description', ''),
                    'population': nation['economy'].get('population', 'Unknown'),
                    'specialties': nation['economy'].get('specialties', []),
                    'territory_count': len(nation.get('territories', []))
                })
            return nations
        except Exception as e:
            print(f"Error getting nations: {e}")
            return []
    
    def get_nation_by_id(self, nation_id: str) -> Optional[Dict]:
        """Get specific nation by ID"""
        return self.nations.find_one({'_id': nation_id})
    
    def get_nation_territories(self, nation_id: str) -> List[int]:
        """Get list of star IDs controlled by nation"""
        nation = self.nations.find_one({'_id': nation_id})
        return nation.get('territories', []) if nation else []
    
    def add_territory(self, nation_id: str, star_id: int) -> bool:
        """Add a star to nation's territories"""
        try:
            result = self.nations.update_one(
                {'_id': nation_id},
                {'$addToSet': {'territories': star_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error adding territory: {e}")
            return False
    
    def remove_territory(self, nation_id: str, star_id: int) -> bool:
        """Remove a star from nation's territories"""
        try:
            result = self.nations.update_one(
                {'_id': nation_id},
                {'$pull': {'territories': star_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error removing territory: {e}")
            return False
    
    def search_nations(self, query: str, limit: int = 10) -> List[Dict]:
        """Search nations by name"""
        if not query:
            return []
        
        search_query = {
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'full_name': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        return list(self.nations.find(search_query).limit(limit))
    
    def get_nation_stats(self) -> Dict:
        """Get statistics about nations"""
        try:
            total_nations = self.nations.count_documents({})
            
            # Get territory counts using basic queries since aggregate is not supported
            all_nations = list(self.nations.find())
            territory_counts = []
            total_territories = 0
            
            for nation in all_nations:
                territory_count = len(nation.get('territories', []))
                territory_counts.append(territory_count)
                total_territories += territory_count
            
            # Calculate statistics
            avg_territories = round(total_territories / total_nations, 2) if total_nations > 0 else 0
            max_territories = max(territory_counts) if territory_counts else 0
            
            stats = {
                'total_nations': total_nations,
                'total_territories': total_territories,
                'avg_territories': avg_territories,
                'max_territories': max_territories
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting nation stats: {e}")
            return {
                'total_nations': 0,
                'total_territories': 0,
                'avg_territories': 0,
                'max_territories': 0
            }
    
    def add_nation(self, nation_data: Dict) -> bool:
        """Add a new nation"""
        try:
            self.nations.insert_one(nation_data)
            return True
        except Exception as e:
            print(f"Error adding nation: {e}")
            return False
    
    def update_nation(self, nation_id: str, updates: Dict) -> bool:
        """Update nation data"""
        try:
            result = self.nations.update_one({'_id': nation_id}, {'$set': updates})
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating nation: {e}")
            return False
    
    def clear_cache(self):
        """Clear internal cache"""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cache_size': len(self._cache),
            'total_nations': self.nations.count_documents({})
        }