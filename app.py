#!/usr/bin/env python3
"""
Starmap Application - Simplified Version
Interactive 3D starmap for science fiction novels (without PDF export dependencies)
"""

import os
import pandas as pd
import plotly.graph_objects as go
from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime
from star_naming import StarNamingSystem
from fictional_planets import fictional_planet_systems
from fictional_names import fictional_star_names
from fictional_nations import (fictional_nations, trade_routes_data, 
                              get_star_nation, get_nation_info, get_nation_color)
from galactic_directions import get_galactic_cardinal_markers, get_galactic_coordinate_grid

app = Flask(__name__)

class StarmapApp:
    def __init__(self):
        self.stars_data = None
        self.naming_system = StarNamingSystem()
        self.load_star_data()
    def load_star_data(self):
        """Load star data from CSV files (real and fictional)"""
        try:
            # Load real star data
            if os.path.exists("stars_output.csv"):
                self.stars_data = pd.read_csv("stars_output.csv")
                print(f"Loaded {len(self.stars_data)} real stars from CSV")
            else:
                print("stars_output.csv not found!")
                self.stars_data = pd.DataFrame()
            # Load fictional star data
            if os.path.exists("fictional_stars.csv"):
                fictional_stars = pd.read_csv("fictional_stars.csv")
                print(f"Loaded {len(fictional_stars)} fictional stars from CSV")
                
                # Merge fictional stars with real stars
                if not self.stars_data.empty:
                    self.stars_data = pd.concat([self.stars_data, fictional_stars], 
                                              ignore_index=True)
                else:
                    self.stars_data = fictional_stars
                    
                print(f"Total stars after merging: {len(self.stars_data)}")
            else:
                print("fictional_stars.csv not found - using only real stars")
                
            # Process star names using the naming system
            print("Processing star names...")
            self.stars_data = self.naming_system.process_star_dataframe(self.stars_data)
            print("Star naming complete")
            
            # Add sample planetary systems
            self.add_sample_planets()
            
            # Add fictional names
            self.add_fictional_names()
        except Exception as e:
            print(f"Error loading star data: {e}")
            self.stars_data = pd.DataFrame()
    
    def add_sample_planets(self):
        """Add sample planetary data"""
        # Comprehensive planetary systems with real and theoretical data
        planet_systems = {
            0: [  # Sol - Our Solar System (complete with all 8 planets)
                {
                    "name": "Mercury", "type": "Terrestrial", "distance_au": 0.387, "mass_earth": 0.0553, 
                    "radius_earth": 0.3829, "orbital_period_days": 87.97, "temperature_k": 440, 
                    "atmosphere": "Virtually none", "discovery_year": "Ancient", "confirmed": True
                },
                {
                    "name": "Venus", "type": "Terrestrial", "distance_au": 0.723, "mass_earth": 0.815,
                    "radius_earth": 0.9499, "orbital_period_days": 224.7, "temperature_k": 737,
                    "atmosphere": "CO2 (96.5%), N2 (3.5%)", "discovery_year": "Ancient", "confirmed": True
                },
                {
                    "name": "Earth", "type": "Terrestrial", "distance_au": 1.0, "mass_earth": 1.0,
                    "radius_earth": 1.0, "orbital_period_days": 365.26, "temperature_k": 288,
                    "atmosphere": "N2 (78%), O2 (21%)", "discovery_year": "N/A", "confirmed": True,
                    "moons": [
                        {
                            "name": "Luna", "type": "Rocky", "mass_earth": 0.0123, "radius_earth": 0.2724,
                            "orbital_distance_km": 384400, "orbital_period_days": 27.3, "temperature_k": 220,
                            "atmosphere": "Virtually none", "description": "Earth's natural satellite"
                        }
                    ]
                },
                {
                    "name": "Mars", "type": "Terrestrial", "distance_au": 1.524, "mass_earth": 0.1074,
                    "radius_earth": 0.5320, "orbital_period_days": 686.98, "temperature_k": 210,
                    "atmosphere": "CO2 (95%), Ar (1.9%)", "discovery_year": "Ancient", "confirmed": True
                },
                {
                    "name": "Jupiter", "type": "Gas Giant", "distance_au": 5.204, "mass_earth": 317.8,
                    "radius_earth": 10.97, "orbital_period_days": 4332.6, "temperature_k": 165,
                    "atmosphere": "H2 (89%), He (10%)", "discovery_year": "Ancient", "confirmed": True
                },
                {
                    "name": "Saturn", "type": "Gas Giant", "distance_au": 9.573, "mass_earth": 95.16,
                    "radius_earth": 9.140, "orbital_period_days": 10759.2, "temperature_k": 134,
                    "atmosphere": "H2 (96%), He (3%)", "discovery_year": "Ancient", "confirmed": True
                },
                {
                    "name": "Uranus", "type": "Ice Giant", "distance_au": 19.165, "mass_earth": 14.54,
                    "radius_earth": 3.981, "orbital_period_days": 30688.5, "temperature_k": 76,
                    "atmosphere": "H2 (83%), He (15%), CH4 (2%)", "discovery_year": "1781", "confirmed": True
                },
                {
                    "name": "Neptune", "type": "Ice Giant", "distance_au": 30.178, "mass_earth": 17.15,
                    "radius_earth": 3.865, "orbital_period_days": 60182, "temperature_k": 72,
                    "atmosphere": "H2 (80%), He (19%), CH4 (1%)", "discovery_year": "1846", "confirmed": True
                }
            ],
            16496: [  # Epsilon Eridani - Real exoplanet system
                {
                    "name": "Epsilon Eridani b", "type": "Gas Giant", "distance_au": 3.4, "mass_earth": 317,
                    "radius_earth": 4.1, "orbital_period_days": 2502, "temperature_k": 120,
                    "atmosphere": "H2, He (estimated)", "discovery_year": "2000", "confirmed": True
                }
            ],
            70666: [  # Proxima Centauri - Real exoplanets
                {
                    "name": "Proxima Centauri b", "type": "Terrestrial", "distance_au": 0.05, "mass_earth": 1.27,
                    "radius_earth": 1.1, "orbital_period_days": 11.2, "temperature_k": 234,
                    "atmosphere": "Unknown", "discovery_year": "2016", "confirmed": True
                },
                {
                    "name": "Proxima Centauri c", "type": "Super-Earth", "distance_au": 1.5, "mass_earth": 6.0,
                    "radius_earth": 1.5, "orbital_period_days": 1928, "temperature_k": 39,
                    "atmosphere": "Unknown", "discovery_year": "2019", "confirmed": True
                },
                {
                    "name": "Proxima Centauri d", "type": "Sub-Earth", "distance_au": 0.029, "mass_earth": 0.26,
                    "radius_earth": 0.81, "orbital_period_days": 5.1, "temperature_k": 350,
                    "atmosphere": "Unknown", "discovery_year": "2022", "confirmed": True
                }
            ],
            32263: [  # Sirius - Hypothetical system for demonstration
                {
                    "name": "Sirius Ab", "type": "Hot Jupiter", "distance_au": 0.1, "mass_earth": 400,
                    "radius_earth": 5.2, "orbital_period_days": 15, "temperature_k": 1200,
                    "atmosphere": "H2, He (theoretical)", "discovery_year": "Future", "confirmed": False
                }
            ],
            71456: [  # Alpha Centauri A - Theoretical planets
                {
                    "name": "Alpha Centauri Ab", "type": "Terrestrial", "distance_au": 1.25, "mass_earth": 1.13,
                    "radius_earth": 1.05, "orbital_period_days": 400, "temperature_k": 250,
                    "atmosphere": "Unknown (theoretical)", "discovery_year": "TBD", "confirmed": False
                }
            ],
            8087: [  # Tau Ceti - Real candidate planets
                {
                    "name": "Tau Ceti e", "type": "Super-Earth", "distance_au": 0.55, "mass_earth": 3.93,
                    "radius_earth": 1.51, "orbital_period_days": 168, "temperature_k": 240,
                    "atmosphere": "Unknown", "discovery_year": "2012", "confirmed": False
                },
                {
                    "name": "Tau Ceti f", "type": "Super-Earth", "distance_au": 1.35, "mass_earth": 3.93,
                    "radius_earth": 1.51, "orbital_period_days": 642, "temperature_k": 150,
                    "atmosphere": "Unknown", "discovery_year": "2012", "confirmed": False
                }
            ]
        }
        
        # Merge real and fictional planet systems
        all_planet_systems = {**planet_systems, **fictional_planet_systems}
        
        # Add planets column
        self.stars_data['planets'] = self.stars_data['id'].map(all_planet_systems).fillna('').apply(list)
    
    def add_fictional_names(self):
        """Add fictional names from Felgenland Union Planetary Survey Database"""
        # Add fictional names to stars
        def get_fictional_name(star_id):
            if star_id in fictional_star_names:
                return fictional_star_names[star_id]['fictional_name']
            return None
        
        def get_fictional_source(star_id):
            if star_id in fictional_star_names:
                return fictional_star_names[star_id]['source']
            return None
            
        def get_fictional_description(star_id):
            if star_id in fictional_star_names:
                return fictional_star_names[star_id]['description']
            return None
        
        self.stars_data['fictional_name'] = self.stars_data['id'].map(get_fictional_name)
        self.stars_data['fictional_source'] = self.stars_data['id'].map(get_fictional_source)
        self.stars_data['fictional_description'] = self.stars_data['id'].map(get_fictional_description)

