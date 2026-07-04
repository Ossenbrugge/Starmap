#!/usr/bin/env python3
"""
Seed Felgenland Saga canon into the starmap, extracted 2026-07-03 from the
author's notes in ~/Documents/Brain/Felgenland Saga/ (source file noted per
block). Two payloads:

  1. historical_events — nation-scale dated events (battles, treaties,
     elections, religious history). Idempotent: inserted only if an event
     with the same title does not already exist.
  2. nations lore columns (population, capital_city, currency,
     economy_summary, military_summary — added by migrate_nation_lore.py).
     Always overwritten: these mirror the Brain canon.

Author rulings (2026-07-03):
  - War span is 2352-2357: armistice 2356, drawdown, treaty SIGNED 2357.
  - Felgenland capital city is Bundstadt, on Stahlburgh, in Holsten Tor.
  - Lalande 21185 was a Terran Directorate client state, liberated 2353;
    the Lalande Republic exists from 2353 (ownership interval flip below).
  - Terran population: 52B (Populations.md) supersedes nations.json ~15.2B.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "starmap.sqlite")

# (year, end_year, title, description, event_type, star_id, nation_id)
EVENTS = [
    # ── Pre-Exodus Earth (Miscellaneous.md, _BOOK 0 Source Dossier.md) ──
    (2080, None, "Sino-Indian–Caliphate War",
     "Religious war on Earth destroys the Islamic holy sites; New Age Islam is born from the ashes.",
     "war", 500000, None),
    (2089, None, "Sammelvolk First Contact",
     "The Sammelvolk make first contact with humanity; suppression of the old faiths begins.",
     "contact", 500000, None),
    (2090, None, "Sammelvolk Landing at Beijing",
     "The Sammelvolk land in Beijing on 15 October; the McWilliams Institute is founded and the first Hybrid, Miranda, is created.",
     "contact", 500000, None),
    # ── Exodus and settlement (_BOOK 0, Colonization numbers.md, Union Provinces.md) ──
    (2170, 2200, "Terran Exodus",
     "The great colonization wave: Phoenix refugees and settlers carry the stolen sternfomotor drive to the near-rim stars.",
     "exodus", None, None),
    # Hansaburgh is in Brandenburg Tor per the Stellar & Planetary Catalog
    # ("Hansaburgh is correctly placed in Brandenburg Tor") — the BOOK 0
    # dossier's "Wolf 359/Hansaburgh" references are outdated.
    (2200, None, "Hansaburgh Founded",
     "Rolf the Navigator founds Hansaburgh on Brandenburg Tor and becomes its first Emperor.",
     "founding", 46945, None),
    (2215, None, "Eisenwald Settled",
     "The jungle moon of Stahlburgh is settled — the Union's future industrial heart.",
     "colonization", 48941, "felgenland_union"),
    (2225, None, "Brandstadt Settlement Begins",
     "American frontier settlers begin colonizing Brandstadt on Tiefe-Grenze Tor.",
     "colonization", 999999, "felgenland_union"),
    # ── Faith and founding (Gospel of Malcolm, 4th/5th Stahlburgh.md) ──
    (2231, 2233, "Central Christian Orthodoxy Founded",
     "Malcolm's ministry on Steel unifies the faithful against Ó Gallchobhair oppression.",
     "religious", 48941, None),
    (2236, None, "Martyrdom of Saint Malcolm",
     "Malcolm is martyred on the Rock of the Saints on 26 November — the cornerstone of the Orthodoxy.",
     "religious", 48941, None),
    (2242, None, "Dynast Revolt on Hansaburgh",
     "Salt-Dynast oligarchs usurp Hansaburgh and kill Emperor Johannes as the salt monopoly collapses; young Karl is enslaved by pirates.",
     "political", 46945, None),
    (2259, None, "Reconquest of Hansaburgh",
     "Karl the Iron Fist retakes Hansaburgh from the usurpers and founds House von Machthaber.",
     "battle", 46945, None),
    (2266, None, "Battle of the Landing",
     "Karl's hundred thousand Assaultmen break the Ó Gallchobhair tyrants in the Valley of the First Farmers, opening the way to Union.",
     "battle", 48941, None),
    # ── Union–Directorate War era (Battle of Wolf 359.md, Peace Talks.md, Maxim Shake up of 2357.md) ──
    (2352, None, "Raimond Becomes Protector",
     "Karl von Machthaber dies at 119; his grandson Raimond succeeds him and leads the Union into war with the Directorate.",
     "political", 48941, "felgenland_union"),
    (2353, 2354, "Battles of Foxtrot",
     "The Directorate destroys the Union Fourth Fleet at Foxtrot in October 2353; a six-month guerrilla campaign ends in the March 2354 breakout.",
     "battle", 113008, None),
    (2356, None, "Battle of Wolf 359",
     "Union divisions under General Eisenbach storm the Directorate's Wolf 359 yards, 12–14 March, crippling its war machine and forcing truce talks.",
     "battle", 118720, None),
    (2356, None, "Peace Talks at Beijing Arcology",
     "Henry and Bonnie face Maxim-Ambassador Victoria at the Beijing Arcology; the Union's allies hold firm for peace and trade.",
     "treaty", 500000, None),
    (2357, None, "Treaty of the Dual Spheres",
     "After the 2356 armistice and a year of drawdown, the treaty is signed, carving the Rim into Union and Directorate spheres of influence with gray-zone buffers like Tau Ceti.",
     "treaty", None, None),
    (2353, None, "Liberation of Lalande 21185",
     "Union forces liberate the Directorate client state at Lalande 21185; the Lalande Republic is born.",
     "battle", 53879, None),
    (2356, None, "Stahlburgh Wheat Famine",
     "Wheat shortages threaten food security and whisky production, shaking the Union's political economy before the 2357 elections.",
     "disaster", 48941, "felgenland_union"),
    # ── Post-war (Dynast Snap Election 2357.md, Potential results of 2357.md, Election 2379.md) ──
    (2357, None, "Post-War Elections of 2357",
     "Gordon's Gold coalition holds the Dynasts in a snap election while von Mackensen's Liberal Federalists take the Commons.",
     "election", None, "felgenland_union"),
    (2357, None, "Maxim Leadership Purges",
     "Post-treaty purges sweep the Directorate: war-era Maxims disappear and Caligula rises as Supreme Leader.",
     "political", None, "terran_directorate"),
    (2357, None, "Lalande Partnership Established",
     "A post-war trade partnership links the Union with the Lalande 21185 Republic.",
     "political", 53879, None),
    (2379, None, "Protector Election of 2379",
     "Henry von Machthaber wins 738 of 973 electors on an Expansionist platform, defeating Maria Therese's Preservationists.",
     "election", None, "felgenland_union"),
]

# nation_id → column → value (sources: Constitution, Union Provinces.md,
# Felgenland Saga Populations.md, War Budget Breakdown.md, Peace Talks.md,
# Stellar & Planetary Catalog.md, Dramatis Personae, Miscellaneous.md)
NATION_LORE = {
    "felgenland_union": {
        "population": "~660 million (2350 est., incl. Brandstadt)",
        "capital_city": "Bundstadt, Stahlburgh (Holsten Tor)",
        "currency": "Union Gold Dragon (UGD)",
        "economy_summary": "Salt trade on Hansaburgh, alpine agriculture and mining on "
                           "Stahlburgh, tropical flora on Eisenwald, fisheries on Lochiel, "
                           "agriculture and light industry on Brandstadt",
        "military_summary": "The Assault (incl. MjGA mecha-jäger grenadiers), Union Navy, "
                            "Line Guards, and the USIS intelligence service",
    },
    "terran_directorate": {
        "population": "~52 billion (2352 est.; 50 billion on Earth)",
        "capital_city": "Beijing Arcology, Earth",
        "currency": None,
        "economy_summary": "Sammelvolk-derived technology, genetic engineering, AI and "
                           "heavy industry, fed by client-state tribute",
        "military_summary": "Zhan Li- and Yin Ching-class cruiser fleets with stealth and "
                            "drone-swarm doctrine under Maxim command",
    },
    "protelani_republic": {
        "population": "~36 million (2350 est.)",
        "capital_city": "Protelan (61 Ursae Majoris)",
        "currency": None,
        "economy_summary": "Independent trade hub; alliance commerce with the Union and Fomalhaut",
        "military_summary": "Republic Navy under Grand Admiral Katje Sorensen; "
                            "Protelani Space Marines",
    },
    "dorsai_republic": {
        "population": "~80 million (2350 est.)",
        "capital_city": "Valorgraemo (Fomalhaut)",
        "currency": None,
        "economy_summary": "Military-professional services — soldiers and strategists are "
                           "the Republic's primary export",
        "military_summary": "Professional contract military famed for tactical discipline; "
                            "credo \"non cedemus\" — we will not yield",
    },
    "neutral_zone": {
        "population": None,
        "capital_city": "Pentothia Prime",
        "currency": None,
        "economy_summary": "Interstellar commerce through the Mercantile Consortium; "
                           "trade outposts across the neutral frontier",
        "military_summary": None,
    },
}


# The Lalande Republic: Directorate client state liberated in 2353 (author
# ruling). Color is a display choice (no canon color exists yet).
LALANDE = dict(
    id="lalande_republic",
    name="Lalande Republic",
    full_name="The Lalande 21185 Republic",
    description="Born from the Society of the Human Phoenix's first refuge — the Star Anchor "
                "jumped to Lalande 21185 in 2168 — the system spent decades as a Terran "
                "Directorate client state until its liberation in 2353. The young Republic "
                "signed a trade partnership with the Felgenland Union in 2357.",
    color="#FF9800",
    government_type="Republic",
    capital_star_id=53879,
    era_start=2353,
    era_end=3000,
)


def seed_lalande(con):
    con.execute(
        "INSERT OR REPLACE INTO nations (id, name, full_name, description, color, "
        "government_type, capital_star_id, era_start, era_end) VALUES (?,?,?,?,?,?,?,?,?)",
        (LALANDE["id"], LALANDE["name"], LALANDE["full_name"], LALANDE["description"],
         LALANDE["color"], LALANDE["government_type"], LALANDE["capital_star_id"],
         LALANDE["era_start"], LALANDE["era_end"]),
    )
    con.execute(
        "INSERT OR IGNORE INTO nation_territories (nation_id, star_id) VALUES (?, ?)",
        (LALANDE["id"], 53879),
    )
    # Ownership flip: Terran client 2170–2352, Lalande Republic from 2353
    con.execute(
        "UPDATE star_ownership SET era_end = 2352 "
        "WHERE star_id = 53879 AND nation_id = 'terran_directorate'",
    )
    con.execute(
        "INSERT OR REPLACE INTO star_ownership (star_id, nation_id, era_start, era_end) "
        "VALUES (53879, 'lalande_republic', 2353, 3000)",
    )
    print("lalande_republic: nation, territory and ownership flip seeded")


def main():
    con = sqlite3.connect(DB_PATH)
    try:
        inserted = 0
        for ev in EVENTS:
            year, end_year, title, desc, etype, star_id, nation_id = ev
            exists = con.execute(
                "SELECT 1 FROM historical_events WHERE title = ?", (title,)
            ).fetchone()
            if exists:
                continue
            con.execute(
                "INSERT INTO historical_events (year, end_year, title, description, event_type, star_id, nation_id) "
                "VALUES (?,?,?,?,?,?,?)",
                (year, end_year, title, desc, etype, star_id, nation_id),
            )
            inserted += 1
        print(f"events: inserted {inserted} new (of {len(EVENTS)} canonical)")

        for nid, cols in NATION_LORE.items():
            sets = ", ".join(f"{c} = ?" for c in cols)
            con.execute(
                f"UPDATE nations SET {sets} WHERE id = ?",
                (*cols.values(), nid),
            )
        print(f"nation lore: updated {len(NATION_LORE)} nations")
        seed_lalande(con)
        con.commit()

        total = con.execute("SELECT COUNT(*) FROM historical_events").fetchone()[0]
        print(f"historical_events total: {total}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
