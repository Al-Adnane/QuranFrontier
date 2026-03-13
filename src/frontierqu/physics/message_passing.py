"""Holistic Message-Passing GNN over the Quranic Complex.

Every verse communicates with every other verse through typed edges.
The answer to any query is a subgraph activation pattern, not a single verse.

Architecture:
    Input: X in R^{6236 x d} (one row per verse)
    Structure: adjacency from QuranicComplex (all edge types)
    Output: H in R^{6236 x h} (transformed representations)
    Query: dot-product attention -> activation pattern
"""
import torch
import torch.nn as nn
from frontierqu.core.simplicial import QuranicComplex


class QuranicGNN(nn.Module):
    """Holistic message-passing network over the entire Quran."""

    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # Build complex and get adjacency (torch sparse COO tensor)
        self.complex = QuranicComplex()
        adj_sparse = self.complex.adjacency_matrix()

        # Coalesce to ensure well-formed sparse tensor
        adj_sparse = adj_sparse.coalesce()
        n = adj_sparse.shape[0]

        # Compute degree for symmetric normalization: D^{-1/2} A D^{-1/2}
        # degree = sum of adjacency weights per row + 1 (self-loop)
        degree = torch.sparse.sum(adj_sparse, dim=1).to_dense() + 1.0
        deg_inv_sqrt = 1.0 / torch.sqrt(degree)

        # Store as buffers (not parameters, but move with .to(device))
        self.register_buffer("_adj", adj_sparse)
        self.register_buffer("_deg_inv_sqrt", deg_inv_sqrt)

        # Edge type weight matrices
        edge_types = ["sequential", "thematic", "cross_reference",
                      "naskh", "munasabat", "linguistic"]
        self.edge_type_weights = nn.ModuleDict({
            etype: nn.Linear(hidden_dim, hidden_dim, bias=False)
            for etype in edge_types
        })

        # Input projection
        self.input_proj = nn.Linear(input_dim, hidden_dim)

        # Message passing layers
        self.layers = nn.ModuleList([
            nn.Linear(hidden_dim, hidden_dim) for _ in range(num_layers)
        ])
        self.global_layers = nn.ModuleList([
            nn.Linear(hidden_dim, hidden_dim) for _ in range(num_layers)
        ])
        self.norms = nn.ModuleList([
            nn.LayerNorm(hidden_dim) for _ in range(num_layers)
        ])

        # Query head
        self.query_proj = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with sparse message passing.

        Args:
            x: [num_vertices, input_dim]
        Returns:
            h: [num_vertices, hidden_dim]
        """
        h = self.input_proj(x)
        adj = self._adj
        deg = self._deg_inv_sqrt

        for layer, global_layer, norm in zip(self.layers, self.global_layers, self.norms):
            # Normalized message aggregation: D^{-1/2} A D^{-1/2} H
            h_scaled = h * deg.unsqueeze(1)
            messages = torch.sparse.mm(adj, h_scaled)
            messages = messages * deg.unsqueeze(1)

            # Global mean-pool broadcast for holistic propagation
            global_ctx = global_layer(h.mean(dim=0, keepdim=True))

            # Update with residual + local messages + global context
            h = norm(torch.relu(layer(h + messages) + global_ctx))

        return h

    def query(self, x: torch.Tensor, query_vec: torch.Tensor) -> torch.Tensor:
        """Query produces subgraph activation pattern.

        Args:
            x: [num_vertices, input_dim]
            query_vec: [hidden_dim]
        Returns:
            activations: [num_vertices] probabilities
        """
        h = self.forward(x)
        q = self.query_proj(query_vec)
        scores = (h * q.unsqueeze(0)).sum(dim=-1)
        return torch.sigmoid(scores)
