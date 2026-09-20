# Starmap — Felgenland Saga

An interactive 3D star map for the *Felgenland Saga* science-fiction universe. Real stellar data from the HYG catalogue is displayed alongside fictional nations, planetary systems, and trade networks from the setting.

---

## Universe overview

The **Felgenland Saga** is set within 30 parsecs of Sol, where human civilisation has expanded to form competing nations:

| Nation | Capital system | Notes |
|---|---|---|
| Terran Directorate | Sol | Earth-centred authoritarian republic |
| Felgenland Union | Holsten Tor (20 LMi) | Federated Persona Union; capital world Stahlburgh |
| Protelani Republic | Protelan (61 UMa) | Ultra-capitalist Mercantile republic |
| Dorsai Republic | Fomalhaut | Elite military specialists |
| Pentothian Trade Conglomerate | Pentothia Prime (Groombridge 1618) | Neutral reptilian trader confederacy |

Key frontier systems include **Tiefe-Grenze Tor** (HD 86729), **Brandenburg Tor** (11 LMi), and **Greifen Tor** (55 Cancri / Copernicus).

---

## Features

- **3D starmap** — Three.js with GPU ShaderMaterial LOD; 24,000+ stars
- **WASD / arrow-key navigation** — fly the camera through space; Q/E for vertical; speed scales with zoom level
- **Mouse controls** — orbit, zoom, pan (OrbitControls)
- **Click stars** for a detail panel showing name, spectral class, distance, and nation
- **Screenshot** — download the current view as a PNG (📷 button in Tools)
- **A-Frame VR view** — optional WebXR mode
- **Nation overlays** — colour-coded star ownership
- **Fictional data** — custom stars, exoplanets, and galactic directions layered over real catalogue data
- **REST API** — versioned JSON API (`/api/v1/`)
- **JWT + session authentication** — protected write endpoints; read endpoints are public

---

## Setup

### Requirements

- Python 3.12+

```bash
pip install -r requirements.txt
```

### Database

Star data lives in `data/starmap.sqlite` (git-ignored). Build it from the JSON/CSV sources, then layer on the saga canon. Order matters:

```bash
python scripts/migrate_to_sqlite.py       # HYG stars, exoplanets, nations, routes
python scripts/seed_star_canon.py         # canon star rows (auto-generated from the live DB)
python scripts/migrate_timeline_events.py
python scripts/migrate_nation_lore.py
python scripts/seed_saga_lore.py
python scripts/seed_master_timeline.py
python scripts/import_provinces.py
```

The Dockerfile runs the same chain at build time.

### Run

```bash
python app_refactored.py
```

Opens at `http://localhost:8080`.

### Docker

```bash
docker compose up --build
```

Serves on `STARMAP_PORT` (default `8081`). The container rebuilds the database into the mounted `data/` volume on first start if it is absent.

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `STARMAP_SECRET_KEY` | (dev key) | Flask session + JWT signing key |
| `STARMAP_PORT` | `8080` | Listening port |

**Always set `STARMAP_SECRET_KEY` before deploying.**

### Default login

| Username | Password |
|---|---|
| `admin` | `felgenland_secure_2025` |
| `starmap_admin` | `galactic_command_auth` |

**Change these before deploying.**

---

## Project structure

```
app_refactored.py          Application entry point (factory pattern)
auth.py                    AuthManager, User model, JWT helpers

app/
  config/                  Flask and auth configuration
  middleware/              Auth and rate-limiting middleware
  repositories/            Data access layer (SQLite)
  routes/                  Flask blueprints — one per domain
    stars_blueprint.py
    nations_blueprint.py
    fictional_blueprint.py
    search_blueprint.py
    stats_blueprint.py
    stellar_regions_blueprint.py
    trade_routes_blueprint.py
    api_routes.py          Protected CRUD routes
    auth_routes.py
    web_routes.py
  services/                Business logic layer
  utils/                   Shared response helpers (success_response / error_response)

models/
  database.py              SQLite singleton (Database class, anchored to data/starmap.sqlite)

static/js/
  starmap-threejs-simple.js   Three.js starmap — sole JS entry point

templates/
  starmap.html             Single-page application shell

static/css/
  starmap.css                 Design tokens + all UI styling

scripts/
  migrate_to_sqlite.py     CSV/JSON → SQLite (first step of the rebuild chain)
  seed_*.py, migrate_*.py  Saga canon layers (see Database above)
  sync_from_brain.py       Reports drift between the author's timeline doc and the DB
  generate_wiki_stubs.py   Emits wiki page stubs into wiki_stubs/ (staging only)

data/
  starmap.sqlite           HYG star catalogue + fictional data
  exoplanets.json          Exoplanet records
```

