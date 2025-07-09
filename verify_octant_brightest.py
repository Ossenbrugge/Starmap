#!/usr/bin/env python3
"""
Verify that the selected stars are indeed the brightest in each octant
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
print(f"Octant range: 130 parsecs from Sol in each direction")

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

print("\n" + "="*80)
print("OCTANT BRIGHTNESS VERIFICATION")
print("="*80)

for i, octant in enumerate(octants):
    octant_num = octant['octant_number']
    x_range = octant['x_range']
    y_range = octant['y_range']
    z_range = octant['z_range']
    
    print(f"\nOctant {octant_num}: {octant['short_name']} Region")
    print(f"Coordinates: X[{x_range[0]:>4} to {x_range[1]:>4}], Y[{y_range[0]:>4} to {y_range[1]:>4}], Z[{z_range[0]:>4} to {z_range[1]:>4}]")
    
    # Filter stars in this octant, excluding Sol (id=0)
    stars_in_octant = stars_df[
        (stars_df['x'] >= x_range[0]) & (stars_df['x'] <= x_range[1]) &
        (stars_df['y'] >= y_range[0]) & (stars_df['y'] <= y_range[1]) &
        (stars_df['z'] >= z_range[0]) & (stars_df['z'] <= z_range[1]) &
        (stars_df['id'] != 0)  # Exclude Sol
    ]
    
    print(f"Total stars in octant: {len(stars_in_octant)}")
    
    if len(stars_in_octant) > 0:
        # Sort by magnitude (brightest first)
        brightest_stars = stars_in_octant.sort_values('mag').head(10)
        
        print(f"\nTop 10 brightest stars in this octant:")
        print(f"{'Rank':<4} {'Name':<20} {'Magnitude':<10} {'Distance (ly)':<12} {'Position (x,y,z)':<20}")
        print("-" * 80)
        
        for idx, (_, star) in enumerate(brightest_stars.iterrows(), 1):
            star_name = get_star_name(star)
            position = f"({star['x']:.1f}, {star['y']:.1f}, {star['z']:.1f})"
            print(f"{idx:<4} {star_name:<20} {star['mag']:<10.2f} {star['dist']:<12.2f} {position:<20}")
        
        # Check if our selected star is indeed the brightest
        actual_brightest = brightest_stars.iloc[0]
        actual_brightest_name = get_star_name(actual_brightest)
        
        expected_name = octant['short_name']
        
        if actual_brightest_name == expected_name:
            print(f"✅ VERIFIED: {expected_name} is indeed the brightest star in this octant!")
        else:
            print(f"❌ ERROR: Expected {expected_name}, but {actual_brightest_name} is actually brightest!")
            print(f"   Expected magnitude: {octant.get('brightest_star_magnitude', 'N/A')}")
            print(f"   Actual magnitude: {actual_brightest['mag']:.2f}")
    else:
        print("❌ No stars found in this octant!")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

# Check if all selected stars are correct
all_correct = True
for octant in octants:
    octant_num = octant['octant_number']
    x_range = octant['x_range']
    y_range = octant['y_range']
    z_range = octant['z_range']
    
    stars_in_octant = stars_df[
        (stars_df['x'] >= x_range[0]) & (stars_df['x'] <= x_range[1]) &
        (stars_df['y'] >= y_range[0]) & (stars_df['y'] <= y_range[1]) &
        (stars_df['z'] >= z_range[0]) & (stars_df['z'] <= z_range[1]) &
        (stars_df['id'] != 0)
    ]
    
    if len(stars_in_octant) > 0:
        actual_brightest = stars_in_octant.loc[stars_in_octant['mag'].idxmin()]
        actual_brightest_name = get_star_name(actual_brightest)
        expected_name = octant['short_name']
        
        if actual_brightest_name != expected_name:
            all_correct = False
            print(f"Octant {octant_num}: Expected {expected_name}, but {actual_brightest_name} is brightest")
        else:
            print(f"Octant {octant_num}: {expected_name} ✅")

if all_correct:
    print("\n🎉 ALL OCTANTS CORRECTLY NAMED! Each octant is named after its brightest star.")
else:
    print("\n⚠️  Some octants may need correction.")