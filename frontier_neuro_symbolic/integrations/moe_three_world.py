"""MoE Three-World Router — Sparse Gating for Neural/Symbolic/Categorical Worlds.

Routes incoming queries to the most appropriate world(s) in the Three-World
Architecture using a Mixture-of-Experts sparse top-2 gating network.

Each "expert" is one of the three worlds:
  - Expert 0: Neural layer  (transformer embeddings)
  - Expert 1: Symbolic layer (deontic + temporal logic, Z3 constraints)
  - Expert 2: Categorical layer (sheaf semantics, Heyting algebra, infinity-topos)

The gating network learns which queries are best served by which world(s),
with an auxiliary load-balancing loss to prevent routing collapse.

Cross-subsystem integration:
  frontier_models/wild/mixture_of_experts.py  (GatingNetwork, MoEOutput)
  frontier_neuro_symbolic/three_world/        (NeuralLayer, SymbolicLayer, CategoricalLayer, ThreeWorldArchitecture)
"""

import sys
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _project_root)

from frontier_models.wild.mixture_of_experts import (
    GatingNetwork,
    ExpertNetwork,
    MoEOutput,
)
try:
    from frontier_neuro_symbolic.three_world.neural_layer import NeuralLayer
    from frontier_neuro_symbolic.three_world.symbolic_layer import SymbolicLayer
    from frontier_neuro_symbolic.three_world.categorical_layer import CategoricalLayer
    _HAS_THREE_WORLD = True
except ImportError:
    _HAS_THREE_WORLD = False
    NeuralLayer = None
    SymbolicLayer = None
    CategoricalLayer = None


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class WorldRoutingResult:
    """Result of routing a query through the MoE Three-World system."""
    query_embedding: torch.Tensor
    routed_output: torch.Tensor
    selected_worlds: List[int]          # Indices of top-2 selected worlds
    world_weights: Dict[str, float]     # {neural, symbolic, categorical} weights
    load_balancing_loss: float
    world_outputs: Dict[str, Any]       # Raw output from each selected world


WORLD_NAMES = {0: "neural", 1: "symbolic", 2: "categorical"}


# ---------------------------------------------------------------------------
# Main integration class
# ---------------------------------------------------------------------------

