#!/usr/bin/env python3
"""
Wiki stub generator — Starmap → staging dir (NEVER into the wiki itself).

Flow stays Brain → Wiki → Starmap: this tool only scaffolds pages that do not
exist yet, writing DokuWiki skeletons to wiki_stubs/ for the author (or their
wiki Claude) to flesh out and copy in. It never touches existing pages, and
every stub carries {{tag>starmap_stub}} so unfinished scaffolds are queryable.

Scope (author-ruled 2026-07-04): systems → planets → provinces index.
Events/battles are prose territory — excluded.

Output:
  wiki_stubs/stars/<slug>.txt      one per named system lacking a page
  wiki_stubs/planets/<slug>.txt    one per known world lacking a page
  wiki_stubs/starmap_province_index.txt   cross-reference of all 331 provinces
"""

import os
import re
import shutil
import sqlite3
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "data" / "starmap.sqlite"
OUT = BASE / "wiki_stubs"
WIKI = Path(os.environ.get(
    "STARMAP_BRAIN_DIR",
    Path.home() / "Documents" / "Brain" / "Felgenland Saga")) / \
    "_wiki-sync" / "data_backup_github" / "pages"

HOLSTEN = (-11.088308, 6.336788, 7.956742)  # 20 LMi, pc

# system display-name → existing wiki page slug, where names diverge
STAR_PAGE_ALIASES = {
    "hawking": "alpha_centauri",
    "epsilon eridani": "episilon_eridani",   # existing page keeps the typo
}
PLANET_PAGE_ALIASES = {
    "foxtrot": "l_98-59_f",
    "asimov": "asimov",       # also exists as tau_ceti_e
    "luna": "moon",
}

STUB_NOTE = ("//⚠ **Starmap-generated stub** — the summary facts below are canon from the "
             "Starmap database; the prose sections await the Brain. Remove this notice when "
             "the page is written.//")


def slugify(name):
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("ß", "ss")
    s = re.sub(r"[^a-z0-9-]+", "_", s).strip("_")
    return re.sub(r"_+", "_", s)


def existing_slugs(namespace):
    d = WIKI / namespace
    return {p.stem for p in d.glob("*.txt")} if d.is_dir() else set()


def page_exists(slug, pages):
    """The wiki mixes hyphen and underscore slugs (l_98-59 vs tiefe_grenze_tor)."""
    return slug in pages or slug.replace("-", "_") in pages


def fmt(v, suffix="", nd=2):
    return f"{round(v, nd)}{suffix}" if v is not None else "—"


def star_stub(con, s, worlds, events, nations):
    name = s["fictional_name"] or s["proper_name"]
    real = s["proper_name"] if s["fictional_name"] else None
    dist_sol = s["dist"] * 3.2616 if s["dist"] else None
    dx = ((s["x"] - HOLSTEN[0]) ** 2 + (s["y"] - HOLSTEN[1]) ** 2 + (s["z"] - HOLSTEN[2]) ** 2) ** 0.5
    dist_holsten = dx * 3.2616

    holder = con.execute(
        "SELECT nation_id FROM star_ownership WHERE star_id=? AND era_end>=3000", (s["id"],)).fetchone()
    nation_id = holder[0] if holder else (s["nation_id"] or None)
    nation = nations.get(nation_id, "—")

    world_lines = "".join(
        f"  * [[planets:{slugify(w['name'])}|{w['name']}]]"
        f" — {w['planet_type'] or 'world'}"
        f"{' · ' + fmt(w['orbit'], ' AU') if w['orbit'] else ''}"
        f"{' · moon of ' + w['parent_planet'] if w['parent_planet'] else ''}\n"
        for w in worlds)
    event_lines = "".join(
        f"  * **{e['year']}{'–' + str(e['end_year']) if e['end_year'] else ''}** — {e['title']}\n"
        for e in events)

    return f"""====== {name} ======

{STUB_NOTE}

**{name}**{f" (official designation **{real}**)" if real else ""} is a {s['spectral_class'] or '?'}-type star of the Felgenland Rim, **{fmt(dist_sol, ' ly', 1)} from Sol** and **{fmt(dist_holsten, ' ly', 1)} from [[stars:holsten_tor|Holsten Tor]]**.

===== Overview =====
//⚠ stub — flesh out from the Brain.//

===== System =====
{world_lines or chr(47)*2 + "No known worlds in the Starmap." + chr(47)*2 + chr(10)}
===== Starmap Chronology =====
{event_lines or chr(47)*2 + "No events recorded." + chr(47)*2 + chr(10)}
===== Summary Facts =====
^ Summary Facts ^^
| Primary Name: | {name} |
| Astral Cartography Designation: | {real or name} |
| Spectral Type: | {s['spectral_class'] or '—'} |
| Apparent Magnitude: | {fmt(s['magnitude'])} |
| Distance from Sol: | {fmt(dist_sol, ' ly', 2)} |
| Distance from Holsten Tor: | {fmt(dist_holsten, ' ly', 2)} |
| Allegiance: | {nation} |
| Settled: | {s['discovery_year'] or '—'} |

{{{{tag>stars starmap_stub}}}}
"""


