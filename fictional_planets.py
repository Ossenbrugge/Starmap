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
    ],
    200001: [  # 61 Ursae Majoris - Protelani Republic system
        {
            "name": "61 UMa a", "alternate_name": "Chaud", "type": "Hothouse", "distance_au": 0.3, "mass_earth": 1.5,
            "radius_earth": 1.1, "orbital_period_days": 78, "temperature_k": 850,
            "atmosphere": "Thick CO2, traces of SO2", "discovery_year": "Future", "confirmed": False,
            "description": "Hot, non-habitable world used as a corporate mining outpost for metals and resources."
        },
        {
            "name": "61 UMa b", "alternate_name": "Frais", "type": "Rocky", "distance_au": 1.0, "mass_earth": 0.5,
            "radius_earth": 0.85, "orbital_period_days": 365, "temperature_k": 280,
            "atmosphere": "Thin CO2, N2", "discovery_year": "Future", "confirmed": False,
            "description": "Rocky planet used for resource extraction, supporting trade operations."
        },
        {
            "name": "61 UMa c", "alternate_name": "Joi", "type": "Gas Giant", "distance_au": 2.5, "mass_earth": 795,
            "radius_earth": 10.0, "orbital_period_days": 1095, "temperature_k": 150,
            "atmosphere": "H2, He (Jupiter-like)", "discovery_year": "Future", "confirmed": False,
            "description": "Gas giant with multiple moons, including Protelan, supporting trade stations for fuel and logistics.",
            "moons": [
                {
                    "name": "61 UMa c I", "alternate_name": "Protelan", "local_name": "Joi I", "type": "Earth-like Moon",
                    "mass_earth": 0.85, "radius_earth": 0.98, "radius_km": 6250,
                    "orbital_distance_km": 180000, "orbital_period_days": 8.5, "temperature_k": 290,
                    "surface_gravity_m_s2": 8.83, "surface_gravity_g": 0.9,
                    "atmosphere": {
                        "pressure_kpa": 110, "pressure_atm": 1.1,
                        "composition": "N₂ (~78%), O₂ (~20%), CO₂ (~500 ppm), H₂O (~1.5%)",
                        "albedo": 0.38
                    },
                    "climate": {
                        "mean_temperature_c": 20, "summer_temperature_c": 25, "winter_temperature_c": 10,
                        "polar_temperature_c": 5, "description": "Temperate, resembling coastal Norway, with frequent storms and fjord-like coasts"
                    },
                    "geography": {
                        "surface_area_km2": 490087000, "land_area_km2": 196035000, "water_area_km2": 294052000,
                        "water_percentage": 60, "land_percentage": 40,
                        "features": ["archipelagos", "small continents", "temperate forests", "grassy plains", "fjord-like coasts"]
                    },
                    "tidal_heating_w_m2": 0.1, "magnetic_field": "Earth-like, deflects Joi's radiation",
                    "discovery_year": "2226", "confirmed": False,
                    "description": "Earth-like moon hosting Havskrun, capital of the Protelani Republic. Features bioluminescent corals and tall hardwoods adapted to low gravity.",
                    "population": "~800 million Protelani (avg. 2m tall)",
                    "cities": [
                        {
                            "name": "Havskrun", "type": "Capital", "population": "~15 million",
                            "description": "Capital city built around fjords, center of corporate and government operations"
                        }
                    ],
                    "culture": {
                        "heritage": "Scandinavian-descended", "festivals": ["Joi Veil Festival (eclipse celebrations)"],
                        "traditions": ["patronymic naming", "corporate clan structures"],
                        "average_height_m": 2.0, "gravity_adaptation": "Low gravity (0.9g) enhanced growth"
                    }
                },
                {
                    "name": "Trade Station Moons", "type": "Icy Moons", "mass_earth": 0.03,
                    "description": "Multiple icy moons used for trade stations and resource extraction",
                    "count": "4-6 smaller moons", "discovery_year": "2226", "confirmed": False
                }
            ]
        },
        {
            "name": "61 UMa d", "alternate_name": "Froid", "type": "Rocky", "distance_au": 4.0, "mass_earth": 0.5,
            "radius_earth": 0.85, "orbital_period_days": 1890, "temperature_k": 180,
            "atmosphere": "Virtually none", "discovery_year": "Future", "confirmed": False,
            "description": "Rocky planet with minimal activity, used for resource extraction."
        },
        {
            "name": "61 UMa e", "alternate_name": "Hiver", "type": "Mars-like Desert", "distance_au": 73, "mass_earth": 0.3,
            "radius_earth": 0.75, "orbital_period_years": 350, "temperature_k": 120,
            "atmosphere": "Thin CO2", "discovery_year": "Future", "confirmed": False,
            "description": "Desert world used for resource extraction, with minimal habitability."
        },
        {
            "name": "61 UMa f", "alternate_name": "Grandpere", "type": "Gas Giant", "distance_au": 154, "mass_earth": 573,
            "radius_earth": 8.0, "orbital_period_years": 4250, "temperature_k": 50,
            "atmosphere": "H2, He, CH4, NH3", "discovery_year": "Future", "confirmed": False,
            "description": "Distant gas giant with icy moons, supporting minimal trade activity.",
            "moons": {
                "count": "Multiple icy moons", "description": "Used for resource extraction and remote trade stations"
            }
        }
    ],
    200002: [  # Fomalhaut - Dorsai Republic system
        {
            "name": "α PsA b", "alternate_name": "Fomalhaut b", "type": "Gas Giant", "distance_au": 177, "mass_earth": 636,
            "radius_earth": 6.5, "orbital_period_years": 1700, "temperature_k": 50,
            "atmosphere": "H2, He, CH4, NH3", "discovery_year": "2008", "confirmed": True,
            "description": "Distant gas giant with potential icy moons used for resource extraction (volatiles, metals). Hosts orbital defense platforms for the Dorsai Republic's rimward security."
        },
        {
            "name": "α PsA c", "alternate_name": "Valorgraemo", "type": "Earth-like", "distance_au": 2.1, "mass_earth": 1.2,
            "radius_earth": 1.0, "orbital_period_days": 780, "temperature_k": 289,
            "surface_gravity_g": 1.0, "surface_gravity_m_s2": 9.81,
            "atmosphere": {
                "pressure_kpa": 101, "pressure_atm": 1.0,
                "composition": "N₂ (~78%), O₂ (~20%), CO₂ (~400 ppm), H₂O (~1.5%)",
                "albedo": 0.35
            },
            "climate": {
                "mean_temperature_c": 16, "summer_temperature_c": 22, "winter_temperature_c": 8,
                "description": "Temperate with fortified highlands and coastal fortresses, resembling Starship Troopers' training terrains"
            },
            "geography": {
                "surface_area_km2": 510064000, "land_area_km2": 148940000, "water_area_km2": 361132000,
                "features": ["continental plateaus", "fortified cities", "shallow seas"]
            },
            "discovery_year": "Future", "confirmed": False,
            "description": "Capital world of the Dorsai Republic, hosting the Citadel of Valoro and military academies. Trains elite soldiers inspired by Dorsai!'s Cletus Grahame and Starship Troopers' Mobile Infantry.",
            "population": "~800 million Dorsai",
            "cities": [
                {
                    "name": "Citadel of Valoro", "type": "Military Capital", "population": "~25 million",
                    "description": "Fortified capital complex housing military academies, command centers, and elite training facilities"
                }
            ],
            "culture": {
                "military_tradition": "Elite soldier training inspired by Dorsai! and Starship Troopers",
                "specialties": ["Tactical warfare", "Mobile Infantry", "Rimward defense"],
                "training_centers": ["Citadel of Valoro", "Highland Fortress Complexes"]
            }
        },
        {
            "name": "α PsA d", "alternate_name": "Batalklendo", "type": "Earth-like", "distance_au": 2.4, "mass_earth": 1.5,
            "radius_earth": 1.1, "orbital_period_days": 950, "temperature_k": 285,
            "surface_gravity_g": 1.1, "surface_gravity_m_s2": 10.79,
            "atmosphere": {
                "pressure_kpa": 111, "pressure_atm": 1.1,
                "composition": "N₂ (~78%), O₂ (~20%), CO₂ (~450 ppm), H₂O (~1.5%)",
                "albedo": 0.35
            },
            "climate": {
                "mean_temperature_c": 12, "summer_temperature_c": 18, "winter_temperature_c": 4,
                "description": "Cool temperate with grassy plains and coniferous forests, ideal for shock troop training"
            },
            "geography": {
                "surface_area_km2": 615752000, "land_area_km2": 179904000, "water_area_km2": 435848000,
                "features": ["rolling plains", "mountain ranges", "small lakes"]
            },
            "discovery_year": "Future", "confirmed": False,
            "description": "Rugged training ground for Dorsai shock troops, inspired by Starship Troopers' Boot Camp and Dorsai!'s tactical fields. Supports agricultural trade.",
            "population": "~350 million training personnel and support",
            "culture": {
                "primary_function": "Military training and shock troop development",
                "terrain_specialties": ["Mountain warfare", "Plains tactics", "Survival training"]
            }
        },
        {
            "name": "α PsA e", "alternate_name": "Marrikoviro", "type": "Earth-like", "distance_au": 2.8, "mass_earth": 1.3,
            "radius_earth": 1.0, "orbital_period_days": 1200, "temperature_k": 291,
            "surface_gravity_g": 1.0, "surface_gravity_m_s2": 9.81,
            "atmosphere": {
                "pressure_kpa": 101, "pressure_atm": 1.0,
                "composition": "N₂ (~78%), O₂ (~20%), CO₂ (~400 ppm), H₂O (~2%)",
                "albedo": 0.35
            },
            "climate": {
                "mean_temperature_c": 18, "summer_temperature_c": 25, "winter_temperature_c": 8,
                "description": "Maritime with frequent storms, hosting naval bases and trade ports"
            },
            "geography": {
                "surface_area_km2": 510064000, "land_area_km2": 153019200, "water_area_km2": 357044800,
                "water_percentage": 70, "land_percentage": 30,
                "features": ["island chains", "coastal forests", "deep ocean basins"]
            },
            "discovery_year": "Future", "confirmed": False,
            "description": "Ocean world with naval bases, reflecting Starship Troopers' Johnny Rico and Dorsai!'s maritime defense capabilities. Vital for rimward commerce.",
            "population": "~250 million naval and trade personnel",
            "culture": {
                "primary_function": "Naval operations and maritime trade",
                "specialties": ["Fleet operations", "Coastal defense", "Trade logistics"]
            }
        }
    ]
}