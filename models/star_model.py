import pandas as pd
import math
import os
from .base_model import BaseModel
from star_naming import StarNamingSystem
from fictional_names import fictional_star_names
from fictional_nations import get_star_nation, get_nation_info
from habitability import HabitabilityAssessment


class StarModel(BaseModel):
    """Model for managing star data and operations"""
    
    def __init__(self):
        self.naming_system = StarNamingSystem()
        self.habitability_assessment = HabitabilityAssessment()
        # Add caching for frequently accessed data
        self._cache = {}
        self._filtered_cache = {}
        self._search_cache = {}
        super().__init__()
    
    def load_data(self):
        """Load star data from CSV files and process it"""
        try:
            # Load real star data
            if os.path.exists("stars_output.csv"):
                self.data = pd.read_csv("stars_output.csv")
                print(f"Loaded {len(self.data)} real stars from CSV")
            else:
                print("stars_output.csv not found!")
                self.data = pd.DataFrame()
            
            # Load fictional star data
            if os.path.exists("fictional_stars.csv"):
                fictional_stars = pd.read_csv("fictional_stars.csv")
                print(f"Loaded {len(fictional_stars)} fictional stars from CSV")
                
                # Merge fictional stars with real stars
                if not self.data.empty:
                    self.data = pd.concat([self.data, fictional_stars], ignore_index=True)
                else:
                    self.data = fictional_stars
                    
                print(f"Total stars after merging: {len(self.data)}")
            else:
                print("fictional_stars.csv not found - using only real stars")
            
            # Process star names using the naming system
            print("Processing star names...")
            self.data = self.naming_system.process_star_dataframe(self.data)
            print("Star naming complete")
            
            # Add fictional names and nation data
            self._add_fictional_data()
            self._add_nation_data()
            
            # Add habitability data
            self._add_habitability_data()
            
        except Exception as e:
            print(f"Error loading star data: {e}")
            self.data = pd.DataFrame()
    
    def _add_fictional_data(self):
        """Add fictional names from the fictional names database"""
        def get_fictional_name(star_id):
            # Ensure star_id is an integer for lookup
            try:
                star_id_int = int(star_id)
                if star_id_int in fictional_star_names:
                    return fictional_star_names[star_id_int]['fictional_name']
            except (ValueError, TypeError):
                pass
            return None
        
        def get_fictional_source(star_id):
            # Ensure star_id is an integer for lookup
            try:
                star_id_int = int(star_id)
                if star_id_int in fictional_star_names:
                    return fictional_star_names[star_id_int]['source']
            except (ValueError, TypeError):
                pass
            return None
        
        def get_fictional_description(star_id):
            # Ensure star_id is an integer for lookup
            try:
                star_id_int = int(star_id)
                if star_id_int in fictional_star_names:
                    return fictional_star_names[star_id_int]['description']
            except (ValueError, TypeError):
                pass
            return None
        
        self.data['fictional_name'] = self.data['id'].map(get_fictional_name)
        self.data['fictional_source'] = self.data['id'].map(get_fictional_source)
        self.data['fictional_description'] = self.data['id'].map(get_fictional_description)
    
    def _add_nation_data(self):
        """Add nation control data to stars"""
        def get_nation_for_star(star_id):
            nation_id = get_star_nation(star_id)
            nation_info = get_nation_info(nation_id)
            if nation_info is None:
                return None
            return {
                'id': nation_id,
                'name': nation_info['name'],
                'color': nation_info['color'],
                'government_type': nation_info['government_type']
            }
        
        self.data['nation'] = self.data['id'].apply(get_nation_for_star)
    
    def _add_habitability_data(self):
        """Add habitability assessment data to stars"""
        print("Calculating habitability scores...")
        
        def calculate_habitability(row):
            try:
                star_data = {
                    'spect': row.get('spect', 'Unknown'),
                    'lum': row.get('lum', 1.0),
                    'mag': row.get('mag', 5.0),
                    'dist': row.get('dist', 100.0)
                }
                return self.habitability_assessment.calculate_habitability_score(star_data)
            except Exception as e:
                # Return default values if calculation fails
                return {
                    'habitability_score': 0.0,
                    'habitability_category': 'Unknown',
                    'exploration_priority': 'Unknown',
                    'score_breakdown': {},
                    'parsed_spectral_type': ('Unknown', 0, 'V')
                }
        
        # Calculate habitability for all stars
        habitability_data = self.data.apply(calculate_habitability, axis=1)
        
        # Extract individual components
        self.data['habitability_score'] = habitability_data.apply(lambda x: x['habitability_score'])
        self.data['habitability_category'] = habitability_data.apply(lambda x: x['habitability_category'])
        self.data['exploration_priority'] = habitability_data.apply(lambda x: x['exploration_priority'])
        self.data['habitability_breakdown'] = habitability_data.apply(lambda x: x['score_breakdown'])
        self.data['parsed_spectral_type'] = habitability_data.apply(lambda x: x['parsed_spectral_type'])
        
        print(f"Habitability assessment complete for {len(self.data)} stars")
        
        # Print summary statistics
        category_counts = self.data['habitability_category'].value_counts()
        print("Habitability distribution:")
        for category, count in category_counts.items():
            print(f"  {category}: {count} stars")
    
    def get_habitability_explanation(self, star_id):
        """Get habitability explanation for a specific star"""
        star_row = self.data[self.data['id'] == star_id]
        if star_row.empty:
            return "Star not found"
        
        star_data = star_row.iloc[0]
        habitability_data = {
            'habitability_score': star_data['habitability_score'],
            'habitability_category': star_data['habitability_category'],
            'parsed_spectral_type': star_data['parsed_spectral_type']
        }
        
        return self.habitability_assessment.get_habitability_explanation(habitability_data)
    
    def get_stars_for_display(self, mag_limit=6.0, count_limit=1000):
        """Get stars suitable for display with filtering and sorting (cached)"""
        if self.data is None or self.data.empty:
            return []
        
        # Create cache key based on parameters
        cache_key = f"display_{mag_limit}_{count_limit}"
        
        # Check cache first
        if cache_key in self._filtered_cache:
            return self._filtered_cache[cache_key]
        
        # Check if we have pre-computed nation priorities
        if 'nation_priority' not in self.data.columns:
            # Add nation priority - stars with nations get priority (cache this computation)
            self.data['nation_priority'] = self.data['id'].apply(
                lambda x: 0 if get_star_nation(x) is not None else 1
            )
        
        # Use view instead of copy for better performance
        display_stars = self.data
        
        # Apply filters
        if mag_limit:
            # Create masks for efficient filtering
            mag_filter = display_stars['mag'] <= mag_limit
            fictional_filter = (display_stars['fictional_name'].notna() & 
                              (display_stars['fictional_name'] != ''))
            nation_filter = display_stars['nation_priority'] == 0
            
            # Combine filters efficiently
            combined_filter = mag_filter | fictional_filter | nation_filter
            display_stars = display_stars[combined_filter]
        
        # Sort efficiently
        display_stars = display_stars.sort_values(['nation_priority', 'mag'])
        
        # Apply count limit
        if count_limit:
            display_stars = display_stars.head(count_limit)
        
        # Format and cache result
        result = self._format_stars_for_json(display_stars)
        self._filtered_cache[cache_key] = result
        
        return result
    
    def _format_stars_for_json(self, stars_df):
        """Convert star dataframe to JSON-serializable format"""
        stars_json = []
        
        for _, star in stars_df.iterrows():
            star_id = int(star['id'])
            
            # Always get fresh nation data to avoid pandas string conversion
            nation_id = get_star_nation(star_id)
            nation_info = get_nation_info(nation_id)
            if nation_info is not None:
                nation_data = {
                    'id': nation_id,
                    'name': nation_info['name'],
                    'color': nation_info['color'],
                    'government_type': nation_info['government_type']
                }
            else:
                nation_data = None
            
            # Get planet data if available
            planets = star.get('planets', [])
            if planets and isinstance(planets, list) and len(planets) > 0:
                planet_data = planets
            else:
                planet_data = []

            star_data = {
                'id': star_id,
                'name': str(star.get('primary_name', f'Star {star["id"]}')),
                'all_names': star.get('all_names', []),
                'catalog_ids': star.get('catalog_ids', []),
                'designation_type': str(star.get('designation_type', 'catalog')),
                'constellation': str(star.get('constellation_short', '')),
                'constellation_full': str(star.get('constellation_full', '')),
                'x': float(star.get('x', 0)),
                'y': float(star.get('y', 0)), 
                'z': float(star.get('z', 0)),
                'mag': float(star.get('mag', 0)),
                'spect': str(star.get('spect', '')),
                'dist': float(star.get('dist', 0)),
                'fictional_name': star.get('fictional_name'),
                'fictional_source': star.get('fictional_source'),
                'fictional_description': star.get('fictional_description'),
                'nation': nation_data,
                'planets': planet_data
            }
            stars_json.append(star_data)
        
        return stars_json
    
    def get_star_details(self, star_id):
        """Get detailed information for a specific star"""
        star = self.get_by_id(star_id)
        if star is None:
            return None
        
        nation_id = get_star_nation(star_id)
        nation_info = get_nation_info(nation_id)
        
        # Get planet data if available
        planets = star.get('planets', [])
        if planets and isinstance(planets, list) and len(planets) > 0:
            planet_data = planets
        else:
            planet_data = []

        details = {
            'id': int(star['id']),
            'name': str(star.get('primary_name', f'Star {star_id}')),
            'all_names': star.get('all_names', []),
            'catalog_ids': star.get('catalog_ids', []),
            'designation_type': str(star.get('designation_type', 'catalog')),
            'constellation': str(star.get('constellation_short', '')),
            'constellation_full': str(star.get('constellation_full', '')),
            'coordinates': {
                'x': float(star.get('x', 0)),
                'y': float(star.get('y', 0)),
                'z': float(star.get('z', 0))
            },
            'properties': {
                'magnitude': float(star.get('mag', 0)),
                'spectral_class': str(star.get('spect', '')),
                'distance': float(star.get('dist', 0)),
                'luminosity': float(star.get('lum', 1.0)),
                'proper_motion_ra': float(star.get('pmra', 0)),
                'proper_motion_dec': float(star.get('pmdec', 0)),
                'bayer': str(star.get('bayer', '')),
                'flamsteed': str(star.get('flam', '')),
                'variable': str(star.get('var', ''))
            },
            'fictional_data': {
                'name': star.get('fictional_name'),
                'source': star.get('fictional_source'),
                'description': star.get('fictional_description')
            },
            'habitability': {
                'score': float(star.get('habitability_score', 0.0)),
                'category': str(star.get('habitability_category', 'Unknown')),
                'exploration_priority': str(star.get('exploration_priority', 'Unknown')),
                'breakdown': star.get('habitability_breakdown', {})
            },
            'nation': {
                'id': nation_id,
                'name': nation_info['name'] if nation_info else None,
                'color': nation_info['color'] if nation_info else '#FFFFFF',
                'government_type': nation_info['government_type'] if nation_info else None,
                'capital_system': nation_info.get('capital_system') if nation_info else None,
                'population': nation_info.get('population') if nation_info else None,
                'description': nation_info.get('description') if nation_info else None
            } if nation_info else None,
            'planets': planet_data
        }
        
        return details
    
    def search_stars(self, query, spectral_type=None):
        """Search stars by name, identifier, or spectral type (cached)"""
        if not query and not spectral_type:
            return []
        
        # Create cache key
        cache_key = f"search_{query}_{spectral_type}"
        
        # Check cache first
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]
        
        results = pd.DataFrame()
        
        if query:
            # Use the naming system to search by name
            results = self.naming_system.search_stars_by_name(self.data, query)
            
            # Also search fictional names efficiently
            fictional_matches = self.data[
                self.data['fictional_name'].str.contains(query, case=False, na=False)
            ]
            
            # Combine results and remove duplicates efficiently
            if not results.empty and not fictional_matches.empty:
                results = pd.concat([results, fictional_matches]).drop_duplicates(subset=['id'])
            elif not fictional_matches.empty:
                results = fictional_matches
        else:
            results = self.data
        
        # Filter by spectral type if provided
        if spectral_type:
            results = self._filter_by_spectral_type(results, spectral_type)
        
        # Format results and cache them
        formatted_results = self._format_search_results(results)
        self._search_cache[cache_key] = formatted_results
        
        return formatted_results
    
    def clear_cache(self):
        """Clear all cached data to free memory"""
        self._cache.clear()
        self._filtered_cache.clear()
        self._search_cache.clear()
    
    def get_cache_stats(self):
        """Get cache statistics for monitoring"""
        return {
            'cache_entries': len(self._cache),
            'filtered_cache_entries': len(self._filtered_cache),
            'search_cache_entries': len(self._search_cache)
        }
    
    def _filter_by_spectral_type(self, data, spectral_type):
        """Enhanced filtering for binary stars - check if ANY component matches"""
        spectral_filter = spectral_type.upper()
        
        def matches_spectral_type(spect_str):
            if pd.isna(spect_str):
                return False
            spect_upper = str(spect_str).upper()
            
            # Split by common binary star separators
            components = []
            for sep in ['+', '/', '&', ',']:
                if sep in spect_upper:
                    components.extend([comp.strip() for comp in spect_upper.split(sep)])
                    break
            else:
                # No separator found, treat as single star
                components = [spect_upper.strip()]
            
            # Check if any component starts with the target spectral type
            for component in components:
                if component.startswith(spectral_filter):
                    return True
                # Also check for embedded spectral types (e.g., "M4+G2V")
                if spectral_filter in component:
                    return True
            return False
        
        # Apply the enhanced filter
        mask = data['spect'].apply(matches_spectral_type)
        return data[mask]
    
    def _format_search_results(self, results_df):
        """Format search results for API response"""
        search_results = []
        
        for _, star in results_df.iterrows():
            result = {
                'id': int(star['id']),
                'name': str(star.get('primary_name', f'Star {star["id"]}')),
                'all_names': star.get('all_names', []),
                'designation_type': str(star.get('designation_type', 'catalog')),
                'constellation': str(star.get('constellation_full', '')),
                'magnitude': float(star.get('mag', 0)),
                'distance': float(star.get('dist', 0)),
                'spectral_class': str(star.get('spect', '')),
                'coordinates': {
                    'x': float(star.get('x', 0)),
                    'y': float(star.get('y', 0)),
                    'z': float(star.get('z', 0))
                },
                'fictional_name': star.get('fictional_name'),
                'fictional_source': star.get('fictional_source')
            }
            search_results.append(result)
        
        return search_results
    
    def calculate_distance(self, star1_id, star2_id):
        """Calculate distance between two stars"""
        star1 = self.get_by_id(star1_id)
        star2 = self.get_by_id(star2_id)
        
        if star1 is None or star2 is None:
            return None
        
        # Calculate 3D distance
        x1, y1, z1 = float(star1['x']), float(star1['y']), float(star1['z'])
        x2, y2, z2 = float(star2['x']), float(star2['y']), float(star2['z'])
        
        distance_parsecs = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
        distance_light_years = distance_parsecs * 3.26156  # 1 parsec = 3.26156 light years
        
        # Also calculate distances from Sol
        sol_distance_1_pc = math.sqrt(x1**2 + y1**2 + z1**2)
        sol_distance_2_pc = math.sqrt(x2**2 + y2**2 + z2**2)
        sol_distance_1_ly = sol_distance_1_pc * 3.26156
        sol_distance_2_ly = sol_distance_2_pc * 3.26156
        
        return {
            'star1': {
                'id': star1_id,
                'name': str(star1.get('primary_name', f'Star {star1_id}')),
                'distance_from_sol_pc': round(sol_distance_1_pc, 4),
                'distance_from_sol_ly': round(sol_distance_1_ly, 4)
            },
            'star2': {
                'id': star2_id,
                'name': str(star2.get('primary_name', f'Star {star2_id}')),
                'distance_from_sol_pc': round(sol_distance_2_pc, 4),
                'distance_from_sol_ly': round(sol_distance_2_ly, 4)
            },
            'distance_between': {
                'parsecs': round(distance_parsecs, 4),
                'light_years': round(distance_light_years, 4),
                'astronomical_units': round(distance_parsecs * 206265, 0),  # 1 pc ≈ 206,265 AU
                'kilometers': round(distance_light_years * 9.461e12, 0)     # 1 ly ≈ 9.461×10^12 km
            }
        }
    
    def get_spectral_types(self):
        """Get list of available spectral types"""
        if self.data is None or self.data.empty:
            return {}
        
        # Extract spectral types from the data
        spectral_types = self.data['spect'].dropna().unique()
        
        # Parse and categorize spectral types
        main_types = {}
        for spect in spectral_types:
            if spect and len(spect) > 0:
                main_class = spect[0].upper()
                if main_class in ['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L', 'T', 'Y']:
                    if main_class not in main_types:
                        main_types[main_class] = []
                    main_types[main_class].append(spect)
        
        # Sort each category
        for key in main_types:
            main_types[key] = sorted(list(set(main_types[key])))
        
        return {
            'main_types': main_types,
            'total_types': len(spectral_types),
            'description': {
                'O': 'Blue giants - Very hot, massive stars',
                'B': 'Blue-white stars - Hot, massive stars', 
                'A': 'White stars - Hot stars with strong hydrogen lines',
                'F': 'Yellow-white stars - Slightly hotter than Sun',
                'G': 'Yellow stars - Sun-like stars',
                'K': 'Orange stars - Cooler than Sun',
                'M': 'Red stars - Cool, low-mass stars',
                'L': 'Brown dwarfs - Very cool objects',
                'T': 'Methane brown dwarfs - Ultra-cool objects'
            }
        }
    
    def get_bright_stars_for_export(self, mag_limit=6.0, count_limit=100):
        """Get bright stars for CSV export"""
        if self.data is None or self.data.empty:
            return pd.DataFrame()
        
        bright_stars = self.data[self.data['mag'] <= mag_limit].head(count_limit)
        
        # Select relevant columns including new naming data
        export_columns = ['id', 'primary_name', 'designation_type', 'constellation_full', 
                         'mag', 'dist', 'spect', 'x', 'y', 'z']
        available_columns = [col for col in export_columns if col in bright_stars.columns]
        
        return bright_stars[available_columns]