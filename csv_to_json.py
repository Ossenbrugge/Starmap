import csv
import json
import os

csv_file = 'data/exoplanet_catalog_20250715_114843_with_fictional.csv'  # Your CSV
json_file = 'data/exoplanets.json'

exoplanets = []
with open(csv_file, mode='r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            ra = float(row.get('ra', 0)) if row.get('ra') else 0.0
            dec = float(row.get('dec', 0)) if row.get('dec') else 0.0
            distance = float(row.get('sy_dist', 0)) if row.get('sy_dist') else 0.0
        except ValueError:
            ra = 0.0
            dec = 0.0
            distance = 0.0
        exoplanet = {
            'name': row.get('pl_name', ''),
            'host_star': row.get('hostname', ''),
            'ra': ra,
            'dec': dec,
            'distance': distance,
            'discovery_method': row.get('discoverymethod', '')
            # Add other fields
        }
        exoplanets.append(exoplanet)

os.makedirs(os.path.dirname(json_file), exist_ok=True)
with open(json_file, 'w') as f:
    json.dump(exoplanets, f, indent=4)

print(f"Converted {len(exoplanets)} exoplanets to {json_file}")