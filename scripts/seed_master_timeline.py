#!/usr/bin/env python3
"""
Master Timeline canon layer — from the CANON-CERTIFIED source of truth:
_wiki-sync/.../pages/felgenland_master_timeline.txt ("Manuscripts win").
Applied 2026-07-04; supersedes several earlier-seeded events and dates.

Chain position: LAST canon step (after seed_saga_lore.py). Idempotent:
deletes superseded titles, updates by title, inserts if absent.

Key rulings encoded:
  - War chronology per the locked timeline (First Asimov 2350 pre-declaration,
    declaration 24 Nov 2352, Foxtrot Oct 2353 / Mar 2354, Second Asimov June
    2354, truce Jun–Oct 2354, Bester Dec 2354, Foundation Plague 2354–2356,
    fighting ends 2356, ACCORD of Dual Spheres signed 15 Jan 2357).
  - Tau Ceti: Directorate stronghold → Union 1055 er... 2355 (system table).
  - Protelan: Republic founded 1 Aug 2184 (older than the Union!); accedes to
    the Union ~2390 → nation era 2184–2390 + ownership flip.
  - Settlement dates reconciled: Hansaburgh founded 2200 by Hadrian von Saltz
    (Rolf discovered ~2185, installed figurehead Kaiser); Stahlburgh/Eisenwald
    2215; Brandstadt ~2220 (named 2225); Lochiel 2230 (supersedes the earlier
    2233 typo-fix ruling); L 98-59 Terran frontier 2225.
  - Era structure through 2510+ (Cultural Renaissance … Splintering ⚠ TBD).
  - Toliman keeps its proper name (the system-wide settler name 'Hawking'
    stays on the primary only) — fixes the doubled entry in nation panels.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "starmap.sqlite")

SUPERSEDED_TITLES = [
    "Sammelvolk First Contact",          # → Sammelvolk Arrive on Earth (2093)
    "Sammelvolk Landing at Beijing",     # folded into arrival; MWI is 2097
    "First Felgenland Settlement",       # 2200 was Hansaburgh, not Stahlburgh
    "Brandenburg Tor Colonized",         # merged into Hansaburgh Founded
    "Protelan Colonized",                # superseded by 2184 Republic founding
    "Battles of Foxtrot",                # split: orbital 2353 / ground 2354
    "Stahlburgh Wheat Famine",           # subsumed by the Foundation Plague
    "Age of Exploration Begins",         # → Era of Exploration period event
    # 2026-07-04 revision: AENEAS BURDEN was the UNION raid on Alpha Centauri;
    # the Ashur/Asher fight was the home-front counterstroke — split in two
    "Operation AENEAS BURDEN — Battle of Ashur",
]

# title → (year, end_year, description)  [None year = keep existing]
EVENT_UPDATES = {
    "Hansaburgh Founded": (2200, None,
        "Kapitän Hadrian von Saltz founds Hansaburgh on Brandenburg Tor (~12,000 colonists; "
        "the Congress of Hansaburgh; salt-mining). Rolf the Navigator — who first reached the "
        "system ~2185 — returns and is installed first Kaiser, a figurehead for the oligarchy."),
    "Holsten Tor Colonized": (2215, None,
        "Stahlburgh is settled under H. Malcolm MacLeod — discovery system #9, the Union's "
        "future capital world."),
    "Eisenwald Settled": (2215, None,
        "The jungle moon of Stahlburgh is settled under Liam MacCarthy — the Union's future "
        "industrial heart."),
    "Brandstadt Settlement Begins": (2220, None,
        "American frontier settlers begin colonizing Brandstadt; Tiefe-Grenze Tor is named in "
        "2225. Brandstadt becomes a full Union province in 2355."),
    "Griefen Tor Colonized": (2230, None,
        "Lochiel is settled under Captain Jonas Strass — petroleum and helium-3 for the rim."),
    "Protelan Republic Established": (2184, None,
        "The Republic of Protelan is founded on 1 August 2184 at 61 Ursae Majoris — "
        "ultra-capitalist, independent, and older than the Union itself. Capital: Havskrun."),
    "Lalande 21185 Colonized": (2170, None,
        "Libertad — the first colony outside Sol — is settled at Lalande 21185; Nakdong follows "
        "later in-system."),
    "Liberation of Lalande 21185": (2353, None,
        "Early 2353: Union Assault and Navy forces liberate Nakdong and the Lalande system, "
        "ending the civil war the Directorate's color revolution ignited."),
    "Union–Directorate War": (2352, 2357,
        "Declared 24 November 2352, eleven days after Karl's death. Five years of rim-wide war "
        "end with the 2356 armistice and the Accord of Dual Spheres, signed 15 January 2357."),
    "Treaty of the Dual Spheres": (2357, None,
        "Signed 15 January 2357 after the weeks-long armistice over Earth, the Accord carves "
        "the Rim into Union and Directorate spheres with gray-zone buffers."),
    "Peace Talks at Beijing Arcology": (2356, None,
        "With the Directorate collapsing into internal chaos and Allied fleets floating over "
        "Earth, Henry and Bonnie face Maxim-Ambassador Victoria at the Beijing Arcology."),
    # ── 2026-07-04 timeline revision ──
    "Operation Glorious Dead": (2353, None,
        "By ~August 2353, the Lalande campaign's ender: Jurgen's suicide bunker assault "
        "decapitates the enemy command, killing the tyrant Xiomar Zhan-Li Esperanza. Wounded, "
        "he receives the Golden Segreant Griffin in hospital."),
    "Liberation of Lalande 21185": (2353, None,
        "With Esperanza dead, Nakdong and the Lalande system are liberated (~mid-August 2353), "
        "ending the civil war. The War Chancellery trumpets a triumph; in truth a mediocre "
        "success that the coming Foxtrot disaster will expose."),
    "The Foundation Plague": (2354, 2356,
        "Loosed on the rim by the Directorate after the truce collapse — a pandemic first "
        "blamed on the Assault after an Asimov outbreak. It rots the Stahlburgh and Eisenwald "
        "harvests into famine; core-world families flee to Hansaburgh."),
    "Battle of Procyon": (2355, None,
        "Early 2355, on the ground: the Fomalhaut Republic Mobile Infantry carry Procyon after "
        "hard fighting — General Eachan's son Donal among the dead — with Lenart's 7th Fleet "
        "in close support. The Protelani Space Marines fare badly; the Fomalhaut infantry "
        "win it."),
    "Battle of Eiswelt": (2355, None,
        "The Pale Horse over Eiswelt: a 'small' Terran listening post on the capital system's "
        "ice world proves a major fleet trap. Jurgen's 75th Grenadiers raid the post; the Navy "
        "wins at terrible cost — O'Riordan's flagship Duchess Máire Gleann O'Cruadhlaoich is "
        "rammed by cloaked Terrans. The ambush births a new doctrine: Directorate stars, not "
        "client states."),
    "Battle of Wolf 359": (2355, None,
        "Weeks after Eiswelt, the new doctrine's first blow: Field Marshal von Eisenbach and "
        "Fleet Admiral von Stahlgeist gut the Terran orbital industry — the Locking yards and "
        "the Ramsen Orbital Forge — as the 7th and 8th Stahlburgh Rifles land. 'The Assault "
        "had gutted Wolf 359's heart.'"),
    "Battle of Protelan": (2355, None,
        "Near-simultaneous with Wolf 359: a cloaked Terran First Fleet slips toward Protelan "
        "while Henry is on-world sealing the alliance with Dictator Halvorsen. Rear Admiral "
        "Sternfahrer's 33rd Strike Fleet (flagship Promachos) and Grand Admiral Sorensen's "
        "Protelani Third hold the line; Lenart's 7th, arriving from Procyon, delivers the "
        "coup de grâce."),
    "Insurrection in Havskrun": (2356, None,
        "Early March 2356: the Terran-backed Svenson faction rises in Havskrun and seizes "
        "Dictator Halvorsen, Terran regiments landing on the islands offshore; the 73rd "
        "'Glorious' Grenadiers dropped by Lenart retake the city — then the pacification "
        "grinds for months. A mimic-mask gas trap kills Eachan Grahame; only by October is "
        "the Dictator rescued and the Svensons captured. The alliance holds."),
    # ── Late-war re-dating (prose Claude, 2026-07-04: torch-drive-coherent) ──
    "Truce of 2354": (2354, 2355,
        "From late June 2354 the guns fall silent for Accord negotiations — until the "
        "Foundation Plague is confirmed as a Terran bioweapon (~April 2355), the casus "
        "belli: Raimond expels Ambassador Victoria and the war resumes."),
    "The Foundation Plague": (2354, 2356,
        "Seeded across the rim during the truce and first blamed on the Assault after an "
        "Asimov outbreak, the plague rots the Stahlburgh and Eisenwald harvests into famine "
        "— Stahlburgh under worldwide quarantine by late 2355. Its confirmation as a Terran "
        "bioweapon in 2355 is the casus belli that reignites the war."),
    "Operation AENEAS BURDEN": (2355, None,
        "May–June 2355: the Union answers the bioweapon with the raid on Alpha Centauri — "
        "Signe's secret super-fleet, pre-positioned during the truce. O'Riordan's 10th, "
        "Sorensen's Protelani Third and Lenart's 7th break the system while Bruce's 2nd "
        "Division takes the ground; a costly, bloody-mess success. The Eighth is cut off "
        "and written off — its odyssey home runs all summer."),
    "Battle of Asher": (2355, None,
        "The home-front counterstroke: a Terran fleet drives on Stahlburgh, and Commodore "
        "Sternfahrer's 21st Fleet baits it behind the gas giant Asher onto von Stahlgeist's "
        "5th, killing the battleship Proletarian Titan — the ambush that earns Johanna "
        "the 33rd."),
    "Henry Crowned Emperor of Hansaburgh": (2355, None,
        "Surviving an April sniper's bullet — dead almost two minutes, revived by Lukas von "
        "Saltz — Henry wins the June general election and is crowned Kaiser of Hansaburgh "
        "at Saint Christopher's."),
    "Battle of Bester": (2355, None,
        "26 December 2355, on Asimov's moon: Jurgen's team extracts the defecting General "
        "Musa — who dares defect only because Klaus's 2354 Asimov victory has already "
        "decided the war. Two Union divisions roll three leaderless Terran ones; the 33rd "
        "and 11th carrier fleets crush the Terran 8th and 9th."),
    "Battle of Procyon": (2356, None,
        "February–March 2356, on the ground: the Fomalhaut Republic Mobile Infantry carry "
        "Procyon after hard fighting — General Eachan's son Donal among the dead — with "
        "Lenart's 7th in close support before it jumps onward to Protelan. The Protelani "
        "Space Marines fare badly; the Fomalhaut infantry win it."),
    "Battle of Eiswelt": (2356, None,
        "Late February 2356 — the Pale Horse over Eiswelt: a 'small' Terran listening post "
        "in the capital system proves a fleet trap. Jurgen's 75th Grenadiers raid the post; "
        "the Navy wins at terrible cost — O'Riordan's flagship Duchess Máire Gleann "
        "O'Cruadhlaoich rammed by cloaked Terrans. Eisenbach's Wolf 359 speech comes 24 "
        "hours later: Directorate stars, not client states."),
    "Battle of Protelan": (2356, None,
        "Early March 2356: a cloaked Terran First Fleet slips toward Protelan — the "
        "Earth-like moon of the gas giant Grandpere — while Henry is on-world sealing the "
        "alliance with Dictator Halvorsen. Rear Admiral Sternfahrer's 33rd (flagship "
        "Promachos) and Sorensen's Protelani Third hold the line; Lenart's 7th, arriving "
        "from Procyon, delivers the coup de grâce."),
    "Battle of Wolf 359": (2356, None,
        "Mid-March 2356, weeks after Eiswelt: the first blow of the new doctrine. Eisenbach "
        "and von Stahlgeist gut the Terran orbital industry — the Locking yards and the "
        "Ramsen Orbital Forge — in a rare all-hands mobilization: the 4th, 5th, 14th, 15th "
        "and 72nd, elements of the 73rd, even the elite 75th. 'The Assault had gutted "
        "Wolf 359's heart.'"),
    "The Mars Campaign": (2356, None,
        "September–November 2356: PROJECT ARES infiltration → Operation SPEAR OF DESTINY → "
        "Operation DEAD ARES. Jurgen's 75th Grenadiers, inserted disguised as pirates, blow "
        "their cover but hold — Ewan Fraser kills Maxim Timon Bauer at his own dinner table "
        "— as the 7th and 8th Stahlburgh Rifles storm the domes. Titan flips, Luna falls; "
        "weeks later, the armistice."),
}

# Retitle after the update pass (title is the idempotency key)
RETITLES = {
    "Treaty of the Dual Spheres": "Accord of Dual Spheres",
    # auto-titled before the star carried its saga name
    "HD 99492 Colonized": "Argylle Tor Colonized",
    # Hansaburgh crowns a Kaiser, not an Emperor (2026-07-04 revision)
    "Henry Crowned Emperor of Hansaburgh": "Henry Crowned Kaiser of Hansaburgh",
}

# (year, end_year, title, description, event_type, star_id, nation_id)
NEW_EVENTS = [
    # ── Pre-Settlement (2093–2170) ──
    (2093, None, "Sammelvolk Arrive on Earth",
     "The Sammelvolk arrive; their Beijing base is established by 2094–96 and humanity is "
     "reduced to 'fancy pets'.", "contact", 500000, None),
    (2097, None, "McWilliams Institute Founded",
     "The MWI rises in Pennsylvania — alien-tech 'cargo cults' in service of the new order.",
     "political", 500000, None),
    (2106, 2109, "Texas Secession & U.S. Civil War",
     "Secession and civil war on Earth; survivors like Raymond Neu-Branfels are sent to the "
     "Mars gulags by 2111.", "war", 500000, None),
    # ── Settlement era ──
    (2235, None, "Sea Revolt on Lochiel",
     "Five years after settlement, Lochiel's seas rise in revolt.", "political", 43464,
     None),
    # ── Union–Directorate War (locked chronology) ──
    (2350, None, "First Battle of Asimov",
     "11–12 September: the Assault's catastrophic, unready defeat under General Meagher at "
     "Tau Ceti — two years before war is even declared.", "battle", 8087, "terran_directorate"),
    (2352, None, "VIKINGRAID at Nakdong",
     "25 November, the war's second day: Max earns 'Maximum Carnage' at Nakdong and Hannah "
     "DeBeck becomes the war's first ace.", "battle", 53879, "felgenland_union"),
    (2352, None, "Operation Glorious Dead",
     "Jurgen Wulfjaeger's suicide bunker assault kills the tyrant Xiomar Zhan-Li Esperanza; "
     "he receives the Golden Segreant Griffin from a hospital bed.", "battle", None,
     "felgenland_union"),
    (2353, None, "Orbital Battle of Foxtrot",
     "5–6 October: the Bismarck and T. Roosevelt go down over L 98-59 f, the Fourth Fleet is "
     "annihilated, and Henry is stranded on Foxtrot — the Navy's brutal wake-up.",
     "battle", 999998, "terran_directorate"),
    (2353, None, "Terran Attack on Hansaburgh",
     "27 December: the Directorate strikes the Union's industrial heartland.",
     "battle", 46945, "terran_directorate"),
    (2354, None, "Ground Battle of Foxtrot",
     "5–7 March, Project Ithaca: after five months of guerrilla war, Geordie Stewart's 73rd "
     "fights through to rescue Henry.", "battle", 999998, "felgenland_union"),
    (2354, None, "SOLAR STRIKE",
     "13 May: the Union strikes into the Sol system itself.", "battle", 500000,
     "felgenland_union"),
    (2354, None, "Second Battle of Asimov",
     "9–11 June: Klaus von Eisenbach's decisive victory secures Tau Ceti and redeems the "
     "Assault for 2350; he is made Field Marshal.", "battle", 8087, "felgenland_union"),
    (2354, None, "Truce of 2354",
     "25 June – 5 October: a three-and-a-half-month truce for Accord negotiations — broken by "
     "the Directorate.", "treaty", None, None),
    (2354, None, "Henry Crowned Emperor of Hansaburgh",
     "Surviving a July assassination attempt at the Congressional Building, Henry wins the "
     "general election and is crowned 16–20 September.", "political", 46945,
     "felgenland_union"),
    (2354, None, "Battle of Bester",
     "26 December, on Asimov's moon: Jurgen's team extracts the defecting General Musa — who "
     "dares defect only because Klaus's June victory has already decided the war.",
     "battle", 8087, "felgenland_union"),
    (2354, 2356, "The Foundation Plague",
     "A pandemic — first blamed on the Assault after an Asimov outbreak — spreads through the "
     "rim and rots the Stahlburgh and Eisenwald harvests into famine; core-world families "
     "flee to Hansaburgh.", "disaster", 48941, None),
    (2355, 2356, "Sol Blockade",
     "The war grinds on across the blockade of Sol and other fronts as the Terran Directorate "
     "fractures from within; the fighting ends in 2356.", "war", 500000, None),
    # ── Cultural Renaissance ──
    (2357, None, "Ashur Kriegswerks Founded",
     "The Campbell–MacCarthy joint venture rises on Ashur under CEO Emma Holden.",
     "political", 48941, "felgenland_union"),
    (2366, None, "Eisenbach Reforms",
     "On the Assault's centennial, Field Marshal Klaus rebuilds it into six standing "
     "divisions; the SturmRitter Mk VI 'Centennial' follows in 2367.", "political", None,
     "felgenland_union"),
    # ── Era of Exploration and after ──
    (2380, None, "Explorer Corps Founded",
     "Henry founds the Erforschungskorps with Jurgen as founding Supreme Expedition Lead.",
     "political", None, "felgenland_union"),
    (2380, 2381, "Chalawan First Contact",
     "The Corps meets the sentient natives of Chalawan at 47 Ursae Majoris.",
     "contact", 53565, "felgenland_union"),
    (2389, None, "Henry Disappears",
     "The Protector vanishes into a space-time anomaly, leaving no elected successor; the "
     "Cognatii cannot agree and the Union drifts leaderless.", "political", None,
     "felgenland_union"),
    (2390, None, "Protelan Accedes to the Union",
     "Amid the Interregnum, Protelan joins the Union — the combined bloc now holds the lion's "
     "share of Rim trade, goading the Maxims toward war.", "political", 56828,
     "felgenland_union"),
    (2391, 2397, "Second Union–Directorate War",
     "A Terran attack on the colonies forces the electors' hand; the war ends in 2397 with "
     "Ilsabeth's total nuclear bombardment of Earth.", "war", None, None),
    (2391, None, "Ilsabeth Elected Protector",
     "The Terran attack ends the Interregnum: Ilsabeth von Machthaber is elected Protector.",
     "political", None, "felgenland_union"),
    (2397, None, "Nuclear Bombardment of Earth",
     "Ilsabeth ends the Second War with the total nuclear bombardment of Earth.",
     "war", 500000, "felgenland_union"),
    # ── War update 2026-07-04 (timeline doc revision + author rulings) ──
    (2351, None, "Color Revolution on Nakdong",
     "A Terran-backed coup topples Prime Minister Javier Suno; the tyrant Xiomar Zhan-Li "
     "Esperanza seizes power and civil war erupts — pro-Union contras against Terran-proxy "
     "Revolutionaries. The Directorate's way: undermine before you invade.",
     "political", 53879, "terran_directorate"),
    (2355, None, "Battle of Protelan",
     "A cloaked Terran First Fleet slips toward Havskrun while Henry seals the Union–Protelan "
     "alliance. Admiral Johanna Sternfahrer's 33rd Strike Fleet screens behind the gas giant, "
     "the 21st Fleet as bait and Fleet Admiral Lunara von Stahlgeist's 5th for the kill — the "
     "SOSTS net trips the stealth drives. (Late 2355; exact date TBC.)",
     "battle", 56828, "felgenland_union"),
    (2355, None, "Insurrection in Havskrun",
     "Terran regiments land off Havskrun with robotic artillery, wreck the arcology and seize "
     "Dictator Halvorsen; Rear Admiral Elaine Lenart drops two battalions of the 73rd "
     "Stahlburgh 'Glorious' Grenadiers to retake the city. The Terrans surrender — the "
     "alliance holds.", "battle", 56828, "felgenland_union"),
    (2355, None, "Tau Ceti Liberated",
     "Following the Second Battle of Asimov, the Tau Ceti client state is freed. The Union "
     "takes no territory in this war — it liberates.", "political", 8087, None),
    # ── The three attacks on the Union homeworlds:
    #    Hansaburgh (Dec 2353) → Asher counterstroke (2354) → Eiswelt trap (2355)
    (2354, None, "Operation AENEAS BURDEN",
     "After the truce collapses, the Union hits back: the raid on Alpha Centauri aimed at "
     "destabilizing the Directorate's grip on its clients. Fleet Admiral O'Riordan's 10th, "
     "Sorensen's Protelani Third and Lenart's 7th break the system while General Bruce's 2nd "
     "Division takes the ground — a costly, bloody-mess success.", "battle", 71456,
     "felgenland_union"),
    (2354, None, "Battle of Asher",
     "The home-front counterstroke: a Terran fleet drives on Stahlburgh, and Commodore "
     "Sternfahrer's 21st Fleet baits it behind the gas giant Asher onto von Stahlgeist's 5th, "
     "killing the battleship Proletarian Titan. The second of three strikes at the Union's "
     "heart — and the ambush that earns Johanna the 33rd.", "battle", 48941,
     "terran_directorate"),
    (2355, None, "Battle of Eiswelt",
     "The Pale Horse over Eiswelt: a Terran listening post on the capital system's ice world "
     "proves a fleet trap; a costly Union naval win.", "battle", 48941,
     "terran_directorate"),
    (2355, None, "Battle of Procyon",
     "The Allies carry the fight to the Directorate's client state at Procyon.",
     "battle", 37173, "dorsai_republic"),
    (2355, None, "Sorai Massacre",
     "The Terran warbot Sorai massacres the Hansaburgh succession congress — Trajan, Signe "
     "Bosdottir and Adolfus killed, the traitor von Schlieffen exposed and slain. Lukas "
     "becomes King of Hesse-on-the-Saltz; Auggie Sternfahrer inherits Saltzenheim.",
     "political", 46945, "terran_directorate"),
    (2356, None, "Armistice of 2356",
     "~November 2356: Maxim Victoria's 0900 parlay aboard the USWC Union of the Felgenland; "
     "Allied fleets float over Earth as the Directorate fractures within.",
     "treaty", 500000, None),
    (2355, 2356, "The Mars Campaign",
     "PROJECT ARES infiltration → Operation SPEAR OF DESTINY → Operation DEAD ARES: Jurgen's "
     "75th Grenadiers, inserted disguised as pirates to seize the Maxim of Mars, Timon Bauer, "
     "blow their cover but hold as the 7th and 8th Stahlburgh Rifles storm the domes. Only "
     "weeks separate Mars, the fall of Luna, and the armistice.", "battle", 500000,
     "felgenland_union"),
    # ── Era structure (period markers) ──
    (2357, 2379, "Cultural Renaissance",
     "From the Accord to Raimond's death: reconstruction, prosperity, and the first peace "
     "colonies.", "era", None, None),
    (2379, 2389, "Era of Exploration",
     "Henry's tenure begins at midnight, 21 July 2379; the Explorer Corps opens the far rim "
     "until his disappearance.", "era", None, None),
    (2389, 2391, "The Interregnum",
     "No Protector; political chaos.", "era", None, None),
    (2397, 2473, "Era of Openness",
     "A multipolar peace: the Union (now including Protelan), the Fomalhaut Republic, and "
     "other powers hold a balance in which no one state can threaten the rest.",
     "era", None, None),
    (2473, 2510, "Die Blütezeit — The Golden Age",
     "The Flowering: the Union's heyday of arts, wealth, and reach.", "era", None, None),
    (2510, None, "The Splintering of the Union",
     "The long decline begins. (Canon TBD.)", "era", None, None),
]


def apply_events(con):
    # Order matters: deletes → inserts → updates → retitles, so that a FRESH
    # rebuild (where NEW_EVENTS are inserted this run) still receives the
    # EVENT_UPDATES corrections layered on top.
    for title in SUPERSEDED_TITLES:
        con.execute("DELETE FROM historical_events WHERE title = ?", (title,))

    inserted = 0
    for year, end_year, title, desc, etype, star_id, nation_id in NEW_EVENTS:
        if con.execute("SELECT 1 FROM historical_events WHERE title = ?", (title,)).fetchone():
            continue
        con.execute(
            "INSERT INTO historical_events (year, end_year, title, description, event_type, "
            "star_id, nation_id) VALUES (?,?,?,?,?,?,?)",
            (year, end_year, title, desc, etype, star_id, nation_id))
        inserted += 1

    for title, (year, end_year, desc) in EVENT_UPDATES.items():
        con.execute(
            "UPDATE historical_events SET year = COALESCE(?, year), end_year = ?, description = ? "
            "WHERE title = ?", (year, end_year, desc, title))

    for old, new in RETITLES.items():
        con.execute("UPDATE historical_events SET title = ? WHERE title = ?", (new, old))

    # Nation attribution fixes (EVENT_UPDATES doesn't touch nation_id)
    con.execute("UPDATE historical_events SET nation_id='dorsai_republic' "
                "WHERE title='Battle of Procyon'")

    # Safety net: retitle/re-seed interactions can duplicate a title — keep
    # the oldest row of any exact-title duplicate
    con.execute("DELETE FROM historical_events WHERE id NOT IN "
                "(SELECT MIN(id) FROM historical_events GROUP BY title)")

    print(f"master timeline: {len(SUPERSEDED_TITLES)} superseded, "
          f"{len(EVENT_UPDATES)} updated, {inserted} new events")


def apply_world_corrections(con):
    """Timeline revision 2026-07-04: Protelan is the Earth-like moon of the
    gas giant GRANDPERE (not Joi — and not the earlier 'Fortuna' conflation).
    Author lore 2026-07-04: Grandpere's 154 AU orbit lies ~3x beyond the
    star's safe sternfomotor jump radius (~50-60 AU for the active G8V per
    the Safe Jump Point formula) — ships jump directly in and out at
    Protelan with no in-system torch crawl, which is what made the moon
    the Rim's mercantile crossroads. protelan.txt dossier still says Joi."""
    con.execute("UPDATE fictional_exoplanets SET parent_planet='Grandpere' WHERE name='Protelan'")
    # Bester is ASIMOV'S MOON (Tau Ceti e I), not an inner planet (prose-Claude
    # catch 2026-07-04). Orbit = distance around its PARENT (moon convention).
    con.execute(
        "UPDATE fictional_exoplanets SET parent_planet='Asimov', planet_type='Rocky Moon', "
        "orbit=0.002, period=2.5, mass=0.01, radius=NULL, description='Cratered, airless moon of Asimov — Tau Ceti "
        "e I — ringed with orbital defense platforms; 10–15 million live in its warrens. "
        "Site of the December 2355 battle where General Musa defected. Named for Alfred "
        "Bester.' WHERE name='Bester' AND host_star_name='Tau Ceti'")
    con.execute("DELETE FROM exoplanets WHERE name='Bester' AND host_star_name='tau Cet'")
    # Tau Ceti designations + real-catalog orbits (tau_ceti.txt authoritative;
    # seeds-README feedback item 2). Heinlein=b, Bradbury=c, Clarke=d,
    # Asimov=e, Bester=e I, Herbert=f. Poul: designation/orbit UNRECONCILED
    # (collides with Herbert; open question for the author) — left as-is.
    con.execute(
        "UPDATE fictional_exoplanets SET orbit=0.105, period=13.665, planet_type='Super-Earth', "
        "mass=2.0, description='Sweltering jungle world — Tau Ceti b — a chaotic frontier of "
        "100–120 million.' WHERE name='Heinlein' AND host_star_name='Tau Ceti'")
    con.execute(
        "UPDATE fictional_exoplanets SET orbit=0.552, period=168.12 "
        "WHERE name='Asimov' AND host_star_name='Tau Ceti'")
    # Poul reconciled 2026-07-04: Tau Ceti g, added to tau_ceti.txt by the
    # prose side (was colliding with Herbert at 1.35 AU)
    con.execute(
        "UPDATE fictional_exoplanets SET orbit=1.7, period=915, mass=1.5, planet_type='Rocky', "
        "description='Cold rocky world just beyond Herbert — Tau Ceti g — past the habitable "
        "zone''s outer edge, its modest population sheltered in domed and valley settlements. "
        "A quiet frontier that saw little of the war; post-2361, a Cetan Confederacy enclave. "
        "Named for Poul Anderson.' WHERE name='Poul' AND host_star_name='Tau Ceti'")
    # Hawking = the SYSTEM; Hawking Prime = the capital WORLD (α Cen A c,
    # settler name New Eden). The separate 'Hawking' world row was a duplicate
    # of the capital (seeds-README feedback item 3).
    con.execute(
        "DELETE FROM fictional_exoplanets WHERE name='Hawking' AND host_star_name='Hawking'")
    con.execute(
        "UPDATE fictional_exoplanets SET orbit=1.1, planet_type='Earth-like', "
        "description='Primary habitable world of Alpha Centauri A (α Cen A c) — settler name "
        "New Eden, Directorate designation Hawking Prime. Temperate capital of the Centauran "
        "Assembly, a Directorate client state of 700–900 million.' "
        "WHERE name='Hawking Prime' AND host_star_name='Hawking'")
    # Protelan lore revision (protelan.txt updated by prose Claude 2026-07-05):
    # Joi is the JUPITER-LIKE INNER GIANT at 2.5 AU — its icy moons anchor the
    # system's mining and logistics. The festival is GRANDPERE's (Starveil),
    # not Joi's — Protelan orbits Grandpere, so it's Grandpere's phases that
    # fill its sky.
    con.execute(
        "UPDATE fictional_exoplanets SET description='Jupiter-like inner giant (Joi, "
        "\"joy\") at 2.5 AU — its icy moons anchor part of the Protelani system''s mining "
        "and logistics.' WHERE name='Joi' AND host_star_name='Protelan'")
    # Grandpere orbit: a stale pre-existing row at 2.5 AU (the OLD dossier
    # layout, before the author swapped Grandpere/Joi) blocked the 154 AU
    # insert-if-absent, leaving two giants stacked at 2.5 (user catch
    # 2026-07-05). 154 AU is the ruling — the jump-geometry wealth lore
    # depends on it. Period = Kepler for ~0.93 M☉ (~1935 yr), not the
    # dossier's "~4.25 million years" typo.
    con.execute(
        "UPDATE fictional_exoplanets SET orbit=154, period=706000, "
        "description='The vast, grandfatherly Neptune-like giant (French grand-père) at "
        "154 AU — beyond the ~56 AU sternfomotor jump periphery, so ships jump directly to "
        "its orbit, a prized shortcut to the Protelani capital. It fills the sky of its "
        "capital moon Protelan, its reflective phases driving the Starveil Festival. That "
        "jump geometry made the moon rich.' WHERE name='Grandpere' AND host_star_name='Protelan'")
    # Dossier physics revision 2026-07-05 (author moved worlds into each
    # star's TRUE habitable zone): Lalande L=0.022 → HZ 0.14–0.20, so
    # Libertad = b at 0.16 AU / ~37 d (temperate capital) and Nakdong = d
    # at 0.13 AU / ~27 d (warm inner edge, jungle world).
    con.execute(
        "UPDATE fictional_exoplanets SET orbit=0.16, period=37 "
        "WHERE name='Libertad' AND host_star_name='Lalande 21185'")
    con.execute(
        "UPDATE fictional_exoplanets SET orbit=0.13, period=27 "
        "WHERE name='Nakdong' AND host_star_name='Lalande 21185'")
    # Pentothia Prime same revision: Auricore now 0.40 AU (~113 d, in the
    # HZ ~0.36–0.68), Cryon pushed to 1.0 AU (~446 d, genuinely frozen).
    con.execute(
        "UPDATE fictional_exoplanets SET orbit=0.40, period=113 "
        "WHERE name='Auricore' AND host_star_name='Pentothia Prime'")
    con.execute(
        "UPDATE fictional_exoplanets SET orbit=1.0, period=446 "
        "WHERE name='Cryon' AND host_star_name='Pentothia Prime'")
    # Fomalhaut same revision (HZ ~3.9–5.6 for the A3V primary): Valorgraemo
    # c 4.3 AU / ~6.4 yr, Batalklendo d 4.7 / ~7.4 yr, Marrikoviro e 5.2 / ~8.6 yr.
    con.execute(
        "UPDATE exoplanets SET semi_major_axis_au=4.3, orbital_period_days=2337 "
        "WHERE name='Valorgraemo' AND host_star_name='Fomalhaut'")
    con.execute(
        "UPDATE fictional_exoplanets SET orbit=4.7, period=2702 "
        "WHERE name='Batalklendo' AND host_star_name='Fomalhaut'")
    con.execute(
        "UPDATE fictional_exoplanets SET orbit=5.2, period=3141 "
        "WHERE name='Marrikoviro' AND host_star_name='Fomalhaut'")
    # Pentothian capital is the WORLD Auricore (Auricore City), not the
    # star name (user ruling 2026-07-05).
    con.execute(
        "UPDATE nations SET capital_city='Auricore City, Auricore' WHERE id='neutral_zone'")
    # Ghost fictional rows in the REAL exoplanets table (user catch
    # 2026-07-05: system maps showed doubled/mispositioned worlds).
    # Two classes: (a) pre-swap 61 UMa junk — Joi/Protelan at 0.93 AU,
    # 'Havskrun' (that's the capital CITY, not a planet), retired
    # 'Halvorsenbard'; (b) renamed real-catalog rows that duplicate
    # authoritative fictional_exoplanets worlds at stale orbits (same
    # class as the Bester/'tau Cet' junk above). Valorgraemo (Fomalhaut)
    # and Heatherly (HD 99492) are canonical originals with no fictional
    # counterpart — they stay.
    for name, host in [
        ("Joi (gas giant)", "61 UMa"), ("Protelan (Joi I)", "61 UMa"),
        ("Havskrun", "61 UMa"), ("Halvorsenbard", "61 UMa"),
        ("Libertad", "Lalande 21185"), ("Nakdong", "Lalande 21185"),
        ("Asimov", "tau Cet"), ("Heinlein", "tau Cet"), ("Poul", "tau Cet"),
        ("Hawking Prime", "Rigil Kentaurus"), ("Foxtrot", "L 98-59"),
    ]:
        con.execute("DELETE FROM exoplanets WHERE name=? AND host_star_name=? "
                    "AND is_fictional=1", (name, host))
    con.execute(
        "UPDATE fictional_exoplanets SET description='A ~100 km orbital station in the far "
        "dark — sternfomotor docks and the Conglomerate''s great trade markets, parked out "
        "beyond the star''s jump radius where the ships arrive.' "
        "WHERE name='Stellarion Trade Nexus' AND host_star_name='Pentothia Prime'")
    con.execute(
        "UPDATE fictional_exoplanets SET description='Capital moon of the Protelan Republic, "
        "orbiting the gas giant Grandpere at 154 AU — beyond the jump periphery, so ships "
        "jump straight in and out, which made it the Rim''s mercantile crossroads and the "
        "Republic rich. A sunless world so far from its star: kept temperate (15–25°C) "
        "purely by tidal heating from Grandpere, under a thick greenhouse atmosphere. Its "
        "low-light ecology is exotic — fungal, mushroom-forest and bioluminescent rather "
        "than sun-driven. Seat of the ultra-capitalist government at Havskrun.' "
        "WHERE name='Protelan' AND parent_planet='Grandpere'")


