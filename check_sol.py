#!/usr/bin/env python3
"""
Check Sol data directly from database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.config import initialize_database, get_database

def main():
    print("🔍 Checking Sol data in database...")
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database")
        return
    
    db = get_database()
    stars = db.stars
    
    # Get Sol directly from database
    sol = stars.find_one({'_id': 500000})
    if sol:
        print(f"Found Sol: {sol['names']['primary_name']}")
        print(f"Exoplanets: {sol['exoplanets']}")
        print(f"Full data: {sol}")
    else:
        print("❌ Sol not found")

if __name__ == "__main__":
    main()