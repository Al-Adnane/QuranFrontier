"""
Tests for Redis Checkpoint Manager

TDD approach: Tests written first, implementation follows.
All tests must use mocking to avoid requiring Redis server.
"""
import json
import hashlib
from unittest.mock import Mock, patch, MagicMock
import pytest

from quran.corpus_extraction.infrastructure.redis_manager import CheckpointManager


class TestCheckpointManagerBasics:
    """Test basic checkpoint save and retrieve functionality"""

    @patch('quran.corpus_extraction.infrastructure.redis_manager.redis.Redis')
    def test_save_and_retrieve_checkpoint(self, mock_redis_class):
        """
        Test save checkpoint with agent_id='agent_1', current_verse=42, status='in_progress'
        Retrieve and verify all fields present
        """
        # Setup mock Redis
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True

        # Create manager
        manager = CheckpointManager(host='localhost', port=6379, db=0)

        # Prepare checkpoint
        checkpoint = {
            'agent_id': 'agent_1',
            'current_verse': 42,
            'status': 'in_progress',
            'timestamp': '2026-03-16T10:00:00Z'
        }

        # Compute hash to match what implementation will store
        checkpoint_hash = manager._compute_hash(checkpoint)
        storage_obj = {
            'data': checkpoint,
            'hash': checkpoint_hash
        }

        # Mock Redis get response with the storage object
        mock_redis.get.return_value = json.dumps(storage_obj).encode('utf-8')
        mock_redis.set.return_value = True

        # Save checkpoint
        result = manager.save_checkpoint('agent_1', checkpoint)
        assert result is True

        # Verify set was called
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert call_args[0][0] == 'checkpoint:agent_1'

        # Retrieve checkpoint
        retrieved = manager.get_checkpoint('agent_1')
        assert retrieved is not None
        assert retrieved['agent_id'] == 'agent_1'
        assert retrieved['current_verse'] == 42
        assert retrieved['status'] == 'in_progress'
        assert retrieved['timestamp'] == '2026-03-16T10:00:00Z'


class TestQueueOperations:
    """Test FIFO queue operations"""

    @patch('quran.corpus_extraction.infrastructure.redis_manager.redis.Redis')
    def test_queue_operations(self, mock_redis_class):
        """
        Add 3 batches to queue
        Verify FIFO order (first in = first out)
        Verify dequeue returns batches in insertion order
        """
        # Setup mock Redis
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True

        # Create manager
        manager = CheckpointManager(host='localhost', port=6379, db=0)

        # Prepare batches
        batch1 = {'batch_id': 'batch_1', 'verses': [1, 2, 3]}
        batch2 = {'batch_id': 'batch_2', 'verses': [4, 5, 6]}
        batch3 = {'batch_id': 'batch_3', 'verses': [7, 8, 9]}

        # Mock Redis operations
        mock_redis.rpush.return_value = 1
        mock_redis.lpop.side_effect = [
            json.dumps(batch1).encode('utf-8'),
            json.dumps(batch2).encode('utf-8'),
            json.dumps(batch3).encode('utf-8'),
            None
        ]

        # Enqueue batches
        assert manager.queue_batch('test_queue', batch1) is True
        assert manager.queue_batch('test_queue', batch2) is True
        assert manager.queue_batch('test_queue', batch3) is True

        # Verify RPUSH was called 3 times
        assert mock_redis.rpush.call_count == 3

        # Dequeue and verify FIFO order
        dequeued1 = manager.get_batch('test_queue')
        assert dequeued1['batch_id'] == 'batch_1'

        dequeued2 = manager.get_batch('test_queue')
        assert dequeued2['batch_id'] == 'batch_2'

        dequeued3 = manager.get_batch('test_queue')
        assert dequeued3['batch_id'] == 'batch_3'

        # Verify empty queue
        dequeued_empty = manager.get_batch('test_queue')
        assert dequeued_empty is None


