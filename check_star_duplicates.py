#!/usr/bin/env python3
"""
Check for duplicates between fictional stars and real stars
"""

import pandas as pd
import json

# Load real stars
print("Loading real stars...")
real_stars = pd.read_csv('stars_output.csv')

# Load fictional stars
print("Loading fictional stars...")
fictional_stars = pd.read_csv('fictional_stars.csv')

print(f"Real stars: {len(real_stars)}")
print(f"Fictional stars: {len(fictional_stars)}")

# Check for ID duplicates
print("\n" + "="*60)
print("CHECKING FOR ID DUPLICATES")
print("="*60)

real_ids = set(real_stars['id'].tolist())
fictional_ids = set(fictional_stars['id'].tolist())

id_duplicates = real_ids.intersection(fictional_ids)

if id_duplicates:
    print(f"❌ Found {len(id_duplicates)} ID duplicates:")
    for dup_id in sorted(id_duplicates):
        real_star = real_stars[real_stars['id'] == dup_id].iloc[0]
        fictional_star = fictional_stars[fictional_stars['id'] == dup_id].iloc[0]
        
        print(f"  ID {dup_id}:")
        print(f"    Real: {real_star.get('proper', 'N/A')} at ({real_star['x']:.1f}, {real_star['y']:.1f}, {real_star['z']:.1f})")
        print(f"    Fictional: {fictional_star.get('proper', 'N/A')} at ({fictional_star['x']:.1f}, {fictional_star['y']:.1f}, {fictional_star['z']:.1f})")
else:
    print("✅ No ID duplicates found")

# Check for coordinate duplicates (stars at same location)
print("\n" + "="*60)
print("CHECKING FOR COORDINATE DUPLICATES")
print("="*60)

# Round coordinates to avoid floating point precision issues
tolerance = 0.01  # 0.01 parsecs tolerance

coordinate_duplicates = []

for _, fstar in fictional_stars.iterrows():
    fx, fy, fz = fstar['x'], fstar['y'], fstar['z']
    
    # Check if any real star is at the same location
    close_stars = real_stars[
        (abs(real_stars['x'] - fx) < tolerance) & 
        (abs(real_stars['y'] - fy) < tolerance) & 
        (abs(real_stars['z'] - fz) < tolerance)
    ]
    
    if len(close_stars) > 0:
        for _, rstar in close_stars.iterrows():
            coordinate_duplicates.append({
                'fictional_id': fstar['id'],
                'fictional_name': fstar.get('proper', 'N/A'),
                'fictional_coords': (fx, fy, fz),
                'real_id': rstar['id'],
                'real_name': rstar.get('proper', 'N/A'),
                'real_coords': (rstar['x'], rstar['y'], rstar['z']),
                'distance': ((fx - rstar['x'])**2 + (fy - rstar['y'])**2 + (fz - rstar['z'])**2)**0.5
            })

if coordinate_duplicates:
    print(f"❌ Found {len(coordinate_duplicates)} coordinate duplicates:")
    for dup in coordinate_duplicates:
        print(f"  Fictional ID {dup['fictional_id']} ({dup['fictional_name']}) at {dup['fictional_coords']}")
        print(f"  Real ID {dup['real_id']} ({dup['real_name']}) at {dup['real_coords']}")
        print(f"  Distance: {dup['distance']:.4f} parsecs")
        print()
else:
    print("✅ No coordinate duplicates found")

# Check for name duplicates
print("\n" + "="*60)
print("CHECKING FOR NAME DUPLICATES")
print("="*60)

# Get proper names, excluding NaN values
real_names = set(real_stars['proper'].dropna().tolist())
fictional_names = set(fictional_stars['proper'].dropna().tolist())

name_duplicates = real_names.intersection(fictional_names)

if name_duplicates:
    print(f"❌ Found {len(name_duplicates)} name duplicates:")
    for dup_name in sorted(name_duplicates):
        real_star = real_stars[real_stars['proper'] == dup_name].iloc[0]
        fictional_star = fictional_stars[fictional_stars['proper'] == dup_name].iloc[0]
        
        print(f"  Name '{dup_name}':")
        print(f"    Real ID {real_star['id']}: at ({real_star['x']:.1f}, {real_star['y']:.1f}, {real_star['z']:.1f})")
        print(f"    Fictional ID {fictional_star['id']}: at ({fictional_star['x']:.1f}, {fictional_star['y']:.1f}, {fictional_star['z']:.1f})")
