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
    48941: [  # 20 Leonis Minoris (Holsten Tor) - Real star with fictional planets
        {
            "name": "Felskern", "type": "Terrestrial", "distance_au": 0.3, "mass_earth": 0.5,
            "radius_earth": 0.8, "orbital_period_days": 37, "temperature_k": 700,
            "atmosphere": "Virtually none", "discovery_year": "Future", "confirmed": False
        },
        {
            "name": "Ninurta", "type": "Gas Giant", "distance_au": 1.2, "mass_earth": 477,
            "radius_earth": 11.0, "orbital_period_days": 511, "temperature_k": 180,
            "atmosphere": "H2, He (Saturn-like)", "discovery_year": "Future", "confirmed": False
        },
        {
            "name": "Stahlburgh", "type": "Terrestrial", "distance_au": 1.4, "mass_earth": 1.0,
            "radius_earth": 1.0, "orbital_period_days": 657, "temperature_k": 285,
            "atmosphere": "N2, O2, CO2 (700ppm)", "discovery_year": "Future", "confirmed": False,
            "moons": [
                {
                    "name": "Eisenwald", "type": "Rocky", "mass_earth": 0.5, "radius_earth": 0.8,
                    "orbital_distance_km": 60000, "orbital_period_days": 6, "temperature_k": 320,
                    "atmosphere": "CO2/CH4/H2O-rich, 1.7 atm", "description": "Hothouse jungle moon, biodiverse trade port"
                }
            ]
        },
        {
            "name": "Ashur", "type": "Gas Giant", "distance_au": 5.0, "mass_earth": 222,
            "radius_earth": 9.0, "orbital_period_days": 4380, "temperature_k": 100,
            "atmosphere": "H2, He (Jupiter-like)", "discovery_year": "Future", "confirmed": False
        },
        {
            "name": "Eiswelt", "type": "Ice Giant", "distance_au": 10.0, "mass_earth": 3.0,
            "radius_earth": 1.7, "orbital_period_days": 11677, "temperature_k": 50,
            "atmosphere": "H2, He, CH4, NH3", "discovery_year": "Future", "confirmed": False
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