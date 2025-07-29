from montydb import MontyClient
import logging
logging.basicConfig(level=logging.DEBUG)

DB_REPO = "./starmap_db"  # Updated to match our actual DB path
client = MontyClient(DB_REPO)
db = client.starmap  # Use the correct database name from the collections

print("🔍 DATABASE INSPECTION REPORT")
print("=" * 50)

# List all collections
collections = db.list_collection_names()
print(f"📋 Collections in DB: {collections}")

# Count documents in key collections
collection_names = ['stars', 'exoplanets', 'fictional_exoplanets', 'nations', 'trade_routes', 'stellar_regions']
for col in collection_names:
    if col in collections:
        count = db[col].count_documents({})
        print(f"📊 {col} has {count} documents")
        
        # Sample one if exists
        sample = db[col].find_one()
        if sample:
            # Show just the key fields for readability
            if col == 'stars':
                name = sample.get('names', {}).get('primary_name', 'Unknown')
                print(f"   Sample star: {name} (ID: {sample.get('_id')})")
            elif col in ['exoplanets', 'fictional_exoplanets']:
                name = sample.get('name', 'Unknown')
                host = sample.get('host_star_name', sample.get('host_star', {}).get('name', 'Unknown'))
                print(f"   Sample planet: {name} orbiting {host}")
            elif col == 'nations':
                name = sample.get('name', 'Unknown')
                print(f"   Sample nation: {name}")
            elif col == 'trade_routes':
                name = sample.get('name', 'Unknown')
                print(f"   Sample route: {name}")
            else:
                print(f"   Sample from {col}: {str(sample)[:100]}...")
        else:
            print(f"   ❌ {col} is empty!")
    else:
        print(f"   ❌ {col} collection missing!")

print("\n🔍 SPECIFIC CHECKS")
print("-" * 30)

# Check for Sol
sol = db.stars.find_one({"names.primary_name": "Sol"})
if sol:
    print(f"🌞 Sol found: ID {sol['_id']}, Exoplanets: {sol.get('exoplanets', {})}")
else:
    print("❌ Sol not found!")

# Check for Holsten Tor (fictional star)
fictional_star = db.stars.find_one({"names.fictional_name": "Holsten Tor"})
if not fictional_star:
    fictional_star = db.stars.find_one({"names.primary_name": "Holsten Tor"})
if fictional_star:
    print(f"🚀 Holsten Tor found: {fictional_star['names']}")
else:
    print("❌ No Holsten Tor found!")

# Check for Kepler exoplanet
kepler = db.exoplanets.find_one({"name": {"$regex": "Kepler", "$options": "i"}})
if kepler:
    print(f"🪐 Kepler exoplanet found: {kepler['name']}")
else:
    print("❌ No Kepler exoplanets found!")

# Check for Sol system planets
sol_planets = list(db.fictional_exoplanets.find({"star_id": 500000}))
if sol_planets:
    planet_names = [p['name'] for p in sol_planets]
    print(f"🌍 Sol system ({len(sol_planets)} planets): {', '.join(planet_names)}")
else:
    print("❌ No Sol system planets found!")

# Check for any fictional exoplanets
fictional_count = db.fictional_exoplanets.count_documents({})
real_count = db.exoplanets.count_documents({})
print(f"\n📈 TOTALS: {real_count} real exoplanets, {fictional_count} fictional exoplanets")

print("\n🚬 Database inspection complete - time for that virtual smoke break! 🚬")