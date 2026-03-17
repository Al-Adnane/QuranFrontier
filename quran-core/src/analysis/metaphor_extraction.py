"""
Quranic Metaphor and Story Extraction Framework

This module provides algorithmic representations of core Quranic metaphors
and narratives as computational structures, enabling analysis of embedded
principles, system dynamics, and contemporary applications.

Author: Claude Code Research
Date: March 2026
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple, Optional
from abc import ABC, abstractmethod
import math


# ==================== CORE ENUMS ====================

class SystemType(Enum):
    """Classification of system types in metaphors"""
    MULTI_AGENT = "multi_agent"  # Bee, spider
    LOAD_BEARING = "load_bearing"  # Mountain
    INFORMATION = "information"  # Light, water
    GROWTH = "growth"  # Palm tree
    EQUILIBRIUM = "equilibrium"  # Garden
    NETWORK = "network"  # Rope, spider
    DISRUPTION = "disruption"  # Wind, storm


class FragilityLevel(Enum):
    """Fragility assessment levels"""
    ROBUST = 0.1
    RESILIENT = 0.3
    VULNERABLE = 0.6
    FRAGILE = 0.85
    CRITICAL = 0.95


class Principle(Enum):
    """Core principles embedded in metaphors"""
    DISTRIBUTED_CONSENSUS = "distributed_consensus"
    SINGLE_POINT_FAILURE = "single_point_failure"
    CAPACITY_LIMITS = "capacity_limits"
    LAYERED_TRANSMISSION = "layered_transmission"
    FOUNDATION_PRIORITY = "foundation_priority"
    ADAPTIVE_ALLOCATION = "adaptive_allocation"
    SUSTAINABILITY = "sustainability"
    RESILIENCE_THROUGH_DEPTH = "resilience_through_depth"


# ==================== BASE CLASSES ====================

class QuranicMetaphor(ABC):
    """Abstract base class for Quranic metaphors with dual-layer classification"""

    def __init__(self, name: str, reference: str, quranic_text: str):
        self.name = name
        self.reference = reference
        self.quranic_text = quranic_text
        self.principles: List[Principle] = []
        self.system_type: Optional[SystemType] = None
        self.fragility_index: float = 0.0

        # Dual-layer fields
        self.classical_meaning: str = ""  # Level 1: Classical tafsir foundation
        self.source_tafsirs: List[str] = []  # Classical Islamic scholars
        self.contemporary_application: str = ""  # Level 2: Modern analytical framework
        self.application_domain: List[str] = []  # Fields where application applies
        self.robustness_score: float = 0.0  # Confidence in application (0-1.0)

    @abstractmethod
    def extract_algorithmic_structure(self) -> Dict:
        """Extract algorithmic representation"""
        pass

    @abstractmethod
    def analyze_edge_cases(self) -> List[Dict]:
        """Identify edge cases and system failures"""
        pass

    @abstractmethod
    def get_applications(self) -> List[Tuple[str, str]]:
        """Get (domain, application) pairs"""
        pass

    def calculate_robustness(self) -> float:
        """Calculate system robustness (1 - fragility)"""
        return 1.0 - self.fragility_index

    def get_principles_summary(self) -> Dict[str, str]:
        """Get summary of embedded principles"""
        return {p.value: p.value for p in self.principles}


class QuranicStory(ABC):
    """Abstract base class for Quranic narratives"""

    def __init__(self, name: str, reference: str, duration_years: int):
        self.name = name
        self.reference = reference
        self.duration_years = duration_years
        self.core_principles: List[str] = []
        self.phases: List[str] = []
        self.key_insights: List[str] = []

    @abstractmethod
    def extract_narrative_algorithm(self) -> Dict:
        """Extract algorithmic representation of narrative"""
        pass

    @abstractmethod
    def analyze_transformation_arc(self) -> Dict:
        """Analyze character/system transformation"""
        pass

    @abstractmethod
    def get_recovery_mechanisms(self) -> List[Dict]:
        """Get mechanisms of recovery/integration"""
        pass


# ==================== METAPHOR IMPLEMENTATIONS ====================

@dataclass
class BeeParameters:
    """Parameters for bee colony system"""
    num_scouts: int = 10
    num_foragers: int = 100
    num_processors: int = 50
    fitness_threshold: float = 0.7
    information_propagation_speed: float = math.log(110)  # O(ln n)
    adaptation_time_hours: float = 3.0


class BeeMetaphor(QuranicMetaphor):
    """
    AL-NAHL (16:68-69) - The Bee

    Distributed consensus algorithm with collective decision-making.
    No central authority; emergent decisions from local interactions.
    """

    def __init__(self):
        super().__init__(
            name="The Bee (Al-Nahl)",
            reference="Surah 16:68-69",
            quranic_text="""
            wa-awha rabbuka ila-n-nahli ani-ttakhidhi mina-l-jibali buyuta
            wa-mina-sh-shajari wa-mimma ya'rishun. Thumma kulee min kulli-th-thamarati
            fa-shrukee subula rabbiki thullulan yakhruju min butooniha sharabun
            mukhtalifun alwanuh feehi shifaun linnas.
            """
        )
        self.params = BeeParameters()
        self.system_type = SystemType.MULTI_AGENT
        self.principles = [
            Principle.DISTRIBUTED_CONSENSUS,
            Principle.ADAPTIVE_ALLOCATION,
            Principle.SUSTAINABILITY,
        ]
        self.fragility_index = 0.15  # Very robust system

        # Dual-layer fields
        self.classical_meaning = "Divine inspiration to bees for construction and production of honey; honey as healing substance. Verified in Ibn Kathir, Al-Tabari, Al-Qurtubi, Al-Razi."
        self.source_tafsirs = [
            "Ibn Kathir (Tafsir al-Qur'an al-Adhim)",
            "Al-Tabari (Jami' al-Bayan)",
            "Al-Qurtubi (Al-Jami' li-Ahkam al-Qur'an)",
            "Al-Razi (Tafsir al-Fakhr al-Razi)"
        ]
        self.contemporary_application = "Distributed consensus algorithms in decentralized systems. Swarm intelligence algorithms without central authority. Emergent collective decision-making."
        self.application_domain = [
            "Blockchain consensus",
            "Peer-to-peer networks",
            "Distributed governance",
            "Multi-agent systems",
            "Swarm robotics"
        ]
        self.robustness_score = 0.85

    def extract_algorithmic_structure(self) -> Dict:
        """Extract bee consensus algorithm"""
        return {
            "states": ["exploration", "recruitment", "coordination", "harvesting", "processing"],
            "decision_mechanism": "waggle_dance_consensus",
            "communication_overhead": f"O(n * ln({self.params.num_scouts}))",
            "fitness_function": "quality * accessibility / (1 + distance)",
            "feedback_loops": {
                "positive": "high_quality_location → stronger_signal → more_workers",
                "negative": "depleted_resource → signal_decay → exploration",
                "stabilizing": "equilibrium_maintenance → balanced_foraging"
            },
            "redundancy_factor": 1.3,  # System survives 30% scout loss
            "communication_efficiency": 0.85,  # 15% overhead
        }

    def analyze_edge_cases(self) -> List[Dict]:
        """Edge cases for bee system"""
        return [
            {
                "case": "information_poisoning",
                "violation": "false_waggle_dance",
                "detection": "redundancy_catches_mismatch",
                "failure_threshold": "33%_false_signals",
                "lesson": "trust_but_verify"
            },
            {
                "case": "tragedy_of_commons",
                "violation": "over_harvesting_single_location",
                "mechanism": "signal_decay_reduces_allocation",
                "prevention": "scouts_naturally_reduce_signaling",
                "outcome": "resource_sustainability"
            },
            {
                "case": "local_optimum_trap",
                "violation": "all_workers_focus_one_location",
                "recovery": "exploratory_scouts_find_better",
                "time_cost_hours": 2-3,
                "lesson": "exploration_prevents_stagnation"
            }
        ]

    def get_applications(self) -> List[Tuple[str, str]]:
        """Application contexts"""
        return [
            ("Supply Chain", "distributed_warehouse_network_decision"),
            ("Consensus Algorithms", "blockchain_transaction_validation"),
            ("Crowdsourcing", "collective_intelligence_platforms"),
            ("Traffic Flow", "autonomous_vehicle_routing"),
            ("Data Centers", "server_load_balancing"),
            ("Swarm Robotics", "multi_robot_coordination"),
            ("Markets", "information_aggregation_price_discovery"),
        ]


class SpiderMetaphor(QuranicMetaphor):
    """
    AL-ANKABUT (29:41) - The Spider

    False authority network with catastrophic single-point-of-failure.
    Star network topology masked as strength, actually extremely fragile.
    """

    def __init__(self):
        super().__init__(
            name="The Spider (Al-Ankabut)",
            reference="Surah 29:41",
            quranic_text="""
            mathalu alladheen ittakhathoo min dooni Allahi awliyaa kamathal
            al-'ankabut ittakhathath bayta wal-'ankabut awhanu al-buyoot
            inlaw alimoo.
            """
        )
        self.system_type = SystemType.NETWORK
        self.principles = [
            Principle.SINGLE_POINT_FAILURE,
        ]
        self.fragility_index = FragilityLevel.CRITICAL.value

        # Dual-layer fields
        self.classical_meaning = "False gods/authorities are like spider's web - appears structured but is frailest of all houses. Verified in Al-Tabari, Al-Qurtubi, Ibn Kathir."
        self.source_tafsirs = [
            "Al-Tabari (Jami' al-Bayan)",
            "Al-Qurtubi (Al-Jami' li-Ahkam al-Qur'an)",
            "Ibn Kathir (Tafsir al-Qur'an al-Adhim)"
        ]
        self.contemporary_application = "Analysis of single-point-of-failure systems and organizational fragility. Network topology vulnerability assessment. Failure cascade analysis."
        self.application_domain = [
            "Network topology analysis",
            "Organizational resilience",
            "Risk management",
            "Cybersecurity",
            "Supply chain vulnerability"
        ]
        self.robustness_score = 0.88

    def extract_algorithmic_structure(self) -> Dict:
        """Extract spider web topology"""
        return {
            "topology": "star_network",
            "center": "false_authority",
            "followers": ["follower_1", "follower_2", "..."],
            "robustness_formula": "R(n) = 1 - (1/n)",
            "single_points_of_failure": 1,
            "network_resilience": "approaches_0_as_n_increases",
            "horizontal_connections": 0,
            "failure_recovery": "impossible",
            "collapse_speed": "instant_upon_center_failure"
        }

    def analyze_edge_cases(self) -> List[Dict]:
        """Edge cases for spider system"""
        return [
            {
                "case": "center_damaged_survives",
                "violation": "some_followers_leave",
                "system_requirement": "must_expand_or_die",
                "lesson": "growth_is_compulsory"
            },
            {
                "case": "attempted_horizontal_bond",
                "violation": "followers_bypass_center",
                "response": "schism_or_reformation",
                "observation": "centralized_systems_suppress_bonds"
            },
            {
                "case": "external_predation",
                "vulnerability": "center_cannot_protect",
                "network_status": "entirely_vulnerable",
                "contrast": "decentralized_can_isolate_damage"
            }
        ]

    def get_applications(self) -> List[Tuple[str, str]]:
        """Application contexts"""
        return [
            ("Governance", "CEO_only_decision_making"),
            ("Religion", "cult_leader_centered_groups"),
            ("Politics", "dictatorial_single_person_rule"),
            ("Finance", "ponzi_schemes_mlm_structures"),
            ("Technology", "single_company_market_dominance"),
            ("Relationships", "codependent_relationships"),
            ("Supply Chain", "single_supplier_dependency"),
            ("Knowledge", "dogmatic_authority_systems"),
        ]


class MountainMetaphor(QuranicMetaphor):
    """
    AL-JABAL (7:143) - The Mountain

    Capacity and threshold analysis. Finite systems have maximum bearing capacity.
    Exceeding capacity causes catastrophic failure. Prophets have greater capacity.
    """

    def __init__(self):
        super().__init__(
            name="The Mountain (Al-Jabal)",
            reference="Surah 7:143",
            quranic_text="""
            wa-lamma ja'a Musa lima'adna-hu wa-takallama-hu rabbuhu qala rabbi
            arani anzur ilayka. Qala lan tarani wa-lakin anzur ila-l-jebali...
            """
        )
        self.system_type = SystemType.LOAD_BEARING
        self.principles = [
            Principle.CAPACITY_LIMITS,
        ]
        self.fragility_index = 0.5

        # Dual-layer fields
        self.classical_meaning = "Every system has finite capacity; even mountains cannot bear infinite load. Demonstrates limits of creation. Verified in Ibn Kathir, Al-Tabari, Al-Qurtubi."
        self.source_tafsirs = [
            "Ibn Kathir (Tafsir al-Qur'an al-Adhim)",
            "Al-Tabari (Jami' al-Bayan)",
            "Al-Qurtubi (Al-Jami' li-Ahkam al-Qur'an)"
        ]
        self.contemporary_application = "Capacity analysis and threshold-based system design. Identifying breaking points and system limits. Graceful degradation under load."
        self.application_domain = [
            "Engineering systems",
            "Cloud infrastructure",
            "Organizational capacity",
            "Software scaling",
            "Disaster recovery"
        ]
        self.robustness_score = 0.87

    def extract_algorithmic_structure(self) -> Dict:
        """Extract capacity model"""
        return {
            "capacity_model": {
                "mountain_capacity": 1e12,
                "prophet_capacity": 1e15,
                "human_capacity": 1e10,
                "angel_capacity": "infinity"
            },
            "stability_condition": "input_load < system_capacity",
            "failure_condition": "input_load >= system_capacity",
            "system_response": {
                "mountain": "disintegration",
                "prophet": "temporary_incapacity_then_recovery",
                "angel": "perfect_perception"
            },
            "design_principles": [
                "capacity_engineering",
                "input_filtering",
                "phased_integration"
            ],
            "safety_factor": 3.0  # Design for 3x expected load
        }

    def analyze_edge_cases(self) -> List[Dict]:
        """Edge cases for capacity system"""
        return [
            {
                "case": "under_designed_system",
                "violation": "load_2x_while_designed_for_x",
                "prevention": "design_for_max_plus_safety"
            },
            {
                "case": "graceful_vs_catastrophic",
                "mountain": "binary_collapse",
                "prophet": "graceful_degradation",
                "engineering": "implement_circuit_breakers"
            },
            {
                "case": "adaptation_without_preparation",
                "result": "resistance_or_failure",
                "principle": "change_requires_preparation"
            }
        ]

    def get_applications(self) -> List[Tuple[str, str]]:
        """Application contexts"""
        return [
            ("Engineering", "system_capacity_planning"),
            ("Org Change", "change_management_protocols"),
            ("Education", "curriculum_pacing"),
            ("Leadership", "succession_planning"),
            ("Team Expansion", "scaling_and_onboarding"),
            ("Infrastructure", "database_capacity_design"),
            ("Personal", "learning_and_growth"),
            ("Politics", "reform_implementation"),
        ]


class LightMetaphor(QuranicMetaphor):
    """
    AN-NUR (24:35-40) - The Light

    Epistemological model of knowledge transmission through multiple layers.
    Pure divine knowledge filtered through layers of mediation to reach humans.
    """

    def __init__(self):
        super().__init__(
            name="The Light (An-Nur)",
            reference="Surah 24:35-40",
            quranic_text="""
            Allahu nuru as-samawati wa-al-ard, mathalu nurihi ka-mikhfatin
            fiha mishkah, fi-al-mishkah qindil, al-qindilu fi zujajah...
            """
        )
        self.system_type = SystemType.INFORMATION
        self.principles = [
            Principle.LAYERED_TRANSMISSION,
        ]
        self.fragility_index = 0.3

        # Dual-layer fields
        self.classical_meaning = "Knowledge transmission through layered system: divine revelation → prophetic heart → textual transmission → human understanding. Verified in Ibn Kathir, Al-Qurtubi, Al-Zamakhshari."
        self.source_tafsirs = [
            "Ibn Kathir (Tafsir al-Qur'an al-Adhim)",
            "Al-Qurtubi (Al-Jami' li-Ahkam al-Qur'an)",
            "Al-Zamakhshari (Al-Kashshaf)"
        ]
        self.contemporary_application = "Information fidelity through layered transmission systems. Signal integrity analysis. Designing transmission architecture for knowledge preservation."
        self.application_domain = [
            "Knowledge management",
            "Data transmission",
            "Educational scaffolding",
            "Telecommunications",
            "Knowledge graphs"
        ]
        self.robustness_score = 0.86

    def extract_algorithmic_structure(self) -> Dict:
        """Extract epistemological layers"""
        return {
            "layers": 6,
            "layer_sequence": [
                "divine_reality",
                "revelation_source",
                "prophetic_reception",
                "linguistic_expression",
                "textual_preservation",
                "scholarly_interpretation",
                "personal_illumination"
            ],
            "attenuation_model": "each_layer_has_filter_factor",
            "total_transmission": "pure_knowledge * ∏(filter_i)",
            "necessary_conditions": [
                "niche_prepared",
                "light_available",
                "clarity_present",
                "grounding_known",
                "medium_adequate",
                "reflection_possible"
            ],
            "understanding": "boolean_AND_of_all_conditions",
            "missing_condition_result": "darkness"
        }

    def analyze_edge_cases(self) -> List[Dict]:
        """Edge cases for light system"""
        return [
            {
                "case": "glass_becomes_opaque",
                "violation": "textual_tradition_corrupted",
                "recovery": "return_to_original_source"
            },
            {
                "case": "niche_becomes_hard",
                "violation": "heart_hardens_against_truth",
                "mechanism": "psychological_defense",
                "prevention": "regular_self_examination"
            },
            {
                "case": "oil_becomes_stagnant",
                "violation": "tradition_dies_becomes_academic",
                "recovery": "return_to_practical_application"
            }
        ]

    def get_applications(self) -> List[Tuple[str, str]]:
        """Application contexts"""
        return [
            ("Education", "knowledge_transmission"),
            ("Mentorship", "wisdom_transfer"),
            ("Science", "theory_to_practice"),
            ("Therapy", "psychological_healing"),
            ("Organizations", "institutional_learning"),
            ("Media", "truth_in_information_age"),
            ("Leadership", "vision_and_direction"),
            ("Art", "inspiration_and_craft"),
        ]


class PalmTreeMetaphor(QuranicMetaphor):
    """
    AN-NAKHLA (14:24-25) - The Palm Tree

    Foundation and sustainable growth model. Deep roots enable long-term
    productivity. Visible growth proportional to hidden foundation strength.
    """

    def __init__(self):
        super().__init__(
            name="The Palm Tree (An-Nakhla)",
            reference="Surah 14:24-25",
            quranic_text="""
            'A-lam tara kayfa dharaba Allahu mathalan kalimatan tayyibah
            ka-shajarah tayyibah, asluha thabit wa-far'uha fi as-sama'...
            """
        )
        self.system_type = SystemType.GROWTH
        self.principles = [
            Principle.FOUNDATION_PRIORITY,
            Principle.RESILIENCE_THROUGH_DEPTH,
        ]
        self.fragility_index = 0.2

        # Dual-layer fields
        self.classical_meaning = "Good word/foundation with deep roots and strong branches produces continuous fruit. Visible success depends entirely on hidden foundations. Verified in Ibn Kathir, Al-Tabari, Al-Qurtubi."
        self.source_tafsirs = [
            "Ibn Kathir (Tafsir al-Qur'an al-Adhim)",
            "Al-Tabari (Jami' al-Bayan)",
            "Al-Qurtubi (Al-Jami' li-Ahkam al-Qur'an)"
        ]
        self.contemporary_application = "Organizational growth model: strong foundations enable sustainable expansion. System architecture determining scalability. Long-term value from foundational investment."
        self.application_domain = [
            "Strategic planning",
            "Organizational development",
            "Software architecture",
            "Infrastructure investment",
            "Product lifecycle"
        ]
        self.robustness_score = 0.89

    def extract_algorithmic_structure(self) -> Dict:
        """Extract growth model"""
        return {
            "components": {
                "roots": "deep_penetration_hidden_work",
                "trunk": "visible_growth_structural_integrity",
                "fruit": "regular_productive_output"
            },
            "growth_formula": "visible_growth = root_strength * water_access * time",
            "fruit_reliability": "depends_on_consistent_root_strength",
            "foundation_phases": {
                "years_1_3": "root_development_hidden",
                "years_3_plus": "exponential_growth"
            },
            "resilience_metric": {
                "deep_roots": "survives_drought_storms",
                "shallow_roots": "vulnerable_to_adversity"
            },
            "sustainability": "long_term_fruit_bearing"
        }

    def analyze_edge_cases(self) -> List[Dict]:
        """Edge cases for growth system"""
        return [
            {
                "case": "rapid_growth_no_foundation",
                "result": "unstable_vulnerable_to_crisis",
                "failure_pattern": "collapse_when_tested"
            },
            {
                "case": "all_root_no_growth",
                "problem": "foundation_without_purpose",
                "solution": "balance_both"
            },
            {
                "case": "replanting_mistakes",
                "violation": "move_tree_without_roots",
                "result": "death_despite_strength",
                "lesson": "understand_systems_before_disrupting"
            }
        ]

    def get_applications(self) -> List[Tuple[str, str]]:
        """Application contexts"""
        return [
            ("Personal", "self_improvement_trajectory"),
            ("Business", "company_building_phases"),
            ("Education", "learning_progression"),
            ("Leadership", "leader_development"),
            ("Relationships", "building_trust"),
            ("Technology", "product_development"),
            ("Community", "organization_building"),
            ("Health", "wellness_maintenance"),
        ]


class GardenMetaphor(QuranicMetaphor):
    """
    AL-JANNAH (2:265-266) - The Garden

    Equilibrium and resource balance. Garden requires ongoing care and proper conditions.
    Demonstrates systems need balance between investment and maintenance.
    """

    def __init__(self):
        super().__init__(
            name="The Garden (Al-Jannah)",
            reference="Surah 2:265-266",
            quranic_text="""
            wa-mathalu alladheen yunfiqoon amwalahum ibtighaa mardati Allahi...
            """
        )
        self.system_type = SystemType.EQUILIBRIUM
        self.principles = [Principle.SUSTAINABILITY, Principle.ADAPTIVE_ALLOCATION]
        self.fragility_index = 0.3
        self.classical_meaning = "Garden requires balanced conditions (water, soil, elevation); proper investment produces abundance; neglect causes loss. Verified in Ibn Kathir, Al-Qurtubi."
        self.source_tafsirs = ["Ibn Kathir (Tafsir al-Qur'an al-Adhim)", "Al-Qurtubi (Al-Jami' li-Ahkam al-Qur'an)", "Al-Tabari (Jami' al-Bayan)"]
        self.contemporary_application = "Ecosystem modeling and resource balance management. System equilibrium requires ongoing maintenance and proper environmental conditions."
        self.application_domain = ["Environmental sustainability", "Economic systems", "Resource allocation", "Project management"]
        self.robustness_score = 0.84

    def extract_algorithmic_structure(self) -> Dict:
        return {
            "components": {"water": "rainfall_irrigation", "soil": "nutrients_foundation", "elevation": "drainage"},
            "balance_formula": "garden_health = investment + maintenance + environmental_factors",
            "equilibrium_condition": "input_water >= evaporation + plant_uptake",
        }

    def analyze_edge_cases(self) -> List[Dict]:
        return [
            {"case": "over_investment_no_maintenance", "result": "wastage_rot"},
            {"case": "maintenance_no_investment", "result": "depletion_poverty"},
            {"case": "perfect_balance", "result": "sustained_abundance"},
        ]

    def get_applications(self) -> List[Tuple[str, str]]:
        return [
            ("Environment", "ecosystem_management"),
            ("Economics", "resource_allocation"),
            ("Health", "lifestyle_balance"),
            ("Organization", "sustainable_operations"),
        ]


class WaterMetaphor(QuranicMetaphor):
    """
    AL-MA' (18:109) - Water/Ocean

    Infinity and overflow. Divine words/knowledge are infinite; no finite resource can contain them.
    """

    def __init__(self):
        super().__init__(
            name="The Water/Ocean (Al-Ma')",
            reference="Surah 18:109",
            quranic_text="""
            Qul law kana al-bahr midaddan li-kalimati rabbi lanatifa al-bahr...
            """
        )
        self.system_type = SystemType.INFORMATION
        self.principles = [Principle.CAPACITY_LIMITS]
        self.fragility_index = 0.15
        self.classical_meaning = "Divine words/knowledge are infinite; no finite resource can contain them. Demonstrates divine boundlessness. Verified in Ibn Kathir, Al-Qurtubi, Al-Tabari."
        self.source_tafsirs = ["Ibn Kathir (Tafsir al-Qur'an al-Adhim)", "Al-Qurtubi (Al-Jami' li-Ahkam al-Qur'an)", "Al-Zamakhshari (Al-Kashshaf)"]
        self.contemporary_application = "Scalability analysis and asymptotic behavior in exponential systems. Understanding limits of finite systems in infinite domains."
        self.application_domain = ["Big data management", "Knowledge systems", "Information overflow", "Database scalability"]
        self.robustness_score = 0.85

    def extract_algorithmic_structure(self) -> Dict:
        return {
            "finite_container": "ocean",
            "infinite_content": "divine_knowledge",
            "overflow": "inevitable",
            "conclusion": "bounded_cannot_contain_unbounded",
        }

    def analyze_edge_cases(self) -> List[Dict]:
        return [
            {"case": "attempting_to_contain_infinite", "result": "overflow_loss"},
        ]

    def get_applications(self) -> List[Tuple[str, str]]:
        return [
            ("Computing", "database_limits"),
            ("Knowledge", "information_management"),
            ("Religion", "divine_infinity"),
        ]


class WindMetaphor(QuranicMetaphor):
    """
    AL-RIAH (105:1-5) - Wind/Storm

    System disruption and resilience. External disruptions destroy systems regardless of
    internal strength. Emphasizes vulnerability to environmental catastrophe.
    """

    def __init__(self):
        super().__init__(
            name="The Wind/Storm (Al-Riah)",
            reference="Surah 105:1-5",
            quranic_text="""
            'Alam tara kayfa fa'ala rabbuka bi-ashabi al-feel...
            """
        )
        self.system_type = SystemType.DISRUPTION
        self.principles = [Principle.SINGLE_POINT_FAILURE]
        self.fragility_index = 0.4
        self.classical_meaning = "External disruptions destroy systems regardless of internal strength. Unpredictable events require humility. Verified in Ibn Kathir, Al-Tabari, Al-Qurtubi."
        self.source_tafsirs = ["Ibn Kathir (Tafsir al-Qur'an al-Adhim)", "Al-Tabari (Jami' al-Bayan)", "Al-Qurtubi (Al-Jami' li-Ahkam al-Qur'an)"]
        self.contemporary_application = "Disruption analysis and systems resilience to external shocks. Chaos theory and antifragility design for handling unpredictable events."
        self.application_domain = ["Risk management", "Business continuity", "Crisis response", "Organizational agility"]
        self.robustness_score = 0.82

    def extract_algorithmic_structure(self) -> Dict:
        return {
            "system": "false_confidence",
            "disruption": "external_catastrophe",
            "outcome": "complete_destruction",
            "lesson": "humility_before_forces_beyond_control",
        }

    def analyze_edge_cases(self) -> List[Dict]:
        return [
            {"case": "internal_strength_external_catastrophe", "result": "collapse"},
        ]

    def get_applications(self) -> List[Tuple[str, str]]:
        return [
            ("Risk", "external_threat_assessment"),
            ("Strategy", "disaster_planning"),
            ("Resilience", "adaptation_capacity"),
        ]


class MirrorMetaphor(QuranicMetaphor):
    """
    AL-ZUJAJ (24:40) - Mirror/Glass

    Distortion and perception. False beliefs create distorted perception like glass that
    refracts light. Demonstrates how understanding medium affects perceived reality.
    """

    def __init__(self):
        super().__init__(
            name="The Mirror/Glass (Al-Zujaj)",
            reference="Surah 24:40",
            quranic_text="""
            wa-mathalu alladheen kafaru ka-mathali alladhee yenqu bi-ayyadihi...
            """
        )
        self.system_type = SystemType.INFORMATION
        self.principles = [Principle.LAYERED_TRANSMISSION]
        self.fragility_index = 0.35
        self.classical_meaning = "False beliefs create distorted perception like glass refracting light. Perception depends on clarity of medium. Verified in Ibn Kathir, Al-Qurtubi, Al-Tabari."
        self.source_tafsirs = ["Ibn Kathir (Tafsir al-Qur'an al-Adhim)", "Al-Qurtubi (Al-Jami' li-Ahkam al-Qur'an)", "Al-Zamakhshari (Al-Kashshaf)"]
        self.contemporary_application = "Information filtering and cognitive bias analysis. Signal integrity and noise analysis in information systems."
        self.application_domain = ["Data quality", "Signal processing", "Epistemic systems", "User interface design"]
        self.robustness_score = 0.79

    def extract_algorithmic_structure(self) -> Dict:
        return {
            "medium": "glass_or_belief_system",
            "input": "light_or_information",
            "output": "refracted_distorted_or_clear",
            "factor": "quality_of_medium",
        }

    def analyze_edge_cases(self) -> List[Dict]:
        return [
            {"case": "distorted_medium", "result": "false_perception"},
            {"case": "clear_medium", "result": "accurate_perception"},
        ]

    def get_applications(self) -> List[Tuple[str, str]]:
        return [
            ("Communication", "clarity_in_transmission"),
            ("Cognition", "bias_detection"),
            ("Technology", "interface_clarity"),
        ]


class RopeMetaphor(QuranicMetaphor):
    """
    AL-HABL (3:103) - Rope

    Unity and cohesion. The rope holds together; division breaks the rope. Strength emerges
    from cohesion. Collective bond provides protection against separation and harm.
    """

    def __init__(self):
        super().__init__(
            name="The Rope (Al-Habl)",
            reference="Surah 3:103",
            quranic_text="""
            wa-i'tasimoo bi-hablillahi jamee'an wa-la tafarraqoo...
            """
        )
        self.system_type = SystemType.NETWORK
        self.principles = [Principle.DISTRIBUTED_CONSENSUS, Principle.RESILIENCE_THROUGH_DEPTH]
        self.fragility_index = 0.15
        self.classical_meaning = "Unity and cohesion are rope; hold together; division is breaking rope. Strength emerges from cohesion. Verified in Ibn Kathir, Al-Tabari, Al-Qurtubi."
        self.source_tafsirs = ["Ibn Kathir (Tafsir al-Qur'an al-Adhim)", "Al-Tabari (Jami' al-Bayan)", "Al-Qurtubi (Al-Jami' li-Ahkam al-Qur'an)"]
        self.contemporary_application = "Social network strength and organizational cohesion metrics. Graph theory analysis of connectivity and network resilience."
        self.application_domain = ["Team dynamics", "Organizational culture", "Network analysis", "Leadership development"]
        self.robustness_score = 0.88

    def extract_algorithmic_structure(self) -> Dict:
        return {
            "components": {"strands": "individuals", "weave": "connection_and_trust"},
            "strength_formula": "rope_strength = number_of_strands * quality_of_weave",
            "failure_mode": "break_if_separated",
            "resilience": "distributed_across_many_connections",
        }

    def analyze_edge_cases(self) -> List[Dict]:
        return [
            {"case": "perfect_unity", "result": "maximum_strength"},
            {"case": "some_separation", "result": "weakened_but_functional"},
            {"case": "complete_separation", "result": "no_strength_no_protection"},
        ]

    def get_applications(self) -> List[Tuple[str, str]]:
        return [
            ("Organization", "team_cohesion"),
            ("Society", "social_bonds"),
            ("Network", "connectivity_resilience"),
            ("Leadership", "unity_building"),
        ]


# ==================== STORY IMPLEMENTATIONS ====================

class TraumaRecoverySystem:
    """Algorithmic model of trauma integration and recovery"""

    @staticmethod
    def recovery_phases() -> Dict[str, Dict]:
        """Stages of trauma integration"""
        return {
            'phase_1_shock': {
                'duration': 'days_to_weeks',
                'symptom': 'disbelief_denial',
                'mechanism': 'immediate_survival_response'
            },
            'phase_2_pain': {
                'duration': 'weeks_to_years',
                'symptom': 'grief_anger_despair',
                'mechanism': 'emotional_processing'
            },
            'phase_3_meaning_making': {
                'duration': 'months_to_years',
                'symptom': 'questioning_learning',
                'mechanism': 'cognitive_reframing'
            },
            'phase_4_integration': {
                'duration': 'years',
                'symptom': 'acceptance_wisdom',
                'mechanism': 'narrative_reconstruction'
            },
            'phase_5_transcendence': {
                'duration': 'lifelong',
                'symptom': 'wisdom_applicable_to_others',
                'mechanism': 'meaning_generation'
            }
        }

    @staticmethod
    def joseph_timeline() -> Dict[str, Dict]:
        """Joseph's specific recovery timeline"""
        return {
            'age_12': {'event': 'vision_family_conflict', 'processing': 0.0},
            'age_12_17': {'event': 'betrayal_slavery', 'processing': 0.1},
            'age_17_24': {'event': 'temptation_accusation', 'processing': 0.2},
            'age_24_31': {'event': 'imprisonment_dream_interpretation', 'processing': 0.4},
            'age_31_37': {'event': 'waiting_for_opportunity', 'processing': 0.5},
            'age_37_40': {'event': 'elevation_family_reunion', 'processing': 0.8},
            'age_40_plus': {'event': 'forgiveness_integration', 'processing': 1.0}
        }


