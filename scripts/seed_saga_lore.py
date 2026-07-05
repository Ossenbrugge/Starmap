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

Author rulings (2026-07-03/04):
  - Griefen Tor discovery_year 2333 was a typo → 2233 (settled during the
    Terran Exodus; Lochiel ratified the 2267 Constitution). Ownership
    interval starts at the Union founding, 2267.
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
    # Canonical title is 'Accord' (master timeline); seeding it under the old
    # 'Treaty' name caused a retitle/re-insert duplicate loop.
    (2357, None, "Accord of Dual Spheres",
     "Signed 15 January 2357 after the weeks-long armistice over Earth, the Accord carves the Rim into Union and Directorate spheres with gray-zone buffers.",
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
    # Cultural Renaissance (wiki: stars/helvetia_tor.txt, planets/neu_helvetica.txt)
    (2371, None, "Neu Helvetica Chartered",
     "The Union's first purpose-built peace colony: alpine émigrés from Stahlburgh settle "
     "Neu Helvetica under the Cultural Renaissance, governing as a confederation of cantons. "
     "Its capital Nielsenstadt honors the engineer-financier Aksel Nielsen.",
     "colonization", 47977, "felgenland_union"),
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
                            "drone-swarm doctrine under Maxim command. Byzantine in method: "
                            "subversion, sabotage and color revolutions before kinetic war",
    },
    "protelani_republic": {
        "population": "~36 million (2350 est.)",
        "capital_city": "Protelan (61 Ursae Majoris)",
        "currency": None,
        "economy_summary": "The Rim's mercantile crossroads: Grandpere orbits beyond the "
                           "star's safe jump radius, so even slow-torch-era ships could jump "
                           "straight in and out at Protelan — wealth built on geometry. "
                           "Alliance commerce with the Union and Fomalhaut",
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
        "capital_city": "Auricore City, Auricore",
        "currency": None,
        "economy_summary": "Interstellar commerce through the Mercantile Consortium; "
                           "trade outposts across the neutral frontier. Unable to match "
                           "Protelan's jump geometry, they built the Auricore Cycler — a "
                           "bazaar-lined cycler working the long crawl in from the jump "
                           "point. Sat out the Union–Directorate War and profited from "
                           "watching it",
        "military_summary": "None to speak of — the Pentothians are profiteers, not fighters",
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


def apply_author_corrections(con):
    """Typo fixes ruled by the author — idempotent, safe on rebuilt DBs."""
    con.execute("UPDATE stars SET discovery_year=2233 WHERE id=43464 AND discovery_year=2333")
    con.execute("UPDATE historical_events SET year=2233, "
                "description='Discovery system #12 is colonized during the Terran Exodus.' "
                "WHERE title='Griefen Tor Colonized' AND year=2333")
    con.execute("UPDATE star_ownership SET era_start=2267 "
                "WHERE star_id=43464 AND nation_id='felgenland_union' AND era_start=2333")


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


# ── Planetary systems (DokuWiki: stars/brandenburg_tor.txt, stars/griefen_tor.txt) ──
# host_star_name uses the fictional system name (matches the star's
# fictional_name, which the frontend includes in its host-name lookup).
# (name, host, planet_type, orbit_au, period_days, mass_earth, radius_earth, description)
SYSTEM_WORLDS = [
    # Brandenburg Tor (11 LMi) — 4 worlds
    ("Hansaburgh", "Brandenburg Tor", "Earth-like", 0.85, 360, 1.1, 1.0,
     "Temperate world of salt flats and farmland — capital of the Imperial Federation of "
     "Hansaburgh and birthplace of Karl von Machthaber. Kaiserstadt hosts the Congressional "
     "Building; Starveil Festivals mark Wogenstern's eclipses."),
    ("Salzkern", "Brandenburg Tor", "Hot Rocky", 0.3, 80, 0.4, 0.8,
     "Hot, Mercury-like world mined for metals and salts that feed Hansaburgh's economy."),
    ("Wogenstern", "Brandenburg Tor", "Gas Giant", 2.0, 1022, None, 9.0,
     "Jupiter-like giant whose icy moons host fuel depots for the Union trade lanes."),
    ("Frostmeer", "Brandenburg Tor", "Ice Giant", 7.0, 6752, 2.0, 1.5,
     "Neptune-like iceworld mined for water and methane volatiles."),
    # Griefen Tor (55 Cancri / Copernicus) — 6 worlds; saga names for the real
    # 55 Cnc planets, plus the fictional ocean world Lochiel
    ("Eisfluss", "Griefen Tor", "Hot Rocky", 0.01544, 0.74, 8.0, 1.9,
     "Super-Earth lava world (55 Cancri e) mined for rare minerals."),
    ("Wolkenmeer", "Griefen Tor", "Gas Giant", 0.1134, 14.65, None, 13.0,
     "Warm gas giant (55 Cancri b) harvested for atmospheric gases and metals."),
    ("Kernfluss", "Griefen Tor", "Gas Giant", 0.2403, 44.4, None, 8.0,
     "Warm gas dwarf (55 Cancri c) yielding volatiles and silicates."),
    ("Frostmeer", "Griefen Tor", "Ice Giant", 0.781, 260, None, 7.0,
     "Cool gas dwarf (55 Cancri f) with icy moons mined for volatiles."),
    ("Lochiel", "Griefen Tor", "Earth-like", 0.9, 320, 1.2, 1.05,
     "Habitable ocean world of archipelagos — the Union's petroleum and helium-3 hub. "
     "Capital: Strasseburgh. Sturmmeer's rare eclipses are celebrated as Tideveil Festivals."),
    ("Sturmmeer", "Griefen Tor", "Gas Giant", 5.74, 5218, None, 12.0,
     "Jupiter-like giant (55 Cancri d) whose icy moons serve as Navy fuel depots."),
]

# Stale rows superseded by the wiki docs: cities were once entered as planets,
# and Hansaburgh had two conflicting orbit entries (0.62 / 1.5 AU vs canon 0.85).
STALE_PLANETS_SQL = [
    "DELETE FROM exoplanets WHERE is_fictional=1 AND host_star_name='11 LMi' "
    "AND name IN ('Hansaburgh','Kaiserstadt','Glückstadt Nexus','Havenknot Verge')",
    # only the old wrong-orbit row (1.5 AU) — the canonical 0.85 AU row stays
    "DELETE FROM fictional_exoplanets WHERE host_star_name='Brandenburg Tor' AND name='Hansaburgh' AND orbit=1.5",
    # Brandstadt relics from before its move to Tiefe-Grenze Tor (the correct
    # row lives in fictional_exoplanets with host 'Tiefe-Grenze Tor')
    "DELETE FROM exoplanets WHERE name='Brandstadt' AND host_star_name IN ('Copernicus','Star 999999')",
]


# ── Missing worlds (drift backlog, DokuWiki dossiers, user-ruled 2026-07-04) ──
# (name, host_star_name, planet_type, orbit_au, period_days, mass, radius, parent_planet, description)
# Skipped on purpose: L 98-59 f (exists as 'Foxtrot'; the dossier's 'Fortress
# Echelon' is the installation on it), the Protelan moon (already present).
MISSING_WORLDS = [
    # Hawking system (Alpha Centauri): A = Hawking, B = Toliman, plus Proxima
    # Hawking = system; the capital WORLD is Hawking Prime (settler name New Eden)
    ("Hawking Prime", "Hawking", "Earth-like", 1.1, 438, 1.1, 1.1, None,
     "Primary habitable world of Alpha Centauri A (α Cen A c) — settler name New Eden. "
     "Temperate capital of the Centauran Assembly, a Directorate client state of "
     "700–900 million."),
    ("Galileo", "Hawking", "Gas Giant", 5.2, 4383, None, 11.0, None,
     "Jupiter-like giant whose moons host mining outposts of 5–10 million."),
    ("Kepler", "Toliman", "Rocky", 0.7, 219, 0.8, 0.9, None,
     "Arid world orbiting Toliman, used for military training; 3–5 million residents."),
    ("Hubble Outpost", "Proxima Centauri", "Rocky", 0.0485, 11.2, 1.07, 1.1, None,
     "Flare-battered habitable-zone world; its orbital station shelters 2–4 million."),
    # L 98-59 — the Directorate fortress system (Foxtrot = planet f, already present)
    ("Outpost Scorch", "L 98-59", "Hot Rocky", 0.02191, 2.25, 0.40, 0.85, None,
     "Scorched, airless sensor-array world fortified to watch the Felgenland Union."),
    ("Ironhold", "L 98-59", "Super-Earth", 0.0304, 3.69, 2.22, 1.385, None,
     "Volcanic forge world — the Directorate's major source of rare metals; 20–30 million."),
    ("Tidal Bastion", "L 98-59", "Water-rich", 0.045, 7.5, 2.31, 1.57, None,
     "Ocean world hosting floating naval fortresses; 15–20 million."),
    ("Viper's Cauldron", "L 98-59", "Super-Venus", 0.06, 12.8, 3.0, None, None,
     "Hellish pressure-cooker used for experimental weapons testing."),
    ("Stormhold", "L 98-59", "Gas Giant", 0.15, 45.2, None, 3.5, None,
     "Turbulent gas dwarf serving as a refueling depot; 10–15 million on orbital platforms."),
    ("Frostspire", "L 98-59", "Ice Giant", 0.22, 78.9, 1.8, 1.3, None,
     "Frozen prison world and interrogation center of the Directorate."),
    # Pentothia Prime (GJ 380)
    ("Vulcara", "Pentothia Prime", "Hot Rocky", 0.05, 4.5, 0.8, 0.9, None,
     "Scorched, mineral-rich Pentothian mining outpost."),
    ("Auricore", "Pentothia Prime", "Super-Earth", 0.40, 113, 1.5, 1.2, None,
     "Warm-temperate capital of the Pentothian Trade Conglomerate — Auricore City and its "
     "orbital trade stations."),
    ("Ferrum Belt", "Pentothia Prime", "Asteroid Belt", 0.3, 45, None, None, None,
     "Resource-rich belt mined for iridium and osmium."),
    ("Cryon", "Pentothia Prime", "Ice Giant", 1.0, 446, 2.0, 1.3, None,
     "Frozen world mined for fusion-grade isotopes."),
    ("Stellarion Trade Nexus", "Pentothia Prime", "Station", 189.98, 547900, None, None, None,
     "A ~100 km orbital station in the far dark — sternfomotor docks and the Conglomerate's "
     "great trade markets, parked out beyond the star's jump radius where the ships arrive."),
    # Orbit is a display placement — the Cycler plies the whole Nexus→Auricore run
    ("Auricore Cycler", "Pentothia Prime", "Cycler", 95.0, None, None, None, None,
     "The Pentothian answer to Protelan's jump geometry: a great cycler shuttling the long "
     "crawl between the Stellarion Trade Nexus and Auricore, lined like a medieval bridge "
     "with shops and mercantile bazaars — spend money while you wait to arrive."),
    # Protelan (61 UMa) — the moon Protelan itself already exists
    ("Chaud", "Protelan", "Hot Rocky", 0.3, 33, 1.5, 1.2, None,
     "Hot, Venus-like mining outpost for metals."),
    ("Frais", "Protelan", "Rocky", 1.0, 347, 0.5, 0.8, None,
     "Cool, Mars-like world worked for rare earths."),
    ("Joi", "Protelan", "Gas Giant", 2.5, 1096, None, 12.0, None,
     "Jupiter-like giant — the Protelan Republic's capital moon orbits it; its eclipses are "
     "celebrated in the Joi Veil Festival."),
    ("Froid", "Protelan", "Rocky", 4.0, 2191, 0.5, 0.8, None,
     "Cold, barren outer world."),
    ("Hiver", "Protelan", "Rocky", 73, 182620, 0.3, 0.7, None,
     "Distant desert world mined for volatiles."),
    ("Grandpere", "Protelan", "Ice Giant", 154, None, None, 10.0, None,
     "Far Neptune-like giant with distant trade stations."),
    # Lalande 21185 — Libertad, Nakdong already present; rest of the
    # lalande_21185.txt roster (user catch 2026-07-05)
    ("Gaso", "Lalande 21185", "Gas Giant", 2.94, 2946, 13.6, 4.0, None,
     "Neptune-like giant (Lalande 21185 c) whose icy moons are worked for volatiles; "
     "orbital platforms serve as refueling stations for 10–20 million."),
    ("Lumirima", "Lalande 21185", "Earth-like", 0.20, 80, 1.5, 1.0, None,
     "Serene aurora-lit world (Lalande 21185 e) of archipelagos and boreal forests — "
     "the system's cultural hub post-2357; 30–50 million."),
    ("Verdkampo", "Lalande 21185", "Earth-like", 0.25, 110, 2.0, 1.1, None,
     "Warm savanna-and-desert world (Lalande 21185 f) of agricultural colonies, a "
     "trade outpost post-2357; 50–70 million."),
    ("Marhavo", "Lalande 21185", "Earth-like", 0.30, 150, 1.8, 1.0, None,
     "Storm-swept ocean world (Lalande 21185 g), 80% sea with island continents — "
     "maritime trade ports vital post-2357; 20–30 million."),
    # Fomalhaut — Valorgraemo lives in the real-exoplanets table; these are the
    # rest of the fomalhaut.txt roster (dossier physics-corrected 2026-07-05:
    # HZ ~3.9–5.6 AU for the A3V primary, worlds at 4.3/4.7/5.2).
    ("Fomalhaut b", "Fomalhaut", "Gas Giant", 177, 620500, None, 11.0, None,
     "Distant super-Jupiter (α PsA b) whose icy moons feed resource extraction — and "
     "whose orbital defense platforms are the Republic's rimward bulwark."),
    ("Batalklendo", "Fomalhaut", "Earth-like", 4.7, 2702, 1.5, 1.1, None,
     "Rugged cool-temperate world (α PsA d) of rolling plains and coniferous forests — "
     "training ground of the Fomalhaut shock troops, and an agricultural exporter."),
    ("Marrikoviro", "Fomalhaut", "Earth-like", 5.2, 3141, 1.3, 1.0, None,
     "Storm-wracked ocean world (α PsA e), 70% sea — naval bases and trade ports "
     "vital to the Republic's maritime defense and rimward commerce."),
    # Tau Ceti — Asimov, Heinlein, Bester already present
    ("Bradbury", "Tau Ceti", "Super-Earth", 0.133, 20.0, 3.1, None, None,
     "Hot, rocky world of Directorate weapons-testing bunkers; 80–100 million."),
    ("Clarke", "Tau Ceti", "Super-Earth", 0.195, 34.7, 3.6, None, None,
     "Dense, iron-rich world under a thin CO₂ atmosphere; 50–70 million."),
    ("Herbert", "Tau Ceti", "Super-Earth", 1.334, 636.13, 3.9, None, None,
     "Cold world on the outer habitable edge — icy continents, 70–90 million."),
    # Tiefe-Grenze Tor — Brandstadt already present
    ("Felsbrand", "Tiefe-Grenze Tor", "Hot Rocky", 0.4, 55, 0.6, 0.9, None,
     "Hot, Venus-like world mined for rare metals."),
    ("Sturmholz", "Tiefe-Grenze Tor", "Gas Giant", 2.5, 1461, None, 10.0, None,
     "Jupiter-like giant whose moons supply volatiles."),
    ("Frostkern", "Tiefe-Grenze Tor", "Ice Giant", 8.0, 8401, 2.0, 1.5, None,
     "Neptune-like iceworld of methane and water ices."),
    # Sol
    ("Titan", "Sol", "Rocky Moon", 9.58, None, 0.0225, 0.2495, "Saturn",
     "Saturn's colonized moon — birthplace of Lena Kocher, mother of the Phoenix Exodus."),
]


def seed_missing_worlds(con):
    n = 0
    for name, host, ptype, orbit, period, mass, radius, parent, desc in MISSING_WORLDS:
        exists = con.execute(
            "SELECT 1 FROM fictional_exoplanets WHERE name=? AND host_star_name=?",
            (name, host)).fetchone()
        if exists:
            continue
        con.execute(
            "INSERT INTO fictional_exoplanets (name, host_star_name, planet_type, "
            "description, orbit, period, mass, radius, parent_planet) VALUES (?,?,?,?,?,?,?,?,?)",
            (name, host, ptype, desc, orbit, period, mass, radius, parent))
        n += 1
    # The Protelan capital moon orbits Joi (61 UMa c I per the dossier)
    con.execute("UPDATE fictional_exoplanets SET parent_planet='Joi' "
                "WHERE name='Protelan' AND (parent_planet IS NULL OR parent_planet='')")
    print(f"missing worlds: inserted {n} of {len(MISSING_WORLDS)}")


# New star rows / namings (user rulings 2026-07-04):
#   - Pathfinder Tor = HD 87883 (star 49558); Explorer Corps prize, settled
#     post-2380 — discovery_year 2380 is an APPROXIMATION pending exact canon.
#   - Shattensonne = 20 LMi B, M7V companion of Holstensonne (20 LMi A);
#     placed 0.05 pc from Holsten Tor for visibility.
#   - Argylle Tor = HD 99492 (star 55681, discovery #13, colonized 2356 —
#     matches the dossier's 2356 survey/landing). NOTE: the wiki dossier says
#     "15 ly from Holsten Tor" but the real separation is 33.8 ly — wiki-side
#     correction pending. Argylle orbit AUs below are DISPLAY ESTIMATES (the
#     dossier gives none); Heatherly sits in the computed K0V habitable zone.
ARGYLLE_WORLDS = [
    ("Argylle I", "Argylle Tor", "Hot Rocky", 0.08, 12, None, 1.2, None,
     'Tidally locked super-Mercury nicknamed "Scorch" — dayside over 800 K, rich in '
     "refractory metals. Surveyed but not colonized."),
    ("Argylle II", "Argylle Tor", "Rocky", 0.35, 100, None, 0.6, None,
     'Barren, airless world nicknamed "Cinder" — ancient lava flows, used as a low-gravity '
     "training range for Assault drop operations."),
    # Heatherly itself already exists in the exoplanets table (0.88 AU, 255 K)
    ("Argylle IV", "Argylle Tor", "Ice Giant", 2.5, 1600, None, 2.0, None,
     'Icy super-Earth nicknamed "Shield" — nitrogen-methane atmosphere, cryovolcanism, a '
     "forward listening post over a subsurface ocean."),
    ("Argylle V", "Argylle Tor", "Gas Giant", 6.0, 6000, None, 11.0, None,
     'Ringed gas giant nicknamed "Guardian" — helium-3 and deuterium mining platforms shelter '
     "in its magnetic field beside a naval refueling station."),
]


def seed_new_stars(con):
    # Helvetia Tor = 15 LMi / HD 84737 (star 47977) — user ruled 2026-07-04.
    # 17.3 ly from Holsten Tor (inside the 10-20 ly band the wiki requires),
    # G2V solar twin, unclaimed until now. Neu Helvetica's 1.7 AU orbit is a
    # display estimate placing it at the inner-temperate edge of the computed
    # 1.58-2.27 AU habitable zone (L = 2.73 Lsun).
    con.execute(
        "UPDATE stars SET fictional_name='Helvetia Tor', discovery_year=2371, "
        "fictional_description='G2V solar twin designated Helvetia Tor at the 2371 chartering "
        "of Neu Helvetica — a Cultural Renaissance peace colony in the Leo Minor home cluster, "
        "17.3 light-years from Holsten Tor.' WHERE hd=84737")
    con.execute(
        "INSERT OR REPLACE INTO star_ownership (star_id, nation_id, era_start, era_end) "
        "VALUES (47977, 'felgenland_union', 2371, 3000)")
    if not con.execute("SELECT 1 FROM fictional_exoplanets WHERE name='Neu Helvetica' "
                       "AND host_star_name='Helvetia Tor'").fetchone():
        con.execute(
            "INSERT INTO fictional_exoplanets (name, host_star_name, planet_type, "
            "description, orbit, period, mass, radius, parent_planet) VALUES (?,?,?,?,?,?,?,?,?)",
            ("Neu Helvetica", "Helvetia Tor", "Earth-like",
             "New Switzerland: a rugged, geologically young world of folded mountains, glacial "
             "valleys and cold high lakes — 45% land, seeded with cold-tolerant Earth and "
             "Stahlburgher stock. Capital Nielsenstadt anchors precision manufacturing and the "
             "rim's financial-clearing sector; its cantons answer to no Dynast, only their ballots.",
             1.7, 770, None, 1.0, None))

    con.execute(
        "UPDATE stars SET fictional_name='Argylle Tor', "
        "fictional_description='K0V orange dwarf named in 2356 for Alasdair Campbell''s "
        "province of Argyll-Inveraray-on-the-Greenwich — a frontier gateway star and home of "
        "the Heatherly colony.' WHERE hd=99492")
    # Union holding from the 2356 settlement (political color via ownership;
    # deliberately NOT added to nation_territories so the frontier colony does
    # not balloon the core Felgenland boundary hull)
    con.execute(
        "INSERT OR REPLACE INTO star_ownership (star_id, nation_id, era_start, era_end) "
        "VALUES (55681, 'felgenland_union', 2356, 3000)")
    # Real detected planets (HD 99492 b/c) stay in the catalog under the
    # star's alias designation so the canon Argylle system view stays clean
    con.execute(
        "UPDATE exoplanets SET host_star_name='83 Leonis B' "
        "WHERE is_fictional=0 AND host_star_name='HD 99492'")
    # Remove the short-lived duplicate Heatherly (the richer exoplanets-table
    # row from an earlier session is canonical)
    con.execute(
        "DELETE FROM fictional_exoplanets WHERE name='Heatherly' AND host_star_name='Argylle Tor'")
    for row in ARGYLLE_WORLDS:
        name, host = row[0], row[1]
        if not con.execute("SELECT 1 FROM fictional_exoplanets WHERE name=? AND host_star_name=?",
                           (name, host)).fetchone():
            con.execute(
                "INSERT INTO fictional_exoplanets (name, host_star_name, planet_type, "
                "description, orbit, period, mass, radius, parent_planet) VALUES (?,?,?,?,?,?,?,?,?)",
                (name, host, row[2], row[8], row[3], row[4], row[5], row[6], row[7]))
    con.execute(
        "UPDATE stars SET fictional_name='Pathfinder Tor', discovery_year=2380, "
        "fictional_description='The Explorer Corps'' first great prize: a long-lived K0 dwarf "
        "with a near-Earth world in its habitable zone, opened for settlement by the Pathfinder "
        "Teams and named in their honor.' WHERE hd=87883")
    # INSERT OR IGNORE (not REPLACE): on fresh builds seed_star_canon's
    # FULL_STARS has already created this row WITH photometry (abs mag,
    # luminosity, color index, ra/dec) — a REPLACE here wiped those columns.
    con.execute(
        "INSERT OR IGNORE INTO stars (id, proper_name, fictional_name, fictional_description, "
        "x, y, z, dist, magnitude, absolute_magnitude, luminosity, color_index, ra, dec, "
        "spectral_class, is_fictional) "
        "VALUES (999997, '20 LMi B', 'Shattensonne', "
        "'The shadow-sun: 20 Leonis Minoris B, the M7V red dwarf companion of Holstensonne. "
        "A symbol of companionship in Union lore.', "
        "-11.038308, 6.336788, 7.956742, 14.93, 14.0, 13.1, 0.0005, 2.0, 10.031, 31.966, "
        "'M7V', 1)")
    print("new stars: Pathfinder Tor named (HD 87883), Shattensonne added (20 LMi B)")


def seed_system_worlds(con):
    for sql in STALE_PLANETS_SQL:
        con.execute(sql)
    n = 0
    for name, host, ptype, orbit, period, mass, radius, desc in SYSTEM_WORLDS:
        exists = con.execute(
            "SELECT 1 FROM fictional_exoplanets WHERE name=? AND host_star_name=?",
            (name, host)).fetchone()
        if exists:
            continue
        con.execute(
            "INSERT INTO fictional_exoplanets (name, host_star_name, planet_type, "
            "description, orbit, period, mass, radius) VALUES (?,?,?,?,?,?,?,?)",
            (name, host, ptype, desc, orbit, period, mass, radius))
        n += 1
    print(f"system worlds: inserted {n} of {len(SYSTEM_WORLDS)} (stale city-planets removed)")


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
        seed_system_worlds(con)
        seed_missing_worlds(con)
        seed_new_stars(con)
        apply_author_corrections(con)
        con.commit()

        total = con.execute("SELECT COUNT(*) FROM historical_events").fetchone()[0]
        print(f"historical_events total: {total}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
