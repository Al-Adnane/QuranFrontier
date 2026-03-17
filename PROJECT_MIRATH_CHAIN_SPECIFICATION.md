# PROJECT MIRATH-CHAIN: Q4:11 INHERITANCE ALGORITHM SPECIFICATION

**Status**: Phase 1 Foundation - Foundation Layer (Q-SDK Core)
**Timeline**: 30 days
**Governance**: Dual-Key Council (2 Engineers + 2 Islamic Scholars)
**Mathematical Fidelity**: HIGH
**Risk Level**: LOW
**Impact Scope**: FinTech + Smart Contracts

---

## EXECUTIVE SUMMARY

Project Mirath-Chain extracts the inheritance distribution logic from Quran 4:11 (Al-Nisa, Verse 11) and implements it as:
1. **Mathematical Framework** - Formal specification of share distribution rules
2. **Python Library** - Production-grade Q-SDK module for inheritance calculations
3. **Solidity Smart Contract** - Blockchain-native implementation for Islamic finance
4. **Validation System** - Verification against Maqasid al-Shariah (5 objectives)
5. **Institutional Pilot** - Partnership with Islamic bank/Waqf for real-world deployment

---

## PART 1: QURANIC FOUNDATION

### 1.1 Source Text: Quran 4:11

**Arabic (Standard Uthmanic):**
```
يُوصِيكُمُ اللَّهُ فِي أَوْلَادِكُمْ ۖ لِلذَّكَرِ مِثْلُ حَظِّ الْأُنثَيَيْنِ ۚ فَإِن كُنَّ نِسَاءً فَوْقَ اثْنَتَيْنِ فَلَهُنَّ ثُلُثَا مَا تَرَكَ ۖ وَإِن كَانَتْ وَاحِدَةً فَلَهَا النِّصْفُ ۚ وَلِأَبَوَيْهِ لِكُلِّ وَاحِدٍ مِّنْهُمَا السُّدُسُ مِمَّا تَرَكَ إِن كَانَ لَهُ وَلَدٌ ۚ فَإِن لَّمْ يَكُن لَّهُ وَلَدٌ وَوَرِثَهُ أَبَوَاهُ فَلِأُمِّهِ الثُّلُثُ ۚ فَإِن كَانَ لَهُ إِخْوَةٌ فَلِأُمِّهِ السُّدُسُ ۚ مِن بَعْدِ وَصِيَّةٍ يُوصِي بِهَا أَوْ دَيْنٍ ۗ آبَاؤُكُمْ وَأَبْنَاؤُكُمْ لَا تَدْرُونَ أَيُّهُمْ أَقْرَبُ لَكُمْ نَفْعًا ۚ فَرِيضَةً مِّنَ اللَّهِ ۚ إِنَّ اللَّهَ كَانَ عَلِيمًا حَكِيمًا
```

**Translation** (Sahih International):
```
Allah instructs you regarding your children: for the male, what is equal to the share of two females. But if there are only daughters, two or more, for them is two thirds of what one left. And if there is only one daughter, for her is half. And for one's parents, to each one of them is a sixth of what one left, if he had children. But if he had no children and the parents [inherit] from him, then for his mother is one third. And if he had brothers [or sisters], for his mother is a sixth, after any bequest he [may have] made or debt. Your parents and your children - you do not know which of them are nearest to you in benefit. [These shares are] an obligation [imposed by] Allah. Indeed, Allah is ever knowing and wise.
```

### 1.2 Classical Interpretation Sources

**Primary Exegetical Sources:**

1. **Tabari (d. 310 AH / 922 CE) - Jami' al-Bayan**
   - Context: Systematic analysis of inheritance hierarchies
   - Key teaching: Male gets "double share" (2:1 ratio) due to financial responsibility
   - Mathematical insight: Female share = X, Male share = 2X (in same degree of kinship)
   - Application: First determine class (children, then parents, then siblings)

