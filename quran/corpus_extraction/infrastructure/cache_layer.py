import time
from typing import Dict, Any, Optional
from collections import defaultdict


class CacheLayer:
    """4-level caching with different TTLs"""

    CACHE_CONFIG = {
        'L1': {'ttl': 300, 'scope': 'verse_basic'},
        'L2': {'ttl': 3600, 'scope': 'tafsir_extracts'},
        'L3': {'ttl': 86400, 'scope': 'scientific_analysis'},
        'L4': {'ttl': 259200, 'scope': 'verified_facts'}
    }

    def __init__(self):
        self.cache = defaultdict(dict)
        self.stats = {'hits': 0, 'misses': 0}

    def set(self, level: str, key: str, value: Any, ttl: Optional[int] = None):
        ttl = ttl or self.CACHE_CONFIG[level]['ttl']
        self.cache[level][key] = (value, time.time() + ttl)

    def get(self, level: str, key: str) -> Optional[Any]:
        if level not in self.cache or key not in self.cache[level]:
            self.stats['misses'] += 1
            return None

        value, expiry = self.cache[level][key]
        if time.time() > expiry:
            del self.cache[level][key]
            self.stats['misses'] += 1
            return None

        self.stats['hits'] += 1
        return value

    def clear_level(self, level: str):
        if level in self.cache:
            self.cache[level].clear()

    def get_stats(self) -> Dict:
        total = self.stats['hits'] + self.stats['misses']
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': self.stats['hits'] / total if total > 0 else 0
        }
