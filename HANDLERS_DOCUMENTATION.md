# Starmap Handlers Documentation

## 📖 Overview

The Starmap application includes a comprehensive set of handlers for managing fictional entities in the universe. These handlers provide a clean, organized way to add, modify, and delete fictional stars, exoplanets, nations, and trade routes while maintaining data integrity and consistency.

## 🔗 Documentation Navigation

- **[README.md](README.md)** - Main project overview with quick API examples
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete REST API documentation
- **[DATA_MANAGEMENT_GUIDE.md](DATA_MANAGEMENT_GUIDE.md)** - Data management workflows and comparison
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development setup and testing
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation hub

## 🗂️ Handler Architecture

All handlers are organized in the `/handlers/` directory with a modular structure:

```
handlers/
├── __init__.py              # Package initialization and exports
├── star_handler.py          # Fictional star management
├── exoplanet_handler.py     # Fictional exoplanet management  
├── nation_handler.py        # Fictional nation management
└── trade_route_handler.py   # Fictional trade route management
```

Each handler follows the same pattern:
- **Validation** of required fields and data integrity
- **Cross-reference checking** to ensure related entities exist
- **Automatic calculation** of derived properties (coordinates, distances, etc.)
- **File management** for both JSON and CSV formats
- **Error handling** with detailed messages

---

## 🌟 Star Handler (`star_handler.py`)

### Purpose
Manages fictional star systems, including validation, coordinate calculation, and data persistence.

### Key Features
- **3D Coordinate Calculation**: Automatically converts RA/Dec/Distance to X/Y/Z coordinates
- **Absolute Magnitude Calculation**: Derives absolute magnitude from apparent magnitude and distance
- **Unique ID Generation**: Creates fictional star IDs starting from 999999 and counting down
- **CSV and JSON Support**: Updates both fictional_stars.csv and stars.json cache

### Methods

#### `add_fictional_star(star_data)`
Adds a new fictional star to the system.

**Required Fields:**
- `name`: Star name (string)
- `ra`: Right ascension in degrees (float)
- `dec`: Declination in degrees (float) 
- `dist`: Distance in parsecs (float)
- `mag`: Apparent magnitude (float)
- `spect`: Spectral type (string)

**Optional Fields:**
- `description`: Star description (string)
- `pmra`, `pmdec`: Proper motion (float)
- `rv`: Radial velocity (float)
- `ci`: Color index (float)
- `lum`: Luminosity (float)
- `var`: Variable star designation (string)

**Example Usage:**
```python
from handlers import StarHandler

handler = StarHandler()
result = handler.add_fictional_star({
    "name": "Alpha Proximi",
    "ra": 214.75,
    "dec": -62.5,
    "dist": 4.24,
    "mag": 11.1,
    "spect": "M5V",
    "description": "Red dwarf companion to Proxima Centauri"
})

if result['success']:
    print(f"Added star with ID: {result['data']['id']}")
else:
    print(f"Error: {result['error']}")
```

#### `get_fictional_stars()`
Returns all fictional stars from the CSV file.

#### `delete_fictional_star(star_id)`
Removes a fictional star by ID.

**Coordinate Calculation Formula:**
```python
x = dist * cos(dec_rad) * cos(ra_rad)
y = dist * cos(dec_rad) * sin(ra_rad)
z = dist * sin(dec_rad)
```

---

## 🪐 Exoplanet Handler (`exoplanet_handler.py`)

### Purpose
Manages fictional exoplanets orbiting stars in the system, with automatic host star validation and habitability assessment.

### Key Features
- **Host Star Validation**: Ensures the host star exists in either real or fictional star databases
- **Automatic Classification**: Determines planet type based on radius/mass
- **Habitability Assessment**: Calculates whether the planet is potentially habitable
- **Equilibrium Temperature**: Estimates planet temperature based on stellar properties
- **Habitable Zone Calculation**: Determines the star's habitable zone boundaries

### Methods

#### `add_fictional_exoplanet(exoplanet_data)`
Adds a new fictional exoplanet to the system.

**Required Fields:**
- `name`: Planet name (string)
- `host_star_id`: ID of the host star (integer)
- `orbital_period_days`: Orbital period in days (float)
- `semi_major_axis_au`: Semi-major axis in AU (float)

