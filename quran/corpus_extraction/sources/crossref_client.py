"""
CrossRef API client for discovering peer-reviewed papers.

This module provides a wrapper around the CrossRef API to search for peer-reviewed
papers by concept names and extract relevant metadata including title, publication
date, authors, and DOI.

Rate limiting: 1 request/second (respectful of their API)
"""

import requests
import time
from typing import List, Dict, Optional


class CrossRefClient:
    """Client for querying CrossRef API."""

    def __init__(self):
        """Initialize the CrossRef client."""
        self.api_endpoint = "https://api.crossref.org/v1/works"
        self.rate_limiter = RateLimiter(requests_per_second=1)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QuranFrontier-SourceDiscovery/1.0'
        })

    def search(self, query: str, limit: int = 10, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search CrossRef for papers matching the query.

        Args:
            query: Search query (concept name or keywords)
            limit: Maximum number of results to return (default 10)
            filters: Optional filters (e.g., type='journal-article')

        Returns:
            List of papers with structure:
            {
                'doi': str,
                'title': str,
                'year': int or None,
                'authors': List[str],
                'source': 'crossref'
            }
        """
        try:
            self.rate_limiter.wait()

            params = {
                'query': query,
                'rows': min(limit, 1000),  # API limit is 1000
                'sort': 'relevance'
            }

            # Add filters if provided (e.g., type, license)
            if filters:
                params.update(filters)

            response = self.session.get(self.api_endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            papers = []

            if 'message' in data and 'items' in data['message']:
                for item in data['message']['items']:
                    paper = self._parse_paper(item)
                    if paper:
                        papers.append(paper)

            return papers

        except requests.RequestException as e:
            print(f"Error querying CrossRef: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error in CrossRef search: {e}")
            return []

    def _parse_paper(self, item: Dict) -> Optional[Dict]:
        """
        Parse a paper from CrossRef API response.

        Args:
            item: Raw paper item from API

        Returns:
            Parsed paper dict or None if invalid
        """
        try:
            # DOI is required for CrossRef results
            doi = item.get('DOI')
            if not doi:
                return None

            # Extract title
            title = ''
            if 'title' in item and item['title']:
                title = item['title'][0] if isinstance(item['title'], list) else item['title']
            if not title:
                return None

            # Extract year
            year = None
            if 'published-online' in item:
                year = self._extract_year(item['published-online'])
            elif 'published-print' in item:
                year = self._extract_year(item['published-print'])
            elif 'issued' in item:
                year = self._extract_year(item['issued'])

            # Extract authors
            authors = []
            if 'author' in item:
                for author in item['author']:
                    name_parts = []
                    if author.get('given'):
                        name_parts.append(author['given'])
                    if author.get('family'):
                        name_parts.append(author['family'])
                    if name_parts:
                        authors.append(' '.join(name_parts))

            return {
                'doi': doi,
                'title': title,
                'year': year,
                'authors': authors,
                'source': 'crossref'
            }

        except Exception as e:
            print(f"Error parsing paper from CrossRef: {e}")
            return None

    def _extract_year(self, date_obj: Dict) -> Optional[int]:
        """
        Extract year from CrossRef date object.

        Args:
            date_obj: Date object with 'date-parts' structure

        Returns:
            Year as integer or None
        """
        try:
            if isinstance(date_obj, dict) and 'date-parts' in date_obj:
                date_parts = date_obj['date-parts']
                if date_parts and len(date_parts) > 0:
                    year_parts = date_parts[0]
                    if year_parts and len(year_parts) > 0:
                        return int(year_parts[0])
            return None
        except Exception:
            return None

    def get_paper_by_doi(self, doi: str) -> Optional[Dict]:
        """
        Retrieve a specific paper by DOI.

        Args:
            doi: Digital Object Identifier

        Returns:
            Paper details or None if not found
        """
        try:
            self.rate_limiter.wait()

            endpoint = f"https://api.crossref.org/v1/works/{doi}"
            response = self.session.get(endpoint, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'message' in data:
                    return self._parse_paper(data['message'])
            return None

        except Exception as e:
            print(f"Error retrieving paper by DOI: {e}")
            return None


class RateLimiter:
    """Simple rate limiter for API requests."""

    def __init__(self, requests_per_second: float = 1.0):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Maximum requests per second
        """
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0

    def wait(self):
        """Wait until it's safe to make the next request."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
