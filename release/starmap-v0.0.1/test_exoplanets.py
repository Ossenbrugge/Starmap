#!/usr/bin/env python3
"""
Test script to verify exoplanet data loading
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.config import initialize_database
from models.exoplanet_model_db import ExoplanetModelDB

def test_exoplanets():
    print("🧪 Testing exoplanet data loading...")
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database")
        return
    
    # Initialize exoplanet model
    exoplanet_model = ExoplanetModelDB()
    
    # Try to migrate just the exoplanet data
    try:
        print("🔄 Migrating exoplanet data...")
        exoplanet_model.migrate_from_json()
        print("✅ Migration completed")
        
        # Test the data retrieval
        real_exoplanets = exoplanet_model.get_exoplanets()
        fictional_exoplanets = exoplanet_model.get_fictional_exoplanets()
        
        print(f"📊 Results:")
        print(f"  Real exoplanets: {len(real_exoplanets)}")
        print(f"  Fictional exoplanets: {len(fictional_exoplanets)}")
        
        # Check if Sol system is loaded
        sol_planets = exoplanet_model.get_exoplanets_by_star_id(500000)
        print(f"  Sol system planets: {len(sol_planets)}")
        
        if sol_planets:
            print("🌍 Sol system planets found:")
            for planet in sol_planets:
                print(f"    - {planet['name']} ({planet['letter']})")
        else:
            print("❌ No Sol system planets found")
        
        print("✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_exoplanets()