class MoEThreeWorldRouter(nn.Module):
    """Mixture-of-Experts router for the Three-World Architecture.

    Architecture:
        1. Input query is projected to a shared embedding space.
        2. GatingNetwork from MoE subsystem computes top-2 sparse weights
           over 3 experts (worlds).
        3. Selected worlds process the query in parallel.
        4. Outputs are combined using the gating weights.
        5. Load-balancing loss encourages uniform world utilization.

    The router wraps each world as an "expert" — the neural world processes
    via transformer forward pass, the symbolic world via constraint checking,
    and the categorical world via sheaf/topos verification.
    """

    def __init__(
        self,
        input_dim: int = 128,
        hidden_dim: int = 256,
        embedding_dim: int = 128,
        vocab_size: int = 1000,
        num_heads: int = 4,
        num_layers: int = 2,
        top_k: int = 2,
        load_loss_weight: float = 0.01,
    ):
        """Initialize MoE Three-World Router.

        Args:
            input_dim: Dimension of input query vectors.
            hidden_dim: Hidden dimension for expert projection networks.
            embedding_dim: Embedding dimension for neural layer.
            vocab_size: Vocabulary size for neural layer tokenizer.
            num_heads: Number of attention heads in neural layer.
            num_layers: Number of transformer layers.
            top_k: Number of worlds to route to (default 2).
            load_loss_weight: Weight for auxiliary load-balancing loss.
        """
        super().__init__()

        self.input_dim = input_dim
        self.top_k = top_k
        self.load_loss_weight = load_loss_weight
        self.num_worlds = 3

        # --- MoE Gating Network (from frontier_models/wild/mixture_of_experts.py) ---
        self.gate = GatingNetwork(
            input_dim=input_dim,
            num_experts=self.num_worlds,
            top_k=top_k,
            noise_epsilon=1e-2,
        )

        # --- Three Worlds (fallback to stubs if Z3/deps missing) ---
        if _HAS_THREE_WORLD and NeuralLayer is not None:
            self.neural_layer = NeuralLayer(
                vocab_size=vocab_size,
                embedding_dim=embedding_dim,
                num_heads=num_heads,
                num_layers=num_layers,
            )
            self.symbolic_layer = SymbolicLayer()
            self.categorical_layer = CategoricalLayer()
        else:
            # Lightweight fallback: use simple linear projections as stand-ins
            self.neural_layer = nn.Sequential(
                nn.Linear(embedding_dim, hidden_dim), nn.GELU(), nn.Linear(hidden_dim, embedding_dim)
            )
            self.symbolic_layer = None
            self.categorical_layer = None

        # --- Expert projection heads (project world outputs to shared space) ---
        # Neural world: takes (seq_len, embedding_dim) -> mean-pool -> (input_dim,)
        self.neural_proj = nn.Linear(embedding_dim, input_dim)

        # Symbolic world: produces a scalar confidence -> project to input_dim
        self.symbolic_proj = nn.Linear(1, input_dim)

        # Categorical world: produces a scalar truth value -> project to input_dim
        self.categorical_proj = nn.Linear(1, input_dim)

        # Output combination layer
        self.output_head = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, input_dim),
        )

    def forward(
        self,
        query: torch.Tensor,
        text: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        interpretation: Optional[Dict[str, float]] = None,
        training: bool = True,
    ) -> WorldRoutingResult:
        """Route a query through the MoE Three-World system.

        Args:
            query: Input query tensor of shape (batch_size, input_dim).
                   If batch_size is missing, it will be unsqueezed.
            text: Optional Arabic text for the neural layer.
            constraints: Optional constraint strings for the symbolic layer.
            interpretation: Optional truth-value dict for the categorical layer.
            training: Whether to add gating noise.

        Returns:
            WorldRoutingResult with combined output and routing metadata.
        """
        if query.dim() == 1:
            query = query.unsqueeze(0)

        batch_size = query.size(0)

        # --- Step 1: Gating ---
        sparse_weights, top_indices, load_loss = self.gate(query, training=training)
        # sparse_weights: (batch, 3), top_indices: (batch, top_k)

        # --- Step 2: Process through selected worlds ---
        world_outputs_raw: Dict[str, Any] = {}
        expert_tensors: Dict[int, torch.Tensor] = {}

        # Determine which worlds are selected (across batch)
        selected_set = set(top_indices.flatten().tolist())

        # Neural world (expert 0)
        if 0 in selected_set:
            neural_out = self._run_neural(text, batch_size)
            expert_tensors[0] = neural_out
            world_outputs_raw["neural"] = neural_out

        # Symbolic world (expert 1)
        if 1 in selected_set:
            symbolic_out = self._run_symbolic(constraints, batch_size)
            expert_tensors[1] = symbolic_out
            world_outputs_raw["symbolic"] = symbolic_out

        # Categorical world (expert 2)
        if 2 in selected_set:
            categorical_out = self._run_categorical(interpretation, batch_size)
            expert_tensors[2] = categorical_out
            world_outputs_raw["categorical"] = categorical_out

        # --- Step 3: Weighted combination ---
        combined = torch.zeros(batch_size, self.input_dim, device=query.device)
        for world_idx, tensor in expert_tensors.items():
            weight = sparse_weights[:, world_idx].unsqueeze(-1)  # (batch, 1)
            combined = combined + weight * tensor

        # --- Step 4: Output projection ---
        output = self.output_head(combined)

        # Build result
        weight_dict = {
            WORLD_NAMES[i]: float(sparse_weights[0, i].item())
            for i in range(self.num_worlds)
        }
        selected_list = top_indices[0].tolist()

        return WorldRoutingResult(
            query_embedding=query,
            routed_output=output,
            selected_worlds=selected_list,
            world_weights=weight_dict,
            load_balancing_loss=float(load_loss.item()),
            world_outputs=world_outputs_raw,
        )

    # ------------------------------------------------------------------
    # World execution helpers
    # ------------------------------------------------------------------

    def _run_neural(self, text: Optional[str], batch_size: int) -> torch.Tensor:
        """Run the neural world on text input."""
        if text is not None and hasattr(self.neural_layer, 'encode_verse'):
            embeddings = self.neural_layer.encode_verse(text)  # (seq_len, emb_dim)
            pooled = embeddings.mean(dim=0)  # (emb_dim,)
        else:
            emb_dim = getattr(self.neural_layer, 'embedding_dim', self.input_dim)
            pooled = torch.zeros(emb_dim)

        projected = self.neural_proj(pooled)  # (input_dim,)
        return projected.unsqueeze(0).expand(batch_size, -1)

    def _run_symbolic(self, constraints: Optional[List[str]], batch_size: int) -> torch.Tensor:
        """Run the symbolic world on constraints."""
        if self.symbolic_layer is not None and constraints:
            is_consistent = self.symbolic_layer.is_consistent(constraints)
            score = 1.0 if is_consistent else 0.0
        else:
            score = 0.5  # No constraints or symbolic layer unavailable

        score_tensor = torch.tensor([[score]], dtype=torch.float32)
        projected = self.symbolic_proj(score_tensor)  # (1, input_dim)
        return projected.expand(batch_size, -1)

    def _run_categorical(self, interpretation: Optional[Dict[str, float]], batch_size: int) -> torch.Tensor:
        """Run the categorical world on an interpretation."""
        if self.categorical_layer is not None:
            if interpretation:
                is_consistent = self.categorical_layer.check_interpretation_consistency(interpretation)
                truth_val = self.categorical_layer.heyting_true() if is_consistent else self.categorical_layer.heyting_false()
            else:
                truth_val = self.categorical_layer.heyting_partial(0.5)
        else:
            # Fallback: neutral truth value when categorical layer unavailable
            truth_val = 0.5

        val_tensor = torch.tensor([[truth_val]], dtype=torch.float32)
        projected = self.categorical_proj(val_tensor)  # (1, input_dim)
        return projected.expand(batch_size, -1)

    # ------------------------------------------------------------------
    # Training utilities
    # ------------------------------------------------------------------

    def compute_loss(
        self,
        routing_result: WorldRoutingResult,
        target: torch.Tensor,
    ) -> Dict[str, torch.Tensor]:
        """Compute combined task loss + load-balancing loss.

        Args:
            routing_result: Output from forward().
            target: Target tensor for the task.

        Returns:
            Dict with 'total_loss', 'task_loss', 'load_loss'.
        """
        task_loss = F.mse_loss(routing_result.routed_output, target)
        load_loss = torch.tensor(routing_result.load_balancing_loss)
        total_loss = task_loss + self.load_loss_weight * load_loss

        return {
            "total_loss": total_loss,
            "task_loss": task_loss,
            "load_loss": load_loss,
        }

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Return gating statistics for monitoring world utilization."""
        usage = self.gate.expert_usage.detach().cpu().numpy()
        return {
            "world_usage": {
                WORLD_NAMES[i]: float(usage[i])
                for i in range(self.num_worlds)
            },
            "top_k": self.top_k,
            "load_loss_weight": self.load_loss_weight,
            "usage_entropy": float(-np.sum(usage * np.log(usage + 1e-9))),
        }
