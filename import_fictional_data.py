#!/usr/bin/env python3
"""
Import fictional data from CSV and JSON files into the MontyDB database
"""

import sys
import json
import csv
import os
from datetime import datetime

# Add database path
sys.path.append('database')
from database.config import initialize_database, get_database

# Import models
from models.star_model_db import StarModelDB
from models.trade_route_model_db import TradeRouteModelDB

class FictionalDataImporter:
    def __init__(self):
        print("🔌 Initializing database connection...")
        if not initialize_database():
            print("❌ Failed to initialize database!")
            sys.exit(1)
        
        self.db = get_database()
        self.star_model = StarModelDB()
        self.trade_route_model = TradeRouteModelDB()
        
        print(f"✅ Connected to MontyDB")
        print(f"📊 Current database stats:")
        print(f"   Stars: {self.star_model.count_documents()}")
        print(f"   Trade routes: {self.trade_route_model.count_documents()}")
    
    def import_fictional_stars(self, csv_file):
        """Import fictional star names from CSV file"""
        print(f"\n📋 Importing fictional star data from {csv_file}...")
        
        if not os.path.exists(csv_file):
            print(f"❌ File {csv_file} not found!")
            return
        
        updated_count = 0
        skipped_count = 0
        
        # Create name mapping for common star names
        name_mapping = {
            'Tiefe-Grenze Tor': ['HD 86729', '86729'],
            'Gliese 581': ['GJ 581', 'Gl 581'],
            'Tau Ceti': ['tau Cet', 'HD 10700'],
            'Gliese 667': ['GJ 667', 'Gl 667'],
            'HD 69830': ['69830'],
            'Eta Cassiopeiae': ['eta Cas', 'HD 4614'],
            '82 G. Eridani': ['82 Eri', 'HD 20794'],
            'Delta Pavonis': ['del Pav', 'HD 190248'],
            'HD 10180': ['10180']
        }
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                star_id = int(row['id'])
                proper_name = row.get('proper', '').strip()
                
                # Skip if no proper name
                if not proper_name:
                    skipped_count += 1
                    continue
                
                # Try to find star by ID first
                star = self.star_model.get_by_id(star_id)
                
                # If not found by ID, try to find by name
                if not star and proper_name in name_mapping:
                    search_names = name_mapping[proper_name]
                    for search_name in search_names:
                        stars = self.star_model.search_stars(search_name, limit=1)
                        if stars:
                            star = self.star_model.get_by_id(stars[0]['id'])
                            if star:
                                print(f"🔍 Found {proper_name} by name search: {star['names']['primary_name']} (ID: {star['_id']})")
                                break
                
                if not star:
                    print(f"⚠️  Star '{proper_name}' (ID {star_id}) not found in database")
                    skipped_count += 1
                    continue
                
                # Update the star with fictional name
                update_data = {
                    'names.fictional_name': proper_name,
                    'names.fictional_source': 'Felgenland Saga',
                    'names.fictional_description': f'Fictional name from the Felgenland universe'
                }
                
                try:
                    result = self.star_model.update_one(
                        {'_id': star['_id']}, 
                        {'$set': update_data}
                    )
                    
                    if result.modified_count > 0:
                        updated_count += 1
                        print(f"✅ Updated star {star['_id']} ({star['names']['primary_name']}) with fictional name: {proper_name}")
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    print(f"❌ Error updating star {star['_id']}: {e}")
                    skipped_count += 1
        
        print(f"\n📊 Fictional stars import completed:")
        print(f"   ✅ Updated: {updated_count} stars")
        print(f"   ⏭️  Skipped: {skipped_count} stars")
    
    def import_trade_routes(self, json_file):
        """Import trade routes from JSON file"""
        print(f"\n🛣️  Importing trade routes from {json_file}...")
        
        if not os.path.exists(json_file):
            print(f"❌ File {json_file} not found!")
            return
        
        # Clear existing trade routes
        print("🧹 Clearing existing trade routes...")
        self.trade_route_model.collection.delete_many({})
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total_routes = 0
        imported_routes = 0
        skipped_routes = 0
        
        # Process each route category
        for category, routes in data.get('trade_routes', {}).items():
            print(f"\n📦 Processing {category} routes...")
            
            for route in routes:
                total_routes += 1
                
                # Use the proper schema for trade routes (matching TradeRouteSchema)
                route_doc = {
                    '_id': f"{route['name'].replace(' ', '_').replace('-', '_').lower()}_{total_routes}",
                    'name': route['name'],
                    'route_type': route['route_type'],
                    'established': route.get('established'),
                    'endpoints': {
                        'from': {
                            'star_id': route['from_star_id'],
                            'system': route['from_system']
                        },
                        'to': {
                            'star_id': route['to_star_id'],
                            'system': route['to_system']
                        }
                    },
                    'logistics': {
                        'cargo_types': route.get('cargo_types', []),
                        'travel_time_days': route.get('travel_time_days', 0),
                        'frequency': route.get('frequency', 'Unknown'),
                        'capacity': route.get('capacity'),
                        'cost_per_unit': route.get('cost_per_unit')
                    },
                    'control': {
                        'controlling_nation': route.get('controlling_nation'),
                        'security_level': route.get('security_level', 'Standard'),
                        'patrol_frequency': route.get('patrol_frequency'),
                        'customs_checkpoints': route.get('customs_checkpoints', [])
                    },
                    'economics': {
                        'economic_zone': route.get('economic_zone'),
                        'trade_volume': route.get('trade_volume'),
                        'revenue': route.get('revenue'),
                        'regions': route.get('regions', [])
                    },
                    'description': route.get('description', ''),
                    'category': category  # Add the route category
                }
                
                try:
                    # Verify that both stars exist
                    from_star = self.star_model.get_by_id(route_doc['endpoints']['from']['star_id'])
                    to_star = self.star_model.get_by_id(route_doc['endpoints']['to']['star_id'])
                    
                    if not from_star:
                        print(f"⚠️  From star ID {route_doc['endpoints']['from']['star_id']} not found for route {route['name']}")
                        skipped_routes += 1
                        continue
                    
                    if not to_star:
                        print(f"⚠️  To star ID {route_doc['endpoints']['to']['star_id']} not found for route {route['name']}")
                        skipped_routes += 1
                        continue
                    
                    # Insert the trade route directly into collection (bypass schema validation)
                    self.trade_route_model.collection.insert_one(route_doc)
                    imported_routes += 1
                    
                    if imported_routes % 10 == 0:
                        print(f"   📈 Imported {imported_routes} routes so far...")
                    
                except Exception as e:
                    print(f"❌ Error importing route {route['name']}: {e}")
                    skipped_routes += 1
        
        print(f"\n📊 Trade routes import completed:")
        print(f"   ✅ Imported: {imported_routes} routes")
        print(f"   ⏭️  Skipped: {skipped_routes} routes")
        print(f"   📋 Total processed: {total_routes} routes")
    
    def find_brightest_stars_in_octants(self):
        """Find the brightest star in each octant for naming"""
        print(f"\n⭐ Finding brightest stars in each octant...")
        
        # Define octant boundaries
        octants = {
            'ppp': {'x_min': 0, 'x_max': 95, 'y_min': 0, 'y_max': 95, 'z_min': 0, 'z_max': 95},
            'ppn': {'x_min': 0, 'x_max': 95, 'y_min': 0, 'y_max': 95, 'z_min': -95, 'z_max': 0},
            'pnp': {'x_min': 0, 'x_max': 95, 'y_min': -95, 'y_max': 0, 'z_min': 0, 'z_max': 95},
            'pnn': {'x_min': 0, 'x_max': 95, 'y_min': -95, 'y_max': 0, 'z_min': -95, 'z_max': 0},
            'npp': {'x_min': -95, 'x_max': 0, 'y_min': 0, 'y_max': 95, 'z_min': 0, 'z_max': 95},
            'npn': {'x_min': -95, 'x_max': 0, 'y_min': 0, 'y_max': 95, 'z_min': -95, 'z_max': 0},
            'nnp': {'x_min': -95, 'x_max': 0, 'y_min': -95, 'y_max': 0, 'z_min': 0, 'z_max': 95},
            'nnn': {'x_min': -95, 'x_max': 0, 'y_min': -95, 'y_max': 0, 'z_min': -95, 'z_max': 0}
        }
        
        brightest_stars = {}
        
        for octant_id, bounds in octants.items():
            print(f"🔍 Searching octant {octant_id}...")
            
            # Query for stars in this octant, sorted by brightness (lowest magnitude = brightest)
            query = {
                'coordinates.x': {'$gte': bounds['x_min'], '$lte': bounds['x_max']},
                'coordinates.y': {'$gte': bounds['y_min'], '$lte': bounds['y_max']},
                'coordinates.z': {'$gte': bounds['z_min'], '$lte': bounds['z_max']},
                'physical_properties.magnitude': {'$exists': True}
            }
            
            stars_in_octant = list(self.star_model.find(
                query, 
                sort=[('physical_properties.magnitude', 1)],  # Ascending = brightest first
                limit=1
            ))
            
            if stars_in_octant:
                brightest = stars_in_octant[0]
                brightest_stars[octant_id] = {
                    'star_id': brightest['_id'],
                    'name': brightest['names']['primary_name'],
                    'fictional_name': brightest['names'].get('fictional_name'),
                    'magnitude': brightest['physical_properties']['magnitude'],
                    'coordinates': brightest['coordinates']
                }
                
                print(f"   ⭐ Brightest: {brightest['names']['primary_name']} (mag {brightest['physical_properties']['magnitude']:.2f})")
            else:
                print(f"   ❌ No stars found in octant {octant_id}")
        
        return brightest_stars
    
    def update_octant_names(self, brightest_stars):
        """Update the stellar regions API to use brightest star names"""
        print(f"\n🏷️  Octant naming recommendations:")
        
        octant_mapping = {
            'ppp': 'octant_ppp',
            'ppn': 'octant_ppn', 
            'pnp': 'octant_pnp',
            'pnn': 'octant_pnn',
            'npp': 'octant_npp',
            'npn': 'octant_npn',
            'nnp': 'octant_nnp',
            'nnn': 'octant_nnn'
        }
        
        for octant_key, star_data in brightest_stars.items():
            octant_id = octant_mapping[octant_key]
            star_name = star_data['fictional_name'] or star_data['name']
            
            print(f"   {octant_id}: '{star_name} Sector' (brightest: {star_data['name']}, mag {star_data['magnitude']:.2f})")
        
        print(f"\n💡 Update the stellar regions API in app_montydb.py with these names!")
        return brightest_stars

def main():
    """Main import process"""
    print("🚀 Starting fictional data import process...")
    
    importer = FictionalDataImporter()
    
    # Import fictional star names
    importer.import_fictional_stars('fictional_stars.csv')
    
    # Import trade routes
    importer.import_trade_routes('trade_routes_data.json')
    
    # Find brightest stars in octants
    brightest_stars = importer.find_brightest_stars_in_octants()
    
    # Display octant naming recommendations
    importer.update_octant_names(brightest_stars)
    
    print("\n✅ Import process completed!")
    print("\n📊 Final database stats:")
    print(f"   Stars: {importer.star_model.count_documents()}")
    print(f"   Trade routes: {importer.trade_route_model.count_documents()}")

if __name__ == "__main__":
    main()