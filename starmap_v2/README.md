# Starmap V2 - Streamlined 3D Interactive Starmap

A completely rewritten, optimized version of the starmap application with clean MVC architecture and modern UI.

## Features

- **24,675 Real Stars** with astronomical data
- **5 Fictional Nations** with political territories  
- **11 Trade Routes** connecting star systems
- **425 Exoplanets** with discovery data
- **Interactive 3D Visualization** powered by Plotly.js
- **Real-time Search** and filtering
- **Political Overlays** showing nation control
- **Modern Responsive UI** with dark space theme

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your browser to: http://localhost:8080

## Architecture

- **Model**: `models/database.py` - Lightweight JSON-based data layer with memory caching
- **View**: `templates/starmap.html` - Clean HTML5 template with Bootstrap 5
- **Controller**: `controllers/api_controller.py` - RESTful API endpoints
- **Frontend**: `static/js/starmap.js` - Modern ES6+ JavaScript with class-based architecture

## API Endpoints

- `GET /api/stars` - Get filtered star data
- `GET /api/star/{id}` - Get detailed star information  
- `GET /api/nations` - Get all fictional nations
- `GET /api/trade-routes` - Get all trade routes
- `GET /api/search` - Search stars by name
- `GET /api/stats` - Get database statistics

## Controls

- **Mouse**: Rotate, zoom, and pan the 3D view
- **Click**: Select stars for detailed information
- **Search**: Type star names for quick navigation
- **Filters**: Adjust magnitude, spectral type, and star count
- **Overlays**: Toggle nations and trade route visualizations

## Data Sources

- Real star data from Hipparcos, Gliese, and HD catalogs
- Exoplanet data from NASA Exoplanet Archive  
- Fictional political and economic data for immersive worldbuilding

## Performance

- In-memory data caching for fast API responses
- Optimized 3D rendering with WebGL acceleration
- Efficient filtering and search algorithms
- Minimal dependencies for quick startup