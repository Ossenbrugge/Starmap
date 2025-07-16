"""
Database schema definitions for MontyDB collections
"""

from datetime import datetime


class StarSchema:
    """Schema for stars collection"""
    
    @staticmethod
    def create_document(star_data):
        """Create a star document from pandas row or dict"""
        return {
            '_id': int(star_data['id']),
            'catalog_data': {
                'hip': star_data.get('hip'),
                'hd': star_data.get('hd'),
                'hr': star_data.get('hr'),
                'gl': star_data.get('gl'),
                'bf': star_data.get('bf'),
                'bayer': star_data.get('bayer'),
                'flamsteed': star_data.get('flam'),
                'uuid': star_data.get('UUID')
            },
            'names': {
                'primary_name': star_data.get('primary_name', f"Star {star_data['id']}"),
                'proper_name': star_data.get('proper'),
                'all_names': star_data.get('all_names', []),
                'catalog_ids': star_data.get('catalog_ids', []),
                'designation_type': star_data.get('designation_type', 'catalog'),
                'fictional_name': star_data.get('fictional_name'),
                'fictional_source': star_data.get('fictional_source'),
                'fictional_description': star_data.get('fictional_description')
            },
            'coordinates': {
                'x': float(star_data.get('x', 0)),
                'y': float(star_data.get('y', 0)),
                'z': float(star_data.get('z', 0)),
                'ra': float(star_data.get('ra', 0)),
                'dec': float(star_data.get('dec', 0)),
                'dist': float(star_data.get('dist', 0))
            },
            'physical_properties': {
                'magnitude': float(star_data.get('mag', 0)),
                'absolute_magnitude': float(star_data.get('absmag', 0)),
                'spectral_class': star_data.get('spect', ''),
                'color_index': float(star_data.get('ci', 0)),
                'luminosity': float(star_data.get('lum', 1.0)),
                'mass': star_data.get('mass'),
                'radius': star_data.get('radius'),
                'temperature': star_data.get('temperature')
            },
            'motion': {
                'proper_motion_ra': float(star_data.get('pmra', 0)),
                'proper_motion_dec': float(star_data.get('pmdec', 0)),
                'radial_velocity': float(star_data.get('rv', 0)),
                'velocity_x': float(star_data.get('vx', 0)),
                'velocity_y': float(star_data.get('vy', 0)),
                'velocity_z': float(star_data.get('vz', 0))
            },
            'classification': {
                'constellation': star_data.get('con'),
                'constellation_full': star_data.get('constellation_full'),
                'component': star_data.get('comp'),
                'component_primary': star_data.get('comp_primary'),
                'base': star_data.get('base'),
                'variable': star_data.get('var'),
                'variable_min': star_data.get('var_min'),
                'variable_max': star_data.get('var_max')
            },
            'habitability': {
                'score': float(star_data.get('habitability_score', 0.0)),
                'category': star_data.get('habitability_category', 'Unknown'),
                'exploration_priority': star_data.get('exploration_priority', 'Unknown'),
                'breakdown': star_data.get('habitability_breakdown', {}),
                'parsed_spectral_type': star_data.get('parsed_spectral_type', ('Unknown', 0, 'V'))
            },
            'political': {
                'nation_id': None,  # Will be populated from nation data
                'controlled_by': None,
                'capital_of': None,
                'strategic_importance': 'normal'
            },
            'exoplanets': {
                'count': len(star_data.get('exoplanets', [])),
                'has_planets': star_data.get('has_exoplanets', False),
                'planets': star_data.get('exoplanets', [])
            },
            'metadata': {
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'data_source': 'migration',
                'version': '1.0'
            }
        }