class JosephStory(QuranicStory):
    """
    YUSUF (12:1-111) - Joseph

    Trauma recovery, pattern recognition, trust system design.
    Complete narrative of betrayal → testing → vindication → forgiveness.
    """

    def __init__(self):
        super().__init__(
            name="Joseph (Yusuf)",
            reference="Surah 12:1-111",
            duration_years=40
        )
        self.core_principles = [
            "trauma_integration",
            "meaning_making",
            "forgiveness",
            "trust_building"
        ]
        self.phases = [
            "innocence_vision",
            "betrayal_trauma",
            "loss_status",
            "false_accusation",
            "wisdom_opportunity",
            "vindication_power",
            "family_reunion",
            "complete_integration"
        ]

    def extract_narrative_algorithm(self) -> Dict:
        """Extract Joseph's narrative as algorithm"""
        return {
            "states": self.phases,
            "total_duration_years": 40,
            "trauma_onset_age": 12,
            "integration_complete_age": 40,
            "processing_path": {
                "initial_processing": 0.1,
                "meaning_making": 0.4,
                "vindication": 0.8,
                "complete_integration": 1.0
            },
            "key_insight": "purpose_maintenance_throughout_trauma",
            "forgiveness_conditions": [
                "achieved_own_justice",
                "understood_brother_motivation",
                "extracted_meaning_from_trauma",
                "secure_in_identity",
                "positioned_to_extend_grace"
            ]
        }

    def analyze_transformation_arc(self) -> Dict:
        """Analyze Joseph's character transformation"""
        return {
            "trauma_to_advantage": {
                "betrayal": "teaches_trust_earned_not_assumed",
                "slavery": "identity_independent_of_status",
                "false_accusation": "compassion_for_innocent_wronged",
                "imprisonment": "patience_becomes_core_competency",
                "waiting_9_years": "trust_in_divine_timing"
            },
            "character_development": {
                "before": "naive_untested_favored_son",
                "after": "wise_compassionate_just_leader"
            },
            "integration_markers": [
                "can_speak_of_trauma",
                "no_emotional_flooding",
                "wisdom_applicable_to_others",
                "uses_experience_constructively",
                "relationships_restored",
                "can_forgive",
                "meaning_attributed",
                "transcendent_perspective"
            ]
        }

    def get_recovery_mechanisms(self) -> List[Dict]:
        """Get mechanisms enabling Joseph's recovery"""
        return [
            {
                "mechanism": "purpose_maintenance",
                "description": "vision_survives_trauma",
                "effect": "identity_independent_of_circumstance"
            },
            {
                "mechanism": "meaning_making",
                "description": "trauma_becomes_tool",
                "effect": "wisdom_extraction_from_suffering"
            },
            {
                "mechanism": "character_formation",
                "description": "tests_build_integrity",
                "effect": "competence_becomes_unshakeable"
            },
            {
                "mechanism": "gradual_integration",
                "description": "processing_over_time",
                "effect": "sustainable_recovery_not_suppression"
            },
            {
                "mechanism": "forgiveness_completion",
                "description": "genuine_not_suppression",
                "effect": "cycle_breaks_family_heals"
            }
        ]


