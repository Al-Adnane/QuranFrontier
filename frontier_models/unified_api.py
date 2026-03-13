"""FrontierQu Unified API - Combining All Models.

This API provides unified access to:
- frontier_models (181+ new architectures)
- frontier_neuro_symbolic (original components)
- Hardware backends
- Model combinations
"""

import torch
from typing import Dict, List, Optional, Any, Union

# Import all frontier_models
from frontier_models.wild import *
from frontier_models.frontier import *
from frontier_models.physics import *
from frontier_models.bio import *
from frontier_models.chem import *
from frontier_models.math import *
from frontier_models.art import *
from frontier_models.psychology import *
from frontier_models.divination import *
from frontier_models.energy import *
from frontier_models.hardware import *
from frontier_models.tech import *
from frontier_models.transport import *
from frontier_models.agri import *
from frontier_models.emerging import *
from frontier_models.professional import *
from frontier_models.cultural import *
from frontier_models.natural import *
from frontier_models.film import *
from frontier_models.lit import *
from frontier_models.social import *
from frontier_models.econ import *
from frontier_models.lingua import *
from frontier_models.anthropology import *
from frontier_models.alchemy import *
from frontier_models.military import *
from frontier_models.mythology import *
from frontier_models.music_sport import *
from frontier_models.architecture import *
from frontier_models.eco import *
from frontier_models.med import *
from frontier_models.hardware.combinator import (
    SequentialChain,
    ParallelEnsemble,
    CrossDomainFusion,
    RecursiveComposition,
    MetaArchitecture,
    create_model_combination,
    generate_all_combinations
)
from frontier_models.hardware.novel_enhancements import (
    QuantumClassicalHybrid,
    ConsciousnessAttention,
    MythologicalPatternRecognition,
    SacredGeometryConstraint,
    AlchemicalTransformation,
    create_novel_enhancement
)


class FrontierQuAPI:
    """Unified API for all FrontierQu models."""
    
    def __init__(self, device: str = 'cpu'):
        self.device = device
        self.models: Dict[str, Any] = {}
        self.hardware_backends: Dict[str, Any] = {}
        
    # ==================== Model Creation ====================
    
    def create_model(self, model_name: str, **kwargs) -> Any:
        """Create any model by name."""
        # Wild models
        wild_creators = {
            'memetic': create_memetic_network,
            'holographic': create_holographic_memory,
            'consciousness': create_consciousness_network,
            'dream': create_dream_network,
            'fractal': create_fractal_network,
            'neuromorphic': create_neuromorphic_spiking,
            'diffusion': create_diffusion_model,
        }
        
        # Frontier models
        frontier_creators = {
            'vedic': create_vedic_network,
            'yogasutra': create_yogasutra_network,
            'i_ching': create_i_ching_network,
            'sufi': create_sufi_imaginal_network,
            'kabbalah': create_kabbalah_sefirot_network,
            'jain': create_jain_seven_valued_network,
            'tarot': create_tarot_network,
            'astrology': create_astrology_network,
        }
        
        # Science models
        science_creators = {
            'dna': create_dna_network,
            'evolution': create_evolution_network,
            'immune': create_immune_network,
            'quantum_field': create_quantum_field_network,
            'molecular': create_molecular_network,
            'graph_theory': create_graph_theory_network,
        }
        
        # Tech models
        tech_creators = {
            'quantum_computing': create_quantum_computing_network,
            'blockchain': create_blockchain_network,
            'robotics': create_robotics_network,
            'cybersecurity': create_cybersecurity_network,
        }
        
        # Combine all creators
        all_creators = {
            **wild_creators,
            **frontier_creators,
            **science_creators,
            **tech_creators,
        }
        
        if model_name not in all_creators:
            available = list(all_creators.keys())
            raise ValueError(f"Unknown model: {model_name}. Available: {available}")
        
        model = all_creators[model_name](**kwargs)
        model = model.to(self.device)
        self.models[model_name] = model
        
        return model
    
    # ==================== Hardware Backends ====================
    
    def create_hardware(self, backend_type: str, **kwargs) -> Any:
        """Create hardware backend."""
        backend = create_hardware_backend(backend_type, **kwargs)
        self.hardware_backends[backend_type] = backend
        return backend
    
    # ==================== Model Combinations ====================
    
    def combine_models(
        self,
        models: List[Any],
        combination_type: str = 'sequential'
    ) -> Any:
        """Combine multiple models."""
        return create_model_combination(models, combination_type)
    
    # ==================== Novel Enhancements ====================
    
    def add_enhancement(
        self,
        enhancement_type: str,
        embed_dim: int,
        **kwargs
    ) -> Any:
        """Add novel enhancement to model."""
        return create_novel_enhancement(enhancement_type, embed_dim, **kwargs)
    
    # ==================== Inference ====================
    
    def run(
        self,
        model_name: str,
        input_data: torch.Tensor,
        **kwargs
    ) -> Dict:
        """Run inference on a model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not created. Use create_model first.")
        
        model = self.models[model_name]
        input_data = input_data.to(self.device)
        model.eval()
        
        with torch.no_grad():
            output = model(input_data, **kwargs)
        
        return output
    
    # ==================== Batch Processing ====================
    
    def run_batch(
        self,
        model_name: str,
        inputs: List[torch.Tensor],
        **kwargs
    ) -> List[Dict]:
        """Run batch inference."""
        results = []
        for input_data in inputs:
            result = self.run(model_name, input_data, **kwargs)
            results.append(result)
        return results
    
    # ==================== Model Info ====================
    
    def list_models(self) -> Dict[str, List[str]]:
        """List all available models by category."""
        return {
            'wild': list(create_memetic_network.__module__.split('.')),
            'frontier': ['vedic', 'yogasutra', 'i_ching', 'sufi', 'kabbalah', 'jain'],
            'science': ['dna', 'evolution', 'immune', 'quantum_field'],
            'tech': ['quantum_computing', 'blockchain', 'robotics'],
            'hardware': ['quantum', 'neuromorphic', 'optical', 'fpga'],
            'enhancements': ['quantum_hybrid', 'consciousness', 'mythological', 'sacred_geometry', 'alchemical'],
            'combinations': ['sequential', 'parallel', 'cross_domain', 'recursive', 'meta'],
        }
    
    # ==================== Export/Import ====================
    
    def save_model(self, model_name: str, path: str) -> None:
        """Save model to disk."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        torch.save(self.models[model_name].state_dict(), path)
    
    def load_model(self, model_name: str, path: str, **kwargs) -> Any:
        """Load model from disk."""
        model = self.create_model(model_name, **kwargs)
        model.load_state_dict(torch.load(path, map_location=self.device))
        return model


# Convenience function
def create_api(device: str = 'cpu') -> FrontierQuAPI:
    """Create FrontierQu API instance."""
    return FrontierQuAPI(device)


# Example usage
if __name__ == '__main__':
    # Create API
    api = create_api()
    
    # List available models
    print("Available models:", api.list_models())
    
    # Create a model
    model = api.create_model('memetic', input_dim=128, embed_dim=256)
    
    # Run inference
    x = torch.randn(2, 128)
    output = api.run('memetic', x)
    print("Output keys:", output.keys())
    
    # Create hardware backend
    quantum = api.create_hardware('quantum')
    
    # Combine models
    model2 = api.create_model('dream', input_dim=128, embed_dim=256)
    combined = api.combine_models([model, model2], 'parallel')
    
    # Add enhancement
    enhancement = api.add_enhancement('consciousness', embed_dim=256)
    
    print("FrontierQu API ready!")
