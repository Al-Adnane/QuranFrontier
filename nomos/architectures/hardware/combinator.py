"""Model Combinator - Wire Every Combination Possible.

Creates all possible model combinations:
- Sequential chaining
- Parallel ensembles
- Cross-domain fusion
- Recursive compositions
- Meta-architectures
"""

import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple, Any
from itertools import combinations, permutations


class SequentialChain(nn.Module):
    """Chain multiple models sequentially."""
    
    def __init__(self, models: List[nn.Module]):
        super().__init__()
        self.models = nn.ModuleList(models)
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Pass through all models in sequence."""
        outputs = [x]
        current = x
        
        for i, model in enumerate(self.models):
            try:
                out = model(current)
                if isinstance(out, dict):
                    current = out.get('output', out.get('hidden_states', current))
                else:
                    current = out
                outputs.append(current)
            except:
                outputs.append(current)
        
        return {
            'final': current,
            'all_outputs': outputs,
            'num_models': len(self.models)
        }


class ParallelEnsemble(nn.Module):
    """Run multiple models in parallel."""
    
    def __init__(self, models: List[nn.Module], fusion: str = 'mean'):
        super().__init__()
        self.models = nn.ModuleList(models)
        self.fusion = fusion
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Run all models in parallel and fuse."""
        outputs = []
        
        for model in self.models:
            try:
                out = model(x)
                if isinstance(out, dict):
                    out_tensor = out.get('output', out.get('hidden_states', x))
                    if isinstance(out_tensor, (dict, list)):
                        out_tensor = x
                    if isinstance(out_tensor, torch.Tensor):
                        outputs.append(out_tensor)
                    else:
                        outputs.append(x)
                elif isinstance(out, torch.Tensor):
                    outputs.append(out)
                else:
                    outputs.append(x)
            except:
                outputs.append(x)
        
        # Ensure all outputs are tensors with same shape
        target_shape = outputs[0].shape
        aligned_outputs = []
        for out in outputs:
            if not isinstance(out, torch.Tensor):
                out = x
            if out.shape != target_shape:
                try:
                    out = F.adaptive_avg_pool1d(out.transpose(1, 2), target_shape[-1]).transpose(1, 2)
                except:
                    out = x
            aligned_outputs.append(out)
        
        # Fuse outputs
        if self.fusion == 'mean':
            fused = torch.stack(aligned_outputs).mean(dim=0)
        elif self.fusion == 'max':
            fused = torch.stack(aligned_outputs).max(dim=0)[0]
        elif self.fusion == 'concat':
            fused = torch.cat(aligned_outputs, dim=-1)
        else:
            fused = aligned_outputs[0]
        
        return {
            'fused': fused,
            'individual': aligned_outputs,
            'num_models': len(self.models),
            'fusion_method': self.fusion
        }


class CrossDomainFusion(nn.Module):
    """Fuse models from different domains."""
    
    def __init__(
        self,
        domain_models: Dict[str, nn.Module],
        fusion_dim: int = 256
    ):
        super().__init__()
        self.domain_models = nn.ModuleDict(domain_models)
        
        # Domain-specific projections
        self.projections = nn.ModuleDict({
            name: nn.Linear(64, fusion_dim)
            for name in domain_models.keys()
        })
        
        # Cross-domain attention
        self.cross_attention = nn.MultiheadAttention(fusion_dim, num_heads=4)
        
        # Fusion output
        self.fusion_output = nn.Linear(fusion_dim * len(domain_models), fusion_dim)
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Process through all domains and fuse."""
        domain_outputs = {}
        
        for name, model in self.domain_models.items():
            try:
                out = model(x)
                if isinstance(out, dict):
                    out = out.get('output', out.get('hidden_states', x))
                domain_outputs[name] = self.projections[name](out)
            except:
                domain_outputs[name] = self.projections[name](x)
        
        # Cross-domain attention
        domain_keys = list(domain_outputs.keys())
        domain_tensors = torch.stack([domain_outputs[k] for k in domain_keys], dim=1)
        
        attended, _ = self.cross_attention(
            domain_tensors[:, 0:1],
            domain_tensors,
            domain_tensors
        )
        
        # Fuse all domains
        all_domains = torch.cat([domain_outputs[k] for k in domain_keys], dim=-1)
        fused = self.fusion_output(all_domains)
        
        return {
            'fused': fused,
            'attended': attended.squeeze(1),
            'domain_outputs': domain_outputs,
            'num_domains': len(domain_models)
        }


class RecursiveComposition(nn.Module):
    """Recursively compose models."""
    
    def __init__(self, base_model: nn.Module, depth: int = 3):
        super().__init__()
        self.base_model = base_model
        self.depth = depth
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Apply model recursively."""
        current = x
        all_states = [x]
        
        for _ in range(self.depth):
            try:
                out = self.base_model(current)
                if isinstance(out, dict):
                    current = out.get('output', out.get('hidden_states', current))
                else:
                    current = out
                all_states.append(current)
            except:
                break
        
        return {
            'final': current,
            'all_states': all_states,
            'depth': len(all_states),
            'max_depth': self.depth
        }


