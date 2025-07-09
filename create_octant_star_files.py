#!/usr/bin/env python3
"""
Create JSON files for each octant containing all stars in that region
"""

import pandas as pd
import json
from datetime import datetime

# Load star data
print("Loading star data...")
stars_df = pd.read_csv('stars_output.csv')

# Load octant definitions
with open('stellar_regions.json', 'r') as f:
    octant_data = json.load(f)

octants = octant_data['regions']

print(f"Loaded {len(stars_df)} stars and {len(octants)} octants")

def get_star_name(star_row):
    """Get the best name for a star"""
    if pd.notna(star_row['proper']):
        return star_row['proper']
    elif pd.notna(star_row['hd']):
        return f"HD {star_row['hd']}"
    elif pd.notna(star_row['hip']):
        return f"HIP {star_row['hip']}"
    else:
        return f"Star {star_row['id']}"

def convert_star_to_dict(star_row):
    """Convert a star pandas row to a dictionary with proper data types"""
    star_dict = {}
    for column in star_row.index:
        value = star_row[column]
        if pd.isna(value):
            star_dict[column] = None
        elif isinstance(value, (int, float)):
            if isinstance(value, float) and value.is_integer():
                star_dict[column] = int(value)
            else:
                star_dict[column] = float(value)
        else:
            star_dict[column] = str(value)
    
    # Add computed name field
    star_dict['display_name'] = get_star_name(star_row)
    
    return star_dict

print("\nCreating octant star files...")

for octant in octants:
    octant_num = octant['octant_number']
    octant_name = octant['short_name']
    x_range = octant['x_range']
    y_range = octant['y_range']
    z_range = octant['z_range']
    
    print(f"\nProcessing Octant {octant_num}: {octant_name}")
    print(f"  Coordinates: X[{x_range[0]} to {x_range[1]}], Y[{y_range[0]} to {y_range[1]}], Z[{z_range[0]} to {z_range[1]}]")
    
    # Filter stars in this octant (including Sol for completeness)
    stars_in_octant = stars_df[
        (stars_df['x'] >= x_range[0]) & (stars_df['x'] <= x_range[1]) &
        (stars_df['y'] >= y_range[0]) & (stars_df['y'] <= y_range[1]) &
        (stars_df['z'] >= z_range[0]) & (stars_df['z'] <= z_range[1])
    ]
    
    # Sort by magnitude (brightest first)
    stars_in_octant = stars_in_octant.sort_values('mag')
    
    print(f"  Found {len(stars_in_octant)} stars in this octant")
    
    # Convert to list of dictionaries
    stars_list = [convert_star_to_dict(star) for _, star in stars_in_octant.iterrows()]
    
    # Create the JSON structure
    octant_file_data = {
        "metadata": {
            "octant_name": octant_name,
            "octant_number": octant_num,
            "full_name": octant['name'],
            "description": octant['description'],
            "coordinate_system": "Cartesian coordinates (parsecs from Sol)",
            "x_range": x_range,
            "y_range": y_range,
            "z_range": z_range,
            "center_point": octant['center_point'],
            "diameter": octant['diameter'],
            "total_stars": len(stars_list),
            "brightest_star": {
                "name": octant['brightest_star'],
                "id": octant['brightest_star_id'],
                "magnitude": octant['brightest_star_magnitude']
            },
            "generated_date": datetime.now().isoformat(),
            "data_source": "Hipparcos catalog + fictional stars"
        },
        "stars": stars_list
    }
    
    # Create filename
    filename = f"{octant_name.lower().replace(' ', '_')}.json"
    
    # Write to file
    with open(filename, 'w') as f:
        json.dump(octant_file_data, f, indent=2)
    
    print(f"  Created: {filename}")
    
    # Print some statistics
    if len(stars_list) > 0:
        brightest = stars_list[0]
        dimmest = stars_list[-1]
        print(f"  Brightest: {brightest['display_name']} (mag {brightest['mag']:.2f})")
        print(f"  Dimmest: {dimmest['display_name']} (mag {dimmest['mag']:.2f})")
        
        # Count stars by magnitude ranges
        mag_ranges = [
            (-30, 0, "Very bright"),
            (0, 2, "Bright"),
            (2, 4, "Moderate"),
            (4, 6, "Dim"),
            (6, 10, "Very dim"),
            (10, 20, "Extremely dim")
        ]
        
        for min_mag, max_mag, desc in mag_ranges:
            count = len([s for s in stars_list if min_mag <= s['mag'] < max_mag])
            if count > 0:
                print(f"  {desc} stars (mag {min_mag}-{max_mag}): {count}")

print(f"\n✅ Created {len(octants)} octant star files:")
for octant in octants:
    filename = f"{octant['short_name'].lower().replace(' ', '_')}.json"
    print(f"  - {filename}")

print(f"\nEach file contains:")
print(f"  - Metadata about the octant")
print(f"  - Complete star catalog for that region")
print(f"  - Stars sorted by brightness (magnitude)")
print(f"  - Computed display names for each star")
print(f"  - All original star data fields")