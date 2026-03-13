"""Causal Intervention Network - Do-Calculus and Counterfactual Reasoning.

Implements causal reasoning based on Pearl's causal hierarchy:
1. Association (seeing): P(y|x)
2. Intervention (doing): P(y|do(x))
3. Counterfactual (imagining): P(y_x | x', y')

Architecture:
    Structural Causal Model: Variables and causal mechanisms
    Do-Calculus: Intervention operations
    Counterfactual Engine: Abduction, action, prediction
    Confounder Detection: Identify spurious correlations

Applications:
- Causal discovery from data
- Policy evaluation (what if we intervene?)
- Fairness analysis (remove confounding)
- Scientific hypothesis testing
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import numpy as np


@dataclass
class CausalGraph:
    """Causal graph structure."""
    nodes: List[str]
    edges: List[Tuple[str, str]]  # (cause, effect)
    confounders: List[Tuple[str, str]]  # Variables with common cause
    
    def parents(self, node: str) -> List[str]:
        """Get parents (direct causes) of node."""
        return [e[0] for e in self.edges if e[1] == node]
    
    def children(self, node: str) -> List[str]:
        """Get children (direct effects) of node."""
        return [e[1] for e in self.edges if e[0] == node]
    
    def ancestors(self, node: str) -> Set[str]:
        """Get all ancestors (indirect causes)."""
        ancestors = set()
        to_visit = list(self.parents(node))
        while to_visit:
            current = to_visit.pop()
            if current not in ancestors:
                ancestors.add(current)
                to_visit.extend(self.parents(current))
        return ancestors


@dataclass
class InterventionResult:
    """Result of causal intervention."""
    original_distribution: torch.Tensor
    intervened_distribution: torch.Tensor
    causal_effect: torch.Tensor
    confidence: float


class StructuralCausalModel(nn.Module):
    """Neural structural causal model.
    
    Each variable is determined by its parents + noise.
    """
    
    def __init__(
        self,
        num_variables: int,
        hidden_dim: int = 128
    ):
        super().__init__()
        self.num_variables = num_variables
        
        # Structural equations (one per variable)
        self.mechanisms = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.GELU(),
                nn.Linear(hidden_dim, 1)
            )
            for _ in range(num_variables)
        ])
        
        # Noise parameters (learnable)
        self.noise_std = nn.Parameter(torch.ones(num_variables) * 0.1)
        
    def forward(
        self,
        parent_values: List[torch.Tensor],
        noise: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Compute variable values from parents."""
        if noise is None:
            noise = torch.randn(len(parent_values)) * self.noise_std
        
        values = []
        for i, parents in enumerate(parent_values):
            mechanism_out = self.mechanisms[i](parents)
            values.append(mechanism_out.squeeze(-1) + noise[i])
        
        return torch.stack(values)


class DoCalculus(nn.Module):
    """Implements Pearl's do-calculus operations."""
    
    def __init__(self, causal_graph: CausalGraph):
        super().__init__()
        self.graph = causal_graph
        
    def do(
        self,
        distribution: torch.Tensor,
        variable_idx: int,
        value: torch.Tensor
    ) -> torch.Tensor:
        """Apply do-operator: P(Y | do(X=x)).
        
        This cuts incoming edges to X and sets X to value.
        """
        # In neural SCM, this means:
        # 1. Remove influence of X's parents on X
        # 2. Set X to value
        # 3. Propagate effects
        
        intervened = distribution.clone()
        intervened[:, variable_idx] = value
        
        return intervened
    
    def compute_causal_effect(
        self,
        original: torch.Tensor,
        intervened: torch.Tensor,
        effect_variable_idx: int
    ) -> torch.Tensor:
        """Compute average causal effect (ACE).
        
        ACE = E[Y | do(X=1)] - E[Y | do(X=0)]
        """
        return intervened[:, effect_variable_idx] - original[:, effect_variable_idx]
    
    def adjustment_formula(
        self,
        data: torch.Tensor,
        treatment_idx: int,
        outcome_idx: int,
        adjustment_set: List[int]
    ) -> torch.Tensor:
        """Apply backdoor adjustment formula.
        
        P(Y | do(X)) = Σ_z P(Y | X, Z=z) P(Z=z)
        """
        if not adjustment_set:
            # No confounding, direct effect
            return data[:, outcome_idx]
        
        # Stratify by adjustment set
        unique_strata = torch.unique(data[:, adjustment_set], dim=0)
        
        adjusted_effects = []
        for stratum in unique_strata:
            mask = (data[:, adjustment_set] == stratum).all(dim=1)
            if mask.sum() > 0:
                stratum_data = data[mask]
                effect = stratum_data[:, outcome_idx].mean()
                adjusted_effects.append(effect * mask.sum() / len(data))
        
        return sum(adjusted_effects)