starmap = StarmapApp()

@app.route('/')
def index():
    """Main starmap page"""
    try:
        return render_template('starmap.html')
    except Exception as e:
        return f"""
        <html>
        <head><title>Starmap - Error</title></head>
        <body>
            <h1>Template Error</h1>
            <p>Error: {str(e)}</p>
            <p>Working directory: {os.getcwd()}</p>
            <p>Templates directory exists: {os.path.exists('templates')}</p>
            <p>Template file exists: {os.path.exists('templates/starmap.html')}</p>
        </body>
        </html>
        """

@app.route('/api/stars')
def get_stars():
    """API endpoint to get star data"""
    try:
        # Prioritize stars that belong to nations and bright stars
        all_stars = starmap.stars_data.copy()
        
        # Add nation priority - stars with nations get priority
        all_stars['nation_priority'] = all_stars['id'].apply(lambda x: 0 if get_star_nation(x) != 'neutral_zone' else 1)
        
        # Sort by nation priority (0 first), then by magnitude (bright first)
        all_stars = all_stars.sort_values(['nation_priority', 'mag'])
        
        # Limit to reasonable number of stars for performance
        stars_subset = all_stars.head(1000)
        
        # Convert to JSON-serializable format
        stars_json = []
        for _, star in stars_subset.iterrows():
            star_id = int(star['id'])
            nation_id = get_star_nation(star_id)
            nation_info = get_nation_info(nation_id)
            
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
                'planets': star.get('planets', []),
                'fictional_name': star.get('fictional_name'),
                'fictional_source': star.get('fictional_source'),
                'fictional_description': star.get('fictional_description'),
                'nation': {
                    'id': nation_id,
                    'name': nation_info['name'],
                    'color': nation_info['color'],
                    'government_type': nation_info['government_type']
                }
            }
            stars_json.append(star_data)
            
        return jsonify(stars_json)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/star/<int:star_id>')
