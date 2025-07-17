# Starmap API Reference

## 📖 Overview

The Starmap API provides comprehensive access to stellar data, fictional entities, and universe management through RESTful endpoints. This reference covers all available endpoints with examples and response formats.

**Base URL**: `http://localhost:8080/api/`

---

## 🔗 Navigation

- **[README.md](README.md)** - Main project overview
- **[HANDLERS_DOCUMENTATION.md](HANDLERS_DOCUMENTATION.md)** - Detailed handler documentation
- **[DATA_MANAGEMENT_GUIDE.md](DATA_MANAGEMENT_GUIDE.md)** - Data management workflows
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development setup
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Documentation hub

---

## 📊 Core Data Endpoints

### Stars

#### `GET /api/stars`
Get star data with optional filtering.

**Query Parameters:**
- `limit` (integer): Maximum number of stars to return (default: 1000)
- `mag_limit` (float): Maximum magnitude limit (default: 8.0)
- `spectral_type` (string): Filter by spectral type

**Example:**
```bash
curl "http://localhost:8080/api/stars?limit=100&mag_limit=6.0&spectral_type=G"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 0,
      "name": "Sol",
      "ra": 0.0,
      "dec": 0.0,
      "distance": 0.0,
      "magnitude": -26.7,
      "spectral_class": "G2V",
      "x": 0.0,
      "y": 0.0,
      "z": 0.0
    }
  ],
  "message": "Loaded 100 stars"
}
```

#### `GET /api/star/<int:star_id>`
Get detailed information for a specific star.

**Example:**
```bash
curl "http://localhost:8080/api/star/0"
```

#### `GET /api/search`
Search stars by name.

**Query Parameters:**
- `q` (string): Search query
- `limit` (integer): Maximum results (default: 20)

**Example:**
```bash
curl "http://localhost:8080/api/search?q=proxima&limit=5"
```

### Nations

#### `GET /api/nations`
Get all nations.

**Example:**
```bash
curl "http://localhost:8080/api/nations"
```

### Trade Routes

#### `GET /api/trade-routes`
Get all trade routes.

**Example:**
```bash
curl "http://localhost:8080/api/trade-routes"
```

### Exoplanets

#### `GET /api/exoplanets`
Get all exoplanets (real catalog data).

#### `GET /api/fictional-exoplanets`
Get fictional exoplanets data.

### System Information

#### `GET /api/stats`
Get application statistics.

#### `GET /api/stellar-regions`
Get stellar regions (galactic octants).

#### `GET /api/galactic-directions`
Get galactic coordinate directions.

---

## 🎭 Fictional Entity Management

### Fictional Stars

#### `GET /api/fictional/stars`
Get all fictional stars.

**Example:**
```bash
curl "http://localhost:8080/api/fictional/stars"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 999999,
      "proper": "Tiefe-Grenze Tor",
      "ra": 151.25,
      "dec": 30.0,
      "dist": 16.86,
      "mag": 9.5,
      "spect": "G5V",
      "fictional_name": "Tiefe-Grenze Tor",
      "fictional_description": "",
      "fictional_created": "2025-01-17T..."
    }
  ],
  "message": "Loaded 1 fictional stars"
}
```

#### `POST /api/fictional/stars`
Add a new fictional star.

**Request Body:**
```json
{
  "name": "Alpha Proximi",
  "ra": 214.75,
  "dec": -62.5,
  "dist": 4.24,
  "mag": 11.1,
  "spect": "M5V",
  "description": "Red dwarf companion to Proxima Centauri"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8080/api/fictional/stars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alpha Proximi",
    "ra": 214.75,
    "dec": -62.5,
    "dist": 4.24,
    "mag": 11.1,
    "spect": "M5V",
    "description": "Red dwarf companion to Proxima Centauri"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 999998,
    "name": "Alpha Proximi",
    "ra": 214.75,
    "dec": -62.5,
    "dist": 4.24,
    "mag": 11.1,
    "absmag": 15.8,
    "spect": "M5V",
    "x": -2.1234,
    "y": 1.5678,
    "z": -3.7890,
    "fictional_created": "2025-01-17T..."
  },
  "message": "Fictional star \"Alpha Proximi\" added successfully with ID 999998"
}
```

#### `DELETE /api/fictional/stars/<int:star_id>`
Delete a fictional star.

