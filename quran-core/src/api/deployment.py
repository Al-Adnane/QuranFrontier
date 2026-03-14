"""
PHASE 3: Deployment infrastructure
Implements:
- Graceful shutdown handling
- Prometheus metrics collection
- Health checks
- Dependency verification
"""

import asyncio
import signal
import time
from contextlib import asynccontextmanager
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, HTTPException, status
import logging

logger = logging.getLogger(__name__)

# Prometheus metrics
request_count = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

embedding_queue = Gauge(
    'embedding_queue_size',
    'Size of pending embedding processing queue'
)

graph_query_count = Counter(
    'graph_queries_total',
    'Total Neo4j graph queries',
    ['query_type']
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

db_connection_pool = Gauge(
    'db_connection_pool_size',
    'Current database connection pool size',
    ['database']
)


class GracefulShutdown:
    """Handle graceful shutdown of services"""

    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.in_flight_requests = 0
        self.start_time = time.time()

    def register_signal_handlers(self):
        """Register SIGTERM/SIGINT handlers"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    async def shutdown(self):
        """Graceful shutdown sequence"""
        logger.info("Starting graceful shutdown...")

        # Stop accepting new requests
        self.shutdown_event.set()

        # Wait for in-flight requests to complete
        max_wait = 30  # seconds
        start = time.time()
        while self.in_flight_requests > 0 and (time.time() - start) < max_wait:
            logger.info(f"Waiting for {self.in_flight_requests} in-flight requests...")
            await asyncio.sleep(1)

        if self.in_flight_requests > 0:
            logger.warning(f"Timeout: {self.in_flight_requests} requests still in-flight")
        else:
            logger.info("All in-flight requests completed")

        logger.info("Graceful shutdown complete")

    async def track_request(self, call_next):
        """Track request for graceful shutdown"""
        # Check if shutdown initiated
        if self.shutdown_event.is_set():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Server shutting down"
            )

        self.in_flight_requests += 1
        try:
            response = await call_next
            return response
        finally:
            self.in_flight_requests -= 1

    def uptime_seconds(self) -> float:
        """Get uptime in seconds"""
        return time.time() - self.start_time


class MetricsMiddleware:
    """Collect Prometheus metrics for all requests"""

    @staticmethod
    async def middleware(request: Request, call_next):
        """Track request metrics"""
        start_time = time.time()
        method = request.method
        endpoint = request.url.path

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time

            # Record metrics
            request_count.labels(
                method=method,
                endpoint=endpoint,
                status=status_code
            ).inc()

            request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            logger.debug(f"{method} {endpoint} - {status_code} ({duration:.3f}s)")

        return response


class HealthCheck:
    """Health check for all dependencies"""

    @staticmethod
    async def check_postgresql() -> Dict[str, Any]:
        """Check PostgreSQL connectivity"""
        try:
            import psycopg2
            import os
            conn = psycopg2.connect(os.getenv("DATABASE_URL", ""))
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            conn.close()
            return {"status": "healthy", "service": "postgresql"}
        except Exception as e:
            logger.error(f"PostgreSQL check failed: {e}")
            return {"status": "unhealthy", "service": "postgresql", "error": str(e)}

    @staticmethod
    async def check_redis() -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            import redis
            import os
            r = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379))
            )
            r.ping()
            return {"status": "healthy", "service": "redis"}
        except Exception as e:
            logger.error(f"Redis check failed: {e}")
            return {"status": "unhealthy", "service": "redis", "error": str(e)}

    @staticmethod
    async def check_neo4j() -> Dict[str, Any]:
        """Check Neo4j connectivity"""
        try:
            from neo4j import GraphDatabase
            import os
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            auth = (
                os.getenv("NEO4J_USER", "neo4j"),
                os.getenv("NEO4J_PASSWORD", "password")
            )
            driver = GraphDatabase.driver(uri, auth=auth)
            driver.verify_connectivity()
            driver.close()
            return {"status": "healthy", "service": "neo4j"}
        except Exception as e:
            logger.error(f"Neo4j check failed: {e}")
            return {"status": "unhealthy", "service": "neo4j", "error": str(e)}

    @staticmethod
    async def full_health_check() -> Dict[str, Any]:
        """Check all dependencies"""
        checks = await asyncio.gather(
            HealthCheck.check_postgresql(),
            HealthCheck.check_redis(),
            HealthCheck.check_neo4j()
        )

        overall_status = "healthy" if all(c["status"] == "healthy" for c in checks) else "degraded"
        return {
            "status": overall_status,
            "dependencies": checks,
            "timestamp": time.time()
        }

    @staticmethod
    async def readiness_check() -> Dict[str, Any]:
        """Check if service is ready to accept traffic"""
        health = await HealthCheck.full_health_check()

        required_services = ["postgresql", "redis", "neo4j"]
        available = {c["service"]: c["status"] for c in health["dependencies"]}

        ready = all(available.get(svc) == "healthy" for svc in required_services)

        return {
            "ready": ready,
            "health": health,
            "message": "Service is ready" if ready else "Service dependencies unhealthy"
        }


class MetricsExporter:
    """Export metrics in Prometheus format"""

    @staticmethod
    def export_metrics() -> bytes:
        """Generate Prometheus metrics output"""
        return generate_latest()

    @staticmethod
    def update_embedding_queue(size: int):
        """Update embedding queue gauge"""
        embedding_queue.set(size)

    @staticmethod
    def record_graph_query(query_type: str):
        """Record graph query"""
        graph_query_count.labels(query_type=query_type).inc()

    @staticmethod
    def record_cache_hit(cache_type: str):
        """Record cache hit"""
        cache_hits.labels(cache_type=cache_type).inc()

    @staticmethod
    def update_connection_pool(database: str, size: int):
        """Update connection pool gauge"""
        db_connection_pool.labels(database=database).set(size)


@asynccontextmanager
async def lifespan_handler(app):
    """
    Handle application startup and shutdown

    Usage in FastAPI:
        app = FastAPI(lifespan=lifespan_handler)
    """
    # Startup
    logger.info("=== QuranFrontier API Starting ===")
    shutdown = GracefulShutdown()
    shutdown.register_signal_handlers()

    # Verify dependencies
    logger.info("Checking dependencies...")
    health = await HealthCheck.full_health_check()
    logger.info(f"Health check: {health['status']}")

    yield

    # Shutdown
    logger.info("=== QuranFrontier API Stopping ===")
    await shutdown.shutdown()
    logger.info("Shutdown complete")