def get_star_details(star_id):
    """Get detailed information for a specific star"""
    try:
        star = starmap.stars_data[starmap.stars_data['id'] == star_id]
        if star.empty:
            return jsonify({'error': 'Star not found'})
            
        star_data = star.iloc[0]
        nation_id = get_star_nation(star_id)
        nation_info = get_nation_info(nation_id)
        
        details = {
            'id': int(star_data['id']),
            'name': str(star_data.get('primary_name', f'Star {star_id}')),
            'all_names': star_data.get('all_names', []),
            'catalog_ids': star_data.get('catalog_ids', []),
            'designation_type': str(star_data.get('designation_type', 'catalog')),
            'constellation': str(star_data.get('constellation_short', '')),
            'constellation_full': str(star_data.get('constellation_full', '')),
            'coordinates': {
                'x': float(star_data.get('x', 0)),
                'y': float(star_data.get('y', 0)),
                'z': float(star_data.get('z', 0))
            },
            'properties': {
                'magnitude': float(star_data.get('mag', 0)),
                'spectral_class': str(star_data.get('spect', '')),
                'distance': float(star_data.get('dist', 0)),
                'luminosity': float(star_data.get('lum', 1.0)),
                'proper_motion_ra': float(star_data.get('pmra', 0)),
                'proper_motion_dec': float(star_data.get('pmdec', 0)),
                'bayer': str(star_data.get('bayer', '')),
                'flamsteed': str(star_data.get('flam', '')),
                'variable': str(star_data.get('var', ''))
            },
            'planets': star_data.get('planets', []),
            'fictional_data': {
                'name': star_data.get('fictional_name'),
                'source': star_data.get('fictional_source'),
                'description': star_data.get('fictional_description')
            },
            'nation': {
                'id': nation_id,
                'name': nation_info['name'],
                'color': nation_info['color'],
                'government_type': nation_info['government_type'],
                'capital_system': nation_info.get('capital_system'),
                'population': nation_info.get('population'),
                'description': nation_info.get('description')
            }
        }
        
        return jsonify(details)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/search')
