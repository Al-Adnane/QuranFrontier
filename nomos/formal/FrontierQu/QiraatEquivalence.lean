-- Qiraat Equivalence: formalize the 7 canonical readings as equivalent types
-- Uses HoTT-inspired univalence to express that variant readings
-- preserving meaning are interchangeable in all contexts.

import FrontierQu.Basic

namespace FrontierQu.QiraatEquivalence

-- ============================================================================
-- Qiraat Variant Structure
-- ============================================================================

/-- Authenticity level of a qiraat reading -/
inductive Authenticity : Type where
  | mutawatir : Authenticity    -- mass-transmitted, highest grade
  | mashhur   : Authenticity    -- well-known, slightly below mutawatir
  | ahad      : Authenticity    -- single-chain, accepted by some scholars
  | shadhdh   : Authenticity    -- anomalous, not accepted for recitation
  deriving BEq, Hashable

/-- A qiraat variant: a specific reading tradition with its narrator chain -/
structure QiraatVariant where
  reading   : String            -- name of the reading (e.g., "Hafs", "Warsh")
  narrator  : String            -- primary narrator (raawi)
  imam      : String            -- the imam of the reading
  authenticity : Authenticity
  deriving BEq

-- ============================================================================
-- The 7 Canonical Readings (Al-Qira'at Al-Sab')
-- ============================================================================

/-- The seven canonical readings with their primary narrators -/
def nafi   : QiraatVariant := ⟨"Nafi'",    "Qaloon",  "Nafi' al-Madani",      .mutawatir⟩
def ibnKathir : QiraatVariant := ⟨"Ibn Kathir", "Al-Bazzi", "Ibn Kathir al-Makki", .mutawatir⟩
def abuAmr : QiraatVariant := ⟨"Abu Amr",  "Al-Duri",  "Abu Amr al-Basri",    .mutawatir⟩
def ibnAmir : QiraatVariant := ⟨"Ibn Amir", "Hisham",   "Ibn Amir al-Shami",   .mutawatir⟩
def asim   : QiraatVariant := ⟨"Asim",     "Hafs",     "Asim al-Kufi",        .mutawatir⟩
def hamza  : QiraatVariant := ⟨"Hamza",    "Khalaf",   "Hamza al-Zayyat",     .mutawatir⟩
def kisai  : QiraatVariant := ⟨"Al-Kisa'i","Al-Layth",  "Al-Kisa'i al-Kufi",   .mutawatir⟩

/-- The list of all 7 canonical readings -/
def canonicalSeven : List QiraatVariant :=
  [nafi, ibnKathir, abuAmr, ibnAmir, asim, hamza, kisai]

-- ============================================================================
-- Equivalence Relation on Readings
-- ============================================================================

/-- Two qiraat variants are equivalent if they both have mutawatir authenticity
    and refer to the same divine text (all canonical readings convey the same
    Quranic message despite pronunciation/recitation differences) -/
def QiraatEquiv (q1 q2 : QiraatVariant) : Prop :=
  q1.authenticity = .mutawatir ∧ q2.authenticity = .mutawatir

-- ============================================================================
-- Axiom: All 7 Canonical Readings Are Equivalent
-- ============================================================================

/-- Axiom: every canonical reading is mutawatir (mass-transmitted) -/
axiom canonical_all_mutawatir :
  ∀ q ∈ canonicalSeven, q.authenticity = Authenticity.mutawatir

/-- Axiom: any two canonical readings are equivalent in their conveyance
    of the Quranic message. This is the foundational principle of
    'ilm al-qira'at: variant readings are all valid divine revelation. -/
axiom canonical_pairwise_equiv :
  ∀ q1 q2 : QiraatVariant,
    q1 ∈ canonicalSeven → q2 ∈ canonicalSeven → QiraatEquiv q1 q2

-- ============================================================================
-- Properties of QiraatEquiv
-- ============================================================================

/-- QiraatEquiv is reflexive on canonical readings -/
theorem qiraat_equiv_refl (q : QiraatVariant) (h : q ∈ canonicalSeven) :
    QiraatEquiv q q :=
  canonical_pairwise_equiv q q h h

/-- QiraatEquiv is symmetric -/
theorem qiraat_equiv_symm (q1 q2 : QiraatVariant) :
    QiraatEquiv q1 q2 → QiraatEquiv q2 q1 := by
  intro ⟨h1, h2⟩
  exact ⟨h2, h1⟩

/-- QiraatEquiv is transitive -/
theorem qiraat_equiv_trans (q1 q2 q3 : QiraatVariant) :
    QiraatEquiv q1 q2 → QiraatEquiv q2 q3 → QiraatEquiv q1 q3 := by
  intro ⟨h1, _⟩ ⟨_, h3⟩
  exact ⟨h1, h3⟩

-- ============================================================================
-- HoTT-Inspired Univalence Stub
-- ============================================================================

/-- A qiraat transport: if two readings are equivalent, any property
    provable about one is provable about the other.
    This is the qiraat analogue of the univalence axiom:
    (q1 ≃ q2) → (P q1 ↔ P q2) -/
axiom qiraat_univalence :
  ∀ (P : QiraatVariant → Prop) (q1 q2 : QiraatVariant),
    QiraatEquiv q1 q2 → (P q1 ↔ P q2)

/-- Corollary: a property true of Hafs (the most common reading today)
    holds for all canonical readings -/
theorem hafs_universal (P : QiraatVariant → Prop)
    (h_hafs : P asim) :
    ∀ q ∈ canonicalSeven, P q := by
  intro q hq
  have h_equiv := canonical_pairwise_equiv asim q
    (by simp [canonicalSeven]; tauto)
    hq
  exact (qiraat_univalence P asim q h_equiv).mp h_hafs

end FrontierQu.QiraatEquivalence
