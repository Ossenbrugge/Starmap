"""
MontyDB Star Model
Handles star data operations using MontyDB
"""

from typing import List, Dict, Any, Optional
from database.config import get_database
import json
import csv
import os

class StarModelDB:
    """Star data model using MontyDB"""
    
    def __init__(self):
        self.db = get_database()
        self.stars = self.db.stars
        self._cache = {}
    
    def migrate_from_json(self, data_path: str = 'data'):
        """Migrate star data from JSON files to MontyDB"""
        print("🔄 Migrating stars to MontyDB...")
        
        try:
            # Clear existing data
            self.stars.delete_many({})
            
            # Load nations for political data
            nations_lookup = {}
            try:
                with open(f'{data_path}/nations.json', 'r') as f:
                    nations = json.load(f)
                    for nation in nations:
                        nations_lookup[nation['_id']] = nation
            except Exception as e:
                print(f"Warning: Could not load nations for political data: {e}")
            
            # Load main stars from JSON
            with open(f'{data_path}/stars.json', 'r') as f:
                raw_stars = json.load(f)
                processed_stars = self._process_json_stars(raw_stars, nations_lookup)
                if processed_stars:
                    self.stars.insert_many(processed_stars)
            
            # Load fictional stars from CSV
            self._load_fictional_stars_csv(data_path, nations_lookup)
            
            count = self.stars.count_documents({})
            print(f"✅ Migrated {count} stars to MontyDB")
            
        except Exception as e:
            print(f"❌ Error migrating stars: {e}")
            raise
    
    def _process_json_stars(self, raw_stars: List[Dict], nations_lookup: Dict) -> List[Dict]:
        """Process raw JSON star data into MontyDB format"""
        processed = []
        
        for star in raw_stars:
            try:
                # Handle problematic names
                primary_name = star['names']['primary_name']
                catalog_ids = star['names'].get('catalog_ids', [])
                
                if (not primary_name or 
                    primary_name in ['nan', 'NaN', 'nan; nan', ''] or 
                    'nan' in primary_name.lower()):
                    
                    # Find a good name from catalog IDs
                    good_name = self._find_good_name(catalog_ids, star)
                    primary_name = good_name
                
                # Build MontyDB document
                doc = {
                    '_id': star['_id'],
                    'catalog_data': {
                        'hip': star['names'].get('hip'),
                        'hd': star['names'].get('hd'),
                        'catalog_ids': catalog_ids
                    },
                    'names': {
                        'primary_name': primary_name,
                        'fictional_name': star['names'].get('fictional_name'),
                        'fictional_description': star['names'].get('fictional_description'),
                        'all_names': [primary_name] + (catalog_ids or [])
                    },
                    'coordinates': {
                        'x': star['coordinates']['x'],
                        'y': star['coordinates']['y'], 
                        'z': star['coordinates']['z'],
                        'ra': star['coordinates']['ra'],
                        'dec': star['coordinates']['dec'],
                        'dist': star['coordinates']['dist']
                    },
                    'physical_properties': {
                        'magnitude': star['physical_properties']['magnitude'],
                        'spectral_class': star['physical_properties']['spectral_class'],
                        'color_index': star['physical_properties'].get('color_index', 0.0),
                        'luminosity': star['physical_properties'].get('luminosity')
                    },
                    'classification': {
                        'constellation': star['classification']['constellation'],
                        'constellation_full': star['classification']['constellation_full']
                    },
                    'exoplanets': {
                        'count': star.get('exoplanets', {}).get('count', 0),
                        'has_planets': star.get('exoplanets', {}).get('has_planets', False)
                    },
                    'is_fictional': False
                }
                
                # Add political data
                political = star.get('political', {})
                if political.get('nation_id'):
                    nation = nations_lookup.get(political['nation_id'])
                    if nation:
                        doc['political'] = {
                            'nation_id': nation['_id'],
                            'nation_name': nation['name'],
                            'strategic_importance': political.get('strategic_importance', 'normal')
                        }
                
                # Check territories
                for nation in nations_lookup.values():
                    if star['_id'] in nation.get('territories', []):
                        doc['political'] = {
                            'nation_id': nation['_id'],
                            'nation_name': nation['name'],
                            'strategic_importance': 'territory'
                        }
                        break
                
                processed.append(doc)
                
            except Exception as e:
                print(f"Warning: Error processing star {star.get('_id', 'unknown')}: {e}")
                continue
        
        return processed
    
    def _find_good_name(self, catalog_ids: List[str], star: Dict) -> str:
        """Find a good name from catalog IDs"""
        if catalog_ids:
            # Prefer proper names, then HIP, then HD, then Gliese
            for catalog_id in catalog_ids:
                if catalog_id and catalog_id != 'nan':
                    if not any(prefix in catalog_id for prefix in ['HIP ', 'HD ', 'Gliese ', 'TIC ']):
                        return catalog_id
            
            # Try HIP
            for catalog_id in catalog_ids:
                if catalog_id and catalog_id.startswith('HIP '):
                    return catalog_id
            
            # Try HD
            for catalog_id in catalog_ids:
                if catalog_id and catalog_id.startswith('HD '):
                    return catalog_id
        
        # Generate from constellation and ID
        constellation = star['classification'].get('constellation', 'Unknown')
        return f"{constellation} {star['_id']}"
    
    def _load_fictional_stars_csv(self, data_path: str, nations_lookup: Dict):
        """Load fictional stars from CSV file"""
        try:
            csv_path = f'{data_path}/fictional_stars.csv'
            if not os.path.exists(csv_path):
                return
            
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                fictional_stars = []
                
                for row in reader:
                    distance = float(row['dist'])
                    if distance > 30.0:  # Distance limit
                        continue
                    
                    doc = {
                        '_id': int(row['id']),
                        'names': {
                            'primary_name': row['proper'] if row['proper'] else f"HD {row['hd']}" if row['hd'] else f"Star {row['id']}",
                            'fictional_name': row['proper'] if row['proper'] else None,
                            'fictional_description': None,
                            'all_names': [row['proper'] if row['proper'] else f"Star {row['id']}"]
                        },
                        'coordinates': {
                            'x': float(row['x']),
                            'y': float(row['y']),
                            'z': float(row['z']),
                            'ra': float(row['ra']),
                            'dec': float(row['dec']),
                            'dist': distance
                        },
                        'physical_properties': {
                            'magnitude': float(row['mag']),
                            'spectral_class': row['spect'] if row['spect'] else 'G5V',
                            'color_index': float(row['ci']) if row['ci'] else 0.0
                        },
                        'classification': {
                            'constellation': row['con'] if row['con'] else 'Unknown',
                            'constellation_full': row['con'] if row['con'] else 'Unknown'
                        },
                        'catalog_data': {
                            'hd': row['hd'] if row['hd'] else None,
                            'catalog_ids': [row['hd']] if row['hd'] else []
                        },
                        'exoplanets': {
                            'count': 0,
                            'has_planets': False
                        },
                        'is_fictional': True
                    }
                    
                    # Add political data
                    for nation in nations_lookup.values():
                        if int(row['id']) in nation.get('territories', []):
                            doc['political'] = {
                                'nation_id': nation['_id'],
                                'nation_name': nation['name'],
                                'strategic_importance': 'territory'
                            }
                            break
                    
                    fictional_stars.append(doc)
                
                if fictional_stars:
                    self.stars.insert_many(fictional_stars)
                    print(f"✅ Loaded {len(fictional_stars)} fictional stars")
                    
        except Exception as e:
            print(f"Warning: Could not load fictional stars: {e}")
    
    def get_stars(self, limit: int = 1000, mag_limit: float = 8.0, spectral_type: str = '') -> List[Dict]:
        """Get filtered star data with distance limit"""
        distance_limit = 30.0
        
        # Build query
        query = {
            'coordinates.dist': {'$lte': distance_limit}
        }
        
        # Add spectral type filter
        if spectral_type:
            query['physical_properties.spectral_class'] = {'$regex': f'^{spectral_type}'}
        
        # For non-fictional stars, apply magnitude limit
        fictional_query = {**query, 'is_fictional': True}
        regular_query = {**query, 'is_fictional': {'$ne': True}, 'physical_properties.magnitude': {'$lte': mag_limit}}
        
        # Get fictional stars first
        fictional_stars = list(self.stars.find(fictional_query))
        
        # Get regular stars to fill remaining limit
        remaining_limit = limit - len(fictional_stars)
        regular_stars = list(self.stars.find(regular_query).limit(remaining_limit)) if remaining_limit > 0 else []
        
        return fictional_stars + regular_stars
    
    def get_star_by_id(self, star_id: int) -> Optional[Dict]:
        """Get specific star by ID"""
        return self.stars.find_one({'_id': star_id})
    
    def search_stars(self, query: str, limit: int = 20) -> List[Dict]:
        """Search stars by name"""
        if not query:
            return []
        
        search_query = {
            '$or': [
                {'names.primary_name': {'$regex': query, '$options': 'i'}},
                {'names.fictional_name': {'$regex': query, '$options': 'i'}},
                {'names.fictional_description': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        return list(self.stars.find(search_query).limit(limit))
    
    def get_stars_by_nation(self, nation_id: str) -> List[Dict]:
        """Get all stars controlled by a nation"""
        return list(self.stars.find({'political.nation_id': nation_id}))
    
    def get_stars_in_region(self, x_range: tuple, y_range: tuple, z_range: tuple) -> List[Dict]:
        """Get stars within coordinate ranges"""
        query = {
            'coordinates.x': {'$gte': x_range[0], '$lte': x_range[1]},
            'coordinates.y': {'$gte': y_range[0], '$lte': y_range[1]},
            'coordinates.z': {'$gte': z_range[0], '$lte': z_range[1]}
        }
        return list(self.stars.find(query))
    
    def add_star(self, star_data: Dict) -> bool:
        """Add a new star"""
        try:
            self.stars.insert_one(star_data)
            return True
        except Exception as e:
            print(f"Error adding star: {e}")
            return False
    
    def update_star(self, star_id: int, updates: Dict) -> bool:
        """Update star data"""
        try:
            result = self.stars.update_one({'_id': star_id}, {'$set': updates})
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating star: {e}")
            return False
    
    def clear_cache(self):
        """Clear internal cache"""
        self._cache.clear()
    
    def update_exoplanet_counts(self):
        """Update star data with exoplanet counts from exoplanet database"""
        print("🔄 Updating star exoplanet counts...")
        
        # Get exoplanet database
        exoplanets_collection = self.db.exoplanets
        fictional_exoplanets_collection = self.db.fictional_exoplanets
        
        # Get all stars
        all_stars = list(self.stars.find())
        updated_count = 0
        
        for star in all_stars:
            star_id = star['_id']
            star_name = star['names']['primary_name']
            
            # Count real exoplanets by star name
            real_exoplanet_count = exoplanets_collection.count_documents({
                'host_star.name': star_name
            })
            
            # Count fictional exoplanets by star ID
            fictional_exoplanet_count = fictional_exoplanets_collection.count_documents({
                'star_id': star_id
            })
            
            total_count = real_exoplanet_count + fictional_exoplanet_count
            has_planets = total_count > 0
            
            # Update star if counts changed
            current_count = star.get('exoplanets', {}).get('count', 0)
            current_has_planets = star.get('exoplanets', {}).get('has_planets', False)
            
            if current_count != total_count or current_has_planets != has_planets:
                self.stars.update_one(
                    {'_id': star_id},
                    {'$set': {
                        'exoplanets.count': total_count,
                        'exoplanets.has_planets': has_planets
                    }}
                )
                updated_count += 1
                
                if total_count > 0:
                    print(f"  ✅ Updated {star_name} ({star_id}): {total_count} planets")
        
        print(f"✅ Updated {updated_count} stars with exoplanet data")

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cache_size': len(self._cache),
            'total_stars': self.stars.count_documents({})
        }