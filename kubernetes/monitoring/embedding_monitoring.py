#!/usr/bin/env python3
"""
Embedding Service Monitoring Script for Phase 3

Monitors:
1. Embedding throughput (vectors/sec) - target 250+
2. Neo4j memory usage with 85% alert
3. Embedding queue depth (Redis)
4. Worker replica scaling status
5. GC behavior and memory trends

Run with:
    python embedding_monitoring.py --interval 10 --duration 3600

Or deploy as Kubernetes CronJob for continuous monitoring.
"""

import json
import time
import logging
import argparse
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmbeddingMonitor:
    """Monitor embedding service metrics and health."""

    def __init__(
        self,
        redis_host: str = 'localhost',
        redis_port: int = 6379,
        neo4j_uri: str = 'bolt://localhost:7687',
        neo4j_user: str = 'neo4j',
        neo4j_password: str = 'password',
        prometheus_url: str = 'http://localhost:9090'
    ):
        """Initialize monitoring client."""
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.prometheus_url = prometheus_url

        self.metrics_history = {
            'throughput': [],
            'neo4j_memory': [],
            'queue_depth': [],
            'worker_replicas': [],
            'gc_events': []
        }

    def query_redis_queue_depth(self) -> Optional[int]:
        """
        Get embedding queue depth from Redis.

        Query: LLEN embedding:queue
        """
        try:
            import redis
            r = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=True
            )
            depth = r.llen('embedding:queue')
            logger.info(f"Queue depth: {depth} items")
            self.metrics_history['queue_depth'].append({
                'timestamp': datetime.now().isoformat(),
                'value': depth
            })
            return depth
        except Exception as e:
            logger.error(f"Failed to query Redis: {e}")
            return None

    def query_neo4j_memory(self) -> Optional[Dict]:
        """
        Get Neo4j memory metrics.

        Query: CALL dbms.queryJmx("java.lang:type=Memory") YIELD attributes
        """
        try:
            from neo4j import GraphDatabase

            driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )

            with driver.session() as session:
                result = session.run(
                    """
                    CALL dbms.queryJmx("java.lang:type=Memory") YIELD attributes
                    UNWIND attributes as attr
                    RETURN attr.name as metric_name, attr.value.value as value
                    """
                )

                memory_data = {}
                for record in result:
                    metric_name = record['metric_name']
                    value = record['value']
                    memory_data[metric_name] = value

            # Calculate usage percentage
            if 'HeapMemoryUsage' in memory_data:
                heap = memory_data['HeapMemoryUsage']
                used = heap.get('used', 0)
                max_mem = heap.get('max', 1)
                usage_pct = (used / max_mem) * 100

                logger.info(
                    f"Neo4j Memory: {used/1024/1024:.1f}MB / "
                    f"{max_mem/1024/1024:.1f}MB ({usage_pct:.1f}%)"
                )

                # Alert if > 85%
                if usage_pct > 85:
                    logger.warning(
                        f"ALERT: Neo4j heap memory > 85% ({usage_pct:.1f}%)"
                    )

                self.metrics_history['neo4j_memory'].append({
                    'timestamp': datetime.now().isoformat(),
                    'used_mb': used / 1024 / 1024,
                    'max_mb': max_mem / 1024 / 1024,
                    'usage_pct': usage_pct
                })

                return {
                    'used_mb': used / 1024 / 1024,
                    'max_mb': max_mem / 1024 / 1024,
                    'usage_pct': usage_pct
                }

            driver.close()

        except Exception as e:
            logger.error(f"Failed to query Neo4j: {e}")
            return None

    def query_embedding_throughput(self) -> Optional[float]:
        """
        Calculate embedding throughput from Prometheus.

        Query: rate(embedding_vectors_processed_total[1m])
        """
        try:
            import requests

            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={
                    'query': 'rate(embedding_vectors_processed_total[1m])'
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success' and data['data']['result']:
                    throughput = float(data['data']['result'][0]['value'][1])
                    logger.info(f"Embedding throughput: {throughput:.1f} vec/sec")

                    if throughput < 200:
                        logger.warning(
                            f"ALERT: Throughput below target "
                            f"({throughput:.1f} < 250)"
                        )

                    self.metrics_history['throughput'].append({
                        'timestamp': datetime.now().isoformat(),
                        'value': throughput
                    })

                    return throughput

        except Exception as e:
            logger.error(f"Failed to query Prometheus: {e}")

        return None

    def query_worker_replicas(self) -> Optional[Dict]:
        """
        Get current and desired worker replica counts.

        Queries Kubernetes API for HPA status.
        """
        try:
            from kubernetes import client, config

            config.load_incluster_config()
            v2_api = client.AutoscalingV2Api()

            hpa = v2_api.read_namespaced_horizontal_pod_autoscaler(
                name='embedding-worker-hpa',
                namespace='quran-system'
            )

            current_replicas = hpa.status.current_replicas
            desired_replicas = hpa.status.desired_replicas
            max_replicas = hpa.spec.max_replicas
            min_replicas = hpa.spec.min_replicas

            logger.info(
                f"Worker replicas: {current_replicas} current, "
                f"{desired_replicas} desired (range: {min_replicas}-{max_replicas})"
            )

            self.metrics_history['worker_replicas'].append({
                'timestamp': datetime.now().isoformat(),
                'current': current_replicas,
                'desired': desired_replicas,
                'min': min_replicas,
                'max': max_replicas
            })

            return {
                'current': current_replicas,
                'desired': desired_replicas,
                'min': min_replicas,
                'max': max_replicas
            }

        except Exception as e:
            logger.error(f"Failed to query Kubernetes: {e}")
            return None

    def query_gc_metrics(self) -> Optional[Dict]:
        """Get Python GC metrics from workers."""
        try:
            import requests

            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={
                    'query': 'increase(python_gc_collections_total[5m])'
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success' and data['data']['result']:
                    total_collections = sum(
                        float(r['value'][1])
                        for r in data['data']['result']
                    )

                    logger.info(f"GC collections (5m): {total_collections:.0f}")

                    self.metrics_history['gc_events'].append({
                        'timestamp': datetime.now().isoformat(),
                        'collections_5m': total_collections
                    })

                    return {'collections_5m': total_collections}

        except Exception as e:
            logger.error(f"Failed to query GC metrics: {e}")

        return None

    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'alerts': [],
            'recommendations': []
        }

        # Throughput metric
        throughput = self.query_embedding_throughput()
        if throughput is not None:
            report['metrics']['throughput_vec_sec'] = throughput
            if throughput >= 250:
                report['alerts'].append({
                    'level': 'success',
                    'message': f'Target throughput achieved: {throughput:.1f} vec/sec'
                })
            elif throughput >= 200:
                report['alerts'].append({
                    'level': 'warning',
                    'message': f'Throughput {throughput:.1f} vec/sec, target is 250+'
                })
            else:
                report['alerts'].append({
                    'level': 'critical',
                    'message': f'Throughput {throughput:.1f} vec/sec is critically low'
                })
                report['recommendations'].append(
                    'Increase worker replicas or check for queue backlog'
                )

        # Neo4j memory metric
        neo4j_mem = self.query_neo4j_memory()
        if neo4j_mem is not None:
            report['metrics']['neo4j_memory'] = neo4j_mem
            if neo4j_mem['usage_pct'] > 85:
                report['alerts'].append({
                    'level': 'critical',
                    'message': f"Neo4j memory > 85%: {neo4j_mem['usage_pct']:.1f}%"
                })
                report['recommendations'].append(
                    'Reduce batch size or enable query cache'
                )
            elif neo4j_mem['usage_pct'] > 70:
                report['alerts'].append({
                    'level': 'warning',
                    'message': f"Neo4j memory trending high: {neo4j_mem['usage_pct']:.1f}%"
                })

        # Queue depth metric
        queue_depth = self.query_redis_queue_depth()
        if queue_depth is not None:
            report['metrics']['queue_depth'] = queue_depth
            if queue_depth > 1000:
                report['alerts'].append({
                    'level': 'critical',
                    'message': f'Queue depth overflow: {queue_depth} items'
                })
                report['recommendations'].append(
                    'Scale up worker replicas immediately'
                )
            elif queue_depth > 500:
                report['alerts'].append({
                    'level': 'warning',
                    'message': f'Queue accumulating: {queue_depth} items'
                })

        # Worker replicas metric
        replicas = self.query_worker_replicas()
        if replicas is not None:
            report['metrics']['worker_replicas'] = replicas
            if replicas['current'] < replicas['desired']:
                report['alerts'].append({
                    'level': 'info',
                    'message': f"Scaling: {replicas['current']} → {replicas['desired']} replicas"
                })
            elif replicas['current'] == 2:
                report['recommendations'].append(
                    'Consider increasing replicas if throughput is below target'
                )

        # GC metrics
        gc_data = self.query_gc_metrics()
        if gc_data is not None:
            report['metrics']['gc_collections_5m'] = gc_data['collections_5m']

        return report

    def run_continuous_monitoring(self, interval: int = 10, duration: int = 3600):
        """
        Run continuous monitoring loop.

        Args:
            interval: Seconds between collection cycles
            duration: Total duration in seconds (0 = infinite)
        """
        start_time = time.time()
        cycle = 0

        logger.info(f"Starting monitoring (interval={interval}s, duration={duration}s)")

        while True:
            cycle += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"Monitoring cycle {cycle}")
            logger.info(f"{'='*60}")

            report = self.generate_health_report()

            # Print summary
            for alert in report['alerts']:
                logger.log(
                    logging.WARNING if alert['level'] == 'warning' else logging.INFO,
                    f"[{alert['level'].upper()}] {alert['message']}"
                )

            if report['recommendations']:
                logger.info("Recommendations:")
                for rec in report['recommendations']:
                    logger.info(f"  - {rec}")

            # Check duration limit
            if duration > 0:
                elapsed = time.time() - start_time
                if elapsed >= duration:
                    logger.info(f"Monitoring duration ({duration}s) reached")
                    break

            # Save report
            self.save_report(report)

            # Wait for next cycle
            time.sleep(interval)

    def save_report(self, report: Dict):
        """Save report to JSON file."""
        report_dir = Path('/tmp/embedding_monitoring')
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = report_dir / f'report_{timestamp}.json'

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.debug(f"Report saved: {filepath}")

    def generate_summary(self) -> Dict:
        """Generate summary from collected metrics history."""
        summary = {
            'collection_duration': (
                (self.metrics_history['throughput'][-1]['timestamp']
                 if self.metrics_history['throughput'] else None)
                if self.metrics_history['throughput'] else None
            ),
            'total_samples': len(self.metrics_history['throughput']),
            'throughput': {},
            'neo4j_memory': {},
            'queue_depth': {},
            'scaling_events': len(self.metrics_history['worker_replicas'])
        }

        # Throughput stats
        if self.metrics_history['throughput']:
            values = [m['value'] for m in self.metrics_history['throughput']]
            import statistics
            summary['throughput'] = {
                'min': min(values),
                'max': max(values),
                'avg': statistics.mean(values),
                'final': values[-1],
                'target': 250
            }

        # Neo4j memory stats
        if self.metrics_history['neo4j_memory']:
            pcts = [m['usage_pct'] for m in self.metrics_history['neo4j_memory']]
            import statistics
            summary['neo4j_memory'] = {
                'min_pct': min(pcts),
                'max_pct': max(pcts),
                'avg_pct': statistics.mean(pcts),
                'final_pct': pcts[-1],
                'alert_threshold': 85
            }

        # Queue depth stats
        if self.metrics_history['queue_depth']:
            values = [m['value'] for m in self.metrics_history['queue_depth']]
            import statistics
            summary['queue_depth'] = {
                'min': min(values),
                'max': max(values),
                'avg': statistics.mean(values),
                'final': values[-1],
                'alert_threshold': 1000
            }

        logger.info("\n" + "="*60)
        logger.info("MONITORING SUMMARY")
        logger.info("="*60)
        logger.info(json.dumps(summary, indent=2, default=str))

        return summary


