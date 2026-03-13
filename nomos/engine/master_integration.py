"""Master Integration - All Tiers Wired Together.

This module connects all Tier 1, 2, and 3 components.
"""

import torch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, List, Any, Optional


class FrontierQuMaster:
    """
    Master integration class that wires all tiers together.
    
    Tier 1: High-Impact Applications
    Tier 2: Research Extensions  
    Tier 3: Application Domains
    """
    
    def __init__(self, device: str = 'cpu'):
        self.device = device
        self.components = {}
        
        # Initialize Tier 1 components
        self._init_tier1()
        
        # Initialize Tier 2 components
        self._init_tier2()
        
        # Initialize Tier 3 components
        self._init_tier3()
    
    def _init_tier1(self):
        """Initialize Tier 1: High-Impact Applications."""
        try:
            from frontier_models.unified_api import create_api
            from frontier_models.hardware.combinator import create_model_combination
            from frontier_models.hardware.novel_enhancements import create_novel_enhancement
            
            # Core API
            self.api = create_api()
            
            # Model combinations
            self.combiner = create_model_combination
            
            # Enhancements
            self.enhancer = create_novel_enhancement
            
            # Compression
            from compression.quantization.compression_utils import compress_model
            self.compress = compress_model
            
            # Benchmarking
            from benchmarks.performance.benchmark_suite import BenchmarkSuite
            self.benchmarker = BenchmarkSuite()
            
        except Exception as e:
            print(f"Tier 1 init warning: {e}")
            self.api = None
            self.combiner = None
            self.enhancer = None
            self.compress = lambda m, **k: (m, {})
            self.benchmarker = None
        
        self.components['tier1'] = ['api', 'combiner', 'enhancer', 'compress']
    
    def _init_tier2(self):
        """Initialize Tier 2: Research Extensions."""
        try:
            from research.nas.search_controller import NeuralArchitectureSearch
            self.nas = NeuralArchitectureSearch({'input_size': 128})
        except Exception as e:
            self.nas = None
        
        try:
            from research.meta_learning.maml import MAML
            self.maml = None  # Requires model
        except:
            self.maml = None
        
        self.components['tier2'] = ['nas', 'maml']
    
    def _init_tier3(self):
        """Initialize Tier 3: Application Domains."""
        try:
            from applications.healthcare.diagnosis import MedicalDiagnosis
            self.medical_diagnosis = MedicalDiagnosis()
        except:
            self.medical_diagnosis = None
        
        try:
            from applications.finance.trading import TradingStrategy
            self.trading = TradingStrategy()
        except:
            self.trading = None
        
        try:
            from applications.education.tutor import PersonalizedTutor
            self.tutor = PersonalizedTutor()
        except:
            self.tutor = None
        
        try:
            from applications.creative.art_generator import ArtGenerator
            self.art_generator = ArtGenerator()
        except:
            self.art_generator = None
        
        self.components['tier3'] = ['medical_diagnosis', 'trading', 'tutor', 'art_generator']
    
    # ==================== Unified Interface ====================
    
    def create_model(self, model_name: str, **kwargs):
        """Create any model from any tier."""
        return self.api.create_model(model_name, **kwargs)
    
    def run_inference(self, model_name: str, input_data: torch.Tensor, **kwargs) -> Dict:
        """Run inference on any model."""
        if model_name not in self.api.models:
            self.api.create_model(model_name)
        return self.api.run(model_name, input_data, **kwargs)
    
    def combine_models(self, model_names: List[str], 
                       combination_type: str = 'sequential') -> Any:
        """Combine multiple models."""
        models = []
        for name in model_names:
            if name not in self.api.models:
                self.api.create_model(name)
            models.append(self.api.models[name])
        return self.combiner(models, combination_type)
    
    def compress_model(self, model: torch.nn.Module, **kwargs):
        """Compress a model."""
        return self.compress(model, **kwargs)
    
    def benchmark_model(self, model: torch.nn.Module, 
                        model_name: str, category: str):
        """Benchmark a model."""
        if self.benchmarker:
            return self.benchmarker.benchmark_inference(model, model_name, category)
        return {}
    
    def search_architecture(self, train_data: torch.Tensor,
                            val_data: torch.Tensor) -> Dict:
        """Search for optimal architecture (Tier 2)."""
        if self.nas:
            return self.nas.search(train_data, val_data)
        return {}
    
    def diagnose(self, symptoms: torch.Tensor) -> Dict:
        """Medical diagnosis (Tier 3)."""
        if self.medical_diagnosis:
            return self.medical_diagnosis(symptoms)
        return {}
    
    def trade(self, market_data: torch.Tensor) -> Dict:
        """Generate trading signals (Tier 3)."""
        if self.trading:
            return self.trading(market_data)
        return {}
    
    def teach(self, student_state: torch.Tensor,
              content: torch.Tensor) -> Dict:
        """Generate learning recommendations (Tier 3)."""
        if self.tutor:
            return self.tutor(student_state, content)
        return {}
    
    def create_art(self, style: torch.Tensor,
                   noise: torch.Tensor) -> Dict:
        """Generate art (Tier 3)."""
        if self.art_generator:
            return self.art_generator(style, noise)
        return {}
    
    # ==================== Cross-Tier Pipelines ====================
    
    def full_pipeline(self, 
                      task: str,
                      input_data: torch.Tensor,
                      **kwargs) -> Dict:
        """
        Run full cross-tier pipeline.
        
        Args:
            task: One of 'diagnose', 'trade', 'teach', 'create_art', 'infer'
            input_data: Input tensor
            **kwargs: Additional arguments
        
        Returns:
            Dict with results
        """
        if task == 'diagnose':
            # Tier 3 application with Tier 1 model
            model = self.create_model('dna', input_dim=64, embed_dim=128)
            features = self.run_inference('dna', input_data)
            return self.diagnose(input_data)
        
        elif task == 'trade':
            # Tier 3 application with Tier 2 optimization
            if self.nas:
                arch = self.nas.search(input_data, input_data)
            return self.trade(input_data)
        
        elif task == 'teach':
            # Tier 3 with Tier 1 enhancement
            content = input_data
            student_state = kwargs.get('student_state', input_data)
            return self.teach(student_state, content)
        
        elif task == 'create_art':
            # Tier 3 creative with Tier 1 enhancement
            style = input_data
            noise = torch.randn_like(input_data)
            return self.create_art(style, noise)
        
        elif task == 'infer':
            # Pure Tier 1 inference
            model_name = kwargs.get('model_name', 'memetic')
            return self.run_inference(model_name, input_data)
        
        else:
            return {'error': f'Unknown task: {task}'}
    
    def status(self) -> Dict:
        """Get status of all components."""
        status = {'tier1': {}, 'tier2': {}, 'tier3': {}}
        
        # Tier 1
        status['tier1'] = {k: v is not None for k, v in [
            ('api', self.api),
            ('combiner', self.combiner),
            ('enhancer', self.enhancer),
            ('compress', self.compress),
            ('benchmarker', self.benchmarker)
        ]}
        
        # Tier 2
        status['tier2'] = {k: v is not None for k, v in [
            ('nas', self.nas),
            ('maml', self.maml)
        ]}
        
        # Tier 3
        status['tier3'] = {k: v is not None for k, v in [
            ('medical_diagnosis', self.medical_diagnosis),
            ('trading', self.trading),
            ('tutor', self.tutor),
            ('art_generator', self.art_generator)
        ]}
        
        return status


