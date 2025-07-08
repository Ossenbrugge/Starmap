# Fictional Nations for the Starmap Application
# Political entities and their territorial control in the galaxy

import json
import os

# Load nations data from JSON file
def load_nations_data():
    """Load nations data from JSON file"""
    try:
        data_file = os.path.join(os.path.dirname(__file__), 'nations_data.json')
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("Warning: nations_data.json not found, using fallback data")
        return get_fallback_data()
    except json.JSONDecodeError as e:
        print(f"Error parsing nations_data.json: {e}")
        return get_fallback_data()

def get_fallback_data():
    """Fallback data in case JSON file is not available"""
    return {
        "nations": {
            "neutral_zone": {
                "name": "Neutral Zone",
                "full_name": "Neutral Systems Territory",
                "capital_system": None,
                "capital_star_id": None,
                "government_type": "Neutral Territory",
                "color": "#9E9E9E",
                "border_color": "#616161",
                "established_year": 2267,
                "description": "Neutral buffer zones between major powers.",
                "territories": [],
                "specialties": ["Diplomacy", "Free Trade", "Mediation"],
                "population": "Variable",
                "military_strength": "Peacekeeping Forces Only"
            }
        }
    }

# Load the data
nations_data = load_nations_data()
fictional_nations = nations_data.get('nations', {})

# Star-to-nation mapping for quick lookup
star_nation_mapping = {}
for nation_id, nation_data in fictional_nations.items():
    for star_id in nation_data["territories"]:
        star_nation_mapping[star_id] = nation_id

def get_star_nation(star_id):
    """Get the nation that controls a specific star system"""
    return star_nation_mapping.get(star_id, None)

def get_nation_info(nation_id):
    """Get full information about a nation"""
    if nation_id is None:
        return None
    return fictional_nations.get(nation_id, None)

def get_nation_color(star_id):
    """Get the color for a star based on its controlling nation"""
    nation_id = get_star_nation(star_id)
    nation = get_nation_info(nation_id)
    if nation is None:
        return "#FFFFFF"  # Default white color for uncontrolled stars
    return nation["color"]

def get_all_nations():
    """Get all fictional nations"""
    return fictional_nations