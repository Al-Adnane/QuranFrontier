"""FrontierQu Frontier Models - Cutting Edge Research Architectures."""

__version__ = "3.0.0"

# Core rigorous architectures only
from .p_adic_network import PAdicNeuralNetwork, create_p_adic_network
from .catuskoti_network import CatuskotiNetwork, create_catuskoti_network
from .sufi_imaginal_network import SufiImaginalNetwork, create_sufi_imaginal_network

__all__ = [
    # 3 rigorous spiritual tradition models (archival of toy models complete)
    'PAdicNeuralNetwork', 'create_p_adic_network',
    'CatuskotiNetwork', 'create_catuskoti_network',
    'SufiImaginalNetwork', 'create_sufi_imaginal_network',
]