def apply_legacy_deletions(con):
    """Canon retired by the author (2026-07-04): Lübeck Tor (star 115218) was
    old data — removed from stars, territories and ownership. Kept here so
    pre-existing databases running the chain also drop it."""
    con.execute("DELETE FROM stars WHERE id=115218")
    con.execute("DELETE FROM nation_territories WHERE star_id=115218")
    con.execute("DELETE FROM star_ownership WHERE star_id=115218")


def apply_territory_and_stars(con):
    # Settlement-date reconciliation (drives era gating and labels)
    con.execute("UPDATE stars SET discovery_year=2200 WHERE id=46945")   # Hansaburgh founded
    con.execute("UPDATE stars SET discovery_year=2230 WHERE id=43464")   # Lochiel settled
    con.execute("UPDATE stars SET discovery_year=2184 WHERE id=56828")   # Protelan Republic
    con.execute("UPDATE stars SET discovery_year=2220 WHERE id=999999")  # Brandstadt settled
    # The system-wide settler name 'Hawking' stays on the primary only
    con.execute("UPDATE stars SET fictional_name='' WHERE id=71453")     # Toliman

    # Protelan: independent 2184–2389, Union member from 2390
    con.execute("UPDATE nations SET era_start=2184, era_end=2390 WHERE id='protelani_republic'")
    con.execute(
        "INSERT OR REPLACE INTO star_ownership (star_id, nation_id, era_start, era_end) "
        "VALUES (56828, 'protelani_republic', 2184, 2389)")
    con.execute(
        "INSERT OR REPLACE INTO star_ownership (star_id, nation_id, era_start, era_end) "
        "VALUES (56828, 'felgenland_union', 2390, 3000)")
    # Remove any older protelani interval with a different start (idempotent cleanup)
    con.execute(
        "DELETE FROM star_ownership WHERE star_id=56828 AND nation_id='protelani_republic' "
        "AND era_start != 2184")

    # Tau Ceti: Directorate stronghold 2192–2354, then LIBERATED 2355.
    # Author ruling 2026-07-04: "the Union didn't take territory in the war,
    # just liberated client states" — overrides the system table's "→ Union
    # (2355)". No successor interval: the freed system shows unaffiliated.
    con.execute(
        "INSERT OR REPLACE INTO star_ownership (star_id, nation_id, era_start, era_end) "
        "VALUES (8087, 'terran_directorate', 2192, 2354)")
    con.execute(
        "DELETE FROM star_ownership WHERE star_id=8087 AND nation_id='felgenland_union'")
    print("master timeline: territory (Tau Ceti liberated 2355, Protelan 2184/2390) + star dates applied")


def main():
    con = sqlite3.connect(DB_PATH)
    try:
        apply_events(con)
        apply_territory_and_stars(con)
        apply_world_corrections(con)
        apply_legacy_deletions(con)
        con.commit()
        n = con.execute("SELECT COUNT(*) FROM historical_events").fetchone()[0]
        print(f"historical_events total: {n}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
