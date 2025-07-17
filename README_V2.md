# Starmap V2 - Clean Edition

A streamlined 3D interactive starmap application with modern Flask architecture.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The app will be available at `http://localhost:5000`

## 📁 Project Structure

```
starmap/
├── app.py                    # Main Flask application
├── controllers/              # API controllers
│   └── api_controller.py     # API endpoints
├── models/                   # Data models
│   └── database.py           # Database interface
├── static/                   # Frontend assets
│   ├── css/starmap.css       # Styles
│   └── js/starmap.js         # JavaScript
├── templates/                # HTML templates
│   └── starmap.html          # Main page
├── data/                     # Data files
│   ├── stars.json            # Star catalog
│   ├── nations.json          # Political entities
│   ├── trade_routes.json     # Trade networks
│   ├── exoplanets.json       # Exoplanet data
│   ├── fictional_stars.csv   # Additional fictional stars
│   ├── exoplanet_catalog_*.csv # Exoplanet catalog
│   └── stellar_regions.json  # Galactic regions
└── _cleanup_backup/          # Legacy files (safe to delete)
```

## ✨ Features

- **3D Interactive Starmap**: Navigate through 30 parsecs of space around Sol
- **Political Overlays**: Visualize nation territories and borders
- **Trade Routes**: View commercial and military supply lines
- **Stellar Regions**: Galactic octants and directional markers
- **Exoplanets**: Real and fictional planetary systems
- **Search**: Find specific stars and systems

## 🗄️ Data Sources

- **Real Star Data**: Based on Gaia and Hipparcos catalogs
- **Fictional Elements**: Custom nations, trade routes, and enhanced lore
- **Exoplanets**: NASA Exoplanet Archive data + fictional additions

## 🧹 Cleanup Summary

This version has been cleaned up from the original codebase:
- ✅ Removed legacy V1 architecture
- ✅ Consolidated duplicate data files
- ✅ Streamlined to single Flask app
- ✅ Moved all data to `/data` directory
- ✅ Preserved all functionality

Legacy files are safely stored in `_cleanup_backup/` and can be deleted once you're satisfied with the cleanup.