from montydb import set_storage, MontyClient
import logging

logging.basicConfig(level=logging.DEBUG)

DB_REPO = "data/starmap.db"  # SQLite
set_storage(DB_REPO, storage="sqlite")

client = MontyClient(DB_REPO)
db = client.starmap_db

print("🔍 DATABASE INSPECTION REPORT")
print("==================================================")

collections = db.list_collection_names()  # Call once
print(f"📋 Collections in DB: {collections}")

for col in ['stars', 'exoplanets', 'fictional_exoplanets', 'nations', 'trade_routes', 'stellar_regions']:
    if col in collections:
        count = db[col].count_documents({})
        print(f"📊 {col} has {count} documents")
        if count > 0:
            sample = db[col].find_one()
            print(f"   Sample from {col}: {sample.get('name') or sample.get('short_name') or sample}")
        else:
            print(f"   ❌ {col} is empty!")
    else:
        print(f"   ❌ {col} collection missing!")

print("\n🔍 SPECIFIC CHECKS")
print("------------------------------")

sol = db.stars.find_one({"names.primary_name": "Sol"})  # Dot notation for subfield
if sol:
    print(f"🌞 Sol found: ID {sol.get('_id')}, Exoplanets: {{'count': {db.exoplanets.count_documents({{'host_star': 'Sol'}})}, 'has_planets': {db.exoplanets.count_documents({{'host_star': 'Sol'}}) > 0}}}")
else:
    print("❌ Sol not found!")

holsten = db.stars.find_one({"names.fictional_name": "Holsten Tor"})  # Dot notation
if holsten:
    print(f"🚀 Holsten Tor found: {holsten}")
else:
    print("❌ Holsten Tor not found!")

kepler = db.exoplanets.find_one({"name": {"$regex": "Kepler", "$options": "i"}})
if kepler:
    print(f"🌌 Kepler exoplanet sample: {kepler}")
else:
    print("❌ No Kepler exoplanets found!")

sol_planets_count = db.exoplanets.count_documents({"host_star": "Sol"}) + db.fictional_exoplanets.count_documents({"host_star": "Sol"})  # Query both
sol_planet_sample = db.exoplanets.find_one({"host_star": "Sol"}) or db.fictional_exoplanets.find_one({"host_star": "Sol"})
if sol_planets_count > 0:
    print(f"🌍 Sol system planets found: {sol_planets_count}")
    print(f"   Sample Sol planet: {sol_planet_sample.get('name')}")
else:
    print("❌ No Sol system planets found!")

print(f"\n📈 TOTALS: {db.exoplanets.count_documents({})} real exoplanets, {db.fictional_exoplanets.count_documents({})} fictional exoplanets")

print("\n🚬 Database inspection complete - time for that virtual smoke break! 🚬")