def search_stars():
    """Search stars by name, identifier, or spectral type"""
    try:
        query = request.args.get('q', '').strip()
        spectral_type = request.args.get('spectral', '').strip()
        
        if not query and not spectral_type:
            return jsonify({'error': 'No search query or spectral type provided'})
        
        # Start with all stars
        if query:
            # Use the naming system to search by name
            results = starmap.naming_system.search_stars_by_name(starmap.stars_data, query)
            
            # Also search fictional names
            fictional_matches = starmap.stars_data[
                starmap.stars_data['fictional_name'].str.contains(query, case=False, na=False)
            ]
            
            # Combine results and remove duplicates
            results = pd.concat([results, fictional_matches]).drop_duplicates(subset=['id'])
        else:
            results = starmap.stars_data.copy()
        
        # Filter by spectral type if provided
        if spectral_type:
            spectral_filter = spectral_type.upper()
            # Enhanced filtering for binary stars - check if ANY component matches
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
            mask = results['spect'].apply(matches_spectral_type)
            results = results[mask]
        
        # Limit results and format - increased limit for spectral searches
        limit = 100 if spectral_type else 50
        results_subset = results.head(limit)
        search_results = []
        
        for _, star in results_subset.iterrows():
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
        
        return jsonify({
            'query': query,
            'spectral_filter': spectral_type,
            'count': len(search_results),
            'total_matching': len(results),
            'results': search_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/planet/add', methods=['POST'])
def add_planet():
    """Add a new planet to a star system"""
    try:
        data = request.get_json()
        star_id = data.get('star_id')
        planet_data = data.get('planet')
        
        if not star_id or not planet_data:
            return jsonify({'error': 'Missing star_id or planet data'})
        
        # Find the star
        star_idx = starmap.stars_data[starmap.stars_data['id'] == star_id].index
        if len(star_idx) == 0:
            return jsonify({'error': 'Star not found'})
        
        star_idx = star_idx[0]
        
        # Get current planets
        current_planets = starmap.stars_data.at[star_idx, 'planets']
        if not isinstance(current_planets, list):
            current_planets = []
        
        # Add new planet with required fields
        new_planet = {
            'name': planet_data.get('name', 'Unknown Planet'),
            'type': planet_data.get('type', 'Unknown'),
            'distance_au': float(planet_data.get('distance_au', 1.0)),
            'mass_earth': float(planet_data.get('mass_earth', 1.0)),
            'radius_earth': float(planet_data.get('radius_earth', 1.0)),
            'orbital_period_days': float(planet_data.get('orbital_period_days', 365)),
            'temperature_k': float(planet_data.get('temperature_k', 250)),
            'atmosphere': planet_data.get('atmosphere', 'Unknown'),
            'discovery_year': planet_data.get('discovery_year', 'TBD'),
            'confirmed': planet_data.get('confirmed', False)
        }
        
        current_planets.append(new_planet)
        starmap.stars_data.at[star_idx, 'planets'] = current_planets
        
        return jsonify({
            'success': True,
            'message': f'Added planet {new_planet["name"]} to {starmap.stars_data.at[star_idx, "primary_name"]}',
            'planet_count': len(current_planets)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/distance')
def calculate_distance():
    """Calculate distance between two stars"""
    try:
        star1_id = request.args.get('star1', type=int)
        star2_id = request.args.get('star2', type=int)
        
        if not star1_id or not star2_id:
            return jsonify({'error': 'Both star1 and star2 IDs required'})
        
        # Find the stars
        star1 = starmap.stars_data[starmap.stars_data['id'] == star1_id]
        star2 = starmap.stars_data[starmap.stars_data['id'] == star2_id]
        
        if star1.empty or star2.empty:
            return jsonify({'error': 'One or both stars not found'})
        
        star1_data = star1.iloc[0]
        star2_data = star2.iloc[0]
        
        # Calculate 3D distance
        import math
        
        x1, y1, z1 = float(star1_data['x']), float(star1_data['y']), float(star1_data['z'])
        x2, y2, z2 = float(star2_data['x']), float(star2_data['y']), float(star2_data['z'])
        
        distance_parsecs = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
        distance_light_years = distance_parsecs * 3.26156  # 1 parsec = 3.26156 light years
        
        # Also calculate distances from Sol
        sol_distance_1_pc = math.sqrt(x1**2 + y1**2 + z1**2)
        sol_distance_2_pc = math.sqrt(x2**2 + y2**2 + z2**2)
        sol_distance_1_ly = sol_distance_1_pc * 3.26156
        sol_distance_2_ly = sol_distance_2_pc * 3.26156
        
        return jsonify({
            'star1': {
                'id': star1_id,
                'name': str(star1_data.get('primary_name', f'Star {star1_id}')),
                'distance_from_sol_pc': round(sol_distance_1_pc, 4),
                'distance_from_sol_ly': round(sol_distance_1_ly, 4)
            },
            'star2': {
                'id': star2_id,
                'name': str(star2_data.get('primary_name', f'Star {star2_id}')),
                'distance_from_sol_pc': round(sol_distance_2_pc, 4),
                'distance_from_sol_ly': round(sol_distance_2_ly, 4)
            },
            'distance_between': {
                'parsecs': round(distance_parsecs, 4),
                'light_years': round(distance_light_years, 4),
                'astronomical_units': round(distance_parsecs * 206265, 0),  # 1 pc ≈ 206,265 AU
                'kilometers': round(distance_light_years * 9.461e12, 0)     # 1 ly ≈ 9.461×10^12 km
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/spectral-types')
def get_spectral_types():
    """Get list of available spectral types"""
    try:
        # Extract spectral types from the data
        spectral_types = starmap.stars_data['spect'].dropna().unique()
        
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
        
        return jsonify({
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
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/systems')
def get_planetary_systems():
    """Get all stars with planetary systems"""
    try:
        # Find stars with planets
        systems = []
        for _, star in starmap.stars_data.iterrows():
            if star.get('planets') and len(star['planets']) > 0:
                systems.append({
                    'id': int(star['id']),
                    'name': str(star.get('primary_name', f'Star {star["id"]}')),
                    'constellation': str(star.get('constellation_full', star.get('constellation_short', ''))),
                    'distance': float(star.get('dist', 0)),
                    'planet_count': len(star['planets']),
                    'confirmed_planets': sum(1 for p in star['planets'] if p.get('confirmed', False)),
                    'candidate_planets': sum(1 for p in star['planets'] if not p.get('confirmed', False))
                })
        
        return jsonify({
            'total_systems': len(systems),
            'systems': sorted(systems, key=lambda x: x['planet_count'], reverse=True)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/export/csv')
def export_csv():
    """Export bright stars as CSV"""
    try:
        # Get bright stars
        bright_stars = starmap.stars_data[starmap.stars_data['mag'] <= 6.0].head(100)
        
        # Select relevant columns including new naming data
        export_columns = ['id', 'primary_name', 'designation_type', 'constellation_full', 'mag', 'dist', 'spect', 'x', 'y', 'z']
        available_columns = [col for col in export_columns if col in bright_stars.columns]
        export_data = bright_stars[available_columns]
        
        # Generate CSV
        csv_content = export_data.to_csv(index=False)
        
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=starmap_export.csv'}
        )
            
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/nations')
def get_nations():
    """Get all fictional nations"""
    try:
        return jsonify({
            'nations': fictional_nations,
            'total_nations': len(fictional_nations)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/trade-routes')
def get_trade_routes():
    """Get all trade routes"""
    try:
        return jsonify({
            'trade_routes': trade_routes_data,
            'total_route_groups': len(trade_routes_data)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/nation/<nation_id>')
def get_nation_details(nation_id):
    """Get detailed information for a specific nation"""
    try:
        if nation_id not in fictional_nations:
            return jsonify({'error': 'Nation not found'})
        
        nation = fictional_nations[nation_id]
        
        # Get territory star details
        territory_stars = []
        for star_id in nation['territories']:
            star = starmap.stars_data[starmap.stars_data['id'] == star_id]
            if not star.empty:
                star_data = star.iloc[0]
                territory_stars.append({
                    'id': int(star_id),
                    'name': str(star_data.get('primary_name', f'Star {star_id}')),
                    'fictional_name': star_data.get('fictional_name'),
                    'coordinates': {
                        'x': float(star_data.get('x', 0)),
                        'y': float(star_data.get('y', 0)),
                        'z': float(star_data.get('z', 0))
                    },
                    'distance': float(star_data.get('dist', 0)),
                    'spectral_class': str(star_data.get('spect', ''))
                })
        
        return jsonify({
            **nation,
            'territory_stars': territory_stars,
            'territory_count': len(territory_stars)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/galactic-directions')
def get_galactic_directions():
    """API endpoint to get galactic cardinal direction markers"""
    try:
        # Get distance parameter from query string (default 50 parsecs)
        distance = float(request.args.get('distance', 50))
        
        # Get the cardinal direction markers
        markers = get_galactic_cardinal_markers(distance)
        
        # Optionally include coordinate grid
        include_grid = request.args.get('grid', 'false').lower() == 'true'
        grid_data = []
        if include_grid:
            grid_data = get_galactic_coordinate_grid(distance)
        
        return jsonify({
            'markers': markers,
            'grid': grid_data,
            'distance': distance,
            'total_markers': len(markers)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("🌟 Starting Starmap Application")
    print("📊 Loaded star data successfully" if not starmap.stars_data.empty else "⚠️  No star data loaded")
    print("🌐 Access the application at:")
    print("   Local:  http://localhost:8080")
    print("   LAN:    http://[your-ip]:8080")
    print("🚀 Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=8080, debug=True)