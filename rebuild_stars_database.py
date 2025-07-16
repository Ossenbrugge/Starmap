#!/usr/bin/env python3
"""
Comprehensive Star Database Rebuilder
Merges data from multiple sources avoiding duplicates and ensuring clean, searchable data
"""

import os
import sys
import pandas as pd
import numpy as np
import re
from datetime import datetime
from pathlib import Path

# Add paths
sys.path.append('database')
sys.path.append('.')

from database.config import initialize_database, get_database, close_database
from database.schema import StarSchema, ExoplanetSchema
from star_naming import StarNamingSystem
from habitability import HabitabilityAssessment


class StarDatabaseRebuilder:
    def __init__(self):
        self.naming_system = StarNamingSystem()
        self.habitability_assessor = HabitabilityAssessment()
        self.db = None
        self.merged_stars = None
        self.duplicate_stats = {
            'total_records': 0,
            'unique_stars': 0,
            'duplicates_removed': 0,
            'sources_merged': 0
        }
        self.exoplanet_stats = {
            'total_planets': 0,
            'stars_with_planets': 0,
            'planets_matched': 0
        }
        
    def initialize_database_connection(self):
        """Initialize MontyDB connection"""
        if not initialize_database():
            raise Exception("Failed to initialize database!")
        self.db = get_database()
        print(f"✅ Connected to MontyDB with collections: {self.db.list_collection_names()}")
    
    def load_data_files(self):
        """Load all star data files"""
        print("📁 Loading star data files...")
        
        # Define file mappings
        files = {
            'stars_output': 'stars_output.csv',
            'unified_catalog': 'unified_stellar_catalog_31.0pc_20250715_114409.csv',
            'periphery_catalog': 'stellar_catalog_with_periphery_20250715_114409.csv',
            'exoplanet_catalog': 'exoplanet_catalog_20250715_114843.csv'
        }
        
        datasets = {}
        
        for name, filename in files.items():
            if os.path.exists(filename):
                try:
                    df = pd.read_csv(filename, low_memory=False)
                    datasets[name] = df
                    print(f"  ✅ {name}: {len(df)} records")
                except Exception as e:
                    print(f"  ❌ Failed to load {filename}: {e}")
            else:
                print(f"  ⚠️  File not found: {filename}")
        
        if not datasets:
            raise Exception("No data files found!")
        
        return datasets
    
    def load_exoplanet_data(self):
        """Load and process exoplanet data"""
        print("🪐 Loading exoplanet data...")
        
        exoplanet_file = 'exoplanet_catalog_20250715_114843.csv'
        if not os.path.exists(exoplanet_file):
            print(f"  ⚠️  Exoplanet file not found: {exoplanet_file}")
            return {}
        
        try:
            df = pd.read_csv(exoplanet_file, low_memory=False)
            print(f"  ✅ Loaded {len(df)} exoplanet records")
            
            # Group planets by host star
            exoplanet_by_host = {}
            exoplanet_by_hip = {}
            
            for _, planet_row in df.iterrows():
                # Clean the planet data
                planet_data = {}
                for col, value in planet_row.items():
                    # Replace dots in field names to avoid MontyDB issues
                    clean_col = col.replace('.', '_')
                    cleaned_value = self.clean_and_normalize_value(value)
                    planet_data[clean_col] = cleaned_value
                
                # Group by host star name
                host_name = planet_data.get('hostname')
                if host_name:
                    if host_name not in exoplanet_by_host:
                        exoplanet_by_host[host_name] = []
                    exoplanet_by_host[host_name].append(planet_data)
                
                # Group by HIP ID for easier matching
                hip_id = planet_data.get('host_hip_id')
                if hip_id and hip_id != 0:
                    if hip_id not in exoplanet_by_hip:
                        exoplanet_by_hip[hip_id] = []
                    exoplanet_by_hip[hip_id].append(planet_data)
            
            self.exoplanet_stats['total_planets'] = len(df)
            print(f"  📊 Planets grouped by {len(exoplanet_by_host)} host stars")
            print(f"  📊 {len(exoplanet_by_hip)} stars have HIP IDs for matching")
            
            return {
                'by_host_name': exoplanet_by_host,
                'by_hip_id': exoplanet_by_hip,
                'raw_data': df
            }
            
        except Exception as e:
            print(f"  ❌ Error loading exoplanet data: {e}")
            return {}
    
    def clean_and_normalize_value(self, value):
        """Clean and normalize a data value"""
        if pd.isna(value) or value == '' or str(value).lower() in ['null', 'nan', 'none']:
            return None
        
        # Convert to string and clean whitespace
        cleaned = str(value).strip()
        
        # Remove multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Handle special cases
        if cleaned.lower() in ['null', 'nan', 'none', '']:
            return None
        
        # Try to convert numeric values
        try:
            if '.' in cleaned or 'e' in cleaned.lower():
                return float(cleaned)
            elif cleaned.isdigit() or (cleaned.startswith('-') and cleaned[1:].isdigit()):
                return int(cleaned)
        except ValueError:
            pass
        
        return cleaned
    
    def extract_star_identifiers(self, row):
        """Extract all possible star identifiers from a row"""
        identifiers = {}
        
        # Primary identifiers
        for col in ['id', 'hip', 'hd', 'hr', 'gaia_id', 'tic_id']:
            val = self.clean_and_normalize_value(row.get(col))
            if val and val != 0:
                identifiers[col] = val
        
        # Gliese identifiers  
        gl = self.clean_and_normalize_value(row.get('gl'))
        if gl:
            # Clean up Gliese format
            gl_clean = str(gl).replace('Gl ', '').replace('GJ ', '').strip()
            if gl_clean:
                identifiers['gliese'] = gl_clean
        
        # Coordinates for position matching
        ra = self.clean_and_normalize_value(row.get('ra'))
        dec = self.clean_and_normalize_value(row.get('dec'))
        if ra is not None and dec is not None:
            identifiers['coordinates'] = (float(ra), float(dec))
        
        # Proper name
        proper = self.clean_and_normalize_value(row.get('proper'))
        if proper:
            identifiers['proper_name'] = proper
        
        return identifiers
    
    def find_duplicate_stars(self, datasets):
        """Find and group duplicate stars across datasets"""
        print("🔍 Identifying duplicate stars...")
        
        all_stars = []
        
        # Process each dataset
        for source_name, df in datasets.items():
            print(f"  Processing {source_name}...")
            
            for idx, row in df.iterrows():
                identifiers = self.extract_star_identifiers(row)
                if identifiers:  # Only process if we have some identifiers
                    star_info = {
                        'source': source_name,
                        'source_index': idx,
                        'identifiers': identifiers,
                        'data': row.to_dict()
                    }
                    all_stars.append(star_info)
        
        print(f"  📊 Total star records: {len(all_stars)}")
        self.duplicate_stats['total_records'] = len(all_stars)
        
        # Group by identifiers
        star_groups = {}
        
        for star in all_stars:
            group_key = self.generate_group_key(star['identifiers'])
            
            if group_key not in star_groups:
                star_groups[group_key] = []
            star_groups[group_key].append(star)
        
        # Identify duplicates
        unique_groups = []
        duplicate_count = 0
        
        for group_key, stars in star_groups.items():
            if len(stars) > 1:
                duplicate_count += len(stars) - 1
            unique_groups.append(stars)
        
        print(f"  📊 Unique star groups: {len(unique_groups)}")
        print(f"  📊 Duplicates removed: {duplicate_count}")
        
        self.duplicate_stats['unique_stars'] = len(unique_groups)
        self.duplicate_stats['duplicates_removed'] = duplicate_count
        
        return unique_groups
    
    def generate_group_key(self, identifiers):
        """Generate a unique key for grouping duplicate stars"""
        # Priority order for matching
        priority_keys = ['hip', 'hd', 'gliese', 'proper_name', 'coordinates']
        
        for key in priority_keys:
            if key in identifiers:
                if key == 'coordinates':
                    # Round coordinates for fuzzy matching
                    ra, dec = identifiers[key]
                    return f"coord_{round(ra, 4)}_{round(dec, 4)}"
                else:
                    return f"{key}_{identifiers[key]}"
        
        # Fallback to first available identifier
        if identifiers:
            first_key = list(identifiers.keys())[0]
            return f"{first_key}_{identifiers[first_key]}"
        
        return "unknown"
    
    def merge_star_group(self, star_group):
        """Merge multiple records of the same star into a single record"""
        if len(star_group) == 1:
            return star_group[0]['data']
        
        # Choose primary record (prefer stars_output, then unified, then others)
        source_priority = ['stars_output', 'unified_catalog', 'periphery_catalog', 'exoplanet_catalog']
        
        primary_star = None
        for source in source_priority:
            for star in star_group:
                if star['source'] == source:
                    primary_star = star
                    break
            if primary_star:
                break
        
        if not primary_star:
            primary_star = star_group[0]
        
        merged_data = primary_star['data'].copy()
        
        # Merge additional data from other sources
        for star in star_group:
            if star == primary_star:
                continue
            
            star_data = star['data']
            
            # Merge fields, prioritizing non-null values
            for field, value in star_data.items():
                cleaned_value = self.clean_and_normalize_value(value)
                
                if cleaned_value is not None:
                    # If primary doesn't have this field or it's null, use the new value
                    primary_value = self.clean_and_normalize_value(merged_data.get(field))
                    
                    if primary_value is None:
                        merged_data[field] = cleaned_value
                    elif field in ['estimated_mass', 'spectral_type', 'teff_gspphot', 'best_mass', 'best_spectral_type']:
                        # For these fields, prefer non-null values from any source
                        merged_data[field] = cleaned_value
        
        # Add source tracking
        sources = [star['source'] for star in star_group]
        merged_data['data_sources'] = '; '.join(set(sources))
        merged_data['primary_source'] = primary_star['source']
        
        self.duplicate_stats['sources_merged'] += len(sources) - 1
        
        return merged_data
    
    def clean_star_data(self, star_data):
        """Clean and normalize star data"""
        cleaned = {}
        
        for field, value in star_data.items():
            cleaned_value = self.clean_and_normalize_value(value)
            cleaned[field] = cleaned_value
        
        # Ensure required numeric fields with better validation
        numeric_fields = {
            'ra': 0.0,
            'dec': 0.0, 
            'dist': 0.0,
            'mag': 0.0,
            'absmag': 0.0,
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'pmra': 0.0,
            'pmdec': 0.0,
            'rv': 0.0,
            'ci': 0.0,
            'lum': 1.0,
            'vx': 0.0,
            'vy': 0.0,
            'vz': 0.0
        }
        
        for field, default_value in numeric_fields.items():
            if field in cleaned and cleaned[field] is not None:
                try:
                    # Handle various string representations
                    val = str(cleaned[field]).strip()
                    if val.lower() in ['', 'null', 'nan', 'none']:
                        cleaned[field] = default_value
                    else:
                        cleaned[field] = float(val)
                except (ValueError, TypeError):
                    cleaned[field] = default_value
            else:
                cleaned[field] = default_value
        
        # Clean spectral type
        if 'spect' in cleaned and cleaned['spect']:
            cleaned['spect'] = str(cleaned['spect']).strip()
        
        # Generate or use existing star ID
        if 'id' not in cleaned or not cleaned['id']:
            # Generate ID from HIP or other identifier
            if cleaned.get('hip'):
                cleaned['id'] = int(float(cleaned['hip']))
            elif cleaned.get('hd'):
                cleaned['id'] = int(float(cleaned['hd'])) + 100000  # Offset to avoid HIP conflicts
            else:
                # Generate based on coordinates
                ra_int = int(cleaned.get('ra', 0) * 1000)
                dec_int = int(abs(cleaned.get('dec', 0)) * 1000)
                cleaned['id'] = ra_int * 10000 + dec_int + 500000  # Large offset
        
        return cleaned
    
    def match_exoplanets_to_star(self, star_data, exoplanet_data):
        """Match exoplanets to a star and return planet information"""
        planets = []
        
        if not exoplanet_data:
            return planets
        
        # Try matching by HIP ID first (most reliable)
        hip_id = star_data.get('hip')
        if hip_id and hip_id != 0:
            planets_by_hip = exoplanet_data.get('by_hip_id', {}).get(hip_id, [])
            if planets_by_hip:
                planets.extend(planets_by_hip)
                return planets
        
        # Try matching by proper name
        proper_name = star_data.get('proper')
        if proper_name:
            planets_by_name = exoplanet_data.get('by_host_name', {}).get(proper_name, [])
            if planets_by_name:
                planets.extend(planets_by_name)
                return planets
        
        # Try matching by primary name
        primary_name = star_data.get('primary_name')
        if primary_name:
            planets_by_name = exoplanet_data.get('by_host_name', {}).get(primary_name, [])
            if planets_by_name:
                planets.extend(planets_by_name)
        
        return planets

    def calculate_enhanced_data(self, star_data, exoplanet_data=None):
        """Calculate additional data like habitability, naming, and exoplanets"""
        # Generate proper names using naming system
        star_series = pd.Series(star_data)
        naming_info = self.naming_system.generate_star_name(star_series)
        
        # Add naming information
        star_data.update({
            'primary_name': naming_info['primary_name'],
            'all_names': naming_info['all_names'],
            'catalog_ids': naming_info['catalog_ids'],
            'constellation_full': naming_info['constellation_full'],
            'designation_type': naming_info['designation_type']
        })
        
        # Match exoplanets to this star
        planets = self.match_exoplanets_to_star(star_data, exoplanet_data)
        star_data['exoplanets'] = planets
        star_data['has_exoplanets'] = len(planets) > 0
        star_data['exoplanet_count'] = len(planets)
        
        if len(planets) > 0:
            self.exoplanet_stats['stars_with_planets'] += 1
            self.exoplanet_stats['planets_matched'] += len(planets)
        
        # Calculate habitability if we have the required data
        try:
            if star_data.get('spect') and star_data.get('spect').strip():
                habitability_data = self.habitability_assessor.calculate_habitability_score(star_data)
                star_data.update({
                    'habitability_score': habitability_data.get('score', 0.0),
                    'habitability_category': habitability_data.get('category', 'Unknown'),
                    'exploration_priority': habitability_data.get('priority', 'Unknown'),
                    'habitability_breakdown': habitability_data.get('breakdown', {}),
                    'parsed_spectral_type': habitability_data.get('parsed_spectral_type', ('Unknown', 0, 'V'))
                })
        except Exception as e:
            print(f"  ⚠️  Could not calculate habitability for star {star_data.get('id', 'unknown')}: {e}")
            star_data.update({
                'habitability_score': 0.0,
                'habitability_category': 'Unknown',
                'exploration_priority': 'Unknown',
                'habitability_breakdown': {},
                'parsed_spectral_type': ('Unknown', 0, 'V')
            })
        
        return star_data
    
    def rebuild_database(self):
        """Main method to rebuild the star database"""
        print("🚀 Starting star database rebuild...")
        print("=" * 60)
        
        # Initialize database
        self.initialize_database_connection()
        
        # Load data files
        datasets = self.load_data_files()
        
        # Load exoplanet data
        exoplanet_data = self.load_exoplanet_data()
        
        # Find and group duplicates
        star_groups = self.find_duplicate_stars(datasets)
        
        # Process and merge stars
        print("🔧 Processing and merging star data...")
        processed_stars = []
        
        for i, star_group in enumerate(star_groups):
            if i % 1000 == 0:
                print(f"  Processing star {i+1}/{len(star_groups)}...")
            
            try:
                # Merge duplicate records
                merged_star = self.merge_star_group(star_group)
                
                # Clean and normalize data
                cleaned_star = self.clean_star_data(merged_star)
                
                # Calculate enhanced data (naming, habitability, exoplanets)
                enhanced_star = self.calculate_enhanced_data(cleaned_star, exoplanet_data)
                
                processed_stars.append(enhanced_star)
                
            except Exception as e:
                print(f"  ⚠️  Error processing star group {i}: {e}")
                continue
        
        print(f"✅ Processed {len(processed_stars)} stars")
        
        # Clear existing collections
        print("🗑️  Clearing existing collections...")
        self.db.stars.drop()
        self.db.exoplanets.drop()
        
        # Insert processed stars
        print("💾 Inserting stars into database...")
        star_documents = []
        
        for star_data in processed_stars:
            try:
                star_doc = StarSchema.create_document(star_data)
                star_documents.append(star_doc)
            except Exception as e:
                print(f"  ⚠️  Error creating document for star {star_data.get('id', 'unknown')}: {e}")
                continue
        
        if star_documents:
            # Insert in batches
            batch_size = 1000
            for i in range(0, len(star_documents), batch_size):
                batch = star_documents[i:i + batch_size]
                try:
                    self.db.stars.insert_many(batch)
                    print(f"  ✅ Inserted batch {i//batch_size + 1}/{(len(star_documents)-1)//batch_size + 1}")
                except Exception as e:
                    print(f"  ❌ Error inserting batch {i//batch_size + 1}: {e}")
        
        # Insert exoplanet data into separate collection
        print("🪐 Inserting exoplanets into database...")
        if exoplanet_data and 'raw_data' in exoplanet_data:
            exoplanet_documents = []
            
            for _, planet_row in exoplanet_data['raw_data'].iterrows():
                try:
                    # Clean planet data
                    planet_data = {}
                    for col, value in planet_row.items():
                        # Replace dots in field names to avoid MontyDB issues
                        clean_col = col.replace('.', '_')
                        planet_data[clean_col] = self.clean_and_normalize_value(value)
                    
                    planet_doc = ExoplanetSchema.create_document(planet_data)
                    exoplanet_documents.append(planet_doc)
                except Exception as e:
                    print(f"  ⚠️  Error creating exoplanet document: {e}")
                    continue
            
            if exoplanet_documents:
                # Insert in batches
                batch_size = 100
                for i in range(0, len(exoplanet_documents), batch_size):
                    batch = exoplanet_documents[i:i + batch_size]
                    try:
                        self.db.exoplanets.insert_many(batch)
                        print(f"  ✅ Inserted exoplanet batch {i//batch_size + 1}/{(len(exoplanet_documents)-1)//batch_size + 1}")
                    except Exception as e:
                        print(f"  ❌ Error inserting exoplanet batch {i//batch_size + 1}: {e}")
        
        # Create indexes for performance
        print("📇 Creating database indexes...")
        try:
            self.db.stars.create_index([("coordinates.ra", 1), ("coordinates.dec", 1)])
            self.db.stars.create_index([("physical_properties.magnitude", 1)])
            self.db.stars.create_index([("physical_properties.spectral_class", 1)])
            self.db.stars.create_index([("names.primary_name", "text")])
            self.db.stars.create_index([("catalog_data.hip", 1)])
            self.db.stars.create_index([("catalog_data.hd", 1)])
            self.db.stars.create_index([("has_exoplanets", 1)])
            self.db.stars.create_index([("exoplanet_count", 1)])
            
            # Exoplanet indexes
            self.db.exoplanets.create_index([("host_star.name", 1)])
            self.db.exoplanets.create_index([("host_star.hip_id", 1)])
            self.db.exoplanets.create_index([("discovery.year", 1)])
            print("  ✅ Indexes created")
        except Exception as e:
            print(f"  ⚠️  Warning: Could not create some indexes: {e}")
        
        # Print final statistics
        final_star_count = self.db.stars.count_documents({})
        final_exoplanet_count = self.db.exoplanets.count_documents({})
        stars_with_planets = self.db.stars.count_documents({"has_exoplanets": True})
        
        print("\n" + "=" * 60)
        print("📊 REBUILD COMPLETE")
        print("=" * 60)
        print(f"Total input records: {self.duplicate_stats['total_records']}")
        print(f"Unique stars identified: {self.duplicate_stats['unique_stars']}")
        print(f"Duplicate records removed: {self.duplicate_stats['duplicates_removed']}")
        print(f"Sources merged: {self.duplicate_stats['sources_merged']}")
        print(f"Stars inserted into database: {final_star_count}")
        print(f"Exoplanets inserted into database: {final_exoplanet_count}")
        print(f"Stars with confirmed exoplanets: {stars_with_planets}")
        print(f"Exoplanets matched to stars: {self.exoplanet_stats['planets_matched']}")
        print(f"Data quality: {(final_star_count/self.duplicate_stats['total_records']*100):.1f}% retention")
        
        return final_star_count
    
    def verify_database(self):
        """Verify the rebuilt database"""
        print("\n🔍 Verifying database...")
        
        # Check total counts
        total_stars = self.db.stars.count_documents({})
        total_exoplanets = self.db.exoplanets.count_documents({})
        print(f"Total stars: {total_stars}")
        print(f"Total exoplanets: {total_exoplanets}")
        
        # Check for proper names
        named_stars = self.db.stars.count_documents({"names.proper_name": {"$ne": None}})
        print(f"Stars with proper names: {named_stars}")
        
        # Check spectral types
        typed_stars = self.db.stars.count_documents({"physical_properties.spectral_class": {"$ne": ""}})
        print(f"Stars with spectral types: {typed_stars}")
        
        # Check habitability scores
        habitable_stars = self.db.stars.count_documents({"habitability.score": {"$gt": 0.5}})
        print(f"Potentially habitable stars: {habitable_stars}")
        
        # Check exoplanet integration
        stars_with_planets = self.db.stars.count_documents({"exoplanets.has_planets": True})
        print(f"Stars with confirmed exoplanets: {stars_with_planets}")
        
        # Sample some stars
        print("\n📋 Sample stars:")
        sample_stars = list(self.db.stars.find({}).limit(5))
        for star in sample_stars:
            planet_count = star.get('exoplanets', {}).get('count', 0)
            planet_info = f" ({planet_count} planets)" if planet_count > 0 else ""
            print(f"  ⭐ {star['names']['primary_name']} ({star['physical_properties']['spectral_class']}) - Mag: {star['physical_properties']['magnitude']}{planet_info}")
        
        # Sample some exoplanet systems
        print("\n🪐 Sample exoplanet systems:")
        sample_planet_stars = list(self.db.stars.find({"exoplanets.has_planets": True}).limit(3))
        for star in sample_planet_stars:
            planet_count = star.get('exoplanets', {}).get('count', 0)
            print(f"  🌟 {star['names']['primary_name']}: {planet_count} confirmed planets")
    
    def cleanup(self):
        """Clean up resources"""
        if self.db:
            close_database()


def main():
    """Main entry point"""
    rebuilder = StarDatabaseRebuilder()
    
    try:
        star_count = rebuilder.rebuild_database()
        rebuilder.verify_database()
        
        print("\n🎉 Star database rebuild completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n💥 Rebuild failed: {e}")
        return 1
    
    finally:
        rebuilder.cleanup()


if __name__ == "__main__":
    exit(main())