class NoahStory(QuranicStory):
    """
    NUH (71:1-28) - Noah

    Long-term persistence, audience resistance, faith transcending outcome.
    Preaching for 950 years with minimal success demonstrates commitment.
    """

    def __init__(self):
        super().__init__(
            name="Noah (Nuh)",
            reference="Surah 71:1-28",
            duration_years=950
        )
        self.core_principles = [
            "long_term_commitment",
            "audience_habituation",
            "increasing_isolation",
            "outcome_independence"
        ]
        self.phases = [
            "initial_preaching_some_interest",
            "sustained_preaching_increasing_rejection",
            "long_term_persistence_mockery",
            "final_warning_hostility",
            "ark_construction_believers_embark",
            "flood_destruction_unbelievers"
        ]

    def extract_narrative_algorithm(self) -> Dict:
        """Extract Noah's narrative as algorithm"""
        return {
            "mission_parameters": {
                "duration_years": 950,
                "message": "believe_monotheism_abandon_idolatry",
                "audience_size": "entire_population",
                "believers_outcome": "300_approximately",
                "population_rejectors": "999700",
                "success_rate": "0.03_percent"
            },
            "persistence_mechanism": "divine_command",
            "persistence_basis": "obedience_transcends_calculation",
            "timeline_phases": {
                "year_1_100": "initial_preaching_some_interest",
                "year_100_500": "sustained_preaching_increasing_rejection",
                "year_500_900": "long_term_persistence_mockery",
                "year_900_950": "final_warning_hostility"
            },
            "outcome_metric": "outcome_independent_of_obedience"
        }

    def analyze_transformation_arc(self) -> Dict:
        """Analyze Noah's transformation"""
        return {
            "audience_progression": {
                "stage_1_early": "some_listen_curious",
                "stage_2_transition": "curiosity_fades",
                "stage_3_opposition": "active_hostility",
                "stage_4_mockery": "ridicule_contempt",
                "stage_5_refusal": "explicit_rejection"
            },
            "noah_response": "continue_preaching_all_stages",
            "psychological_challenge": {
                "isolation_increases": True,
                "rewards_absent": True,
                "opposition_grows": True,
                "success_impossible": True,
                "nevertheless_persists": True
            },
            "teaching": {
                "obedience_transcends_outcome": True,
                "duty_independent_of_success": True,
                "faith_means_continuing_impossible": True,
                "measure_by_effort_not_results": True
            }
        }

    def get_recovery_mechanisms(self) -> List[Dict]:
        """Get mechanisms enabling Noah's persistence"""
        return [
            {
                "mechanism": "divine_command",
                "description": "direct_instruction_from_god",
                "effect": "motivation_transcends_rational_calculation"
            },
            {
                "mechanism": "ark_construction",
                "description": "practical_preparation_alongside_preaching",
                "effect": "maintains_belief_despite_mockery"
            },
            {
                "mechanism": "community_formation",
                "description": "small_group_of_believers",
                "effect": "prevents_complete_isolation"
            },
            {
                "mechanism": "long_view",
                "description": "final_prayer_and_dua",
                "effect": "transcends_individual_lifetime"
            }
        ]