**Optional Fields:**
- `radius_earth`: Planet radius in Earth radii (float)
- `radius_jupiter`: Planet radius in Jupiter radii (float)
- `mass_earth`: Planet mass in Earth masses (float) 
- `mass_jupiter`: Planet mass in Jupiter masses (float)
- `orbital_eccentricity`: Orbital eccentricity (float)
- `orbital_inclination`: Orbital inclination in degrees (float)
- `description`: Planet description (string)
- `planet_type`: Override automatic classification (string)
- `habitability_score`: Custom habitability score (float)
- `atmosphere`: Atmospheric description (string)
- `surface_description`: Surface features (string)
- `population`: Population count (integer)
- `government_type`: Governmental system (string)

**Example Usage:**
```python
from handlers import ExoplanetHandler

handler = ExoplanetHandler()
result = handler.add_fictional_exoplanet({
    "name": "New Terra",
    "host_star_id": 999999,
    "orbital_period_days": 387.2,
    "semi_major_axis_au": 1.15,
    "radius_earth": 1.08,
    "mass_earth": 1.12,
    "description": "A promising world for colonization",
    "atmosphere": "Nitrogen-oxygen with traces of noble gases",
    "population": 2500000
})
```

#### `get_fictional_exoplanets()`
Returns all fictional exoplanets.

#### `get_exoplanets_by_star(star_id)`
Returns all exoplanets for a specific host star.

#### `delete_fictional_exoplanet(planet_name)`
Removes a fictional exoplanet by name.

**Planet Classification Logic:**
- **Terrestrial**: Radius < 1.25 Earth radii OR Mass < 2 Earth masses
- **Super-Earth**: Radius 1.25-2.0 Earth radii OR Mass 2-10 Earth masses  
- **Mini-Neptune**: Radius 2.0-4.0 Earth radii OR Mass 10-50 Earth masses
- **Gas Giant**: Radius > 4.0 Earth radii OR Mass > 50 Earth masses

---

## 🏛️ Nation Handler (`nation_handler.py`)

### Purpose
Manages fictional political entities, including territories, government types, and diplomatic relationships.

### Key Features
- **Territory Validation**: Ensures all claimed star systems exist
- **Unique ID Generation**: Creates nation IDs from names with conflict resolution
- **Political Metadata**: Tracks government types, establishment dates, diplomatic stances
- **Economic Data**: Manages economic focus, specialties, and trade information
- **Military Information**: Tracks military strength and doctrine
- **Cultural Details**: Stores cultural descriptions and special traits

### Methods

#### `add_fictional_nation(nation_data)`
Adds a new fictional nation to the system.

**Required Fields:**
- `name`: Nation name (string)
- `full_name`: Full official name (string)
- `government_type`: Type of government (string)
- `capital_system`: Name of capital system (string)
- `capital_star_id`: Star ID of capital system (integer)

**Optional Fields:**
- `territories`: List of controlled star IDs (list of integers)
- `established_year`: Year established (integer)
- `political_alignment`: Political stance (string)
- `diplomatic_stance`: Diplomatic approach (string)
- `capital_planet`: Name of capital planet (string)
- `primary_color`: Nation color for maps (string, hex format)
- `border_color`: Border color (string, hex format)
- `economic_focus`: Economic focus description (string)
- `economic_specialties`: List of economic specialties (list of strings)
- `population`: Population description (string)
- `military_strength`: Military capabilities (string)
- `description`: Nation description (string)
- `culture_description`: Cultural details (string)
- `history`: Historical background (string)
- `technology_level`: Technology classification (string)
- `society_type`: Social organization (string)
- `diplomatic_relations`: Relations with other nations (dict)
- `special_traits`: Unique characteristics (list of strings)

**Example Usage:**
```python
from handlers import NationHandler

handler = NationHandler()
result = handler.add_fictional_nation({
    "name": "Frontier Alliance",
    "full_name": "The Frontier Alliance of Independent Worlds",
    "government_type": "Democratic Confederation",
    "capital_system": "Liberty Prime",
    "capital_star_id": 999998,
    "territories": [999998, 999997, 999996],
    "primary_color": "#4A90E2",
    "economic_focus": "Resource extraction and frontier trade",
    "economic_specialties": ["Mining", "Agriculture", "Frontier Services"],
    "population": "15 million across all systems",
    "description": "A confederation of independent frontier worlds"
})
```

