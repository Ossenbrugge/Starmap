-- Starmap SQLite Schema
-- Generated during rebuild. Run scripts/migrate_to_sqlite.py to populate.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS stars (
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
    is_fictional     INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_stars_magnitude     ON stars(magnitude);
CREATE INDEX IF NOT EXISTS idx_stars_spectral      ON stars(spectral_class);
CREATE INDEX IF NOT EXISTS idx_stars_nation        ON stars(nation_id);
CREATE INDEX IF NOT EXISTS idx_stars_x             ON stars(x);
CREATE INDEX IF NOT EXISTS idx_stars_y             ON stars(y);
CREATE INDEX IF NOT EXISTS idx_stars_z             ON stars(z);
CREATE INDEX IF NOT EXISTS idx_stars_proper_name   ON stars(proper_name);

CREATE TABLE IF NOT EXISTS exoplanets (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    host_star_name   TEXT,
    ra               REAL,
    dec              REAL,
    distance         REAL,
    discovery_method TEXT,
    is_fictional     INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_exoplanets_host ON exoplanets(host_star_name);

CREATE TABLE IF NOT EXISTS fictional_exoplanets (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    host_star_name   TEXT,
    planet_type      TEXT,
    description      TEXT,
    orbit            REAL,
    period           REAL,
    mass             REAL,
    radius           REAL
);

CREATE INDEX IF NOT EXISTS idx_fictional_exo_host ON fictional_exoplanets(host_star_name);

CREATE TABLE IF NOT EXISTS nations (
    id               TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    full_name        TEXT,
    description      TEXT,
    color            TEXT,
    government_type  TEXT,
    capital_star_id  INTEGER
);

CREATE TABLE IF NOT EXISTS nation_territories (
    nation_id        TEXT NOT NULL,
    star_id          INTEGER NOT NULL,
    PRIMARY KEY (nation_id, star_id),
    FOREIGN KEY (nation_id) REFERENCES nations(id)
    -- star_id has no FK: some territory IDs use alternate catalog numbering
);

CREATE INDEX IF NOT EXISTS idx_nation_territories_nation ON nation_territories(nation_id);
CREATE INDEX IF NOT EXISTS idx_nation_territories_star   ON nation_territories(star_id);

CREATE TABLE IF NOT EXISTS trade_routes (
    id               TEXT PRIMARY KEY,
    name             TEXT,
    from_star_id     INTEGER,
    to_star_id       INTEGER,
    nation_id        TEXT,
    route_type       TEXT,
    category         TEXT,
    frequency        TEXT
);

CREATE TABLE IF NOT EXISTS stellar_regions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    short_name       TEXT,
    description      TEXT,
    octant_number    INTEGER,
    x_min            REAL,
    x_max            REAL,
    y_min            REAL,
    y_max            REAL,
    z_min            REAL,
    z_max            REAL,
    color_r          INTEGER,
    color_g          INTEGER,
    color_b          INTEGER
);
