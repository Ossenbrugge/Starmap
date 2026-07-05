#!/usr/bin/env python3
"""
Province coordinate generator for Felgenland worlds.

Method (formalised from Eric's hand-built tables):
  Each province is a roughly-square lat/long bounding box + centroid, with the box
  DERIVED from the target area and LATITUDE-CORRECTED (a degree of longitude shrinks
  by cos(latitude), so boxes stay square in km, not in degrees).

  For area A (km^2) at centroid latitude phi on a planet of mean radius R (km):
      km_per_deg_lat = R * pi / 180
      side           = sqrt(A)                       # square side in km
      dlat           = side / km_per_deg_lat         # degrees of latitude
      dlon           = side / (km_per_deg_lat * cos(phi))
      NE = (phi + dlat/2, lam + dlon/2) ; SW = (phi - dlat/2, lam - dlon/2)

Modes:
  full     - tile the habitable latitudes edge-to-edge (mature worlds).
  frontier - place N settled cores of a target size inside one or more settled
             zones ("clusters"), leaving the rest of the world unclaimed. (Brandstadt)

This file is the prototype; it graduates to the Starmap project (which owns the
province DB + can render the result), emitting the same CSV/wiki column format.
"""
import math

def make_box(lat, lon, area_km2, R_km):
    """Return (clat, clon, area, ne_lat, ne_lon, sw_lat, sw_lon) for a square box."""
    km_per_deg = R_km * math.pi / 180.0
    side = math.sqrt(area_km2)
    dlat = side / km_per_deg
    dlon = side / (km_per_deg * math.cos(math.radians(lat)))
    return (round(lat, 2), round(lon, 2), int(round(area_km2)),
            round(lat + dlat/2, 2), round(lon + dlon/2, 2),
            round(lat - dlat/2, 2), round(lon - dlon/2, 2))

def cluster_grid(count, anchor_lat, anchor_lon, areas, R_km):
    """Lay `count` boxes in a centered grid around (anchor_lat, anchor_lon).
    Center slot is filled first (index 0) so a capital lands centrally.
    `areas` is a list of per-province target areas (len==count)."""
    cols = math.ceil(math.sqrt(count))
    rows = math.ceil(count / cols)
    km_per_deg = R_km * math.pi / 180.0
    # build slot centers (row,col) -> (lat,lon), spacing = a nominal box side
    nominal_side = math.sqrt(sum(areas)/len(areas))
    d_lat = nominal_side / km_per_deg
    slots = []
    for r in range(rows):
        lat = anchor_lat + (r - (rows-1)/2.0) * d_lat
        d_lon = nominal_side / (km_per_deg * math.cos(math.radians(lat)))
        for c in range(cols):
            lon = anchor_lon + (c - (cols-1)/2.0) * d_lon
            slots.append((lat, lon))
    # order slots by distance from the anchor so index 0 is central (capital)
    slots.sort(key=lambda p: (p[0]-anchor_lat)**2 + (p[1]-anchor_lon)**2)
    out = []
    for i in range(count):
        lat, lon = slots[i]
        out.append(make_box(lat, lon, areas[i], R_km))
    return out

# ---- Brandstadt driver -------------------------------------------------------
R = 8282.3  # mean radius, km  (=> 144.6 km / deg latitude)

# (num, name, continent, key_features, population, dynasty, rank)
PROV = [
 (1,"Koshkonong Star-Hollow","Northridge","Planetary capital, temperate forest, Flame Gardens",2500000,"Wilson","Herzog"),
 (2,"Boone Nexus Plains","Northridge","Grasslands, agricultural hub",2000000,"Carter","Graf"),
 (3,"Harlan Grid River","Northridge","River valley, light industry",1900000,"Bailey","Graf"),
 (4,"Cumberland Frontier Hills","Northridge","Low mountains, mining outposts",1800000,"Tucker","Graf"),
 (5,"Tupelo Star-Creek","Northridge","Coastal plains, fishing communities",2000000,"Jenkins","Graf"),
 (6,"Yazoo Orbital Fields","Northridge","Fertile farmlands, agro-processing",2100000,"Hayes","Graf"),
 (7,"Paducah Nova Bend","Northridge","River bend, trade hub",1900000,"Russell","Graf"),
 (8,"Jellico Verge Marsh","Northridge","Coastal marshes, biodiversity reserve",1800000,"Coleman","Graf"),
 (9,"Apalachee Grid Coast","Southplains","Coastal plains, port facilities",2000000,"Dixon","Graf"),
 (10,"Natchez Star-Ridge","Southplains","Grasslands, cultural festivals",2000000,"Warren","Graf"),
 (11,"Chickasaw Nexus Hollow","Southplains","Temperate forest, light industry",1900000,"Harper","Graf"),
 (12,"Okefenokee Frontier Swamp","Southplains","Wetlands, eco-tourism",1800000,"Sawyer","Graf"),
 (13,"Talladega Orbital Plains","Southplains","Grasslands, agricultural research",2100000,"Logan","Graf"),
 (14,"Dothan Nova Fields","Southplains","Farmlands, export hub",2000000,"Bennett","Graf"),
 (15,"Opelika Verge Valley","Southplains","River valley, small settlements",1800000,"Floyd","Graf"),
]
# settled-core area tracks population (=> ~1 person/km2 in-province; world stays ~0.087)
AREA = {p[0]: p[4] for p in PROV}

north = [p for p in PROV if p[2]=="Northridge"]   # 8, capital first
south = [p for p in PROV if p[2]=="Southplains"]   # 7
nb = cluster_grid(len(north), 24.0, -100.0, [AREA[p[0]] for p in north], R)
sb = cluster_grid(len(south), -22.0,  70.0, [AREA[p[0]] for p in south], R)

rows = {}
for p, box in list(zip(north, nb)) + list(zip(south, sb)):
    rows[p[0]] = (p, box)

hdr = "^ Province Number ^ Province Name ^ Dynasty Name ^ Centroid Latitude (°N) ^ Centroid Longitude (°E) ^ Area (km²) ^ NE Latitude (°N) ^ NE Longitude (°E) ^ SW Latitude (°N) ^ SW Longitude (°E) ^ Population ^ Dynast Rank ^ Continent ^ Key Features ^"
print(hdr)
tot=0
for n in range(1,16):
    (num,name,cont,feat,pop,dyn,rank),(clat,clon,area,nel,nen,swl,swn) = rows[n]
    tot+=area
    print(f"| {num} | {name} | {dyn} | {clat} | {clon} | {area:,} | {nel} | {nen} | {swl} | {swn} | {pop:,} | {rank} | {cont} | {feat} |")
print(f"\n# claimed land total: {tot:,} km2  ({100*tot/344_000_000:.1f}% of 344M)")