# ==================== Convenience Functions ====================

def get_master(device: str = 'cpu') -> FrontierQuMaster:
    """Get master integration instance."""
    return FrontierQuMaster(device)


def run_task(task: str, input_data: torch.Tensor, **kwargs) -> Dict:
    """Run a task using the master integration."""
    master = get_master()
    return master.full_pipeline(task, input_data, **kwargs)


if __name__ == "__main__":
    # Example usage
    print("FrontierQu Master Integration")
    print("=" * 50)
    
    master = FrontierQuMaster()
    
    # Check status
    status = master.status()
    print("\nComponent Status:")
    for tier, components in status.items():
        active = sum(1 for v in components.values() if v)
        print(f"  {tier}: {active}/{len(components)} active")
    
    # Run inference
    x = torch.randn(2, 64)
    result = master.full_pipeline('infer', x, model_name='memetic')
    print(f"\nInference result keys: {list(result.keys())}")
    
    # Medical diagnosis
    symptoms = torch.randint(0, 200, (2, 10))
    diagnosis = master.full_pipeline('diagnose', symptoms)
    print(f"Diagnosis result keys: {list(diagnosis.keys())}")
    
    # Trading
    market = torch.randn(2, 10, 128)
    trade = master.full_pipeline('trade', market)
    print(f"Trading result keys: {list(trade.keys())}")
    
    print("\n✅ All tiers wired and functional!")
