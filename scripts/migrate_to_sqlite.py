#!/usr/bin/env python3
"""
Migration script: JSON files → SQLite database.

Run once from the project root:
    python scripts/migrate_to_sqlite.py

Safe to re-run (uses INSERT OR REPLACE / INSERT OR IGNORE).
"""

import csv
import json
import os
import sqlite3
import sys

# Resolve paths relative to project root (parent of scripts/)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SCHEMA_FILE = os.path.join(ROOT, "models", "schema.sql")
DB_PATH = os.path.join(DATA_DIR, "starmap.sqlite")


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _float(v):
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _int(v):
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def load_json(filename, default=None):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"  [skip] {filename} not found")
        return default if default is not None else []
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"  [error] {filename}: {e}")
        return default if default is not None else []


# ─── Migration functions ──────────────────────────────────────────────────────

def migrate_stars(cur):
    print("Migrating stars...")
    data = load_json("stars.json", [])
    if not data:
        print("  [warn] No star data found")
        return

    inserted = 0
    for star in data:
        coords = star.get("coordinates") or {}
        names = star.get("names") or {}
        phys = star.get("physical_properties") or {}
        cat = star.get("catalog_data") or {}
        cls = star.get("classification") or {}
        pol = star.get("political") or {}

        cur.execute(
            """
            INSERT OR REPLACE INTO stars
                (id, hip, hd, bayer, flamsteed, constellation,
                 proper_name, fictional_name, fictional_description,
                 x, y, z, dist, ra, dec,
                 magnitude, absolute_magnitude, spectral_class,
                 color_index, luminosity, nation_id, is_fictional)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                _int(star.get("_id") or star.get("id")),
                _float(cat.get("hip")),
                _float(cat.get("hd")),
                str(cat.get("bayer", "") or ""),
                _float(cat.get("flamsteed")),
                str(cls.get("constellation") or ""),
                str(names.get("proper_name") or names.get("primary_name") or ""),
                str(names.get("fictional_name") or ""),
                str(names.get("fictional_description") or ""),
                _float(coords.get("x") or star.get("x")) or 0.0,
                _float(coords.get("y") or star.get("y")) or 0.0,
                _float(coords.get("z") or star.get("z")) or 0.0,
                _float(coords.get("dist") or star.get("dist")),
                _float(coords.get("ra") or star.get("ra")),
                _float(coords.get("dec") or star.get("dec")),
                _float(phys.get("magnitude") or star.get("magnitude") or star.get("mag")),
                _float(phys.get("absolute_magnitude")),
                str(phys.get("spectral_class") or star.get("spectral_class") or star.get("spect") or ""),
                _float(phys.get("color_index")),
                _float(phys.get("luminosity")),
                str(pol.get("nation_id") or ""),
                0,
            ),
        )
        inserted += 1
        if inserted % 1000 == 0:
            print(f"  {inserted}/{len(data)} stars...")

    print(f"  Done: {inserted} stars migrated")


def migrate_fictional_stars_csv(cur):
    print("Migrating fictional stars from CSV...")
    csv_path = os.path.join(DATA_DIR, "fictional_stars.csv")
    if not os.path.exists(csv_path):
        print("  [skip] fictional_stars.csv not found")
        return

    inserted = 0
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dist = _float(row.get("dist")) or 30.0
            if dist > 30.0:
                continue
            star_id = _int(row.get("id"))
            if star_id is None:
                continue
            cur.execute(
                """
                INSERT OR REPLACE INTO stars
                    (id, proper_name, fictional_name, x, y, z, dist,
                     magnitude, spectral_class, constellation, is_fictional)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    star_id,
                    str(row.get("proper") or f"Star {star_id}"),
                    str(row.get("proper") or ""),
                    _float(row.get("x")) or 0.0,
                    _float(row.get("y")) or 0.0,
                    _float(row.get("z")) or 0.0,
                    dist,
                    _float(row.get("mag")) or 8.0,
                    str(row.get("spect") or "G5V"),
                    str(row.get("con") or ""),
                    1,
                ),
            )
            inserted += 1

    print(f"  Done: {inserted} fictional stars migrated")


def migrate_exoplanets(cur):
    print("Migrating real exoplanets...")
    data = load_json("exoplanets.json", [])
    for planet in data:
        cur.execute(
            """
            INSERT OR IGNORE INTO exoplanets
                (name, host_star_name, ra, dec, distance, discovery_method, is_fictional)
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                str(planet.get("name") or ""),
                str(planet.get("host_star") or planet.get("hostname") or ""),
                _float(planet.get("ra")),
                _float(planet.get("dec")),
                _float(planet.get("distance")),
                str(planet.get("discovery_method") or ""),
                0,
            ),
        )
    print(f"  Done: {len(data)} exoplanets migrated")
    _enrich_exoplanets_from_catalog(cur)


def _enrich_exoplanets_from_catalog(cur):
    """Orbital/physical enrichment from the NASA-archive catalog export.
    exoplanets.json only carries ra/dec/distance — without this step fresh
    builds have NULL semi-major axes and the system orbital views collapse
    (found 2026-07-05 via fresh-vs-live parity diff)."""
    path = os.path.join(DATA_DIR, "exoplanet_catalog_20250715_114843_with_fictional.csv")
    if not os.path.exists(path):
        print("  [skip] exoplanet catalog CSV not found — orbits not enriched")
        return
    n = 0
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fields, vals = [], []
            for col, src in (
                ("semi_major_axis_au", "pl_orbsmax"),
                ("orbital_period_days", "pl_orbper"),
                ("planet_radius_earth", "pl_rade"),
                ("planet_mass_earth", "pl_bmasse"),
                ("equilibrium_temp_k", "pl_eqt"),
            ):
                v = _float(row.get(src))
                if v is not None:
                    fields.append(f"{col}=?")
                    vals.append(v)
            if row.get("planet_type"):
                fields.append("planet_type=?")
                vals.append(row["planet_type"])
            if row.get("potentially_habitable"):
                fields.append("potentially_habitable=?")
                vals.append(1 if row["potentially_habitable"] == "True" else 0)
            sid = _int(row.get("star_id"))
            if sid is not None:
                fields.append("star_id=?")
                vals.append(sid)
            if not fields:
                continue
            n += cur.execute(
                f"UPDATE exoplanets SET {', '.join(fields)} WHERE name=?",
                (*vals, row["pl_name"])).rowcount
    print(f"  Done: {n} exoplanets enriched with orbital data")


def migrate_fictional_exoplanets(cur):
    print("Migrating fictional exoplanets...")
    data = load_json("fictional_exoplanets.json", [])
    if isinstance(data, dict):
        data = data.get("planets") or data.get("exoplanets") or []
    for planet in data:
        cur.execute(
            """
            INSERT OR IGNORE INTO fictional_exoplanets
                (name, host_star_name, planet_type, description,
                 orbit, period, mass, radius)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                str(planet.get("name") or ""),
                str(planet.get("host_star") or ""),
                str(planet.get("type") or ""),
                str(planet.get("description") or ""),
                _float(planet.get("orbit")),
                _float(planet.get("period")),
                _float(planet.get("mass")),
                _float(planet.get("radius")),
            ),
        )
    print(f"  Done: {len(data)} fictional exoplanets migrated")


