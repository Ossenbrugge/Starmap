#!/usr/bin/env python3
"""
Data migration script to convert CSV/JSON data to MontyDB
"""

import os
import json
import pandas as pd
from datetime import datetime

from config import get_database, initialize_database
from schema import (
    StarSchema, NationSchema, TradeRouteSchema, 
    StellarRegionSchema, PlanetarySystemSchema, MetadataSchema
)

# Import existing data loaders
import sys
sys.path.append('..')
from fictional_planets import fictional_planet_systems
from fictional_nations import get_star_nation, get_nation_info


class DataMigrator:
    """Handles migration of existing data to MontyDB"""
    
    def __init__(self):
        self.db = None
        self.stats = {
            'stars': 0,
            'nations': 0,
            'trade_routes': 0,
            'stellar_regions': 0,
            'planetary_systems': 0,
            'errors': []
        }
    
    def migrate_all(self):
        """Run complete migration"""
        print("🚀 Starting data migration to MontyDB...")
        
        # Initialize database
        if not initialize_database():
            print("❌ Failed to initialize database")
            return False
        
        self.db = get_database()
        
        # Run migrations in order
        try:
            self._migrate_stars()
            self._migrate_nations()
            self._migrate_trade_routes()
            self._migrate_stellar_regions()
            self._migrate_planetary_systems()
            self._create_indexes()
            self._save_metadata()
            
            self._print_migration_summary()
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            self.stats['errors'].append(str(e))
            return False
    
    def _migrate_stars(self):
        """Migrate star data from CSV files"""
        print("\n📊 Migrating star data...")
        
        stars_collection = self.db.stars
        
        # Load real stars
        stars_data = []
        if os.path.exists("../stars_output.csv"):
            real_stars = pd.read_csv("../stars_output.csv")
            stars_data.append(real_stars)
            print(f"   ✅ Loaded {len(real_stars)} real stars")
        
        # Load fictional stars
        if os.path.exists("../fictional_stars.csv"):
            fictional_stars = pd.read_csv("../fictional_stars.csv")
            stars_data.append(fictional_stars)
            print(f"   ✅ Loaded {len(fictional_stars)} fictional stars")
        
        if not stars_data:
            print("   ⚠️  No star data files found")
            return
        
        # Combine all star data
        all_stars = pd.concat(stars_data, ignore_index=True)
        
        # Process star names (simplified for migration)
        self._process_star_names(all_stars)
        
        # Add nation data
        self._add_nation_data_to_stars(all_stars)
        
        # Add habitability data (simplified)
        self._add_habitability_data_to_stars(all_stars)
        
        # Convert to MongoDB documents
        star_documents = []
        for _, star in all_stars.iterrows():
            try:
                doc = StarSchema.create_document(star)
                star_documents.append(doc)
            except Exception as e:
                self.stats['errors'].append(f"Star {star.get('id', 'unknown')}: {e}")
        
        # Insert into database
        if star_documents:
            stars_collection.insert_many(star_documents)
            self.stats['stars'] = len(star_documents)
            print(f"   ✅ Migrated {len(star_documents)} stars")
    
    def _migrate_nations(self):
        """Migrate nation data from JSON"""
        print("\n🏛️  Migrating nation data...")
        
        nations_collection = self.db.nations
        
        if not os.path.exists("../nations_data.json"):
            print("   ⚠️  nations_data.json not found")
            return
        
        with open("../nations_data.json", 'r') as f:
            nations_data = json.load(f)
        
        nation_documents = []
        for nation_id, nation_info in nations_data.get('nations', {}).items():
            try:
                doc = NationSchema.create_document(nation_id, nation_info)
                nation_documents.append(doc)
            except Exception as e:
                self.stats['errors'].append(f"Nation {nation_id}: {e}")
        
        if nation_documents:
            nations_collection.insert_many(nation_documents)
            self.stats['nations'] = len(nation_documents)
            print(f"   ✅ Migrated {len(nation_documents)} nations")
            
            # Update star political data
            self._update_star_political_data(nations_data)
    
    def _migrate_trade_routes(self):
        """Migrate trade route data from JSON"""
        print("\n🛣️  Migrating trade route data...")
        
        trade_routes_collection = self.db.trade_routes
        
        if not os.path.exists("../trade_routes_data.json"):
            print("   ⚠️  trade_routes_data.json not found")
            return
        
        with open("../trade_routes_data.json", 'r') as f:
            trade_data = json.load(f)
        
        route_documents = []
        for category, routes in trade_data.get('trade_routes', {}).items():
            if isinstance(routes, list):
                for route in routes:
                    try:
                        doc = TradeRouteSchema.create_document(route)
                        route_documents.append(doc)
                    except Exception as e:
                        self.stats['errors'].append(f"Trade route {route.get('name', 'unknown')}: {e}")
        
        if route_documents:
            trade_routes_collection.insert_many(route_documents)
            self.stats['trade_routes'] = len(route_documents)
            print(f"   ✅ Migrated {len(route_documents)} trade routes")
    
    def _migrate_stellar_regions(self):
        """Migrate stellar region data from JSON"""
        print("\n🌌 Migrating stellar region data...")
        
        regions_collection = self.db.stellar_regions
        
        if not os.path.exists("../stellar_regions.json"):
            print("   ⚠️  stellar_regions.json not found")
            return
        
        with open("../stellar_regions.json", 'r') as f:
            regions_data = json.load(f)
        
        region_documents = []
        for region in regions_data.get('regions', []):
            try:
                doc = StellarRegionSchema.create_document(region)
                region_documents.append(doc)
            except Exception as e:
                self.stats['errors'].append(f"Region {region.get('name', 'unknown')}: {e}")
        
        if region_documents:
            regions_collection.insert_many(region_documents)
            self.stats['stellar_regions'] = len(region_documents)
            print(f"   ✅ Migrated {len(region_documents)} stellar regions")
    
    def _migrate_planetary_systems(self):
        """Migrate planetary system data"""
        print("\n🪐 Migrating planetary system data...")
        
        systems_collection = self.db.planetary_systems
        
        system_documents = []
        for star_id, planets_list in fictional_planet_systems.items():
            try:
                system_data = {
                    'system_name': f"System {star_id}",
                    'planets': planets_list,
                    'total_planets': len(planets_list),
                    'has_life': any(p.get('atmosphere', '').find('O2') > -1 for p in planets_list),
                    'colonized': False
                }
                doc = PlanetarySystemSchema.create_document(star_id, system_data)
                system_documents.append(doc)
            except Exception as e:
                self.stats['errors'].append(f"System {star_id}: {e}")
        
        if system_documents:
            systems_collection.insert_many(system_documents)
            self.stats['planetary_systems'] = len(system_documents)
            print(f"   ✅ Migrated {len(system_documents)} planetary systems")
    
    def _create_indexes(self):
        """Create indexes for performance"""
        print("\n🔍 Creating database indexes...")
        
        # Stars collection indexes
        stars = self.db.stars
        stars.create_index([("coordinates.x", 1), ("coordinates.y", 1), ("coordinates.z", 1)])
        stars.create_index([("physical_properties.magnitude", 1)])
        stars.create_index([("physical_properties.spectral_class", 1)])
        stars.create_index([("names.primary_name", 1)])
        stars.create_index([("names.fictional_name", 1)])
        stars.create_index([("political.nation_id", 1)])
        stars.create_index([("habitability.category", 1)])
        
        # Nations collection indexes
        nations = self.db.nations
        nations.create_index([("name", 1)])
        nations.create_index([("capital.star_id", 1)])
        
        # Trade routes collection indexes
        trade_routes = self.db.trade_routes
        trade_routes.create_index([("endpoints.from.star_id", 1)])
        trade_routes.create_index([("endpoints.to.star_id", 1)])
        trade_routes.create_index([("control.controlling_nation", 1)])
        trade_routes.create_index([("route_type", 1)])
        
        # Stellar regions collection indexes
        stellar_regions = self.db.stellar_regions
        stellar_regions.create_index([("boundaries.x_range", 1)])
        stellar_regions.create_index([("boundaries.y_range", 1)])
        stellar_regions.create_index([("boundaries.z_range", 1)])
        
        # Planetary systems collection indexes
        planetary_systems = self.db.planetary_systems
        planetary_systems.create_index([("star_id", 1)])
        planetary_systems.create_index([("has_life", 1)])
        planetary_systems.create_index([("colonized", 1)])
        
        print("   ✅ Created performance indexes")
    
    def _save_metadata(self):
        """Save migration metadata"""
        print("\n💾 Saving migration metadata...")
        
        metadata_collection = self.db.metadata
        
        migration_metadata = {
            'migration_date': datetime.utcnow(),
            'stats': self.stats,
            'data_sources': {
                'stars_real': '../stars_output.csv',
                'stars_fictional': '../fictional_stars.csv',
                'nations': '../nations_data.json',
                'trade_routes': '../trade_routes_data.json',
                'stellar_regions': '../stellar_regions.json',
                'planetary_systems': 'fictional_planet_systems'
            },
            'version': '1.0'
        }
        
        metadata_doc = MetadataSchema.create_document('migration', migration_metadata)
        metadata_collection.insert_one(metadata_doc)
        
        print("   ✅ Saved migration metadata")
    
    def _process_star_names(self, stars_df):
        """Process star names (simplified version)"""
        # Add primary name column
        stars_df['primary_name'] = stars_df.apply(
            lambda row: row.get('proper', f"Star {row['id']}"), axis=1
        )
        
        # Add basic name processing
        stars_df['all_names'] = stars_df.apply(
            lambda row: [n for n in [row.get('proper'), row.get('bf')] if n], axis=1
        )
        
        stars_df['designation_type'] = 'catalog'
        stars_df['constellation_full'] = stars_df.get('con', '')
    
    def _add_nation_data_to_stars(self, stars_df):
        """Add nation control data to stars"""
        def get_nation_id(star_id):
            return get_star_nation(star_id)
        
        stars_df['nation_id'] = stars_df['id'].apply(get_nation_id)
    
    def _add_habitability_data_to_stars(self, stars_df):
        """Add basic habitability data (simplified)"""
        stars_df['habitability_score'] = 0.5  # Default score
        stars_df['habitability_category'] = 'Unknown'
        stars_df['exploration_priority'] = 'Low'
        stars_df['habitability_breakdown'] = [{}] * len(stars_df)
        stars_df['parsed_spectral_type'] = [('Unknown', 0, 'V')] * len(stars_df)
    
    def _update_star_political_data(self, nations_data):
        """Update star political data after nations are loaded"""
        stars_collection = self.db.stars
        
        for nation_id, nation_info in nations_data.get('nations', {}).items():
            territories = nation_info.get('territories', [])
            capital_star_id = nation_info.get('capital_star_id')
            
            # Update controlled territories
            for star_id in territories:
                stars_collection.update_one(
                    {'_id': star_id},
                    {'$set': {
                        'political.nation_id': nation_id,
                        'political.controlled_by': nation_id,
                        'political.strategic_importance': 'territory'
                    }}
                )
            
            # Update capital
            if capital_star_id:
                stars_collection.update_one(
                    {'_id': capital_star_id},
                    {'$set': {
                        'political.nation_id': nation_id,
                        'political.controlled_by': nation_id,
                        'political.capital_of': nation_id,
                        'political.strategic_importance': 'capital'
                    }}
                )
    
    def _print_migration_summary(self):
        """Print migration summary"""
        print("\n" + "="*50)
        print("📋 MIGRATION SUMMARY")
        print("="*50)
        print(f"Stars migrated: {self.stats['stars']}")
        print(f"Nations migrated: {self.stats['nations']}")
        print(f"Trade routes migrated: {self.stats['trade_routes']}")
        print(f"Stellar regions migrated: {self.stats['stellar_regions']}")
        print(f"Planetary systems migrated: {self.stats['planetary_systems']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(self.stats['errors']) > 5:
                print(f"   ... and {len(self.stats['errors']) - 5} more")
        else:
            print("\n✅ Migration completed successfully!")
        
        print("="*50)


def main():
    """Main migration function"""
    migrator = DataMigrator()
    success = migrator.migrate_all()
    
    if success:
        print("\n🎉 Data migration completed successfully!")
        print("You can now use the MontyDB-powered Starmap application.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())