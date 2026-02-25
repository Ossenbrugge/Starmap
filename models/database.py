"""
Database - SQLite backend for Starmap.

Run scripts/migrate_to_sqlite.py once to populate data/starmap.sqlite
from the legacy JSON files.
"""

import os
import sqlite3
import threading
from typing import Any, Dict, List, Optional

_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "starmap.sqlite")


def _row_factory(cursor, row):
    """Return rows as plain dicts."""
    cols = [d[0] for d in cursor.description]
    return dict(zip(cols, row))


class Database:
    """
    SQLite-backed database.  All public methods preserve the same
    signatures as the legacy in-memory version so the repository layer
    needs no changes.
    """

    def __init__(self, data_dir: str = "data"):
        # Always use the path anchored to this file so the app can be started from any CWD.
        db_path = _DB_PATH
        if not os.path.exists(db_path):
            raise FileNotFoundError(
                f"SQLite database not found at '{db_path}'. "
                "Run 'python scripts/migrate_to_sqlite.py' first."
            )
        self._con = sqlite3.connect(db_path, check_same_thread=False)
        self._lock = threading.Lock()
        self._con.row_factory = _row_factory
        self._con.execute("PRAGMA journal_mode = WAL")
        self._con.execute("PRAGMA foreign_keys = ON")
        print(f"Database opened: {db_path}")

    def _q(self, sql: str, params: tuple = ()) -> List[Dict]:
        with self._lock:
            return self._con.execute(sql, params).fetchall()

    def _one(self, sql: str, params: tuple = ()) -> Optional[Dict]:
        with self._lock:
            return self._con.execute(sql, params).fetchone()

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    @staticmethod
    def _clean_star_name(raw: str) -> str:
        """Return empty string if name is nan/null garbage."""
        if not raw:
            return ""
        s = str(raw).strip()
        if s.lower() in ("nan", "nan; nan", "nan;nan", "none", "null", ""):
            return ""
        return s

    def _star_to_dict(self, row: Dict) -> Dict:
        """Normalise a DB row into the client-facing star shape."""
        if row is None:
            return {}
        proper   = self._clean_star_name(row.get("proper_name"))
        fictional = self._clean_star_name(row.get("fictional_name"))
        # Fallback name: catalog ID (HIP/HD) or generic
        if not proper and not fictional:
            hip = row.get("hip")
            hd  = row.get("hd")
            dn  = row.get("discovery_number")
            if dn is not None:
                fallback = f"Discovery-{int(dn):04d}"
            elif hip:
                fallback = f"HIP {int(hip)}"
            elif hd:
                fallback = f"HD {int(hd)}"
            else:
                fallback = f"Star {row.get('id')}"
        else:
            fallback = fictional or proper
        return {
            "id": row.get("id"),
            "_id": row.get("id"),
            "name": proper or fictional or fallback,
            "proper_name": proper,
            "fictional_name": fictional,
            "fictional_description": row.get("fictional_description") or "",
            "x": row.get("x") or 0.0,
            "y": row.get("y") or 0.0,
            "z": row.get("z") or 0.0,
            "dist": row.get("dist"),
            "ra": row.get("ra"),
            "dec": row.get("dec"),
            "magnitude": row.get("magnitude"),
            "mag": row.get("magnitude"),
            "absolute_magnitude": row.get("absolute_magnitude"),
            "spectral_class": row.get("spectral_class") or "",
            "spect": row.get("spectral_class") or "",
            "color_index": row.get("color_index"),
            "luminosity": row.get("luminosity"),
            "constellation": row.get("constellation") or "",
            "con": row.get("constellation") or "",
            "hip": row.get("hip"),
            "hd": row.get("hd"),
            "nation_id": row.get("nation_id") or "",
            "is_fictional": bool(row.get("is_fictional")),
            "era_start": row.get("era_start"),
            "era_end": row.get("era_end"),
            "discovery_number": row.get("discovery_number"),
            "discovery_year": row.get("discovery_year"),
        }

    # ── Stars ─────────────────────────────────────────────────────────────────

    def get_stars(
        self,
        limit: int = 1000,
        mag_limit: float = 8.0,
        spectral_type: str = "",
    ) -> List[Dict]:
        """Return stars filtered by magnitude and/or spectral type."""
        params: list = [mag_limit]
        where = "magnitude IS NOT NULL AND magnitude <= ?"

        if spectral_type:
            where += " AND spectral_class LIKE ?"
            params.append(f"{spectral_type}%")

        rows = self._q(
            f"SELECT * FROM stars WHERE {where} ORDER BY magnitude LIMIT ?",
            tuple(params) + (limit,),
        )
        return [self._star_to_dict(r) for r in rows]

    def get_stars_paginated(
        self,
        page: int = 1,
        limit: int = 1000,
        mag_limit: float = 8.0,
        spectral_type: str = "",
        constellation: str = "",
    ):
        """Return (rows, total_count) for paginated star queries."""
        params: list = [mag_limit]
        where = "magnitude IS NOT NULL AND magnitude <= ?"

        if spectral_type:
            where += " AND spectral_class LIKE ?"
            params.append(f"{spectral_type}%")

        if constellation:
            where += " AND constellation LIKE ?"
            params.append(f"%{constellation}%")

        total = self._one(
            f"SELECT COUNT(*) AS cnt FROM stars WHERE {where}", tuple(params)
        )["cnt"]

        offset = (page - 1) * limit
        rows = self._q(
            f"SELECT * FROM stars WHERE {where} ORDER BY magnitude LIMIT ? OFFSET ?",
            tuple(params) + (limit, offset),
        )
        return [self._star_to_dict(r) for r in rows], total

    def get_star_by_id(self, star_id: int) -> Optional[Dict]:
        row = self._one("SELECT * FROM stars WHERE id = ?", (star_id,))
        return self._star_to_dict(row) if row else None

    def search_stars(self, query: str, limit: int = 100) -> List[Dict]:
        like = f"%{query}%"
        rows = self._q(
            """SELECT * FROM stars
               WHERE proper_name LIKE ? OR fictional_name LIKE ?
               LIMIT ?""",
            (like, like, limit),
        )
        return [self._star_to_dict(r) for r in rows]

    def get_stars_in_radius(
        self, x: float, y: float, z: float, radius: float
    ) -> List[Dict]:
        """Return stars within `radius` parsecs of (x, y, z)."""
        r2 = radius * radius
        rows = self._q(
            """SELECT *,
                      ((x-?)*(x-?) + (y-?)*(y-?) + (z-?)*(z-?)) AS dist2
               FROM stars
               WHERE dist2 <= ?
               ORDER BY dist2""",
            (x, x, y, y, z, z, r2),
        )
        return [self._star_to_dict(r) for r in rows]

    def add_star(self, star_data: Dict) -> bool:
        try:
            with self._lock:
                self._con.execute(
                    """INSERT OR REPLACE INTO stars
                       (id, proper_name, fictional_name, fictional_description,
                        x, y, z, dist, ra, dec, magnitude, absolute_magnitude,
                        spectral_class, color_index, luminosity,
                        constellation, nation_id, is_fictional)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        star_data.get("id") or star_data.get("_id"),
                        star_data.get("proper_name") or star_data.get("name") or "",
                        star_data.get("fictional_name") or "",
                        star_data.get("fictional_description") or "",
                        star_data.get("x") or 0.0,
                        star_data.get("y") or 0.0,
                        star_data.get("z") or 0.0,
                        star_data.get("dist"),
                        star_data.get("ra"),
                        star_data.get("dec"),
                        star_data.get("magnitude") or star_data.get("mag"),
                        star_data.get("absolute_magnitude"),
                        star_data.get("spectral_class") or star_data.get("spect") or "",
                        star_data.get("color_index"),
                        star_data.get("luminosity"),
                        star_data.get("constellation") or "",
                        star_data.get("nation_id") or "",
                        1 if star_data.get("is_fictional") else 0,
                    ),
                )
                self._con.commit()
            return True
        except Exception as e:
            print(f"add_star error: {e}")
            return False

    def update_star(self, star_id: int, star_data: Dict) -> bool:
        try:
            with self._lock:
                self._con.execute(
                    """UPDATE stars SET
                       proper_name=?, fictional_name=?, fictional_description=?,
                       x=?, y=?, z=?, dist=?, magnitude=?, spectral_class=?,
                       constellation=?, nation_id=?
                       WHERE id=?""",
                    (
                        star_data.get("proper_name") or star_data.get("name") or "",
                        star_data.get("fictional_name") or "",
                        star_data.get("fictional_description") or "",
                        star_data.get("x") or 0.0,
                        star_data.get("y") or 0.0,
                        star_data.get("z") or 0.0,
                        star_data.get("dist"),
                        star_data.get("magnitude") or star_data.get("mag"),
                        star_data.get("spectral_class") or star_data.get("spect") or "",
                        star_data.get("constellation") or "",
                        star_data.get("nation_id") or "",
                        star_id,
                    ),
                )
                self._con.commit()
                changed = self._con.execute("SELECT changes()").fetchone()["changes()"] > 0
            return changed
        except Exception as e:
            print(f"update_star error: {e}")
            return False

    def delete_star(self, star_id: int) -> bool:
        try:
            with self._lock:
                self._con.execute("DELETE FROM stars WHERE id = ?", (star_id,))
                self._con.commit()
                changed = self._con.execute("SELECT changes()").fetchone()["changes()"] > 0
            return changed
        except Exception as e:
            print(f"delete_star error: {e}")
            return False

    def get_fictional_stars(self) -> List[Dict]:
        rows = self._q("SELECT * FROM stars WHERE is_fictional = 1")
        return [self._star_to_dict(r) for r in rows]

    # ── Exoplanets ────────────────────────────────────────────────────────────

    def get_exoplanets(self) -> List[Dict]:
        return self._q("SELECT * FROM exoplanets WHERE is_fictional = 0")

    def get_fictional_exoplanets(self) -> List[Dict]:
        # Primary source: exoplanets table with is_fictional=1 (has full orbital data)
        rows = self._q("SELECT * FROM exoplanets WHERE is_fictional = 1")
        # Also include legacy fictional_exoplanets table entries (include parent_planet and map_url)
        legacy = self._q("""
            SELECT id, name, host_star_name, planet_type, description,
                   orbit AS semi_major_axis_au, period AS orbital_period_days,
                   mass AS planet_mass_earth, radius AS planet_radius_earth,
                   NULL AS equilibrium_temp_k, NULL AS potentially_habitable,
                   NULL AS star_id, 1 AS is_fictional,
                   parent_planet, map_url
            FROM fictional_exoplanets
        """)
        return rows + legacy

    # ── Nations ───────────────────────────────────────────────────────────────

    @staticmethod
    def _enrich_nation(nation: Dict, territories: List[Dict]) -> Dict:
        """Add nested compatibility fields so the template and Three.js get the
        same rich structure that nations.json originally provided."""
        color = nation.get("color") or "#888888"
        nation["color"] = color
        nation["_id"] = nation["id"]
        nation["territories"] = [t["star_id"] for t in territories]
        # Nested fields consumed by the frontend
        nation["appearance"] = {
            "color": color,
            "border_color": color,
        }
        nation["government"] = {
            "type": nation.get("government_type") or "",
        }
        nation["capital"] = {
            "system": nation.get("full_name", "").replace("The ", "") or nation["name"],
            "star_id": nation.get("capital_star_id"),
            "planet": "",
        }
        nation["era_start"] = nation.get("era_start")
        nation["era_end"] = nation.get("era_end")
        return nation

    def get_nations(self) -> List[Dict]:
        nations = self._q("SELECT * FROM nations")
        for nation in nations:
            territories = self._q(
                "SELECT star_id FROM nation_territories WHERE nation_id = ?",
                (nation["id"],),
            )
            self._enrich_nation(nation, territories)
        return nations

    def get_nation_by_id(self, nation_id: str) -> Optional[Dict]:
        nation = self._one("SELECT * FROM nations WHERE id = ?", (nation_id,))
        if nation:
            territories = self._q(
                "SELECT star_id FROM nation_territories WHERE nation_id = ?",
                (nation_id,),
            )
            self._enrich_nation(nation, territories)
        return nation

    def add_nation(self, nation_data: Dict) -> bool:
        try:
            nation_id = str(nation_data.get("id") or nation_data.get("_id") or "")
            with self._lock:
                self._con.execute(
                    """INSERT OR REPLACE INTO nations
                       (id, name, full_name, description, color, government_type, capital_star_id)
                       VALUES (?,?,?,?,?,?,?)""",
                    (
                        nation_id,
                        str(nation_data.get("name") or ""),
                        str(nation_data.get("full_name") or ""),
                        str(nation_data.get("description") or ""),
                        str(nation_data.get("color") or ""),
                        str(nation_data.get("government_type") or ""),
                        nation_data.get("capital_star_id"),
                    ),
                )
                for star_id in nation_data.get("territories", []):
                    self._con.execute(
                        "INSERT OR IGNORE INTO nation_territories (nation_id, star_id) VALUES (?,?)",
                        (nation_id, star_id),
                    )
                self._con.commit()
            return True
        except Exception as e:
            print(f"add_nation error: {e}")
            return False

    # ── Trade routes ──────────────────────────────────────────────────────────

    def get_trade_routes(self) -> List[Dict]:
        routes = self._q("SELECT * FROM trade_routes")
        # Re-shape to match the legacy nested 'endpoints' format
        for r in routes:
            r["endpoints"] = {
                "from": {"star_id": r.get("from_star_id")},
                "to":   {"star_id": r.get("to_star_id")},
            }
        return routes

    # ── Stellar regions ───────────────────────────────────────────────────────

    def get_stellar_regions(self) -> List[Dict]:
        rows = self._q("SELECT * FROM stellar_regions")
        for r in rows:
            r["center"] = [
                (r.get("x_min", 0) + r.get("x_max", 0)) / 2,
                (r.get("y_min", 0) + r.get("y_max", 0)) / 2,
                (r.get("z_min", 0) + r.get("z_max", 0)) / 2,
            ]
            r["x_range"] = [r.get("x_min"), r.get("x_max")]
            r["y_range"] = [r.get("y_min"), r.get("y_max")]
            r["z_range"] = [r.get("z_min"), r.get("z_max")]
            r["color"] = [
                r.get("color_r", 128),
                r.get("color_g", 128),
                r.get("color_b", 128),
            ]
        return rows

    # ── Statistics ────────────────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        return {
            "stars":                self._one("SELECT COUNT(*) AS c FROM stars WHERE is_fictional=0")["c"],
            "fictional_stars":      self._one("SELECT COUNT(*) AS c FROM stars WHERE is_fictional=1")["c"],
            "nations":              self._one("SELECT COUNT(*) AS c FROM nations")["c"],
            "exoplanets":           self._one("SELECT COUNT(*) AS c FROM exoplanets WHERE is_fictional=0")["c"],
            "fictional_exoplanets": self._one("SELECT COUNT(*) AS c FROM exoplanets WHERE is_fictional=1")["c"],
            "trade_routes":         self._one("SELECT COUNT(*) AS c FROM trade_routes")["c"],
            "stellar_regions":      self._one("SELECT COUNT(*) AS c FROM stellar_regions")["c"],
        }

    def get_system_stats(self, star_id: int) -> Optional[Dict]:
        star = self.get_star_by_id(star_id)
        if not star:
            return None
        star_name = star.get("name") or ""
        return {
            "star": star,
            "exoplanets": self._q(
                "SELECT * FROM exoplanets WHERE host_star_name = ?", (star_name,)
            ),
            "fictional_exoplanets": self._q(
                "SELECT * FROM exoplanets WHERE is_fictional=1 AND host_star_name = ?", (star_name,)
            ),
        }

    # ── Saved Views ───────────────────────────────────────────────────────────

    def get_saved_views(self, user_id: int) -> List[Dict]:
        return self._q(
            "SELECT * FROM saved_views WHERE user_id=? ORDER BY created_at DESC",
            (user_id,),
        )

    def save_view(self, user_id: int, name: str, params: str) -> Optional[int]:
        try:
            with self._lock:
                self._con.execute(
                    "INSERT INTO saved_views (user_id, name, params) VALUES (?,?,?)",
                    (user_id, name[:200], params),
                )
                self._con.commit()
                row = self._con.execute("SELECT last_insert_rowid() AS id").fetchone()
            return row["id"] if row else None
        except Exception as e:
            print(f"save_view error: {e}")
            return None

    def delete_saved_view(self, view_id: int, user_id: int) -> bool:
        try:
            with self._lock:
                self._con.execute(
                    "DELETE FROM saved_views WHERE id=? AND user_id=?",
                    (view_id, user_id),
                )
                self._con.commit()
                changed = self._con.execute("SELECT changes() AS c").fetchone()["c"] > 0
            return changed
        except Exception as e:
            print(f"delete_saved_view error: {e}")
            return False

    def reload_data(self):
        """No-op: data is always on disk with SQLite."""
        pass
