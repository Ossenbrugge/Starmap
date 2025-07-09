#!/usr/bin/env python3
"""
Remove fictional 61 Ursae Majoris and assign fictional data to real star
"""

import pandas as pd
import json

# Load datasets
print("Loading datasets...")
real_stars = pd.read_csv('stars_output.csv')
fictional_stars = pd.read_csv('fictional_stars.csv')

print(f"Real stars: {len(real_stars)}")
print(f"Fictional stars: {len(fictional_stars)}")

# Find the fictional 61 Ursae Majoris
fictional_61_uma = fictional_stars[fictional_stars['id'] == 200001]
if len(fictional_61_uma) == 0:
    print("❌ Fictional 61 Ursae Majoris (ID 200001) not found")
    exit(1)

fictional_61_uma = fictional_61_uma.iloc[0]
print(f"Found fictional 61 Ursae Majoris (ID {fictional_61_uma['id']})")

# Find the real star with matching HIP/HD
real_61_uma = real_stars[
    (real_stars['hip'] == fictional_61_uma['hip']) & 
    (real_stars['hd'] == fictional_61_uma['hd'])
]

if len(real_61_uma) == 0:
    print("❌ Real star with matching HIP/HD not found")
    exit(1)

real_61_uma = real_61_uma.iloc[0]
print(f"Found real 61 Ursae Majoris (ID {real_61_uma['id']})")

print("\nMapping:")
print(f"  Fictional ID {fictional_61_uma['id']} → Real ID {real_61_uma['id']}")
print(f"  HIP {fictional_61_uma['hip']}, HD {fictional_61_uma['hd']}")
print(f"  Fictional position: ({fictional_61_uma['x']:.2f}, {fictional_61_uma['y']:.2f}, {fictional_61_uma['z']:.2f})")
print(f"  Real position: ({real_61_uma['x']:.2f}, {real_61_uma['y']:.2f}, {real_61_uma['z']:.2f})")

# Remove the fictional star from the dataset
print("\n" + "="*60)
print("REMOVING FICTIONAL STAR")
print("="*60)

cleaned_fictional_stars = fictional_stars[fictional_stars['id'] != 200001]
print(f"Removed fictional 61 Ursae Majoris. Fictional stars: {len(fictional_stars)} → {len(cleaned_fictional_stars)}")

# Save cleaned fictional stars
cleaned_fictional_stars.to_csv('fictional_stars_clean.csv', index=False)
print("Saved cleaned fictional stars to fictional_stars_clean.csv")

# Update fictional names mapping
print("\n" + "="*60)
print("UPDATING FICTIONAL NAMES MAPPING")
print("="*60)

try:
    with open('fictional_names.py', 'r') as f:
        content = f.read()
        exec(content)
        fictional_names = fictional_star_names
    
    # Update the mapping to use real star ID
    if 200001 in fictional_names:
        fictional_names[int(real_61_uma['id'])] = fictional_names[200001]
        del fictional_names[200001]
        print(f"Updated fictional names: 200001 → {real_61_uma['id']}")
    
    # Write updated fictional_names.py
    with open('fictional_names_updated.py', 'w') as f:
        f.write("# Updated Fictional Star Names Database\n")
        f.write("# Removed fictional 61 Ursae Majoris duplicate\n\n")
        f.write("fictional_star_names = {\n")
        
        for star_id, name_data in fictional_names.items():
            f.write(f"    {star_id}: {{\n")
            for key, value in name_data.items():
                if isinstance(value, str):
                    f.write(f"        \"{key}\": \"{value}\",\n")
                else:
                    f.write(f"        \"{key}\": {value},\n")
            f.write("    },\n")
        
        f.write("}\n")
    
    print("Created fictional_names_updated.py")
    
except Exception as e:
    print(f"Error updating fictional names: {e}")

# Update nations data
print("\n" + "="*60)
print("UPDATING NATIONS DATA")
print("="*60)

