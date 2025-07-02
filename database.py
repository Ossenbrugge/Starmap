#!/usr/bin/env python3
"""
Database module for Starmap application
Handles MongoDB embedded database operations
"""

import pandas as pd
import pymongo
from pymongo import MongoClient
import json
import os
from typing import List, Dict, Any, Optional

class StarmapDatabase:
    def __init__(self, db_name: str = "starmap_db", host: str = "localhost", port: int = 27017):
        """Initialize database connection"""
        self.db_name = db_name
        self.host = host
        self.port = port
        self.client = None
        self.db = None
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.host, self.port, serverSelectionTimeoutMS=5000)
            self.client.server_info()  # Test connection
            self.db = self.client[self.db_name]
            print(f"Connected to MongoDB at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False
    
    def import_csv_data(self, csv_file: str) -> bool:
        """Import star data from CSV file"""
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            print(f"Loaded {len(df)} stars from {csv_file}")
            
            # Clean and prepare data
            df = df.fillna('')  # Replace NaN with empty strings
            
            # Convert to dictionary format
            stars_data = df.to_dict('records')
            
            # Clear existing data
            self.db.stars.drop()
            
            # Insert new data
            result = self.db.stars.insert_many(stars_data)
            print(f"Inserted {len(result.inserted_ids)} stars into database")
            
            # Create indexes for better performance
            self.db.stars.create_index([("proper", 1)])
            self.db.stars.create_index([("x", 1), ("y", 1), ("z", 1)])
            self.db.stars.create_index([("mag", 1)])
            
            return True
            
        except Exception as e:
            print(f"Error importing CSV data: {e}")
            return False
    
    def get_star_by_id(self, star_id: int) -> Optional[Dict]:
        """Get star by ID"""
        return self.db.stars.find_one({"id": star_id})
    
    def get_stars_in_range(self, x_range: tuple, y_range: tuple, z_range: tuple = None) -> List[Dict]:
        """Get stars within specified coordinate ranges"""
        query = {
            "x": {"$gte": x_range[0], "$lte": x_range[1]},
            "y": {"$gte": y_range[0], "$lte": y_range[1]}
        }
        
        if z_range:
            query["z"] = {"$gte": z_range[0], "$lte": z_range[1]}
            
        return list(self.db.stars.find(query))
    
    def get_bright_stars(self, mag_limit: float = 6.0) -> List[Dict]:
        """Get stars brighter than magnitude limit"""
        return list(self.db.stars.find({"mag": {"$lte": mag_limit}}).sort("mag", 1))
    
    def search_stars(self, name: str) -> List[Dict]:
        """Search stars by name"""
        return list(self.db.stars.find({
            "$or": [
                {"proper": {"$regex": name, "$options": "i"}},
                {"bayer": {"$regex": name, "$options": "i"}},
                {"con": {"$regex": name, "$options": "i"}}
            ]
        }))
    
    def get_all_stars(self, limit: int = None) -> List[Dict]:
        """Get all stars with optional limit"""
        query = self.db.stars.find()
        if limit:
            query = query.limit(limit)
        return list(query)
    
    def add_planet_system(self, star_id: int, planets: List[Dict]) -> bool:
        """Add planetary system to a star"""
        try:
            result = self.db.stars.update_one(
                {"id": star_id},
                {"$set": {"planets": planets}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error adding planet system: {e}")
            return False
    
    def get_star_with_planets(self, star_id: int) -> Optional[Dict]:
        """Get star with its planetary system"""
        return self.db.stars.find_one({"id": star_id})
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("Database connection closed")

def init_sample_planets():
    """Initialize sample planetary systems for demonstration"""
    sample_systems = {
        0: [  # Sol system
            {"name": "Mercury", "type": "terrestrial", "distance_au": 0.39, "mass_earth": 0.055, "radius_earth": 0.38},
            {"name": "Venus", "type": "terrestrial", "distance_au": 0.72, "mass_earth": 0.815, "radius_earth": 0.95},
            {"name": "Earth", "type": "terrestrial", "distance_au": 1.0, "mass_earth": 1.0, "radius_earth": 1.0},
            {"name": "Mars", "type": "terrestrial", "distance_au": 1.52, "mass_earth": 0.107, "radius_earth": 0.53}
        ],
        16496: [  # Epsilon Eridani system
            {"name": "Epsilon Eridani b", "type": "gas giant", "distance_au": 3.4, "mass_earth": 317, "radius_earth": 4.1}
        ]
    }
    return sample_systems

if __name__ == "__main__":
    # Test database functionality
    db = StarmapDatabase()
    if db.connect():
        print("Database connection successful!")
        
        # Import CSV data if available
        if os.path.exists("stars_output.csv"):
            db.import_csv_data("stars_output.csv")
            
            # Add sample planetary systems
            sample_systems = init_sample_planets()
            for star_id, planets in sample_systems.items():
                db.add_planet_system(star_id, planets)
                print(f"Added {len(planets)} planets to star {star_id}")
        
        db.close()
    else:
        print("Failed to connect to database!")