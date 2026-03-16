"""
Semantic Scholar API client for discovering academic papers.

This module provides a wrapper around the Semantic Scholar v1 API to search for
papers by concept names and extract relevant metadata including title, year,
authors, and DOI.

Rate limiting: 1-2 requests/second (respectful of their API)
"""

import requests
import time
from typing import List, Dict, Optional
from datetime import datetime


class SemanticScholarClient:
    """Client for querying Semantic Scholar API v1."""

    def __init__(self):
        """Initialize the Semantic Scholar client."""
        self.api_endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.rate_limiter = RateLimiter(requests_per_second=1)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QuranFrontier-SourceDiscovery/1.0'
        })

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search Semantic Scholar for papers matching the query.

        Args:
            query: Search query (concept name or keywords)
            limit: Maximum number of results to return (default 10)

        Returns:
            List of papers with structure:
            {
                'doi': str or None,
                'title': str,
                'year': int or None,
                'authors': List[str],
                'source': 'semantic_scholar'
            }
        """
        try:
            self.rate_limiter.wait()

            params = {
                'query': query,
                'limit': min(limit, 100),  # API limit is 100
                'fields': 'paperId,title,year,authors,externalIds,venue'
            }

            response = self.session.get(self.api_endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            papers = []

            if 'data' in data:
                for item in data['data']:
                    paper = self._parse_paper(item)
                    if paper:
                        papers.append(paper)

            return papers

        except requests.RequestException as e:
            print(f"Error querying Semantic Scholar: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error in Semantic Scholar search: {e}")
            return []

    def _parse_paper(self, item: Dict) -> Optional[Dict]:
        """
        Parse a paper from Semantic Scholar API response.

        Args:
            item: Raw paper item from API

        Returns:
            Parsed paper dict or None if invalid
        """
        try:
            # Extract DOI
            doi = None
            if 'externalIds' in item and item['externalIds']:
                doi = item['externalIds'].get('DOI')

            # Extract title
            title = item.get('title', '')
            if not title:
                return None

            # Extract year
            year = item.get('year')

            # Extract authors
            authors = []
            if 'authors' in item and item['authors']:
                authors = [
                    author.get('name', '')
                    for author in item['authors']
                    if author.get('name')
                ]

            return {
                'doi': doi,
                'title': title,
                'year': year,
                'authors': authors,
                'source': 'semantic_scholar'
            }

        except Exception as e:
            print(f"Error parsing paper from Semantic Scholar: {e}")
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

            endpoint = f"https://api.semanticscholar.org/graph/v1/paper/{doi}"
            params = {
                'fields': 'paperId,title,year,authors,externalIds,venue'
            }

            response = self.session.get(endpoint, params=params, timeout=10)

            if response.status_code == 200:
                return self._parse_paper(response.json())
            else:
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
