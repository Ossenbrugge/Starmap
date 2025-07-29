#!/usr/bin/env python3
"""
Migration Script: JSON/CSV to MontyDB
Migrates all data from flat files to MontyDB collections
"""

import os
import sys
import shutil
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.config import initialize_database, get_collection_stats
from models.star_model_db import StarModelDB
from models.nation_model_db import NationModelDB
from models.trade_route_model_db import TradeRouteModelDB
from models.exoplanet_model_db import ExoplanetModelDB

def create_backup():
    """Create backup of existing data files"""
    print("📦 Creating backup of existing data...")
    
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup data files
    data_files = ['data/stars.json', 'data/nations.json', 'data/trade_routes.json', 
                  'data/stellar_regions.json', 'data/exoplanets.json',
                  'data/fictional_stars.csv', 'data/exoplanet_catalog_20250715_114843.csv']
    
    for file_path in data_files:
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_dir)
            print(f"  ✅ Backed up {file_path}")
    
    print(f"✅ Backup created in {backup_dir}")
    return backup_dir

def migrate_stellar_regions():
    """Migrate stellar regions data"""
    try:
        print("🔄 Migrating stellar regions...")
        
        from database.config import get_database
        db = get_database()
        stellar_regions = db.stellar_regions
        
        # Clear existing data
        stellar_regions.delete_many({})
        
        # Load from JSON file
        import json
        with open('data/stellar_regions.json', 'r') as f:
            regions = json.load(f)
            
            processed_regions = []
            for region in regions:
                doc = {
                    '_id': region['_id'],
                    'name': region['name'],
                    'boundaries': {
                        'x_range': region['boundaries']['x_range'],
                        'y_range': region['boundaries']['y_range'],
                        'z_range': region['boundaries']['z_range']
                    },
                    'properties': {
                        'brightest_star': region['properties']['brightest_star'],
                        'brightest_star_id': region['properties']['brightest_star_id']
                    },
                    'description': region.get('description', ''),
                    'star_count': region.get('star_count', 0)
                }
                processed_regions.append(doc)
            
            if processed_regions:
                stellar_regions.insert_many(processed_regions)
                print(f"✅ Migrated {len(processed_regions)} stellar regions")
            
    except Exception as e:
        print(f"⚠️  Could not migrate stellar regions: {e}")

def verify_migration():
    """Verify migration was successful"""
    print("🔍 Verifying migration...")
    
    stats = get_collection_stats()
    print("\n📊 Migration Statistics:")
    print(f"  Stars: {stats.get('stars', 0)}")
    print(f"  Nations: {stats.get('nations', 0)}")
    print(f"  Trade Routes: {stats.get('trade_routes', 0)}")
    print(f"  Stellar Regions: {stats.get('stellar_regions', 0)}")
    
    total_records = sum(stats.values())
    if total_records > 0:
        print(f"\n✅ Migration successful! Total records: {total_records}")
        return True
    else:
        print("\n❌ Migration failed - no records found")
        return False

def main():
    """Main migration process"""
    print("🚀 Starting MontyDB Migration")
    print("=" * 50)
    
    try:
        # Step 1: Create backup
        backup_dir = create_backup()
        
        # Step 2: Initialize database
        print("\n🔧 Initializing MontyDB...")
        if not initialize_database():
            print("❌ Failed to initialize database")
            return False
        
        # Step 3: Migrate data
        print("\n📊 Migrating data to MontyDB...")
        
        # Migrate nations first (needed for political data)
        nation_model = NationModelDB()
        nation_model.migrate_from_json()
        
        # Migrate stars
        star_model = StarModelDB()
        star_model.migrate_from_json()
        
        # Migrate trade routes
        trade_model = TradeRouteModelDB()
        trade_model.migrate_from_json()
        
        # Migrate exoplanets and Sol system
        exoplanet_model = ExoplanetModelDB()
        exoplanet_model.migrate_from_json()
        
        # Migrate stellar regions
        migrate_stellar_regions()
        
        # Step 4: Verify migration
        if verify_migration():
            print(f"\n🎉 Migration completed successfully!")
            print(f"📁 Data backup stored in: {backup_dir}")
            print(f"🗄️  MontyDB database location: ./starmap_db")
            print(f"🚀 Run 'python app_montydb.py' to start the application")
            return True
        else:
            print(f"\n❌ Migration verification failed")
            return False
            
    except Exception as e:
        print(f"\n💥 Migration failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)