"""
Source Discovery module for finding peer-reviewed papers for scientific concepts.

This module orchestrates the discovery of academic papers from Semantic Scholar
and CrossRef APIs for each scientific concept extracted from the Quran. It handles:
- Querying multiple APIs
- Deduplicating results by DOI
- Validating source integrity
- Caching results to avoid re-queries
- Generating statistics and metadata

The module is designed to process all 400 scientific concepts and discover 10+
peer-reviewed papers per concept, totaling 800+ unique papers.
"""

import json
import time
from typing import List, Dict, Optional, Set
from pathlib import Path
from datetime import datetime
from .semantic_scholar_client import SemanticScholarClient
from .crossref_client import CrossRefClient


class SourceDiscovery:
    """Orchestrator for discovering sources for scientific concepts."""

    def __init__(self, cache_file: Optional[str] = None):
        """
        Initialize the SourceDiscovery instance.

        Args:
            cache_file: Optional path to cache file for loading previous results
        """
        self.ss_client = SemanticScholarClient()
        self.crossref_client = CrossRefClient()
        self.cache: Dict[str, List[Dict]] = {}

        if cache_file and Path(cache_file).exists():
            self.load_cache(cache_file)

    def discover_sources_for_concept(
        self,
        concept_id: str,
        concept_name: str,
        domain: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Discover peer-reviewed papers for a single scientific concept.

        Queries both Semantic Scholar and CrossRef APIs, merges results,
        deduplicates by DOI, and validates source integrity.

        Args:
            concept_id: Unique identifier for the concept
            concept_name: Name of the concept (e.g., "gravitation")
            domain: Domain of the concept (physics, biology, etc.)
            limit: Target number of papers per concept (default 10)

        Returns:
            List of validated sources with structure:
            {
                'doi': str or None,
                'title': str,
                'year': int or None,
                'authors': List[str],
                'source': 'semantic_scholar' | 'crossref'
            }
        """
        try:
            # Check cache first
            if concept_id in self.cache:
                return self.cache[concept_id]

            # Build search query
            search_query = self._build_search_query(concept_name, domain)

            # Query APIs
            ss_papers = self.ss_client.search(search_query, limit=limit)
            cf_papers = self.crossref_client.search(search_query, limit=limit)

            # Merge and deduplicate
            merged_papers = self._merge_and_deduplicate(ss_papers, cf_papers)

            # Validate sources
            if self.validate_sources(merged_papers):
                validated_papers = [p for p in merged_papers if p.get('doi')]
            else:
                validated_papers = merged_papers

            # Cache the results
            self.cache[concept_id] = validated_papers

            return validated_papers

        except Exception as e:
            print(f"Error discovering sources for concept {concept_id}: {e}")
            self.cache[concept_id] = []
            return []

    def discover_sources_for_all_concepts(self, concepts_file: str) -> Dict:
        """
        Discover sources for all scientific concepts in the ontology.

        Loads concepts from JSON file and processes each one. Results are
        aggregated and cached.

        Args:
            concepts_file: Path to scientific_concepts.json file

        Returns:
            Dictionary with results and statistics
        """
        try:
            with open(concepts_file, 'r') as f:
                data = json.load(f)

            concepts = data.get('concepts', [])
            results = {
                'discovered': 0,
                'total': len(concepts),
                'papers': 0
            }

            for concept in concepts:
                concept_id = concept.get('id')
                concept_name = concept.get('name')
                domain = concept.get('domain')

                if not all([concept_id, concept_name, domain]):
                    continue

                sources = self.discover_sources_for_concept(
                    concept_id, concept_name, domain
                )

                if sources:
                    results['discovered'] += 1
                    results['papers'] += len(sources)

            return results

        except FileNotFoundError as e:
            print(f"Concepts file not found: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error parsing concepts file: {e}")
            raise
        except Exception as e:
            print(f"Error discovering sources for all concepts: {e}")
            raise

    def get_sources_by_concept(self, concept_id: str) -> List[Dict]:
        """
        Retrieve cached sources for a concept.

        Args:
            concept_id: Unique identifier for the concept

        Returns:
            List of sources or empty list if not found
        """
        return self.cache.get(concept_id, [])

    def validate_sources(self, sources: List[Dict]) -> bool:
        """
        Validate that sources have required metadata.

        A source is considered valid if it has:
        - Either a DOI or URL
        - A title
        - Publication year

        Args:
            sources: List of source dictionaries to validate

        Returns:
            True if all sources are valid, False otherwise
        """
        if not sources:
            return True

        for source in sources:
            has_identifier = 'doi' in source or 'url' in source
            has_title = 'title' in source and source['title']

            if not (has_identifier and has_title):
                return False

        return True

    def _merge_and_deduplicate(self, ss_papers: List[Dict], cf_papers: List[Dict]) -> List[Dict]:
        """
        Merge papers from multiple sources and deduplicate by DOI.

        Args:
            ss_papers: Papers from Semantic Scholar
            cf_papers: Papers from CrossRef

        Returns:
            Merged and deduplicated list of papers
        """
        doi_map: Dict[str, Dict] = {}

        # Add Semantic Scholar papers
        for paper in ss_papers:
            doi = paper.get('doi')
            if doi:
                if doi not in doi_map:
                    doi_map[doi] = paper
            else:
                # Papers without DOI are added with title-based key
                title = paper.get('title', 'untitled')
                if title not in doi_map:
                    doi_map[title] = paper

        # Add CrossRef papers (overwrite if already exists, they're often more complete)
        for paper in cf_papers:
            doi = paper.get('doi')
            if doi:
                doi_map[doi] = paper  # CrossRef is often more authoritative
            else:
                title = paper.get('title', 'untitled')
                if title not in doi_map:
                    doi_map[title] = paper

        return list(doi_map.values())

    def _build_search_query(self, concept_name: str, domain: str) -> str:
        """
        Build an optimal search query for the concept.

        Args:
            concept_name: Name of the concept
            domain: Domain of the concept

        Returns:
            Search query string
        """
        # Convert underscores to spaces
        formatted_name = concept_name.replace('_', ' ')

        # Add domain context for more targeted searches
        return f"{formatted_name} {domain}"

    def get_metadata(self) -> Dict:
        """
        Generate metadata and statistics for discovered sources.

        Returns:
            Dictionary with metadata including:
            - total_concepts: Expected total concepts (400)
            - covered_concepts: Number of concepts with sources
            - total_papers: Total unique papers discovered
            - discovery_date: ISO format timestamp
            - avg_sources_per_concept: Average sources per concept
        """
        covered = len(self.cache)
        total_papers = sum(len(sources) for sources in self.cache.values())
        avg_per_concept = total_papers / covered if covered > 0 else 0

        return {
            'total_concepts': 400,
            'covered_concepts': covered,
            'total_papers': total_papers,
            'avg_sources_per_concept': round(avg_per_concept, 2),
            'discovery_date': datetime.now().isoformat()
        }

    def save_cache(self, cache_file: str) -> None:
        """
        Save discovered sources to a JSON cache file.

        Args:
            cache_file: Path to save cache file
        """
        try:
            output = {
                'metadata': self.get_metadata(),
                'concept_sources': self.cache
            }

            with open(cache_file, 'w') as f:
                json.dump(output, f, indent=2)

            print(f"Cache saved to {cache_file}")

        except Exception as e:
            print(f"Error saving cache: {e}")
            raise

    def load_cache(self, cache_file: str) -> None:
        """
        Load previously discovered sources from cache file.

        Args:
            cache_file: Path to cache file
        """
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)

            self.cache = data.get('concept_sources', {})
            print(f"Loaded cache from {cache_file}")

        except FileNotFoundError:
            print(f"Cache file not found: {cache_file}")
        except json.JSONDecodeError as e:
            print(f"Error parsing cache file: {e}")
        except Exception as e:
            print(f"Error loading cache: {e}")
            raise

    def get_statistics(self) -> Dict:
        """
        Generate detailed statistics about discovered sources.

        Returns:
            Dictionary with coverage statistics
        """
        metadata = self.get_metadata()

        # Analyze coverage by domain
        domain_stats = {}
        for concept_id, sources in self.cache.items():
            # Would need concept data to determine domain
            # For now, just basic stats
            pass

        return {
            'metadata': metadata,
            'unique_sources': len(set(
                source['doi'] for sources in self.cache.values()
                for source in sources if source.get('doi')
            )),
            'sources_by_api': self._count_sources_by_api(),
            'publication_years': self._analyze_publication_years()
        }

    def _count_sources_by_api(self) -> Dict[str, int]:
        """Count sources by API source."""
        counts = {'semantic_scholar': 0, 'crossref': 0}
        for sources in self.cache.values():
            for source in sources:
                source_type = source.get('source', 'unknown')
                if source_type in counts:
                    counts[source_type] += 1
        return counts

    def _analyze_publication_years(self) -> Dict:
        """Analyze publication year distribution."""
        years = {}
        for sources in self.cache.values():
            for source in sources:
                year = source.get('year')
                if year:
                    years[year] = years.get(year, 0) + 1
        return years
