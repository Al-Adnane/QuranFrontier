"""
Test suite for QAValidator - Comprehensive QA and validation reports
"""
import pytest
import json
import os
from pathlib import Path
from datetime import datetime

# Add parent directories to path for imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from quran.corpus_extraction.output.qa_validator import QAValidator


class TestQAValidatorInitialization:
    """Test QA validator initialization"""

    def test_qa_validator_initialization(self):
        """Verify validator initialized with corpus file"""
        corpus_file = 'quran/corpus_extraction/output/complete_corpus.json'
        validator = QAValidator(corpus_file)

        assert validator.corpus_file == corpus_file
        assert hasattr(validator, 'generate_complete_report')
        assert hasattr(validator, '_validate_corpus_structure')
        assert hasattr(validator, '_verify_scientific_domains')
        assert hasattr(validator, '_verify_tafsir_integration')
        assert hasattr(validator, '_check_verification_compliance')
        assert hasattr(validator, '_analyze_confidence_scores')
        assert hasattr(validator, '_check_zero_fabrication_compliance')
        assert hasattr(validator, '_generate_metrics_dashboard')
        assert hasattr(validator, 'save_report')


class TestValidateCorpusStructure:
    """Test corpus structure validation"""

    def test_validate_corpus_structure(self):
        """Verify corpus structure and integrity"""
        corpus_file = 'quran/corpus_extraction/output/complete_corpus.json'
        validator = QAValidator(corpus_file)

        result = validator._validate_corpus_structure()

        assert isinstance(result, dict)
        assert 'total_verses' in result
        assert 'verses_with_all_fields' in result
        assert 'missing_fields' in result
        assert 'duplicates' in result
        assert 'structural_issues' in result
        assert 'validation_passed' in result

        # Verify structural requirements
        assert result['total_verses'] == 6236
        assert result['validation_passed'] is True
        assert len(result['duplicates']) == 0
        assert len(result['structural_issues']) == 0


class TestVerifyScientificDomains:
    """Test scientific domain coverage verification"""

    def test_verify_scientific_domains(self):
        """Check domain coverage percentages"""
        corpus_file = 'quran/corpus_extraction/output/complete_corpus.json'
        validator = QAValidator(corpus_file)

        result = validator._verify_scientific_domains()

        assert isinstance(result, dict)
        assert 'physics_coverage' in result
        assert 'biology_coverage' in result
        assert 'medicine_coverage' in result
        assert 'engineering_coverage' in result
        assert 'agriculture_coverage' in result
        assert 'overall_domain_coverage' in result
        assert 'gaps' in result

        # Verify coverage requirements
        assert 0 <= result['physics_coverage'] <= 1
        assert 0 <= result['biology_coverage'] <= 1
        assert 0 <= result['medicine_coverage'] <= 1
        assert 0 <= result['engineering_coverage'] <= 1
        assert 0 <= result['agriculture_coverage'] <= 1


class TestVerifyTafsirIntegration:
    """Test tafsir integration validation"""

    def test_verify_tafsir_integration(self):
        """Check tafsir count per verse and integration quality"""
        corpus_file = 'quran/corpus_extraction/output/complete_corpus.json'
        validator = QAValidator(corpus_file)

        result = validator._verify_tafsir_integration()

        assert isinstance(result, dict)
        assert 'verses_with_tafsirs' in result
        assert 'average_tafsir_count' in result
        assert 'tafsir_agreement_stats' in result
        assert 'madhab_distribution' in result
        assert 'tafsir_coverage' in result
        assert 'issues' in result

        # Verify tafsir requirements
        assert result['verses_with_tafsirs'] > 0
        assert result['average_tafsir_count'] >= 0
        assert 0 <= result['tafsir_coverage'] <= 1


class TestCheckVerificationCompliance:
    """Test 5-layer verification compliance"""

    def test_check_verification_compliance(self):
        """Count verses passing each verification layer"""
        corpus_file = 'quran/corpus_extraction/output/complete_corpus.json'
        validator = QAValidator(corpus_file)

        result = validator._check_verification_compliance()

        assert isinstance(result, dict)
        assert 'layer_1_passed' in result
        assert 'layer_2_passed' in result
        assert 'layer_3_passed' in result
        assert 'layer_4_passed' in result
        assert 'layer_5_passed' in result
        assert 'overall_verification_rate' in result
        assert 'failed_verses' in result
        assert 'issues' in result

        # Verify compliance requirements
        assert result['layer_1_passed'] == 6236  # 100%
        assert result['layer_5_passed'] == 6236  # 100%
        assert 0 <= result['overall_verification_rate'] <= 1


