#!/usr/bin/env python3
"""
Canon drift report: compares the author's Brain notes against the starmap DB
and repo snapshots, and prints what has drifted. READ-ONLY — it never writes;
canon decisions belong to the author. Exit code 1 when drift is found (CI-able).

Usage:
    python scripts/sync_from_brain.py            # full report
    STARMAP_BRAIN_DIR=/path python scripts/sync_from_brain.py

Checks:
  1. Province CSVs — Brain copy vs repo snapshot (data/provinces/) vs DB counts
  2. Brandstadt province table in 'Union Provinces.md' vs DB
  3. 'Felgenland Saga Populations.md' figures vs nations.population
  4. DokuWiki star dossiers (stars/*.txt) vs starmap systems + their planets
"""

import hashlib
import os
import re
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "data" / "starmap.sqlite"
BRAIN = Path(os.environ.get(
    "STARMAP_BRAIN_DIR",
    Path.home() / "Documents" / "Brain" / "Felgenland Saga"))

PROVINCE_CSVS = {  # world → (filename, expected DB world rows come from DB itself)
    "Stahlburgh": "stahlburgh_provinces_with_ranks.csv",
    "Eisenwald": "Eisenwald_Provinces_Updated.csv",
    "Hansaburgh": "hansaburgh_provinces_ranks_refactored.csv",
    "Lochiel": "Lochiel_Provinces_Updated.csv",
}

POPULATION_NATIONS = {
    "Dorsai Republic": "dorsai_republic",
    "Protelani Republic": "protelani_republic",
    "Felgenland Union": "felgenland_union",
    "Terran Directorate": "terran_directorate",
}
# Documented deltas that are NOT drift (author-ruled):
#   Union: Populations.md lists the 630M core worlds; the DB adds ~30M Brandstadt.
UNION_BRANDSTADT_DELTA_M = 30

ok, info, drift = [], [], []


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_province_csvs(con):
    for world, fname in PROVINCE_CSVS.items():
        brain_f = BRAIN / fname
        snap_f = BASE / "data" / "provinces" / fname
        if not brain_f.exists():
            drift.append(f"provinces/{world}: Brain CSV missing ({brain_f.name})")
            continue
        if not snap_f.exists():
            drift.append(f"provinces/{world}: repo snapshot missing — copy from Brain and run import_provinces.py")
            continue
        if _sha(brain_f) != _sha(snap_f):
            drift.append(f"provinces/{world}: Brain CSV differs from repo snapshot — re-copy + re-run import_provinces.py")
            continue
        n_csv = sum(1 for line in brain_f.read_text(encoding="utf-8-sig").splitlines()[1:] if line.strip())
        n_db = con.execute("SELECT COUNT(*) FROM provinces WHERE world=?", (world,)).fetchone()[0]
        if n_csv != n_db:
            drift.append(f"provinces/{world}: CSV has {n_csv} rows but DB has {n_db} — re-run import_provinces.py")
        else:
            ok.append(f"provinces/{world}: {n_db} rows, snapshot current")


def check_brandstadt(con):
    src = BRAIN / "Union Provinces.md"
    if not src.exists():
        drift.append("Brandstadt: 'Union Provinces.md' not found in Brain")
        return
    rows = re.findall(
        r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(Northridge|Southplains)\s*\|[^|]*\|\s*([\d,]+)\s*\|\s*[\d,]+\s*\|\s*([^|]+?)\s*\|",
        src.read_text(), re.M)
    if not rows:
        drift.append("Brandstadt: could not parse the province table in 'Union Provinces.md'")
        return
    brain = {name: (int(pop.replace(",", "")), dyn) for _, name, _, pop, dyn in rows}
    db = {r[0]: (r[1], r[2]) for r in con.execute(
        "SELECT name, population, dynasty FROM provinces WHERE world='Brandstadt'")}
    missing = sorted(set(brain) - set(db))
    extra = sorted(set(db) - set(brain))
    changed = sorted(n for n in set(brain) & set(db)
                     if brain[n] != db[n])
    if missing or extra or changed:
        for n in missing:
            drift.append(f"Brandstadt: '{n}' in Brain but not in DB")
        for n in extra:
            drift.append(f"Brandstadt: '{n}' in DB but not in Brain")
        for n in changed:
            drift.append(f"Brandstadt: '{n}' pop/dynasty differ (Brain {brain[n]} vs DB {db[n]})")
    else:
        ok.append(f"Brandstadt: {len(brain)} provinces match")