**Example:**
```bash
curl -X DELETE "http://localhost:8080/api/fictional/stars/999998"
```

### Fictional Exoplanets

#### `GET /api/fictional/exoplanets`
Get all fictional exoplanets.

#### `POST /api/fictional/exoplanets`
Add a new fictional exoplanet.

**Request Body:**
```json
{
  "name": "New Terra",
  "host_star_id": 999998,
  "orbital_period_days": 387.2,
  "semi_major_axis_au": 1.15,
  "radius_earth": 1.08,
  "mass_earth": 1.12,
  "description": "A promising world for colonization",
  "atmosphere": "Nitrogen-oxygen with traces of noble gases",
  "population": 2500000
}
```

**Example:**
```bash
curl -X POST "http://localhost:8080/api/fictional/exoplanets" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Terra",
    "host_star_id": 999998,
    "orbital_period_days": 387.2,
    "semi_major_axis_au": 1.15,
    "radius_earth": 1.08,
    "mass_earth": 1.12,
    "description": "A promising world for colonization"
  }'
```

### Fictional Nations

#### `GET /api/fictional/nations`
Get all fictional nations.

#### `POST /api/fictional/nations`
Add a new fictional nation.

**Request Body:**
```json
{
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
}
```

**Example:**
```bash
curl -X POST "http://localhost:8080/api/fictional/nations" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Frontier Alliance",
    "full_name": "The Frontier Alliance of Independent Worlds",
    "government_type": "Democratic Confederation",
    "capital_system": "Liberty Prime",
    "capital_star_id": 999998,
    "territories": [999998, 999997],
    "primary_color": "#4A90E2",
    "description": "A confederation of independent frontier worlds"
  }'
```

#### `DELETE /api/fictional/nations/<string:nation_id>`
Delete a fictional nation.

**Example:**
```bash
curl -X DELETE "http://localhost:8080/api/fictional/nations/frontier_alliance"
```

### Fictional Trade Routes

#### `GET /api/fictional/trade-routes`
Get all fictional trade routes.

#### `POST /api/fictional/trade-routes`
Add a new fictional trade route.

**Request Body:**
```json
{
  "name": "Frontier Express",
  "from_star_id": 999998,
  "to_star_id": 999997,
  "controlling_nation": "frontier_alliance",
  "route_type": "Commercial",
  "cargo_types": ["Raw Materials", "Manufactured Goods", "Personnel"],
  "frequency": "Twice Weekly",
  "security_level": "Medium",
  "description": "Major commercial route serving frontier worlds"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8080/api/fictional/trade-routes" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Frontier Express",
    "from_star_id": 999998,
    "to_star_id": 999997,
    "controlling_nation": "frontier_alliance",
    "route_type": "Commercial",
    "cargo_types": ["Raw Materials", "Manufactured Goods"],
    "frequency": "Twice Weekly",
    "description": "Major commercial route"
  }'
```

#### `DELETE /api/fictional/trade-routes/<string:route_id>`
Delete a fictional trade route.

**Example:**
```bash
curl -X DELETE "http://localhost:8080/api/fictional/trade-routes/frontier_express"
```

---

## 📝 Response Formats

