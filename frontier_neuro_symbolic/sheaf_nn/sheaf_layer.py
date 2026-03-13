"""Sheaf convolution layer for simplicial complexes.

Implements sheaf neural networks that respect the categorical structure
of simplicial complexes through restriction maps and gluing axioms.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional


class SheafConvLayer(nn.Module):
    """Sheaf convolution on a simplicial complex.

    A sheaf assigns to each node i a vector space F_i = R^{d_i}, and to each
    edge (i,j) a restriction map F_ij: F_i -> F_j. The sheaf convolution
    computes messages via restriction maps and aggregates them.

    For node j, the message from node i is:
        m_ij = F_ij(x_i) + b_ij = W_ij @ x_i + b_ij

    The updated feature is:
        x'_j = ReLU(∑_i m_ij) = ReLU(∑_i (W_ij @ x_i + b_ij))

    The restriction maps W_ij are learned parameters per edge, ensuring
    preservation of local-to-global consistency (sheaf axiom).
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        num_nodes: int,
        num_edges: int,
        bias: bool = True,
        use_self_loop: bool = True,
    ):
        """Initialize sheaf convolution layer.

        Args:
            in_channels: Input feature dimension (d_in).
            out_channels: Output feature dimension (d_out).
            num_nodes: Number of nodes in the simplicial complex.
            num_edges: Number of edges in the simplicial complex.
            bias: Whether to include bias terms in restriction maps.
            use_self_loop: Whether to add self-loops (identity restriction).
        """
        super().__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.num_nodes = num_nodes
        self.num_edges = num_edges
        self.bias = bias
        self.use_self_loop = use_self_loop

        # Restriction maps F_ij: R^{d_in} -> R^{d_out} per edge
        # Shape: (num_edges, out_channels, in_channels)
        self.weight_edge = nn.Parameter(
            torch.Tensor(num_edges, out_channels, in_channels)
        )

        # Self-loop restriction maps (identity) per node
        # Shape: (num_nodes, out_channels, in_channels)
        self.weight_self = nn.Parameter(
            torch.Tensor(num_nodes, out_channels, in_channels)
        )

        # Bias terms per edge
        if bias:
            self.bias_edge = nn.Parameter(torch.Tensor(num_edges, out_channels))
            self.bias_self = nn.Parameter(torch.Tensor(num_nodes, out_channels))
        else:
            self.register_parameter("bias_edge", None)
            self.register_parameter("bias_self", None)

        self.reset_parameters()

    def reset_parameters(self):
        """Initialize parameters using Kaiming uniform."""
        nn.init.kaiming_uniform_(self.weight_edge, a=1.0, mode="fan_in")
        nn.init.kaiming_uniform_(self.weight_self, a=1.0, mode="fan_in")

        if self.bias_edge is not None:
            nn.init.zeros_(self.bias_edge)
            nn.init.zeros_(self.bias_self)

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass of sheaf convolution.

        Args:
            x: Node features of shape (num_nodes, in_channels) or (batch_size * num_nodes, in_channels).
            edge_index: Edge indices of shape (2, num_edges).
                        edge_index[0] = source nodes
                        edge_index[1] = target nodes

        Returns:
            Updated node features of shape (num_nodes, out_channels) or (batch_size * num_nodes, out_channels).
        """
        # Check if this is a batched input
        if x.size(0) > self.num_nodes and x.size(0) % self.num_nodes == 0:
            # Handle batched case
            num_batches = x.size(0) // self.num_nodes
            x_reshaped = x.view(num_batches, self.num_nodes, -1)
            results = []
            for batch_x in x_reshaped:
                results.append(self._forward_single(batch_x, edge_index))
            return torch.cat(results, dim=0)
        else:
            # Single batch (non-batched input)
            return self._forward_single(x, edge_index)

    def _forward_single(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        """Single forward pass for non-batched input.

        Args:
            x: Node features of shape (num_nodes, in_channels).
            edge_index: Edge indices of shape (2, num_edges).

        Returns:
            Updated node features of shape (num_nodes, out_channels).
        """
        # Initialize output aggregation
        out = torch.zeros(
            x.size(0), self.out_channels, device=x.device, dtype=x.dtype
        )

        # Self-loop contributions: x'_i += W_i @ x_i + b_i
        if self.use_self_loop:
            # x: (num_nodes, in_channels)
            # weight_self: (num_nodes, out_channels, in_channels)
            # Use batched matrix multiplication
            self_contrib = torch.einsum("ni,noi->no", x, self.weight_self)
            # self_contrib: (num_nodes, out_channels)

            if self.bias_self is not None:
                self_contrib = self_contrib + self.bias_self

            out = out + self_contrib

        # Edge contributions: for each edge (i -> j)
        # x'_j += F_ij(x_i) + b_ij = W_ij @ x_i + b_ij
        if edge_index.size(1) > 0:
            src, dst = edge_index[0], edge_index[1]

            # Gather source features: (num_edges, in_channels)
            x_src = x[src]

            # Apply restriction maps via batched matmul
            # weight_edge: (num_edges, out_channels, in_channels)
            # x_src: (num_edges, in_channels)
            edge_contrib = torch.einsum("ei,eoi->eo", x_src, self.weight_edge)
            # edge_contrib: (num_edges, out_channels)

            if self.bias_edge is not None:
                edge_contrib = edge_contrib + self.bias_edge

            # Aggregate to target nodes (sum pooling respects gluing axiom)
            out = out.index_add(0, dst, edge_contrib)

        # Apply ReLU activation
        out = F.relu(out)

        return out

    def extra_repr(self) -> str:
        """Return extra representation string."""
        return (
            f"in_channels={self.in_channels}, "
            f"out_channels={self.out_channels}, "
            f"num_nodes={self.num_nodes}, "
            f"num_edges={self.num_edges}, "
            f"bias={self.bias}, "
            f"use_self_loop={self.use_self_loop}"
        )


class MultiSheafConvLayer(nn.Module):
    """Stack of multiple sheaf convolution layers.

    Allows building deeper sheaf networks by composing multiple
    sheaf convolution layers with appropriate dimension matching.
    """

    def __init__(
        self,
        in_channels: int,
        hidden_channels: list,
        out_channels: int,
        num_nodes: int,
        num_edges: int,
    ):
        """Initialize multi-layer sheaf convolution.

        Args:
            in_channels: Input feature dimension.
            hidden_channels: List of hidden layer dimensions.
            out_channels: Output feature dimension.
            num_nodes: Number of nodes.
            num_edges: Number of edges.
        """
        super().__init__()

        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.out_channels = out_channels

        # Build layers
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

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass through all layers.

        Args:
            x: Node features.
            edge_index: Edge indices.

        Returns:
            Output features after all sheaf convolutions.
        """
        for i, layer in enumerate(self.layers):
            x = layer(x, edge_index)
            # Skip activation on final layer (let downstream handle it)
            if i < len(self.layers) - 1:
                x = F.relu(x)

        return x