def planet_stub(w, system_name, system_slug):
    bits = [b for b in [
        w["planet_type"],
        f"{fmt(w['orbit'], ' AU')}" if w["orbit"] else None,
        f"period {fmt(w['period'], ' d', 1)}" if w["period"] else None,
        f"{fmt(w['mass'], ' M⊕', 2)}" if w["mass"] else None,
        f"{fmt(w['radius'], ' R⊕', 2)}" if w["radius"] else None,
    ] if b]
    return f"""====== {w['name']} ======

{STUB_NOTE}

**{w['name']}** is a {w['planet_type'] or 'world'} of the [[stars:{system_slug}|{system_name}]] system{f", a moon of {w['parent_planet']}" if w['parent_planet'] else ""}.

{w['description'] or ''}

===== Overview =====
//⚠ stub — flesh out from the Brain.//

===== Summary Facts =====
^ Summary Facts ^^
| System: | [[stars:{system_slug}|{system_name}]] |
| Type: | {w['planet_type'] or '—'} |
| Orbit: | {fmt(w['orbit'], ' AU')} |
| Orbital Period: | {fmt(w['period'], ' days', 1)} |
| Mass: | {fmt(w['mass'], ' M⊕')} |
| Radius: | {fmt(w['radius'], ' R⊕')} |
{f"| Moon of: | {w['parent_planet']} |" if w['parent_planet'] else ""}

{{{{tag>planets starmap_stub}}}}
"""


def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "stars").mkdir(parents=True)
    (OUT / "planets").mkdir()

    nations = {r["id"]: r["name"] for r in con.execute("SELECT id, name FROM nations")}
    star_pages = existing_slugs("stars")
    planet_pages = existing_slugs("planets")

    # ── Named systems ──
    systems = con.execute(
        "SELECT * FROM stars WHERE (fictional_name IS NOT NULL AND fictional_name != '') "
        "UNION SELECT s.* FROM stars s JOIN historical_events e ON e.star_id = s.id "
        "WHERE COALESCE(s.fictional_name,'') = ''").fetchall()

    made_stars = []
    star_slug_by_name = {}
    for s in systems:
        name = s["fictional_name"] or s["proper_name"]
        if not name or name.startswith("nan"):
            continue
        slug = STAR_PAGE_ALIASES.get(name.lower(), slugify(name))
        star_slug_by_name[name] = slug
        if page_exists(slug, star_pages):
            continue
        hosts = {h for h in (s["proper_name"], s["fictional_name"], str(s["id"])) if h}
        ph = ",".join("?" * len(hosts))
        worlds = con.execute(
            f"SELECT name, planet_type, orbit, period, mass, radius, parent_planet, description "
            f"FROM fictional_exoplanets WHERE host_star_name IN ({ph}) ORDER BY orbit", list(hosts)).fetchall()
        events = con.execute(
            "SELECT year, end_year, title FROM historical_events WHERE star_id=? ORDER BY year",
            (s["id"],)).fetchall()
        (OUT / "stars" / f"{slug}.txt").write_text(star_stub(con, s, worlds, events, nations))
        made_stars.append(name)

    # ── Worlds ──
    made_planets = []
    star_rows = {s["id"]: s for s in con.execute("SELECT * FROM stars WHERE fictional_name != '' OR proper_name != ''")}
    worlds = con.execute(
        "SELECT f.*, f.host_star_name AS host FROM fictional_exoplanets f ORDER BY f.host_star_name, f.orbit").fetchall()
    for w in worlds:
        slug = PLANET_PAGE_ALIASES.get(w["name"].lower(), slugify(w["name"]))
        if page_exists(slug, planet_pages):
            continue
        host_star = con.execute(
            "SELECT * FROM stars WHERE proper_name = ? OR fictional_name = ? LIMIT 1",
            (w["host"], w["host"])).fetchone()
        sys_name = (host_star["fictional_name"] or host_star["proper_name"]) if host_star else w["host"]
        sys_slug = STAR_PAGE_ALIASES.get(sys_name.lower(), slugify(sys_name))
        (OUT / "planets" / f"{slug}.txt").write_text(planet_stub(w, sys_name, sys_slug))
        made_planets.append(w["name"])

    # ── Provinces index ──
    lines = ["====== Starmap Province Index ======", "", STUB_NOTE, "",
             "//A machine-generated cross-reference of every Union province in the Starmap; "
             "regenerate rather than edit.//", ""]
    for world, star_id in [("Hansaburgh", 46945), ("Stahlburgh", 48941), ("Eisenwald", 48941),
                           ("Lochiel", 43464), ("Brandstadt", 999999)]:
        rows = con.execute(
            "SELECT province_number, name, dynasty, dynast_rank, population, area_km2 "
            "FROM provinces WHERE world=? ORDER BY province_number", (world,)).fetchall()
        total = sum(r["population"] or 0 for r in rows)
        lines.append(f"===== {world} ({len(rows)} provinces · pop {total:,}) =====")
        lines.append("^ # ^ Province ^ Dynasty ^ Rank ^ Population ^ Area (km²) ^")
        for r in rows:
            lines.append(f"| {r['province_number'] or ''} | {r['name']} | {r['dynasty'] or '—'} | "
                         f"{r['dynast_rank'] or '—'} | {r['population'] or '—'} | {r['area_km2'] or '—'} |")
        lines.append("")
    lines.append("{{tag>reference starmap_stub}}")
    (OUT / "starmap_province_index.txt").write_text("\n".join(lines))

    print(f"systems: {len(made_stars)} stubs → {', '.join(made_stars) or 'none needed'}")
    print(f"planets: {len(made_planets)} stubs")
    print(f"provinces: index written ({OUT / 'starmap_province_index.txt'})")
    con.close()


if __name__ == "__main__":
    main()