try:
    with open('nations_data.json', 'r') as f:
        nations_data = json.load(f)
    
    updates_made = 0
    for nation_key, nation in nations_data.get('nations', {}).items():
        if 'territories' in nation:
            updated_territories = []
            for territory_id in nation['territories']:
                if territory_id == 200001:
                    updated_territories.append(int(real_61_uma['id']))
                    print(f"Updated {nation['name']} territory: 200001 → {real_61_uma['id']}")
                    updates_made += 1
                else:
                    updated_territories.append(territory_id)
            
            nation['territories'] = updated_territories
    
    # Convert numpy types to native Python types for JSON serialization
    def convert_numpy_types(obj):
        if isinstance(obj, dict):
            return {key: convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        elif hasattr(obj, 'item'):  # numpy scalar
            return obj.item()
        else:
            return obj
    
    nations_data = convert_numpy_types(nations_data)
    
    with open('nations_data_updated.json', 'w') as f:
        json.dump(nations_data, f, indent=2)
    
    print(f"Updated nations_data_updated.json with {updates_made} territory changes")
    
except Exception as e:
    print(f"Error updating nations data: {e}")

# Update trade routes data
print("\n" + "="*60)
print("UPDATING TRADE ROUTES DATA")
print("="*60)

try:
    with open('trade_routes_data.json', 'r') as f:
        trade_routes_data = json.load(f)
    
    updates_made = 0
    for route in trade_routes_data.get('routes', []):
        if 'origin_star_id' in route and route['origin_star_id'] == 200001:
            route['origin_star_id'] = int(real_61_uma['id'])
            print(f"Updated trade route origin: 200001 → {real_61_uma['id']}")
            updates_made += 1
        
        if 'destination_star_id' in route and route['destination_star_id'] == 200001:
            route['destination_star_id'] = int(real_61_uma['id'])
            print(f"Updated trade route destination: 200001 → {real_61_uma['id']}")
            updates_made += 1
    
    with open('trade_routes_data_updated.json', 'w') as f:
        json.dump(trade_routes_data, f, indent=2)
    
    print(f"Updated trade_routes_data_updated.json with {updates_made} route changes")
    
except Exception as e:
    print(f"Error updating trade routes data: {e}")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

print(f"📊 BEFORE:")
print(f"  - Real stars: {len(real_stars)}")
print(f"  - Fictional stars: {len(fictional_stars)}")
print(f"  - Total: {len(real_stars) + len(fictional_stars)}")

print(f"\n📊 AFTER:")
print(f"  - Real stars: {len(real_stars)} (unchanged)")
print(f"  - Fictional stars: {len(cleaned_fictional_stars)}")
print(f"  - Total: {len(real_stars) + len(cleaned_fictional_stars)}")

print(f"\n🔄 CHANGES MADE:")
print(f"  - Removed fictional 61 Ursae Majoris (ID 200001)")
print(f"  - Assigned fictional data to real star (ID {real_61_uma['id']})")
print(f"  - Updated fictional names mapping")
print(f"  - Updated nations data")
print(f"  - Updated trade routes data")

print(f"\n📁 FILES CREATED:")
print(f"  - fictional_stars_clean.csv (13 fictional stars)")
print(f"  - fictional_names_updated.py (updated mappings)")
print(f"  - nations_data_updated.json (updated territories)")
print(f"  - trade_routes_data_updated.json (updated routes)")

print(f"\n🎯 NEXT STEPS:")
print(f"  1. Replace fictional_stars.csv with fictional_stars_clean.csv")
print(f"  2. Replace fictional_names.py with fictional_names_updated.py")
print(f"  3. Replace nations_data.json with nations_data_updated.json")
print(f"  4. Replace trade_routes_data.json with trade_routes_data_updated.json")
print(f"  5. Restart application")

print(f"\n✅ RESULT:")
print(f"  - No more HIP/HD catalog overlaps")
print(f"  - Fictional data properly assigned to real star")
print(f"  - Clean dataset with {len(real_stars) + len(cleaned_fictional_stars)} total stars")