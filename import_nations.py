#!/usr/bin/env python3
"""
Import nations data from nations_data.json into the MontyDB database
"""

import sys
import json
import os
from datetime import datetime

# Add database path
sys.path.append('database')
from database.config import initialize_database, get_database

# Import models
from models.nation_model_db import NationModelDB

class NationsImporter:
    def __init__(self):
        print("🔌 Initializing database connection...")
        if not initialize_database():
            print("❌ Failed to initialize database!")
            sys.exit(1)
        
        self.db = get_database()
        self.nation_model = NationModelDB()
        
        print(f"✅ Connected to MontyDB")
        print(f"📊 Current nations in database: {self.nation_model.count_documents()}")
    
    def import_nations(self, json_file):
        """Import nations from JSON file"""
        print(f"\n🏛️  Importing nations from {json_file}...")
        
        if not os.path.exists(json_file):
            print(f"❌ File {json_file} not found!")
            return
        
        # Clear existing nations
        print("🧹 Clearing existing nations...")
        self.nation_model.collection.delete_many({})
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported_count = 0
        skipped_count = 0
        
        # Process each nation
        for nation_id, nation_data in data.get('nations', {}).items():
            try:
                # Create nation document using schema
                nation_doc = {
                    '_id': nation_id,
                    'name': nation_data['name'],
                    'full_name': nation_data['full_name'],
                    'government': {
                        'type': nation_data['government_type'],
                        'established_year': nation_data['established_year'],
                        'political_alignment': nation_data.get('political_alignment'),
                        'diplomatic_stance': nation_data.get('diplomatic_stance')
                    },
                    'capital': {
                        'system': nation_data['capital_system'],
                        'star_id': nation_data['capital_star_id'],
                        'planet': nation_data['capital_planet']
                    },
                    'territories': nation_data.get('territories', []),
                    'appearance': {
                        'color': nation_data['color'],
                        'border_color': nation_data['border_color']
                    },
                    'economy': {
                        'focus': nation_data.get('economic_focus'),
                        'specialties': nation_data.get('specialties', []),
                        'population': nation_data.get('population'),
                        'gdp': nation_data.get('gdp'),
                        'trade_volume': nation_data.get('trade_volume')
                    },
                    'military': {
                        'strength': nation_data.get('military_strength'),
                        'doctrine': nation_data.get('military_doctrine'),
                        'fleet_size': nation_data.get('fleet_size')
                    },
                    'description': nation_data['description']
                }
                
                # Insert nation into database
                self.nation_model.collection.insert_one(nation_doc)
                imported_count += 1
                
                print(f"✅ Imported nation: {nation_data['name']}")
                
            except Exception as e:
                print(f"❌ Error importing nation {nation_id}: {e}")
                skipped_count += 1
        
        print(f"\n📊 Nations import completed:")
        print(f"   ✅ Imported: {imported_count} nations")
        print(f"   ⏭️  Skipped: {skipped_count} nations")
        
        return imported_count

def main():
    """Main import process"""
    print("🚀 Starting nations import process...")
    
    importer = NationsImporter()
    
    # Import nations
    imported = importer.import_nations('nations_data.json')
    
    if imported > 0:
        print(f"\n✅ Successfully imported {imported} nations!")
        print(f"📊 Total nations in database: {importer.nation_model.count_documents()}")
    else:
        print("\n❌ No nations were imported!")

if __name__ == "__main__":
    main()