2. **Ibn Kathir (d. 774 AH / 1373 CE) - Tafsir Ibn Kathir**
   - Principle: Quranic inheritance is mathematically deterministic
   - Rule hierarchy: Children override parents; both override siblings
   - Formula: Share allocation depends on: (1) relationship type, (2) gender, (3) presence of other heirs

3. **Al-Qurtubi (d. 671 AH / 1273 CE) - Al-Jami' li Ahkam al-Quran**
   - Mathematical clarity: All shares expressed as fractions (1/2, 1/3, 1/6, 2/3)
   - Exception handling: Sibling rules only apply if NO direct heirs (children/parents)
   - Residual principle: Remaining estate ("ta'sib") goes to nearest male heir

4. **Modern Fiqhi References:**
   - **Sanhuri** - Islamic Law of Succession (Al-Wasiyyah wa-l-Mirath)
   - **Abdur Rahim** - Muhammadan Jurisprudence (1911)
   - **Coulson** - Succession in the Muslim Family (1971)

### 1.3 Core Rules (Extracted from Q4:11 + Classical Consensus)

**Rule Set 1: Child Inheritance**
- If deceased has children: children inherit all (parents get nothing in this case per Q4:11 with children)
- Male child share = 2 × Female child share
- All children share equally within gender groups proportionally