else:
    print("✅ No name duplicates found")

# Check for HIP/HD duplicates
print("\n" + "="*60)
print("CHECKING FOR HIP/HD CATALOG DUPLICATES")
print("="*60)

hip_duplicates = []
hd_duplicates = []

# Check HIP numbers
if 'hip' in real_stars.columns and 'hip' in fictional_stars.columns:
    real_hip = set(real_stars['hip'].dropna().tolist())
    fictional_hip = set(fictional_stars['hip'].dropna().tolist())
    hip_duplicates = real_hip.intersection(fictional_hip)

# Check HD numbers
if 'hd' in real_stars.columns and 'hd' in fictional_stars.columns:
    real_hd = set(real_stars['hd'].dropna().tolist())
    fictional_hd = set(fictional_stars['hd'].dropna().tolist())
    hd_duplicates = real_hd.intersection(fictional_hd)

if hip_duplicates:
    print(f"❌ Found {len(hip_duplicates)} HIP duplicates: {sorted(hip_duplicates)}")
else:
    print("✅ No HIP duplicates found")

if hd_duplicates:
    print(f"❌ Found {len(hd_duplicates)} HD duplicates: {sorted(hd_duplicates)}")
else:
    print("✅ No HD duplicates found")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

total_duplicates = len(id_duplicates) + len(coordinate_duplicates) + len(name_duplicates) + len(hip_duplicates) + len(hd_duplicates)

if total_duplicates == 0:
    print("🎉 NO DUPLICATES FOUND!")
    print("✅ Real stars and fictional stars are completely separate datasets")
    print(f"✅ Total unique stars: {len(real_stars) + len(fictional_stars)}")
else:
    print(f"⚠️  FOUND {total_duplicates} TOTAL DUPLICATES:")
    if id_duplicates:
        print(f"  - {len(id_duplicates)} ID duplicates")
    if coordinate_duplicates:
        print(f"  - {len(coordinate_duplicates)} coordinate duplicates")
    if name_duplicates:
        print(f"  - {len(name_duplicates)} name duplicates")
    if hip_duplicates:
        print(f"  - {len(hip_duplicates)} HIP duplicates")
    if hd_duplicates:
        print(f"  - {len(hd_duplicates)} HD duplicates")
    
    print("\n🔧 RECOMMENDATIONS:")
    if id_duplicates:
        print("  - Resolve ID conflicts by reassigning fictional star IDs")
    if coordinate_duplicates:
        print("  - Check if fictional stars are meant to replace real stars")
    if name_duplicates:
        print("  - Consider renaming fictional stars to avoid conflicts")

# Check the merged dataset used by the application
print("\n" + "="*60)
print("CHECKING APPLICATION MERGED DATASET")
print("="*60)

# This simulates what the application does in star_model.py
print("Simulating application merge process...")

# Load and merge like the application does
real_df = pd.read_csv('stars_output.csv')
fictional_df = pd.read_csv('fictional_stars.csv')

print(f"Before merge: Real={len(real_df)}, Fictional={len(fictional_df)}")

# Merge datasets (fictional stars should be appended)
merged_df = pd.concat([real_df, fictional_df], ignore_index=True)

print(f"After merge: Total={len(merged_df)}")

# Check for duplicates in merged dataset
merged_id_duplicates = merged_df[merged_df.duplicated(subset=['id'], keep=False)]

if len(merged_id_duplicates) > 0:
    print(f"❌ Found {len(merged_id_duplicates)} duplicate IDs in merged dataset:")
    for _, dup in merged_id_duplicates.iterrows():
        print(f"  ID {dup['id']}: {dup.get('proper', 'N/A')}")
else:
    print("✅ No duplicate IDs in merged dataset")

# Final verification
expected_total = len(real_stars) + len(fictional_stars)
actual_total = len(merged_df)

if expected_total == actual_total:
    print(f"✅ Merge successful: {expected_total} stars total")
else:
    print(f"❌ Merge issue: Expected {expected_total}, got {actual_total}")