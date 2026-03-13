"""Spiritual Tradition Neural Network Models - 21 architectures."""

__version__ = "4.0.0"

from .p_adic_network import PAdicNeuralNetwork, create_p_adic_network
from .catuskoti_network import CatuskotiNetwork, create_catuskoti_network
from .sufi_imaginal_network import SufiImaginalNetwork, create_sufi_imaginal_network
from .analects_network import AnalectsNetwork, create_analects_network
from .bon_soul_retrieval_network import BonSoulRetrievalNetwork, create_bon_soul_retrieval_network
from .conceptual_blending import ConceptualBlendingNetwork, create_conceptual_blending_network
from .gnostic_aeons_network import GnosticAeonsNetwork, create_gnostic_aeons_network
from .hermetic_correspondence_network import HermeticCorrespondenceNetwork, create_hermetic_correspondence_network
from .i_ching_network import IChingNetwork, create_i_ching_network
from .ifa_divination_network import IfaDivinationNetwork, create_ifa_divination_network
from .iit_network import IntegratedInformationNetwork, create_iit_network
from .jain_seven_valued_network import JainSevenValuedNetwork, create_jain_seven_valued_network
from .kabbalah_sefirot_network import KabbalahSefirotNetwork, create_kabbalah_sefirot_network
from .nahuatl_theater_network import NahuatlTheaterNetwork, create_nahuatl_theater_network
from .polynesian_wayfinding_network import PolynesianWayfindingNetwork, create_polynesian_wayfinding_network
from .predictive_coding import PredictiveCodingNetwork, create_predictive_coding_network
from .shinto_musubi_network import ShintoMusubiNetwork, create_shinto_musubi_network
from .stoic_lekta_network import StoicLektaNetwork, create_stoic_lekta_network
from .vedic_network import VedicNetwork, create_vedic_network
from .yogasutra_network import YogasutraNetwork, create_yogasutra_network
from .zoroastrian_dualism_network import ZoroastrianDualismNetwork, create_zoroastrian_dualism_network

__all__ = [
    'PAdicNeuralNetwork', 'create_p_adic_network',
    'CatuskotiNetwork', 'create_catuskoti_network',
    'SufiImaginalNetwork', 'create_sufi_imaginal_network',
    'AnalectsNetwork', 'create_analects_network',
    'BonSoulRetrievalNetwork', 'create_bon_soul_retrieval_network',
    'ConceptualBlendingNetwork', 'create_conceptual_blending_network',
    'GnosticAeonsNetwork', 'create_gnostic_aeons_network',
    'HermeticCorrespondenceNetwork', 'create_hermetic_correspondence_network',
    'IChingNetwork', 'create_i_ching_network',
    'IfaDivinationNetwork', 'create_ifa_divination_network',
    'IntegratedInformationNetwork', 'create_iit_network',
    'JainSevenValuedNetwork', 'create_jain_seven_valued_network',
    'KabbalahSefirotNetwork', 'create_kabbalah_sefirot_network',
    'NahuatlTheaterNetwork', 'create_nahuatl_theater_network',
    'PolynesianWayfindingNetwork', 'create_polynesian_wayfinding_network',
    'PredictiveCodingNetwork', 'create_predictive_coding_network',
    'ShintoMusubiNetwork', 'create_shinto_musubi_network',
    'StoicLektaNetwork', 'create_stoic_lekta_network',
    'VedicNetwork', 'create_vedic_network',
    'YogasutraNetwork', 'create_yogasutra_network',
    'ZoroastrianDualismNetwork', 'create_zoroastrian_dualism_network',
]
