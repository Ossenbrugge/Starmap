#!/usr/bin/env python3
"""
Script to update Sol specifically with its planetary system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.config import initialize_database, get_database

def main():
    print("🌍 Updating Sol with planetary system data...")
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database")
        return
    
    db = get_database()
    stars = db.stars
    fictional_exoplanets = db.fictional_exoplanets
    
    # Get Sol's data
    sol = stars.find_one({'_id': 500000})
    if not sol:
        print("❌ Sol not found in database")
        return
    
    print(f"Found Sol: {sol['names']['primary_name']}")
    
    # Count Sol's planets
    planet_count = fictional_exoplanets.count_documents({'star_id': 500000})
    print(f"Found {planet_count} planets for Sol")
    
    # Update Sol with planet data
    if planet_count > 0:
        # Use the correct update format for nested fields
        result = stars.update_one(
            {'_id': 500000},
            {
                '$set': {
                    'exoplanets': {
                        'count': planet_count,
                        'has_planets': True
                    }
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"✅ Updated Sol with {planet_count} planets")
        else:
            print("ℹ️ Sol already up to date")
    else:
        print("❌ No planets found for Sol")
    
    # Verify the update
    updated_sol = stars.find_one({'_id': 500000})
    print(f"Sol now shows: {updated_sol['exoplanets']['count']} planets, has_planets: {updated_sol['exoplanets']['has_planets']}")

if __name__ == "__main__":
    main()