### Success Response
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Detailed error message"
}
```

### Common HTTP Status Codes
- **200 OK**: Successful GET request
- **201 Created**: Successful POST request
- **400 Bad Request**: Invalid request data or validation failure
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

---

## 🔍 Validation Rules

### Fictional Stars
**Required Fields:**
- `name` (string): Star name
- `ra` (float): Right ascension in degrees (0-360)
- `dec` (float): Declination in degrees (-90 to 90)
- `dist` (float): Distance in parsecs (> 0)
- `mag` (float): Apparent magnitude
- `spect` (string): Spectral type

**Automatic Calculations:**
- 3D coordinates (x, y, z) from RA/Dec/Distance
- Absolute magnitude from apparent magnitude and distance
- Unique fictional ID (999999 and counting down)

### Fictional Exoplanets
**Required Fields:**
- `name` (string): Planet name
- `host_star_id` (integer): Must be valid star ID
- `orbital_period_days` (float): Orbital period > 0
- `semi_major_axis_au` (float): Semi-major axis > 0

**Validation:**
- Host star must exist in star database
- Planet name must be unique

### Fictional Nations
**Required Fields:**
- `name` (string): Nation name
- `full_name` (string): Full official name
- `government_type` (string): Government type
- `capital_system` (string): Capital system name
- `capital_star_id` (integer): Must be valid star ID

**Validation:**
- All territory star IDs must exist
- Capital star must exist
- Nation name must be unique

### Fictional Trade Routes
**Required Fields:**
- `name` (string): Route name
- `from_star_id` (integer): Origin star ID
- `to_star_id` (integer): Destination star ID
- `controlling_nation` (string): Must be valid nation ID
- `route_type` (string): Route classification

**Validation:**
- Both endpoint stars must exist
- Controlling nation must exist
- Route name must be unique

---

## 🛡️ Error Handling

### Validation Errors
```json
{
  "success": false,
  "error": "Missing required field: name"
}
```

### Cross-Reference Errors
```json
{
  "success": false,
  "error": "Host star with ID 999999 not found"
}
```

### Duplicate Name Errors
```json
{
  "success": false,
  "error": "Nation with name \"Frontier Alliance\" already exists"
}
```

---

## 🚀 Usage Examples

### Complete System Creation Workflow

```bash
# 1. Create a fictional star
STAR_RESPONSE=$(curl -s -X POST "http://localhost:8080/api/fictional/stars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Kepler-442 Alternative",
    "ra": 294.1,
    "dec": 39.3,
    "dist": 113.0,
    "mag": 14.8,
    "spect": "K2V",
    "description": "Orange dwarf star with habitable planets"
  }')

# Extract star ID from response
STAR_ID=$(echo $STAR_RESPONSE | jq -r '.data.id')

# 2. Add a planet to the system
curl -X POST "http://localhost:8080/api/fictional/exoplanets" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Kepler-442 Alt b\",
    \"host_star_id\": $STAR_ID,
    \"orbital_period_days\": 112.3,
    \"semi_major_axis_au\": 0.41,
    \"radius_earth\": 1.34,
    \"mass_earth\": 2.3,
    \"description\": \"Potentially habitable super-Earth\"
  }"

# 3. Create a nation claiming the system
curl -X POST "http://localhost:8080/api/fictional/nations" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Kepler Republic\",
    \"full_name\": \"The Kepler Colonial Republic\",
    \"government_type\": \"Colonial Republic\",
    \"capital_system\": \"Kepler-442 Alternative\",
    \"capital_star_id\": $STAR_ID,
    \"territories\": [$STAR_ID],
    \"primary_color\": \"#8A2BE2\",
    \"description\": \"A distant colonial republic\"
  }"

# 4. Add trade route to Sol
curl -X POST "http://localhost:8080/api/fictional/trade-routes" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Kepler Trade Lane\",
    \"from_star_id\": 0,
    \"to_star_id\": $STAR_ID,
    \"controlling_nation\": \"kepler_republic\",
    \"route_type\": \"Colonial Supply\",
    \"cargo_types\": [\"Colonial Supplies\", \"Technology\"],
    \"frequency\": \"Monthly\",
    \"description\": \"Supply route to distant colony\"
  }"
```

### Bulk Data Retrieval

```bash
# Get overview of all fictional content
curl "http://localhost:8080/api/fictional/stars" | jq '.data | length'
curl "http://localhost:8080/api/fictional/exoplanets" | jq '.data | length'
curl "http://localhost:8080/api/fictional/nations" | jq '.data | length'
curl "http://localhost:8080/api/fictional/trade-routes" | jq '.data | length'

# Get system statistics
curl "http://localhost:8080/api/stats" | jq '.'
```

---

## 🔗 Related Documentation

- **[README.md](README.md)** - Project overview with quick start guide
- **[HANDLERS_DOCUMENTATION.md](HANDLERS_DOCUMENTATION.md)** - Detailed handler implementation
- **[DATA_MANAGEMENT_GUIDE.md](DATA_MANAGEMENT_GUIDE.md)** - Alternative data management methods
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development setup and testing
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation navigation

---

## 📊 Performance Notes

- **Cache Updates**: Adding fictional entities triggers automatic database cache refresh
- **Response Times**: Most GET requests respond in < 100ms
- **Validation**: POST requests include comprehensive validation before processing
- **File Operations**: All changes are persisted to both CSV and JSON files as appropriate
- **Memory Usage**: All star data is cached in memory for fast access

---

*For implementation details and advanced usage, see [HANDLERS_DOCUMENTATION.md](HANDLERS_DOCUMENTATION.md)*