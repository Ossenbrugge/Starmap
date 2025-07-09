"""
Data entry templates for Starmap database
These templates provide standardized formats for adding new data
"""

from datetime import datetime
from typing import Dict, List, Optional, Union


class StarTemplate:
    """Template for adding new stars to the database"""
    
    @staticmethod
    def create_basic_star(
        star_id: int,
        name: str,
        x: float,
        y: float,
        z: float,
        magnitude: float,
        spectral_class: str,
        distance_parsecs: Optional[float] = None
    ) -> Dict:
        """Create a basic star entry"""
        
        if distance_parsecs is None:
            distance_parsecs = (x**2 + y**2 + z**2)**0.5
        
        return {
            'id': star_id,
            'hip': None,
            'hd': None,
            'hr': None,
            'gl': None,
            'bf': None,
            'proper': name,
            'ra': 0.0,  # Will be calculated from coordinates
            'dec': 0.0,  # Will be calculated from coordinates
            'dist': distance_parsecs,
            'pmra': 0.0,
            'pmdec': 0.0,
            'rv': 0.0,
            'mag': magnitude,
            'absmag': magnitude,  # Will be calculated
            'spect': spectral_class,
            'ci': 0.0,
            'x': x,
            'y': y,
            'z': z,
            'vx': 0.0,
            'vy': 0.0,
            'vz': 0.0,
            'rarad': 0.0,
            'decrad': 0.0,
            'pmrarad': 0.0,
            'pmdecrad': 0.0,
            'bayer': '',
            'flam': '',
            'con': '',
            'comp': 1,
            'comp_primary': star_id,
            'base': star_id,
            'lum': 1.0,  # Will be calculated from spectral class
            'var': '',
            'var_min': None,
            'var_max': None,
            'UUID': f"custom-star-{star_id}"
        }
    
    @staticmethod
    def create_fictional_star(
        star_id: int,
        system_name: str,
        fictional_name: str,
        x: float,
        y: float,
        z: float,
        magnitude: float,
        spectral_class: str,
        description: str = "",
        source: str = "Custom Addition"
    ) -> Dict:
        """Create a fictional star with narrative elements"""
        
        base_star = StarTemplate.create_basic_star(
            star_id, system_name, x, y, z, magnitude, spectral_class
        )
        
        # Add fictional elements
        base_star.update({
            'fictional_name': fictional_name,
            'fictional_source': source,
            'fictional_description': description,
            'proper': system_name
        })
        
        return base_star


class NationTemplate:
    """Template for adding new nations/political entities"""
    
    @staticmethod
    def create_nation(
        nation_id: str,
        name: str,
        full_name: str,
        government_type: str,
        capital_system: str,
        capital_star_id: int,
        capital_planet: str,
        established_year: int,
        color: str = "#FF6B6B",
        border_color: str = "#FF5252",
        description: str = "",
        territories: Optional[List[int]] = None,
        specialties: Optional[List[str]] = None
    ) -> Dict:
        """Create a new nation entry"""
        
        if territories is None:
            territories = [capital_star_id]
        
        if specialties is None:
            specialties = ["Trade", "Exploration"]
        
        return {
            'name': name,
            'full_name': full_name,
            'capital_system': capital_system,
            'capital_star_id': capital_star_id,
            'capital_planet': capital_planet,
            'government_type': government_type,
            'color': color,
            'border_color': border_color,
            'established_year': established_year,
            'description': description,
            'territories': territories,
            'specialties': specialties,
            'population': "Unknown",
            'military_strength': "Standard Defense Forces",
            'economic_focus': "Balanced Economy",
            'political_alignment': "Independent",
            'diplomatic_stance': "Neutral"
        }
    
    @staticmethod
    def create_trading_confederation(
        nation_id: str,
        name: str,
        capital_system: str,
        capital_star_id: int,
        established_year: int,
        member_systems: List[int],
        trade_specialties: List[str]
    ) -> Dict:
        """Create a trade-focused confederation"""
        
        return NationTemplate.create_nation(
            nation_id=nation_id,
            name=name,
            full_name=f"The {name} Trading Confederation",
            government_type="Trade Confederation",
            capital_system=capital_system,
            capital_star_id=capital_star_id,
            capital_planet="Trade Hub Alpha",
            established_year=established_year,
            color="#4CAF50",
            border_color="#388E3C",
            description=f"A peaceful trading confederation specializing in {', '.join(trade_specialties)}",
            territories=member_systems,
            specialties=trade_specialties
        )
    
    @staticmethod
    def create_exploration_coalition(
        nation_id: str,
        name: str,
        capital_system: str,
        capital_star_id: int,
        established_year: int,
        frontier_systems: List[int]
    ) -> Dict:
        """Create an exploration-focused coalition"""
        
        return NationTemplate.create_nation(
            nation_id=nation_id,
            name=name,
            full_name=f"The {name} Exploration Coalition",
            government_type="Exploration Coalition",
            capital_system=capital_system,
            capital_star_id=capital_star_id,
            capital_planet="Explorer Base",
            established_year=established_year,
            color="#2196F3",
            border_color="#1976D2",
            description="A coalition of explorers and scientists pushing the boundaries of known space",
            territories=frontier_systems,
            specialties=["Exploration", "Scientific Research", "Frontier Development"]
        )


