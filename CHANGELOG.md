# Changelog — Starmap · Felgenland Saga

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Era/timeline system: slider, playback, guided tours (full history and War Tour),
  historical event markers with clustered glyphs, era-aware nation colours and labels.
- Animated system map (orbital view with habitable-zone band and Kepler-relative speeds).
- Astrogator's details panel: magnitudes, spectral data, mass/luminosity estimates,
  jump periphery, travel times, companion stars, charted worlds.
- Nation lore panel, two-nation compare mode, Felgenland province browser (331 provinces).
- Print-ready map export (PNG/SVG), shareable deep links, saved views for logged-in users.
- Distance-based View Range with GPU depth fade; canon stars always visible and selectable.
- Docker appliance (`docker compose up`), configurable `STARMAP_PORT`, `/health` endpoint.
- In-process pytest suite (77 tests) with fixture database; CI on Linux, macOS, Windows.

### Changed
- Rendering moved from Plotly to Three.js with a ShaderMaterial star field (24k+ stars).
- Storage moved from MontyDB to a single SQLite file built by `scripts/migrate_to_sqlite.py`
  plus the saga canon seed scripts.
- All `GET` API endpoints are public; writes and saved views require JWT or session auth.
- Legacy `/api/<path>` requests redirect to `/api/v1/<path>`.
- Consolidated UI styling into `static/css/starmap.css` with a token-based design system.

### Removed
- Legacy MontyDB controllers, handlers and one-off CSV conversion scripts.
- Exoplanet marker spheres on the galaxy map (the system map covers them).
- Dead "Star Limit" control (replaced by View Range).

## [0.1.0-alpha] — 2024

Initial Plotly + MontyDB prototype: 3D star catalogue, nations, trade routes,
planetary systems, REST API and CRUD tooling. Superseded by the Three.js/SQLite stack above.
