import requests
import time
from typing import Dict, Any, Optional
from collections import deque


class ApiIntegrationLayer:
    """Multi-source API integration with rate limiting and caching"""

    def __init__(self, quran_api_key=None, ansari_api_key=None, rate_limit_per_hour=100):
        self.quran_base = "https://api.quran.com/api/v4"
        self.ansari_base = "https://api.ansari.chat/v1"
        self.rate_limit = rate_limit_per_hour
        self.request_timestamps = deque()
        self.request_count = 0

    def get_verse_from_quran(self, surah: int, ayah: int) -> Optional[Dict[str, Any]]:
        """Retrieve verse from quran.com API"""
        self._check_rate_limit()
        try:
            endpoint = f"{self.quran_base}/verses/by_key/{surah}:{ayah}"
            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()['verse']
                return {
                    'surah': surah,
                    'ayah': ayah,
                    'text_ar': data.get('text_madani', ''),
                    'translation': data.get('translations', [{}])[0].get('text', ''),
                    'source': 'quran.com'
                }
            return {'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'error': str(e)}

    def get_tafsir_from_ansari(self, surah: int, ayah: int, tafsir_name: str) -> Optional[Dict]:
        """Retrieve tafsir from ansari.chat API"""
        self._check_rate_limit()
        try:
            endpoint = f"{self.ansari_base}/tafsir"
            params = {'surah': surah, 'ayah': ayah, 'tafsir': tafsir_name}
            response = requests.get(endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'surah': surah,
                    'ayah': ayah,
                    'source': tafsir_name,
                    'text': data.get('interpretation', '')
                }
            return None
        except Exception:
            return None

    def get_asbab_nuzul(self, surah: int, ayah: int) -> Optional[Dict]:
        """Retrieve asbab al-nuzul context"""
        self._check_rate_limit()
        try:
            endpoint = f"{self.ansari_base}/asbab-nuzul"
            response = requests.get(endpoint, params={'surah': surah, 'ayah': ayah}, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception:
            return None

    def _check_rate_limit(self):
        """Enforce rate limiting"""
        now = time.time()
        while self.request_timestamps and self.request_timestamps[0] < now - 3600:
            self.request_timestamps.popleft()
        if len(self.request_timestamps) >= self.rate_limit:
            wait = self.request_timestamps[0] + 3600 - now
            time.sleep(wait + 0.1)
        self.request_timestamps.append(now)
        self.request_count += 1

    def get_request_count(self) -> int:
        return self.request_count

    def get_remaining_quota(self) -> int:
        return self.rate_limit - len(self.request_timestamps)
