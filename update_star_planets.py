#!/usr/bin/env python3
"""
Script to update star data with exoplanet counts
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.config import initialize_database
from models.star_model_db import StarModelDB

def main():
    print("🔄 Updating star exoplanet counts...")
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database")
        return
    
    # Initialize star model
    star_model = StarModelDB()
    
    # Update exoplanet counts
    star_model.update_exoplanet_counts()
    
    print("✅ Star exoplanet counts updated successfully")

if __name__ == "__main__":
    main()