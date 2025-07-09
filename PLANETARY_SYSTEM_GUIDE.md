# Planetary System Guide

A comprehensive guide to planetary systems in the Starmap application, including how to add new worlds and configure orbital parameters.

📖 **[← Back to Main Documentation](README.md#-documentation-hub)**

## Overview
The Starmap application includes interactive planetary system visualization for stars with known or theoretical exoplanets, featuring detailed system minimaps and planetary data.

## Current Systems Available

The Starmap includes 6 detailed planetary systems with comprehensive data. These systems combine real astronomical data with fictional worlds for the Felgenland Saga:

### 1. Holsten Tor System (20 Leonis Minoris)
- **Real Star**: 20 Leonis Minoris A, 15.05 light years away
- **Planets**: 5 total (1 confirmed, 4 fictional)
- **Fictional Worlds**: Capital of Felgenland Union
- **Features**: Trading hub with industrial worlds

### 2. Griefen Tor System (55 Cancri) 
- **Real Star**: 55 Cancri (Copernicus), 12.34 light years away
- **Planets**: 6 total (5 confirmed, 1 fictional)
- **Fictional Worlds**: Resource extraction center
- **Features**: Mining operations and confirmed exoplanets

### 3. Brandenburgh Tor System (11 Leonis Minoris)
- **Real Star**: 11 Leonis Minoris, 11.37 light years away  
- **Planets**: 4 fictional worlds
- **Fictional Worlds**: Border fortress system
- **Features**: Gateway to outer territories

### 4. Tiefe-Grenze Tor System (Fictional)
- **Fictional Star**: Rimward trading hub
- **Planets**: 4 fictional worlds
- **Features**: Deep frontier trade center
- **Status**: Completely fictional system

### 5. Protelan System (61 Ursae Majoris)
- **Real Star**: 61 UMa, 9.61 light years away
- **Planets**: 6 fictional worlds including Protelan moon
- **Fictional Worlds**: Ultra-capitalist republic capital
- **Features**: Corporate trade hub with unique culture

### 6. Fomalhaut System (α Piscis Austrini)
- **Real Star**: Fomalhaut, 7.70 light years away
- **Planets**: 4 total (1 confirmed, 3 fictional)
- **Fictional Worlds**: Dorsai Republic military center
- **Features**: Elite military training facility

## How to Use

### Accessing System View
1. **Search** for a star with planets (Sol, Proxima, etc.)
2. **Click** the star result to select it
3. **Click** the "🌌 System View" button in the planet panel
4. The **modal** opens showing the orbital map

### Interactive Features

#### Orbital Map
- **Green dotted circles**: Habitable zone boundaries
- **White circles**: Orbital paths  
- **Colored dots**: Planets (color-coded by type)
- **Yellow star**: Central star
- **Hover**: Shows detailed planet information

#### Animation
- **▶️ Start Animation**: Begins orbital motion
- **⏸️ Stop Animation**: Pauses the animation
- **Physics**: Uses Kepler's laws (inner planets move faster)

#### Planet Selection
- **Click planets** on the map to highlight them
- **Click planet cards** in the side panel
- **Highlighting** shows in both map and list

### Planet Information
Each planet shows:
- **Name** and discovery year
- **Type** (Terrestrial, Gas Giant, etc.)
- **Distance** from star in AU
- **Mass** compared to Earth  
- **Orbital period** in Earth days
- **Confirmation status** (Confirmed/Candidate)
- **Habitable zone** indication

## Adding New Exoplanets

### Manual Addition (via API)
```javascript
// Example: Add a new planet to Sirius
fetch('/api/planet/add', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        star_id: 32263, // Sirius ID
        planet: {
            name: "Sirius Ab-2",
            type: "Hot Jupiter", 
            distance_au: 0.15,
            mass_earth: 200,
            radius_earth: 4.5,
            orbital_period_days: 25,
            temperature_k: 1000,
            atmosphere: "H2, He",
            discovery_year: "2024",
            confirmed: true
        }
    })
});
```

### Adding New Exoplanet Systems
When new exoplanets are discovered:

1. **Update** the `fictional_planets.py` file with new systems
2. **Add** comprehensive data including:
   - Physical characteristics
   - Orbital parameters  
   - Atmospheric composition
   - Discovery details
3. **Restart** the application to load new data

## Planet Types and Colors

- **Terrestrial**: Brown (#8B4513) - Rocky planets like Earth, Mars
- **Super-Earth**: Green (#228B22) - Large rocky planets (1.25-2× Earth)  
- **Sub-Earth**: Tan (#CD853F) - Small rocky planets (<0.8× Earth)
- **Gas Giant**: Orange (#FF4500) - Jupiter and Saturn-like planets
- **Hot Jupiter**: Red (#FF6347) - Close-in gas giants
- **Ice Giant**: Blue (#4169E1) - Uranus and Neptune-like planets
- **Neptune-like**: Dark Blue (#0000CD) - Neptune analogs
- **Unknown**: Gray (#696969) - Unclassified planets

## Improved Size Scaling

The mini-map now uses **logarithmic scaling** for large planets to ensure proportional display:

- **Linear scaling** for planets < 5× Earth radius
- **Logarithmic scaling** for gas giants and ice giants  
- **Maximum size limit** prevents Jupiter from overwhelming the display
- **Minimum size guarantee** ensures small planets remain visible

### Size Examples:
- Mercury: 0.38× Earth → Small brown dot
- Earth: 1.0× Earth → Standard reference size
- Jupiter: 11.0× Earth → Large but proportional orange dot
- Saturn: 9.1× Earth → Slightly smaller than Jupiter
- Uranus: 4.0× Earth → Medium blue dot
- Neptune: 3.9× Earth → Similar to Uranus

## Habitable Zone
- **Inner boundary**: 0.95 AU (Venus-like conditions)
- **Outer boundary**: 1.37 AU (Mars-like conditions)  
- **Indication**: Green dotted circles on map
- **Badge**: Blue "Habitable Zone" badge on qualifying planets

## Testing the System

### Quick Test Steps
1. Search "Holsten Tor" → Click result → Click "🌌 System View"
2. Click "▶️ Start Animation" to see orbital motion
3. Click on planets to highlight them
4. Try "Griefen Tor" to see real exoplanet data from 55 Cancri
5. Test "Protelan" to see the ultra-capitalist republic system

### Expected Behavior
- ✅ **Labels**: Planet names display properly (not %{text})
- ✅ **Animation**: Planets orbit smoothly when started
- ✅ **Hover**: Detailed info appears on mouse over
- ✅ **Clicking**: Planets highlight in both map and list
- ✅ **Habitable Zone**: Green circles for Sol system

This system provides a foundation for incorporating future exoplanet discoveries and serves as an excellent tool for science fiction world-building!

## Related Documentation

- **[📖 Main Documentation](README.md)** - Complete application overview and quick start
- **[🧭 Galactic Directions Guide](GALACTIC_DIRECTIONS.md)** - Coordinate systems and navigation overlays
- **[🛣️ Trade Routes Guide](TRADE_ROUTES_README.md)** - Trade network structure and economic zones
- **[🌌 Universe Overview](README.md#-the-felgenland-saga-universe)** - Political entities and trade networks
- **[🔌 API Reference](README.md#-api-reference)** - Backend API for planetary system data
- **[📊 Data Analysis Report](PLANETARY_SYSTEMS_ANALYSIS.md)** - System verification and data quality

---
📖 **[← Back to Main Documentation](README.md#-documentation-hub)**