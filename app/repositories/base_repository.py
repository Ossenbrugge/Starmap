"""
Base Repository - Clean Architecture Foundation Layer
Abstract base class for all repository implementations with proper database connection management
"""

import abc
from typing import Any, Dict, List, Optional, Callable
from contextlib import contextmanager
import time
from dataclasses import dataclass
from collections import Counter
from datetime import datetime, timedelta
import threading
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# Decorators for repository operations
def with_caching(func: Callable) -> Callable:
    """
    Decorator to add caching behavior to repository methods
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.cache_enabled:
            return func(self, *args, **kwargs)

        # Create cache key from function name and arguments
        key = f"{func.__name__}:{self.create_cache_key(*args, **kwargs)}"

        # Try to get from cache first
        cached_result = self.get_from_cache(key)
        if cached_result is not None:
            return cached_result

        # Execute function and cache result
        result = func(self, *args, **kwargs)
        if isinstance(result, dict) and result.get('success', False):
            self.set_cache(key, result)

        return result
    return wrapper

def with_metrics(func: Callable) -> Callable:
    """
    Decorator to add metrics collection to repository methods
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with self.timed_operation(func.__name__):
            return func(self, *args, **kwargs)
    return wrapper

@dataclass
class RepositoryCache:
    """Simple LRU cache for repository operations"""
    max_size: int = 1000
    ttl_minutes: int = 30

    def __post_init__(self):
        self.cache = {}
        self.access_count = {}
        self.max_age = timedelta(minutes=self.ttl_minutes)
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if datetime.now() - entry['timestamp'] < self.max_age:
                    self.access_count[key] = self.access_count.get(key, 0) + 1
                    return entry['value']
                else:
                    del self.cache[key]
                    del self.access_count[key]
            return None

    def set(self, key: str, value: Any) -> None:
        """Set value in cache with eviction"""
        with self.lock:
            if len(self.cache) >= self.max_size:
                # Evict least recently accessed
                oldest_key = min(self.access_count.keys(),
                               key=lambda k: self.access_count[k])
                if oldest_key:
                    del self.cache[oldest_key]
                    del self.access_count[oldest_key]

            self.cache[key] = {'value': value, 'timestamp': datetime.now()}
            self.access_count[key] = 1

    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.access_count.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                'entries': len(self.cache),
                'max_size': self.max_size,
                'ttl_minutes': self.ttl_minutes,
                'hit_rate': sum(self.access_count.values()) / max(len(self.access_count), 1)
            }

@dataclass
class RepositoryMetrics:
    """Metrics collection for repository operations"""
    def __post_init__(self):
        self.operation_counts: Counter = Counter()
        self.operation_times: Dict[str, List[float]] = {}
        self.error_counts: Counter = Counter()
        self.lock = threading.Lock()

    def record_operation(self, operation: str, duration_ms: float, success: bool = True) -> None:
        """Record an operation with duration"""
        with self.lock:
            self.operation_counts[operation] += 1
            if operation not in self.operation_times:
                self.operation_times[operation] = []
            self.operation_times[operation].append(duration_ms)

            # Keep only last 100 timings
            if len(self.operation_times[operation]) > 100:
                self.operation_times[operation] = self.operation_times[operation][-100:]

            if not success:
                self.error_counts[operation] += 1

    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for a specific operation"""
        with self.lock:
            if operation not in self.operation_counts:
                return self._empty_stats(operation)

            timings = self.operation_times.get(operation, [])
            count = self.operation_counts[operation]
            error_count = self.error_counts[operation]

            stats = {
                'operation': operation,
                'total_calls': count,
                'error_count': error_count,
                'success_rate': (count - error_count) / max(count, 1) * 100
            }

            if timings:
                stats.update({
                    'avg_duration_ms': sum(timings) / len(timings),
                    'min_duration_ms': min(timings),
                    'max_duration_ms': max(timings),
                    'median_duration_ms': sorted(timings)[len(timings) // 2]
                })
            else:
                stats.update({
                    'avg_duration_ms': 0.0,
                    'min_duration_ms': 0.0,
                    'max_duration_ms': 0.0,
                    'median_duration_ms': 0.0
                })

            return stats

    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all operations"""
        with self.lock:
            all_stats = {}
            for operation in self.operation_counts.keys():
                all_stats[operation] = self.get_operation_stats(operation)
            return all_stats

    def _empty_stats(self, operation: str) -> Dict[str, Any]:
        """Return empty stats structure"""
        return {
            'operation': operation,
            'total_calls': 0,
            'error_count': 0,
            'success_rate': 0.0,
            'avg_duration_ms': 0.0,
            'min_duration_ms': 0.0,
            'max_duration_ms': 0.0,
            'median_duration_ms': 0.0
        }

