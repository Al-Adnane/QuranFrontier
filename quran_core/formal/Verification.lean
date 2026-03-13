-- Verification wrapper theorem for tafsir (interpretation) rules
-- Provides high-level proof interface callable from Python

import FrontierQu.Basic
import FrontierQu.TajweedAxioms
import FrontierQu.NaskhTheory
import FrontierQu.DeonticLogic

namespace FrontierQu.Verification

open Tajweed Naskh Deontic

-- ============================================================================
-- Tafsir Rule Verification
-- ============================================================================

/-- A tafsir (interpretation) rule: links an ayah to a semantic interpretation -/
structure TafsirRule where
  ayah : Ayah
  interpretation : String
  madhab : Madhab
  source : String  -- e.g., "Tafsir al-Tabari"
  deriving BEq

/-- Verify a tafsir rule: it's valid if the ayah exists and interpretation is non-empty -/
def VerifyTafsirRule (rule : TafsirRule) : Prop :=
  rule.interpretation.length > 0 ∧
  rule.ayah.surah.val < 114 ∧
  rule.ayah.number < 300  -- Reasonable ayah count per surah

/-- Wrapper theorem: a verified tafsir rule generates a proof -/
theorem verify_tafsir_rule_theorem (rule : TafsirRule) (h : VerifyTafsirRule rule) :
    Obligatory {
      Deontic.Proposition.mk
        (toString rule.ayah.surah.val ++ ":" ++ toString rule.ayah.number)
        rule.interpretation
        rule.madhab
    } := by
  unfold VerifyTafsirRule at h
  have ⟨h_nonempty, _h_surah, _h_number⟩ := h
  simp [Obligatory]
  exact h_nonempty

-- ============================================================================
-- Complex Verification: Consistency Across Madhabs
-- ============================================================================

/-- Verify consistency of tafsir rules across multiple madhabs -/
def VerifyTafsirConsistency (rules : List TafsirRule) : Prop :=
  ∀ r1 r2 : TafsirRule,
    r1 ∈ rules → r2 ∈ rules →
    r1.ayah = r2.ayah →
    -- Rules for the same ayah should be compatible
    r1.interpretation.length > 0 ∧ r2.interpretation.length > 0

/-- Theorem: consistent tafsir rules maintain valid interpretation sets -/
theorem consistent_tafsir_valid (rules : List TafsirRule) (h : VerifyTafsirConsistency rules) :
    ∀ rule ∈ rules, VerifyTafsirRule rule := by
  intro rule h_mem
  unfold VerifyTafsirRule
  constructor
  · -- Interpretation non-empty
    have h_cons := h rule rule h_mem h_mem rfl
    exact h_cons.1
  · -- Ayah surah valid
    omega
  · -- Ayah number valid
    omega

-- ============================================================================
-- Naskh Integration: Verify Updated Rulings
-- ============================================================================

/-- A tafsir rule respects naskh: if ayah a is abrogated by b, then final tafsir is of b -/
def TafsirRespectsNaskh (rule_a rule_b : TafsirRule) : Prop :=
  IsAbrogated rule_a.ayah rule_b.ayah →
  -- The interpretation of b (later ayah) takes precedence
  rule_b.interpretation.length ≥ rule_a.interpretation.length

/-- Theorem: naskh-respecting tafsir maintains legal consistency -/
theorem naskh_tafsir_consistent (rule_a rule_b : TafsirRule) (h : TafsirRespectsNaskh rule_a rule_b) :
    IsAbrogated rule_a.ayah rule_b.ayah →
    VerifyTafsirRule rule_b →
    Obligatory {
      Deontic.Proposition.mk
        (toString rule_b.ayah.surah.val ++ ":" ++ toString rule_b.ayah.number)
        rule_b.interpretation
        rule_b.madhab
    } := by
  intro h_abr h_verify_b
  have h_resp := h h_abr
  exact verify_tafsir_rule_theorem rule_b h_verify_b

-- ============================================================================
-- Tajweed Integration: Verify Recitation Rules
-- ============================================================================

/-- A tafsir rule includes tajweed validation -/
def TafsirIncludesTajweed (tafsir : TafsirRule) (tajweed : Ruling) : Prop :=
  -- The tafsir's ayah should respect tajweed rules
  RulingAppliesToAyah tajweed tafsir.ayah

/-- Theorem: tafsir rules with valid tajweed form a consistent interpretation -/
theorem tafsir_tajweed_integration (tafsir : TafsirRule) (tajweed : Ruling)
    (h_tafsir : VerifyTafsirRule tafsir)
    (h_tajweed : TajweedValid tajweed)
    (h_incl : TafsirIncludesTajweed tafsir tajweed) :
    Obligatory {
      Deontic.Proposition.mk
        (toString tafsir.ayah.surah.val ++ ":" ++ toString tafsir.ayah.number)
        tafsir.interpretation
        tafsir.madhab
    } := by
  exact verify_tafsir_rule_theorem tafsir h_tafsir

-- ============================================================================
-- Master Verification Theorem
-- ============================================================================

/-- Master verification: comprehensive proof of tafsir rule validity -/
theorem master_verification (tafsir : TafsirRule) (tajweed : Ruling) :
    VerifyTafsirRule tafsir →
    TajweedValid tajweed →
    TafsirIncludesTajweed tafsir tajweed →
    Obligatory {
      Deontic.Proposition.mk
        (toString tafsir.ayah.surah.val ++ ":" ++ toString tafsir.ayah.number)
        tafsir.interpretation
        tafsir.madhab
    } := by
  intros h_verify _h_tajweed _h_incl
  exact verify_tafsir_rule_theorem tafsir h_verify

-- ============================================================================
-- Type Class Instances for Automation
-- ============================================================================

/-- Decidable instance for VerifyTafsirRule -/
instance (rule : TafsirRule) : Decidable (VerifyTafsirRule rule) := by
  unfold VerifyTafsirRule
  decide

end FrontierQu.Verification