class TestCheckpointIntegrity:
    """Test SHA256 hash computation for integrity verification"""

    @patch('quran.corpus_extraction.infrastructure.redis_manager.redis.Redis')
    def test_checkpoint_integrity(self, mock_redis_class):
        """
        Save checkpoint
        Verify SHA256 hash is computed
        Retrieve and hash should match
        """
        # Setup mock Redis
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True

        # Create manager
        manager = CheckpointManager(host='localhost', port=6379, db=0)

        # Prepare checkpoint
        checkpoint = {
            'agent_id': 'agent_1',
            'current_verse': 42,
            'status': 'in_progress',
            'timestamp': '2026-03-16T10:00:00Z'
        }

        # Compute expected hash
        data_str = json.dumps(checkpoint, sort_keys=True)
        expected_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()

        # Mock Redis operations
        saved_data = {
            'data': checkpoint,
            'hash': expected_hash
        }
        mock_redis.set.return_value = True
        mock_redis.get.return_value = json.dumps(saved_data).encode('utf-8')

        # Save checkpoint
        result = manager.save_checkpoint('agent_1', checkpoint)
        assert result is True

        # Retrieve checkpoint
        retrieved = manager.get_checkpoint('agent_1')
        assert retrieved is not None

        # Verify hash is included and matches
        retrieved_hash = manager._compute_hash(retrieved.get('data', retrieved))
        assert retrieved_hash == expected_hash


class TestConnectionErrorHandling:
    """Test graceful handling of Redis connection failures"""

    @patch('quran.corpus_extraction.infrastructure.redis_manager.redis.Redis')
    def test_connection_error_handling(self, mock_redis_class):
        """
        Mock Redis connection failure
        Verify methods handle gracefully (return False or None)
        """
        # Setup mock Redis to raise connection error
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True

        # Create manager
        manager = CheckpointManager(host='localhost', port=6379, db=0)

        # Mock connection failure on set
        mock_redis.set.side_effect = Exception("Connection refused")

        # Prepare checkpoint
        checkpoint = {
            'agent_id': 'agent_1',
            'current_verse': 42,
            'status': 'in_progress'
        }

        # Save should handle error gracefully
        result = manager.save_checkpoint('agent_1', checkpoint)
        assert result is False

        # Mock connection failure on get
        mock_redis.get.side_effect = Exception("Connection refused")

        # Retrieve should handle error gracefully
        retrieved = manager.get_checkpoint('agent_1')
        assert retrieved is None

        # Mock connection failure on rpush
        mock_redis.rpush.side_effect = Exception("Connection refused")

        # Queue should handle error gracefully
        batch = {'batch_id': 'batch_1', 'verses': [1, 2, 3]}
        result = manager.queue_batch('test_queue', batch)
        assert result is False

        # Mock connection failure on lpop
        mock_redis.lpop.side_effect = Exception("Connection refused")

        # Dequeue should handle error gracefully
        dequeued = manager.get_batch('test_queue')
        assert dequeued is None


class TestMultipleAgentCheckpoints:
    """Test checkpoint isolation across multiple agents"""

    @patch('quran.corpus_extraction.infrastructure.redis_manager.redis.Redis')
    def test_multiple_agent_checkpoints(self, mock_redis_class):
        """
        Save checkpoints for 5 different agent_ids
        Verify each agent gets own checkpoint (no cross-contamination)
        """
        # Setup mock Redis
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.ping.return_value = True

        # Create manager
        manager = CheckpointManager(host='localhost', port=6379, db=0)

        # Prepare checkpoints for 5 agents
        agent_checkpoints = {}
        for i in range(1, 6):
            checkpoint = {
                'agent_id': f'agent_{i}',
                'current_verse': i * 10,
                'status': 'in_progress',
                'timestamp': f'2026-03-16T{10+i}:00:00Z'
            }
            agent_checkpoints[f'agent_{i}'] = checkpoint

        # Mock Redis storage
        stored_data = {}

        def mock_set(key, value):
            stored_data[key] = value
            return True

        def mock_get(key):
            data = stored_data.get(key)
            if data is None:
                return None
            # Ensure it's returned as bytes if it's a string
            if isinstance(data, str):
                return data.encode('utf-8')
            return data

        mock_redis.set.side_effect = mock_set
        mock_redis.get.side_effect = mock_get

        # Save all checkpoints
        for agent_id, checkpoint in agent_checkpoints.items():
            result = manager.save_checkpoint(agent_id, checkpoint)
            assert result is True

        # Verify each agent has unique checkpoint (no cross-contamination)
        for agent_id, original_checkpoint in agent_checkpoints.items():
            retrieved = manager.get_checkpoint(agent_id)
            assert retrieved is not None
            assert retrieved['agent_id'] == agent_id
            assert retrieved['current_verse'] == original_checkpoint['current_verse']
            assert retrieved['status'] == original_checkpoint['status']

            # Verify no contamination from other agents
            for other_agent_id, other_checkpoint in agent_checkpoints.items():
                if agent_id != other_agent_id:
                    assert retrieved['current_verse'] != other_checkpoint['current_verse']