class RepositoryError(Exception):
    """Base exception for repository operations"""
    pass

class ConnectionError(RepositoryError):
    """Database connection error"""
    pass

class ValidationError(RepositoryError):
    """Data validation error"""
    pass

class AbstractBaseRepository(abc.ABC):
    """
    Abstract base class for all repository implementations.

    Provides common functionality and enforces consistent patterns across
    all data access operations in the clean architecture.
    """

    def __init__(self, database=None, cache_enabled: bool = True):
        """Initialize repository with database connection"""
        self.database = database
        self.cache = RepositoryCache() if cache_enabled else None
        self.metrics = RepositoryMetrics()
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def cache_enabled(self) -> bool:
        """Check if caching is enabled"""
        return self.cache is not None

    @abc.abstractmethod
    def get_by_id(self, id: Any) -> Dict[str, Any]:
        """Retrieve entity by ID"""
        pass

    @abc.abstractmethod
    def get_all(self) -> Dict[str, Any]:
        """Retrieve all entities"""
        pass

    @abc.abstractmethod
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new entity"""
        pass

    @abc.abstractmethod
    def update(self, id: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing entity"""
        pass

    @abc.abstractmethod
    def delete(self, id: Any) -> Dict[str, Any]:
        """Delete entity by ID"""
        pass

    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that all required fields are present in data

        Args:
            data: The data to validate
            required_fields: List of required field names

        Raises:
            ValidationError: If any required field is missing
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)

        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

    @contextmanager
    def timed_operation(self, operation_name: str):
        """Context manager to time repository operations"""
        start_time = time.time()
        try:
            yield
            duration_ms = (time.time() - start_time) * 1000
            self.metrics.record_operation(operation_name, duration_ms, success=True)
            self.logger.debug(f"{operation_name} completed in {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.metrics.record_operation(operation_name, duration_ms, success=False)
            self.logger.error(f"{operation_name} failed after {duration_ms:.2f}ms: {str(e)}")
            raise

    def create_cache_key(self, *args, **kwargs) -> str:
        """Create a cache key from arguments"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return "|".join(key_parts)

    def _load_model(self):
        """Load the model class for this repository - to be overridden by subclasses"""
        return None

    def _handle_database_error(self, operation: str, error: Exception) -> Dict[str, Any]:
        """Handle database errors consistently"""
        error_msg = f"Database error in {operation}: {str(error)}"
        self.logger.error(error_msg)
        return {'success': False, 'error': error_msg}

    def get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if enabled and available"""
        if self.cache_enabled and self.cache:
            return self.cache.get(key)
        return None

    def set_cache(self, key: str, value: Any) -> None:
        """Set value in cache if enabled"""
        if self.cache_enabled and self.cache:
            self.cache.set(key, value)

    def clear_cache(self) -> None:
        """Clear cache if enabled"""
        if self.cache_enabled and self.cache:
            self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if self.cache_enabled and self.cache:
            return self.cache.get_stats()
        return {'enabled': False}

    def get_metrics(self) -> Dict[str, Any]:
        """Get operation metrics"""
        return self.metrics.get_all_stats()

    def health_check(self) -> Dict[str, Any]:
        """Health check for repository and dependencies"""
        try:
            # Test basic connectivity
            health_status = {
                'repository': self.__class__.__name__,
                'status': 'healthy',
                'cache_enabled': self.cache_enabled,
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    'total_operations': sum(self.metrics.operation_counts.values()),
                    'error_rate': sum(self.metrics.error_counts.values()) /
                                max(sum(self.metrics.operation_counts.values()), 1) * 100
                }
            }

            if self.database:
                health_status['database'] = 'connected'

            return health_status
        except Exception as e:
            return {
                'repository': self.__class__.__name__,
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def __repr__(self) -> str:
        """String representation of the repository"""
        return f"{self.__class__.__name__}(cache={self.cache_enabled})"


# Alias for backward compatibility
BaseRepository = AbstractBaseRepository
