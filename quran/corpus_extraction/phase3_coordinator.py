#!/usr/bin/env python3
"""
Phase 3 Coordinator - Parallel Verse Extraction.

Spawns 32 extraction agents in parallel to extract all 6,236 Quranic verses.
Each agent processes ~195 verses and saves to a separate corpus_<N>.json file.

Architecture:
- 32 agents in parallel
- Each processes ~195 verses
- Checkpointing for recovery
- API rate limiting respected
- Zero-fabrication guarantee
"""

import subprocess
import sys
import os
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Phase3-Coordinator - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Phase3Coordinator:
    """Coordinate 32 parallel extraction agents for all Quranic verses."""

    def __init__(self):
        """Initialize the coordinator."""
        self.num_agents = 32
        self.verses_per_agent = 195  # Roughly 6236 / 32
        self.base_path = (
            '/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday'
            '/quran/corpus_extraction/extraction'
        )
        self.output_dir = (
            '/Users/mac/Desktop/QuranFrontier/.claude/worktrees/magical-faraday'
            '/quran/corpus_extraction/output'
        )

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        logger.info(
            f"Phase 3 Coordinator initialized: "
            f"{self.num_agents} agents, "
            f"~{self.verses_per_agent} verses per agent"
        )

    def execute_all_agents(self, max_workers: int = 32) -> Dict:
        """
        Launch all 32 agents in parallel.

        Args:
            max_workers: Maximum number of parallel agents (default: 32)

        Returns:
            Dictionary with results from all agents
        """
        logger.info(f"Starting parallel execution with {max_workers} workers")

        futures = []
        start_time = datetime.now()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for agent_num in range(1, self.num_agents + 1):
                agent_script = os.path.join(self.base_path, f'agent_{agent_num}.py')

                future = executor.submit(
                    self._run_agent,
                    agent_num,
                    agent_script
                )
                futures.append((agent_num, future))

                logger.info(f"Submitted agent {agent_num}")

            # Collect results as they complete
            results = {}
            completed_count = 0

            for agent_num, future in as_completed(futures):
                try:
                    result = future.result(timeout=3600)  # 1 hour timeout per agent
                    results[agent_num] = result

                    completed_count += 1
                    logger.info(
                        f"Agent {agent_num} completed ({completed_count}/{self.num_agents}): "
                        f"{result.get('status', 'unknown')}"
                    )

                except Exception as e:
                    logger.error(f"Agent {agent_num} failed: {str(e)}")
                    results[agent_num] = {
                        'agent_id': f'agent_{agent_num}',
                        'status': 'error',
                        'error': str(e)
                    }

        end_time = datetime.now()
        duration = end_time - start_time

        # Aggregate results
        aggregated = self._aggregate_results(results, duration)

        logger.info(f"All agents completed in {duration}")
        return aggregated

    def _run_agent(self, agent_num: int, agent_script: str) -> Dict:
        """
        Run a single agent script.

        Args:
            agent_num: Agent number
            agent_script: Path to agent script

        Returns:
            Dictionary with agent result
        """
        logger.info(f"Running agent {agent_num}: {agent_script}")

        try:
            # Run agent as subprocess
            result = subprocess.run(
                [sys.executable, agent_script],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if result.returncode == 0:
                logger.info(f"Agent {agent_num} completed successfully")
                return {
                    'agent_num': agent_num,
                    'status': 'success',
                    'returncode': result.returncode,
                    'stdout': result.stdout[:500],  # First 500 chars of output
                }
            else:
                logger.warning(f"Agent {agent_num} returned code {result.returncode}")
                return {
                    'agent_num': agent_num,
                    'status': 'failed',
                    'returncode': result.returncode,
                    'stderr': result.stderr[:500],
                }

        except subprocess.TimeoutExpired:
            logger.error(f"Agent {agent_num} timed out")
            return {
                'agent_num': agent_num,
                'status': 'timeout',
                'error': 'Execution timeout after 1 hour'
            }

        except Exception as e:
            logger.error(f"Agent {agent_num} execution error: {str(e)}")
            return {
                'agent_num': agent_num,
                'status': 'error',
                'error': str(e)
            }

    def _aggregate_results(self,
                          results: Dict,
                          duration) -> Dict:
        """
        Aggregate and report results from all agents.

        Args:
            results: Dictionary of agent results
            duration: Total execution duration

        Returns:
            Aggregated results dictionary
        """
        # Count statuses
        success_count = sum(1 for r in results.values() if r.get('status') == 'success')
        failed_count = sum(1 for r in results.values() if r.get('status') == 'failed')
        error_count = sum(1 for r in results.values() if r.get('status') == 'error')
        timeout_count = sum(1 for r in results.values() if r.get('status') == 'timeout')

        # Verify output files
        output_files = self._verify_output_files()

        # Count total verses extracted
        total_verses = self._count_total_verses()

        aggregated = {
            'coordinator_status': 'completed',
            'total_agents': self.num_agents,
            'agents_successful': success_count,
            'agents_failed': failed_count,
            'agents_error': error_count,
            'agents_timeout': timeout_count,
            'total_duration_seconds': duration.total_seconds(),
            'agent_results': results,
            'output_files': output_files,
            'total_verses_extracted': total_verses,
            'timestamp': datetime.now().isoformat()
        }

        return aggregated

    def _verify_output_files(self) -> Dict[str, Dict]:
        """
        Verify that all output files were created and get their stats.

        Returns:
            Dictionary mapping agent number to file stats
        """
        output_files = {}

        for agent_num in range(1, self.num_agents + 1):
            corpus_file = os.path.join(
                self.output_dir,
                f'corpus_{agent_num}.json'
            )

            if os.path.exists(corpus_file):
                file_size = os.path.getsize(corpus_file)
                try:
                    with open(corpus_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        verse_count = len(data)
                    output_files[agent_num] = {
                        'exists': True,
                        'file_size_bytes': file_size,
                        'verse_count': verse_count,
                        'path': corpus_file
                    }
                except Exception as e:
                    output_files[agent_num] = {
                        'exists': True,
                        'file_size_bytes': file_size,
                        'error': str(e),
                        'path': corpus_file
                    }
            else:
                output_files[agent_num] = {
                    'exists': False,
                    'path': corpus_file
                }

        return output_files

    def _count_total_verses(self) -> int:
        """
        Count total verses extracted across all output files.

        Returns:
            Total number of verses
        """
        total = 0

        for agent_num in range(1, self.num_agents + 1):
            corpus_file = os.path.join(
                self.output_dir,
                f'corpus_{agent_num}.json'
            )

            if os.path.exists(corpus_file):
                try:
                    with open(corpus_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        total += len(data)
                except Exception as e:
                    logger.warning(f"Error reading {corpus_file}: {e}")

        return total

    def generate_report(self, results: Dict) -> str:
        """
        Generate a human-readable report of execution results.

        Args:
            results: Aggregated results dictionary

        Returns:
            Formatted report string
        """
        report_lines = [
            "=" * 70,
            "PHASE 3 PARALLEL VERSE EXTRACTION - FINAL REPORT",
            "=" * 70,
            "",
            f"Execution Status: {results['coordinator_status']}",
            f"Total Duration: {results['total_duration_seconds']:.2f} seconds",
            f"Timestamp: {results['timestamp']}",
            "",
            "AGENT EXECUTION SUMMARY:",
            f"  Total Agents: {results['total_agents']}",
            f"  Successful: {results['agents_successful']}",
            f"  Failed: {results['agents_failed']}",
            f"  Error: {results['agents_error']}",
            f"  Timeout: {results['agents_timeout']}",
            "",
            "OUTPUT VERIFICATION:",
            f"  Total Verses Extracted: {results['total_verses_extracted']}",
            f"  Expected: 6,236",
            f"  Match: {'YES' if results['total_verses_extracted'] == 6236 else 'NO'}",
            "",
            "OUTPUT FILES:",
        ]

        # Add file stats
        output_files = results.get('output_files', {})
        for agent_num in range(1, self.num_agents + 1):
            file_info = output_files.get(agent_num, {})
            if file_info.get('exists'):
                verse_count = file_info.get('verse_count', 'unknown')
                size_kb = file_info.get('file_size_bytes', 0) / 1024
                report_lines.append(
                    f"  corpus_{agent_num}.json: "
                    f"{verse_count} verses ({size_kb:.1f} KB)"
                )
            else:
                report_lines.append(f"  corpus_{agent_num}.json: NOT FOUND")

        report_lines.extend([
            "",
            "=" * 70,
            "PHASE 3 EXTRACTION COMPLETE",
            "=" * 70,
        ])

        return "\n".join(report_lines)


def main():
    """Main entry point for Phase 3 Coordinator."""
    logger.info("Starting Phase 3 Coordinator - Parallel Verse Extraction")

    coordinator = Phase3Coordinator()

    # Execute all agents in parallel
    results = coordinator.execute_all_agents(max_workers=32)

    # Generate and print report
    report = coordinator.generate_report(results)
    print(report)

    # Save detailed results
    results_file = os.path.join(
        coordinator.output_dir,
        'phase3_results.json'
    )
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"Detailed results saved to {results_file}")

    # Determine exit code
    success = (
        results['agents_successful'] == coordinator.num_agents and
        results['total_verses_extracted'] == 6236
    )

    if success:
        logger.info("Phase 3 extraction SUCCESSFUL")
        return 0
    else:
        logger.error("Phase 3 extraction INCOMPLETE or FAILED")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