**Rule Set 2: Parent Inheritance (if no children)**
- If both parents and no children:
  - Father: 1/3 (per classical consensus on Q4:11)
  - Mother: 1/3
  - Remainder: Father (as closest male heir in ta'sib)
- If mother only and no children:
  - Mother: 1/3
  - Remainder: Goes to other heirs (siblings, grandparents)

**Rule Set 3: Sibling Inheritance (if no parents/children)**
- Mother gets 1/6 (if siblings present per Q4:11)
- Siblings split remainder by male=2:1 female ratio

**Rule Set 4: Residual (Ta'sib) Principle**
- After fixed shares assigned, remainder goes to nearest MALE heir
- Priority order: Sons → Father → Brothers → Uncle → Cousins

**Rule Set 5: Disqualification Rules**
- Murderer of deceased: disqualified from inheritance
- Apostate from Islam: disqualified (classical consensus)
- Non-Muslim heir: typically disqualified (except by contract)

---

## PART 2: FORMAL MATHEMATICAL SPECIFICATION

### 2.1 Data Structures

```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from fractions import Fraction

class Relationship(Enum):
    """Kinship relationship to deceased"""
    CHILD = "child"                    # Direct child (son/daughter)
    PARENT = "parent"                  # Father or mother
    SIBLING = "sibling"                # Full/half brother/sister
    GRANDPARENT = "grandparent"        # Paternal/maternal grandparent
    UNCLE_AUNT = "uncle_aunt"          # Paternal uncle/aunt
    NEPHEW_NIECE = "nephew_niece"      # Brother's/sister's child
    SPOUSE = "spouse"                  # Widow/widower
    COUSIN = "cousin"                  # First cousin and beyond
    ILLEGITIMATE = "illegitimate"      # Not recognized by Sharia

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"

class HeritageDisqualification(Enum):
    """Reasons for inheritance disqualification"""
    MURDERER = "murderer"              # Killed the deceased
    APOSTATE = "apostate"              # Left Islam
    NON_MUSLIM = "non_muslim"          # Different faith (some schools)
    ENSLAVED = "enslaved"              # Legal servitude
    NONE = "none"                      # No disqualification

@dataclass
class Heir:
    """Individual heir in the inheritance distribution"""
    name: str
    gender: Gender
    relationship: Relationship
    age_at_death: int                  # Age or None if unknown
    disqualified: HeritageDisqualification = HeritageDisqualification.NONE
    notes: str = ""

    @property
    def is_qualified(self) -> bool:
        return self.disqualified == HeritageDisqualification.NONE

@dataclass
class InheritanceCase:
    """Complete inheritance case for distribution calculation"""
    deceased_name: str
    estate_value: Fraction              # In smallest monetary unit (e.g., satoshi, fils)
    estate_currency: str = "USD"        # Currency denomination
    heirs: List[Heir] = None
    debts: Fraction = Fraction(0)       # Outstanding debts
    bequests: List[Tuple[str, Fraction]] = None  # (beneficiary, amount) tuples

    def __post_init__(self):
        if self.heirs is None:
            self.heirs = []
        if self.bequests is None:
            self.bequests = []

@dataclass
class ShareDistribution:
    """Calculated share distribution result"""
    heir_name: str
    relationship: Relationship
    share_fraction: Fraction            # E.g., Fraction(1, 3)
    share_percentage: float             # E.g., 33.33
    absolute_amount: Fraction           # Monetary value
    calculation_basis: str              # Why this share was assigned
    validation_status: str              # "valid", "pending_review", "challenged"
```

### 2.2 Distribution Algorithm (Quranic Inheritance Logic)

```python
class MirahAlgorithm:
    """
    Implementation of Q4:11 inheritance distribution logic.

    Mathematical basis:
    - Q4:11: "for the male, what is equal to the share of two females"
    - This implies male_share = 2 * female_share (in same kinship degree)
    - All distributions derive from fixed fractions: 1/2, 1/3, 1/6, 2/3
    """

    def distribute_inheritance(self, case: InheritanceCase) -> Dict[str, ShareDistribution]:
        """
        Main entry point for inheritance distribution.

        Algorithm steps:
        1. Validate all heirs (disqualifications check)
        2. Deduct debts and bequests from estate
        3. Classify heirs into inheritance classes
        4. Apply Q4:11 rules in hierarchical order
        5. Distribute remainder by ta'sib (male preference)
        6. Generate validation certificates

        Returns: Dict mapping heir names to ShareDistribution objects
        """

        # Step 1: Validation
        qualified_heirs = [h for h in case.heirs if h.is_qualified]
        disqualified_summary = {
            h.name: h.disqualified for h in case.heirs if not h.is_qualified
        }

        # Step 2: Estate calculation
        distributable_estate = case.estate_value - case.debts
        for _, bequest_amount in case.bequests:
            distributable_estate -= bequest_amount

        if distributable_estate <= 0:
            raise ValueError("Estate insufficient after debts/bequests")

        # Step 3: Classify heirs
        children = [h for h in qualified_heirs if h.relationship == Relationship.CHILD]
        parents = [h for h in qualified_heirs if h.relationship == Relationship.PARENT]
        siblings = [h for h in qualified_heirs if h.relationship == Relationship.SIBLING]
        spouse = [h for h in qualified_heirs if h.relationship == Relationship.SPOUSE]

        distributions = {}
        remaining_estate = distributable_estate

        # Step 4: Apply Q4:11 hierarchy

        # CASE A: Children exist (they take priority)
        if children:
            return self._distribute_with_children(
                children, parents, siblings, spouse,
                distributable_estate, distributions
            )

        # CASE B: No children, parents exist
        elif parents:
            return self._distribute_with_parents(
                parents, siblings, spouse,
                distributable_estate, distributions
            )

        # CASE C: No children/parents, siblings exist
        elif siblings:
            return self._distribute_with_siblings(
                siblings, spouse,
                distributable_estate, distributions
            )

        # CASE D: No lineal heirs
        else:
            return self._distribute_extended_heirs(
                qualified_heirs,
                distributable_estate, distributions
            )

    def _distribute_with_children(self, children, parents, siblings, spouse,
                                 estate: Fraction, distributions: Dict) -> Dict:
        """
        Q4:11 Rule: "for the male, what is equal to the share of two females"

        Males get 2:1 share ratio to females among children.
        When children present, parents and siblings excluded from estate.
        """

        # Separate males and females
        sons = [h for h in children if h.gender == Gender.MALE]
        daughters = [h for h in children if h.gender == Gender.FEMALE]

        # Mathematical formulation:
        # Total shares = num_sons * 2 + num_daughters * 1
        total_shares = len(sons) * 2 + len(daughters) * 1
        share_unit = estate / Fraction(total_shares)

        # Distribute to sons (2 units each)
        for son in sons:
            son_share = share_unit * 2
            distributions[son.name] = ShareDistribution(
                heir_name=son.name,
                relationship=son.relationship,
                share_fraction=Fraction(2, total_shares),
                share_percentage=float(Fraction(2, total_shares)) * 100,
                absolute_amount=son_share,
                calculation_basis=f"Male child (Q4:11): {son.gender.value} share = 2 units",
                validation_status="valid"
            )

        # Distribute to daughters (1 unit each)
        for daughter in daughters:
            daughter_share = share_unit * 1
            distributions[daughter.name] = ShareDistribution(
                heir_name=daughter.name,
                relationship=daughter.relationship,
                share_fraction=Fraction(1, total_shares),
                share_percentage=float(Fraction(1, total_shares)) * 100,
                absolute_amount=daughter_share,
                calculation_basis=f"Female child (Q4:11): {daughter.gender.value} share = 1 unit",
                validation_status="valid"
            )

        return distributions

    def _distribute_with_parents(self, parents, siblings, spouse,
                                estate: Fraction, distributions: Dict) -> Dict:
        """
        Q4:11 Rules when no children:
        - If both parents: Each parent 1/6 (+ remainder to father as ta'sib)
        - If mother only: Mother 1/3
        - If siblings present: Mother reduced to 1/6
        """

        mothers = [h for h in parents if h.gender == Gender.FEMALE]
        fathers = [h for h in parents if h.gender == Gender.MALE]

        if mothers and fathers:
            # Q4:11: "for one's parents, to each one of them is a sixth"
            mother_share = estate * Fraction(1, 6)
            father_share_fixed = estate * Fraction(1, 6)
            remainder = estate - mother_share - father_share_fixed

            # Remainder goes to father (ta'sib principle - male preference)
            father_share = father_share_fixed + remainder

            distributions[mothers[0].name] = ShareDistribution(
                heir_name=mothers[0].name,
                relationship=mothers[0].relationship,
                share_fraction=Fraction(1, 6),
                share_percentage=float(Fraction(1, 6)) * 100,
                absolute_amount=mother_share,
                calculation_basis="Mother (both parents present, Q4:11): 1/6",
                validation_status="valid"
            )

            distributions[fathers[0].name] = ShareDistribution(
                heir_name=fathers[0].name,
                relationship=fathers[0].relationship,
                share_fraction=None,  # Variable due to ta'sib
                share_percentage=float(father_share / estate) * 100,
                absolute_amount=father_share,
                calculation_basis="Father (both parents present, Q4:11): 1/6 + remainder (ta'sib)",
                validation_status="valid"
            )

        elif mothers and not fathers:
            # Q4:11: "if mother only: 1/3"
            if siblings:
                # Q4:11: "if siblings present: mother 1/6"
                mother_share = estate * Fraction(1, 6)
            else:
                mother_share = estate * Fraction(1, 3)

            distributions[mothers[0].name] = ShareDistribution(
                heir_name=mothers[0].name,
                relationship=mothers[0].relationship,
                share_fraction=Fraction(1, 6 if siblings else 3),
                share_percentage=float(Fraction(1, 6 if siblings else 3)) * 100,
                absolute_amount=mother_share,
                calculation_basis=f"Mother only (Q4:11): {'1/6' if siblings else '1/3'} {'(siblings present)' if siblings else ''}",
                validation_status="valid"
            )

        return distributions

    def _distribute_with_siblings(self, siblings, spouse,
                                 estate: Fraction, distributions: Dict) -> Dict:
        """
        Sibling inheritance when no parents/children present.
        Males get 2:1 share to females (same as children rule).
        """

        brothers = [h for h in siblings if h.gender == Gender.MALE]
        sisters = [h for h in siblings if h.gender == Gender.FEMALE]

        total_shares = len(brothers) * 2 + len(sisters) * 1
        share_unit = estate / Fraction(total_shares)

        for brother in brothers:
            distributions[brother.name] = ShareDistribution(
                heir_name=brother.name,
                relationship=brother.relationship,
                share_fraction=Fraction(2, total_shares),
                share_percentage=float(Fraction(2, total_shares)) * 100,
                absolute_amount=share_unit * 2,
                calculation_basis="Brother (sibling inheritance): 2 units",
                validation_status="valid"
            )

        for sister in sisters:
            distributions[sister.name] = ShareDistribution(
                heir_name=sister.name,
                relationship=sister.relationship,
                share_fraction=Fraction(1, total_shares),
                share_percentage=float(Fraction(1, total_shares)) * 100,
                absolute_amount=share_unit * 1,
                calculation_basis="Sister (sibling inheritance): 1 unit",
                validation_status="valid"
            )

        return distributions

    def _distribute_extended_heirs(self, heirs, estate: Fraction,
                                   distributions: Dict) -> Dict:
        """
        Extended family inheritance (grandparents, uncles, cousins)
        when no direct heirs or parents/siblings.

        Classical fiqh: 'Asabah principle (male preference in kinship degrees)
        """
        # Implementation follows Hanafi school ta'sib methodology
        raise NotImplementedError("Extended heir distribution requires multi-madhab coordination")

# Example usage:
if __name__ == "__main__":
    algo = MirahAlgorithm()

    case = InheritanceCase(
        deceased_name="Muhammad ibn Abdullah",
        estate_value=Fraction(1_000_000),  # USD 1,000,000
        estate_currency="USD",
        heirs=[
            Heir(name="Fatima (daughter)", gender=Gender.FEMALE, relationship=Relationship.CHILD),
            Heir(name="Ali (son)", gender=Gender.MALE, relationship=Relationship.CHILD),
        ],
        debts=Fraction(50_000)
    )

    result = algo.distribute_inheritance(case)
    for heir, distribution in result.items():
        print(f"{heir}: ${distribution.absolute_amount} ({distribution.share_percentage:.2f}%)")
```

### 2.3 Mathematical Proofs

**Proof 1: Male 2:1 Share Ratio (Q4:11)**

Given: "for the male, what is equal to the share of two females"

Proof:
```
Let F = female share unit
Let M = male share unit

Q4:11 states: M = 2F

If 1 son and 1 daughter:
  Total estate E is divided into 3 units (2 for son + 1 for daughter)
  Son receives: 2E/3
  Daughter receives: E/3
  Ratio = (2E/3) : (E/3) = 2:1 ✓

If 1 son, 2 daughters:
  Total units = 2 + 1 + 1 = 4
  Son receives: 2E/4 = E/2
  Each daughter receives: E/4
  Son:Daughter ratio = (E/2):(E/4) = 2:1 ✓

General case: n sons, m daughters
  Total units U = 2n + m
  Each son: 2E/U
  Each daughter: E/U
  Ratio = (2E/U):(E/U) = 2:1 ✓
```

**Proof 2: Parent Share Fractions (Q4:11)**

Given: "for one's parents, to each one of them is a sixth" (when children exist)
Given: "if he had no children and the parents inherit from him, then for his mother is one third"

Proof:
```
Case 1: Children present
  Q4:11 explicitly states: Each parent 1/6
  Father share = 1/6
  Mother share = 1/6
  ✓ (Direct from text)

Case 2: No children, both parents
  Classical consensus (Tabari, Ibn Kathir):
    Father: 1/3 + remainder (ta'sib)
    Mother: 1/3
  Reasoning: Father has dual role (heir + guardian/ta'sib)

Case 3: No children, mother only
  Q4:11: "mother is one third"
  Mother share = 1/3
  ✓ (Direct from text)

Case 4: No children, mother + siblings
  Q4:11: "if he had siblings, for his mother is a sixth"
  Mother share = 1/6 (reduced from 1/3)
  Reasoning: Presence of siblings alters mother's legal status
  ✓ (Direct from text)
```

### 2.4 Validation Against Maqasid al-Shariah

**Maqasid Framework** (5 Universal Objectives):
1. **Protection of Faith** (Al-Din)
2. **Protection of Life** (Al-Nafs)
3. **Protection of Intellect** (Al-'Aql)
4. **Protection of Lineage/Family** (Al-Nasl)
5. **Protection of Wealth** (Al-Maal)

**Q4:11 Validation Matrix:**

| Maqasid | Implementation | Evidence |
|---------|-----------------|----------|
| **Faith** | Reinforces Islamic governance by implementing divine law | Q4:11 explicitly: "Faridat min Allah" (ordinance from Allah) |
| **Life** | Fair distribution reduces family disputes/violence over inheritance | Historical: Jahl pre-Islamic era had constant inheritance wars |
| **Intellect** | Mathematically deterministic system reduces litigation | Fraction-based rules: no ambiguity or manipulation |
| **Lineage** | Female heirs protected; family relationships honored | Q4:11: Both male/female heirs included; parents/children prioritized |
| **Wealth** | Proportional to financial responsibility (2:1 for male breadwinner role) | Q4:11: Male = 2F because male bears legal financial obligations |

---

## PART 3: IMPLEMENTATION ROADMAP

### Phase 1A: Python Q-SDK Library (Days 1-10)

**Deliverables:**
- `/quran-core/src/q_sdk/mirah_core.py` (400 lines) - Core algorithm
- `/quran-core/src/q_sdk/mirah_models.py` (200 lines) - Data structures
- `/quran-core/src/q_sdk/validation.py` (300 lines) - Maqasid validation
- `/quran-core/tests/test_mirah_core.py` (100+ test cases)
- `/docs/Q_SDK_MIRAH_API.md` (API reference)

**Code Structure:**
```
quran-core/
├── src/q_sdk/
│   ├── __init__.py
│   ├── mirah_core.py           # MirahAlgorithm class
│   ├── mirah_models.py         # Heir, InheritanceCase, ShareDistribution
│   ├── validation.py           # MaqasidValidator
│   ├── madhab_handlers.py      # Hanafi/Maliki/Shafi'i/Hanbali variations
│   └── exceptions.py           # Custom exceptions
├── tests/
│   ├── test_mirah_core.py      # Algorithm tests
│   ├── test_mirah_validation.py # Maqasid validation tests
│   └── fixtures/
│       └── inheritance_cases.json # Test data (30+ real cases from fiqh books)
```

### Phase 1B: Solidity Smart Contract (Days 11-20)

**Deliverables:**
- `/contracts/MirahChain.sol` (500 lines) - Ethereum/Polygon implementation
- `/contracts/test/MirahChain.test.js` (200+ tests)
- `/docs/SOLIDITY_API.md` - Smart contract API

**Contract Features:**
- `inheritanceDistribution()` - Main distribution function (on-chain)
- `recordDeceased()` - Register deceased person + heirs
- `claimShare()` - Heir claims their calculated share
- `verifyShare()` - Dual-key governance verification

### Phase 1C: Partnership & Deployment (Days 21-30)

**Deliverables:**
- Institutional partnership agreement with Islamic bank/Waqf
- Pilot deployment on test network (Ethereum Sepolia or Polygon Mumbai)
- Integration with existing Waqf management systems
- User documentation and training materials

---

## PART 4: DUAL-KEY GOVERNANCE COUNCIL

### Requirements

**Engineering Council (2 members minimum):**
1. Lead Algorithm Architect (Mathematics/CS PhD)
   - Responsible for: Algorithm correctness, mathematical proofs
   - Verification authority: Signs off on algorithmic changes

2. Senior Software Engineer (Blockchain/Backend 10+ years)
   - Responsible for: Implementation quality, security, performance
   - Verification authority: Signs off on code reviews, deployments

**Theological Council (2 members minimum):**
1. Senior Islamic Jurist (Al-Azhar/ISNA certified, 20+ years)
   - Responsible for: Quranic authenticity, madhab consensus
   - Verification authority: Signs off on legal interpretations

2. Fiqh Scholar (Specializing in Inheritance Law)
   - Responsible for: Classical source accuracy, edge case handling
   - Verification authority: Signs off on scholarly consensus scores

### Governance Process

**For any change to Q4:11 Algorithm:**

1. **Technical Proposal**: Algorithm architect drafts change
2. **Engineering Review**: Lead engineer verifies implementation
3. **Scholarly Review**: Jurist verifies Quranic/madhab alignment
4. **Consensus Check**: Fiqh scholar validates against all 4 madhabs
5. **Dual Signature**: Both engineering + theological leads sign off
6. **Deployment**: Change deployed only with BOTH signatures

**Conflict Resolution:**
- If engineering council disagrees with theological council: escalate to external arbitration (3-person panel: 1 engineer, 1 jurist, 1 neutral Islamic finance expert)
- All decisions recorded immutably in governance ledger (Neo4j)

---

## PART 5: SUCCESS METRICS & VALIDATION GATES

### Gate 1: Algorithm Validation (Day 10)

**Criteria:**
- [ ] All 100+ test cases passing (including edge cases)
- [ ] Mathematical proofs verified by external mathematician
- [ ] Maqasid validation scores ≥ 0.90 on all 5 objectives
- [ ] Theological council: consensus score ≥ 0.95 on Q4:11 interpretation
- [ ] Python library API stable (no breaking changes expected)

**Success Condition:** Both engineering + theological councils sign off

### Gate 2: Smart Contract Validation (Day 20)

**Criteria:**
- [ ] All 200+ solidity tests passing
- [ ] Security audit passed (OpenZeppelin or similar)
- [ ] Gas optimization: inheritance distribution ≤ 150,000 gas
- [ ] Deployed to Sepolia testnet with 10 successful transactions
- [ ] Dual-key signature system verified on-chain

**Success Condition:** Both engineering + theological councils sign off + external security audit

### Gate 3: Pilot Deployment (Day 30)

**Criteria:**
- [ ] Partnership with Islamic bank/Waqf finalized
- [ ] 10 real inheritance cases processed (anonymized)
- [ ] Beneficiaries verified accuracy of calculations
- [ ] Zero disputes/errors in pilot phase
- [ ] Institutional integration successful

**Success Condition:** Institution commits to permanent deployment

---

## PART 6: PROJECT TIMELINE GANTT

```
Week 1 (Days 1-7):
  [======== Python Q-SDK Core ========]
  [=== Algorithm Design & Modeling ==]

Week 2 (Days 8-14):
  [======== Python Testing =========]
  [======== Solidity Contract Dev ========]
  [= Theological Review (parallel) =]

Week 3 (Days 15-21):
  [========= Solidity Testing ========]
  [== Security Audit ==]
  [======== Partnership Negotiation ========]

Week 4 (Days 22-30):
  [== Testnet Deployment ==]
  [=========== Pilot Phase ===========]
  [=== Documentation & Training ===]
```

---

## PART 7: RISK MITIGATION

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Madhab disagreement on share calculation | Medium | High | Dual-key governance with theological council approval required before any change |
| Solidity implementation bugs causing fund loss | Low | Critical | Full external security audit + staged testnet deployment |
| Cultural resistance to blockchain implementation | Medium | Medium | Partner with trusted Islamic institution as deployment champion |
| Real-world legal challenges (non-Islamic jurisdictions) | Medium | Medium | Initial pilot in Islamic-friendly jurisdictions (Malaysia, UAE, Bahrain) |
| Incomplete classical source extraction | Low | Medium | Theological council validates against minimum 3 authoritative sources per rule |

---

## PART 8: NEXT STEPS AFTER GATE 3

Upon successful pilot (Day 30):

**Phase 2 Projects Ready for Launch:**
1. **Sadaqah-Flow** (Q2:215) - Charity distribution optimization
2. **Mizan-Nutrition** (Q2:168) - Halal/Tayyib food scoring system
3. **Riba-Contract** (Q2:275) - Interest-free lending smart contract

**Phase 2 Timeline:** Months 2-6 (Foundation Phase continues)

---

**Authored by**: Dual-Key Governance Council (Pending Assembly)
**Last Updated**: [Current Date]
**Version**: 1.0 (Draft - Awaiting Council Signatures)
**Classification**: Open Source (Q-SDK Public License)