#### `get_fictional_nations()`
Returns all fictional nations.

#### `get_nation_by_id(nation_id)`
Returns a specific nation by ID.

#### `get_nations_by_territory(star_id)`
Returns all nations controlling a specific star system.

#### `update_nation(nation_id, updates)`
Updates an existing nation's data.

#### `delete_nation(nation_id)`
Removes a nation by ID.

#### `validate_nation_data(nation_data)`
Validates nation data without adding it to the system.

---

## 🚛 Trade Route Handler (`trade_route_handler.py`)

### Purpose
Manages fictional trade routes connecting star systems, including logistics, economics, and route optimization.

### Key Features
- **Endpoint Validation**: Ensures both origin and destination star systems exist
- **Nation Control Validation**: Verifies the controlling nation exists
- **3D Distance Calculation**: Computes route length in parsecs
- **Travel Time Estimation**: Calculates journey duration based on distance and ship speed
- **Economic Zone Assignment**: Determines trade zones based on controlling nation
- **Route Efficiency Analysis**: Evaluates route conditions and efficiency

### Methods

#### `add_fictional_trade_route(route_data)`
Adds a new fictional trade route to the system.

**Required Fields:**
- `name`: Route name (string)
- `from_star_id`: Origin star system ID (integer)
- `to_star_id`: Destination star system ID (integer)
- `controlling_nation`: Nation ID controlling the route (string)
- `route_type`: Type of route (string, e.g., "Commercial", "Military", "Resource")

**Optional Fields:**
- `established_year`: Year route was established (integer)
- `cargo_types`: Types of cargo transported (list of strings)
- `frequency`: How often ships travel the route (string)
- `capacity`: Route cargo capacity (integer)
- `cost_per_unit`: Shipping cost per unit (float)
- `security_level`: Security classification (string)
- `patrol_frequency`: Military patrol schedule (string)
- `customs_checkpoints`: Customs stations (list of strings)
- `trade_volume`: Annual trade volume (float)
- `revenue`: Annual revenue (float)
- `regions`: Geographic regions served (list of strings)
- `description`: Route description (string)
- `category`: Route category (string)
- `efficiency_rating`: Route efficiency (string)
- `danger_level`: Threat assessment (string)
- `special_features`: Unique route characteristics (list of strings)
- `historical_significance`: Historical importance (string)
- `trade_regulations`: Applicable regulations (list of strings)
- `shipping_companies`: Operating companies (list of strings)
- `route_conditions`: Current conditions (string)
- `ship_speed`: Speed multiplier for travel time (float, default 1.0)

**Example Usage:**
```python
from handlers import TradeRouteHandler

handler = TradeRouteHandler()
result = handler.add_fictional_trade_route({
    "name": "Frontier Express",
    "from_star_id": 999998,
    "to_star_id": 999997,
    "controlling_nation": "frontier_alliance",
    "route_type": "Commercial",
    "cargo_types": ["Raw Materials", "Manufactured Goods", "Personnel"],
    "frequency": "Twice Weekly",
    "security_level": "Medium",
    "description": "Major commercial route serving frontier worlds"
})
```

#### `get_fictional_trade_routes()`
Returns all fictional trade routes.

#### `get_routes_by_nation(nation_id)`
Returns all routes controlled by a specific nation.

#### `get_routes_by_system(star_id)`
Returns all routes that include a specific star system.

#### `update_trade_route(route_id, updates)`
Updates an existing trade route.

#### `delete_trade_route(route_id)`
Removes a trade route by ID.

#### `validate_route_data(route_data)`
Validates trade route data without adding it to the system.

**Distance Calculation Formula:**
```python
distance = sqrt((x2-x1)² + (y2-y1)² + (z2-z1)²)
travel_time_days = distance / (base_speed * ship_speed_multiplier)
```

---

## 🔧 Integration with Starmap

### API Controller Integration

All handlers are automatically integrated with the API controller (`controllers/api_controller.py`):

