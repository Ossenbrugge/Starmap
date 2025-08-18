#!/usr/bin/env python3
"""
Test MontyDB update operations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import initialize_database, get_database

def main():
    print("[TEST] Testing MontyDB update operations...")
    
    # Initialize database
    if not initialize_database():
        print("[FAIL] Failed to initialize database")
        return
    
    db = get_database()
    stars = db.stars
    
    # Get Sol's current data
    print("Before update:")
    sol = stars.find_one({'_id': 500000})
    if sol:
        print(f"  Exoplanets: {sol['exoplanets']}")
    else:
        print("  Sol not found")
        return
    
    # Try different update approaches
    print("\nTrying approach 1: Direct nested field update...")
    result1 = stars.update_one(
        {'_id': 500000},
        {'$set': {'exoplanets.count': 8, 'exoplanets.has_planets': True}}
    )
    print(f"  Result: matched={result1.matched_count}, modified={result1.modified_count}")
    
    # Check result
    sol = stars.find_one({'_id': 500000})
    print(f"  After: {sol['exoplanets']}")
    
    print("\nTrying approach 2: Full object replacement...")
    result2 = stars.update_one(
        {'_id': 500000},
        {'$set': {'exoplanets': {'count': 8, 'has_planets': True}}}
    )
    print(f"  Result: matched={result2.matched_count}, modified={result2.modified_count}")
    
    # Check final result
    sol = stars.find_one({'_id': 500000})
    print(f"  Final: {sol['exoplanets']}")

if __name__ == "__main__":
    main()