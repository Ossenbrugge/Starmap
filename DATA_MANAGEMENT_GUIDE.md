# Starmap Data Management Guide

## Overview

This guide provides comprehensive instructions for managing data in the Starmap database using the new MontyDB-powered CRUD system. You can add, modify, and remove stars, nations, trade routes, and planetary systems with streamlined templates and validation.

## Quick Start

### 1. Basic Setup

```python
from managers.data_manager import DataManager

# Initialize the data manager
dm = DataManager()

# Get current database status
status = dm.get_comprehensive_statistics()
print(f"Database contains {status['stars']['total_stars']} stars")
```

### 2. Using Templates

```python
# Get all available templates
templates = dm.get_templates()

# Create a fictional star using template
star_id = dm.add_star_from_template(
    template_type='fictional',
    star_id=900001,
    system_name="New Haven",
    fictional_name="Paradise Prime",
    x=45.2, y=-23.1, z=67.8,
    magnitude=4.2,
    spectral_class="G5V",
    description="A promising system for human colonization"
)

# Create a trading nation
nation_id = dm.add_nation_from_template(
    template_type='confederation',
    name="Meridian Traders",
    capital_star_id=900001,
    member_systems=[900001, 900002, 900003],
    trade_specialties=["Rare Metals", "Technology"]
)
```

## Data Templates

### Star Templates

#### Basic Star
```python
from templates.data_templates import StarTemplate

star_data = StarTemplate.create_basic_star(
    star_id=900001,
    name="New Frontier",
    x=45.2, y=-23.1, z=67.8,
    magnitude=4.2,
    spectral_class="G5V"
)
```

#### Fictional Star
```python
star_data = StarTemplate.create_fictional_star(
    star_id=900002,
    system_name="Haven System",
    fictional_name="New Eden",
    x=78.3, y=12.7, z=-45.9,
    magnitude=3.8,
    spectral_class="F8V",
    description="A promising system for colonization",
    source="Custom Universe"
)
```

### Nation Templates

#### Basic Nation
```python
from templates.data_templates import NationTemplate

nation_data = NationTemplate.create_nation(
    nation_id="stellar_republic",
    name="Stellar Republic",
    full_name="The Stellar Republic",
    government_type="Democratic Republic",
    capital_system="Liberty Prime",
    capital_star_id=900001,
    capital_planet="Freedom World",
    established_year=2350,
    description="A democratic federation of star systems"
)
```

#### Trading Confederation
```python
nation_data = NationTemplate.create_trading_confederation(
    nation_id="trade_alliance",
    name="Commercial Alliance",
    capital_system="Trade Hub Alpha",
    capital_star_id=900001,
    established_year=2345,
    member_systems=[900001, 900002, 900003],
    trade_specialties=["Electronics", "Rare Metals", "Food"]
)
```

#### Exploration Coalition
```python
nation_data = NationTemplate.create_exploration_coalition(
    nation_id="frontier_explorers",
    name="Frontier Explorers",
    capital_system="Explorer Base",
    capital_star_id=900001,
    established_year=2360,
    frontier_systems=[900001, 900002, 900003]
)
```

### Trade Route Templates

#### Basic Trade Route
```python
from templates.data_templates import TradeRouteTemplate

route_data = TradeRouteTemplate.create_trade_route(
    route_name="Commercial Highway",
    from_star_id=900001,
    from_system="Hub Alpha",
    to_star_id=900002,
    to_system="Hub Beta",
    route_type="Commercial",
    controlling_nation="trade_alliance",
    cargo_types=["Electronics", "Textiles", "Food"],
    travel_time_days=14,
    frequency="Weekly"
)
```

#### Mining Route
```python
route_data = TradeRouteTemplate.create_mining_route(
    route_name="Asteroid Mining Route",
    mining_system="Minerva Prime",
    mining_star_id=900001,
    processing_system="Industrial Hub",
    processing_star_id=900002,
    controlling_nation="trade_alliance",
    ore_types=["Iron", "Platinum", "Rare Earths"]
)
```

#### Passenger Route
```python
route_data = TradeRouteTemplate.create_passenger_route(
    route_name="Colonial Express",
    departure_system="Old Terra",
    departure_star_id=0,
    destination_system="New Eden",
    destination_star_id=900002,
    controlling_nation="stellar_republic",
    service_class="Luxury"
)
```

### Planetary System Templates

#### Basic Planet
```python
from templates.data_templates import PlanetarySystemTemplate

planet_data = PlanetarySystemTemplate.create_planet(
    name="New Earth",
    planet_type="Terrestrial",
    distance_au=1.2,
    mass_earth=1.1,
    radius_earth=1.05,
    orbital_period_days=438,
    temperature_k=288,
    atmosphere="N2 (78%), O2 (21%), CO2 (400ppm)"
)
```