```python
from handlers import StarHandler, ExoplanetHandler, NationHandler, TradeRouteHandler

class APIController:
    def __init__(self, database):
        self.db = database
        self.star_handler = StarHandler()
        self.exoplanet_handler = ExoplanetHandler()
        self.nation_handler = NationHandler()
        self.trade_route_handler = TradeRouteHandler()
```

### Database Cache Management

When new fictional entities are added, the database cache automatically reloads:

```python
result = self.star_handler.add_fictional_star(data)
if result['success']:
    self.db.reload_cache()  # Refresh cache with new data
```

### File Management

Handlers manage multiple file formats:
- **CSV Files**: `fictional_stars.csv`, `fictional_exoplanets.csv`
- **JSON Files**: `stars.json`, `nations.json`, `trade_routes.json`, `exoplanets.json`

---

## 📋 Best Practices

### Data Validation
1. **Always validate required fields** before processing
2. **Cross-reference related entities** (host stars, nations, territories)
3. **Use appropriate data types** and ranges
4. **Provide meaningful error messages** for validation failures

### ID Management
1. **Fictional stars**: Use IDs 999999 and below (counting down)
2. **Nations**: Generate IDs from names (e.g., "frontier_alliance")
3. **Trade routes**: Generate IDs from names with conflict resolution
4. **Exoplanets**: Use planet names as primary identifiers

### Error Handling
All handlers return consistent response formats:
```python
# Success response
{
    'success': True,
    'data': {...},
    'message': 'Operation completed successfully'
}

# Error response  
{
    'success': False,
    'error': 'Detailed error message'
}
```

### Performance Considerations
1. **Cache reloading** occurs after successful additions
2. **File operations** are optimized for both CSV and JSON formats
3. **Validation** is performed before expensive operations
4. **Coordinate calculations** use efficient mathematical formulas

---

## 🚀 Usage Examples

### Creating a Complete Star System

```python
from handlers import StarHandler, ExoplanetHandler, NationHandler, TradeRouteHandler

# 1. Add a fictional star
star_handler = StarHandler()
star_result = star_handler.add_fictional_star({
    "name": "Kepler-442 Alternative",
    "ra": 294.1,
    "dec": 39.3,
    "dist": 370.0,  # Light years converted to parsecs 
    "mag": 14.8,
    "spect": "K2V",
    "description": "Orange dwarf star with habitable planets"
})

star_id = star_result['data']['id']

# 2. Add planets to the system
exoplanet_handler = ExoplanetHandler()
planet_result = exoplanet_handler.add_fictional_exoplanet({
    "name": "Kepler-442 Alt b",
    "host_star_id": star_id,
    "orbital_period_days": 112.3,
    "semi_major_axis_au": 0.41,
    "radius_earth": 1.34,
    "mass_earth": 2.3,
    "description": "Potentially habitable super-Earth"
})

# 3. Create a nation claiming the system
nation_handler = NationHandler()
nation_result = nation_handler.add_fictional_nation({
    "name": "Kepler Republic",
    "full_name": "The Kepler Colonial Republic",
    "government_type": "Colonial Republic",
    "capital_system": "Kepler-442 Alternative",
    "capital_star_id": star_id,
    "territories": [star_id],
    "primary_color": "#8A2BE2"
})

# 4. Add trade route connecting to existing systems
route_handler = TradeRouteHandler()
route_result = route_handler.add_fictional_trade_route({
    "name": "Kepler Trade Lane",
    "from_star_id": 0,  # Sol
    "to_star_id": star_id,
    "controlling_nation": "kepler_republic", 
    "route_type": "Colonial Supply",
    "cargo_types": ["Colonial Supplies", "Technology", "Personnel"]
})
```

---

## 🔗 Related Documentation

- **[README.md](README.md)** - Main project overview with API examples
- **[DATA_MANAGEMENT_GUIDE.md](DATA_MANAGEMENT_GUIDE.md)** - Complete data management workflows
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development setup and contribution guidelines
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Navigation hub for all documentation

---

## 📝 Notes

- All handlers are **thread-safe** for concurrent API access
- **Fictional star IDs** start at 999999 and count down to avoid conflicts
- **Cache reloading** ensures immediate availability of new entities
- **Cross-validation** prevents orphaned references between entities
- **Error messages** are designed to be user-friendly and actionable

*For technical implementation details, see the source code in `/handlers/` directory.*