def main():
    parser = argparse.ArgumentParser(
        description='Monitor Phase 3 Embedding Service'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Seconds between monitoring cycles'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=3600,
        help='Total monitoring duration in seconds (0=infinite)'
    )
    parser.add_argument(
        '--redis-host',
        default='localhost',
        help='Redis host'
    )
    parser.add_argument(
        '--redis-port',
        type=int,
        default=6379,
        help='Redis port'
    )
    parser.add_argument(
        '--neo4j-uri',
        default='bolt://localhost:7687',
        help='Neo4j connection URI'
    )
    parser.add_argument(
        '--neo4j-user',
        default='neo4j',
        help='Neo4j username'
    )
    parser.add_argument(
        '--neo4j-password',
        default='password',
        help='Neo4j password'
    )
    parser.add_argument(
        '--prometheus-url',
        default='http://localhost:9090',
        help='Prometheus URL'
    )

    args = parser.parse_args()

    monitor = EmbeddingMonitor(
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        neo4j_uri=args.neo4j_uri,
        neo4j_user=args.neo4j_user,
        neo4j_password=args.neo4j_password,
        prometheus_url=args.prometheus_url
    )

    try:
        monitor.run_continuous_monitoring(
            interval=args.interval,
            duration=args.duration
        )
        monitor.generate_summary()
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
        monitor.generate_summary()
        sys.exit(0)


if __name__ == '__main__':
    main()
