"""
Memory Optimization Module for Phase 3 Embedding Service

Implements streaming embedding generation, memory-mapped vectors, and
garbage collection tuning to increase throughput from 120 vec/sec to 250+ vec/sec.

Key optimizations:
1. Streaming generator - don't hold full batch in memory
2. Memory-mapped vector storage for large datasets
3. Aggressive GC after 1000 vectors
4. Neo4j batch size increase (50 → 100) with connection pooling
"""

import gc
import logging
import mmap
import struct
from pathlib import Path
from typing import Generator, Dict, List, Optional, Tuple
import numpy as np
from contextlib import contextmanager
import time

logger = logging.getLogger(__name__)


class StreamingEmbeddingGenerator:
    """
    Generate embeddings in streaming fashion to minimize memory footprint.

    Key features:
    - Yields vectors one at a time instead of accumulating in memory
    - Integrates with Neo4j batching (100 verses per transaction)
    - Triggers GC every 1000 vectors
    - Tracks memory usage and throughput
    """

    def __init__(
        self,
        batch_size: int = 100,
        gc_interval: int = 1000,
        neo4j_batch_size: int = 100,
        connection_pool_timeout: int = 45
    ):
        """
        Initialize streaming generator.

        Args:
            batch_size: Vectors per batch (default 100)
            gc_interval: Force GC after N vectors (default 1000)
            neo4j_batch_size: Verses per Neo4j transaction (default 100)
            connection_pool_timeout: Connection pool timeout in seconds (default 45s)
        """
        self.batch_size = batch_size
        self.gc_interval = gc_interval
        self.neo4j_batch_size = neo4j_batch_size
        self.connection_pool_timeout = connection_pool_timeout
        self.vectors_processed = 0
        self.start_time = None
        self.checkpoint_time = None

    def stream_embeddings(
        self,
        texts: List[Dict],
        embedding_func
    ) -> Generator[Dict, None, None]:
        """
        Stream embeddings one vector at a time.

        Args:
            texts: List of text documents with metadata
            embedding_func: Function that takes text and returns embedding

        Yields:
            Dict with 'vector', 'metadata', 'throughput_vec_sec'
        """
        self.start_time = time.time()
        self.checkpoint_time = self.start_time
        self.vectors_processed = 0

        for idx, text_record in enumerate(texts):
            # Generate embedding
            vector = embedding_func(text_record['text'])

            # Validate vector
            if not self._is_valid_vector(vector):
                logger.warning(f"Invalid vector at index {idx}, skipping")
                continue

            self.vectors_processed += 1

            # Calculate throughput every 100 vectors
            if self.vectors_processed % 100 == 0:
                elapsed = time.time() - self.checkpoint_time
                throughput = 100 / elapsed if elapsed > 0 else 0
                logger.info(
                    f"Throughput: {throughput:.1f} vec/sec "
                    f"(total: {self.vectors_processed})"
                )

            # Force GC every N vectors to prevent memory bloat
            if self.vectors_processed % self.gc_interval == 0:
                gc.collect()
                logger.debug(f"GC triggered at {self.vectors_processed} vectors")

            yield {
                'vector': vector,
                'metadata': {
                    'index': idx,
                    'text_id': text_record.get('metadata_id', f'text_{idx}'),
                    'timestamp': time.time()
                },
                'throughput_vec_sec': self.vectors_processed / (
                    time.time() - self.start_time
                ) if time.time() > self.start_time else 0
            }

    @staticmethod
    def _is_valid_vector(vector) -> bool:
        """Validate embedding vector."""
        try:
            arr = np.array(vector, dtype=np.float32)
            return (
                len(arr) == 768 and
                np.all(np.isfinite(arr))
            )
        except Exception as e:
            logger.error(f"Vector validation error: {e}")
            return False

    def get_throughput(self) -> float:
        """Calculate current throughput in vectors/sec."""
        if not self.start_time or self.vectors_processed == 0:
            return 0.0
        elapsed = time.time() - self.start_time
        return self.vectors_processed / elapsed if elapsed > 0 else 0.0


