"""
Database Configuration - Phase 3 Database Optimization
Centralized database configuration and connection management
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    # Connection settings
    max_connections: int = 10
    connection_timeout: float = 30.0
    max_idle_time: float = 600.0  # 10 minutes

    # Performance settings
    enable_connection_pooling: bool = True
    enable_query_caching: bool = True
    enable_compression: bool = True

    # Cache settings
    cache_ttl: int = 300  # 5 minutes default
    cache_max_items: int = 1000

    # Monitoring settings
    enable_performance_monitoring: bool = True
    log_slow_queries: bool = True
    slow_query_threshold_ms: float = 100.0

    # Environment-specific settings
    environment: str = "development"

    @classmethod
    def from_environment(cls) -> 'DatabaseConfig':
        """Create configuration from environment variables"""
        return cls(
            max_connections=int(os.getenv('DB_MAX_CONNECTIONS', '10')),
            connection_timeout=float(os.getenv('DB_CONNECTION_TIMEOUT', '30.0')),
            max_idle_time=float(os.getenv('DB_MAX_IDLE_TIME', '600.0')),
            enable_connection_pooling=os.getenv('DB_ENABLE_POOLING', 'true').lower() == 'true',
            enable_query_caching=os.getenv('DB_ENABLE_CACHING', 'true').lower() == 'true',
            enable_compression=os.getenv('DB_ENABLE_COMPRESSION', 'true').lower() == 'true',
            cache_ttl=int(os.getenv('DB_CACHE_TTL', '300')),
            cache_max_items=int(os.getenv('DB_CACHE_MAX_ITEMS', '1000')),
            enable_performance_monitoring=os.getenv('DB_ENABLE_MONITORING', 'true').lower() == 'true',
            log_slow_queries=os.getenv('DB_LOG_SLOW_QUERIES', 'true').lower() == 'true',
            slow_query_threshold_ms=float(os.getenv('DB_SLOW_QUERY_THRESHOLD', '100.0')),
            environment=os.getenv('APP_ENV', 'development')
        )


class QueryOptimizer:
    """Database query optimization utilities"""

    @staticmethod
    def optimize_query_plan(query: Dict[str, Any], data_size: int) -> Dict[str, Any]:
        """
        Optimize query based on expected data size

        Args:
            query: Original query dictionary
            data_size: Expected result size

        Returns:
            Optimized query dictionary
        """
        optimized = query.copy()

        # Add database-specific optimizations
        if data_size > 1000:
            # For large datasets, ensure proper indexing hints
            optimized['_hint'] = {'$natural': 1}

        if data_size < 10:
            # For small datasets, use memory sorting
            optimized['_sort'] = {'$natural': 1}

        return optimized

    @staticmethod
    def estimate_result_size(query: Dict[str, Any], collection_stats: Dict[str, Any]) -> int:
        """
        Estimate result size for query optimization

        Args:
            query: Query dictionary
            collection_stats: Collection statistics

        Returns:
            Estimated result size
        """
        # Simple estimation based on collection size
        total_docs = collection_stats.get('count', 0)

        # Apply filters estimation (simplified)
        if query:
            # Estimate selectivity based on filter complexity
            filter_count = len(query)
            selectivity = max(0.01, min(1.0, 1.0 / (2 ** filter_count)))
            return int(total_docs * selectivity)

        return total_docs


class ConnectionPoolManager:
    """Database connection pool management"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pools: Dict[str, Any] = {}
        self._active_connections = 0

    def get_connection_pool(self, database_name: str) -> Optional[Any]:
        """
        Get or create connection pool for database

        Args:
            database_name: Name of the database

        Returns:
            Connection pool object or None
        """
        if not self.config.enable_connection_pooling:
            return None

        if database_name not in self._pools:
            # Create new connection pool
            self._pools[database_name] = self._create_pool(database_name)

        return self._pools[database_name]

    def _create_pool(self, database_name: str) -> Any:
        """Create a new connection pool"""
        # This would integrate with actual database connection library
        # For now, return a placeholder
        return {
            'database': database_name,
            'max_connections': self.config.max_connections,
            'active_connections': 0,
            'created_at': os.times()[4] if hasattr(os, 'times') else 0
        }

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            'total_pools': len(self._pools),
            'active_connections': self._active_connections,
            'pool_details': self._pools
        }

    def close_all_pools(self) -> None:
        """Close all connection pools"""
        for pool in self._pools.values():
            # Close pool connections
            pass
        self._pools.clear()


# Global configuration instance
_db_config = DatabaseConfig.from_environment()
_connection_pool_manager = ConnectionPoolManager(_db_config)


def get_database_config() -> DatabaseConfig:
    """Get global database configuration"""
    return _db_config


def get_connection_pool_manager() -> ConnectionPoolManager:
    """Get global connection pool manager"""
    return _connection_pool_manager


def reset_database_config() -> None:
    """Reset database configuration (for testing)"""
    global _db_config, _connection_pool_manager
    _db_config = DatabaseConfig.from_environment()
    _connection_pool_manager = ConnectionPoolManager(_db_config)
