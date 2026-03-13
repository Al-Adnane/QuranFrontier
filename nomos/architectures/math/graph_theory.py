"""Graph Theory Network - Network Topology.

Inspired by: Graph Theory
"""

import torch
import torch.nn as nn


class GraphTheoryNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256, num_nodes: int = 10):
        super().__init__()
        self.nodes = nn.Parameter(torch.randn(num_nodes, embed_dim) * 0.1)
        self.edges = nn.Linear(embed_dim * 2, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        node_embs = self.nodes + x.mean(dim=1, keepdim=True)
        return {'nodes': node_embs, 'connectivity': torch.sigmoid(self.edges(torch.cat([node_embs.mean(0), node_embs.std(0)], -1)))}


def create_graph_theory_network(input_dim: int = 128, embed_dim: int = 256):
    return GraphTheoryNetwork(input_dim, embed_dim)
