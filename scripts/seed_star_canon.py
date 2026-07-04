#!/usr/bin/env python3
"""
Star/nation/route canon values — AUTO-GENERATED from the live DB 2026-07-04.

Historically these values (the discovery systems' names and years, nation
founding eras, trade-route era spans, fictional-world flags in the exoplanets
table) were applied directly to the live database and never captured in the
JSON sources, so a from-scratch rebuild lost them. This script replays them.

Chain position: AFTER migrate_to_sqlite.py, BEFORE migrate_timeline_events.py
(the timeline baseline derives ownership from nations.era_start + stars.discovery_year).

Idempotent: pure UPDATE/upsert by stable keys. Regenerate from a live DB with
the snippet in the repo history if canon moves again.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "starmap.sqlite")

STARS = [{'id': 3814,
  'fictional_name': 'Eta Cassiopeiae',
  'fictional_description': 'Fictional name from the Felgenland universe',
  'nation_id': '',
  'discovery_number': None,
  'discovery_year': None,
  'era_start': None,
  'era_end': None},
 {'id': 8087,
  'fictional_name': 'Tau Ceti',
  'fictional_description': 'Terran Directorate-controlled system 3.65 pc from Sol. Home to the '
                           'colony worlds Asimov (habitable), Heinlein, Poul, and Bester — all '
                           'named for classic SF authors.',
  'nation_id': 'terran_directorate',
  'discovery_number': 6,
  'discovery_year': 2192,
  'era_start': None,
  'era_end': None},
 {'id': 16496,
  'fictional_name': 'Epsilon Eridani',
  'fictional_description': 'ε Eridani (Ran) — noted as a Rimstar in Felgenland Saga lore. 3.22 pc '
                           'from Sol.',
  'nation_id': 'terran_directorate',
  'discovery_number': 4,
  'discovery_year': 2191,
  'era_start': None,
  'era_end': None},
 {'id': 37173,
  'fictional_name': '',
  'fictional_description': 'Procyon (α CMi) — client state of the Terran Directorate. 3.51 pc from '
                           'Sol.',
  'nation_id': 'terran_directorate',
  'discovery_number': 5,
  'discovery_year': 2191,
  'era_start': None,
  'era_end': None},
 {'id': 43464,
  'fictional_name': 'Griefen Tor',
  'fictional_description': 'Greifen Tor is the gateway to Felgenland Union rimward space, a '
                           'bustling trade hub orbiting the system known to Earth astronomers as '
                           '55 Cancri.',
  'nation_id': 'felgenland_union',
  'discovery_number': 12,
  'discovery_year': 2233,
  'era_start': None,
  'era_end': None},
 {'id': 46945,
  'fictional_name': 'Brandenburg Tor',
  'fictional_description': 'Brandenburg Tor (11 LMi) — Union Industrial Heartland System 11.37 pc '
                           'from Sol. Major manufacturing and logistics hub; capital world: '
                           'Hansaburgh.',
  'nation_id': 'felgenland_union',
  'discovery_number': 7,
  'discovery_year': 2199,
  'era_start': None,
  'era_end': None},
 {'id': 47977,
  'fictional_name': 'Helvetia Tor',
  'fictional_description': 'G2V solar twin designated Helvetia Tor at the 2371 chartering of Neu '
                           'Helvetica — a Cultural Renaissance peace colony in the Leo Minor home '
                           'cluster, 17.3 light-years from Holsten Tor.',
  'nation_id': '',
  'discovery_number': None,
  'discovery_year': 2371,
  'era_start': None,
  'era_end': None},
 {'id': 48941,
  'fictional_name': 'Holsten Tor',
  'fictional_description': 'Holsten Tor (20 LMi) — Union Core Capital System 15.05 pc from Sol. '
                           'Capital world: Stahlburgh. Home of the Felgenland Union government.',
  'nation_id': 'felgenland_union',
  'discovery_number': 9,
  'discovery_year': 2215,
  'era_start': None,
  'era_end': None},
 {'id': 49558,
  'fictional_name': 'Pathfinder Tor',
  'fictional_description': "The Explorer Corps' first great prize: a long-lived K0 dwarf with a "
                           'near-Earth world in its habitable zone, opened for settlement by the '
                           'Pathfinder Teams and named in their honor.',
  'nation_id': '',
  'discovery_number': None,
  'discovery_year': 2380,
  'era_start': None,
  'era_end': None},
 {'id': 49767,
  'fictional_name': 'Pentothia Prime',
  'fictional_description': '',
  'nation_id': 'neutral_zone',
  'discovery_number': None,
  'discovery_year': None,
  'era_start': None,
  'era_end': None},
 {'id': 53879,
  'fictional_name': 'Lalande 21185',
  'fictional_description': 'Contested border system 2.55 pc from Sol. Libertad (b) was the first '
                           'human colony outside Sol; Nakdong (c) became a bitter war-zone — site '
                           "of Max's long patrol.",
  'nation_id': 'terran_directorate',
  'discovery_number': 1,
  'discovery_year': 2170,
  'era_start': None,
  'era_end': None},
 {'id': 55681,
  'fictional_name': 'Argylle Tor',
  'fictional_description': "K0V orange dwarf named in 2356 for Alasdair Campbell's province of "
                           'Argyll-Inveraray-on-the-Greenwich — a frontier gateway star and home '
                           'of the Heatherly colony.',
  'nation_id': 'felgenland_union',
  'discovery_number': 13,
  'discovery_year': 2356,
  'era_start': None,
  'era_end': None},
 {'id': 56828,
  'fictional_name': 'Protelan',
  'fictional_description': 'Protelan system (61 UMa) 9.61 pc from Sol — core Union world. Capital: '
                           'Protelan, a moon of the gas giant Grandpere. Seat of the Protelani '
                           'Republic.',
  'nation_id': 'protelani_republic',
  'discovery_number': 8,
  'discovery_year': 2205,
  'era_start': None,
  'era_end': None},
 {'id': 70666,
  'fictional_name': '',
  'fictional_description': '',
  'nation_id': '',
  'discovery_number': None,
  'discovery_year': 2184,
  'era_start': None,
  'era_end': None},
 {'id': 71453,
  'fictional_name': 'Hawking',
  'fictional_description': 'Alpha Centauri B — secondary star of the Hawking system. 1.32 pc from '
                           'Sol.',
  'nation_id': '',
  'discovery_number': None,
  'discovery_year': 2184,
  'era_start': None,
  'era_end': None},
 {'id': 71456,
  'fictional_name': 'Hawking',
  'fictional_description': 'Alpha Centauri A — the settler name for the whole Alpha Centauri '
                           'system is Hawking. The Terran Directorate designates its primary '
                           'habitable world Hawking Prime (α Cen A c). 1.32 pc from Sol.',
  'nation_id': '',
  'discovery_number': 2,
  'discovery_year': 2184,
  'era_start': None,
  'era_end': None},
 {'id': 98924,
  'fictional_name': 'Delta Pavonis',
  'fictional_description': 'Fictional name from the Felgenland universe',
  'nation_id': '',
  'discovery_number': None,
  'discovery_year': None,
  'era_start': None,
  'era_end': None},
 {'id': 101479,
  'fictional_name': 'HD 10180',
  'fictional_description': 'Fictional name from the Felgenland universe',
  'nation_id': '',
  'discovery_number': None,
  'discovery_year': None,
  'era_start': None,
  'era_end': None},
 {'id': 113008,
  'fictional_name': '',
  'fictional_description': 'Independent republic capital system (α PsA) 7.7 pc from Sol. Capital '
                           'world: Valorgraemo (α PsA c), seat of the Fomalhaut Republic.',
  'nation_id': 'dorsai_republic',
  'discovery_number': 10,
  'discovery_year': 2220,
  'era_start': None,
  'era_end': None},
 {'id': 115218,
  'fictional_name': 'Lübeck Tor',
  'fictional_description': 'Third gateway system of the Felgenland Union, established as a '
                           'resupply and cultural exchange depot along the Holsten corridor. Known '
                           'for its orbital ring market and the annual Lübecker Handelstage trade '
                           'festival.',
  'nation_id': None,
  'discovery_number': None,
  'discovery_year': None,
  'era_start': 2170,
  'era_end': 3000},
 {'id': 118720,
  'fictional_name': '',
  'fictional_description': 'Wolf 359 — site of a notable military operation in the Felgenland '
                           'Saga. 2.39 pc from Sol.',
  'nation_id': '',
  'discovery_number': 3,
  'discovery_year': 2188,
  'era_start': None,
  'era_end': None},
 {'id': 500000,
  'fictional_name': '',
  'fictional_description': '',
  'nation_id': '',
  'discovery_number': 0,
  'discovery_year': None,
  'era_start': None,
  'era_end': None},
 {'id': 999997,
  'fictional_name': 'Shattensonne',
  'fictional_description': 'The shadow-sun: 20 Leonis Minoris B, the M7V red dwarf companion of '
                           'Holstensonne. A symbol of companionship in Union lore.',
  'nation_id': None,
  'discovery_number': None,
  'discovery_year': None,
  'era_start': None,
  'era_end': None},
 {'id': 999998,
  'fictional_name': 'L 98-59',
  'fictional_description': 'Terran-controlled frontier system (M3V) 10.6 pc from Sol. Site of the '
                           'loss of ISN Bismarck and T. Roosevelt. Home to Foxtrot (L 98-59 f), '
                           'the outermost known world.',
  'nation_id': 'terran_directorate',
  'discovery_number': 11,
  'discovery_year': 2225,
  'era_start': 2170,
  'era_end': 3000},
 {'id': 999999,
  'fictional_name': 'Tiefe-Grenze Tor',
  'fictional_description': 'Tiefe-Grenze Tor (HD 86729) — Union frontier colony system 16.86 pc '
                           'from Sol. Colony world Brandstadt (c) is transitioning from outpost to '
                           'full colonial world.',
  'nation_id': None,
  'discovery_number': None,
  'discovery_year': None,
  'era_start': 2170,
  'era_end': 3000}]

NATIONS = [{'id': 'dorsai_republic', 'era_start': 2210, 'era_end': 3000},
 {'id': 'felgenland_union', 'era_start': 2267, 'era_end': 3000},
 {'id': 'lalande_republic', 'era_start': 2353, 'era_end': 3000},
 {'id': 'neutral_zone', 'era_start': 2170, 'era_end': 3000},
 {'id': 'protelani_republic', 'era_start': 2199, 'era_end': 3000},
 {'id': 'terran_directorate', 'era_start': 2091, 'era_end': 3000}]

TRADE_ROUTES = [{'id': 'centauri_sirius_trade_route_6', 'era_start': 2091, 'era_end': 3000},
 {'id': 'dorsai_brandenburg_trade_route_18', 'era_start': 2210, 'era_end': 3000},
 {'id': 'dorsai_felgenland_military_alliance_route_14', 'era_start': 2210, 'era_end': 3000},
 {'id': 'dorsai_griefen_trade_route_19', 'era_start': 2210, 'era_end': 3000},
 {'id': 'dorsai_lalande_colony_trade_route_17', 'era_start': 2210, 'era_end': 3000},
 {'id': 'dorsai_protelan_defense_corridor_15', 'era_start': 2210, 'era_end': 3000},
 {'id': 'holsten_brandenburg_route_8', 'era_start': 2267, 'era_end': 3000},
 {'id': 'pentothian_dorsai_trade_22', 'era_start': 2170, 'era_end': 3000},
 {'id': 'pentothian_felgenland_trade_21', 'era_start': 2170, 'era_end': 3000},
 {'id': 'pentothian_protelan_trade_23', 'era_start': 2170, 'era_end': 3000},
 {'id': 'pentothian_terran_neutral_trade_20', 'era_start': 2170, 'era_end': 3000},
 {'id': 'protelan_brandenburg_express_11', 'era_start': 2199, 'era_end': 3000},
 {'id': 'protelan_holsten_commercial_corridor_10', 'era_start': 2199, 'era_end': 3000},
 {'id': 'protelan_trade_corridor_13', 'era_start': 2199, 'era_end': 3000},
 {'id': 'sirius_proxima_trade_link_5', 'era_start': 2091, 'era_end': 3000},
 {'id': 'tiefe_grenze_brandenburg_frontier_route_25', 'era_start': 2267, 'era_end': 3000},
 {'id': 'tiefe_grenze_griefen_frontier_route_26', 'era_start': 2267, 'era_end': 3000},
 {'id': 'tiefe_grenze_holsten_frontier_route_24', 'era_start': 2267, 'era_end': 3000}]

FICTIONAL_EXOPLANETS = [{'name': 'Asimov',
  'host_star_name': 'tau Cet',
  'semi_major_axis_au': 0.29,
  'orbital_period_days': 64.0,
  'planet_radius_earth': 1.0,
  'planet_mass_earth': 1.1,
  'equilibrium_temp_k': 470.0,
  'planet_type': 'Rocky',
  'potentially_habitable': 0,
  'star_id': 8087},
 {'name': 'Bester',
  'host_star_name': 'tau Cet',
  'semi_major_axis_au': 1.7,
  'orbital_period_days': 817.0,
  'planet_radius_earth': 2.1,
  'planet_mass_earth': 4.5,
  'equilibrium_temp_k': 192.0,
  'planet_type': 'Rocky',
  'potentially_habitable': 0,
  'star_id': 8087},
 {'name': 'Foxtrot',
  'host_star_name': 'L 98-59',
  'semi_major_axis_au': 0.105,
  'orbital_period_days': 13.8,
  'planet_radius_earth': 1.5,
  'planet_mass_earth': 2.3,
  'equilibrium_temp_k': 220.0,
  'planet_type': 'Rocky',
  'potentially_habitable': 1,
  'star_id': 999998},
 {'name': 'Halvorsenbard',
  'host_star_name': '61 UMa',
  'semi_major_axis_au': 2.4,
  'orbital_period_days': 1364.0,
  'planet_radius_earth': 2.8,
  'planet_mass_earth': 7.2,
  'equilibrium_temp_k': 161.0,
  'planet_type': 'Rocky',
  'potentially_habitable': 0,
  'star_id': 56828},
 {'name': 'Havskrun',
  'host_star_name': '61 UMa',
  'semi_major_axis_au': 1.48,
  'orbital_period_days': 658.0,
  'planet_radius_earth': 1.3,
  'planet_mass_earth': 2.1,
  'equilibrium_temp_k': 205.0,
  'planet_type': 'Rocky',
  'potentially_habitable': 0,
  'star_id': 56828},
 {'name': 'Hawking Prime',
  'host_star_name': 'Rigil Kentaurus',
  'semi_major_axis_au': 1.25,
  'orbital_period_days': 510.0,
  'planet_radius_earth': 1.35,
  'planet_mass_earth': 1.9,
  'equilibrium_temp_k': 267.0,
  'planet_type': 'Rocky',
  'potentially_habitable': 1,
  'star_id': 71456},
 {'name': 'Heatherly',
  'host_star_name': 'HD 99492',
  'semi_major_axis_au': 0.88,
  'orbital_period_days': 298.0,
  'planet_radius_earth': 1.3,
  'planet_mass_earth': 1.9,
  'equilibrium_temp_k': 255.0,
  'planet_type': 'Rocky',
  'potentially_habitable': 1,
  'star_id': 55681},
 {'name': 'Heinlein',
  'host_star_name': 'tau Cet',
  'semi_major_axis_au': 0.58,
  'orbital_period_days': 164.0,
  'planet_radius_earth': 1.3,
  'planet_mass_earth': 1.9,
  'equilibrium_temp_k': 330.0,
  'planet_type': 'Rocky',
  'potentially_habitable': 0,
  'star_id': 8087},
 {'name': 'Joi (gas giant)',
  'host_star_name': '61 UMa',
  'semi_major_axis_au': 0.93,
  'orbital_period_days': 328.0,
  'planet_radius_earth': 7.8,
  'planet_mass_earth': 40.0,
  'equilibrium_temp_k': 258.0,
  'planet_type': 'Gas Giant',
  'potentially_habitable': 0,
  'star_id': 56828},
 {'name': 'Libertad',
  'host_star_name': 'Lalande 21185',
  'semi_major_axis_au': 0.079,
  'orbital_period_days': 7.2,
  'planet_radius_earth': 0.92,
  'planet_mass_earth': 0.8,
  'equilibrium_temp_k': 380.0,
  'planet_type': 'Rocky',
  'potentially_habitable': 0,
  'star_id': 53879},
 {'name': 'Nakdong',
  'host_star_name': 'Lalande 21185',
  'semi_major_axis_au': 0.13,
  'orbital_period_days': 20.9,
  'planet_radius_earth': 1.15,
  'planet_mass_earth': 1.3,
  'equilibrium_temp_k': 220.0,
  'planet_type': 'Rocky',
  'potentially_habitable': 1,
  'star_id': 53879},
 {'name': 'Poul',
  'host_star_name': 'tau Cet',
  'semi_major_axis_au': 0.92,
  'orbital_period_days': 325.0,
  'planet_radius_earth': 1.2,
  'planet_mass_earth': 1.6,
  'equilibrium_temp_k': 261.0,
  'planet_type': 'Rocky',
  'potentially_habitable': 1,
  'star_id': 8087},
 {'name': 'Protelan (Joi I)',
  'host_star_name': '61 UMa',
  'semi_major_axis_au': 0.93,
  'orbital_period_days': 328.0,
  'planet_radius_earth': 0.97,
  'planet_mass_earth': 0.9,
  'equilibrium_temp_k': 263.0,
  'planet_type': 'Rocky',
  'potentially_habitable': 1,
  'star_id': 56828},
 {'name': 'Valorgraemo',
  'host_star_name': 'Fomalhaut',
  'semi_major_axis_au': 4.1,
  'orbital_period_days': 2715.0,
  'planet_radius_earth': 1.5,
  'planet_mass_earth': 2.8,
  'equilibrium_temp_k': 280.0,
  'planet_type': 'Rocky',
  'potentially_habitable': 1,
  'star_id': 113008}]


def main():
    con = sqlite3.connect(DB_PATH)
    try:
        for s in STARS:
            con.execute(
                "UPDATE stars SET fictional_name=?, fictional_description=?, nation_id=?, "
                "discovery_number=?, discovery_year=?, era_start=?, era_end=? WHERE id=?",
                (s["fictional_name"], s["fictional_description"], s["nation_id"],
                 s["discovery_number"], s["discovery_year"], s["era_start"], s["era_end"], s["id"]))
        for n in NATIONS:
            con.execute("UPDATE nations SET era_start=?, era_end=? WHERE id=?",
                        (n["era_start"], n["era_end"], n["id"]))
        for r in TRADE_ROUTES:
            con.execute("UPDATE trade_routes SET era_start=?, era_end=? WHERE id=?",
                        (r["era_start"], r["era_end"], r["id"]))
        for p in FICTIONAL_EXOPLANETS:
            cur = con.execute(
                "UPDATE exoplanets SET is_fictional=1, semi_major_axis_au=?, orbital_period_days=?, "
                "planet_radius_earth=?, planet_mass_earth=?, equilibrium_temp_k=?, planet_type=?, "
                "potentially_habitable=?, star_id=? WHERE name=? AND host_star_name=?",
                (p["semi_major_axis_au"], p["orbital_period_days"], p["planet_radius_earth"],
                 p["planet_mass_earth"], p["equilibrium_temp_k"], p["planet_type"],
                 p["potentially_habitable"], p["star_id"], p["name"], p["host_star_name"]))
            if cur.rowcount == 0:
                con.execute(
                    "INSERT INTO exoplanets (name, host_star_name, is_fictional, semi_major_axis_au, "
                    "orbital_period_days, planet_radius_earth, planet_mass_earth, equilibrium_temp_k, "
                    "planet_type, potentially_habitable, star_id) VALUES (?,?,1,?,?,?,?,?,?,?,?)",
                    (p["name"], p["host_star_name"], p["semi_major_axis_au"], p["orbital_period_days"],
                     p["planet_radius_earth"], p["planet_mass_earth"], p["equilibrium_temp_k"],
                     p["planet_type"], p["potentially_habitable"], p["star_id"]))
        con.commit()
        print(f"star canon: {len(STARS)} stars, {len(NATIONS)} nations, "
              f"{len(TRADE_ROUTES)} routes, {len(FICTIONAL_EXOPLANETS)} fictional exoplanets applied")
    finally:
        con.close()


if __name__ == "__main__":
    main()
