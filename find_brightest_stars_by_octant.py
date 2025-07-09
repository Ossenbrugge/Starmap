#!/usr/bin/env python3
"""
Find the brightest star in each galactic octant
"""

import pandas as pd
import json

# Load star data
print("Loading star data...")
stars_df = pd.read_csv('stars_output.csv')

# Load octant definitions
with open('stellar_regions.json', 'r') as f:
    octant_data = json.load(f)

octants = octant_data['regions']

print(f"Loaded {len(stars_df)} stars and {len(octants)} octants")

# Find brightest star in each octant
brightest_stars = {}

for octant in octants:
    octant_name = octant['name']
    x_range = octant['x_range']
    y_range = octant['y_range']
    z_range = octant['z_range']
    
    print(f"\nAnalyzing {octant_name}:")
    print(f"  X: {x_range[0]} to {x_range[1]}")
    print(f"  Y: {y_range[0]} to {y_range[1]}")
    print(f"  Z: {z_range[0]} to {z_range[1]}")
    
    # Filter stars in this octant, excluding Sol (id=0)
    stars_in_octant = stars_df[
        (stars_df['x'] >= x_range[0]) & (stars_df['x'] <= x_range[1]) &
        (stars_df['y'] >= y_range[0]) & (stars_df['y'] <= y_range[1]) &
        (stars_df['z'] >= z_range[0]) & (stars_df['z'] <= z_range[1]) &
        (stars_df['id'] != 0)  # Exclude Sol
    ]
    
    print(f"  Stars in octant: {len(stars_in_octant)}")
    
    if len(stars_in_octant) > 0:
        # Find brightest star (lowest magnitude)
        brightest_star = stars_in_octant.loc[stars_in_octant['mag'].idxmin()]
        
        print(f"  Brightest star: {brightest_star['proper'] if pd.notna(brightest_star['proper']) else 'Unknown'}")
        print(f"  Magnitude: {brightest_star['mag']}")
        print(f"  Distance: {brightest_star['dist']:.2f} ly")
        print(f"  Position: ({brightest_star['x']:.1f}, {brightest_star['y']:.1f}, {brightest_star['z']:.1f})")
        
        # Check if star has a proper name
        star_name = brightest_star['proper'] if pd.notna(brightest_star['proper']) else f"HD {brightest_star['hd']}" if pd.notna(brightest_star['hd']) else f"HIP {brightest_star['hip']}" if pd.notna(brightest_star['hip']) else f"Star {brightest_star['id']}"
        
        brightest_stars[octant_name] = {
            'star_name': star_name,
            'magnitude': brightest_star['mag'],
            'distance': brightest_star['dist'],
            'position': [brightest_star['x'], brightest_star['y'], brightest_star['z']],
            'star_id': brightest_star['id']
        }
    else:
        print(f"  No stars found in this octant!")

print("\n" + "="*50)
print("BRIGHTEST STARS BY OCTANT:")
print("="*50)

for octant_name, star_info in brightest_stars.items():
    print(f"{octant_name}: {star_info['star_name']} (mag {star_info['magnitude']:.2f})")

# Update the stellar regions JSON file
print("\nUpdating stellar_regions.json...")

for octant in octants:
    octant_name = octant['name']
    if octant_name in brightest_stars:
        star_info = brightest_stars[octant_name]
        octant['brightest_star'] = star_info['star_name']
        octant['brightest_star_id'] = int(star_info['star_id'])
        octant['brightest_star_magnitude'] = float(star_info['magnitude'])
        
        # Update the name and short_name to the brightest star
        octant['original_name'] = octant['name']
        octant['name'] = f"{star_info['star_name']} Region"
        octant['short_name'] = star_info['star_name']
        
        # Update description - clean up any existing description and create new one
        original_desc = octant['description']
        if 'Galactic region centered on' in original_desc:
            # Extract the original galactic direction description
            parts = original_desc.split('. ')
            galactic_desc = [part for part in parts if 'ward' in part and 'octant' in part]
            if galactic_desc:
                base_desc = galactic_desc[0]
            else:
                base_desc = original_desc
        else:
            base_desc = original_desc
        
        octant['description'] = f"Galactic region centered on {star_info['star_name']} (magnitude {star_info['magnitude']:.2f}), the brightest star in this octant. {base_desc}"

# Save updated data
with open('stellar_regions.json', 'w') as f:
    json.dump(octant_data, f, indent=2)

print("Updated stellar_regions.json with brightest star names")