# ==================== ANALYSIS UTILITIES ====================

class MetaphorAnalyzer:
    """Utilities for analyzing metaphor systems"""

    def __init__(self):
        self.metaphors: Dict[str, QuranicMetaphor] = {}
        self.stories: Dict[str, QuranicStory] = {}
        self._initialize()

    def _initialize(self):
        """Initialize all metaphors and stories"""
        # Metaphors
        self.metaphors["bee"] = BeeMetaphor()
        self.metaphors["spider"] = SpiderMetaphor()
        self.metaphors["mountain"] = MountainMetaphor()
        self.metaphors["light"] = LightMetaphor()
        self.metaphors["palm_tree"] = PalmTreeMetaphor()

        # Stories
        self.stories["joseph"] = JosephStory()
        self.stories["noah"] = NoahStory()

    def analyze_metaphor(self, metaphor_name: str) -> Dict:
        """Comprehensive analysis of a metaphor"""
        if metaphor_name not in self.metaphors:
            return {"error": f"Metaphor {metaphor_name} not found"}

        m = self.metaphors[metaphor_name]
        return {
            "name": m.name,
            "reference": m.reference,
            "system_type": m.system_type.value if m.system_type else None,
            "algorithmic_structure": m.extract_algorithmic_structure(),
            "principles": m.get_principles_summary(),
            "fragility_index": m.fragility_index,
            "robustness": m.calculate_robustness(),
            "edge_cases": m.analyze_edge_cases(),
            "applications": m.get_applications()
        }

    def analyze_story(self, story_name: str) -> Dict:
        """Comprehensive analysis of a story"""
        if story_name not in self.stories:
            return {"error": f"Story {story_name} not found"}

        s = self.stories[story_name]
        return {
            "name": s.name,
            "reference": s.reference,
            "duration_years": s.duration_years,
            "core_principles": s.core_principles,
            "phases": s.phases,
            "narrative_algorithm": s.extract_narrative_algorithm(),
            "transformation_arc": s.analyze_transformation_arc(),
            "recovery_mechanisms": s.get_recovery_mechanisms()
        }

    def compare_metaphors(self, names: List[str]) -> Dict:
        """Compare multiple metaphors"""
        comparisons = {}
        for name in names:
            if name in self.metaphors:
                m = self.metaphors[name]
                comparisons[name] = {
                    "system_type": m.system_type.value if m.system_type else None,
                    "fragility": m.fragility_index,
                    "robustness": m.calculate_robustness(),
                    "principles": list(m.get_principles_summary().keys())
                }
        return comparisons

    def get_applications_by_domain(self, domain: str) -> Dict[str, List[str]]:
        """Get all applications in a domain"""
        results = {}
        for name, metaphor in self.metaphors.items():
            apps = metaphor.get_applications()
            for d, app in apps:
                if domain.lower() in d.lower():
                    if name not in results:
                        results[name] = []
                    results[name].append(app)
        return results


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    analyzer = MetaphorAnalyzer()

    print("=" * 80)
    print("QURANIC METAPHOR ANALYSIS")
    print("=" * 80)

    # Analyze each metaphor
    for metaphor_name in ["bee", "spider", "mountain", "light", "palm_tree"]:
        analysis = analyzer.analyze_metaphor(metaphor_name)
        print(f"\n{analysis['name']}")
        print(f"Reference: {analysis['reference']}")
        print(f"System Type: {analysis['system_type']}")
        print(f"Robustness: {analysis['robustness']:.2f}")
        print(f"Applications: {len(analysis['applications'])} domains")

    print("\n" + "=" * 80)
    print("QURANIC STORIES ANALYSIS")
    print("=" * 80)

    # Analyze each story
    for story_name in ["joseph", "noah"]:
        analysis = analyzer.analyze_story(story_name)
        print(f"\n{analysis['name']}")
        print(f"Reference: {analysis['reference']}")
        print(f"Duration: {analysis['duration_years']} years")
        print(f"Core Principles: {', '.join(analysis['core_principles'])}")
        print(f"Phases: {len(analysis['phases'])}")

    print("\n" + "=" * 80)
    print("COMPARISON: ROBUSTNESS RANKINGS")
    print("=" * 80)

    comparison = analyzer.compare_metaphors(["bee", "spider", "mountain", "light", "palm_tree"])
    sorted_comp = sorted(comparison.items(), key=lambda x: x[1]["robustness"], reverse=True)
    for name, data in sorted_comp:
        print(f"{name:20} | Robustness: {data['robustness']:.2f} | Fragility: {data['fragility']:.2f}")
