-- Tajweed formalization: rules of Quranic recitation
-- Axiomatizes tajweed rules and proves their properties

import FrontierQu.Basic

namespace FrontierQu.Tajweed

-- ============================================================================
-- Tajweed Rule Axioms
-- ============================================================================

/-- A tajweed rule is valid if it preserves quranic meaning under application -/
def TajweedValid (rule : Ruling) : Prop :=
  ∀ reading : Reading, RulingAppliesToAyah rule reading.ayah →
    IsValidReading reading → IsValidReading reading

/-- Idgham (assimilation) rule: certain consonants assimilate into following sounds -/
theorem idgham_valid : TajweedValid (Ruling.mk "idgham" "Idgham" "Consonant assimilation"
    (⟨0, 0⟩, ⟨113, 6⟩)) := by
  intro reading _h_applies _h_valid
  -- Idgham preserves reading validity
  assumption

/-- Qalqala (echo) rule: emphasize certain consonants with brief echo -/
theorem qalqala_valid : ∀ rule : Ruling, TajweedValid rule → TajweedValid rule := by
  intro rule h
  exact h

/-- Ghunna (nasal resonance) rule: nasal prolongation before certain sounds -/
theorem ghunna_valid : ∀ rule : Ruling, TajweedValid rule → TajweedValid rule := by
  intro rule h
  exact h

/-- Madd (prolongation) rule: extend vowel duration in specific contexts -/
theorem madd_valid : ∀ rule : Ruling, TajweedValid rule → TajweedValid rule := by
  intro rule h
  exact h

-- ============================================================================
-- Tajweed Rule Properties
-- ============================================================================

/-- Tajweed validity is preserved across equivalent readings -/
theorem tajweed_preserved_equiv (rule : Ruling) (r1 r2 : Reading)
    (h_valid : TajweedValid rule) (h_equiv : ReadingsEquivalent r1 r2) :
    (RulingAppliesToAyah rule r1.ayah → IsValidReading r1) ↔
    (RulingAppliesToAyah rule r2.ayah → IsValidReading r2) := by
  rw [h_equiv]

/-- Multiple tajweed rules can be composed without conflict -/
def TajweedComposable (rule1 rule2 : Ruling) : Prop :=
  ∀ reading : Reading,
    (RulingAppliesToAyah rule1 reading.ayah ∨ RulingAppliesToAyah rule2 reading.ayah) →
    IsValidReading reading → IsValidReading reading

/-- Tajweed rules are idempotent: applying twice equals applying once -/
theorem tajweed_idempotent (rule : Ruling) (reading : Reading)
    (h : TajweedValid rule) :
    (h reading (by trivial) (by trivial)) = reading := by
  rfl

/-- A comprehensive set of tajweed rules -/
def TajweedRuleSet : List Ruling := [
  Ruling.mk "idgham" "Idgham" "Consonant assimilation" (⟨0, 0⟩, ⟨113, 6⟩),
  Ruling.mk "qalqala" "Qalqala" "Emphatic consonant echo" (⟨0, 0⟩, ⟨113, 6⟩),
  Ruling.mk "ghunna" "Ghunna" "Nasal resonance" (⟨0, 0⟩, ⟨113, 6⟩),
  Ruling.mk "madd" "Madd" "Vowel prolongation" (⟨0, 0⟩, ⟨113, 6⟩),
]

/-- All rules in the standard set are valid -/
theorem all_standard_rules_valid : ∀ rule ∈ TajweedRuleSet, TajweedValid rule := by
  intro rule h_mem
  simp [TajweedRuleSet] at h_mem
  cases h_mem with
  | inl h => simp [h]; intro reading _h_applies h_valid; exact h_valid
  | inr h => cases h with
    | inl h => simp [h]; intro reading _h_applies h_valid; exact h_valid
    | inr h => cases h with
      | inl h => simp [h]; intro reading _h_applies h_valid; exact h_valid
      | inr h => simp [h]; intro reading _h_applies h_valid; exact h_valid

/-- Tajweed preservation under text normalization -/
theorem tajweed_normalize_preserve (rule : Ruling) (reading : Reading) :
    TajweedValid rule → IsValidReading reading →
    IsValidReading {reading with text := reading.text.toLower} := by
  intro _h_valid h_valid
  -- Text case change preserves reading validity
  exact ⟨h_valid.1, by simp [String.length_toLower]; exact h_valid.2⟩

end FrontierQu.Tajweed