class MemoryMappedVectorStore:
    """
    Store vectors using memory-mapped files for efficient disk/memory hybrid storage.

    Allows storing millions of vectors without loading all into RAM.
    """

    def __init__(self, filepath: str, max_vectors: int = 500000, dim: int = 768):
        """
        Initialize memory-mapped vector store.

        Args:
            filepath: Path to mmap file
            max_vectors: Maximum vectors to store
            dim: Embedding dimension (default 768)
        """
        self.filepath = Path(filepath)
        self.max_vectors = max_vectors
        self.dim = dim
        self.dtype = np.float32
        self.bytes_per_vector = dim * self.dtype().itemsize
        self.total_size = max_vectors * self.bytes_per_vector
        self.count = 0
        self.mmap_file = None
        self.metadata = {}

        self._init_mmap()

    def _init_mmap(self):
        """Initialize memory-mapped file."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not self.filepath.exists():
            with open(self.filepath, 'wb') as f:
                f.write(b'\x00' * self.total_size)
            logger.info(f"Created mmap file: {self.filepath} ({self.total_size} bytes)")

        # Open with mmap
        with open(self.filepath, 'r+b') as f:
            self.mmap_file = mmap.mmap(f.fileno(), 0)

    def add_vector(self, vector: np.ndarray, metadata: Optional[Dict] = None):
        """Add vector to store."""
        if self.count >= self.max_vectors:
            raise ValueError("Vector store is full")

        # Convert to float32
        vec = np.array(vector, dtype=self.dtype)

        # Write to mmap
        offset = self.count * self.bytes_per_vector
        self.mmap_file[offset:offset + self.bytes_per_vector] = vec.tobytes()

        # Store metadata
        if metadata:
            self.metadata[self.count] = metadata

        self.count += 1

    def get_vector(self, idx: int) -> np.ndarray:
        """Retrieve vector by index."""
        if idx >= self.count:
            raise IndexError(f"Index {idx} out of range")

        offset = idx * self.bytes_per_vector
        data = self.mmap_file[offset:offset + self.bytes_per_vector]
        return np.frombuffer(data, dtype=self.dtype).copy()

    def get_batch(self, start_idx: int, size: int) -> np.ndarray:
        """Retrieve batch of vectors efficiently."""
        end_idx = min(start_idx + size, self.count)
        batch_size = end_idx - start_idx

        offset = start_idx * self.bytes_per_vector
        batch_bytes = self.mmap_file[
            offset:offset + batch_size * self.bytes_per_vector
        ]

        return np.frombuffer(batch_bytes, dtype=self.dtype).reshape(
            batch_size, self.dim
        ).copy()

    def close(self):
        """Close memory-mapped file."""
        if self.mmap_file:
            self.mmap_file.close()

    def __del__(self):
        self.close()


class Neo4jBatchOptimizer:
    """
    Optimize Neo4j operations with larger batches and connection pooling.

    Changes from baseline:
    - Batch size: 50 → 100 verses per transaction
    - Connection pool timeout: 30s → 45s
    - Enable query cache for repeated lookups
    """

    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize Neo4j optimizer.

        Args:
            uri: Neo4j connection URI (bolt://...)
            user: Username
            password: Password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.batch_size = 100  # Increased from 50
        self.connection_pool_timeout = 45  # Increased from 30s
        self.query_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0

    @contextmanager
    def batch_transaction(self, session):
        """
        Context manager for batch transactions.

        Usage:
            with optimizer.batch_transaction(session) as tx:
                tx.run("CREATE (n) VALUES (...)")
        """
        tx = session.begin_transaction()
        try:
            yield tx
            tx.commit()
        except Exception as e:
            tx.rollback()
            logger.error(f"Batch transaction error: {e}")
            raise

    def create_batch_insert_query(
        self,
        vectors: List[np.ndarray],
        metadata: List[Dict]
    ) -> str:
        """
        Create optimized Cypher query for batch insertion.

        Inserts 100 vectors in single transaction.
        """
        values = []
        for i, (vec, meta) in enumerate(zip(vectors, metadata)):
            vec_str = str(vec.tolist())[:100] + "..."  # Truncate for logging
            values.append(f"""
                {{
                    id: {meta.get('text_id', i)},
                    dimension: {len(vec)},
                    norm: {float(np.linalg.norm(vec))},
                    verse: '{meta.get('verse', '')}',
                    text_type: '{meta.get('text_type', 'unknown')}'
                }}
            """)

        return f"""
            UNWIND [{', '.join(values)}] as item
            CREATE (v:Vector {{
                id: item.id,
                dimension: item.dimension,
                norm: item.norm,
                verse: item.verse,
                text_type: item.text_type,
                created_at: datetime()
            }})
            RETURN count(*) as created
        """

    def get_or_query(self, query_key: str, query: str, session) -> Optional[Dict]:
        """
        Cached query execution.

        Args:
            query_key: Cache key
            query: Cypher query
            session: Neo4j session
        """
        # Check cache
        if query_key in self.query_cache:
            self.cache_hits += 1
            return self.query_cache[query_key]

        # Execute and cache
        self.cache_misses += 1
        result = session.run(query).single()
        if result:
            self.query_cache[query_key] = dict(result)

        return result

    def get_cache_stats(self) -> Dict:
        """Get query cache statistics."""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate_pct': hit_rate,
            'cached_queries': len(self.query_cache)
        }


class GarbageCollectionOptimizer:
    """
    Tune Python garbage collection for embedding workloads.

    Strategy:
    - Set low collection thresholds to prevent heap bloat
    - Force collection every 1000 vectors
    - Monitor memory before/after collection
    """

    def __init__(self, collect_interval: int = 1000):
        """
        Initialize GC optimizer.

        Args:
            collect_interval: Vectors between forced collections
        """
        self.collect_interval = collect_interval
        self.collection_count = 0
        self.vectors_since_collection = 0
        self.memory_before = []
        self.memory_after = []

    def should_collect(self, vector_count: int) -> bool:
        """Check if GC should run."""
        self.vectors_since_collection = vector_count % self.collect_interval
        return self.vectors_since_collection == 0

    def run_collection(self) -> Dict:
        """
        Run garbage collection and return stats.

        Returns:
            Dict with memory deltas and collection stats
        """
        import psutil
        import os

        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        # Run collection
        collected = gc.collect()
        self.collection_count += 1

        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        delta = mem_before - mem_after

        self.memory_before.append(mem_before)
        self.memory_after.append(mem_after)

        return {
            'collection_count': self.collection_count,
            'objects_collected': collected,
            'memory_before_mb': mem_before,
            'memory_after_mb': mem_after,
            'memory_freed_mb': delta,
            'avg_freed_per_collection': (
                sum(self.memory_before[i] - self.memory_after[i]
                    for i in range(len(self.memory_before)))
                / len(self.memory_before)
                if self.memory_before else 0
            )
        }

    def get_stats(self) -> Dict:
        """Get GC statistics."""
        return {
            'total_collections': self.collection_count,
            'avg_memory_freed_mb': (
                np.mean(
                    [self.memory_before[i] - self.memory_after[i]
                     for i in range(len(self.memory_before))]
                ) if self.memory_before else 0
            ),
            'peak_memory_mb': max(self.memory_before) if self.memory_before else 0
        }


def optimize_embedding_worker(
    worker_config: Dict,
    batch_size: int = 100,
    gc_interval: int = 1000
) -> Dict:
    """
    Apply all memory optimizations to embedding worker.

    Args:
        worker_config: Worker configuration dict
        batch_size: Batch size for Neo4j operations
        gc_interval: GC interval in vectors

    Returns:
        Optimized configuration
    """
    optimized = worker_config.copy()

    # Update Neo4j settings
    optimized['neo4j'] = {
        'batch_size': batch_size,
        'connection_pool_timeout_sec': 45,
        'enable_query_cache': True,
        'max_cache_size': 10000
    }

    # Update embedding settings
    optimized['embedding'] = {
        'streaming_mode': True,
        'gc_interval_vectors': gc_interval,
        'memory_mapped_storage': True,
        'mmap_path': '/tmp/quran_vectors.mmap'
    }

    # Resource requests
    optimized['resources'] = {
        'cpu_request': '500m',
        'cpu_limit': '1000m',
        'memory_request': '512Mi',
        'memory_limit': '1Gi'
    }

    logger.info(f"Worker optimized: {optimized}")
    return optimized
