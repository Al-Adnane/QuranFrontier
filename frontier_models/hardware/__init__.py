"""Hardware Integration - Complete Collection."""

__version__ = "1.0.0"

from .backends import (
    QuantumHardwareBackend,
    NeuromorphicBackend,
    OpticalComputingBackend,
    FPGAAccelerator,
    HardwareRouter,
    create_hardware_backend
)

from .combinator import (
    SequentialChain,
    ParallelEnsemble,
    CrossDomainFusion,
    RecursiveComposition,
    MetaArchitecture,
    create_model_combination,
    generate_all_combinations
)

__all__ = [
    # Hardware Backends
    'QuantumHardwareBackend',
    'NeuromorphicBackend',
    'OpticalComputingBackend',
    'FPGAAccelerator',
    'HardwareRouter',
    'create_hardware_backend',
    
    # Model Combinations
    'SequentialChain',
    'ParallelEnsemble',
    'CrossDomainFusion',
    'RecursiveComposition',
    'MetaArchitecture',
    'create_model_combination',
    'generate_all_combinations',
]
