#!/usr/bin/env python3
"""
Tier-1 timeline migration: historical_events + star_ownership tables.

- historical_events: point or period events shown on the era slider and map.
  Seeded from canon already in the repo: nation foundings (nations table),
  system colonizations (stars.discovery_year), and the Felgenland Saga story
  dates that were previously hardcoded in templates/starmap.html.
- star_ownership: (star_id, nation_id, era_start, era_end) intervals so
  territory can change over time. Seeded with baseline rows derived from
  nation_territories + nation founding years + star discovery years, which
  reproduces today's behaviour exactly. Border changes (e.g. war-time flips)
  are a data edit: close one interval's era_end and insert the successor's.

Idempotent: tables are created IF NOT EXISTS and seeding is skipped when a
table already has rows. Re-run safely at any time.
"""

import os
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "starmap.sqlite")

# Canonical Felgenland Saga story events (dates from the saga timeline;
# previously hardcoded as STORY_MOMENTS / tick labels in starmap.html).
STORY_EVENTS = [
    dict(year=2170, end_year=None, title="Phoenix Exodus",
         description="Lena's death sparks the Phoenix Exodus from Sol — the first great "
                     "wave of interstellar emigration.",
         event_type="exodus", star_id=500000, nation_id=None),
    dict(year=2200, end_year=None, title="First Felgenland Settlement",
         description="Stahlburgh is founded on Holsten Tor, the first Felgenland settlement.",
         event_type="colonization", star_id=48941, nation_id="felgenland_union"),
    dict(year=2267, end_year=None, title="Felgenland Union Founded",
         description="The Felgenland Union is founded at Bundstadt on 21 June 2267.",
         event_type="founding", star_id=48941, nation_id="felgenland_union"),
    dict(year=2352, end_year=2357, title="Union–Directorate War",
         description="Open war between the Felgenland Union and the Terran Directorate, "
                     "at its height around 2355.",
         event_type="war", star_id=None, nation_id=None),
    dict(year=2379, end_year=None, title="Age of Exploration Begins",
         description="Raimond dies and Henry becomes Protector of the Felgenland Union, "
                     "opening the Age of Exploration.",
         event_type="era", star_id=None, nation_id="felgenland_union"),
]


def create_tables(con):
    con.executescript("""
        CREATE TABLE IF NOT EXISTS historical_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            year        INTEGER NOT NULL,
            end_year    INTEGER,              -- NULL = point event
            title       TEXT NOT NULL,
            description TEXT,
            event_type  TEXT NOT NULL,        -- founding|colonization|war|exodus|era|other
            star_id     INTEGER,              -- optional map pin
            nation_id   TEXT                  -- optional nation association
        );
        CREATE INDEX IF NOT EXISTS idx_events_year ON historical_events(year);

        CREATE TABLE IF NOT EXISTS star_ownership (
            star_id    INTEGER NOT NULL,
            nation_id  TEXT NOT NULL,
            era_start  INTEGER NOT NULL,
            era_end    INTEGER NOT NULL DEFAULT 3000,
            PRIMARY KEY (star_id, era_start)
        );
        CREATE INDEX IF NOT EXISTS idx_ownership_star ON star_ownership(star_id);
    """)


def seed_events(con):
    n = con.execute("SELECT COUNT(*) FROM historical_events").fetchone()[0]
    if n:
        print(f"historical_events already has {n} rows — skipping seed")
        return

    rows = []

    for ev in STORY_EVENTS:
        rows.append((ev["year"], ev["end_year"], ev["title"], ev["description"],
                     ev["event_type"], ev["star_id"], ev["nation_id"]))

    # Nation foundings from the nations table. The Felgenland Union founding is
    # covered by the richer story event above, so skip nations that already
    # have a founding event at the same year.
    manual_foundings = {(e["nation_id"], e["year"]) for e in STORY_EVENTS
                        if e["event_type"] == "founding"}
    for nat in con.execute(
            "SELECT id, name, era_start, capital_star_id, description FROM nations "
            "WHERE era_start IS NOT NULL").fetchall():
        nid, name, year, capital, desc = nat
        if (nid, year) in manual_foundings:
            continue
        first_sentence = (desc or "").split(". ")[0].strip()
        if first_sentence and not first_sentence.endswith("."):
            first_sentence += "."
        rows.append((year, None, f"{name} Established", first_sentence,
                     "founding", capital, nid))

    # System colonizations from stars.discovery_year (the 14 discovery systems).
    # Sol (discovery_number 0) has no discovery_year: always settled. Companion
    # stars (Proxima/Toliman) share the Hawking system's year but carry no
    # discovery_number — the system event covers them.
    for st in con.execute(
            "SELECT id, proper_name, fictional_name, discovery_number, discovery_year, nation_id "
            "FROM stars WHERE discovery_year IS NOT NULL AND discovery_number IS NOT NULL "
            "ORDER BY discovery_number").fetchall():
        sid, proper, fictional, dnum, dyear, nation = st
        name = (fictional or proper or f"Discovery-{int(dnum):04d}").strip()
        # 2200 Holsten Tor settlement is covered by the story event above
        if sid == 48941 and dyear == 2215:
            desc = ("Holsten Tor formally chartered as discovery system "
                    f"#{int(dnum)} (first settled 2200).")
        else:
            desc = f"Discovery system #{int(dnum)} is colonized."
        rows.append((dyear, None, f"{name} Colonized", desc,
                     "colonization", sid, nation or None))

    con.executemany(
        "INSERT INTO historical_events (year, end_year, title, description, event_type, star_id, nation_id) "
        "VALUES (?,?,?,?,?,?,?)", rows)
    print(f"Seeded {len(rows)} historical events")


def seed_ownership(con):
    n = con.execute("SELECT COUNT(*) FROM star_ownership").fetchone()[0]
    if n:
        print(f"star_ownership already has {n} rows — skipping seed")
        return

    rows = []
    for terr in con.execute("""
            SELECT t.star_id, t.nation_id, n.era_start, n.era_end, s.discovery_year
            FROM nation_territories t
            JOIN nations n ON n.id = t.nation_id
            LEFT JOIN stars s ON s.id = t.star_id
            """).fetchall():
        star_id, nation_id, n_start, n_end, dyear = terr
        start = max(v for v in (n_start or 2020, dyear) if v is not None)
        rows.append((star_id, nation_id, start, n_end or 3000))

    con.executemany(
        "INSERT INTO star_ownership (star_id, nation_id, era_start, era_end) VALUES (?,?,?,?)",
        rows)
    print(f"Seeded {len(rows)} baseline ownership intervals")


def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        sys.exit(1)
    con = sqlite3.connect(DB_PATH)
    try:
        create_tables(con)
        seed_events(con)
        seed_ownership(con)
        con.commit()
        for t in ("historical_events", "star_ownership"):
            c = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"{t}: {c} rows")
    finally:
        con.close()


if __name__ == "__main__":
    main()
