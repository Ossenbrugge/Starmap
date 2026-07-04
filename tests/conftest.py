"""
Pytest fixtures for the Starmap test suite.

The suite runs entirely in-process against ``create_app()`` from
``app_refactored.py`` (Flask test client — no live server) and a small
fixture SQLite database built from scratch for each test session.

Import order matters: environment variables must be set before any app
module is imported, and ``models.database._DB_PATH`` must point at the
fixture DB before ``app_refactored`` is imported (importing it creates
the app and opens the database singleton at module level).
"""

import os
import sqlite3
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test credentials — must be in the environment before auth modules import.
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "TestAdminPass123"

os.environ["STARMAP_SECRET_KEY"] = "test-secret-key"
os.environ["FLASK_ENV"] = "testing"
os.environ["STARMAP_ADMIN_PASSWORD"] = ADMIN_PASSWORD
os.environ["STARMAP_ADMIN2_PASSWORD"] = "TestAdmin2Pass456"


# ── Fixture database ─────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE stars (
    id               INTEGER PRIMARY KEY,
    hip              REAL,
    hd               REAL,
    bayer            TEXT,
    flamsteed        REAL,
    constellation    TEXT,
    proper_name      TEXT,
    fictional_name   TEXT,
    fictional_description TEXT,
    x                REAL NOT NULL DEFAULT 0,
    y                REAL NOT NULL DEFAULT 0,
    z                REAL NOT NULL DEFAULT 0,
    dist             REAL,
    ra               REAL,
    dec              REAL,
    magnitude        REAL,
    absolute_magnitude REAL,
    spectral_class   TEXT,
    color_index      REAL,
    luminosity       REAL,
    nation_id        TEXT,
    is_fictional     INTEGER NOT NULL DEFAULT 0,
    era_start        INTEGER DEFAULT NULL,
    era_end          INTEGER DEFAULT NULL,
    discovery_number INTEGER DEFAULT NULL,
    discovery_year   INTEGER DEFAULT NULL
);
CREATE TABLE exoplanets (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    host_star_name   TEXT,
    ra               REAL,
    dec              REAL,
    distance         REAL,
    discovery_method TEXT,
    is_fictional     INTEGER NOT NULL DEFAULT 0,
    semi_major_axis_au REAL,
    orbital_period_days REAL,
    planet_radius_earth REAL,
    planet_mass_earth REAL,
    equilibrium_temp_k REAL,
    planet_type      TEXT,
    potentially_habitable INTEGER DEFAULT 0,
    star_id          INTEGER
);
CREATE TABLE fictional_exoplanets (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    host_star_name   TEXT,
    planet_type      TEXT,
    description      TEXT,
    orbit            REAL,
    period           REAL,
    mass             REAL,
    radius           REAL,
    parent_planet    TEXT DEFAULT NULL,
    map_url          TEXT DEFAULT NULL
);
CREATE TABLE nations (
    id               TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    full_name        TEXT,
    description      TEXT,
    color            TEXT,
    government_type  TEXT,
    capital_star_id  INTEGER,
    era_start        INTEGER DEFAULT NULL,
    era_end          INTEGER DEFAULT NULL
);
CREATE TABLE nation_territories (
    nation_id        TEXT NOT NULL,
    star_id          INTEGER NOT NULL,
    PRIMARY KEY (nation_id, star_id),
    FOREIGN KEY (nation_id) REFERENCES nations(id)
);
CREATE TABLE trade_routes (
    id               TEXT PRIMARY KEY,
    name             TEXT,
    from_star_id     INTEGER,
    to_star_id       INTEGER,
    nation_id        TEXT,
    route_type       TEXT,
    category         TEXT,
    frequency        TEXT,
    era_start        INTEGER DEFAULT NULL,
    era_end          INTEGER DEFAULT NULL
);
CREATE TABLE stellar_regions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    short_name       TEXT,
    description      TEXT,
    octant_number    INTEGER,
    x_min REAL, x_max REAL,
    y_min REAL, y_max REAL,
    z_min REAL, z_max REAL,
    color_r INTEGER, color_g INTEGER, color_b INTEGER
);
CREATE TABLE saved_views (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    params TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

# (id, hip, constellation, proper_name, fictional_name, x, y, z, dist,
#  magnitude, spectral_class, nation_id, is_fictional,
#  discovery_number, discovery_year)
STARS = [
    (0,      None,  "",    "Sol",             "",        0.0,   0.0,   0.0,  0.0,  -26.74, "G2V", "terran_directorate", 0, 0,    None),
    (71456,  71456, "Cen", "Rigil Kentaurus", "Hawking", 3.03, -3.06, -0.14, 1.34,  -0.27, "G2V", "terran_directorate", 0, 2,    2091),
    (53879,  53879, "UMa", "Lalande 21185",   "",       -6.5,   1.6,   4.9,  2.55,   7.5,  "M2V", "terran_directorate", 0, 1,    2080),
    (8087,   8087,  "Cet", "Tau Ceti",        "",        9.0,  -8.0,  -3.0,  3.65,   3.5,  "G8V", "felgenland_union",   0, 6,    2200),
    (42,     None,  "Lyr", "Dim Test Star",   "",       20.0,  20.0,  20.0, 10.6,    9.5,  "M5V", "",                   0, None, None),
    (90001,  90001, "Ori", "nan",             "",       50.0,  50.0,  50.0, 26.5,    6.0,  "K0V", "",                   0, None, None),
    (999001, None,  "",    "",                "Nova Testia", 10.0, 10.0, 10.0, 5.3, 12.0,  "M4V", "",                   1, None, None),
]

NATIONS = [
    # id, name, full_name, description, color, government_type,
    # capital_star_id, era_start, era_end
    ("terran_directorate", "Terran Directorate", "The Terran Directorate",
     "Founding human polity", "#0066cc", "directorate", 0, 2091, None),
    ("felgenland_union", "Felgenland Union", "The Felgenland Union",
     "Breakaway trade federation", "#cc3300", "federation", 8087, 2210, 2357),
]

TERRITORIES = [
    ("terran_directorate", 0),
    ("terran_directorate", 71456),
    ("terran_directorate", 53879),
    ("felgenland_union", 8087),
]

TRADE_ROUTES = [
    # id, name, from, to, nation, type, category, frequency, era_start, era_end
    ("sol_centauri_run", "Sol-Centauri Run", 0, 71456,
     "terran_directorate", "commercial", "primary", "daily", 2100, None),
    ("tau_ceti_loop", "Tau Ceti Loop", 8087, 0,
     "felgenland_union", "commercial", "secondary", "weekly", 2210, 2357),
]

EXOPLANETS = [
    # name, host_star_name, is_fictional, planet_type, potentially_habitable, star_id
    ("Tau Ceti e", "Tau Ceti", 0, "super-earth", 1, 8087),
    ("Lalande b", "Lalande 21185", 0, "terrestrial", 0, 53879),
    ("New Brandenburg", "Tau Ceti", 1, "terrestrial", 1, 8087),
]

LEGACY_FICTIONAL_EXOPLANETS = [
    # name, host_star_name, planet_type, description, orbit, period, mass,
    # radius, parent_planet, map_url
    ("Legacy Colony World", "Rigil Kentaurus", "terrestrial",
     "Seeded via the legacy fictional_exoplanets table",
     1.2, 400.0, 1.1, 1.05, None, "http://example.com/map"),
]

STELLAR_REGIONS = [
    # name, short_name, description, octant, x_min, x_max, y_min, y_max,
    # z_min, z_max, r, g, b
    ("Test Octant", "TO", "Fixture region", 1,
     0.0, 10.0, -10.0, 0.0, 0.0, 20.0, 100, 150, 200),
]


def build_fixture_db(db_path):
    """Create and seed the fixture SQLite database."""
    con = sqlite3.connect(str(db_path))
    con.executescript(SCHEMA)
    con.executemany(
        """INSERT INTO stars
           (id, hip, constellation, proper_name, fictional_name,
            x, y, z, dist, magnitude, spectral_class, nation_id,
            is_fictional, discovery_number, discovery_year)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        STARS,
    )
    con.executemany(
        """INSERT INTO nations
           (id, name, full_name, description, color, government_type,
            capital_star_id, era_start, era_end)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        NATIONS,
    )
    con.executemany(
        "INSERT INTO nation_territories (nation_id, star_id) VALUES (?,?)",
        TERRITORIES,
    )
    con.executemany(
        """INSERT INTO trade_routes
           (id, name, from_star_id, to_star_id, nation_id, route_type,
            category, frequency, era_start, era_end)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        TRADE_ROUTES,
    )
    con.executemany(
        """INSERT INTO exoplanets
           (name, host_star_name, is_fictional, planet_type,
            potentially_habitable, star_id)
           VALUES (?,?,?,?,?,?)""",
        EXOPLANETS,
    )
    con.executemany(
        """INSERT INTO fictional_exoplanets
           (name, host_star_name, planet_type, description, orbit, period,
            mass, radius, parent_planet, map_url)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        LEGACY_FICTIONAL_EXOPLANETS,
    )
    con.executemany(
        """INSERT INTO stellar_regions
           (name, short_name, description, octant_number,
            x_min, x_max, y_min, y_max, z_min, z_max,
            color_r, color_g, color_b)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        STELLAR_REGIONS,
    )
    con.commit()
    con.close()


# ── Application fixtures ─────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app(tmp_path_factory):
    """Session-wide Flask app wired to the fixture SQLite database."""
    db_path = tmp_path_factory.mktemp("db") / "starmap_test.sqlite"
    build_fixture_db(db_path)

    # Point every Database() instantiation (the app singleton and the
    # per-request instance in the timeline blueprint) at the fixture DB
    # before app_refactored is imported.
    import models.database as database_module
    database_module._DB_PATH = str(db_path)

    import app_refactored

    flask_app = app_refactored.app
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    """Fresh, unauthenticated test client per test."""
    return app.test_client()


@pytest.fixture
def logged_in_client(app):
    """Test client with an authenticated Flask-Login session."""
    test_client = app.test_client()
    response = test_client.post(
        "/login",
        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 302, "session login failed"
    return test_client


@pytest.fixture(scope="session")
def jwt_headers(app):
    """Authorization headers with a valid JWT for the admin user."""
    from app.services.auth_service import auth_service

    user = auth_service.auth_manager.users[ADMIN_USERNAME]
    token = auth_service.generate_jwt_token(user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def database(app):
    """The shared Database singleton, for direct unit tests."""
    from app_refactored import get_database

    return get_database()
