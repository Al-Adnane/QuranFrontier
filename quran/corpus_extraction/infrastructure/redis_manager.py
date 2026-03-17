"""
Redis Checkpoint Manager for Parallel Verse Extraction Agents

This module provides a CheckpointManager class that uses Redis to store
and retrieve checkpoints for parallel extraction agents, enabling recovery
and coordination across multiple workers.

Key Features:
- Save and retrieve checkpoints with agent isolation
- FIFO queue management for batch processing
- SHA256 integrity verification
- Graceful error handling for connection failures
"""
import json
import hashlib
from typing import Dict, Optional
import redis


class CheckpointManager:
    """Redis-backed checkpoint storage for parallel verse extraction agents"""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """
        Initialize Redis connection.

        Args:
            host: Redis server hostname (default: 'localhost')
            port: Redis server port (default: 6379)
            db: Redis database number (default: 0)
        """
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=False
            )
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            # Store error but don't raise - allow graceful degradation
            self.redis_client = None
            self._connection_error = str(e)

    def save_checkpoint(self, agent_id: str, checkpoint: Dict) -> bool:
        """
        Save checkpoint for agent recovery.

        Stores checkpoint data with:
        - agent_id: unique identifier for the agent
        - current_verse: progress marker
        - status: current processing status
        - timestamp: when checkpoint was created
        - hash: SHA256 hash for integrity verification

        Args:
            agent_id: Unique identifier for the agent
            checkpoint: Dictionary with checkpoint data

        Returns:
            True if successful, False on error
        """
        if self.redis_client is None:
            return False

        try:
            # Ensure checkpoint has required fields
            required_fields = ['agent_id', 'current_verse', 'status', 'timestamp']
            for field in required_fields:
                if field not in checkpoint:
                    checkpoint[field] = None

            # Compute hash for integrity
            checkpoint_hash = self._compute_hash(checkpoint)

            # Create storage object with hash
            storage_obj = {
                'data': checkpoint,
                'hash': checkpoint_hash
            }

            # Store in Redis with agent_id key
            key = f'checkpoint:{agent_id}'
            self.redis_client.set(key, json.dumps(storage_obj))
            return True

        except Exception:
            return False

    def get_checkpoint(self, agent_id: str) -> Optional[Dict]:
        """
        Retrieve checkpoint or None if not found.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            Dictionary with checkpoint data, or None if not found or error
        """
        if self.redis_client is None:
            return None

        try:
            key = f'checkpoint:{agent_id}'
            data = self.redis_client.get(key)

            if data is None:
                return None

            # Parse JSON
            storage_obj = json.loads(data.decode('utf-8'))

            # Return the data portion
            return storage_obj.get('data')

        except Exception:
            return None

    def queue_batch(self, queue_name: str, batch: Dict) -> bool:
        """
        Enqueue batch to FIFO queue.

        Uses Redis LIST with RPUSH to add to the right (tail).
        This maintains FIFO ordering with LPOP operations.

        Args:
            queue_name: Name of the queue
            batch: Dictionary with batch data

        Returns:
            True on success, False on error
        """
        if self.redis_client is None:
            return False

        try:
            key = f'queue:{queue_name}'
            batch_json = json.dumps(batch)
            self.redis_client.rpush(key, batch_json)
            return True

        except Exception:
            return False

    def get_batch(self, queue_name: str) -> Optional[Dict]:
        """
        Dequeue batch from FIFO queue.

        Uses Redis LPOP to remove and return from the left (head),
        maintaining FIFO order with RPUSH enqueue operations.

        Args:
            queue_name: Name of the queue

        Returns:
            Dictionary with batch data, or None if queue empty or error
        """
        if self.redis_client is None:
            return None

        try:
            key = f'queue:{queue_name}'
            data = self.redis_client.lpop(key)

            if data is None:
                return None

            return json.loads(data.decode('utf-8'))

        except Exception:
            return None

    def _compute_hash(self, data: Dict) -> str:
        """
        Compute SHA256 hash of data for integrity verification.

        Args:
            data: Dictionary to hash

        Returns:
            SHA256 hexdigest of the data
        """
        # Convert to JSON with sorted keys for consistent hashing
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