class NationSchema:
    """Schema for nations collection"""
    
    @staticmethod
    def create_document(nation_id, nation_data):
        """Create a nation document"""
        return {
            '_id': nation_id,
            'name': nation_data['name'],
            'full_name': nation_data['full_name'],
            'government': {
                'type': nation_data['government_type'],
                'established_year': nation_data['established_year'],
                'political_alignment': nation_data.get('political_alignment'),
                'diplomatic_stance': nation_data.get('diplomatic_stance')
            },
            'capital': {
                'system': nation_data['capital_system'],
                'star_id': nation_data['capital_star_id'],
                'planet': nation_data['capital_planet']
            },
            'territories': nation_data.get('territories', []),
            'appearance': {
                'color': nation_data['color'],
                'border_color': nation_data['border_color']
            },
            'economy': {
                'focus': nation_data.get('economic_focus'),
                'specialties': nation_data.get('specialties', []),
                'population': nation_data.get('population'),
                'gdp': nation_data.get('gdp'),
                'trade_volume': nation_data.get('trade_volume')
            },
            'military': {
                'strength': nation_data.get('military_strength'),
                'doctrine': nation_data.get('military_doctrine'),
                'fleet_size': nation_data.get('fleet_size')
            },
            'description': nation_data['description'],
            'metadata': {
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'data_source': 'migration',
                'version': '1.0'
            }
        }


class TradeRouteSchema:
    """Schema for trade_routes collection"""
    
    @staticmethod
    def create_document(route_data):
        """Create a trade route document"""
        return {
            '_id': route_data['name'].replace(' ', '_').replace('-', '_').lower(),
            'name': route_data['name'],
            'route_type': route_data['route_type'],
            'established': route_data['established'],
            'endpoints': {
                'from': {
                    'star_id': route_data['from_star_id'],
                    'system': route_data['from_system']
                },
                'to': {
                    'star_id': route_data['to_star_id'],
                    'system': route_data['to_system']
                }
            },
            'logistics': {
                'cargo_types': route_data.get('cargo_types', []),
                'travel_time_days': route_data.get('travel_time_days', 0),
                'frequency': route_data.get('frequency', 'Unknown'),
                'capacity': route_data.get('capacity'),
                'cost_per_unit': route_data.get('cost_per_unit')
            },
            'control': {
                'controlling_nation': route_data.get('controlling_nation'),
                'security_level': route_data.get('security_level', 'Standard'),
                'patrol_frequency': route_data.get('patrol_frequency'),
                'customs_checkpoints': route_data.get('customs_checkpoints', [])
            },
            'economics': {
                'economic_zone': route_data.get('economic_zone'),
                'trade_volume': route_data.get('trade_volume'),
                'revenue': route_data.get('revenue'),
                'regions': route_data.get('regions', [])
            },
            'description': route_data.get('description', ''),
            'metadata': {
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'data_source': 'migration',
                'version': '1.0'
            }
        }


class StellarRegionSchema:
    """Schema for stellar_regions collection"""
    
    @staticmethod
    def create_document(region_data):
        """Create a stellar region document"""
        return {
            '_id': region_data['name'].replace(' ', '_').lower(),
            'name': region_data['name'],
            'short_name': region_data['short_name'],
            'description': region_data['description'],
            'boundaries': {
                'x_range': region_data['x_range'],
                'y_range': region_data['y_range'],
                'z_range': region_data['z_range'],
                'center_point': region_data['center_point'],
                'diameter': region_data['diameter']
            },
            'appearance': {
                'color': region_data['color'],
                'octant_number': region_data['octant_number']
            },
            'properties': {
                'classification': region_data['classification'],
                'established': region_data['established'],
                'brightest_star': region_data['brightest_star'],
                'brightest_star_id': region_data['brightest_star_id'],
                'brightest_star_magnitude': region_data['brightest_star_magnitude']
            },
            'statistics': {
                'total_stars': 0,  # Will be calculated
                'inhabited_systems': 0,
                'nation_controlled': 0,
                'trade_routes': 0
            },
            'metadata': {
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'data_source': 'migration',
                'version': '1.0'
            }
        }


class PlanetarySystemSchema:
    """Schema for planetary_systems collection"""
    
    @staticmethod
    def create_document(star_id, system_data):
        """Create a planetary system document"""
        return {
            '_id': star_id,
            'star_id': star_id,
            'system_name': system_data.get('system_name'),
            'planets': system_data.get('planets', []),
            'habitable_worlds': system_data.get('habitable_worlds', []),
            'total_planets': len(system_data.get('planets', [])),
            'has_life': system_data.get('has_life', False),
            'colonized': system_data.get('colonized', False),
            'population': system_data.get('population', 0),
            'government': system_data.get('government'),
            'economy': system_data.get('economy'),
            'description': system_data.get('description', ''),
            'metadata': {
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'data_source': 'migration',
                'version': '1.0'
            }
        }


