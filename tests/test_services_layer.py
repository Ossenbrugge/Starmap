"""
Test Services Layer - Unit Tests for Business Logic Services
Tests all services in the new architecture
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


class TestStarService:
    """Test StarService functionality"""

    @patch('app.services.star_service.StarRepository')
    def test_get_star_by_id_success(self, mock_repo):
        """Test successful star retrieval by ID"""
        from app.services.star_service import StarService

        # Setup mock
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_id.return_value = {
            'success': True,
            'data': {'id': '1', 'name': 'Test Star', 'magnitude': 4.5}
        }
        mock_repo.return_value = mock_repo_instance

        # Test service
        service = StarService()
        result = service.get_star_by_id('1')

        assert result['success'] is True
        assert result['data']['name'] == 'Test Star'
        mock_repo_instance.get_by_id.assert_called_once_with('1')

    @patch('app.services.star_service.StarRepository')
    def test_get_star_by_id_not_found(self, mock_repo):
        """Test star not found scenario"""
        from app.services.star_service import StarService

        # Setup mock
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_id.return_value = {
            'success': False,
            'error': 'Star not found'
        }
        mock_repo.return_value = mock_repo_instance

        # Test service
        service = StarService()
        result = service.get_star_by_id('999')

        assert result['success'] is False
        assert 'error' in result

    @patch('app.services.star_service.StarRepository')
    def test_search_stars(self, mock_repo):
        """Test star search functionality"""
        from app.services.star_service import StarService

        # Setup mock
        mock_repo_instance = MagicMock()
        mock_repo_instance.search.return_value = {
            'success': True,
            'data': [
                {'id': '1', 'name': 'Sirius', 'magnitude': -1.46},
                {'id': '2', 'name': 'Vega', 'magnitude': 0.03}
            ]
        }
        mock_repo.return_value = mock_repo_instance

        # Test service
        service = StarService()
        result = service.search_stars('query', filters={})

        assert result['success'] is True
        assert len(result['data']) == 2
        mock_repo_instance.search.assert_called_once()


class TestNationService:
    """Test NationService functionality"""

    @patch('app.services.nation_service.NationRepository')
    def test_get_nation_by_id_success(self, mock_repo):
        """Test successful nation retrieval"""
        from app.services.nation_service import NationService

        # Setup mock
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_id.return_value = {
            'success': True,
            'data': {'id': '1', 'name': 'Test Nation', 'capital': 'Capital City'}
        }
        mock_repo.return_value = mock_repo_instance

        # Test service
        service = NationService()
        result = service.get_nation_by_id('1')

        assert result['success'] is True
        assert result['data']['name'] == 'Test Nation'

    @patch('app.services.nation_service.NationRepository')
    def test_get_all_nations(self, mock_repo):
        """Test getting all nations"""
        from app.services.nation_service import NationService

        # Setup mock
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_all.return_value = {
            'success': True,
            'data': [
                {'id': '1', 'name': 'Nation A'},
                {'id': '2', 'name': 'Nation B'}
            ]
        }
        mock_repo.return_value = mock_repo_instance

        # Test service
        service = NationService()
        result = service.get_all_nations()

        assert result['success'] is True
        assert len(result['data']) == 2


class TestTradeRouteService:
    """Test TradeRouteService functionality"""

    @patch('app.services.trade_route_service.TradeRouteRepository')
    def test_get_trade_route_by_id_success(self, mock_repo):
        """Test successful trade route retrieval"""
        from app.services.trade_route_service import TradeRouteService

        # Setup mock
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_id.return_value = {
            'success': True,
            'data': {'id': '1', 'name': 'Trade Route 1', 'from_nation': 'A', 'to_nation': 'B'}
        }
        mock_repo.return_value = mock_repo_instance

        # Test service
        service = TradeRouteService()
        result = service.get_trade_route_by_id('1')

        assert result['success'] is True
        assert result['data']['name'] == 'Trade Route 1'

    @patch('app.services.trade_route_service.TradeRouteRepository')
    def test_calculate_route_efficiency(self, mock_repo):
        """Test route efficiency calculation"""
        from app.services.trade_route_service import TradeRouteService

        # Setup service
        service = TradeRouteService()

        # Mock route data
        route = {
            'distance': 100,
            'trade_volume': 1000,
            'security_level': 0.8,
            'infrastructure_quality': 0.9
        }

        # Test efficiency calculation
        efficiency = service._calculate_efficiency(route)

        # Should return a valid efficiency score
        assert isinstance(efficiency, (int, float))
        assert 0 <= efficiency <= 1  # Should be between 0 and 1

    @patch('app.services.trade_route_service.TradeRouteRepository')
    def test_optimize_route(self, mock_repo):
        """Test route optimization"""
        from app.services.trade_route_service import TradeRouteService

        # Setup mock
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_by_id.return_value = {
            'success': True,
            'data': {
                'id': '1',
                'distance': 100,
                'trade_volume': 1000,
                'security_level': 0.5
            }
        }
        mock_repo.return_value = mock_repo_instance

        # Test service
        service = TradeRouteService()
        result = service.optimize_route('1')

        # Should return optimization suggestions
        assert 'success' in result


class TestAuthService:
    """Test AuthService functionality"""

    @patch('app.services.auth_service.UserRepository')
    def test_authenticate_user_success(self, mock_repo):
        """Test successful user authentication"""
        from app.services.auth_service import AuthService

        # Setup mock
        mock_repo_instance = MagicMock()
        mock_repo_instance.find_by_username.return_value = {
            'success': True,
            'data': {'username': 'testuser', 'password_hash': 'hashed_password', 'role': 'user'}
        }
        mock_repo.return_value = mock_repo_instance

        # Test service
        service = AuthService()

        # Mock password verification
        with patch('app.services.auth_service.verify_password', return_value=True):
            result = service.authenticate_user('testuser', 'password')

        assert result['success'] is True
        assert 'token' in result

    @patch('app.services.auth_service.UserRepository')
    def test_authenticate_user_failure(self, mock_repo):
        """Test failed user authentication"""
        from app.services.auth_service import AuthService

        # Setup mock
        mock_repo_instance = MagicMock()
        mock_repo_instance.find_by_username.return_value = {
            'success': False,
            'error': 'User not found'
        }
        mock_repo.return_value = mock_repo_instance

        # Test service
        service = AuthService()
        result = service.authenticate_user('nonexistent', 'password')

        assert result['success'] is False
        assert 'error' in result

    def test_validate_token_success(self):
        """Test successful token validation"""
        from app.services.auth_service import AuthService

        service = AuthService()

        # Mock a valid token structure
        with patch('app.services.auth_service.jwt.decode') as mock_decode:
            mock_decode.return_value = {'username': 'testuser', 'exp': 1234567890}

            result = service.validate_token('valid_token')

            assert result['success'] is True
            assert result['data'] == {'username': 'testuser', 'exp': 1234567890}

    def test_validate_token_failure(self):
        """Test failed token validation"""
        from app.services.auth_service import AuthService

        service = AuthService()

        # Mock token validation failure
        with patch('app.services.auth_service.jwt.decode') as mock_decode:
            mock_decode.side_effect = Exception("Invalid token")

            result = service.validate_token('invalid_token')

            assert result['success'] is False
            assert 'error' in result


class TestSearchService:
    """Test SearchService functionality"""

    @patch('app.services.search_service.StarService')
    @patch('app.services.search_service.NationService')
    def test_unified_search(self, mock_nation_service, mock_star_service):
        """Test unified search across multiple services"""
        from app.services.search_service import SearchService

        # Setup mocks
        mock_star_instance = MagicMock()
        mock_star_instance.search_stars.return_value = {
            'success': True,
            'data': [{'id': '1', 'name': 'Sirius'}]
        }
        mock_star_service.return_value = mock_star_instance

        mock_nation_instance = MagicMock()
        mock_nation_instance.search_nations.return_value = {
            'success': True,
            'data': [{'id': '1', 'name': 'Federation'}]
        }
        mock_nation_service.return_value = mock_nation_instance

        # Test service
        service = SearchService()
        result = service.unified_search('query')

        assert result['success'] is True
        assert 'stars' in result['data']
        assert 'nations' in result['data']

    def test_search_with_filters(self):
        """Test search with filters applied"""
        from app.services.search_service import SearchService

        service = SearchService()

        # Test filter validation
        filters = {'magnitude_max': 5.0, 'nation_id': '1'}
        processed_filters = service._process_search_filters(filters)

        assert 'magnitude' in processed_filters
        assert processed_filters['nation_id'] == '1'


class TestStatsService:
    """Test StatsService functionality"""

    @patch('app.services.stats_service.StarRepository')
    @patch('app.services.stats_service.NationRepository')
    @patch('app.services.stats_service.TradeRouteRepository')
    def test_get_system_stats(self, mock_trade_repo, mock_nation_repo, mock_star_repo):
        """Test system-wide statistics"""
        from app.services.stats_service import StatsService

        # Setup mocks
        for mock_repo in [mock_star_repo, mock_nation_repo, mock_trade_repo]:
            mock_instance = MagicMock()
            mock_instance.count.return_value = {'success': True, 'data': 10}
            mock_repo.return_value = mock_instance

        # Test service
        service = StatsService()
        result = service.get_system_stats()

        assert result['success'] is True
        assert 'stars_count' in result['data']
        assert 'nations_count' in result['data']
        assert 'trade_routes_count' in result['data']
        assert result['data']['stars_count'] == 10

    @patch('app.services.stats_service.StarRepository')
    def test_get_star_distribution(self, mock_repo):
        """Test star distribution statistics"""
        from app.services.stats_service import StatsService

        # Setup mock
        mock_instance = MagicMock()
        mock_instance.get_spectral_distribution.return_value = {
            'success': True,
            'data': {'O': 10, 'B': 20, 'A': 30}
        }
        mock_repo.return_value = mock_instance

        # Test service
        service = StatsService()
        result = service.get_star_distribution()

        assert result['success'] is True
        assert 'O' in result['data']
        assert 'B' in result['data']
