"""
Galactic Cardinal Direction Markers for Starmap
Provides cardinal direction markers to help users visualize the starmap within the Milky Way galaxy.
"""

import math
import numpy as np

# Galactic coordinate system constants
GALACTIC_CENTER_RA = 266.4051  # Right ascension of galactic center (J2000)
GALACTIC_CENTER_DEC = -28.9362  # Declination of galactic center (J2000)
GALACTIC_NORTH_POLE_RA = 192.8595  # Right ascension of galactic north pole (J2000)
GALACTIC_NORTH_POLE_DEC = 27.1284  # Declination of galactic north pole (J2000)

def deg_to_rad(degrees):
    """Convert degrees to radians"""
    return degrees * math.pi / 180

def galactic_to_equatorial(l, b):
    """
    Convert galactic coordinates (l, b) to equatorial (RA, Dec)
    l: galactic longitude in degrees
    b: galactic latitude in degrees
    Returns: (RA, Dec) in degrees
    """
    # Convert to radians
    l_rad = deg_to_rad(l)
    b_rad = deg_to_rad(b)
    
    # Galactic coordinate system transformation constants
    l_ncp = deg_to_rad(122.932)  # Galactic longitude of north celestial pole
    ra_ngp = deg_to_rad(GALACTIC_NORTH_POLE_RA)  # RA of north galactic pole
    dec_ngp = deg_to_rad(GALACTIC_NORTH_POLE_DEC)  # Dec of north galactic pole
    
    # Transformation to equatorial coordinates
    sin_dec = math.sin(b_rad) * math.sin(dec_ngp) + math.cos(b_rad) * math.cos(dec_ngp) * math.sin(l_rad - l_ncp)
    dec = math.asin(sin_dec)
    
    cos_ra_diff = (math.cos(l_rad - l_ncp) * math.cos(b_rad)) / math.cos(dec)
    sin_ra_diff = (math.sin(dec_ngp) * math.cos(b_rad) * math.sin(l_rad - l_ncp) - math.sin(b_rad) * math.cos(dec_ngp)) / math.cos(dec)
    
    ra = ra_ngp + math.atan2(sin_ra_diff, cos_ra_diff)
    
    # Convert back to degrees
    ra_deg = ra * 180 / math.pi
    dec_deg = dec * 180 / math.pi
    
    # Normalize RA to 0-360 range
    if ra_deg < 0:
        ra_deg += 360
    
    return ra_deg, dec_deg

def equatorial_to_cartesian(ra, dec, distance=50):
    """
    Convert equatorial coordinates to Cartesian coordinates
    ra: right ascension in degrees
    dec: declination in degrees  
    distance: distance in parsecs (default 50 pc for visualization)
    Returns: (x, y, z) in parsecs
    """
    # Convert to radians
    ra_rad = deg_to_rad(ra)
    dec_rad = deg_to_rad(dec)
    
    # Calculate Cartesian coordinates
    x = distance * math.cos(dec_rad) * math.cos(ra_rad)
    y = distance * math.cos(dec_rad) * math.sin(ra_rad)
    z = distance * math.sin(dec_rad)
    
    return x, y, z