#### Habitable World
```python
planet_data = PlanetarySystemTemplate.create_habitable_world(
    name="Paradise",
    distance_au=1.0,
    mass_earth=1.0,
    radius_earth=1.0,
    inhabited=True,
    population=5000000,
    civilization_level="Industrial"
)
```

#### Complete Planetary System
```python
system_data = PlanetarySystemTemplate.create_planetary_system(
    star_id=900001,
    system_name="New Eden System",
    planets=[
        PlanetarySystemTemplate.create_planet(
            name="Scorcher", planet_type="Hot Terrestrial", 
            distance_au=0.3, mass_earth=0.8, temperature_k=600
        ),
        PlanetarySystemTemplate.create_habitable_world(
            name="Eden Prime", distance_au=1.2, 
            inhabited=True, population=2500000
        ),
        PlanetarySystemTemplate.create_gas_giant(
            name="Guardian", distance_au=5.2, 
            mass_earth=318, radius_earth=11.2, moon_count=16
        )
    ],
    description="A three-planet system with one habitable world"
)
```

## CRUD Operations

### Star Operations

#### Create
```python
# Add a star
star_id = dm.add_star(star_data)

# Add multiple stars
star_ids = dm.bulk_add_stars([star_data1, star_data2, star_data3])

# Import from CSV
count = dm.import_stars_from_csv("new_stars.csv")
```

#### Read
```python
# Get star details
star = dm.get_star(900001)

# Search stars
results = dm.search_stars(
    query="Eden",
    magnitude_range=(0, 6),
    nation_id="stellar_republic",
    habitability_min=0.6
)

# Get stars in coordinate range
nearby_stars = dm.star_manager.get_stars_in_region(
    x_range=(40, 50),
    y_range=(-30, -20),
    z_range=(60, 70)
)
```

#### Update
```python
# Update star information
dm.update_star(900001, {
    'fictional_name': 'New Paradise',
    'fictional_description': 'Updated description'
})

# Assign to nation
dm.star_manager.assign_to_nation(900001, 'stellar_republic', 'territory')
```

#### Delete
```python
# Delete a star
dm.delete_star(900001, force=True)

# Delete all fictional stars
dm.star_manager.delete_fictional_stars()
```

### Nation Operations

#### Create
```python
# Add a nation
nation_id = dm.add_nation(nation_data)

# Create with template
nation_id = dm.add_nation_from_template(
    template_type='confederation',
    name="New Alliance",
    capital_star_id=900001,
    member_systems=[900001, 900002],
    trade_specialties=["Technology", "Medicine"]
)
```

#### Read
```python
# Get nation details
nation = dm.get_nation('stellar_republic')

# List all nations
nations = dm.list_nations()

# Filter nations
democratic_nations = dm.list_nations(government_type='Democratic Republic')
```

#### Update
```python
# Update nation information
dm.update_nation('stellar_republic', {
    'description': 'Updated description',
    'population': '50 million citizens'
})

# Add territory
dm.add_territory('stellar_republic', 900003)

# Change capital
dm.nation_manager.change_capital('stellar_republic', 900002, 'New Capital')
```

#### Delete
```python
# Delete nation (transfer territories)
dm.delete_nation('stellar_republic', transfer_territories_to='trade_alliance')

# Delete nation (make territories independent)
dm.delete_nation('stellar_republic')
```

### Trade Route Operations

#### Create
```python
# Add trade route
route_id = dm.add_trade_route(route_data)

# Create with template
route_id = dm.add_trade_route_from_template(
    template_type='mining',
    route_name="New Mining Route",
    mining_star_id=900001,
    processing_star_id=900002,
    controlling_nation='trade_alliance',
    ore_types=['Gold', 'Platinum']
)
```

#### Read
```python
# Get route details
route = dm.get_trade_route('commercial_highway')

# List routes
routes = dm.list_trade_routes()

# Filter routes
mining_routes = dm.list_trade_routes(route_type='Mining')
alliance_routes = dm.list_trade_routes(controlling_nation='trade_alliance')
```

#### Update
```python
# Update route information
dm.update_trade_route('commercial_highway', {
    'frequency': 'Daily',
    'security_level': 'High'
})

# Change controlling nation
dm.trade_route_manager.change_route_control('commercial_highway', 'new_nation')
```

#### Delete
```python
# Delete route
dm.delete_trade_route('commercial_highway')

# Delete all routes for a nation
dm.trade_route_manager.delete_routes_by_nation('old_nation')
```

### Planetary System Operations

#### Create
```python
# Add planetary system
star_id = dm.add_planetary_system(system_data)

# Create habitable system
star_id = dm.system_manager.create_habitable_system(
    star_id=900001,
    system_name="Eden System",
    num_planets=4,
    habitable_planet_name="New Earth"
)
```

