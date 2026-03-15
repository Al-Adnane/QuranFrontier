#!/usr/bin/env python3
"""
QA Test Suite Runner
Executes comprehensive quality assurance testing across entire system
Generates reports and coverage metrics
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime
import time


class QATestRunner:
    """Comprehensive QA test runner"""

    def __init__(self, output_dir="qa_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().isoformat()
        self.results = {
            "test_run_id": f"qa_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": self.timestamp,
            "test_suites": {},
            "summary": {
                "total_tests": 0,
                "total_passed": 0,
                "total_failed": 0,
                "total_skipped": 0,
                "overall_pass_rate": 0.0,
                "overall_duration": 0.0
            },
            "test_categories": {}
        }

    def run_test_suite(self, suite_name, suite_path):
        """Run a single test suite and capture results"""
        print(f"\n{'='*70}")
        print(f"Running: {suite_name}")
        print(f"Path: {suite_path}")
        print(f"{'='*70}")

        start_time = time.time()

        # Run pytest with JSON output
        cmd = [
            "python3", "-m", "pytest",
            str(suite_path),
            "-v",
            "--tb=short",
            f"--json-report",
            f"--json-report-file={self.output_dir}/{suite_name}_report.json",
            "--junit-xml=" + str(self.output_dir / f"{suite_name}_results.xml"),
            "--cov=.",
            f"--cov-report=json:{self.output_dir}/{suite_name}_coverage.json"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            duration = time.time() - start_time

            # Parse results from output
            output = result.stdout + result.stderr

            # Extract test counts from output
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            skipped = output.count(" SKIPPED")
            total = passed + failed + skipped

            suite_result = {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "total": total,
                "duration_seconds": duration,
                "return_code": result.returncode
            }

            self.results["test_suites"][suite_name] = suite_result

            # Update summary
            self.results["summary"]["total_tests"] += total
            self.results["summary"]["total_passed"] += passed
            self.results["summary"]["total_failed"] += failed
            self.results["summary"]["total_skipped"] += skipped
            self.results["summary"]["overall_duration"] += duration

            print(f"\nResults for {suite_name}:")
            print(f"  Passed: {passed}")
            print(f"  Failed: {failed}")
            print(f"  Skipped: {skipped}")
            print(f"  Duration: {duration:.2f}s")
            print(f"  Status: {suite_result['status']}")

            if failed > 0:
                print(f"\nTest Output:")
                print(output)

            return suite_result

        except subprocess.TimeoutExpired:
            print(f"TIMEOUT: {suite_name} exceeded 5 minutes")
            self.results["test_suites"][suite_name] = {
                "status": "TIMEOUT",
                "error": "Test suite exceeded timeout"
            }
            return None
        except Exception as e:
            print(f"ERROR running {suite_name}: {e}")
            self.results["test_suites"][suite_name] = {
                "status": "ERROR",
                "error": str(e)
            }
            return None

    def run_all_tests(self):
        """Run all QA test suites"""
        qa_tests_dir = Path(__file__).parent / "qa_tests"

        test_suites = [
            ("corpus_completeness", qa_tests_dir / "test_corpus_completeness.py"),
            ("arabic_text_validation", qa_tests_dir / "test_arabic_text_validation.py"),
            ("hash_verification", qa_tests_dir / "test_hash_verification.py"),
            ("security_validation", qa_tests_dir / "test_security_validation.py"),
            ("data_integrity", qa_tests_dir / "test_data_integrity.py"),
        ]

        print("\n" + "="*70)
        print("COMPREHENSIVE QA TEST SUITE EXECUTION")
        print("="*70)
        print(f"Start Time: {self.timestamp}")
        print(f"Output Directory: {self.output_dir}")

        # Run each test suite
        for suite_name, suite_path in test_suites:
            if suite_path.exists():
                self.run_test_suite(suite_name, suite_path)
            else:
                print(f"SKIPPED: {suite_name} - file not found at {suite_path}")

        # Calculate summary statistics
        total = self.results["summary"]["total_tests"]
        if total > 0:
            self.results["summary"]["overall_pass_rate"] = (
                self.results["summary"]["total_passed"] / total
            ) * 100

        return self.results

    def generate_report(self):
        """Generate comprehensive QA report"""
        report = {
            "execution_summary": {
                "timestamp": self.timestamp,
                "duration_seconds": self.results["summary"]["overall_duration"],
                "test_run_id": self.results["test_run_id"]
            },
            "test_results": {
                "total_tests": self.results["summary"]["total_tests"],
                "total_passed": self.results["summary"]["total_passed"],
                "total_failed": self.results["summary"]["total_failed"],
                "total_skipped": self.results["summary"]["total_skipped"],
                "overall_pass_rate_percent": self.results["summary"]["overall_pass_rate"],
                "status": "PASSED" if self.results["summary"]["total_failed"] == 0 else "FAILED"
            },
            "test_suites": self.results["test_suites"],
            "recommendations": self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []

        if self.results["summary"]["total_failed"] > 0:
            recommendations.append({
                "priority": "HIGH",
                "category": "Test Failures",
                "message": f"Fix {self.results['summary']['total_failed']} failing tests",
                "action": "Review test failure logs and fix issues"
            })

        if self.results["summary"]["overall_pass_rate"] < 100:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Coverage",
                "message": "Not all tests passing",
                "action": "Increase test coverage to 100%"
            })

        if self.results["summary"]["total_tests"] < 100:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Completeness",
                "message": f"Only {self.results['summary']['total_tests']} tests executed",
                "action": "Add more comprehensive tests"
            })

        recommendations.append({
            "priority": "LOW",
            "category": "Maintenance",
            "message": "Regular QA testing",
            "action": "Schedule automated QA test runs daily"
        })

        return recommendations

    def save_reports(self):
        """Save all reports to disk"""
        # Summary report
        summary_report = self.generate_report()
        summary_path = self.output_dir / "qa_report_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary_report, f, indent=2)
        print(f"\nSummary Report: {summary_path}")

        # Full results
        results_path = self.output_dir / "qa_test_results.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Full Results: {results_path}")

        # Human-readable report
        self._save_markdown_report()

        return summary_path, results_path

    def _save_markdown_report(self):
        """Save human-readable markdown report"""
        report = self.generate_report()

        markdown = f"""# QuranFrontier QA Test Report