def get_galactic_cardinal_markers(distance=50):
    """
    Get galactic cardinal direction markers for visualization
    distance: distance from origin in parsecs for marker placement
    Returns: list of marker dictionaries
    """
    markers = []
    
    # Define galactic cardinal directions
    directions = [
        {
            'name': 'Coreward',
            'description': 'Toward the galactic center (Sagittarius)',
            'galactic_l': 0,
            'galactic_b': 0,
            'color': '#FFD700',  # Gold
            'symbol': '⚫'
        },
        {
            'name': 'Spinward',
            'description': 'Toward galactic rotation (Cygnus)',
            'galactic_l': 90,
            'galactic_b': 0,
            'color': '#00CED1',  # Dark Turquoise
            'symbol': '🌀'
        },
        {
            'name': 'Rimward',
            'description': 'Toward the galactic rim (Gemini/Auriga)',
            'galactic_l': 180,
            'galactic_b': 0,
            'color': '#FF6347',  # Tomato
            'symbol': '🌌'
        },
        {
            'name': 'Anti-Spinward',
            'description': 'Opposite galactic rotation (Vela)',
            'galactic_l': 270,
            'galactic_b': 0,
            'color': '#9370DB',  # Medium Purple
            'symbol': '🔄'
        },
        {
            'name': 'Driftward',
            'description': 'Above galactic plane (Galactic North, Coma Berenices)',
            'galactic_l': 0,
            'galactic_b': 90,
            'color': '#32CD32',  # Lime Green
            'symbol': '⬆️'
        },
        {
            'name': 'Anti-Driftward',
            'description': 'Below galactic plane (Galactic South, Sculptor)',
            'galactic_l': 0,
            'galactic_b': -90,
            'color': '#FFA500',  # Orange
            'symbol': '⬇️'
        }
    ]
    
    for direction in directions:
        # Convert galactic to equatorial coordinates
        ra, dec = galactic_to_equatorial(direction['galactic_l'], direction['galactic_b'])
        
        # Convert to Cartesian coordinates
        x, y, z = equatorial_to_cartesian(ra, dec, distance)
        
        # Create marker
        marker = {
            'name': direction['name'],
            'description': direction['description'],
            'galactic_l': direction['galactic_l'],
            'galactic_b': direction['galactic_b'],
            'ra': ra,
            'dec': dec,
            'x': x,
            'y': y,
            'z': z,
            'color': direction['color'],
            'symbol': direction['symbol'],
            'type': 'galactic_cardinal'
        }
        
        markers.append(marker)
    
    return markers

def get_galactic_coordinate_grid(distance=50, grid_spacing=30):
    """
    Get a grid of galactic coordinate markers for enhanced visualization
    distance: distance from origin in parsecs
    grid_spacing: spacing between grid lines in degrees
    Returns: list of grid line points
    """
    grid_points = []
    
    # Create longitude grid lines (l = constant)
    for l in range(0, 360, grid_spacing):
        points = []
        for b in range(-90, 91, 10):
            ra, dec = galactic_to_equatorial(l, b)
            x, y, z = equatorial_to_cartesian(ra, dec, distance)
            points.append([x, y, z])
        grid_points.append({
            'type': 'longitude_line',
            'galactic_l': l,
            'points': points,
            'color': '#444444'
        })
    
    # Create latitude grid lines (b = constant)
    for b in range(-60, 61, 30):
        if b == 0:
            continue  # Skip galactic equator, will be handled separately
        points = []
        for l in range(0, 360, 10):
            ra, dec = galactic_to_equatorial(l, b)
            x, y, z = equatorial_to_cartesian(ra, dec, distance)
            points.append([x, y, z])
        grid_points.append({
            'type': 'latitude_line',
            'galactic_b': b,
            'points': points,
            'color': '#444444'
        })
    
    # Special handling for galactic equator (b = 0)
    equator_points = []
    for l in range(0, 360, 5):
        ra, dec = galactic_to_equatorial(l, 0)
        x, y, z = equatorial_to_cartesian(ra, dec, distance)
        equator_points.append([x, y, z])
    grid_points.append({
        'type': 'galactic_equator',
        'galactic_b': 0,
        'points': equator_points,
        'color': '#666666'
    })
    
    return grid_points

if __name__ == "__main__":
    # Test the functions
    markers = get_galactic_cardinal_markers()
    print("Galactic Cardinal Direction Markers:")
    for marker in markers:
        print(f"{marker['name']}: ({marker['x']:.2f}, {marker['y']:.2f}, {marker['z']:.2f})")
        print(f"  Galactic: l={marker['galactic_l']}°, b={marker['galactic_b']}°")
        print(f"  Equatorial: RA={marker['ra']:.2f}°, Dec={marker['dec']:.2f}°")
        print()