#!/usr/bin/env python3
"""
Add lore columns to the nations table: population, capital_city, currency,
economy_summary, military_summary. Idempotent — skips columns that already
exist. Values are filled separately (from the Felgenland Saga canon notes);
NULL columns are simply hidden by the frontend.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "starmap.sqlite")

COLUMNS = [
    ("population",       "TEXT"),   # freeform, includes reference year
    ("capital_city",     "TEXT"),
    ("currency",         "TEXT"),
    ("economy_summary",  "TEXT"),
    ("military_summary", "TEXT"),
]


def main():
    con = sqlite3.connect(DB_PATH)
    try:
        existing = {r[1] for r in con.execute("PRAGMA table_info(nations)")}
        for name, coltype in COLUMNS:
            if name in existing:
                print(f"nations.{name} already exists — skipping")
                continue
            con.execute(f"ALTER TABLE nations ADD COLUMN {name} {coltype}")
            print(f"added nations.{name}")
        con.commit()
    finally:
        con.close()


if __name__ == "__main__":
    main()
