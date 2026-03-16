import pytest
import time
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from quran.corpus_extraction.infrastructure.cache_layer import CacheLayer


def test_cache_levels():
    cache = CacheLayer()
    cache.set('L1', 'key1', {'data': 'value1'})
    cache.set('L2', 'key2', {'data': 'value2'})
    cache.set('L3', 'key3', {'data': 'value3'})
    cache.set('L4', 'key4', {'data': 'value4'})

    assert cache.get('L1', 'key1') == {'data': 'value1'}
    assert cache.get('L2', 'key2') == {'data': 'value2'}
    assert cache.get('L3', 'key3') == {'data': 'value3'}
    assert cache.get('L4', 'key4') == {'data': 'value4'}


def test_cache_expiration():
    cache = CacheLayer()
    cache.set('L1', 'test', {'value': 'data'}, ttl=1)
    assert cache.get('L1', 'test') is not None
    time.sleep(2)
    assert cache.get('L1', 'test') is None


def test_cache_stats():
    cache = CacheLayer()
    cache.set('L2', 'key1', {'data': 'v1'})
    cache.get('L2', 'key1')  # hit
    cache.get('L2', 'key1')  # hit
    cache.get('L2', 'missing')  # miss

    stats = cache.get_stats()
    assert stats['hits'] == 2
    assert stats['misses'] == 1