def _millions(text):
    """'~660 million (…)' / '52,000 million' / '52 billion' → float millions."""
    if not text:
        return None
    m = re.search(r"([\d,.]+)\s*(million|billion)", text.replace("~", ""))
    if not m:
        return None
    val = float(m.group(1).replace(",", ""))
    return val * (1000 if m.group(2) == "billion" else 1)


def check_populations(con):
    src = BRAIN / "Felgenland Saga Populations.md"
    if not src.exists():
        drift.append("populations: 'Felgenland Saga Populations.md' not found")
        return
    text = src.read_text()
    for label, nid in POPULATION_NATIONS.items():
        m = re.search(rf"^{re.escape(label)}:\s*(.+)$", text, re.M)
        if not m:
            info.append(f"populations: no line for '{label}' in Brain file")
            continue
        brain_m = _millions(m.group(1))
        row = con.execute("SELECT population FROM nations WHERE id=?", (nid,)).fetchone()
        db_m = _millions(row[0] if row else None)
        if brain_m is None or db_m is None:
            info.append(f"populations/{nid}: unparseable (Brain {m.group(1)!r} vs DB {row[0] if row else None!r})")
        elif nid == "felgenland_union" and abs(db_m - (brain_m + UNION_BRANDSTADT_DELTA_M)) < 1:
            ok.append(f"populations/{nid}: {db_m:.0f}M = Brain {brain_m:.0f}M core + {UNION_BRANDSTADT_DELTA_M}M Brandstadt")
        elif abs(brain_m - db_m) < 1:
            ok.append(f"populations/{nid}: {db_m:.0f}M matches")
        else:
            drift.append(f"populations/{nid}: Brain says {brain_m:.0f}M, DB says {db_m:.0f}M")