class TradeRouteTemplate:
    """Template for adding new trade routes"""
    
    @staticmethod
    def create_trade_route(
        route_name: str,
        from_star_id: int,
        from_system: str,
        to_star_id: int,
        to_system: str,
        route_type: str,
        controlling_nation: str,
        cargo_types: List[str],
        travel_time_days: int,
        frequency: str = "Weekly",
        security_level: str = "Standard",
        established_year: int = 2300,
        description: str = ""
    ) -> Dict:
        """Create a new trade route entry"""
        
        return {
            'name': route_name,
            'from_star_id': from_star_id,
            'to_star_id': to_star_id,
            'from_system': from_system,
            'to_system': to_system,
            'route_type': route_type,
            'established': established_year,
            'cargo_types': cargo_types,
            'travel_time_days': travel_time_days,
            'frequency': frequency,
            'controlling_nation': controlling_nation,
            'security_level': security_level,
            'description': description,
            'regions': [],
            'economic_zone': "Free Trade Zone"
        }
    
    @staticmethod
    def create_mining_route(
        route_name: str,
        mining_system: str,
        mining_star_id: int,
        processing_system: str,
        processing_star_id: int,
        controlling_nation: str,
        ore_types: List[str]
    ) -> Dict:
        """Create a mining-focused trade route"""
        
        return TradeRouteTemplate.create_trade_route(
            route_name=route_name,
            from_star_id=mining_star_id,
            from_system=mining_system,
            to_star_id=processing_star_id,
            to_system=processing_system,
            route_type="Mining",
            controlling_nation=controlling_nation,
            cargo_types=ore_types + ["Mining Equipment", "Processed Materials"],
            travel_time_days=14,
            frequency="Bi-weekly",
            security_level="High",
            description=f"Mining route transporting {', '.join(ore_types)} from {mining_system} to {processing_system}"
        )
    
    @staticmethod
    def create_passenger_route(
        route_name: str,
        departure_system: str,
        departure_star_id: int,
        destination_system: str,
        destination_star_id: int,
        controlling_nation: str,
        service_class: str = "Standard"
    ) -> Dict:
        """Create a passenger transport route"""
        
        return TradeRouteTemplate.create_trade_route(
            route_name=route_name,
            from_star_id=departure_star_id,
            from_system=departure_system,
            to_star_id=destination_star_id,
            to_system=destination_system,
            route_type="Passenger",
            controlling_nation=controlling_nation,
            cargo_types=["Passengers", "Personal Effects", "Mail"],
            travel_time_days=7,
            frequency="Daily",
            security_level="Maximum",
            description=f"{service_class} passenger service between {departure_system} and {destination_system}"
        )


