# Galactic Directions Guide

Complete documentation for the galactic coordinate system, navigation overlays, and directional indicators in the Starmap application.

📖 **[← Back to Main Documentation](README.md#-documentation-hub)**

## Overview
The Galactic Directions feature helps users visualize the starmap's orientation within the Milky Way galaxy by providing cardinal direction markers and coordinate grids based on galactic coordinates.

## Cardinal Directions

### Primary Directions
- **Coreward** (🔴 Gold): Toward the galactic center (Sagittarius, l ≈ 0°)
- **Rimward** (🔴 Tomato): Toward the galactic rim (Gemini/Auriga, l ≈ 180°)
- **Spinward** (🔵 Dark Turquoise): Toward galactic rotation (Cygnus, l ≈ 90°)
- **Anti-Spinward** (🟣 Medium Purple): Opposite galactic rotation (Vela, l ≈ 270°)

### Vertical Directions
- **Driftward** (🟢 Lime Green): Above the galactic plane (Galactic North, b > 0°, toward Coma Berenices)
- **Anti-Driftward** (🟠 Orange): Below the galactic plane (Galactic South, b < 0°, toward Sculptor)

## Controls

### UI Elements
- **Show Cardinal Directions**: Toggle visibility of the 6 cardinal direction markers
- **Show Galactic Grid**: Toggle visibility of galactic coordinate grid lines
- **Distance Slider**: Adjust marker placement distance (25-100 parsecs from origin)

### Features
- Markers use distinctive diamond symbols with directional icons
- Hover tooltips show galactic coordinates and descriptions
- Grid lines show galactic longitude and latitude references
- Galactic equator is highlighted with a solid line
- Other grid lines use dashed styling

## Technical Implementation

### Coordinate System
- Uses standard galactic coordinate system (l, b)
- Converts galactic coordinates to equatorial (RA, Dec)
- Transforms to Cartesian coordinates for 3D visualization
- Origin represents Sol (our solar system)

### API Endpoints
- `GET /api/galactic-directions`: Fetch cardinal markers
- Parameters:
  - `distance`: Marker placement distance in parsecs (default: 50)
  - `grid`: Include coordinate grid lines (default: false)

### Files
- `galactic_directions.py`: Core calculation module
- `app.py`: Flask API endpoints
- `starmap.js`: JavaScript visualization functions
- `starmap.html`: UI controls

## Usage in Science Fiction Context

This feature helps authors and worldbuilders:
1. **Orient their fictional star systems** within the galaxy
2. **Plan interstellar travel routes** using galactic directions
3. **Describe locations** using standard galactic terminology
4. **Visualize galactic-scale conflicts** and territories
5. **Understand the relationship** between their fictional systems and real astronomical features

## Astronomical Accuracy

The coordinate transformations use standard astronomical constants:
- Galactic center: RA 266.4°, Dec -28.9° (J2000)
- Galactic north pole: RA 192.9°, Dec 27.1° (J2000)
- Follows IAU galactic coordinate system conventions

This ensures the directions accurately represent real galactic orientation for scientifically-grounded fiction.

## Related Documentation

- **[📖 Main Documentation](README.md)** - Complete application overview and user interface guide
- **[🪐 Planetary System Guide](PLANETARY_SYSTEM_GUIDE.md)** - Detailed planetary systems and world-building
- **[🛣️ Trade Routes Guide](TRADE_ROUTES_README.md)** - Trade network structure and economic zones
- **[🌌 Universe Overview](README.md#-the-felgenland-saga-universe)** - Political entities and trade networks
- **[🔌 API Reference](README.md#-api-reference)** - Complete backend API documentation
- **[📊 Data Analysis Report](PLANETARY_SYSTEMS_ANALYSIS.md)** - System verification and data quality

---
📖 **[← Back to Main Documentation](README.md#-documentation-hub)**