---

## API reference

All endpoints use the prefix `/api/v1/`. Requests to `/api/<path>` redirect to `/api/v1/<path>` (HTTP 301).

### Public (no auth)

All `GET` endpoints are public.

| Endpoint | Description |
|---|---|
| `/api/v1/stars` | Paginated star list (`limit`, `mag_limit`, `spectral_type`, `page`) |
| `/api/v1/stars/<id>` | Single star with trade-route summary |
| `/api/v1/stars/search?q=` · `/stars/nearby` | Star search and proximity queries |
| `/api/v1/search?q=<query>` | Combined star + nation search |
| `/api/v1/fictional-stars` · `/fictional-exoplanets` | Canon stars and worlds |
| `/api/v1/exoplanets` | Real exoplanet catalogue |
| `/api/v1/nations` · `/nations/<id>` · `/nations/<id>/stars` · `/nations/<id>/territories` | Nations and holdings |
| `/api/v1/provinces` | Felgenland Union provinces |
| `/api/v1/trade-routes` | Trade network |
| `/api/v1/timeline` · `/events` · `/star-ownership` | Era timeline, historical events, ownership intervals |
| `/api/v1/stellar-regions` · `/galactic-directions` | Region boundaries and named directions |
| `/api/v1/stats` | Dataset statistics |
| `/health` | Health check |

### Protected (JWT or session cookie)

Every write is guarded.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/fictional-stars` | Add a fictional star (`name`, `x`, `y`, `z` required) |
| DELETE | `/api/v1/fictional-stars/<id>` | Delete a fictional star |
| POST | `/api/v1/fictional-exoplanets` | Add a fictional exoplanet |
| POST / DELETE | `/api/v1/fictional/{stars,nations,trade-routes}` | Legacy fictional CRUD |
| GET / POST / DELETE | `/api/v1/views` | Saved camera views for the logged-in user |

### Auth endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/login` | Session login |
| GET | `/logout` | Session logout |
| POST | `/api/auth/token` | Issue JWT token (session must be active) |

**Using a JWT token:**

```bash
# Get a token
curl -X POST http://localhost:8080/api/auth/token \
     -b "session=<cookie>"

# Authenticate a request
curl http://localhost:8080/api/v1/nations/felgenland_union \
     -H "Authorization: Bearer <token>"
```

---

## Controls

### 3D view

| Input | Action |
|---|---|
| Left-drag | Orbit camera |
| Right-drag / two-finger drag | Pan |
| Scroll | Zoom |
| W / Arrow Up | Fly forward |
| S / Arrow Down | Fly back |
| A / Arrow Left | Fly left |
| D / Arrow Right | Fly right |
| Q | Fly up |
| E | Fly down |
| Click a star | Show detail panel |

Navigation speed scales with camera distance — fast when zoomed out, fine-grained when zoomed in.

### Screenshot

Click **📷 Screenshot** in the Tools panel to download the current view as a timestamped PNG.

---

## Data sources

- **Stars** — HYG catalogue (Hipparcos, Yale Bright Star, Gliese/Jahreiß)
- **Exoplanets** — NASA Exoplanet Archive
- **Political data, trade routes, planetary systems** — original *Felgenland Saga* lore

---

## Testing

```bash
python -m pytest tests/
```

The suite runs fully in-process (Flask test client + a fixture SQLite database); no server needs to be running. CI runs it on Linux, macOS and Windows.