def migrate_nations(cur):
    print("Migrating nations...")
    data = load_json("nations.json", [])
    for nation in data:
        nation_id = str(nation.get("_id") or nation.get("id") or "")
        appearance = nation.get("appearance") or {}
        government = nation.get("government") or {}
        capital = nation.get("capital") or {}

        cur.execute(
            """
            INSERT OR REPLACE INTO nations
                (id, name, full_name, description, color, government_type, capital_star_id)
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                nation_id,
                str(nation.get("name") or ""),
                str(nation.get("full_name") or ""),
                str(nation.get("description") or ""),
                str(appearance.get("color") or ""),
                str(government.get("type") or ""),
                _int(capital.get("star_id")),
            ),
        )

        # Insert territory entries
        for star_id in nation.get("territories", []):
            cur.execute(
                "INSERT OR IGNORE INTO nation_territories (nation_id, star_id) VALUES (?,?)",
                (nation_id, _int(star_id)),
            )

    print(f"  Done: {len(data)} nations migrated")


def migrate_trade_routes(cur):
    print("Migrating trade routes...")
    data = load_json("trade_routes.json", [])
    for route in data:
        endpoints = route.get("endpoints") or {}
        from_ep = endpoints.get("from") or {}
        to_ep = endpoints.get("to") or {}
        control = route.get("control") or {}
        logistics = route.get("logistics") or {}

        cur.execute(
            """
            INSERT OR REPLACE INTO trade_routes
                (id, name, from_star_id, to_star_id, nation_id,
                 route_type, category, frequency)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                str(route.get("_id") or route.get("id") or ""),
                str(route.get("name") or ""),
                _int(from_ep.get("star_id")),
                _int(to_ep.get("star_id")),
                str(control.get("controlling_nation") or ""),
                str(route.get("route_type") or ""),
                str(route.get("category") or ""),
                str(logistics.get("frequency") or ""),
            ),
        )
    print(f"  Done: {len(data)} trade routes migrated")


def migrate_stellar_regions(cur):
    print("Migrating stellar regions...")
    data = load_json("stellar_regions.json", {})
    regions = data.get("regions", []) if isinstance(data, dict) else data

    for region in regions:
        color = region.get("color") or [128, 128, 128]
        x_range = region.get("x_range", [0, 30])
        y_range = region.get("y_range", [0, 30])
        z_range = region.get("z_range", [0, 30])

        cur.execute(
            """
            INSERT INTO stellar_regions
                (name, short_name, description, octant_number,
                 x_min, x_max, y_min, y_max, z_min, z_max,
                 color_r, color_g, color_b)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                str(region.get("name") or ""),
                str(region.get("short_name") or ""),
                str(region.get("description") or ""),
                _int(region.get("octant_number")),
                _float(x_range[0]), _float(x_range[1]),
                _float(y_range[0]), _float(y_range[1]),
                _float(z_range[0]), _float(z_range[1]),
                _int(color[0]) if isinstance(color, list) else 128,
                _int(color[1]) if isinstance(color, list) else 128,
                _int(color[2]) if isinstance(color, list) else 128,
            ),
        )
    print(f"  Done: {len(regions)} stellar regions migrated")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print(f"Starmap JSON → SQLite migration")
    print(f"  DB: {DB_PATH}")
    print(f"  Data: {DATA_DIR}")
    print()

    # Create schema
    with open(SCHEMA_FILE, encoding="utf-8") as f:
        schema_sql = f.read()

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode = WAL")
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(schema_sql)

    cur = con.cursor()

    try:
        migrate_stars(cur)
        migrate_fictional_stars_csv(cur)
        migrate_exoplanets(cur)
        migrate_fictional_exoplanets(cur)
        migrate_nations(cur)
        migrate_trade_routes(cur)
        migrate_stellar_regions(cur)

        con.commit()
        print()
        print("Migration complete!")

        # Print summary
        tables = ["stars", "exoplanets", "fictional_exoplanets",
                  "nations", "nation_territories", "trade_routes", "stellar_regions"]
        print("\nRow counts:")
        for table in tables:
            count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table}: {count}")

    except Exception as e:
        con.rollback()
        print(f"\nMigration FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        con.close()


if __name__ == "__main__":
    main()