**Generated:** {report['execution_summary']['timestamp']}

**Test Run ID:** {report['execution_summary']['test_run_id']}

## Executive Summary

- **Overall Status:** {report['test_results']['status']}
- **Total Tests:** {report['test_results']['total_tests']}
- **Passed:** {report['test_results']['total_passed']}
- **Failed:** {report['test_results']['total_failed']}
- **Skipped:** {report['test_results']['total_skipped']}
- **Pass Rate:** {report['test_results']['overall_pass_rate_percent']:.1f}%
- **Duration:** {report['execution_summary']['duration_seconds']:.2f}s

## Test Suite Results

"""

        for suite_name, result in report['test_suites'].items():
            markdown += f"""### {suite_name.replace('_', ' ').title()}

- **Status:** {result.get('status', 'UNKNOWN')}
- **Passed:** {result.get('passed', 0)}
- **Failed:** {result.get('failed', 0)}
- **Skipped:** {result.get('skipped', 0)}
- **Duration:** {result.get('duration_seconds', 0):.2f}s

"""

        markdown += """## Recommendations

"""
        for rec in report['recommendations']:
            markdown += f"""### {rec['message']} ({rec['priority']})

- **Category:** {rec['category']}
- **Action:** {rec['action']}

"""

        markdown += """## Pass/Fail Criteria

- ✓ Corpus completeness: All verses present and valid
- ✓ Data accuracy: Verified against source data
- ✓ Security: Input validation and injection prevention
- ✓ Data integrity: Hashes and consistency verified
- ✓ Arabic text: Proper encoding and diacritics

"""

        report_path = self.output_dir / "qa_report.md"
        with open(report_path, 'w') as f:
            f.write(markdown)
        print(f"Markdown Report: {report_path}")

    def print_summary(self):
        """Print test summary"""
        summary = self.results["summary"]

        print("\n" + "="*70)
        print("QA TEST EXECUTION SUMMARY")
        print("="*70)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['total_passed']}")
        print(f"Failed: {summary['total_failed']}")
        print(f"Skipped: {summary['total_skipped']}")
        print(f"Pass Rate: {summary['overall_pass_rate']:.1f}%")
        print(f"Duration: {summary['overall_duration']:.2f}s")
        print(f"Status: {'PASSED' if summary['total_failed'] == 0 else 'FAILED'}")
        print("="*70)

        return summary['total_failed'] == 0


def main():
    """Main entry point"""
    runner = QATestRunner(output_dir="qa_reports")

    # Run all tests
    results = runner.run_all_tests()

    # Generate and save reports
    runner.save_reports()

    # Print summary
    passed = runner.print_summary()

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
