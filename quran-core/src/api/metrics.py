"""Prometheus metrics for Quran API.

Exposes standard application and system metrics for monitoring.
"""
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    start_http_server,
)
import time
from functools import wraps

# Request metrics
request_count = Counter(
    'api_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

# Error metrics
error_count = Counter(
    'api_errors_total',
    'Total API errors',
    ['error_type', 'endpoint']
)

# Database metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query latency in seconds',
    ['query_type'],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0)
)

db_connection_count = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

# Semantic search metrics
embedding_latency = Histogram(
    'embedding_latency_seconds',
    'Embedding generation latency in seconds',
    ['model'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

semantic_search_results = Histogram(
    'semantic_search_result_count',
    'Number of results returned by semantic search',
    buckets=(1, 5, 10, 25, 50, 100)
)

semantic_search_latency = Histogram(
    'semantic_search_latency_seconds',
    'Semantic search query latency in seconds',
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
)

# Neo4j metrics
graph_query_latency = Histogram(
    'graph_query_latency_seconds',
    'Knowledge graph query latency in seconds',
    ['query_type'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0)
)

graph_node_count = Gauge(
    'graph_nodes_total',
    'Total number of nodes in knowledge graph',
    ['node_type']
)

graph_relationship_count = Gauge(
    'graph_relationships_total',
    'Total number of relationships in knowledge graph',
    ['relationship_type']
)

# Cache metrics
cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# Feature flag metrics
feature_flag_status = Gauge(
    'feature_flag_enabled',
    'Feature flag enabled status',
    ['flag_name']
)


def track_request(endpoint: str):
    """Decorator to track HTTP request metrics."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            method = kwargs.get('method', 'UNKNOWN')
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                status = getattr(result, 'status_code', 200)
                request_count.labels(method=method, endpoint=endpoint, status=status).inc()
                return result
            except Exception as e:
                error_count.labels(error_type=type(e).__name__, endpoint=endpoint).inc()
                raise
            finally:
                duration = time.time() - start_time
                request_duration.labels(method=method, endpoint=endpoint).observe(duration)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            method = kwargs.get('method', 'UNKNOWN')
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                status = getattr(result, 'status_code', 200)
                request_count.labels(method=method, endpoint=endpoint, status=status).inc()
                return result
            except Exception as e:
                error_count.labels(error_type=type(e).__name__, endpoint=endpoint).inc()
                raise
            finally:
                duration = time.time() - start_time
                request_duration.labels(method=method, endpoint=endpoint).observe(duration)

        # Return appropriate wrapper based on function type
        if hasattr(func, '__await__'):
            return async_wrapper
        return sync_wrapper

    return decorator


def track_embedding(model: str):
    """Decorator to track embedding generation metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                embedding_latency.labels(model=model).observe(duration)
        return wrapper
    return decorator


def track_db_query(query_type: str):
    """Decorator to track database query metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                db_query_duration.labels(query_type=query_type).observe(duration)
        return wrapper
    return decorator


def track_graph_query(query_type: str):
    """Decorator to track knowledge graph query metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                graph_query_latency.labels(query_type=query_type).observe(duration)
        return wrapper
    return decorator


def initialize_metrics(port: int = 8001) -> None:
    """Initialize metrics server for Prometheus scraping.

    Args:
        port: Port to expose metrics on
    """
    try:
        start_http_server(port)
    except Exception as e:
        # If port is already in use, continue without metrics
        pass


def update_graph_statistics(stats: dict) -> None:
    """Update graph statistics gauges.

    Args:
        stats: Dictionary with node_types and relationship_types
    """
    if 'node_types' in stats:
        for node_type, count in stats['node_types'].items():
            graph_node_count.labels(node_type=node_type).set(count)

    if 'relationship_types' in stats:
        for rel_type, count in stats['relationship_types'].items():
            graph_relationship_count.labels(relationship_type=rel_type).set(count)


def update_feature_flags(flags: dict) -> None:
    """Update feature flag status gauges.

    Args:
        flags: Dictionary of feature flag names and values
    """
    for flag_name, enabled in flags.items():
        feature_flag_status.labels(flag_name=flag_name).set(1 if enabled else 0)
