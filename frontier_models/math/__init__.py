"""Mathematics Models - Complete Collection."""

__version__ = "1.0.0"

from .graph_theory import GraphTheoryNetwork, create_graph_theory_network
from .topology import TopologyNetwork, create_topology_network
from .number_theory import NumberTheoryNetwork, create_number_theory_network
from .calculus import CalculusNetwork, create_calculus_network
from .network_science import NetworkScienceNetwork, create_network_science_network

__all__ = [
    'GraphTheoryNetwork', 'create_graph_theory_network',
    'TopologyNetwork', 'create_topology_network',
    'NumberTheoryNetwork', 'create_number_theory_network',
    'CalculusNetwork', 'create_calculus_network',
    'NetworkScienceNetwork', 'create_network_science_network',
]