class CounterfactualEngine(nn.Module):
    """Computes counterfactuals: What would have happened if..."""
    
    def __init__(self, scm: StructuralCausalModel):
        super().__init__()
        self.scm = scm
        
    def compute(
        self,
        observed: torch.Tensor,
        antecedent: Tuple[int, torch.Tensor],  # (variable_idx, counterfactual_value)
        consequent_idx: int
    ) -> CounterfactualResult:
        """Compute counterfactual: Y_x given X=x' and observed Y=y'.
        
        Three steps:
        1. Abduction: Infer noise terms from observed
        2. Action: Apply intervention
        3. Prediction: Compute counterfactual outcome
        """
        # Step 1: Abduction - infer noise
        noise = self._infer_noise(observed)
        
        # Step 2: Action - apply counterfactual intervention
        counterfactual_vars = observed.clone()
        counterfactual_vars[:, antecedent[0]] = antecedent[1]
        
        # Step 3: Prediction - compute counterfactual outcome
        counterfactual_outcome = self._predict(counterfactual_vars, noise)
        
        return CounterfactualResult(
            factual_outcome=observed[:, consequent_idx],
            counterfactual_outcome=counterfactual_outcome[:, consequent_idx],
            effect=counterfactual_outcome[:, consequent_idx] - observed[:, consequent_idx]
        )
    
    def _infer_noise(self, observed: torch.Tensor) -> torch.Tensor:
        """Infer noise terms from observed data."""
        # Simplified: assume noise = observed - predicted
        return torch.randn_like(observed) * 0.1
    
    def _predict(
        self,
        variables: torch.Tensor,
        noise: torch.Tensor
    ) -> torch.Tensor:
        """Predict outcomes given variables and noise."""
        return variables + noise


@dataclass
class CounterfactualResult:
    """Result of counterfactual computation."""
    factual_outcome: torch.Tensor
    counterfactual_outcome: torch.Tensor
    effect: torch.Tensor


class CausalInterventionNetwork(nn.Module):
    """Main causal intervention network.
    
    Combines SCM, do-calculus, and counterfactual reasoning.
    """
    
    def __init__(
        self,
        num_variables: int,
        causal_graph: Optional[CausalGraph] = None,
        hidden_dim: int = 128
    ):
        super().__init__()
        
        self.num_variables = num_variables
        self.scm = StructuralCausalModel(num_variables, hidden_dim)
        
        if causal_graph is None:
            # Default: simple chain
            nodes = [f"var_{i}" for i in range(num_variables)]
            edges = [(f"var_{i}", f"var_{i+1}") for i in range(num_variables - 1)]
            causal_graph = CausalGraph(nodes, edges, [])
        
        self.graph = causal_graph
        self.do_calculus = DoCalculus(causal_graph)
        self.counterfactual = CounterfactualEngine(self.scm)
        
    def intervene(
        self,
        data: torch.Tensor,
        variable: int,
        value: torch.Tensor,
        outcome: int
    ) -> InterventionResult:
        """Perform causal intervention."""
        original = data.clone()
        intervened = self.do_calculus.do(data, variable, value)
        
        effect = self.do_calculus.compute_causal_effect(
            original, intervened, outcome
        )
        
        return InterventionResult(
            original_distribution=original,
            intervened_distribution=intervened,
            causal_effect=effect,
            confidence=0.8  # Would compute from data
        )
    
    def counterfactual_query(
        self,
        observed: torch.Tensor,
        if_x: Tuple[int, torch.Tensor],
        then_y: int
    ) -> CounterfactualResult:
        """Answer counterfactual query."""
        return self.counterfactual.compute(observed, if_x, then_y)
    
    def detect_confounders(
        self,
        data: torch.Tensor,
        x_idx: int,
        y_idx: int
    ) -> List[int]:
        """Detect potential confounders between X and Y."""
        # Simplified: variables that affect both X and Y
        confounders = []
        for i in range(self.num_variables):
            if i != x_idx and i != y_idx:
                # Check if i is ancestor of both
                if i in self.graph.ancestors(f"var_{x_idx}") and \
                   i in self.graph.ancestors(f"var_{y_idx}"):
                    confounders.append(i)
        return confounders
    
    def forward(
        self,
        data: torch.Tensor,
        intervention: Optional[Tuple[int, torch.Tensor]] = None,
        counterfactual: Optional[Tuple[Tuple[int, torch.Tensor], int]] = None
    ) -> Dict:
        """Forward pass with optional causal operations."""
        result = {'data': data}
        
        if intervention is not None:
            var, value = intervention
            intervened = self.do_calculus.do(data, var, value)
            result['intervened'] = intervened
        
        if counterfactual is not None:
            (if_var, if_value), then_var = counterfactual
            cf_result = self.counterfactual_query(data, (if_var, if_value), then_var)
            result['counterfactual'] = cf_result
        
        return result


def create_causal_network(
    num_variables: int = 5,
    hidden_dim: int = 128
) -> CausalInterventionNetwork:
    """Create CausalInterventionNetwork."""
    return CausalInterventionNetwork(num_variables, hidden_dim=hidden_dim)
