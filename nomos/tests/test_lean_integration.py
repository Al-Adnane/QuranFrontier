"""
Tests for Lean 4 Proof Assistant integration.
Tests: lean syntax validation, tafsir verification, naskh proofs, theorem caching.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from frontier_neuro_symbolic.system_integration.lean_interface import (
    LeanProver,
    LeanProverError,
    ProofResult,
)


@pytest.fixture
def lean_prover():
    """Create a LeanProver instance for testing."""
    return LeanProver(cache_enabled=True)


@pytest.fixture
def mock_lean_output():
    """Mock Lean subprocess output."""
    return {
        "result": "success",
        "message": "Proof verified",
        "proof_steps": 5,
        "duration_ms": 45,
    }


class TestLeanProverBasics:
    """Test basic LeanProver initialization and configuration."""

    def test_lean_prover_initialization(self):
        """Test LeanProver initializes with default settings."""
        prover = LeanProver()
        assert prover is not None
        assert prover.cache_enabled is True
        assert isinstance(prover.theorem_cache, dict)

    def test_lean_prover_cache_toggle(self):
        """Test cache can be enabled/disabled."""
        prover_cached = LeanProver(cache_enabled=True)
        prover_uncached = LeanProver(cache_enabled=False)
        assert prover_cached.cache_enabled is True
        assert prover_uncached.cache_enabled is False

    def test_lean_config_valid(self):
        """Test Lean executable discovery (may be None if not installed)."""
        prover = LeanProver()
        # Lean might not be installed, but prover should still initialize
        assert prover is not None
        # lean_executable can be None if Lean isn't installed, which is OK for testing

    def test_proof_result_creation(self):
        """Test ProofResult dataclass."""
        result = ProofResult(
            verified=True,
            message="Test proof",
            proof_steps=3,
            duration_ms=100,
        )
        assert result.verified is True
        assert result.message == "Test proof"
        assert result.proof_steps == 3


class TestTajweedVerification:
    """Test Tajweed rule verification."""

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.subprocess.run")
    def test_verify_tajweed_rule_success(self, mock_run, lean_prover, mock_lean_output):
        """Test successful tajweed rule verification."""
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_lean_output)
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        result = lean_prover.verify_tajweed_rule("test_rule")
        assert isinstance(result, ProofResult)

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.LeanProver._run_lean_command")
    def test_verify_tajweed_rule_failure(self, mock_run_cmd, lean_prover):
        """Test tajweed verification handles proof failure."""
        mock_run_cmd.return_value = {
            "verified": False,
            "result": "error",
            "message": "Proof failed"
        }

        with pytest.raises(LeanProverError):
            lean_prover.verify_tajweed_rule("invalid_rule")

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.subprocess.run")
    def test_verify_tajweed_rule_caching(self, mock_run, lean_prover, mock_lean_output):
        """Test tajweed verification results are cached."""
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_lean_output)
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        # First call - should invoke Lean
        result1 = lean_prover.verify_tajweed_rule("cached_rule")
        call_count_1 = mock_run.call_count

        # Second call - should use cache
        result2 = lean_prover.verify_tajweed_rule("cached_rule")
        call_count_2 = mock_run.call_count

        assert result1.verified == result2.verified
        assert call_count_2 == call_count_1  # No additional call


class TestNaskhVerification:
    """Test Naskh ordering and abrogation proofs."""

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.subprocess.run")
    def test_verify_naskh_order(self, mock_run, lean_prover, mock_lean_output):
        """Test verification of naskh temporal order."""
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_lean_output)
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        result = lean_prover.verify_naskh_order("ayah_1", "ayah_2")
        assert isinstance(result, ProofResult)

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.subprocess.run")
    def test_verify_naskh_transitivity(self, mock_run, lean_prover, mock_lean_output):
        """Test transitivity proof for naskh relation."""
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_lean_output)
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        result = lean_prover.verify_naskh_transitivity("a1", "a2", "a3")
        assert isinstance(result, ProofResult)

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.subprocess.run")
    def test_verify_naskh_no_cycles(self, mock_run, lean_prover, mock_lean_output):
        """Test acyclicity proof for naskh DAG."""
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_lean_output)
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        result = lean_prover.verify_naskh_acyclic(["a1", "a2", "a3"])
        assert isinstance(result, ProofResult)


class TestDeonticLogic:
    """Test deontic logic consistency proofs."""

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.subprocess.run")
    def test_deontic_consistency(self, mock_run, lean_prover, mock_lean_output):
        """Test proof of deontic logic consistency."""
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_lean_output)
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        result = lean_prover.prove_deontic_consistency("obligation")
        assert isinstance(result, ProofResult)

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.subprocess.run")
    def test_madhab_compatibility(self, mock_run, lean_prover, mock_lean_output):
        """Test compatibility of deontic rules with Madhab constraints."""
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_lean_output)
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        result = lean_prover.verify_madhab_constraint("Hanafi", "rule_1")
        assert isinstance(result, ProofResult)


class TestTafsirVerification:
    """Test tafsir rule verification and proofs."""

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.subprocess.run")
    def test_verify_tafsir_rule(self, mock_run, lean_prover, mock_lean_output):
        """Test verification of tafsir rule with proof."""
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_lean_output)
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        tafsir_rule = {
            "ayah_number": 2.2,
            "interpretation": "test",
            "madhab": "Hanafi",
        }
        result = lean_prover.verify_tafsir_rule(tafsir_rule)
        assert isinstance(result, ProofResult)

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.subprocess.run")
    def test_verify_tafsir_consistency(self, mock_run, lean_prover, mock_lean_output):
        """Test proof of tafsir consistency across madhabs."""
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_lean_output)
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        tafsir_rules = [
            {"ayah_number": 2.2, "madhab": "Hanafi"},
            {"ayah_number": 2.2, "madhab": "Maliki"},
        ]
        result = lean_prover.verify_tafsir_consistency(tafsir_rules)
        assert isinstance(result, ProofResult)


class TestCaching:
    """Test theorem caching and persistence."""

    def test_cache_clear(self, lean_prover):
        """Test cache can be cleared."""
        lean_prover.theorem_cache["test"] = ProofResult(
            verified=True, message="test", proof_steps=1, duration_ms=10
        )
        lean_prover.clear_cache()
        assert len(lean_prover.theorem_cache) == 0

    def test_cache_stats(self, lean_prover):
        """Test cache statistics."""
        lean_prover.theorem_cache["test1"] = ProofResult(
            verified=True, message="test1", proof_steps=1, duration_ms=10
        )
        lean_prover.theorem_cache["test2"] = ProofResult(
            verified=True, message="test2", proof_steps=2, duration_ms=20
        )
        stats = lean_prover.cache_stats()
        assert stats["cached_theorems"] == 2
        assert stats["total_proof_steps"] == 3
        assert stats["total_duration_ms"] == 30


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_lean_prover_error(self):
        """Test LeanProverError exception."""
        with pytest.raises(LeanProverError):
            raise LeanProverError("Test error")

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.LeanProver._run_lean_command")
    def test_lean_execution_timeout(self, mock_run_cmd, lean_prover):
        """Test timeout handling in Lean execution."""
        mock_run_cmd.side_effect = TimeoutError("Lean execution timeout")
        with pytest.raises(TimeoutError):
            lean_prover.verify_tajweed_rule("timeout_rule")

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.LeanProver._run_lean_command")
    def test_invalid_json_output(self, mock_run_cmd, lean_prover):
        """Test handling of invalid JSON from Lean."""
        mock_run_cmd.return_value = {
            "verified": False,
            "message": "Parse error"
        }

        with pytest.raises(LeanProverError):
            lean_prover.verify_tajweed_rule("invalid_json")


class TestLeanSyntaxValidation:
    """Test Lean syntax checking."""

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.subprocess.run")
    def test_validate_lean_syntax_success(self, mock_run, lean_prover):
        """Test successful syntax validation."""
        mock_process = MagicMock()
        mock_process.stdout = json.dumps({"valid": True})
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        valid = lean_prover.validate_lean_syntax("theorem test : True := trivial")
        assert valid is True

    @patch("frontier_neuro_symbolic.system_integration.lean_interface.LeanProver._run_lean_command")
    def test_validate_lean_syntax_failure(self, mock_run_cmd, lean_prover):
        """Test syntax validation failure."""
        mock_run_cmd.return_value = {"valid": False, "error": "Parse error"}

        valid = lean_prover.validate_lean_syntax("invalid theorem")
        assert valid is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
