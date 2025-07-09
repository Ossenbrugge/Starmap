#!/usr/bin/env python3
"""
Check what the HIP/HD overlaps are specifically
"""

import pandas as pd

# Load datasets
print("Loading datasets...")
real_stars = pd.read_csv('stars_output.csv')
fictional_stars = pd.read_csv('fictional_stars.csv')

print(f"Real stars: {len(real_stars)}")
print(f"Fictional stars: {len(fictional_stars)}")

# Check HIP overlaps
print("\n" + "="*60)
print("HIP CATALOG OVERLAPS")
print("="*60)

real_hip = real_stars['hip'].dropna()
fictional_hip = fictional_stars['hip'].dropna()

hip_overlaps = []
for hip in fictional_hip:
    if hip in real_hip.values:
        real_match = real_stars[real_stars['hip'] == hip].iloc[0]
        fictional_match = fictional_stars[fictional_stars['hip'] == hip].iloc[0]
        
        hip_overlaps.append({
            'hip': hip,
            'real_id': real_match['id'],
            'real_name': real_match.get('proper', 'N/A'),
            'real_coords': (real_match['x'], real_match['y'], real_match['z']),
            'fictional_id': fictional_match['id'],
            'fictional_name': fictional_match.get('proper', 'N/A'),
            'fictional_coords': (fictional_match['x'], fictional_match['y'], fictional_match['z'])
        })

if hip_overlaps:
    print(f"Found {len(hip_overlaps)} HIP overlaps:")
    for overlap in hip_overlaps:
        print(f"\nHIP {overlap['hip']}:")
        print(f"  Real star (ID {overlap['real_id']}): {overlap['real_name']}")
        print(f"    Position: ({overlap['real_coords'][0]:.2f}, {overlap['real_coords'][1]:.2f}, {overlap['real_coords'][2]:.2f})")
        print(f"  Fictional star (ID {overlap['fictional_id']}): {overlap['fictional_name']}")
        print(f"    Position: ({overlap['fictional_coords'][0]:.2f}, {overlap['fictional_coords'][1]:.2f}, {overlap['fictional_coords'][2]:.2f})")
else:
    print("No HIP overlaps found")

# Check HD overlaps
print("\n" + "="*60)
print("HD CATALOG OVERLAPS")
print("="*60)

real_hd = real_stars['hd'].dropna()
fictional_hd = fictional_stars['hd'].dropna()

hd_overlaps = []
for hd in fictional_hd:
    if hd in real_hd.values:
        real_match = real_stars[real_stars['hd'] == hd].iloc[0]
        fictional_match = fictional_stars[fictional_stars['hd'] == hd].iloc[0]
        
        hd_overlaps.append({
            'hd': hd,
            'real_id': real_match['id'],
            'real_name': real_match.get('proper', 'N/A'),
            'real_coords': (real_match['x'], real_match['y'], real_match['z']),
            'fictional_id': fictional_match['id'],
            'fictional_name': fictional_match.get('proper', 'N/A'),
            'fictional_coords': (fictional_match['x'], fictional_match['y'], fictional_match['z'])
        })

if hd_overlaps:
    print(f"Found {len(hd_overlaps)} HD overlaps:")
    for overlap in hd_overlaps:
        print(f"\nHD {overlap['hd']}:")
        print(f"  Real star (ID {overlap['real_id']}): {overlap['real_name']}")
        print(f"    Position: ({overlap['real_coords'][0]:.2f}, {overlap['real_coords'][1]:.2f}, {overlap['real_coords'][2]:.2f})")
        print(f"  Fictional star (ID {overlap['fictional_id']}): {overlap['fictional_name']}")
        print(f"    Position: ({overlap['fictional_coords'][0]:.2f}, {overlap['fictional_coords'][1]:.2f}, {overlap['fictional_coords'][2]:.2f})")
else:
    print("No HD overlaps found")

# Check what these fictional stars are
print("\n" + "="*60)
print("FICTIONAL STARS WITH CATALOG NUMBERS")
print("="*60)

print("Current fictional stars:")
for _, star in fictional_stars.iterrows():
    hip = star.get('hip', 'N/A')
    hd = star.get('hd', 'N/A')
    print(f"  ID {star['id']}: {star.get('proper', 'N/A')}")
    print(f"    HIP: {hip}, HD: {hd}")
    print(f"    Position: ({star['x']:.2f}, {star['y']:.2f}, {star['z']:.2f})")
    print()

print("\n" + "="*60)
print("ANALYSIS")
print("="*60)

print("These overlaps indicate that fictional stars are using real catalog numbers.")
print("This could happen if:")
print("1. The fictional stars were created based on real stars")
print("2. The catalog numbers were copied accidentally")
print("3. The fictional stars are meant to represent alternate versions of real stars")
print()
print("Recommendations:")
print("1. Remove HIP/HD catalog numbers from fictional stars")
print("2. Or assign fictional catalog numbers (e.g., HIP 900000+)")
print("3. Or clearly document that these are alternate versions of real stars")