class PlanetarySystemTemplate:
    """Template for adding planetary systems"""
    
    @staticmethod
    def create_planet(
        name: str,
        planet_type: str,
        distance_au: float,
        mass_earth: float,
        radius_earth: float,
        orbital_period_days: float,
        temperature_k: float,
        atmosphere: str = "None",
        has_life: bool = False,
        inhabited: bool = False,
        population: int = 0,
        discovery_year: str = "2300",
        confirmed: bool = True
    ) -> Dict:
        """Create a planet entry"""
        
        return {
            'name': name,
            'type': planet_type,
            'distance_au': distance_au,
            'mass_earth': mass_earth,
            'radius_earth': radius_earth,
            'orbital_period_days': orbital_period_days,
            'temperature_k': temperature_k,
            'atmosphere': atmosphere,
            'has_life': has_life,
            'inhabited': inhabited,
            'population': population,
            'discovery_year': discovery_year,
            'confirmed': confirmed,
            'surface_gravity': mass_earth / (radius_earth ** 2),  # Approximate
            'escape_velocity': (2 * 11.2 * (mass_earth / radius_earth) ** 0.5),  # km/s, approximate
            'day_length_hours': 24.0,  # Default Earth-like
            'axial_tilt_degrees': 23.5,  # Default Earth-like
            'moons': []
        }
    
    @staticmethod
    def create_habitable_world(
        name: str,
        distance_au: float,
        mass_earth: float = 1.0,
        radius_earth: float = 1.0,
        atmosphere: str = "N2 (78%), O2 (21%), CO2 (400ppm)",
        inhabited: bool = False,
        population: int = 0,
        civilization_level: str = "None"
    ) -> Dict:
        """Create a habitable world"""
        
        # Calculate orbital period using Kepler's third law (simplified)
        orbital_period = (distance_au ** 1.5) * 365.25
        
        # Calculate temperature based on distance (very simplified)
        temperature = 278 * (1.0 / distance_au) ** 0.5  # Approximate
        
        planet = PlanetarySystemTemplate.create_planet(
            name=name,
            planet_type="Habitable Terrestrial",
            distance_au=distance_au,
            mass_earth=mass_earth,
            radius_earth=radius_earth,
            orbital_period_days=orbital_period,
            temperature_k=temperature,
            atmosphere=atmosphere,
            has_life=True,
            inhabited=inhabited,
            population=population
        )
        
        planet['civilization_level'] = civilization_level
        planet['habitability_score'] = 0.8  # High habitability
        
        return planet
    
    @staticmethod
    def create_gas_giant(
        name: str,
        distance_au: float,
        mass_earth: float,
        radius_earth: float,
        atmosphere: str = "H2, He (Jupiter-like)",
        moon_count: int = 0
    ) -> Dict:
        """Create a gas giant"""
        
        orbital_period = (distance_au ** 1.5) * 365.25
        temperature = 278 * (1.0 / distance_au) ** 0.5
        
        planet = PlanetarySystemTemplate.create_planet(
            name=name,
            planet_type="Gas Giant",
            distance_au=distance_au,
            mass_earth=mass_earth,
            radius_earth=radius_earth,
            orbital_period_days=orbital_period,
            temperature_k=temperature,
            atmosphere=atmosphere
        )
        
        planet['moon_count'] = moon_count
        planet['ring_system'] = moon_count > 10  # Assume ring system for large moon counts
        
        return planet
    
    @staticmethod
    def create_planetary_system(
        star_id: int,
        system_name: str,
        planets: List[Dict],
        system_age_billion_years: float = 4.5,
        metallicity: float = 0.0,
        description: str = ""
    ) -> Dict:
        """Create a complete planetary system"""
        
        # Calculate system statistics
        total_planets = len(planets)
        habitable_worlds = [p for p in planets if p.get('has_life', False)]
        gas_giants = [p for p in planets if p.get('type') == 'Gas Giant']
        terrestrial_planets = [p for p in planets if 'Terrestrial' in p.get('type', '')]
        
        has_life = len(habitable_worlds) > 0
        colonized = any(p.get('inhabited', False) for p in planets)
        total_population = sum(p.get('population', 0) for p in planets)
        
        return {
            'star_id': star_id,
            'system_name': system_name,
            'planets': planets,
            'total_planets': total_planets,
            'terrestrial_planets': len(terrestrial_planets),
            'gas_giants': len(gas_giants),
            'habitable_worlds': habitable_worlds,
            'has_life': has_life,
            'colonized': colonized,
            'total_population': total_population,
            'system_age_billion_years': system_age_billion_years,
            'metallicity': metallicity,
            'description': description,
            'discovery_status': 'Confirmed',
            'exploration_level': 'Surveyed' if has_life else 'Basic Survey'
        }


