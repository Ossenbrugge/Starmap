# Starmap - Felgenland Saga

A 3D interactive starmap for the **Felgenland Saga** universe, featuring real astronomical data enhanced with fictional political entities, trade networks, and planetary systems.

## 🌌 Universe Overview

The **Felgenland Saga** is set in a region of space within 30 parsecs of Earth, where human civilization has expanded to form competing nations and trade networks. This starmap brings that universe to life with:

- **Real astronomical data** from Gaia, Hipparcos, and NASA catalogs
- **Fictional political nations** with territories and capitals
- **Trade routes** connecting major systems
- **Enhanced planetary systems** including habitable worlds and capitals

## ✨ Features

- **24,676 Real Stars** with accurate astronomical data from multiple catalogs
- **5 Major Nations** controlling territories across human space:
  - **Terran Directorate** - Earth-centered authoritarian republic
  - **Felgenland Union** - Trade federation with Eclipse Festival culture
  - **Protelani Republic** - Ultra-capitalist republic on Protelan moon
  - **Dorsai Republic** - Elite military training specialists
  - **Pentothian Trade Conglomerate** - Neutral reptilian traders
- **18 Trade Routes** connecting capitals and resource systems
- **41 Fictional Planets** across key star systems including:
  - **Stahlburgh** - Capital of Felgenland Union (20 LMi system)
  - **Protelan** - Protelani Republic capital moon (61 UMa system)
  - **Pentothia Prime** - Reptilian trade hub (Groombridge 1618)
  - **Valorgraemo** - Dorsai military academy world (Fomalhaut)
- **425 Real Exoplanets** from NASA Exoplanet Archive
- **Interactive 3D Visualization** with political overlays
- **Real-time Search** and advanced filtering
- **Modern Responsive UI** with space-themed design

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open your browser to:** http://localhost:8080

## 🏛️ Major Star Systems

### Political Capitals
- **Sol** (Terran Directorate) - Earth and the Solar System
- **Holsten Tor** (20 LMi) - Felgenland Union capital with Stahlburgh world
- **61 Ursae Majoris** - Protelani Republic capital with Protelan moon
- **Fomalhaut** - Dorsai Republic with military training worlds
- **Pentothia Prime** (Groombridge 1618) - Neutral reptilian trade hub

### Key Frontier Systems
- **Tiefe-Grenze Tor** (HD 86729) - Deep frontier gateway of Felgenland Union
- **Brandenburg Tor** (11 LMi) - Manufacturing hub
- **Griefen Tor** (55 Cancri) - Resource extraction center

## 🛠️ Architecture

- **Backend**: Flask with clean MVC architecture
- **Database**: JSON-based with in-memory caching for performance
- **Frontend**: Modern JavaScript with Plotly.js for 3D visualization
- **UI**: Bootstrap 5 with custom space-themed styling

```
starmap/
├── app.py                    # Main Flask application
├── controllers/              # API controllers
├── models/                   # Data models and database
├── static/                   # Frontend assets (CSS, JS)
├── templates/                # HTML templates
└── data/                     # All data files (stars, nations, planets)
```

## 🔌 API Endpoints

- `GET /api/stars` - Get filtered star data
- `GET /api/star/{id}` - Get detailed star information with planets
- `GET /api/nations` - Get all political nations
- `GET /api/trade-routes` - Get trade and military routes
- `GET /api/search` - Search stars by name
- `GET /api/fictional-exoplanets` - Get fictional planetary systems
- `GET /api/stellar-regions` - Get galactic regions
- `GET /api/stats` - Get database statistics

## 🎮 Controls

- **Mouse**: Rotate, zoom, and pan the 3D starmap
- **Click**: Select stars for detailed information including planets
- **Search**: Find specific stars or systems
- **Filters**: Adjust magnitude, spectral type, and star count limits
- **Overlays**: Toggle nations, trade routes, galactic regions, and directions
- **Nations Legend**: View detailed information about political entities

## 📊 Data Sources

- **Real Stars**: Gaia DR3, Hipparcos, Henry Draper Catalog
- **Exoplanets**: NASA Exoplanet Archive with confirmed discoveries
- **Political Data**: Original Felgenland Saga universe lore
- **Trade Networks**: Custom economic and military route systems
- **Planetary Systems**: Mix of real confirmed planets and fictional worlds

## 🎯 Universe Scope

The starmap covers a **30 parsec sphere** around Sol, representing the practical limits of human expansion in the Felgenland Saga timeline. This includes:

- **Most stars visible to the naked eye**
- **All major nearby stellar neighbors**
- **Key systems for interstellar civilization**
- **Realistic travel distances for trade and politics**

## ⚡ Performance Features

- **In-memory data caching** for instant API responses
- **WebGL-accelerated 3D rendering** with smooth navigation
- **Efficient spatial filtering** for large star catalogs
- **Optimized search algorithms** with fuzzy matching
- **Responsive design** for desktop and mobile devices

---

*Part of the **Felgenland Saga** universe - explore the political intrigue, trade networks, and frontier conflicts that define human expansion among the stars.*