-- Basic Quranic types and definitions for formal verification
-- Provides foundations: Ayah, Reading, Ruling, Madhab

import Mathlib.Data.List.Basic
import Mathlib.Order.Lattice

namespace FrontierQu

-- ============================================================================
-- Basic Quranic Types
-- ============================================================================

/-- A Surah (chapter) identifier, 1-114 -/
def SurahId := Fin 114

/-- An Ayah (verse) number within a surah -/
def AyahNumber := ℕ

/-- Ayah reference: (surah, ayah_number) -/
structure Ayah where
  surah : SurahId
  number : AyahNumber
  deriving BEq, Hashable

/-- A quranic reading (variant pronunciation/interpretation) -/
structure Reading where
  ayah : Ayah
  text : String
  reciter : String  -- e.g., "Hafs", "Warsh", "Qaloon"
  deriving BEq

/-- A tajweed (Quranic recitation rule) ruling -/
structure Ruling where
  id : String
  name : String  -- e.g., "Idgham Mutajanis", "Qalqala"
  description : String
  ayah_range : Ayah × Ayah  -- range of applicable ayahs
  deriving BEq

/-- Islamic school of jurisprudence -/
inductive Madhab : Type where
  | Hanafi : Madhab
  | Maliki : Madhab
  | Shafi : Madhab
  | Hanbali : Madhab
  deriving BEq, Hashable

-- ============================================================================
-- Predicates on Quranic Objects
-- ============================================================================

/-- A reading is valid if it conforms to known recitation standards -/
def IsValidReading (reading : Reading) : Prop :=
  reading.reciter ∈ ["Hafs", "Warsh", "Qaloon", "Duri", "Kisai"] ∧
  reading.text.length > 0

/-- A ruling applies to an ayah if it's within the ruling's range -/
def RulingAppliesToAyah (ruling : Ruling) (ayah : Ayah) : Prop :=
  ayah.surah.val >= ruling.ayah_range.1.surah.val ∧
  ayah.surah.val <= ruling.ayah_range.2.surah.val

/-- Two readings are equivalent if they refer to the same ayah -/
def ReadingsEquivalent (r1 r2 : Reading) : Prop :=
  r1.ayah = r2.ayah

-- ============================================================================
-- Properties
-- ============================================================================

/-- A valid reading cannot have empty text -/
theorem valid_reading_nonempty (reading : Reading) (h : IsValidReading reading) :
    reading.text.length > 0 := h.2

/-- Equivalence of readings is reflexive -/
theorem readings_equiv_refl (r : Reading) : ReadingsEquivalent r r := rfl

/-- Equivalence of readings is symmetric -/
theorem readings_equiv_symm (r1 r2 : Reading) :
    ReadingsEquivalent r1 r2 → ReadingsEquivalent r2 r1 := by
  intro h
  exact h.symm

/-- Equivalence of readings is transitive -/
theorem readings_equiv_trans (r1 r2 r3 : Reading) :
    ReadingsEquivalent r1 r2 → ReadingsEquivalent r2 r3 → ReadingsEquivalent r1 r3 := by
  intro h1 h2
  exact h1.trans h2

end FrontierQu