def _strip_note(name):
    """'Asimov (Tau Ceti e, System Capital)' → 'Asimov'."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()


# Astro field labels that appear bold in some dossier layouts — never planets
_FIELD_LABELS = {
    "mass", "type", "radius", "notes", "status", "description", "population",
    "narrative", "climate", "geography", "atmosphere", "age", "luminosity",
    "metallicity", "temperature", "feasibility", "feasibility notes",
    "semi-major axis", "orbital period", "surface gravity", "source",
    "also known as", "simbad identifier", "rotation period", "proper motion",
    "radial velocity", "summary facts", "symbol", "designation", "moon",
}


def _dossier_planets(text):
    """Planet names from a DokuWiki star dossier. Conservative by design:
    [[planets:…]] links, numbered bold list entries, and bold entries whose
    parenthetical looks like a planet designation (e.g. '11 LMi b')."""
    names = set()
    for label in re.findall(r"\[\[planets:[^|\]]+\|([^\]]+)\]\]", text):
        names.add(_strip_note(label))
    # numbered system lists: '5. **Lochiel** – …'
    for m in re.finditer(r"^\s*\d+\.\s+\*\*([^*]+?)\*\*", text, re.M):
        names.add(_strip_note(m.group(1)))
    # bold with letter designation: '**Hansaburgh (11 LMi b)**:'
    for m in re.finditer(r"\*\*([A-ZÄÖÜ][\w'’ -]{2,30}?)\s*\(([^)]*)\)\*\*\s*[:–-]", text):
        if re.search(r"\b[b-h]\b", m.group(2)):
            names.add(m.group(1).strip())
    return {n for n in names
            if n and n.lower() not in _FIELD_LABELS
            and not re.fullmatch(r"[a-h]", n)                # bare letters
            and not re.match(r"(?i)(tau ceti|lalande|l ?98|55 canc|proxima)", n)}  # raw designations


def check_star_dossiers(con):
    stars_dir = BRAIN / "DokuWiki-export-ROOT-20260625-004312" / "stars"
    if not stars_dir.is_dir():
        info.append("dossiers: DokuWiki export dir not found — skipping")
        return

    db_stars = con.execute(
        "SELECT id, proper_name, fictional_name, name FROM "
        "(SELECT id, proper_name, fictional_name, proper_name AS name FROM stars "
        " WHERE fictional_name IS NOT NULL AND fictional_name != '')").fetchall()
    by_name = {}
    for sid, proper, fictional, _ in db_stars:
        for key in (proper, fictional):
            if key:
                by_name[key.lower()] = (sid, fictional)

    # Every fictional world name in the DB, any host — dossiers cross-link
    # other systems' worlds (travel tables), which are not "missing" here.
    all_db_worlds = {r[0] for r in con.execute(
        "SELECT name FROM exoplanets WHERE is_fictional=1 "
        "UNION SELECT name FROM fictional_exoplanets")}

    # Known aliases: dossier title → starmap name
    aliases = {
        "alpha centauri": "hawking", "episilon eridani": "epsilon eridani",
        "lalande 21185": "lalande 21185", "wolf 359": "wolf 359",
        "sol": "sol", "tau ceti": "tau ceti", "l 98-59": "l 98-59",
    }

    for path in sorted(stars_dir.glob("*.txt")):
        if path.stem in ("c_template",):
            continue
        text = path.read_text()
        m = re.search(r"^======\s*(.+?)\s*======", text, re.M)
        title = (m.group(1) if m else path.stem.replace("_", " ")).strip()
        # 'GJ 380 (Pentothia Prime)' → try the saga name first, then the base
        paren = re.search(r"^(.*?)\s*\((.+?)\)\s*$", title)
        candidates = ([paren.group(2), paren.group(1)] if paren else [title])
        candidates = [aliases.get(c.lower(), c.lower()) for c in candidates]

        hit = next((by_name[c] for c in candidates if c in by_name), None)
        key = candidates[0]
        if not hit:
            # try direct star-name match against ALL stars (incl. non-fictional)
            for c in candidates:
                row = con.execute(
                    "SELECT id, COALESCE(fictional_name, proper_name) FROM stars "
                    "WHERE LOWER(COALESCE(fictional_name,'')) = ? OR LOWER(COALESCE(proper_name,'')) = ? LIMIT 1",
                    (c, c)).fetchone()
                if row:
                    hit = (row[0], row[1])
                    break
        if not hit:
            drift.append(f"dossiers: '{title}' ({path.name}) has no matching starmap system")
            continue

        sid, sysname = hit
        star = con.execute(
            "SELECT proper_name, fictional_name FROM stars WHERE id=?", (sid,)).fetchone()
        hosts = {h for h in (star[0], star[1], str(sid)) if h}
        db_planets = set()
        for h in hosts:
            db_planets.update(r[0] for r in con.execute(
                "SELECT name FROM exoplanets WHERE is_fictional=1 AND host_star_name=?", (h,)))
            db_planets.update(r[0] for r in con.execute(
                "SELECT name FROM fictional_exoplanets WHERE host_star_name=?", (h,)))

        wiki_planets = _dossier_planets(text)
        missing = sorted(p for p in wiki_planets
                         if p not in db_planets and p not in all_db_worlds)
        if missing:
            drift.append(f"dossiers/{title}: worlds in wiki but not in starmap: {', '.join(missing)}")
        else:
            ok.append(f"dossiers/{title}: {len(wiki_planets)} wiki worlds all present ({len(db_planets)} in DB)")


def main():
    if not BRAIN.is_dir():
        print(f"Brain directory not found: {BRAIN}")
        sys.exit(2)
    con = sqlite3.connect(DB_PATH)
    try:
        check_province_csvs(con)
        check_brandstadt(con)
        check_populations(con)
        check_star_dossiers(con)
    finally:
        con.close()

    print(f"Canon drift report — Brain: {BRAIN}\n")
    for line in ok:
        print(f"  OK    {line}")
    for line in info:
        print(f"  INFO  {line}")
    for line in drift:
        print(f"  DRIFT {line}")
    print(f"\n{len(ok)} ok · {len(info)} info · {len(drift)} drift")
    sys.exit(1 if drift else 0)


if __name__ == "__main__":
    main()