class MetaArchitecture(nn.Module):
    """Meta-architecture combining all combination strategies."""
    
    def __init__(
        self,
        models: List[nn.Module],
        combination_strategy: str = 'all'
    ):
        super().__init__()
        self.models = nn.ModuleList(models)
        self.combination_strategy = combination_strategy
        
        # Create all combination types
        if len(models) >= 2:
            self.sequential = SequentialChain(models[:min(3, len(models))])
            self.ensemble = ParallelEnsemble(models[:min(3, len(models))])
        
        # Meta-learner
        self.meta_learner = nn.Linear(64 * len(models), 64)
        
    def forward(self, x: torch.Tensor) -> Dict:
        """Apply meta-architecture."""
        all_outputs = []
        
        # Get outputs from all models
        for model in self.models:
            try:
                out = model(x)
                if isinstance(out, dict):
                    out_tensor = out.get('output', out.get('hidden_states', x))
                    if isinstance(out_tensor, dict):
                        out_tensor = x
                    all_outputs.append(out_tensor)
                else:
                    all_outputs.append(out)
            except:
                all_outputs.append(x)
        
        # Align shapes
        target_shape = all_outputs[0].shape
        aligned = []
        for out in all_outputs:
            if out.shape != target_shape:
                out = F.adaptive_avg_pool1d(out.transpose(1, 2), target_shape[-1]).transpose(1, 2)
            aligned.append(out)
        
        # Meta-learning fusion
        combined = torch.cat(aligned, dim=-1)
        meta_output = self.meta_learner(combined)
        
        return {
            'meta_output': meta_output,
            'individual_outputs': aligned,
            'num_models': len(self.models),
            'combination_strategy': self.combination_strategy
        }


def create_model_combination(
    models: List[nn.Module],
    combination_type: str = 'sequential'
) -> nn.Module:
    """Create model combination."""
    if combination_type == 'sequential':
        return SequentialChain(models)
    elif combination_type == 'parallel':
        return ParallelEnsemble(models)
    elif combination_type == 'cross_domain':
        domain_models = {f'model_{i}': m for i, m in enumerate(models)}
        return CrossDomainFusion(domain_models)
    elif combination_type == 'recursive':
        return RecursiveComposition(models[0])
    elif combination_type == 'meta':
        return MetaArchitecture(models)
    else:
        return SequentialChain(models)


def generate_all_combinations(
    models: List[nn.Module],
    max_size: int = 3
) -> List[nn.Module]:
    """Generate all possible model combinations."""
    all_combos = []
    
    # Sequential combinations
    for size in range(2, min(max_size + 1, len(models) + 1)):
        for combo in permutations(models, size):
            all_combos.append(SequentialChain(list(combo)))
    
    # Parallel combinations
    for size in range(2, min(max_size + 1, len(models) + 1)):
        for combo in combinations(models, size):
            all_combos.append(ParallelEnsemble(list(combo)))
    
    return all_combos
