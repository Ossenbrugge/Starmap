"""
Streamlined Database Model for Starmap V2
Uses direct JSON file access with caching for optimal performance
"""

import json
import os
import csv
from typing import List, Dict, Any, Optional

class Database:
    """Lightweight database interface using JSON files with smart caching"""
    
    def __init__(self, data_path: str = '../starmap_db_backup/starmap'):
        self.data_path = data_path
        self._cache = {}
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all data into memory cache for fast access"""
        print("📊 Loading database into memory...")
        
        try:
            # Load nations first (needed for political data)
            with open(f'{self.data_path}/nations.json', 'r') as f:
                self._cache['nations'] = json.load(f)
            
            # Load stars
            with open(f'{self.data_path}/stars.json', 'r') as f:
                raw_stars = json.load(f)
                self._cache['stars'] = self._process_stars(raw_stars)
            
            # Load fictional stars from CSV
            self._load_fictional_stars()
            
            # Load fictional exoplanets from CSV
            self._load_fictional_exoplanets()
            
            # Load trade routes
            with open(f'{self.data_path}/trade_routes.json', 'r') as f:
                self._cache['trade_routes'] = json.load(f)
            
            # Load exoplanets
            with open(f'{self.data_path}/exoplanets.json', 'r') as f:
                self._cache['exoplanets'] = json.load(f)
            
            print(f"✅ Loaded {len(self._cache['stars'])} stars, {len(self._cache['nations'])} nations, {len(self._cache['trade_routes'])} trade routes")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self._cache = {'stars': [], 'nations': [], 'trade_routes': [], 'exoplanets': []}
    
    def _load_fictional_stars(self):
        """Load fictional stars from CSV file"""
        try:
            fictional_csv_path = '../fictional_stars.csv'
            if os.path.exists(fictional_csv_path):
                with open(fictional_csv_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Convert CSV row to star format
                        fictional_star = {
                            'id': int(row['id']),
                            'name': row['proper'] if row['proper'] else f"HD {row['hd']}" if row['hd'] else f"Star {row['id']}",
                            'fictional_name': row['proper'] if row['proper'] else None,
                            'fictional_description': None,
                            'x': float(row['x']),
                            'y': float(row['y']),
                            'z': float(row['z']),
                            'ra': float(row['ra']),
                            'dec': float(row['dec']),
                            'distance': float(row['dist']),
                            'magnitude': float(row['mag']),
                            'spectral_class': row['spect'] if row['spect'] else 'G5V',
                            'color_index': float(row['ci']) if row['ci'] else 0.0,
                            'constellation': row['con'] if row['con'] else 'Unknown',
                            'constellation_full': row['con'] if row['con'] else 'Unknown',
                            'catalog_ids': [row['hd']] if row['hd'] else [],
                            'exoplanet_count': 0,
                            'has_planets': False,
                            'is_fictional': True
                        }
                        
                        # Add political data from nations
                        self._add_political_data(fictional_star)
                        
                        # Add to cache
                        self._cache['stars'].append(fictional_star)
                        
            # Add additional fictional stars that don't exist in the database
            additional_fictional_stars = [
                {
                    'id': 52409,
                    'name': 'Gj 380',
                    'fictional_name': 'Gj 380',
                    'fictional_description': 'Pentothia Prime - Neutral trading center controlled by reptilian merchants.',
                    'x': 15.2,
                    'y': -8.4,
                    'z': 12.7,
                    'ra': 200.5,
                    'dec': -25.3,
                    'distance': 22.1,
                    'magnitude': 8.2,
                    'spectral_class': 'K2V',
                    'color_index': 0.9,
                    'constellation': 'Cen',
                    'constellation_full': 'Centaurus',
                    'catalog_ids': [],
                    'exoplanet_count': 0,
                    'has_planets': False,
                    'is_fictional': True
                }
            ]
            
            for star in additional_fictional_stars:
                # Add political data from nations
                self._add_political_data(star)
                # Add to cache
                self._cache['stars'].append(star)
                        
            print(f"✅ Loaded {len([s for s in self._cache['stars'] if s.get('is_fictional', False) or s['id'] >= 999999])} fictional stars")
        except Exception as e:
            print(f"Warning: Could not load fictional stars: {e}")
            
    def _load_fictional_exoplanets(self):
        """Load fictional exoplanets from CSV file"""
        try:
            exoplanet_csv_path = '../exoplanet_catalog_20250715_114843.csv'
            fictional_planets = []
            
            if os.path.exists(exoplanet_csv_path):
                with open(exoplanet_csv_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            star_id = int(row['star_id']) if row['star_id'] and row['star_id'] != 'nan' else None
                            if star_id:
                                planet = {
                                    'id': f"{star_id}_{row['pl_letter']}",
                                    'name': row['pl_name'],
                                    'star_id': star_id,
                                    'host_star': row['hostname'],
                                    'orbital_period': float(row['orbital_period_days']) if row['orbital_period_days'] else None,
                                    'semi_major_axis': float(row['semi_major_axis_au']) if row['semi_major_axis_au'] else None,
                                    'planet_radius_earth': float(row['planet_radius_earth']) if row['planet_radius_earth'] else None,
                                    'planet_mass_earth': float(row['planet_mass_earth']) if row['planet_mass_earth'] else None,
                                    'equilibrium_temperature': float(row['equilibrium_temperature_k']) if row['equilibrium_temperature_k'] else None,
                                    'discovery_year': int(row['discovery_year']) if row['discovery_year'] else None,
                                    'discovery_method': row['discovery_method'],
                                    'potentially_habitable': row['potentially_habitable'] == 'True',
                                    'host_distance_pc': float(row['host_distance_pc']) if row['host_distance_pc'] else None,
                                    'is_fictional': True
                                }
                                fictional_planets.append(planet)
                                
                                # Update the star's exoplanet count
                                for star in self._cache['stars']:
                                    if star['id'] == star_id:
                                        star['exoplanet_count'] = star.get('exoplanet_count', 0) + 1
                                        star['has_planets'] = True
                                        break
                        except (ValueError, KeyError) as e:
                            continue  # Skip invalid rows
            
            # Add Solar System planets
            solar_system_planets = [
                {
                    'id': '500000_mercury',
                    'name': 'Mercury',
                    'star_id': 500000,
                    'host_star': 'Sol',
                    'orbital_period': 87.97,
                    'semi_major_axis': 0.39,
                    'planet_radius_earth': 0.38,
                    'planet_mass_earth': 0.055,
                    'equilibrium_temperature': 340,
                    'discovery_year': None,
                    'discovery_method': 'Historical',
                    'potentially_habitable': False,
                    'host_distance_pc': 0.0,
                    'is_fictional': True
                },
                {
                    'id': '500000_venus',
                    'name': 'Venus',
                    'star_id': 500000,
                    'host_star': 'Sol',
                    'orbital_period': 224.7,
                    'semi_major_axis': 0.72,
                    'planet_radius_earth': 0.95,
                    'planet_mass_earth': 0.82,
                    'equilibrium_temperature': 737,
                    'discovery_year': None,
                    'discovery_method': 'Historical',
                    'potentially_habitable': False,
                    'host_distance_pc': 0.0,
                    'is_fictional': True
                },
                {
                    'id': '500000_earth',
                    'name': 'Earth',
                    'star_id': 500000,
                    'host_star': 'Sol',
                    'orbital_period': 365.25,
                    'semi_major_axis': 1.0,
                    'planet_radius_earth': 1.0,
                    'planet_mass_earth': 1.0,
                    'equilibrium_temperature': 288,
                    'discovery_year': None,
                    'discovery_method': 'Historical',
                    'potentially_habitable': True,
                    'host_distance_pc': 0.0,
                    'is_fictional': True
                },
                {
                    'id': '500000_mars',
                    'name': 'Mars',
                    'star_id': 500000,
                    'host_star': 'Sol',
                    'orbital_period': 687.0,
                    'semi_major_axis': 1.52,
                    'planet_radius_earth': 0.53,
                    'planet_mass_earth': 0.11,
                    'equilibrium_temperature': 210,
                    'discovery_year': None,
                    'discovery_method': 'Historical',
                    'potentially_habitable': False,
                    'host_distance_pc': 0.0,
                    'is_fictional': True
                },
                {
                    'id': '500000_jupiter',
                    'name': 'Jupiter',
                    'star_id': 500000,
                    'host_star': 'Sol',
                    'orbital_period': 4333.0,
                    'semi_major_axis': 5.2,
                    'planet_radius_earth': 11.2,
                    'planet_mass_earth': 318.0,
                    'equilibrium_temperature': 165,
                    'discovery_year': None,
                    'discovery_method': 'Historical',
                    'potentially_habitable': False,
                    'host_distance_pc': 0.0,
                    'is_fictional': True
                },
                {
                    'id': '500000_saturn',
                    'name': 'Saturn',
                    'star_id': 500000,
                    'host_star': 'Sol',
                    'orbital_period': 10759.0,
                    'semi_major_axis': 9.5,
                    'planet_radius_earth': 9.4,
                    'planet_mass_earth': 95.2,
                    'equilibrium_temperature': 134,
                    'discovery_year': None,
                    'discovery_method': 'Historical',
                    'potentially_habitable': False,
                    'host_distance_pc': 0.0,
                    'is_fictional': True
                },
                {
                    'id': '500000_uranus',
                    'name': 'Uranus',
                    'star_id': 500000,
                    'host_star': 'Sol',
                    'orbital_period': 30687.0,
                    'semi_major_axis': 19.2,
                    'planet_radius_earth': 4.0,
                    'planet_mass_earth': 14.5,
                    'equilibrium_temperature': 76,
                    'discovery_year': 1781,
                    'discovery_method': 'Historical',
                    'potentially_habitable': False,
                    'host_distance_pc': 0.0,
                    'is_fictional': True
                },
                {
                    'id': '500000_neptune',
                    'name': 'Neptune',
                    'star_id': 500000,
                    'host_star': 'Sol',
                    'orbital_period': 60190.0,
                    'semi_major_axis': 30.1,
                    'planet_radius_earth': 3.9,
                    'planet_mass_earth': 17.1,
                    'equilibrium_temperature': 72,
                    'discovery_year': 1846,
                    'discovery_method': 'Historical',
                    'potentially_habitable': False,
                    'host_distance_pc': 0.0,
                    'is_fictional': True
                }
            ]
            
            fictional_planets.extend(solar_system_planets)
            
            # Update Sol's exoplanet count
            for star in self._cache['stars']:
                if star['id'] == 500000:
                    star['exoplanet_count'] = star.get('exoplanet_count', 0) + len(solar_system_planets)
                    star['has_planets'] = True
                    break
                
            self._cache['fictional_exoplanets'] = fictional_planets
            print(f"✅ Loaded {len(fictional_planets)} fictional exoplanets")
        except Exception as e:
            print(f"Warning: Could not load fictional exoplanets: {e}")
            self._cache['fictional_exoplanets'] = []
    
    def _add_political_data(self, star):
        """Add political data to a star based on nations territories"""
        try:
            nations_lookup = {}
            
            # Create nations lookup
            for nation in self._cache.get('nations', []):
                nations_lookup[nation['_id']] = nation
            
            # Check if this star is in any nation's territories
            for nation in nations_lookup.values():
                if star['id'] in nation.get('territories', []):
                    star['nation'] = {
                        'id': nation['_id'],
                        'name': nation['name'],
                        'color': nation['appearance']['color'],
                        'capital_system': nation['capital']['system']
                    }
                    star['strategic_importance'] = 'territory'
                    break
        except Exception as e:
            pass  # Ignore errors in political data assignment
    
    def _process_stars(self, raw_stars: List[Dict]) -> List[Dict]:
        """Process and optimize star data"""
        processed = []
        nations_lookup = {}
        
        # Create nations lookup for faster access
        try:
            with open(f'{self.data_path}/nations.json', 'r') as f:
                nations = json.load(f)
                for nation in nations:
                    nations_lookup[nation['_id']] = nation
        except:
            pass
        
        for star in raw_stars:
            try:
                # Extract essential data
                # Add some fictional names for key systems
                fictional_names = {
                    113008: {'name': 'Valorgram', 'desc': 'Military capital of the Dorsai Republic, home to the legendary Citadel of Valoro.'},
                    56828: {'name': 'Protelan Hub', 'desc': 'Ultra-capitalist trade hub of the Protelani Republic.'},
                    52409: {'name': 'Gj 380', 'desc': 'Pentothia Prime - Neutral trading center controlled by reptilian merchants.'},
                    32263: {'name': 'Sirius Gate', 'desc': 'Major industrial and administrative hub.'},
                    71456: {'name': 'Centauri Station', 'desc': 'Administrative center of the Terran Directorate.'},
                    999999: {'name': 'Tiefe-Grenze Tor', 'desc': 'Deep frontier gateway system of the Felgenland Union, monitoring the outer boundaries of human space.'},
                    0: {'name': 'Sol Central', 'desc': 'The heart of human civilization and seat of the Terran Directorate.'},
                    48941: {'name': 'Holsten Tor', 'desc': 'Capital of the Felgenland Union, known for its Eclipse Festivals.'},
                    46945: {'name': 'Brandenburgh Tor', 'desc': 'Manufacturing hub of the Felgenland Union.'},
                    43464: {'name': 'Griefen Tor', 'desc': 'Resource extraction center of the Felgenland Union.'},
                    115218: {'name': 'Tiefe-Grenze Tor Outpost', 'desc': 'Frontier outpost of the Felgenland Union.'},
                    74766: {'name': 'Gliese Station', 'desc': 'Remote frontier trading post.'},
                    53879: {'name': 'Lalande Colony', 'desc': 'Terran colonial outpost.'},
                    70666: {'name': 'Proxima Base', 'desc': 'Terran frontier military base.'},
                    71453: {'name': 'Alpha Centauri B Station', 'desc': 'Secondary Terran administrative center.'},
                    101479: {'name': 'Capricorni Gate', 'desc': 'Strategic trade junction in the Felgenland Union territory.'}
                }
                
                # Generate a good name for the star
                primary_name = star['names']['primary_name']
                catalog_ids = star['names'].get('catalog_ids', [])
                
                # Fix problematic names by using catalog IDs
                if (not primary_name or 
                    primary_name in ['nan', 'NaN', 'nan; nan', ''] or 
                    'nan' in primary_name.lower()):
                    
                    # Try to find a good name from catalog IDs
                    good_name = None
                    if catalog_ids:
                        # Prefer proper names, then HIP, then HD, then Gliese
                        for catalog_id in catalog_ids:
                            if catalog_id and catalog_id != 'nan':
                                # Check if it's not a technical catalog ID
                                if not any(prefix in catalog_id for prefix in ['HIP ', 'HD ', 'Gliese ', 'TIC ']):
                                    good_name = catalog_id
                                    break
                        
                        # If no proper name found, use HIP number
                        if not good_name:
                            for catalog_id in catalog_ids:
                                if catalog_id and catalog_id.startswith('HIP '):
                                    good_name = catalog_id
                                    break
                        
                        # If no HIP, use HD
                        if not good_name:
                            for catalog_id in catalog_ids:
                                if catalog_id and catalog_id.startswith('HD '):
                                    good_name = catalog_id
                                    break
                        
                        # If no HD, use Gliese
                        if not good_name:
                            for catalog_id in catalog_ids:
                                if catalog_id and catalog_id.startswith('Gliese '):
                                    good_name = catalog_id
                                    break
                    
                    # If still no good name, generate one from constellation and ID
                    if not good_name:
                        constellation = star['classification'].get('constellation', 'Unknown')
                        good_name = f"{constellation} {star['_id']}"
                    
                    primary_name = good_name
                
                processed_star = {
                    'id': star['_id'],
                    'name': primary_name,
                    'fictional_name': star['names'].get('fictional_name') or fictional_names.get(star['_id'], {}).get('name'),
                    'fictional_description': star['names'].get('fictional_description') or fictional_names.get(star['_id'], {}).get('desc'),
                    'x': star['coordinates']['x'],
                    'y': star['coordinates']['y'],
                    'z': star['coordinates']['z'],
                    'ra': star['coordinates']['ra'],
                    'dec': star['coordinates']['dec'],
                    'distance': star['coordinates']['dist'],
                    'magnitude': star['physical_properties']['magnitude'],
                    'spectral_class': star['physical_properties']['spectral_class'],
                    'color_index': star['physical_properties'].get('color_index', 0.0),
                    'constellation': star['classification']['constellation'],
                    'constellation_full': star['classification']['constellation_full'],
                    'catalog_ids': star['names'].get('catalog_ids', []),
                    'exoplanet_count': star.get('exoplanets', {}).get('count', 0),
                    'has_planets': star.get('exoplanets', {}).get('has_planets', False)
                }
                
                # Add political data if available
                political = star.get('political', {})
                if political.get('nation_id'):
                    nation = nations_lookup.get(political['nation_id'])
                    if nation:
                        processed_star['nation'] = {
                            'id': nation['_id'],
                            'name': nation['name'],
                            'color': nation['appearance']['color'],
                            'capital_system': nation['capital']['system']
                        }
                        processed_star['strategic_importance'] = political.get('strategic_importance', 'normal')
                
                # Check if this star is in any nation's territories
                if not processed_star.get('nation'):
                    for nation in nations_lookup.values():
                        if star['_id'] in nation.get('territories', []):
                            processed_star['nation'] = {
                                'id': nation['_id'],
                                'name': nation['name'],
                                'color': nation['appearance']['color'],
                                'capital_system': nation['capital']['system']
                            }
                            processed_star['strategic_importance'] = 'territory'
                            break
                
                processed.append(processed_star)
                
            except Exception as e:
                print(f"Warning: Error processing star {star.get('_id', 'unknown')}: {e}")
                continue
        
        return processed
    
    def get_stars(self, limit: int = 1000, mag_limit: float = 8.0, spectral_type: str = '') -> List[Dict]:
        """Get filtered star data"""
        stars = self._cache.get('stars', [])
        
        # Separate fictional and non-fictional stars
        fictional_stars = []
        regular_stars = []
        
        for star in stars:
            if star.get('is_fictional', False):
                if spectral_type and not star['spectral_class'].startswith(spectral_type):
                    continue
                fictional_stars.append(star)
            else:
                if star['magnitude'] > mag_limit:
                    continue
                if spectral_type and not star['spectral_class'].startswith(spectral_type):
                    continue
                regular_stars.append(star)
        
        # Combine fictional stars first, then regular stars up to limit
        filtered = fictional_stars[:]
        remaining_limit = limit - len(fictional_stars)
        
        if remaining_limit > 0:
            filtered.extend(regular_stars[:remaining_limit])
        
        return filtered
    
    def get_star_by_id(self, star_id: int) -> Optional[Dict]:
        """Get specific star by ID"""
        for star in self._cache.get('stars', []):
            if star['id'] == star_id:
                return star
        return None
    
    def search_stars(self, query: str, limit: int = 20) -> List[Dict]:
        """Search stars by name"""
        if not query:
            return []
        
        query = query.lower()
        results = []
        
        for star in self._cache.get('stars', []):
            if query in star['name'].lower():
                results.append(star)
            elif star['fictional_name'] and query in star['fictional_name'].lower():
                results.append(star)
            elif star['fictional_description'] and query in star['fictional_description'].lower():
                results.append(star)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_nations(self) -> List[Dict]:
        """Get all nations with optimized format"""
        nations = []
        for nation in self._cache.get('nations', []):
            nations.append({
                'id': nation['_id'],
                'name': nation['name'],
                'full_name': nation['full_name'],
                'government_type': nation['government']['type'],
                'capital_system': nation['capital']['system'],
                'capital_star_id': nation['capital']['star_id'],
                'color': nation['appearance']['color'],
                'border_color': nation['appearance']['border_color'],
                'description': nation['description'],
                'population': nation['economy'].get('population', 'Unknown'),
                'specialties': nation['economy'].get('specialties', [])
            })
        return nations
    
    def get_trade_routes(self) -> List[Dict]:
        """Get all trade routes"""
        return self._cache.get('trade_routes', [])
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        return {
            'stars': len(self._cache.get('stars', [])),
            'nations': len(self._cache.get('nations', [])),
            'trade_routes': len(self._cache.get('trade_routes', [])),
            'exoplanets': len(self._cache.get('exoplanets', [])),
            'fictional_exoplanets': len(self._cache.get('fictional_exoplanets', []))
        }
    
    def get_fictional_exoplanets(self) -> List[Dict]:
        """Get all fictional exoplanets"""
        return self._cache.get('fictional_exoplanets', [])
    
    def get_exoplanets(self) -> List[Dict]:
        """Get all exoplanets (real catalog data)"""
        return self._cache.get('exoplanets', [])