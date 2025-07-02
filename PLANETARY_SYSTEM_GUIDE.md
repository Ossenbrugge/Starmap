# Planetary System Mini-Map Guide

## Overview
The Starmap application now includes interactive planetary system visualization for stars with known or theoretical exoplanets.

## Current Systems Available

### 1. Sol (Our Solar System)
- **8 planets**: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune
- **Status**: All confirmed with precise astronomical data
- **Features**: Complete orbital data, habitable zone display, logarithmic size scaling

### 2. Proxima Centauri System
- **3 planets**: Proxima b, c, d  
- **Status**: All confirmed exoplanets
- **Features**: Nearest exoplanet system to Earth

### 3. Epsilon Eridani System  
- **1 planet**: Epsilon Eridani b
- **Status**: Confirmed gas giant
- **Features**: Real exoplanet discovery from 2000

### 4. Alpha Centauri A System
- **1 planet**: Alpha Centauri Ab
- **Status**: Theoretical/candidate
- **Features**: Potential habitable world

### 5. Sirius System
- **1 planet**: Sirius Ab  
- **Status**: Hypothetical hot Jupiter
- **Features**: Demonstration of extreme conditions

### 6. Tau Ceti System
- **2 planets**: Tau Ceti e, f
- **Status**: Candidate super-Earths
- **Features**: Potentially habitable candidates

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

### James Webb Telescope Integration
When new exoplanets are discovered:

1. **Update** the planet_systems dictionary in `app_simple.py`
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
1. Search "Sol" → Click result → Click "🌌 System View"
2. Click "▶️ Start Animation" to see orbital motion
3. Click on Earth or Mars to highlight them
4. Try "Proxima" to see real exoplanet data
5. Test "Epsilon Eridani" for a gas giant example

### Expected Behavior
- ✅ **Labels**: Planet names display properly (not %{text})
- ✅ **Animation**: Planets orbit smoothly when started
- ✅ **Hover**: Detailed info appears on mouse over
- ✅ **Clicking**: Planets highlight in both map and list
- ✅ **Habitable Zone**: Green circles for Sol system

This system provides a foundation for incorporating future exoplanet discoveries and serves as an excellent tool for science fiction world-building!