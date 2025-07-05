# Starmap: A Picture of the Felgenland Saga

An interactive 3D starmap application for science fiction world-building, featuring political overlays, planetary systems, and trade route visualization. Built with Flask and designed specifically for the Felgenland Saga universe.

## 🌟 Features

### Core Functionality
- **Interactive 3D Visualization**: Navigate through space with a fully interactive 3D starmap using Plotly.js
- **Political Overlays**: Visualize fictional nations, territories, borders, and trade routes
- **Planetary Systems**: Detailed planetary data with interactive system minimaps
- **Distance Measurement**: Measure distances between star systems
- **Galactic Navigation**: Grid overlays and directional indicators
- **Multi-format Export**: Export maps as PNG, JPG, or PDF

### Star Information
- Magnitude, spectral class, distance from Sol
- Coordinates and proper motion data
- Constellation information
- Fictional names and descriptions
- Nation allegiance and political data

### User Interface
- **Single-window Layout**: Floating overlay panels for optimal screen usage
- **Collapsible Controls**: Magnitude scales, overlays, and tools
- **Real-time Data**: Live star information and planetary system details
- **Responsive Design**: Works on desktop and tablet devices

## 📖 Documentation Hub

### Quick Start Guides
- **[Installation & Setup](#-quick-start)** - Get started immediately
- **[User Interface Guide](#-user-interface)** - Navigate the starmap interface

### Detailed Documentation
- **[Planetary System Guide](PLANETARY_SYSTEM_GUIDE.md)** - Complete guide to planetary systems, including how to add new worlds and moons
- **[Galactic Directions Guide](GALACTIC_DIRECTIONS.md)** - Coordinate systems, galactic grid, and navigation overlays

### Technical References
- **[Application Structure](#-application-structure)** - MVC architecture overview
- **[Data Files](#-data-files)** - Understanding the data sources
- **[API Endpoints](#-api-endpoints)** - Backend API reference

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Web browser (Chrome, Firefox, Safari, or Edge)

### Installation

1. **Clone or download this repository**

2. **Set up the virtual environment**:
   ```bash
   # Make the setup script executable and run it
   chmod +x activate_venv.sh
   ./activate_venv.sh
   ```

3. **Run the application**:
   ```bash
   # Using the provided script
   chmod +x run_starmap.sh
   ./run_starmap.sh
   
   # Or run directly
   python app.py
   ```

4. **Access the application**:
   - **Local**: http://localhost:8080
   - **LAN**: http://[your-ip]:8080

### First Steps
1. Click "Update" to load the starmap
2. Use mouse to rotate, zoom, and pan the 3D view
3. Click on stars to view detailed information
4. Try the political overlays to see fictional nations
5. Enable trade routes to see economic connections

## 🎮 User Interface

### Main Controls Panel (Left)
- **Basic Settings**: Magnitude limits, star count, search
- **Spectral Filtering**: Filter by star type (O, B, A, F, G, K, M)
- **Tools**: Distance measurement, nation legend
- **Overlays**: Nations, borders, trade routes, galactic grid

### Data Panel (Right)
- **Star Information**: Complete star data and properties
- **Planetary Systems**: Planet details with system minimap access
- **Search Results**: Star search and filtering results
- **Distance Results**: Measurements between star systems

### Bottom Controls
- **Panel Toggles**: Show/hide control and data panels
- **Export Options**: Include/exclude UI in exported images

### Overlays System
- **Nations**: Show political control of star systems
- **Borders**: Territory boundaries around controlled systems  
- **Trade Routes**: Economic connections between systems
- **Galactic Grid**: Coordinate reference system
- **Directions**: Galactic navigation indicators

*Note: Trade routes automatically enable the nations overlay as they depend on political data.*

## 🏗️ Application Structure

```
Starmap/
├── app.py                  # Main Flask application (MVC orchestration)
├── requirements.txt        # Python dependencies
├── run_starmap.sh         # Application launcher
├── activate_venv.sh       # Virtual environment setup
│
├── models/                # Data layer (MVC)
│   ├── star_model.py     # Star data management
│   ├── planet_model.py   # Planetary system data
│   ├── nation_model.py   # Political entity data
│   └── base_model.py     # Base model class
│
├── views/                 # Presentation layer (MVC)
│   └── api_views.py      # JSON API and template rendering
│
├── controllers/           # Business logic (MVC)
│   ├── star_controller.py    # Star operations
│   ├── planet_controller.py  # Planetary system operations
│   ├── nation_controller.py  # Political data operations
│   ├── map_controller.py     # Galactic mapping operations
│   └── base_controller.py    # Base controller class
│
├── templates/
│   └── starmap.html      # Main application interface
│
├── static/
│   ├── css/style.css     # Application styles
│   └── js/
│       ├── starmap.js    # Main application logic
│       └── planetary_system.js  # System minimap functionality
│
└── data files (see below)
```

## 📊 Data Files

### Core Star Data
- **`stars_output.csv`** - Real astronomical star catalog (24,670+ stars)
- **`fictional_stars.csv`** - Fictional star additions for the saga
- **`star_naming.py`** - Star naming and designation system

### Science Fiction World Data
- **`nations_data.json`** - Political entities, trade routes, economic zones
- **`fictional_names.py`** - Fictional star system names and descriptions
- **`fictional_planets.py`** - Planetary systems with detailed world data
- **`fictional_nations.py`** - Political entity management functions

### Galactic Systems
- **`galactic_directions.py`** - Coordinate systems and navigation
- **`GALACTIC_DIRECTIONS.md`** - Documentation for galactic coordinate system

## 🌍 The Felgenland Saga Universe

This starmap visualizes the political landscape of the Felgenland Saga:

### Major Powers
- **🔵 Terran Directorate** - Earth-based authoritarian republic (Blue)
- **🟢 Felgenland Union** - Rimward trade federation (Green)  
- **🟣 Protelani Republic** - Ultra-capitalist corporate state (Purple)
- **🔴 Dorsai Republic** - Elite military training systems (Red)

### Key Features
- **Political Borders**: Territorial spheres around controlled systems
- **Trade Networks**: Economic routes connecting allied systems
- **Strategic Systems**: Capital worlds and important installations
- **Fictional Worlds**: Custom planetary systems with detailed descriptions

## 🔌 API Endpoints

The application provides a RESTful API for accessing starmap data:

### Star Data
- `GET /api/stars` - Get filtered star list
- `GET /api/star/<id>` - Get detailed star information
- `GET /api/search?q=<query>` - Search stars by name
- `GET /api/distance?star1=<id>&star2=<id>` - Calculate distances

### Political Data  
- `GET /api/nations` - Get all political entities
- `GET /api/nation/<id>` - Get nation details
- `GET /api/trade-routes` - Get trade route networks

### Planetary Systems
- `GET /api/systems` - Get all planetary systems
- `GET /api/system/<star_id>` - Get planetary system details

### Galactic Navigation
- `GET /api/galactic-directions` - Get galactic coordinate overlays

## 🛠️ Customization

### Adding New Star Systems
See **[Planetary System Guide](PLANETARY_SYSTEM_GUIDE.md)** for detailed instructions on:
- Creating new planetary systems
- Adding moons to planets
- Configuring orbital parameters
- Setting up fictional worlds

### Political Modifications
Edit `nations_data.json` to:
- Add new political entities
- Create trade routes
- Define territorial boundaries
- Configure economic zones

### Galactic Features
Modify `galactic_directions.py` for:
- Custom coordinate systems
- Navigation overlays  
- Galactic grid configurations

## 📋 System Requirements

### Server Requirements
- **Python**: 3.8 or higher
- **Memory**: 512MB RAM minimum (1GB recommended)
- **Storage**: 50MB for application + star data
- **Network**: Port 8080 (configurable)

### Client Requirements
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **JavaScript**: Must be enabled
- **WebGL**: Required for 3D visualization
- **Memory**: 1GB RAM recommended for large star datasets

## 🔧 Troubleshooting

### Common Issues

**1. Application Won't Start**
```bash
# Check Python version
python --version  # Should be 3.8+

# Verify virtual environment
source starmap_venv/bin/activate
pip list | grep -E "(Flask|plotly|pandas)"
```

**2. Star Data Not Loading**
- Ensure `stars_output.csv` is in the root directory
- Check file permissions and encoding (should be UTF-8)
- Look for error messages in the console

**3. Slow Performance**
- Reduce star count in magnitude controls
- Lower magnitude limit to show fewer stars
- Close other browser tabs to free memory

**4. Network Access Issues**
```bash
# Find your IP address
# macOS/Linux:
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows:  
ipconfig | findstr "IPv4"
```

**5. Political Overlays Not Working**
- Check browser console for JavaScript errors
- Ensure `nations_data.json` is valid JSON
- Verify Flask app loaded nations data successfully

### Performance Optimization

**For Large Datasets (>10,000 stars):**
- Set magnitude limit to 6.0 or lower
- Limit star count to 1000 or fewer
- Disable overlays when not needed
- Use Chrome or Firefox for better WebGL performance

**For Network Sharing:**
- Check firewall settings for port 8080
- Ensure devices are on the same network
- Use static IP address if possible

## 📄 License

This project is designed for personal and educational use in science fiction writing and world-building. See [LICENSE](LICENSE) for full terms.

## 🤝 Contributing

This is a specialized tool for the Felgenland Saga universe. If you're interested in creating your own science fiction starmap:

1. Fork this repository
2. Modify the data files for your universe  
3. Update the political entities and trade routes
4. Customize the planetary systems
5. Share your creation!

---

**Ready to explore the galaxy?** Start with the [Quick Start](#-quick-start) guide or dive into the [Planetary System Guide](PLANETARY_SYSTEM_GUIDE.md) to begin building your own worlds.