#!/usr/bin/env python3
"""
Fix octant naming by properly mapping each octant to its brightest star
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

# Define the octant mappings clearly
octant_mappings = []

for i, octant in enumerate(octants):
    octant_num = octant['octant_number']
    x_range = octant['x_range']
    y_range = octant['y_range']
    z_range = octant['z_range']
    
    print(f"\nOctant {octant_num}: {octant['name']}")
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
        
        star_name = brightest_star['proper'] if pd.notna(brightest_star['proper']) else f"HD {brightest_star['hd']}" if pd.notna(brightest_star['hd']) else f"HIP {brightest_star['hip']}" if pd.notna(brightest_star['hip']) else f"Star {brightest_star['id']}"
        
        print(f"  Brightest star: {star_name} (mag {brightest_star['mag']:.2f})")
        
        octant_mappings.append({
            'octant_number': octant_num,
            'star_name': star_name,
            'magnitude': brightest_star['mag'],
            'star_id': brightest_star['id'],
            'position': [brightest_star['x'], brightest_star['y'], brightest_star['z']]
        })

print("\n" + "="*60)
print("CORRECT OCTANT MAPPINGS:")
print("="*60)

# Now update each octant with its correct brightest star
for i, octant in enumerate(octants):
    octant_num = octant['octant_number']
    
    # Find the corresponding mapping
    mapping = next(m for m in octant_mappings if m['octant_number'] == octant_num)
    
    star_name = mapping['star_name']
    magnitude = mapping['magnitude']
    
    print(f"Octant {octant_num}: {star_name} (mag {magnitude:.2f})")
    
    # Update the octant data
    octant['brightest_star'] = star_name
    octant['brightest_star_id'] = int(mapping['star_id'])
    octant['brightest_star_magnitude'] = float(magnitude)
    
    # Store original name if not already done
    if 'original_name' not in octant:
        octant['original_name'] = octant['name']
    
    # Update the name and short_name
    octant['name'] = f"{star_name} Region"
    octant['short_name'] = star_name
    
    # Get the original galactic direction description
    original_desc = octant.get('description', '')
    if 'Galactic region centered on' in original_desc:
        # Extract the part after the first period
        parts = original_desc.split('. ', 1)
        if len(parts) > 1:
            base_desc = parts[1]
        else:
            base_desc = original_desc
    else:
        base_desc = original_desc
    
    # Update description
    octant['description'] = f"Galactic region centered on {star_name} (magnitude {magnitude:.2f}), the brightest star in this octant. {base_desc}"

# Save updated data
print(f"\nSaving updated stellar_regions.json...")
with open('stellar_regions.json', 'w') as f:
    json.dump(octant_data, f, indent=2)

print("Successfully updated all octant names!")

# Verify the results
print("\nFinal verification:")
for octant in octants:
    print(f"  Octant {octant['octant_number']}: {octant['short_name']}")