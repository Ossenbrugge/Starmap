from montydb import set_storage, MontyClient
import json
import math
import os
import shutil
import logging
from bson.json_util import loads

logging.basicConfig(level=logging.DEBUG)

DB_REPO = "data/starmap.db"  # SQLite file
os.makedirs(os.path.dirname(DB_REPO), exist_ok=True)
set_storage(DB_REPO, storage="sqlite")

client = MontyClient(DB_REPO)
db = client.starmap_db

def to_cartesian(ra_deg, dec_deg, distance):
    ra_rad = math.radians(ra_deg or 0)
    dec_rad = math.radians(dec_deg or 0)  # Change dec_rad to dec_deg here!
    x = distance * math.cos(dec_rad) * math.cos(ra_rad)
    y = distance * math.cos(dec_rad) * math.sin(ra_rad)
    z = distance * math.sin(dec_rad)
    return x, y, z

def migrate_collection(file_path, col_name, convert_coords=False):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data_str = f.read()
        try:
            data = loads(data_str)
            if isinstance(data, dict):
                data = data.get('regions', [])  # For stellar_regions
            if not isinstance(data, list):
                raise ValueError(f"{col_name} data is not a list")
        except Exception as e:
            logging.error(f"Error parsing {file_path}: {e}")
            return

        db[col_name].drop()
        if convert_coords:
            for item in data:
                if 'ra' in item:
                    item['x'], item['y'], item['z'] = to_cartesian(item.get('ra'), item.get('dec'), item.get('distance'))
        if data:
            db[col_name].insert_many(data)
            logging.debug(f"Imported {len(data)} items to {col_name}")
        else:
            logging.warning(f"No data to import for {col_name}")
    else:
        logging.warning(f"{file_path} not found—skipping {col_name}")

# Backup if DB exists and is file
if os.path.exists(DB_REPO) and os.path.isfile(DB_REPO):
    shutil.copy(DB_REPO, DB_REPO + '_backup')

migrate_collection('data/stars.json', 'stars', convert_coords=True)
migrate_collection('data/exoplanets.json', 'exoplanets', convert_coords=True)
migrate_collection('data/fictional_exoplanets.json', 'fictional_exoplanets', convert_coords=True)
migrate_collection('data/nations.json', 'nations')
migrate_collection('data/trade_routes.json', 'trade_routes')
migrate_collection('data/stellar_regions.json', 'stellar_regions')

print("Migration complete—check logs.")