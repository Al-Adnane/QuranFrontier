# Dorar.net Hadith Database Integration Plan

## Executive Summary
dorar.net (الدرر السنية) provides public API access to their Islamic hadith encyclopedia. **Integration is feasible with no authentication required.**

---

## 1. API AVAILABILITY

### Primary Endpoint
**Status:** ✅ Public API Available

**Official Endpoint:**
```
https://dorar.net/dorar_api.json?skey={search_term}
```

**Documentation:**
- Article: https://dorar.net/article/389/ (خدمة واجهة الموسوعة الحديثية API)
- Sample implementations provided in ZIP files:
  - PHP: https://dorar.net/files/dorar_api.zip
  - JavaScript: https://dorar.net/files/dorar_json_api.js.zip

### Enhanced API Wrapper (Community)
A more feature-rich wrapper API is available on GitHub:
- **Repository:** https://github.com/AhmedElTabarani/dorar-hadith-api
- **Endpoints:** Provides advanced filtering, categorization, and metadata

---

## 2. ACCESS METHOD

### Option A: Direct Official API (Recommended for simplicity)
- **Endpoint:** `https://dorar.net/dorar_api.json?skey={search_term}`
- **Method:** GET request
- **Returns:** JSON with HTML-formatted results
- **Results per query:** 15 hadiths

### Option B: Enhanced Wrapper API (Recommended for features)
**Endpoints:**

1. **Basic Search (15 results)**
   ```
   GET /v1/api/hadith/search?value={text}
   ```

2. **Site Search (30 results)**
   ```
   GET /v1/site/hadith/search?value={text}
   ```

3. **Individual Hadith**
   ```
   GET /v1/site/hadith/:id
   ```

4. **Similar Hadiths**
   ```
   GET /v1/site/hadith/similar/:id
   ```

5. **Alternative Versions**
   ```
   GET /v1/site/hadith/alternate/:id
   ```

6. **Transmission Chains**
   ```
   GET /v1/site/hadith/usul/:id
   ```

7. **Commentary/Explanation**
   ```
   GET /v1/site/sharh/:id
   ```

---

## 3. AUTHENTICATION

**Status:** ✅ **NOT REQUIRED**

- No API keys needed
- No OAuth flow
- Open public access
- Designed for website and forum integration

**Rate Limiting:**
- 100 searches per IP address per day (applies to wrapper API)
- 5-second result caching

---

## 4. DATA STRUCTURE

### Fields Returned per Hadith
- **Hadith Text:** Full hadith statement with search term highlighting
- **Narrator (الراوي):** Person who reported the hadith
- **Authenticator (المحدث):** Islamic scholar who evaluated authenticity
- **Source (المصدر):** Reference book/collection name
- **Location (الصفحة أو الرقم):** Page number or hadith number
- **Authenticity Grade (خلاصة حكم المحدث):** Scholar's verdict (صحيح, ضعيف, منكر, etc.)

### Sample Response (from testing)
- Query: "الصلاة" (prayer)
- Results: 15 hadiths returned
- Quality: High-quality authenticated content with scholarly assessments
- Authenticity grades observed: Sahih (صحيح), Hasan (حسن), Weak (ضعيف), Mawdu (موضوع)

---

## 5. EXPECTED RECORDS

- **Estimated total hadiths:** 50,000+ (based on "الموسوعة الحديثية" - Hadith Encyclopedia scope)
- **Coverage:** Multiple hadith collections including Sahih Al-Bukhari, Sahih Muslim, and others
- **Authentication verdicts:** Comprehensive scholarly assessments from Islamic experts
- **Language:** Arabic with potential English metadata

---

## 6. IMPLEMENTATION PLAN

### Phase 1: Python Client Skeleton (Ready-to-Code)

