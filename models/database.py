"""
Database Models and Data Management
Central database interface for the Starmap application
"""

import json
import os
from typing import Dict, List, Any, Optional


class Database:
    """
    Central database class that manages all data operations
    using in-memory storage with file system persistence
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the database with data directory

        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        self._ensure_data_dir()
        self._load_all_data()

    def _ensure_data_dir(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"✅ Created data directory: {self.data_dir}")

    def _load_all_data(self):
        """Load all data files into memory"""
        print("📊 Loading database into memory...")

        # Load data with proper error handling
        self._stars = self._load_json_file("stars.json", [])
        self._exoplanets = self._load_json_file("exoplanets.json", [])
        self._nations = self._load_json_file("nations.json", [])
        self._trade_routes = self._load_json_file("trade_routes.json", [])
        self._stellar_regions = self._load_json_file("stellar_regions.json", [])
        self._fictional_exoplanets = self._load_json_file("fictional_exoplanets.json", [])

        print("🎉 Database loaded successfully!")

    def _load_json_file(self, filename: str, default_data: Any = None) -> Any:
        """
        Load JSON file with safe error handling

        Args:
            filename: Name of the file to load
            default_data: Default data to return if file doesn't exist or is invalid

        Returns:
            Parsed JSON data or default_data
        """
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}, using default")
            return default_data if default_data is not None else {}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded {filename}")
            return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"❌ Error loading {filename}: {e}, using default")
            return default_data if default_data is not None else {}

    def _save_json_file(self, filename: str, data: Any):
        """
        Save data to JSON file

        Args:
            filename: Name of the file to save
            data: Data to save
        """
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {filename}")
        except IOError as e:
            print(f"❌ Error saving {filename}: {e}")

    # Stars methods
    def get_stars(self, limit: int = 1000, mag_limit: float = 8.0,
                  spectral_type: str = "") -> List[Dict[str, Any]]:
        """
        Retrieve stars from database with optional filtering

        Args:
            limit: Maximum number of stars to return (default: 1000)
            mag_limit: Magnitude limit filter (default: 8.0)
            spectral_type: Spectral class filter (optional)

        Returns:
            List of star dictionaries
        """
        try:
            filtered_stars = []

            for star in self._stars:
                # Apply magnitude filter
                if self._get_star_magnitude(star) > mag_limit:
                    continue

                # Apply spectral type filter if specified
                if spectral_type and spectral_type.lower() not in self._get_star_spectral_class(star).lower():
                    continue

                filtered_stars.append(star)

            # Apply limit
            return filtered_stars[:limit]

        except Exception as e:
            print(f"❌ Error getting stars: {e}")
            return []

    def _get_star_magnitude(self, star: Dict[str, Any]) -> float:
        """Extract magnitude from star data"""
        return star.get('magnitude', star.get('mag', 999))

    def _get_star_spectral_class(self, star: Dict[str, Any]) -> str:
        """Extract spectral class from star data"""
        return star.get('spectral_class', star.get('spect', ''))

    def get_star_by_id(self, star_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific star by ID

        Args:
            star_id: The star ID to find

        Returns:
            Star dictionary or None if not found
        """
        try:
            for star in self._stars:
                if star.get('id') == star_id:
                    return star
            return None
        except Exception as e:
            print(f"❌ Error getting star by ID {star_id}: {e}")
            return None

    def add_star(self, star_data: Dict[str, Any]) -> bool:
        """
        Add a new star to the database

        Args:
            star_data: Star data dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            self._stars.append(star_data)
            self._save_json_file("stars.json", self._stars)
            return True
        except Exception as e:
            print(f"❌ Error adding star: {e}")
            return False

    def update_star(self, star_id: int, star_data: Dict[str, Any]) -> bool:
        """
        Update an existing star

        Args:
            star_id: ID of the star to update
            star_data: Updated star data

        Returns:
            True if successful, False otherwise
        """
        try:
            for i, star in enumerate(self._stars):
                if star.get('id') == star_id:
                    star_data['id'] = star_id
                    self._stars[i] = star_data
                    self._save_json_file("stars.json", self._stars)
                    return True
            return False
        except Exception as e:
            print(f"❌ Error updating star {star_id}: {e}")
            return False

    def delete_star(self, star_id: int) -> bool:
        """
        Delete a star by ID

        Args:
            star_id: ID of the star to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            original_length = len(self._stars)
            self._stars = [star for star in self._stars if star.get('id') != star_id]

            if len(self._stars) < original_length:
                self._save_json_file("stars.json", self._stars)
                return True
            return False
        except Exception as e:
            print(f"❌ Error deleting star {star_id}: {e}")
            return False

    # Nations methods
    def get_nations(self) -> List[Dict[str, Any]]:
        """Retrieve all nations"""
        try:
            return self._nations.copy()
        except Exception as e:
            print(f"❌ Error getting nations: {e}")
            return []

    def get_nation_by_id(self, nation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific nation by ID"""
        try:
            for nation in self._nations:
                if nation.get('id') == nation_id:
                    return nation
            return None
        except Exception as e:
            print(f"❌ Error getting nation by ID {nation_id}: {e}")
            return None

    def add_nation(self, nation_data: Dict[str, Any]) -> bool:
        """Add a new nation"""
        try:
            self._nations.append(nation_data)
            self._save_json_file("nations.json", self._nations)
            return True
        except Exception as e:
            print(f"❌ Error adding nation: {e}")
            return False

    # Exoplanets methods
    def get_exoplanets(self) -> List[Dict[str, Any]]:
        """Retrieve all exoplanets"""
        try:
            return self._exoplanets.copy()
        except Exception as e:
            print(f"❌ Error getting exoplanets: {e}")
            return []

    def get_fictional_exoplanets(self) -> List[Dict[str, Any]]:
        """Retrieve all fictional exoplanets"""
        try:
            return self._fictional_exoplanets.copy()
        except Exception as e:
            print(f"❌ Error getting fictional exoplanets: {e}")
            return []

    def get_trade_routes(self) -> List[Dict[str, Any]]:
        """Retrieve all trade routes"""
        try:
            return self._trade_routes.copy()
        except Exception as e:
            print(f"❌ Error getting trade routes: {e}")
            return []

    def get_stellar_regions(self) -> List[Dict[str, Any]]:
        """Retrieve all stellar regions"""
        try:
            return self._stellar_regions.copy()
        except Exception as e:
            print(f"❌ Error getting stellar regions: {e}")
            return []

    # Statistics methods
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            return {
                'stars': len(self._stars),
                'nations': len(self._nations),
                'exoplanets': len(self._exoplanets),
                'fictional_exoplanets': len(self._fictional_exoplanets),
                'trade_routes': len(self._trade_routes),
                'stellar_regions': len(self._stellar_regions)
            }
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}

    def reload_data(self):
        """Reload all data from files"""
        print("🔄 Reloading database data...")
        self._load_all_data()
        print("✅ Database reloaded successfully!")

    def search_stars(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search stars by name or ID

        Args:
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of matching stars
        """
        try:
            results = []
            query_lower = query.lower()

            for star in self._stars:
                if query_lower in star.get('name', '').lower():
                    results.append(star)
                elif str(query_lower) in str(star.get('id', '')):
                    results.append(star)

            return results[:limit]
        except Exception as e:
            print(f"❌ Error searching stars: {e}")
            return []

    def get_system_stats(self, star_id: int) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific stellar system"""
        try:
            star = self.get_star_by_id(star_id)
            if not star:
                return None

            system_stats = {
                'star': star,
                'exoplanets': [p for p in self._exoplanets if p.get('hostname') == star.get('name')],
                'fictional_exoplanets': [p for p in self._fictional_exoplanets if p.get('host_star') == star.get('name')]
            }

            return system_stats
        except Exception as e:
            print(f"❌ Error getting system stats for star {star_id}: {e}")
            return None
