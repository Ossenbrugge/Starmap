"""
Base Repository - Unified Data Access Layer
Provides common patterns and utilities for all repositories
"""

import time
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from functools import wraps
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RepositoryCache:
    """Simple in-memory cache with TTL support"""

    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data if not expired"""
        if key in self.cache:
            cached_item = self.cache[key]
            if time.time() - cached_item['timestamp'] < cached_item['ttl']:
                return cached_item['data']
            else:
                # Remove expired item
                del self.cache[key]
        return None

    def set(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Set cache item with TTL"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl or self.default_ttl
        }

    def clear(self) -> None:
        """Clear all cached items"""
        self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_items = len(self.cache)
        expired_items = sum(1 if time.time() - item['timestamp'] >= item['ttl'] else 0
                          for item in self.cache.values())

        # Clean up expired items
        for key in list(self.cache.keys()):
            if time.time() - self.cache[key]['timestamp'] >= self.cache[key]['ttl']:
                del self.cache[key]

        return {
            'total_items': len(self.cache),
            'expired_items': expired_items,
            'hit_rate': 'N/A',  # Would need hit/miss counters for full stats
            'memory_usage': 'N/A'  # Would need to calculate actual memory usage
        }


class RepositoryMetrics:
    """Performance monitoring for repository operations"""

    def __init__(self):
        self.operation_counts: Dict[str, int] = {}
        self.operation_times: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}

    def record_operation(self, operation: str, duration: float, success: bool = True) -> None:
        """Record operation metrics"""
        # Count operations
        self.operation_counts[operation] = self.operation_counts.get(operation, 0) + 1

        # Record timing
        if operation not in self.operation_times:
            self.operation_times[operation] = []
        self.operation_times[operation].append(duration)

        # Keep only last 100 timings per operation
        if len(self.operation_times[operation]) > 100:
            self.operation_times[operation].pop(0)

        # Record errors
        if not success:
            self.error_counts[operation] = self.error_counts.get(operation, 0) + 1

    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get performance stats for a specific operation"""
        if operation not in self.operation_times:
            return {'error': 'No data available for operation'}

        times = self.operation_times[operation]
        return {
            'operation': operation,
            'total_calls': self.operation_counts.get(operation, 0),
            'error_count': self.error_counts.get(operation, 0),
            'avg_duration_ms': sum(times) / len(times) * 1000,
            'min_duration_ms': min(times) * 1000,
            'max_duration_ms': max(times) * 1000,
            'recent_calls': len(times)
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """Get all performance statistics"""
        stats = {}
        for operation in self.operation_times.keys():
            stats[operation] = self.get_operation_stats(operation)
        return stats


def with_metrics(operation_name: str):
    """Decorator to add performance monitoring to repository methods"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()

            try:
                result = func(self, *args, **kwargs)
                success = result.get('success', True) if isinstance(result, dict) else True
                duration = time.time() - start_time

                # Record metrics
                if hasattr(self, 'metrics'):
                    self.metrics.record_operation(operation_name, duration, success)

                logger.debug(f"Operation '{operation_name}' completed in {duration:.3f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                if hasattr(self, 'metrics'):
                    self.metrics.record_operation(operation_name, duration, False)

                logger.error(f"Operation '{operation_name}' failed after {duration:.3f}s: {str(e)}")
                raise

        return wrapper
    return decorator


def with_caching(cache_key_prefix: str, ttl: Optional[int] = None):
    """Decorator to add caching to repository methods"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, 'cache'):
                return func(self, *args, **kwargs)

            # Generate cache key from function name and arguments
            cache_key = f"{cache_key_prefix}:{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"

            # Try to get from cache first
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result

            # Execute function and cache result
            result = func(self, *args, **kwargs)

            if isinstance(result, dict) and result.get('success', False):
                self.cache.set(cache_key, result, ttl)
                logger.debug(f"Cached result for key: {cache_key}")

            return result

        return wrapper
    return decorator



class BaseRepository(ABC):
    """Base repository class with common functionality"""

    def __init__(self, cache: Optional[RepositoryCache] = None, enable_cache: bool = True):
        """Initialize base repository with caching and metrics"""
        self.cache = cache or RepositoryCache()
        self.metrics = RepositoryMetrics()
        self.enable_cache = enable_cache
        self.logger = logging.getLogger(self.__class__.__name__)

        # Try to import database modules
        self._setup_database_imports()

    def _setup_database_imports(self):
        """Set up database imports with fallback handling"""
        try:
            from database.config import get_collection_stats, get_database
            self.MONTYDB_AVAILABLE = True
            self.get_database = get_database
            self.get_collection_stats = get_collection_stats
        except ImportError:
            self.MONTYDB_AVAILABLE = False
            self.get_database = None
            self.get_collection_stats = None

    @abstractmethod
    def _get_model_class(self) -> Any:
        """Return the model class for this repository"""
        pass

    @abstractmethod
    def _get_model_import_path(self) -> str:
        """Return the import path for the model class"""
        pass

    def _load_model(self):
        """Load the model class with error handling"""
        try:
            model_path = self._get_model_import_path()
            module_path, class_name = model_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            model_class = getattr(module, class_name)
            return model_class()
        except (ImportError, AttributeError) as e:
            self.logger.warning(f"Could not load enhanced model: {e}")
            return None

    @with_metrics("get_cache_stats")
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if hasattr(self, 'cache') and self.cache:
            return {'success': True, 'data': self.cache.get_stats()}
        return {
            'success': False,
            'error': 'Caching not enabled or available'
        }

    @with_metrics("get_performance_stats")
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            'success': True,
            'data': self.metrics.get_all_stats()
        }

    def clear_cache(self) -> Dict[str, Any]:
        """Clear the cache"""
        if hasattr(self, 'cache') and self.cache:
            self.cache.clear()
            return {'success': True, 'message': 'Cache cleared successfully'}
        return {
            'success': False,
            'error': 'Caching not enabled or available'
        }

    def _handle_database_error(self, operation: str, error: Exception) -> Dict[str, Any]:
        """Standardized database error handling"""
        error_msg = f'Database error in {operation}: {str(error)}'
        self.logger.error(error_msg)
        return {'success': False, 'error': error_msg}

    def _validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> Optional[str]:
        """Validate that required fields are present in data"""
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}"
        return None

    def _create_cache_key(self, operation: str, *args, **kwargs) -> str:
        """Create a consistent cache key"""
        args_str = "_".join(str(arg) for arg in args)
        kwargs_str = "_".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return f"{operation}_{args_str}_{kwargs_str}".strip("_")


# Global instances for shared use
_shared_cache = RepositoryCache()
_shared_metrics = RepositoryMetrics()