#### Read
```python
# Get system details
system = dm.get_planetary_system(900001)

# List systems
systems = dm.list_planetary_systems()

# Filter systems
habitable_systems = dm.list_planetary_systems(has_life=True)
colonized_systems = dm.list_planetary_systems(colonized=True)
```

#### Update
```python
# Update system information
dm.update_planetary_system(900001, {
    'description': 'Updated system description',
    'exploration_level': 'Fully Surveyed'
})

# Update planet
dm.system_manager.update_planet(900001, 'Eden Prime', {
    'population': 10000000,
    'inhabited': True
})

# Colonize planet
dm.system_manager.colonize_planet(900001, 'New Earth', population=5000000)
```

#### Delete
```python
# Delete system
dm.delete_planetary_system(900001)

# Remove planet from system
dm.system_manager.remove_planet_from_system(900001, 'Unwanted Planet')
```

## Felgenland Saga Cleanup

### Preview Cleanup
```python
# See what would be removed
preview = dm.preview_felgenland_cleanup()
print(f"Would remove {len(preview['nations_to_remove'])} nations")
print(f"Would remove {len(preview['trade_routes_to_remove'])} trade routes")
```

### Backup Before Cleanup
```python
# Create backup
backup_result = dm.backup_felgenland_data("felgenland_backup.json")
print(f"Backed up {backup_result['nations_backed_up']} nations")
```

### Complete Cleanup
```python
# Remove all Felgenland data
result = dm.remove_felgenland_data(confirm=True)
print(f"Removed {result['nations_removed']} nations")
print(f"Removed {result['trade_routes_removed']} trade routes")
```

### Selective Cleanup
```python
# Remove only specific components
result = dm.selective_felgenland_cleanup(
    remove_nations=True,
    remove_trade_routes=True,
    remove_planetary_systems=False,
    clean_fictional_data=True,
    remove_fictional_stars=False
)
```

## Data Validation

### Validate Before Adding
```python
# Validate star data
errors = dm.validate_star_data(star_data)
if errors:
    print("Validation errors:", errors)
else:
    dm.add_star(star_data)

# Validate nation data
errors = dm.validate_nation_data(nation_data)
if not errors:
    dm.add_nation(nation_data)
```

## Bulk Operations

### Import Data
```python
# Import stars from CSV
count = dm.import_stars_from_csv("stars.csv")

# Import trade routes from JSON
count = dm.import_trade_routes_from_json("trade_routes.json")

# Import planetary systems from dictionary
systems_dict = {
    900001: [planet1_data, planet2_data, planet3_data],
    900002: [planet4_data, planet5_data]
}
count = dm.import_planetary_systems_from_dict(systems_dict)
```

### Batch Operations
```python
# Add multiple stars
star_ids = dm.bulk_add_stars([star1_data, star2_data, star3_data])

# Add multiple trade routes
route_ids = dm.bulk_add_trade_routes([route1_data, route2_data])
```

## Analysis and Statistics

### Basic Statistics
```python
# Get comprehensive statistics
stats = dm.get_comprehensive_statistics()

# Get specific statistics
star_stats = dm.get_star_statistics()
nation_stats = dm.get_nation_statistics()
trade_stats = dm.get_trade_route_statistics()
system_stats = dm.get_system_statistics()
```

### Advanced Analysis
```python
# Analyze galactic situation
situation = dm.analyze_galactic_situation()
print(f"Galactic control: {situation['galactic_overview']['control_percentage']}%")

# Analyze trade network
network = dm.analyze_trade_network()
print(f"Trade network density: {network['summary']['network_density']}")

# Find expansion targets for a nation
targets = dm.suggest_expansion_targets('stellar_republic', max_distance=30.0)
```

## Utility Functions

### Find Connections
```python
# Find all connections for a star
connections = dm.find_connections(900001)
print(f"Star: {connections['star']['name']}")
print(f"Controlled by: {connections['nation']['name'] if connections['nation'] else 'Independent'}")
print(f"Trade routes: {len(connections['trade_routes'])}")
```

### Export Data
```python
# Export all data
dm.export_data('all', 'complete_database.json')

# Export specific data types
dm.export_data('stars', 'stars_export.json')
dm.export_data('nations', 'nations_export.json')
dm.export_data('trade_routes', 'trade_routes_export.json')
```

## Error Handling

### Validation Errors
```python
try:
    star_id = dm.add_star(invalid_star_data)
except Exception as e:
    print(f"Error adding star: {e}")
    
    # Validate first
    errors = dm.validate_star_data(invalid_star_data)
    for error in errors:
        print(f"Validation error: {error}")
```

### Dependency Errors
```python
try:
    dm.delete_star(900001)
except Exception as e:
    print(f"Cannot delete star: {e}")
    
    # Check dependencies
    dependencies = dm.star_manager._check_star_dependencies(900001)
    print(f"Dependencies: {dependencies}")
```

