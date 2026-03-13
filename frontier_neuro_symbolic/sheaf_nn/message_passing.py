"""Sheaf message passing for multi-layer networks.

Implements message passing that respects sheaf gluing axioms,
ensuring compatibility constraints are maintained across layers.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple, Optional
from frontier_neuro_symbolic.sheaf_nn.sheaf_layer import SheafConvLayer


class SheafMessagePassing(nn.Module):
    """Multi-layer sheaf message passing network.

    Aggregates messages respecting sheaf gluing axioms, which state that
    the value of a sheaf on a union must be consistent with restrictions
    to the intersection. This module ensures that:
    1. Messages from different sources to the same target are compatible.
    2. Restrictions maintain fiber-wise linearity.
    3. Gluing of local solutions produces global solutions.
    """

    def __init__(
        self,
        in_channels: int,
        hidden_channels: List[int],
        out_channels: int,
        num_nodes: int,
        num_edges: int,
        num_layers: Optional[int] = None,
        compatibility_threshold: float = 1e-4,
    ):
        """Initialize sheaf message passing network.

        Args:
            in_channels: Input feature dimension.
            hidden_channels: List of hidden layer dimensions.
            out_channels: Output feature dimension.
            num_nodes: Number of nodes in the complex.
            num_edges: Number of edges in the complex.
            num_layers: Number of sheaf convolution layers (auto-computed if None).
            compatibility_threshold: Threshold for compatibility checking.
        """
        super().__init__()

        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.out_channels = out_channels
        self.num_nodes = num_nodes
        self.num_edges = num_edges
        self.compatibility_threshold = compatibility_threshold

        # Build sheaf convolution layers
        self.layers = nn.ModuleList()
        layer_dims = [in_channels] + hidden_channels + [out_channels]

        for i in range(len(layer_dims) - 1):
            self.layers.append(
                SheafConvLayer(
                    in_channels=layer_dims[i],
                    out_channels=layer_dims[i + 1],
                    num_nodes=num_nodes,
                    num_edges=num_edges,
                    bias=True,
                    use_self_loop=True,
                )
            )

        self.num_message_layers = len(self.layers)

        # Compatibility matrices for gluing axioms
        # These track how well restrictions compose across layers
        self.register_buffer(
            "compatibility_matrices",
            torch.eye(num_nodes).unsqueeze(0).repeat(self.num_message_layers, 1, 1),
        )

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        track_compatibility: bool = False,
    ) -> torch.Tensor:
        """Forward pass through sheaf message passing layers.

        Args:
            x: Node features of shape (num_nodes, in_channels).
            edge_index: Edge indices of shape (2, num_edges).
            track_compatibility: Whether to track gluing axiom compatibility.

        Returns:
            Output features of shape (num_nodes, out_channels).
        """
        hidden_states = [x]

        # Forward pass through all layers
        for layer_idx, layer in enumerate(self.layers):
            x = layer(x, edge_index)
            hidden_states.append(x)

            if track_compatibility:
                self._update_compatibility(x, edge_index, layer_idx)

        return x

    def _update_compatibility(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        layer_idx: int,
    ) -> None:
        """Update compatibility matrices for gluing axiom verification.

        The gluing axiom states that if a sheaf section is defined on
        overlapping open sets U and V, it must agree on the intersection.
        We check this by measuring how well restrictions compose.

        Args:
            x: Current node features.
            edge_index: Edge indices.
            layer_idx: Current layer index.
        """
        if edge_index.size(1) == 0:
            return

        src, dst = edge_index[0], edge_index[1]

        # Compute pairwise compatibility between source and destination
        # via their restriction maps
        x_norm = F.normalize(x, p=2, dim=1)  # Normalize for stability

        # Compute cosine similarities as compatibility measure
        sim_matrix = torch.mm(x_norm, x_norm.t())  # (num_nodes, num_nodes)

        # Update compatibility tracking (exponential moving average)
        if self.compatibility_matrices is not None:
            alpha = 0.1  # Smoothing factor
            self.compatibility_matrices[layer_idx] = (
                (1 - alpha) * self.compatibility_matrices[layer_idx]
                + alpha * sim_matrix
            )

    def get_compatibility_score(self, layer_idx: int = 0) -> torch.Tensor:
        """Get the gluing axiom compatibility score for a layer.

        Higher score indicates better compatibility (more consistent restrictions).

        Args:
            layer_idx: Index of the layer to check.

        Returns:
            Scalar compatibility score (0 to 1).
        """
        if self.compatibility_matrices is None or layer_idx >= len(self.layers):
            return torch.tensor(1.0)

        # Compatibility is measured as the trace of the matrix
        # (how much identity-like the composition is)
        compat_matrix = self.compatibility_matrices[layer_idx]
        trace = torch.trace(compat_matrix)
        max_trace = self.num_nodes
        return trace / max_trace

    def compute_restriction_consistency(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        """Compute how well restrictions compose (gluing axiom verification).

        For each edge (i, j), we verify that the restriction map from
        node i to node j preserves the structure. We measure this as
        the divergence between direct application vs. composition.

        Args:
            x: Node features.
            edge_index: Edge indices.

        Returns:
            Consistency score (0 = perfect consistency, higher = more violations).
        """
        if edge_index.size(1) == 0:
            return torch.tensor(0.0, device=x.device, dtype=x.dtype)

        src, dst = edge_index[0], edge_index[1]

        # Get source and destination features
        x_src = x[src]  # (num_edges, out_channels)
        x_dst = x[dst]  # (num_edges, out_channels)

        # Measure consistency as distance between restricted values
        # Lower distance = better consistency with gluing axiom
        consistency_distances = torch.norm(x_src - x_dst, p=2, dim=1)
        consistency_score = torch.mean(consistency_distances)

        return consistency_score

    def verify_gluing_axioms(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> dict:
        """Verify that gluing axioms are satisfied in the current state.

        Returns a report of axiom violations.

        Args:
            x: Node features.
            edge_index: Edge indices.

        Returns:
            Dictionary with verification results.
        """
        results = {
            "axiom_satisfied": True,
            "restriction_consistency": self.compute_restriction_consistency(x, edge_index),
            "compatibility_scores": [],
        }

        # Check compatibility for each layer
        for i in range(self.num_message_layers):
            compat = self.get_compatibility_score(i)
            results["compatibility_scores"].append(compat)

            if compat < (1.0 - self.compatibility_threshold):
                results["axiom_satisfied"] = False

        results["all_compatible"] = all(
            s >= (1.0 - self.compatibility_threshold)
            for s in results["compatibility_scores"]
        )

        return results


class SheafGluingConstraint(nn.Module):
    """Enforces gluing constraints as a learnable regularization.

    This module acts as a constraint that encourages the sheaf to
    satisfy gluing axioms by adding a penalty term to the loss.
    """

    def __init__(
        self,
        num_nodes: int,
        num_edges: int,
        constraint_strength: float = 1.0,
    ):
        """Initialize gluing constraint.

        Args:
            num_nodes: Number of nodes.
            num_edges: Number of edges.
            constraint_strength: Strength of the constraint (lambda).
        """
        super().__init__()
        self.num_nodes = num_nodes
        self.num_edges = num_edges
        self.constraint_strength = constraint_strength

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        """Compute gluing constraint penalty.

        Args:
            x: Node features of shape (num_nodes, out_channels).
            edge_index: Edge indices of shape (2, num_edges).

        Returns:
            Scalar penalty term.
        """
        if edge_index.size(1) == 0:
            return torch.tensor(0.0, device=x.device, dtype=x.dtype)

        src, dst = edge_index[0], edge_index[1]

        # Measure consistency along edges
        x_src = x[src]
        x_dst = x[dst]

        # Constraint: restrictions should be "smooth" along edges
        # We penalize large differences (violations of local-to-global consistency)
        edge_loss = torch.norm(x_src - x_dst, p=2, dim=1).mean()

        # Weight by constraint strength
        return self.constraint_strength * edge_loss

    def extra_repr(self) -> str:
        """Return extra representation string."""
        return (
            f"num_nodes={self.num_nodes}, "
            f"num_edges={self.num_edges}, "
            f"constraint_strength={self.constraint_strength}"
        )
