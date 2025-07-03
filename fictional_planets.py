# Fictional planetary systems for the Starmap application
# Separated from real astronomical data

fictional_planet_systems = {
    999999: [  # Tiefe-Grenze Tor - Fictional system from Felgenland Union
        {
            "name": "Felsbrand", "type": "Terrestrial", "distance_au": 0.4, "mass_earth": 0.6,
            "radius_earth": 0.9, "orbital_period_days": 73, "temperature_k": 650,
            "atmosphere": "CO2, traces of SO2", "discovery_year": "2080", "confirmed": False
        },
        {
            "name": "Brandstadt", "type": "Super-Earth", "distance_au": 0.9, "mass_earth": 3.0,
            "radius_earth": 1.4, "orbital_period_days": 347, "temperature_k": 288,
            "atmosphere": "N2 (78%), O2 (21%), CO2 (500ppm)", "discovery_year": "2080", "confirmed": False
        },
        {
            "name": "Sturmholz", "type": "Gas Giant", "distance_au": 2.5, "mass_earth": 254,
            "radius_earth": 10.0, "orbital_period_days": 1460, "temperature_k": 120,
            "atmosphere": "H2, He (Jupiter-like)", "discovery_year": "2080", "confirmed": False
        },
        {
            "name": "Frostkern", "type": "Ice Giant", "distance_au": 8.0, "mass_earth": 2.0,
            "radius_earth": 1.5, "orbital_period_days": 8395, "temperature_k": 45,
            "atmosphere": "H2, He, CH4, NH3", "discovery_year": "2080", "confirmed": False
        }
    ],
    48941: [  # 20 Leonis Minoris A (Holsten Tor) - Real star with confirmed and fictional planets
        {
            "name": "Felskern", "type": "Hot Neptune", "distance_au": 0.1916, "mass_earth": 9.2,
            "radius_earth": 3.0, "orbital_period_days": 31, "temperature_k": 800,
            "atmosphere": "Thin atmosphere (hot, non-habitable)", "discovery_year": "2015", "confirmed": True,
            "real_name": "HD 86728 b (20 LMi A b)", "description": "Hot, non-habitable world with thin atmosphere, used as mining outpost for metals and resources."
        },
        {
            "name": "Ninurta", "type": "Gas Giant", "distance_au": 1.2, "mass_earth": 477,
            "radius_earth": 11.0, "orbital_period_days": 511, "temperature_k": 180,
            "atmosphere": "H2, He (Saturn-like)", "discovery_year": "Future", "confirmed": False,
            "moons": [
                {
                    "name": "Trade Station Complex", "type": "Artificial", "mass_earth": 0.05, "radius_earth": 0.1,
                    "orbital_distance_km": 50000, "orbital_period_days": 3, "temperature_k": 180,
                    "atmosphere": "Artificial life support", "description": "Icy moons hosting trade stations for fuel and logistics"
                }
            ]
        },
        {
            "name": "Stahlburgh", "type": "Earth-like", "distance_au": 1.4, "mass_earth": 1.4,
            "radius_earth": 1.0, "orbital_period_days": 657, "temperature_k": 284,
            "atmosphere": "CO₂ (700 ppm)/N₂/O₂, 0.9 atm", "discovery_year": "Future", "confirmed": False,
            "local_name": "Alpine Prime",
            "climate": {
                "mean_temperature_c": 11,
                "summer_temperature_c": 17,
                "winter_temperature_c": 3,
                "biomes": ["coniferous forests", "grassy highlands", "tundra patches"],
                "description": "Slightly warmer than Edinburgh, Scotland; stable seasons due to low axial tilt (10°)"
            },
            "geography": {
                "supercontinent_area_km2": 120000000,
                "features": ["coastal forests", "inland plateaus", "mountain ranges", "vast oceans"]
            },
            "surface_gravity_g": 1.4,
            "magnetic_field": "Earth-like, shields stellar radiation",
            "moons": [
                {
                    "name": "Eisenwald", "type": "Rocky", "mass_earth": 0.5, "radius_earth": 0.8,
                    "orbital_distance_km": 60000, "orbital_period_days": 6, "temperature_k": 320,
                    "atmosphere": "CO₂/CH₄/H₂O-rich, 1.7 atm", 
                    "local_name": "Jungle Moon",
                    "climate": {
                        "equatorial_temperature_c": 35,
                        "tropical_temperature_c": 25,
                        "polar_temperature_c": 7,
                        "description": "Hothouse jungle equator, tropical/sub-tropical to 70° latitude, temperate poles"
                    },
                    "tidal_heating": 0.15,
                    "magnetic_field": "Shields planetary/stellar radiation",
                    "description": "Vibrant trade port with biodiverse markets, central to Felgenland's economy"
                }
            ],
            "description": "Hosts rugged colonies and administrative centers, key to trade hub operations"
        },
        {
            "name": "Ashur", "type": "Gas Giant", "distance_au": 5.0, "mass_earth": 221,
            "radius_earth": 9.0, "orbital_period_days": 4380, "temperature_k": 100,
            "atmosphere": "H2, He (Jupiter-like)", "discovery_year": "Future", "confirmed": False,
            "description": "Jupiter-like, named after Assyrian god of war and empire; orbital platforms serve as trade gateways"
        },
        {
            "name": "Eiswelt", "type": "Ice Giant", "distance_au": 10.0, "mass_earth": 3.0,
            "radius_earth": 1.7, "orbital_period_days": 11677, "temperature_k": 50,
            "atmosphere": "H2, He, CH4, NH3", "discovery_year": "Future", "confirmed": False,
            "description": "Neptune-like, mined for volatiles to support trade hub"
        }
    ],
    43464: [  # 55 Cancri (Griefen Tor) - Mix of real and fictional planets
        {
            "name": "Eisfluss", "type": "Super-Earth", "distance_au": 0.01544, "mass_earth": 7.99,
            "radius_earth": 1.875, "orbital_period_days": 0.74, "temperature_k": 2000,
            "atmosphere": "Likely none (lava world)", "discovery_year": "2004", "confirmed": True,
            "real_name": "Janssen (55 Cancri e)"
        },
        {
            "name": "Wolkenmeer", "type": "Gas Giant", "distance_au": 0.1134, "mass_earth": 261,
            "radius_earth": 11.2, "orbital_period_days": 14.65, "temperature_k": 800,
            "atmosphere": "H2, He", "discovery_year": "1996", "confirmed": True,
            "real_name": "Galileo (55 Cancri b)"
        },
        {
            "name": "Kernfluss", "type": "Gas Giant", "distance_au": 0.2403, "mass_earth": 54.3,
            "radius_earth": 6.8, "orbital_period_days": 44.34, "temperature_k": 500,
            "atmosphere": "H2, He", "discovery_year": "2002", "confirmed": True,
            "real_name": "Brahe (55 Cancri c)"
        },
        {
            "name": "Frostmeer", "type": "Gas Giant", "distance_au": 0.781, "mass_earth": 44.7,
            "radius_earth": 6.2, "orbital_period_days": 259.88, "temperature_k": 250,
            "atmosphere": "H2, He", "discovery_year": "2007", "confirmed": True,
            "real_name": "Harriot (55 Cancri f)"
        },
        {
            "name": "Lochiel", "type": "Ocean World", "distance_au": 0.9, "mass_earth": 1.2,
            "radius_earth": 1.1, "orbital_period_days": 330, "temperature_k": 280,
            "atmosphere": "N2, O2, H2O vapor", "discovery_year": "Future", "confirmed": False,
            "real_name": "Fictional - not in real 55 Cancri system"
        },
        {
            "name": "Sturmmeer", "type": "Gas Giant", "distance_au": 5.74, "mass_earth": 1213,
            "radius_earth": 14.8, "orbital_period_days": 5169, "temperature_k": 85,
            "atmosphere": "H2, He", "discovery_year": "2002", "confirmed": True,
            "real_name": "Lipperhey (55 Cancri d)"
        }
    ],
    46945: [  # 11 Leonis Minoris (Brandenburgh Tor) - Fictional planets
        {
            "name": "Salzkern", "type": "Terrestrial", "distance_au": 0.8, "mass_earth": 0.9,
            "radius_earth": 0.95, "orbital_period_days": 285, "temperature_k": 320,
            "atmosphere": "CO2, N2, traces of SO2", "discovery_year": "Future", "confirmed": False
        },
        {
            "name": "Hansaburgh", "type": "Super-Earth", "distance_au": 1.2, "mass_earth": 2.1,
            "radius_earth": 1.25, "orbital_period_days": 510, "temperature_k": 275,
            "atmosphere": "N2 (75%), O2 (23%), CO2 (800ppm)", "discovery_year": "Future", "confirmed": False
        },
        {
            "name": "Wogenstern", "type": "Gas Giant", "distance_au": 3.5, "mass_earth": 185,
            "radius_earth": 8.5, "orbital_period_days": 2555, "temperature_k": 95,
            "atmosphere": "H2, He (Jupiter-like)", "discovery_year": "Future", "confirmed": False
        },
        {
            "name": "Frostmeer", "type": "Ice Giant", "distance_au": 7.2, "mass_earth": 12.3,
            "radius_earth": 3.2, "orbital_period_days": 7580, "temperature_k": 55,
            "atmosphere": "H2, He, CH4, NH3", "discovery_year": "Future", "confirmed": False
        }
    ]
}