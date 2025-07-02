<<<<<<< HEAD
# Starmap - Interactive 3D Star Viewer

A Python-based web application for creating interactive 3D starmaps for science fiction novels. This application provides a local web interface to explore star data, view star systems with planetary information, and export maps for your creative projects.

## Features

- **Interactive 3D Visualization**: Navigate through space with a fully interactive 3D starmap
- **Star Information**: Click on any star to view detailed information including:
  - Magnitude, spectral class, distance
  - Coordinates and proper motion
  - Constellation information
- **Planetary Systems**: View planetary data for select star systems
- **Export Functionality**: Generate PDF reports of star data
- **Local & LAN Access**: Run locally or share on your local network
- **Customizable Views**: Filter stars by magnitude and adjust display settings

## Quick Start

1. **Setup Environment**:
   ```bash
   python setup.py
   ```

2. **Activate Virtual Environment**:
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Run Application**:
   ```bash
   python app.py
   ```

4. **Access Application**:
   - Local: http://localhost:5000
   - LAN: http://[your-ip]:5000

## Data Source

The application uses `stars_output.csv` which should contain star data with columns:
- `id`, `proper` (name), `x`, `y`, `z` (coordinates)
- `mag` (magnitude), `spect` (spectral class), `dist` (distance)
- `con` (constellation), and other astronomical data

## Application Structure

```
Starmap/
├── app.py              # Main Flask application
├── database.py         # MongoDB database operations
├── start_mongodb.py    # MongoDB startup script
├── setup.py           # Environment setup
├── requirements.txt   # Python dependencies
├── stars_output.csv   # Star data (your file)
├── templates/
│   └── starmap.html   # Web interface template
├── static/
│   ├── css/style.css  # Application styles
│   └── js/starmap.js  # Interactive functionality
└── venv/              # Virtual environment
```

## Usage

### Basic Navigation

1. **Load Stars**: Click "Update Starmap" to load the initial view
2. **Navigate**: Use mouse to rotate, zoom, and pan the 3D view
3. **Filter Stars**: Adjust magnitude limit and star count sliders
4. **Click Stars**: Click any star to view detailed information
5. **Export**: Generate PDF reports of your starmap data

### Controls

- **Magnitude Limit**: Show only stars brighter than this value
- **Max Stars**: Limit the number of stars displayed for performance
- **Reset View**: Return to the default camera position
- **Export PDF**: Generate a printable report

### LAN Access

To access from other devices on your network:

1. Find your computer's IP address:
   ```bash
   # macOS/Linux
   ifconfig | grep inet
   
   # Windows
   ipconfig
   ```

2. Other devices can access: `http://[your-ip]:5000`

## Customization

### Adding Planetary Systems

Edit `app.py` to add more planetary systems in the `add_sample_planets()` method:

```python
planet_systems = {
    star_id: [
        {
            "name": "Planet Name",
            "type": "Planet Type",
            "distance_au": 1.0,
            "mass_earth": 1.0
        }
    ]
}
```

### Database Integration

For full MongoDB integration:

1. Install MongoDB locally
2. Run `python start_mongodb.py` to start the database
3. Use `database.py` functions for advanced data operations

## Dependencies

- Flask 3.0.0 - Web framework
- Plotly 5.17.0 - 3D visualization
- Pandas 2.2.0 - Data manipulation
- PyMongo 4.6.1 - MongoDB integration
- WeasyPrint 61.2 - PDF generation

## Performance Notes

- The application limits display to 2000 stars for optimal performance
- Adjust the star count slider for better performance on slower devices
- PDF exports are limited to the brightest 100 stars by default

## Troubleshooting

1. **CSV Not Found**: Ensure `stars_output.csv` is in the root directory
2. **Module Errors**: Activate the virtual environment before running
3. **Slow Performance**: Reduce the star count or magnitude limit
4. **LAN Access Issues**: Check firewall settings and IP address

## License

This project is designed for personal and educational use in science fiction writing and world-building.
=======
- 👋 Hi, I’m @Ossenbrugge
- 👀 I’m interested in Python, Java, FabricMC Modding
- 📫 How to reach me - Here or on Discord@ossenbrugge_79788

<!---
Ossenbrugge/Ossenbrugge is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->
>>>>>>> 4a7454939e43d929ecc4c796edd448011ded1e67
