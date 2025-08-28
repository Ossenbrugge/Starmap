"""
Test Repository Layer - Unit Tests for Repository Pattern Implementation
Tests all repositories in the new architecture
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.repositories.base_repository import RepositoryCache, RepositoryMetrics


class TestRepositoryCache:
    """Test RepositoryCache functionality"""

    def test_cache_initialization(self):
        """Test cache initializes correctly"""
        cache = RepositoryCache()
        assert cache.default_ttl == 300
        assert isinstance(cache.cache, dict)
        assert len(cache.cache) == 0

    def test_cache_set_and_get(self):
        """Test setting and getting cache values"""
        cache = RepositoryCache()

        # Set a value
        cache.set('test_key', {'data': 'test_value'})

        # Get the value
        result = cache.get('test_key')
        assert result == {'data': 'test_value'}

    def test_cache_expiration(self):
        """Test cache expiration"""
        cache = RepositoryCache(default_ttl=1)  # 1 second TTL

        # Set a value
        cache.set('test_key', {'data': 'test_value'})

        # Sleep for more than TTL
        import time
        time.sleep(1.1)

        # Value should be expired
        result = cache.get('test_key')
        assert result is None

    def test_cache_clear(self):
        """Test cache clearing"""
        cache = RepositoryCache()

        # Set multiple values
        cache.set('key1', {'data': 'value1'})
        cache.set('key2', {'data': 'value2'})

        # Clear cache
        cache.clear()

        # Both should be None
        assert cache.get('key1') is None
        assert cache.get('key2') is None

    def test_cache_stats(self):
        """Test cache statistics"""
        cache = RepositoryCache()

        stats = cache.get_stats()
        assert 'total_items' in stats
        assert 'expired_items' in stats
        assert stats['total_items'] == 0


class TestRepositoryMetrics:
    """Test RepositoryMetrics functionality"""

    def test_metrics_initialization(self):
        """Test metrics initializes correctly"""
        metrics = RepositoryMetrics()

        assert isinstance(metrics.operation_counts, dict)
        assert isinstance(metrics.operation_times, dict)
        assert isinstance(metrics.error_counts, dict)

    def test_record_operation_success(self):
        """Test recording successful operations"""
        metrics = RepositoryMetrics()

        # Record a successful operation
        metrics.record_operation('test_op', 0.123, success=True)

        # Check counts
        assert metrics.operation_counts['test_op'] == 1
        assert len(metrics.operation_times['test_op']) == 1
        assert metrics.operation_times['test_op'][0] == 0.123
        assert metrics.error_counts['test_op'] == 0

    def test_record_operation_failure(self):
        """Test recording failed operations"""
        metrics = RepositoryMetrics()

        # Record a failed operation
        metrics.record_operation('test_op', 0.456, success=False)

        # Check counts
        assert metrics.operation_counts['test_op'] == 1
        assert len(metrics.operation_times['test_op']) == 1
        assert metrics.error_counts['test_op'] == 1

    def test_get_operation_stats(self):
        """Test getting operation statistics"""
        metrics = RepositoryMetrics()

        # Record some operations
        metrics.record_operation('test_op', 0.1, success=True)
        metrics.record_operation('test_op', 0.2, success=True)
        metrics.record_operation('test_op', 0.3, success=False)

        stats = metrics.get_operation_stats('test_op')

        assert stats['operation'] == 'test_op'
        assert stats['total_calls'] == 3
        assert stats['error_count'] == 1
        assert stats['avg_duration_ms'] == 200.0  # (0.1 + 0.2 + 0.3) / 3 * 1000

    def test_get_all_stats(self):
        """Test getting all statistics"""
        metrics = RepositoryMetrics()

        # Record operations for different operations
        metrics.record_operation('op1', 0.1, success=True)
        metrics.record_operation('op2', 0.2, success=True)

        stats = metrics.get_all_stats()

        assert 'op1' in stats
        assert 'op2' in stats
        assert len(stats) == 2


class TestBaseRepository:
    """Test BaseRepository common functionality"""

    def test_base_repository_initialization(self):
        """Test basic repository initialization"""
        from app.repositories.base_repository import BaseRepository

        # We can't instantiate BaseRepository directly since it's abstract
        # This test would need to be implemented by concrete repositories
        pass

    def test_validate_required_fields(self):
        """Test field validation in repository"""
        from app.repositories.base_repository import BaseRepository

        # Create a mock repository
        mock_repo = MagicMock(spec=BaseRepository)

        # Add the validation method to the mock
        from app.repositories.base_repository import BaseRepository
        BaseRepository._validate_required_fields(mock_repo, {}, [])

        # Test with missing fields
        result = BaseRepository._validate_required_fields(
            mock_repo, {'field1': 'value1'}, ['field1', 'field2']
        )
        assert result == "Missing required fields: field2"

        # Test with all fields present
        result = BaseRepository._validate_required_fields(
            mock_repo, {'field1': 'value1', 'field2': 'value2'}, ['field1', 'field2']
        )
        assert result is None
