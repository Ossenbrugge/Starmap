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

Star data lives in `data/starmap.sqlite`. If that file does not exist, migrate from the source CSV:

```bash
python scripts/migrate_to_sqlite.py
```

### Run

```bash
python app_refactored.py
```

Opens at `http://localhost:8080`.

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

scripts/
  migrate_to_sqlite.py     One-time CSV → SQLite migration

data/
  starmap.sqlite           HYG star catalogue + fictional data
  exoplanets.json          Exoplanet records
```

---

## API reference

All endpoints use the prefix `/api/v1/`. Requests to `/api/<path>` redirect to `/api/v1/<path>` (HTTP 301).

### Public (no auth)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/stars` | Paginated star list (`limit`, `mag_limit`, `spectral_type`, `page`) |
| GET | `/api/v1/stars/<id>` | Single star with trade-route summary |
| GET | `/api/v1/fictional-stars` | All fictional stars |
| GET | `/api/v1/fictional-exoplanets` | All fictional exoplanets |
| GET | `/api/v1/nations` | All nations |
| GET | `/api/v1/stats` | Dataset statistics |
| GET | `/api/v1/galactic-directions` | Named galactic directions |
| GET | `/api/v1/search?q=<query>` | Star search by name |
| GET | `/health` | Health check |

### Protected (JWT or session cookie)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/nations/<id>` | Nation detail |
| GET | `/api/v1/nations/<id>/stars` | Stars controlled by a nation |
| GET | `/api/v1/nations/<id>/territories` | Nation territory data |
| POST | `/api/v1/fictional-stars` | Add a fictional star (`name`, `x`, `y`, `z` required) |
| DELETE | `/api/v1/fictional-stars/<id>` | Delete a fictional star |
| POST | `/api/v1/fictional-exoplanets` | Add a fictional exoplanet (`name`, `star_name`, `distance`, `period` required) |

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

Some tests require the server to be running on `localhost:8080`.
