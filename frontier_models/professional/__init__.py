"""Professional Models - Complete Collection."""

__version__ = "1.0.0"

from .legal import LegalReasoningNetwork, create_legal_reasoning_network
from .education import EducationPedagogyNetwork, create_education_pedagogy_network
from .business import BusinessStrategyNetwork, create_business_strategy_network
from .marketing import MarketingNetwork, create_marketing_network
from .urban_planning import UrbanPlanningNetwork, create_urban_planning_network

__all__ = [
    'LegalReasoningNetwork', 'create_legal_reasoning_network',
    'EducationPedagogyNetwork', 'create_education_pedagogy_network',
    'BusinessStrategyNetwork', 'create_business_strategy_network',
    'MarketingNetwork', 'create_marketing_network',
    'UrbanPlanningNetwork', 'create_urban_planning_network',
]