class TestAnalyzeConfidenceScores:
    """Test confidence score analysis"""

    def test_analyze_confidence_scores(self):
        """Check confidence score distribution"""
        corpus_file = 'quran/corpus_extraction/output/complete_corpus.json'
        validator = QAValidator(corpus_file)

        result = validator._analyze_confidence_scores()

        assert isinstance(result, dict)
        assert 'average_confidence' in result
        assert 'min_confidence' in result
        assert 'max_confidence' in result
        assert 'verses_above_95_percent' in result
        assert 'verses_below_80_percent' in result
        assert 'distribution' in result

        # Verify confidence requirements
        assert 0 <= result['average_confidence'] <= 1
        assert 0 <= result['min_confidence'] <= 1
        assert 0 <= result['max_confidence'] <= 1
        assert result['verses_above_95_percent'] >= 0
        assert result['verses_below_80_percent'] >= 0


class TestCheckZeroFabricationCompliance:
    """Test zero-fabrication guarantee verification"""

    def test_check_zero_fabrication_compliance(self):
        """Verify zero-fabrication guarantee"""
        corpus_file = 'quran/corpus_extraction/output/complete_corpus.json'
        validator = QAValidator(corpus_file)

        result = validator._check_zero_fabrication_compliance()

        assert isinstance(result, dict)
        assert 'all_verses_api_verified' in result
        assert 'verses_with_sources' in result
        assert 'verses_missing_sources' in result
        assert 'unverifiable_claims' in result
        assert 'fabrication_risk' in result
        assert 'issues' in result

        # Verify zero-fabrication requirements
        assert result['all_verses_api_verified'] is True
        assert result['verses_with_sources'] == 6236
        assert result['verses_missing_sources'] == 0
        assert len(result['unverifiable_claims']) == 0
        assert result['fabrication_risk'] == 'low'


class TestGenerateMetricsDashboard:
    """Test metrics dashboard generation"""

    def test_generate_metrics_dashboard(self):
        """Generate overall project metrics"""
        corpus_file = 'quran/corpus_extraction/output/complete_corpus.json'
        validator = QAValidator(corpus_file)

        result = validator._generate_metrics_dashboard()

        assert isinstance(result, dict)
        assert 'project_completion' in result
        assert 'data_quality_score' in result
        assert 'verification_score' in result
        assert 'coverage_score' in result
        assert 'overall_project_score' in result

        # Verify metrics ranges
        assert 0 <= result['project_completion'] <= 100
        assert 0 <= result['data_quality_score'] <= 1
        assert 0 <= result['verification_score'] <= 1
        assert 0 <= result['coverage_score'] <= 1
        assert 0 <= result['overall_project_score'] <= 1


class TestGenerateCompleteReport:
    """Test complete report generation"""

    def test_generate_complete_report(self):
        """Generate all QA reports"""
        corpus_file = 'quran/corpus_extraction/output/complete_corpus.json'
        validator = QAValidator(corpus_file)

        report = validator.generate_complete_report()

        assert isinstance(report, dict)
        assert 'execution_summary' in report
        assert 'corpus_statistics' in report
        assert 'verification_report' in report
        assert 'coverage_analysis' in report
        assert 'domain_analysis' in report
        assert 'tafsir_analysis' in report
        assert 'error_log' in report
        assert 'recommendations' in report
        assert 'timestamp' in report

        # Verify execution summary
        assert report['execution_summary']['total_verses_extracted'] == 6236
        assert report['execution_summary']['project_completion_percent'] == 100.0

        # Verify corpus statistics
        assert report['corpus_statistics']['total_verses'] == 6236
        assert report['corpus_statistics']['validation_passed'] is True


class TestSaveReport:
    """Test report saving functionality"""

    def test_save_report(self, tmp_path):
        """Save report to JSON file and verify"""
        corpus_file = 'quran/corpus_extraction/output/complete_corpus.json'
        validator = QAValidator(corpus_file)

        report = validator.generate_complete_report()
        output_file = str(tmp_path / 'test_report.json')

        success = validator.save_report(report, output_file)

        assert success is True
        assert os.path.exists(output_file)

        # Verify saved report
        with open(output_file, 'r') as f:
            saved_report = json.load(f)

        assert saved_report['execution_summary']['total_verses_extracted'] == 6236
        assert saved_report['corpus_statistics']['validation_passed'] is True


class TestIntegration:
    """Integration tests for complete workflow"""

    def test_complete_qa_workflow(self):
        """Test complete QA validation workflow"""
        corpus_file = 'quran/corpus_extraction/output/complete_corpus.json'
        validator = QAValidator(corpus_file)

        # Generate complete report
        report = validator.generate_complete_report()

        assert report is not None
        assert isinstance(report, dict)

        # Verify all sections are present
        required_sections = [
            'execution_summary',
            'corpus_statistics',
            'verification_report',
            'coverage_analysis',
            'domain_analysis',
            'tafsir_analysis',
            'error_log',
            'recommendations',
            'timestamp'
        ]

        for section in required_sections:
            assert section in report, f"Missing section: {section}"

        # Verify data integrity
        assert report['corpus_statistics']['total_verses'] == 6236
        assert report['corpus_statistics']['validation_passed'] is True
        assert report['verification_report']['layer_1_quran_api']['passed'] == 6236
        assert report['verification_report']['layer_5_zero_fabrication']['passed'] == 6236
