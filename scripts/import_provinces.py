#!/usr/bin/env python3
"""
Import Felgenland Union provinces into the starmap DB.

Sources (snapshotted from ~/Documents/Brain/Felgenland Saga/ on 2026-07-03):
  data/provinces/stahlburgh_provinces_with_ranks.csv      → Stahlburgh (Holsten Tor)
  data/provinces/Eisenwald_Provinces_Updated.csv          → Eisenwald  (moon of Stahlburgh, Holsten Tor)
  data/provinces/hansaburgh_provinces_ranks_refactored.csv→ Hansaburgh (Brandenburg Tor)
  data/provinces/Lochiel_Provinces_Updated.csv            → Lochiel    (system unmapped in canon)
  BRANDSTADT list below (from Union Provinces.md)         → Brandstadt (Tiefe-Grenze Tor)

Idempotent: drops and rebuilds the provinces table (data mirrors the Brain
canon; local edits belong in the source files, not the DB).
"""

import csv
import os
import re
import sqlite3

BASE = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(BASE, "data", "starmap.sqlite")
CSV_DIR = os.path.join(BASE, "data", "provinces")

# world → (csv file, star_id) — Lochiel's host system is not yet in canon
WORLDS = [
    ("Stahlburgh", "stahlburgh_provinces_with_ranks.csv", 48941),
    ("Eisenwald",  "Eisenwald_Provinces_Updated.csv",     48941),
    ("Hansaburgh", "hansaburgh_provinces_ranks_refactored.csv", 46945),
    ("Lochiel",    "Lochiel_Provinces_Updated.csv",       None),
]

# Brandstadt's 15 provinces (Union Provinces.md, "Brandstadt Provinces" table)
BRANDSTADT = [
    # (number, name, continent, features, population, area, dynasty)
    (1, "Koshkonong Star-Hollow", "Northridge", "Planetary capital, temperate forest, Flame Gardens", 2500000, 23000000, "Wilson"),
    (2, "Boone Nexus Plains", "Northridge", "Grasslands, agricultural hub", 2000000, 22500000, "Carter"),
    (3, "Harlan Grid River", "Northridge", "River valley, light industry", 1900000, 22800000, "Bailey"),
    (4, "Cumberland Frontier Hills", "Northridge", "Low mountains, mining outposts", 1800000, 23200000, "Tucker"),
    (5, "Tupelo Star-Creek", "Northridge", "Coastal plains, fishing communities", 2000000, 22600000, "Jenkins"),
    (6, "Yazoo Orbital Fields", "Northridge", "Fertile farmlands, agro-processing", 2100000, 22900000, "Hayes"),
    (7, "Paducah Nova Bend", "Northridge", "River bend, trade hub", 1900000, 23100000, "Russell"),
    (8, "Jellico Verge Marsh", "Northridge", "Coastal marshes, biodiversity reserve", 1800000, 23400000, "Coleman"),
    (9, "Apalachee Grid Coast", "Southplains", "Coastal plains, port facilities", 2000000, 22700000, "Dixon"),
    (10, "Natchez Star-Ridge", "Southplains", "Grasslands, cultural festivals", 2000000, 22800000, "Warren"),
    (11, "Chickasaw Nexus Hollow", "Southplains", "Temperate forest, light industry", 1900000, 23000000, "Harper"),
    (12, "Okefenokee Frontier Swamp", "Southplains", "Wetlands, eco-tourism", 1800000, 23300000, "Sawyer"),
    (13, "Talladega Orbital Plains", "Southplains", "Grasslands, agricultural research", 2100000, 22600000, "Logan"),
    (14, "Dothan Nova Fields", "Southplains", "Farmlands, export hub", 2000000, 22900000, "Bennett"),
    (15, "Opelika Verge Valley", "Southplains", "River valley, small settlements", 1800000, 23100000, "Floyd"),
]


def _num(value):
    """Parse '1,600,000' / '1600000' / '' → int or None."""
    if value is None:
        return None
    s = re.sub(r"[^\d]", "", str(value))
    return int(s) if s else None


def import_csv(cur, world, filename, star_id):
    path = os.path.join(CSV_DIR, filename)
    count = 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            name = (row.get("Province Name") or "").strip()
            if not name:
                continue
            cur.execute(
                "INSERT INTO provinces (world, star_id, province_number, name, dynasty, "
                "dynast_rank, population, area_km2, notes) VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    world, star_id,
                    _num(row.get("Province Number")),
                    name,
                    (row.get("Dynasty Name") or "").strip(),
                    (row.get("Dynast Rank") or "").strip(),
                    _num(row.get("Population")),
                    _num(row.get("Area (km²)") or row.get("Area (km2)")),
                    None,
                ),
            )
            count += 1
    print(f"  {world}: {count} provinces")
    return count


def main():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS provinces;
        CREATE TABLE provinces (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            world           TEXT NOT NULL,
            star_id         INTEGER,           -- NULL when the host system is not yet canon
            province_number INTEGER,
            name            TEXT NOT NULL,
            dynasty         TEXT,
            dynast_rank     TEXT,
            population      INTEGER,
            area_km2        INTEGER,
            notes           TEXT
        );
        CREATE INDEX idx_provinces_world ON provinces(world);
        CREATE INDEX idx_provinces_star  ON provinces(star_id);
    """)

    total = 0
    for world, filename, star_id in WORLDS:
        total += import_csv(cur, world, filename, star_id)

    for num, name, continent, features, pop, area, dynasty in BRANDSTADT:
        cur.execute(
            "INSERT INTO provinces (world, star_id, province_number, name, dynasty, "
            "dynast_rank, population, area_km2, notes) VALUES (?,?,?,?,?,?,?,?,?)",
            ("Brandstadt", 999999, num, name, dynasty, "Dynast", pop, area,
             f"{continent} — {features}"),
        )
    total += len(BRANDSTADT)
    print(f"  Brandstadt: {len(BRANDSTADT)} provinces")

    con.commit()
    rows = cur.execute(
        "SELECT world, COUNT(*), SUM(population) FROM provinces GROUP BY world ORDER BY world"
    ).fetchall()
    for w, c, p in rows:
        print(f"  → {w}: {c} provinces, pop {p:,}" if p else f"  → {w}: {c} provinces")
    print(f"provinces total: {total}")
    con.close()


if __name__ == "__main__":
    main()