## Best Practices

### 1. Always Validate Data
```python
# Always validate before adding
errors = dm.validate_star_data(star_data)
if errors:
    print("Fix these errors before adding:", errors)
    return

dm.add_star(star_data)
```

### 2. Use Transactions for Related Operations
```python
# When adding related data, check for errors
try:
    # Add star
    star_id = dm.add_star(star_data)
    
    # Add nation
    nation_id = dm.add_nation(nation_data)
    
    # Assign star to nation
    dm.add_territory(nation_id, star_id)
    
    # Add trade route
    route_id = dm.add_trade_route(route_data)
    
    print("All operations successful")
    
except Exception as e:
    print(f"Operation failed: {e}")
    # Consider cleanup if needed
```

### 3. Regular Backups
```python
# Create regular backups
from datetime import datetime

backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
dm.export_data('all', backup_file)
```

### 4. Monitor Database Health
```python
# Regular health checks
stats = dm.get_comprehensive_statistics()
print(f"Database health:")
print(f"  Stars: {stats['stars']['total_stars']}")
print(f"  Nations: {stats['nations']['total_nations']}")
print(f"  Trade Routes: {stats['trade_routes']['total_routes']}")
print(f"  Planetary Systems: {stats['planetary_systems']['total_systems']}")

# Check for territorial conflicts
conflicts = dm.nation_manager.analyze_territorial_conflicts()
if conflicts:
    print(f"Found {len(conflicts)} territorial conflicts")
    dm.nation_manager.fix_territorial_conflicts()
```

## Common Workflows

### 1. Adding a New Star System
```python
# Complete workflow for adding a new star system
def add_complete_star_system(name, x, y, z, magnitude, spectral_class, planets):
    dm = DataManager()
    
    # Generate unique ID
    star_id = 900000 + hash(name) % 100000
    
    # Add star
    star_data = StarTemplate.create_fictional_star(
        star_id=star_id,
        system_name=name,
        fictional_name=name,
        x=x, y=y, z=z,
        magnitude=magnitude,
        spectral_class=spectral_class,
        description=f"Custom star system: {name}"
    )
    
    dm.add_star(star_data)
    
    # Add planetary system
    system_data = PlanetarySystemTemplate.create_planetary_system(
        star_id=star_id,
        system_name=name,
        planets=planets,
        description=f"Planetary system around {name}"
    )
    
    dm.add_planetary_system(system_data)
    
    return star_id

# Usage
planets = [
    PlanetarySystemTemplate.create_habitable_world(
        name="Paradise", distance_au=1.2, inhabited=True, population=1000000
    )
]

star_id = add_complete_star_system(
    "New Eden", 45.2, -12.3, 78.1, 4.5, "G2V", planets
)
```

### 2. Creating a New Nation with Territory
```python
def create_nation_with_territory(name, government_type, capital_star_id, territory_star_ids):
    dm = DataManager()
    
    # Create nation
    nation_id = dm.add_nation_from_template(
        template_type='basic',
        nation_id=name.lower().replace(' ', '_'),
        name=name,
        government_type=government_type,
        capital_star_id=capital_star_id,
        territories=territory_star_ids
    )
    
    # Add territories
    for star_id in territory_star_ids:
        if star_id != capital_star_id:
            dm.add_territory(nation_id, star_id)
    
    return nation_id

# Usage
nation_id = create_nation_with_territory(
    "New Republic", "Democratic Republic", 900001, [900001, 900002, 900003]
)
```

### 3. Setting Up Trade Network
```python
def setup_trade_network(nation_id, trade_hubs):
    dm = DataManager()
    
    route_ids = []
    
    # Create routes between all hubs
    for i, hub1 in enumerate(trade_hubs):
        for hub2 in trade_hubs[i+1:]:
            route_id = dm.add_trade_route_from_template(
                template_type='basic',
                route_name=f"{hub1['name']} - {hub2['name']} Route",
                from_star_id=hub1['star_id'],
                from_system=hub1['name'],
                to_star_id=hub2['star_id'],
                to_system=hub2['name'],
                route_type='Commercial',
                controlling_nation=nation_id,
                cargo_types=['General Cargo', 'Passengers'],
                travel_time_days=7
            )
            route_ids.append(route_id)
    
    return route_ids

# Usage
trade_hubs = [
    {'name': 'Hub Alpha', 'star_id': 900001},
    {'name': 'Hub Beta', 'star_id': 900002},
    {'name': 'Hub Gamma', 'star_id': 900003}
]

route_ids = setup_trade_network('new_republic', trade_hubs)
```

This comprehensive guide provides everything needed to manage data in the Starmap database effectively. Use the templates for consistency, always validate data before adding, and leverage the powerful search and analysis capabilities to maintain your custom universe.