class ExoplanetSchema:
    """Schema for exoplanets collection"""
    
    @staticmethod
    def create_document(planet_data):
        """Create an exoplanet document from CSV data"""
        return {
            '_id': planet_data.get('pl_name', '').replace(' ', '_').lower(),
            'name': planet_data.get('pl_name', ''),
            'letter': planet_data.get('pl_letter', ''),
            'host_star': {
                'name': planet_data.get('hostname', ''),
                'hip_id': planet_data.get('host_hip_id'),
                'hd_id': planet_data.get('host_hd_id'),
                'gaia_id': planet_data.get('host_gaia_id'),
                'tic_id': planet_data.get('host_tic_id'),
                'distance_pc': planet_data.get('host_distance_pc'),
                'coordinates': {
                    'ra': planet_data.get('host_ra_deg') or planet_data.get('sky_coord_ra'),
                    'dec': planet_data.get('host_dec_deg') or planet_data.get('sky_coord_dec')
                },
                'properties': {
                    'v_magnitude': planet_data.get('host_v_magnitude'),
                    'k_magnitude': planet_data.get('host_k_magnitude'),
                    'temperature_k': planet_data.get('host_temperature_k'),
                    'radius_solar': planet_data.get('host_radius_solar'),
                    'mass_solar': planet_data.get('host_mass_solar'),
                    'metallicity': planet_data.get('host_metallicity'),
                    'spectral_type': planet_data.get('host_spectral_type')
                }
            },
            'orbital_properties': {
                'period_days': planet_data.get('orbital_period_days'),
                'semi_major_axis_au': planet_data.get('semi_major_axis_au'),
                'eccentricity': planet_data.get('orbital_eccentricity'),
                'inclination_deg': planet_data.get('pl_orbincl'),
                'longitude_periastron_deg': planet_data.get('pl_orblper'),
                'time_periastron_jd': planet_data.get('pl_orbtper')
            },
            'physical_properties': {
                'radius_earth': planet_data.get('planet_radius_earth'),
                'radius_jupiter': planet_data.get('planet_radius_jupiter'),
                'mass_earth': planet_data.get('planet_mass_earth'),
                'mass_jupiter': planet_data.get('planet_mass_jupiter'),
                'density_g_cm3': planet_data.get('pl_dens'),
                'equilibrium_temperature_k': planet_data.get('equilibrium_temperature_k'),
                'insolation_earth': planet_data.get('insolation_earth')
            },
            'discovery': {
                'year': planet_data.get('discovery_year'),
                'method': planet_data.get('discovery_method'),
                'facility': planet_data.get('discovery_facility'),
                'publication_date': planet_data.get('disc_pubdate'),
                'reference': planet_data.get('pl_refname')
            },
            'habitability': {
                'potentially_habitable': planet_data.get('potentially_habitable', False),
                'habitable_zone_au': planet_data.get('habitable_zone_au'),
                'planet_type': planet_data.get('planet_type', 'Unknown')
            },
            'detection_flags': {
                'transit': planet_data.get('tran_flag', 0) == 1,
                'radial_velocity': planet_data.get('rv_flag', 0) == 1,
                'astrometry': planet_data.get('ast_flag', 0) == 1,
                'imaging': planet_data.get('ima_flag', 0) == 1,
                'microlensing': planet_data.get('micro_flag', 0) == 1
            },
            'metadata': {
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'data_source': 'exoplanet_archive',
                'version': '1.0',
                'confirmed': planet_data.get('soltype', '') == 'Published Confirmed'
            }
        }


class MetadataSchema:
    """Schema for metadata collection"""
    
    @staticmethod
    def create_document(metadata_type, data):
        """Create a metadata document"""
        return {
            '_id': metadata_type,
            'type': metadata_type,
            'data': data,
            'last_updated': datetime.utcnow(),
            'version': '1.0'
        }