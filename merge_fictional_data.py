#!/usr/bin/env python3
"""
Remove fictional star duplicates and merge fictional data into real stars
"""

import pandas as pd
import json

# Load datasets
print("Loading datasets...")
real_stars = pd.read_csv('stars_output.csv')
fictional_stars = pd.read_csv('fictional_stars.csv')
fictional_names = {}

# Load fictional names mapping
try:
    with open('fictional_names.py', 'r') as f:
        content = f.read()
        # Extract the fictional_star_names dictionary
        exec(content)
        fictional_names = fictional_star_names
    print(f"Loaded {len(fictional_names)} fictional names")
except:
    print("Could not load fictional_names.py")

print(f"Real stars: {len(real_stars)}")
print(f"Fictional stars: {len(fictional_stars)}")

# Create a mapping of fictional star names to real star IDs
name_to_real_id = {}
for name, data in fictional_names.items():
    if isinstance(name, int):
        # This is a star ID mapping
        name_to_real_id[name] = data

print(f"Found {len(name_to_real_id)} fictional name mappings")

# Identify which fictional stars are actually real stars
print("\n" + "="*60)
print("IDENTIFYING FICTIONAL STARS THAT ARE REAL STARS")
print("="*60)

fictional_to_real_mapping = {}
truly_fictional = []

for _, fstar in fictional_stars.iterrows():
    fid = fstar['id']
    fname = fstar.get('proper', '')
    
    # Check if this fictional star matches a real star by name
    matching_real = real_stars[real_stars['proper'] == fname]
    
    if len(matching_real) > 0:
        # This fictional star is actually a real star
        real_id = matching_real.iloc[0]['id']
        fictional_to_real_mapping[fid] = real_id
        print(f"Fictional ID {fid} ({fname}) → Real ID {real_id}")
    else:
        # This is a truly fictional star
        truly_fictional.append(fstar)
        print(f"Fictional ID {fid} ({fname}) → Keep as fictional")

print(f"\nFound {len(fictional_to_real_mapping)} fictional stars that are real stars")
print(f"Found {len(truly_fictional)} truly fictional stars")

# Create new fictional stars dataset with only truly fictional stars
print("\n" + "="*60)
print("CREATING CLEAN FICTIONAL STARS DATASET")
print("="*60)

if truly_fictional:
    clean_fictional_df = pd.DataFrame(truly_fictional)
    clean_fictional_df.to_csv('fictional_stars_clean.csv', index=False)
    print(f"Created fictional_stars_clean.csv with {len(clean_fictional_df)} truly fictional stars")
else:
    # Create empty file if no truly fictional stars
    pd.DataFrame(columns=real_stars.columns).to_csv('fictional_stars_clean.csv', index=False)
    print("Created empty fictional_stars_clean.csv (no truly fictional stars)")

# Update fictional_names.py to use real star IDs
print("\n" + "="*60)
print("UPDATING FICTIONAL NAMES MAPPING")
print("="*60)

updated_fictional_names = {}

for star_id, name_data in fictional_names.items():
    if star_id in fictional_to_real_mapping:
        # Map to real star ID
        real_id = fictional_to_real_mapping[star_id]
        updated_fictional_names[real_id] = name_data
        print(f"Mapped fictional ID {star_id} → real ID {real_id} ({name_data.get('fictional_name', 'N/A')})")
    else:
        # Keep as is (either already real or truly fictional)
        updated_fictional_names[star_id] = name_data

# Write updated fictional_names.py
with open('fictional_names_updated.py', 'w') as f:
    f.write("# Updated Fictional Star Names Database\n")
    f.write("# Merged fictional data with real stars\n\n")
    f.write("fictional_star_names = {\n")
    
    for star_id, name_data in updated_fictional_names.items():
        f.write(f"    {star_id}: {{\n")
        for key, value in name_data.items():
            if isinstance(value, str):
                f.write(f"        \"{key}\": \"{value}\",\n")
            else:
                f.write(f"        \"{key}\": {value},\n")
        f.write("    },\n")
    
    f.write("}\n")

print(f"Created fictional_names_updated.py with {len(updated_fictional_names)} entries")

# Update nations_data.json to use real star IDs
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
                if territory_id in fictional_to_real_mapping:
                    real_id = fictional_to_real_mapping[territory_id]
                    updated_territories.append(real_id)
                    print(f"Updated {nation['name']} territory: fictional ID {territory_id} → real ID {real_id}")
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
    
    # Save updated nations data
    with open('nations_data_updated.json', 'w') as f:
        json.dump(nations_data, f, indent=2)
    
    print(f"Updated nations_data_updated.json with {updates_made} territory ID changes")
    
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
        if 'origin_star_id' in route and route['origin_star_id'] in fictional_to_real_mapping:
            old_id = route['origin_star_id']
            new_id = fictional_to_real_mapping[old_id]
            route['origin_star_id'] = new_id
            print(f"Updated trade route origin: fictional ID {old_id} → real ID {new_id}")
            updates_made += 1
        
        if 'destination_star_id' in route and route['destination_star_id'] in fictional_to_real_mapping:
            old_id = route['destination_star_id']
            new_id = fictional_to_real_mapping[old_id]
            route['destination_star_id'] = new_id
            print(f"Updated trade route destination: fictional ID {old_id} → real ID {new_id}")
            updates_made += 1
    
    # Save updated trade routes data
    with open('trade_routes_data_updated.json', 'w') as f:
        json.dump(trade_routes_data, f, indent=2)
    
    print(f"Updated trade_routes_data_updated.json with {updates_made} route changes")
    
except Exception as e:
    print(f"Error updating trade routes data: {e}")

# Create summary report
print("\n" + "="*60)
print("SUMMARY REPORT")
print("="*60)

print(f"📊 ORIGINAL DATA:")
print(f"  - Real stars: {len(real_stars)}")
print(f"  - Fictional stars: {len(fictional_stars)}")
print(f"  - Total: {len(real_stars) + len(fictional_stars)}")

print(f"\n📊 AFTER CLEANUP:")
print(f"  - Real stars: {len(real_stars)} (unchanged)")
print(f"  - Truly fictional stars: {len(truly_fictional)}")
print(f"  - Total: {len(real_stars) + len(truly_fictional)}")

print(f"\n🔄 MAPPINGS CREATED:")
print(f"  - Fictional → Real star mappings: {len(fictional_to_real_mapping)}")
print(f"  - Updated fictional names: {len(updated_fictional_names)}")

print(f"\n📁 FILES CREATED:")
print(f"  - fictional_stars_clean.csv (clean fictional stars)")
print(f"  - fictional_names_updated.py (updated name mappings)")
print(f"  - nations_data_updated.json (updated nation territories)")
print(f"  - trade_routes_data_updated.json (updated trade routes)")

print(f"\n🎯 NEXT STEPS:")
print(f"  1. Replace fictional_stars.csv with fictional_stars_clean.csv")
print(f"  2. Replace fictional_names.py with fictional_names_updated.py")
print(f"  3. Replace nations_data.json with nations_data_updated.json")
print(f"  4. Replace trade_routes_data.json with trade_routes_data_updated.json")
print(f"  5. Restart the application to load the updated data")

# Show the fictional to real mapping for reference
if fictional_to_real_mapping:
    print(f"\n📋 FICTIONAL TO REAL STAR MAPPINGS:")
    for fid, rid in fictional_to_real_mapping.items():
        fname = fictional_stars[fictional_stars['id'] == fid].iloc[0].get('proper', 'N/A')
        print(f"  {fid} ({fname}) → {rid}")