```python
import requests
import json
from typing import List, Dict, Optional
from urllib.parse import urlencode

class DorarHadithClient:
    """Client for accessing dorar.net hadith database."""

    # Choose one:
    OFFICIAL_API = "https://dorar.net/dorar_api.json"
    WRAPPER_API = "https://api.example.com/v1"  # Community wrapper (if hosted)

    def __init__(self, use_wrapper: bool = False):
        self.use_wrapper = use_wrapper
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QuranFrontier/1.0 (Islamic Data Integration)'
        })

    def search(self, query: str, limit: Optional[int] = None) -> Dict:
        """
        Search hadith database.

        Args:
            query: Search term in Arabic or English
            limit: Max results (15 for official API, configurable for wrapper)

        Returns:
            JSON response with hadith results
        """
        if self.use_wrapper:
            return self._search_wrapper(query)
        else:
            return self._search_official(query)

    def _search_official(self, query: str) -> Dict:
        """Search using official dorar.net API."""
        params = {'skey': query}
        try:
            response = self.session.get(
                self.OFFICIAL_API,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"API request failed: {e}")

    def _search_wrapper(self, query: str) -> Dict:
        """Search using community wrapper API."""
        endpoint = f"{self.WRAPPER_API}/hadith/search"
        params = {'value': query}
        try:
            response = self.session.get(
                endpoint,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Wrapper API request failed: {e}")

    def get_hadith_by_id(self, hadith_id: str) -> Dict:
        """Retrieve specific hadith by ID (wrapper API only)."""
        if not self.use_wrapper:
            raise NotImplementedError(
                "get_hadith_by_id requires wrapper API"
            )
        endpoint = f"{self.WRAPPER_API}/hadith/{hadith_id}"
        response = self.session.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_similar(self, hadith_id: str) -> Dict:
        """Get similar hadiths (wrapper API only)."""
        if not self.use_wrapper:
            raise NotImplementedError("get_similar requires wrapper API")
        endpoint = f"{self.WRAPPER_API}/hadith/similar/{hadith_id}"
        response = self.session.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.json()


# Usage Example
if __name__ == "__main__":
    # Using official API
    client = DorarHadithClient(use_wrapper=False)

    results = client.search("الصلاة")  # Search for "prayer"
    print(json.dumps(results, ensure_ascii=False, indent=2))

    # To use wrapper API when available:
    # client = DorarHadithClient(use_wrapper=True)
```

### Phase 2: Data Pipeline Integration

```python
from datetime import datetime

class DorarPipeline:
    """Pipeline for syncing dorar.net data into QuranFrontier."""

    def __init__(self, client: DorarHadithClient, db_connection=None):
        self.client = client
        self.db = db_connection
        self.batch_size = 50
        self.search_queries = [
            "الصلاة",      # Prayer
            "الزكاة",      # Almsgiving
            "الصيام",      # Fasting
            "الحج",        # Pilgrimage
            "التوحيد",     # Monotheism
            # Add more topical searches
        ]

    def sync_all(self):
        """Sync hadiths from all search queries."""
        for query in self.search_queries:
            try:
                self._sync_query(query)
            except Exception as e:
                print(f"Error syncing query '{query}': {e}")

    def _sync_query(self, query: str):
        """Sync results from a single search query."""
        results = self.client.search(query)
        # Parse HTML results
        # Store in database
        # Track sync timestamp
        pass

    def parse_hadith_entry(self, html_entry: str) -> Dict:
        """
        Parse HTML-formatted hadith entry.

        Returns:
            {
                'text': str,
                'narrator': str,
                'authenticator': str,
                'source': str,
                'grade': str,
                'synced_at': datetime
            }
        """
        # Use BeautifulSoup or regex to parse HTML
        pass
```

### Phase 3: Error Handling & Resilience

```python
import backoff

class ResilientDorarClient(DorarHadithClient):
    """Enhanced client with retry logic and error handling."""

    @backoff.on_exception(
        backoff.expo,
        requests.RequestException,
        max_tries=3
    )
    def search(self, query: str) -> Dict:
        """Search with automatic retry on failure."""
        return super().search(query)

    def validate_response(self, response: Dict) -> bool:
        """Validate API response structure."""
        required_keys = {'ahadith', 'result'} if not self.use_wrapper else {'data', 'metadata'}
        return all(key in response for key in required_keys)
```

---

## 7. RECOMMENDATIONS

### ✅ Proceed with Integration

**Yes** - dorar.net integration is recommended because:

1. **Public API available** - No authentication barriers
2. **No rate limit conflicts** - 100/day per IP is reasonable for batch sync
3. **High quality data** - Scholarly authenticated hadiths with detailed metadata
4. **Multiple endpoint options** - Both official (simple) and wrapper (featured) available
5. **Community support** - Active GitHub projects and documentation

### Implementation Strategy

**Recommended approach:**
1. Start with **Official API** for MVP (simpler, no external dependencies)
2. Migrate to **Wrapper API** once stable (better features: similar hadiths, commentary, etc.)
3. Use **topical search queries** to build initial dataset (not bulk scraping)
4. Implement caching (5-second minimum from API, consider 1-day local cache)
5. Schedule background syncs for new hadiths

### Next Steps

1. Set up DorarHadithClient in QuranFrontier codebase
2. Implement initial 5 topical searches for MVP
3. Build database schema to store parsed hadith entries
4. Create async sync job (nightly or weekly)
5. Add UI to display dorar.net hadiths alongside other sources

---

## 8. REFERENCES

- **Official API Documentation:** https://dorar.net/article/389/
- **GitHub Wrapper:** https://github.com/AhmedElTabarani/dorar-hadith-api
- **Direct API Endpoint:** https://dorar.net/dorar_api.json
- **Contact Support:** [email protected]

---

**Status:** ✅ Ready to proceed with implementation
**Test Results:** API functional, 15+ hadiths per search verified
**Confidence Level:** High - Public, documented API with active community support
