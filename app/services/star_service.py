"""
Star Service - Business Logic Layer
Handles star-related operations with clean separation of concerns
"""

import math
from typing import Dict, List, Any, Optional
from app.repositories.star_repository import StarRepository


class StarService:
    """Service for star business logic operations"""

    def __init__(self, star_repository: Optional[StarRepository] = None):
        self.star_repository = star_repository or StarRepository()

    def get_stars(self, limit: int = 1000, mag_limit: float = 8.0,
                  spectral_type: str = "") -> Dict[str, Any]:
        """Get stars with filtering and business logic"""
        try:
            if limit < 1 or limit > 50000:
                return {'success': False, 'error': 'Limit must be between 1 and 50000'}

            if mag_limit < -2.0 or mag_limit > 15.0:
                return {'success': False, 'error': 'Magnitude limit must be between -2.0 and 15.0'}

            spectral_type = spectral_type.upper().strip()
            valid_spectral = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
            if spectral_type and spectral_type[0] not in valid_spectral:
                return {'success': False, 'error': 'Invalid spectral type'}

            result = self.star_repository.get_stars(limit, mag_limit, spectral_type)

            if not result['success']:
                return result

            stars = result['data']
            client_stars = [self._convert_star_to_client_format(star) for star in stars]

            return {'success': True, 'data': client_stars}

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve stars: {str(e)}'}

    def get_filtered_stars(self, count_limit: Optional[int] = None,
                           mag_limit: Optional[float] = None,
                           spectral_type: Optional[str] = None,
                           constellation: Optional[str] = None) -> Dict[str, Any]:
        """Get stars with filtering parameters"""
        return self.get_stars(
            limit=count_limit or 1000,
            mag_limit=mag_limit or 8.0,
            spectral_type=spectral_type or ""
        )

    def get_stars_paginated(self, page: int = 1, limit: int = 1000,
                            mag_limit: float = 8.0, spectral_type: str = "",
                            constellation: str = "") -> Dict[str, Any]:
        """Get paginated stars; returns {success, data, total}."""
        try:
            if mag_limit < -2.0 or mag_limit > 15.0:
                return {'success': False, 'error': 'Magnitude limit must be between -2.0 and 15.0'}

            spectral_type = spectral_type.upper().strip()
            valid_spectral = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
            if spectral_type and spectral_type[0] not in valid_spectral:
                return {'success': False, 'error': 'Invalid spectral type'}

            db = self.star_repository.database
            if not db:
                return {'success': False, 'error': 'Database not available'}

            rows, total = db.get_stars_paginated(
                page=page, limit=limit, mag_limit=mag_limit,
                spectral_type=spectral_type, constellation=constellation,
            )
            client_stars = [self._convert_star_to_client_format(s) for s in rows]
            return {'success': True, 'data': client_stars, 'total': total}

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve stars: {str(e)}'}

    def get_star_by_id(self, star_id: int) -> Dict[str, Any]:
        """Get detailed information for a specific star by ID"""
        return self.get_star_details(star_id)

    def search_stars(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search stars by name or properties"""
        try:
            result = self.star_repository.search_stars(query, limit) if hasattr(self.star_repository, 'search_stars') else {'success': False}
            if result.get('success'):
                return result
        except Exception:
            pass

        # Fallback: search through already-loaded data in the db singleton
        try:
            from app_refactored import get_database
            db = get_database()
            raw = db.search_stars(query, limit)
            client = [self._convert_star_to_client_format(s) for s in raw]
            return {'success': True, 'data': client, 'count': len(client)}
        except Exception as e:
            return {'success': False, 'error': f'Search failed: {str(e)}'}

    def get_stars_in_radius(self, x: float, y: float, z: float, radius: float) -> Dict[str, Any]:
        """Get stars within specified radius of coordinates"""
        try:
            all_stars_result = self.get_filtered_stars(count_limit=25000)
            if not all_stars_result['success']:
                return all_stars_result

            nearby_stars = []
            for star in all_stars_result['data']:
                try:
                    distance = math.sqrt(
                        (float(star.get('x', 0)) - x) ** 2 +
                        (float(star.get('y', 0)) - y) ** 2 +
                        (float(star.get('z', 0)) - z) ** 2
                    )
                    if distance <= radius:
                        star['distance_from_center'] = distance
                        nearby_stars.append(star)
                except (ValueError, TypeError):
                    continue

            nearby_stars.sort(key=lambda s: s['distance_from_center'])

            return {
                'success': True,
                'data': nearby_stars,
                'search_center': {'x': x, 'y': y, 'z': z},
                'search_radius': radius,
                'count': len(nearby_stars)
            }

        except Exception as e:
            return {'success': False, 'error': f'Radius search failed: {str(e)}'}

    def get_star_details(self, star_id: int) -> Dict[str, Any]:
        """Get detailed information for a specific star"""
        try:
            result = self.star_repository.get_star_by_id(star_id)
            if not result['success']:
                return result

            star = result['data']
            if not star:
                return {'success': False, 'error': 'Star not found'}

            trade_result = self.star_repository.get_trade_routes_by_star(star_id)
            trade_routes = trade_result.get('data', []) if trade_result['success'] else []

            return {
                'success': True,
                'data': {
                    **self._convert_star_to_client_format(star),
                    'trade_routes': [
                        {
                            'id': r.get('_id', r.get('id')),
                            'name': r.get('name'),
                            'route_type': r.get('route_type'),
                        }
                        for r in trade_routes
                    ]
                }
            }

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve star details: {str(e)}'}

    def get_fictional_exoplanets(self) -> Dict[str, Any]:
        """Get fictional exoplanets"""
        try:
            return self.star_repository.get_fictional_exoplanets()
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve fictional exoplanets: {str(e)}'}

    def get_exoplanets(self) -> Dict[str, Any]:
        """Get real exoplanets"""
        try:
            return self.star_repository.get_exoplanets()
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve exoplanets: {str(e)}'}

    def get_stars_by_nation(self, nation_id: str) -> Dict[str, Any]:
        """Get all stars controlled by a nation"""
        try:
            result = self.star_repository.get_stars_by_nation(nation_id)
            if not result['success']:
                return result
            client_stars = [self._convert_star_to_client_format(s) for s in result['data']]
            return {'success': True, 'data': client_stars}
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve stars by nation: {str(e)}'}

    def get_fictional_stars(self) -> Dict[str, Any]:
        """Get all fictional stars"""
        try:
            return self.star_repository.get_fictional_stars()
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve fictional stars: {str(e)}'}

    def add_fictional_star(self, star_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new fictional star"""
        try:
            required_fields = ['name', 'x', 'y', 'z']
            if not all(field in star_data for field in required_fields):
                return {'success': False, 'error': 'Missing required fields: name, x, y, z'}

            for coord in ['x', 'y', 'z']:
                value = star_data.get(coord, 0)
                if not isinstance(value, (int, float)) or abs(value) > 1000.0:
                    return {'success': False, 'error': f'Invalid {coord} coordinate'}

            result = self.star_repository.add_fictional_star(star_data)
            if result['success']:
                return {'success': True, 'data': result['data']}
            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to add fictional star: {str(e)}'}

    def delete_fictional_star(self, star_id: int) -> Dict[str, Any]:
        """Delete a fictional star"""
        try:
            result = self.star_repository.delete_fictional_star(star_id)
            if result['success']:
                return {'success': True, 'message': 'Fictional star deleted successfully'}
            return result
        except Exception as e:
            return {'success': False, 'error': f'Failed to delete fictional star: {str(e)}'}

    def add_fictional_exoplanet(self, exoplanet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new fictional exoplanet"""
        try:
            required_fields = ['name', 'star_name', 'distance', 'period']
            if not all(field in exoplanet_data for field in required_fields):
                return {'success': False, 'error': 'Missing required fields: name, star_name, distance, period'}

            result = self.star_repository.add_fictional_exoplanet(exoplanet_data)
            if result['success']:
                return {'success': True, 'data': result['data']}
            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to add fictional exoplanet: {str(e)}'}

    def _convert_star_to_client_format(self, star: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert star data to client-friendly format.
        Handles both the nested format (physical_properties, coordinates, etc.)
        and the flat format (direct x, y, z, magnitude, etc.) from the Database class.
        """
        # ── Nested format (structured JSON) ──────────────────────────────────
        if 'coordinates' in star and isinstance(star['coordinates'], dict):
            coords = star['coordinates']
            names = star.get('names', {}) or {}
            phys = star.get('physical_properties', {}) or {}
            classification = star.get('classification', {}) or {}
            exoplanets_info = star.get('exoplanets', {}) or {}

            return {
                'id': star.get('_id', star.get('id')),
                'name': self._get_best_star_name(star),
                'fictional_name': names.get('fictional_name'),
                'fictional_description': names.get('fictional_description'),
                'x': coords.get('x', 0),
                'y': coords.get('y', 0),
                'z': coords.get('z', 0),
                'distance': coords.get('dist', coords.get('distance', 0)),
                'magnitude': phys.get('magnitude', star.get('magnitude', star.get('mag', 0))),
                'spectral_class': phys.get('spectral_class', star.get('spectral_class', '')),
                'constellation': classification.get('constellation', star.get('constellation', '')),
                'exoplanet_count': exoplanets_info.get('count', 0),
                'has_planets': exoplanets_info.get('has_planets', False),
                'is_fictional': star.get('is_fictional', False),
            }

        # ── Flat format (CSV-derived or simple JSON) ──────────────────────────
        return {
            'id': star.get('id', star.get('_id')),
            'name': star.get('name', star.get('proper', f"Star {star.get('id', '?')}")),
            'fictional_name': star.get('fictional_name'),
            'fictional_description': star.get('fictional_description'),
            'x': float(star.get('x', 0) or 0),
            'y': float(star.get('y', 0) or 0),
            'z': float(star.get('z', 0) or 0),
            'distance': float(star.get('distance', star.get('dist', 0)) or 0),
            'magnitude': float(star.get('magnitude', star.get('mag', 0)) or 0),
            'spectral_class': star.get('spectral_class', star.get('spect', '')),
            'constellation': star.get('constellation', star.get('con', '')),
            'exoplanet_count': 0,
            'has_planets': False,
            'is_fictional': star.get('is_fictional', False),
            'nation_id': star.get('nation_id', ''),
            # Astrogation fields — the details panel surfaces everything the
            # catalog knows: designations, photometry and sky position.
            'absolute_magnitude': star.get('absolute_magnitude'),
            'color_index': star.get('color_index'),
            'ra': star.get('ra'),
            'dec': star.get('dec'),
            'hip': star.get('hip'),
            'hd': star.get('hd'),
            'bayer': star.get('bayer'),
            'flamsteed': star.get('flamsteed'),
            # Era/lore fields — the frontend gates names, labels and nation
            # colors on these; luminosity drives the system-map habitable zone.
            'proper_name': star.get('proper_name', ''),
            'discovery_number': star.get('discovery_number'),
            'discovery_year': star.get('discovery_year'),
            'era_start': star.get('era_start'),
            'era_end': star.get('era_end'),
            'luminosity': star.get('luminosity'),
        }

    def _get_best_star_name(self, star: Dict[str, Any]) -> str:
        """Get the best available name for a star"""
        try:
            names = star.get('names', {}) or {}
            primary = names.get('primary_name', '')

            if not primary or primary in ('nan', 'nan; nan', 'NaN', ''):
                catalog_ids = names.get('catalog_ids', [])
                preferred = ['HD', 'HIP', 'Gliese', 'HR']
                for pref in preferred:
                    for cid in catalog_ids:
                        if str(cid).startswith(pref):
                            return str(cid)
                if catalog_ids:
                    return str(catalog_ids[0])

                classification = star.get('classification', {}) or {}
                constellation = classification.get('constellation', '')
                star_id = star.get('_id', '')
                return f"{constellation} {star_id}".strip() or f"Star {star_id}"

            return primary

        except Exception:
            return f"Star {star.get('_id', star.get('id', 'Unknown'))}"