class StellarRegionTemplate:
    """Template for adding stellar regions"""
    
    @staticmethod
    def create_stellar_region(
        region_name: str,
        short_name: str,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        z_min: float,
        z_max: float,
        color: List[int] = None,
        description: str = "",
        brightest_star_name: str = "",
        brightest_star_id: Optional[int] = None,
        classification: str = "Galactic Region"
    ) -> Dict:
        """Create a stellar region definition"""
        
        if color is None:
            color = [100, 150, 200]  # Default blue-ish color
        
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        center_z = (z_min + z_max) / 2
        
        diameter = max(x_max - x_min, y_max - y_min, z_max - z_min)
        
        return {
            'name': region_name,
            'short_name': short_name,
            'description': description,
            'x_range': [x_min, x_max],
            'y_range': [y_min, y_max],
            'z_range': [z_min, z_max],
            'center_point': [center_x, center_y, center_z],
            'color': color,
            'diameter': diameter,
            'classification': classification,
            'established': "Galactic Survey Era",
            'brightest_star': brightest_star_name,
            'brightest_star_id': brightest_star_id,
            'brightest_star_magnitude': 0.0  # Will be calculated
        }


# Example usage templates
EXAMPLE_TEMPLATES = {
    'star': {
        'basic_star': StarTemplate.create_basic_star(
            star_id=900001,
            name="New Frontier",
            x=45.2,
            y=-23.1,
            z=67.8,
            magnitude=4.2,
            spectral_class="G5V"
        ),
        'fictional_star': StarTemplate.create_fictional_star(
            star_id=900002,
            system_name="Haven System",
            fictional_name="New Eden",
            x=78.3,
            y=12.7,
            z=-45.9,
            magnitude=3.8,
            spectral_class="F8V",
            description="A promising system for colonization with multiple habitable worlds",
            source="Custom Universe"
        )
    },
    
    'nation': {
        'trading_confederation': NationTemplate.create_trading_confederation(
            nation_id="meridian_traders",
            name="Meridian Traders",
            capital_system="Meridian Prime",
            capital_star_id=900001,
            established_year=2345,
            member_systems=[900001, 900002, 900003],
            trade_specialties=["Rare Metals", "Technology", "Foodstuffs"]
        ),
        'exploration_coalition': NationTemplate.create_exploration_coalition(
            nation_id="frontier_explorers",
            name="Frontier Explorers",
            capital_system="Explorer's Rest",
            capital_star_id=900004,
            established_year=2356,
            frontier_systems=[900004, 900005, 900006]
        )
    },
    
    'trade_route': {
        'mining_route': TradeRouteTemplate.create_mining_route(
            route_name="Asteroid Belt Express",
            mining_system="Minerva Prime",
            mining_star_id=900001,
            processing_system="Industrial Complex Alpha",
            processing_star_id=900002,
            controlling_nation="meridian_traders",
            ore_types=["Iron Ore", "Rare Earth Elements", "Platinum"]
        ),
        'passenger_route': TradeRouteTemplate.create_passenger_route(
            route_name="Colonial Express",
            departure_system="Old Terra",
            departure_star_id=0,
            destination_system="New Eden",
            destination_star_id=900002,
            controlling_nation="frontier_explorers",
            service_class="Luxury"
        )
    },
    
    'planetary_system': {
        'multi_planet_system': PlanetarySystemTemplate.create_planetary_system(
            star_id=900001,
            system_name="New Eden System",
            planets=[
                PlanetarySystemTemplate.create_planet(
                    name="Scorcher", planet_type="Hot Terrestrial", distance_au=0.3,
                    mass_earth=0.8, radius_earth=0.9, orbital_period_days=45,
                    temperature_k=600, atmosphere="CO2, SO2"
                ),
                PlanetarySystemTemplate.create_habitable_world(
                    name="Eden Prime", distance_au=1.2, mass_earth=1.1,
                    radius_earth=1.05, inhabited=True, population=2500000,
                    civilization_level="Early Industrial"
                ),
                PlanetarySystemTemplate.create_gas_giant(
                    name="Guardian", distance_au=5.2, mass_earth=318,
                    radius_earth=11.2, moon_count=16
                )
            ],
            description="A promising system with one inhabited world and rich resources"
        )
    }
}