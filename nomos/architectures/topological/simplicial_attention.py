"""Simplicial Attention Transformer - Higher-Order Attention Mechanism."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import numpy as np

# Optional torch_geometric import
try:
    from torch_geometric.nn import MessagePassing
    HAS_TORCH_GEOMETRIC = True
except ImportError:
    HAS_TORCH_GEOMETRIC = False
    MessagePassing = nn.Module  # Fallback


@dataclass
class SimplicialStructure:
    """Simplicial complex structure."""
    vertices: torch.Tensor          # [num_vertices, feature_dim]
    edges: torch.Tensor             # [num_edges, 2] edge indices
    triangles: torch.Tensor         # [num_triangles, 3] triangle indices
    edge_features: Optional[torch.Tensor] = None
    triangle_features: Optional[torch.Tensor] = None


@dataclass
class SimplicialOutput:
    """Output from SimplicialAttentionTransformer."""
    vertex_embeddings: torch.Tensor
    edge_embeddings: torch.Tensor
    triangle_embeddings: torch.Tensor
    attention_weights: Dict[str, torch.Tensor]
    betti_numbers: Dict[int, int]


class SimplicialEmbedding(nn.Module):
    """Learn embeddings for simplices of different dimensions."""
    
    def __init__(
        self,
        num_vertices: int,
        num_edges: int,
        num_triangles: int,
        embed_dim: int
    ):
        super().__init__()
        
        self.vertex_embed = nn.Embedding(num_vertices, embed_dim)
        self.edge_embed = nn.Embedding(num_edges, embed_dim)
        self.triangle_embed = nn.Embedding(num_triangles, embed_dim)
        
        # Positional encodings for each dimension
        self.vertex_pos = nn.Parameter(torch.randn(num_vertices, embed_dim) * 0.1)
        self.edge_pos = nn.Parameter(torch.randn(num_edges, embed_dim) * 0.1)
        self.triangle_pos = nn.Parameter(torch.randn(num_triangles, embed_dim) * 0.1)
        
    def forward(
        self,
        vertex_ids: torch.Tensor,
        edge_ids: torch.Tensor,
        triangle_ids: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Get embeddings for all simplices.
        
        Args:
            vertex_ids: Vertex indices
            edge_ids: Edge indices
            triangle_ids: Triangle indices
        Returns:
            vertex_emb, edge_emb, triangle_emb
        """
        v_emb = self.vertex_embed(vertex_ids) + self.vertex_pos[vertex_ids]
        e_emb = self.edge_embed(edge_ids) + self.edge_pos[edge_ids]
        t_emb = self.triangle_embed(triangle_ids) + self.triangle_pos[triangle_ids]
        
        return v_emb, e_emb, t_emb


class SimplicialAttentionLayer(MessagePassing):
    """Attention layer operating on simplicial complexes."""
    
    def __init__(
        self,
        embed_dim: int,
        num_heads: int = 8,
        dropout: float = 0.1,
        simplex_dim: int = 1  # 0=vertices, 1=edges, 2=triangles
    ):
        super().__init__(aggr='add', flow='source_to_target')
        
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.simplex_dim = simplex_dim
        self.head_dim = embed_dim // num_heads
        
        # Query, Key, Value projections
        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        
        # Output projection
        self.out_proj = nn.Linear(embed_dim, embed_dim)
        
        # Attention scaling
        self.scale = np.sqrt(self.head_dim)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        # Layer norm
        self.norm = nn.LayerNorm(embed_dim)
        
    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        simplex_features: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Apply simplicial attention.
        
        Args:
            x: Node features [num_nodes, embed_dim]
            edge_index: Edge connectivity [2, num_edges]
            simplex_features: Optional simplex-specific features
        Returns:
            Updated node features
        """
        residual = x
        
        # Project to Q, K, V
        q = self.q_proj(x).view(-1, self.num_heads, self.head_dim)
        k = self.k_proj(x).view(-1, self.num_heads, self.head_dim)
        v = self.v_proj(x).view(-1, self.num_heads, self.head_dim)
        
        # Compute attention weights
        # For simplicial attention, we attend over the star of each simplex
        attention_scores = (q * k[edge_index[1]]).sum(dim=-1) / self.scale
        
        # Apply softmax over neighbors
        attention_weights = F.softmax(attention_scores, dim=0)
        attention_weights = self.dropout(attention_weights)
        
        # Message passing with attention
        out = self.propagate(
            edge_index,
            x=v,
            attention_weights=attention_weights
        )
        
        # Reshape and project
        out = out.view(-1, self.embed_dim)
        out = self.out_proj(out)
        
        # Residual + norm
        out = self.norm(out + residual)
        
        return out
    
    def message(
        self,
        x_j: torch.Tensor,
        attention_weights: torch.Tensor
    ) -> torch.Tensor:
        """Compute messages with attention."""
        # attention_weights: [num_edges, num_heads]
        # x_j: [num_edges, num_heads, head_dim]
        return attention_weights.unsqueeze(-1) * x_j


class BoundaryOperator(nn.Module):
    """Boundary operator for simplicial complexes.
    
    ∂_k: C_k → C_{k-1}
    
    For edges (k=1): ∂_1(e) = v_j - v_i
    For triangles (k=2): ∂_2(t) = e_1 + e_2 + e_3 (oriented)
    """
    
    def __init__(self, from_dim: int, to_dim: int):
        super().__init__()
        self.from_dim = from_dim
        self.to_dim = to_dim
        
    def forward(
        self,
        simplex_features: torch.Tensor,
        boundary_matrix: torch.Tensor
    ) -> torch.Tensor:
        """Apply boundary operator.
        
        Args:
            simplex_features: Features of k-simplices
            boundary_matrix: Sparse boundary matrix [num_(k-1), num_k]
        Returns:
            Features on (k-1)-simplices
        """
        # Matrix multiplication: boundary @ features
        return torch.sparse.mm(boundary_matrix, simplex_features)


class SimplicialAttentionTransformer(nn.Module):
    """Main Simplicial Attention Transformer model.
    
    Extends standard transformer to operate on simplicial complexes,
    enabling higher-order attention over triangles and beyond.
    """
    
    def __init__(
        self,
        num_vertices: int,
        num_edges: int,
        num_triangles: int,
        embed_dim: int = 512,
        num_heads: int = 8,
        num_layers: int = 6,
        dropout: float = 0.1,
        max_seq_len: int = 512
    ):
        super().__init__()
        
        # Embeddings
        self.embedding = SimplicialEmbedding(
            num_vertices, num_edges, num_triangles, embed_dim
        )
        
        # Vertex attention layers
        self.vertex_attention = nn.ModuleList([
            SimplicialAttentionLayer(embed_dim, num_heads, dropout, simplex_dim=0)
            for _ in range(num_layers)
        ])
        
        # Edge attention layers
        self.edge_attention = nn.ModuleList([
            SimplicialAttentionLayer(embed_dim, num_heads, dropout, simplex_dim=1)
            for _ in range(num_layers)
        ])
        
        # Triangle attention layers
        self.triangle_attention = nn.ModuleList([
            SimplicialAttentionLayer(embed_dim, num_heads, dropout, simplex_dim=2)
            for _ in range(num_layers)
        ])
        
        # Boundary operators
        self.boundary_1_0 = BoundaryOperator(1, 0)
        self.boundary_2_1 = BoundaryOperator(2, 1)
        
        # Coboundary operators (adjoint of boundary)
        self.coboundary_0_1 = BoundaryOperator(0, 1)
        self.coboundary_1_2 = BoundaryOperator(1, 2)
        
        # Fusion layers
        self.vertex_fusion = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim),
            nn.GELU(),
            nn.LayerNorm(embed_dim)
        )
        self.edge_fusion = nn.Sequential(
            nn.Linear(embed_dim * 3, embed_dim),
            nn.GELU(),
            nn.LayerNorm(embed_dim)
        )
        
        # Output heads
        self.vertex_head = nn.Linear(embed_dim, embed_dim)
        self.edge_head = nn.Linear(embed_dim, embed_dim)
        self.triangle_head = nn.Linear(embed_dim, embed_dim)
        
        # Store dimensions
        self.num_vertices = num_vertices
        self.num_edges = num_edges
        self.num_triangles = num_triangles
        self.embed_dim = embed_dim
        
    def build_boundary_matrices(
        self,
        edges: torch.Tensor,
        triangles: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Build sparse boundary matrices.
        
        Args:
            edges: [num_edges, 2]
            triangles: [num_triangles, 3]
        Returns:
            boundary_1_0: [num_vertices, num_edges]
            boundary_2_1: [num_edges, num_triangles]
        """
        # ∂_1: edges → vertices
        # Each edge (i, j) contributes +1 to j and -1 to i
        indices_1_0 = []
        values_1_0 = []
        
        for e_idx, (i, j) in enumerate(edges.tolist()):
            indices_1_0.append([i, e_idx])
            values_1_0.append(-1)
            indices_1_0.append([j, e_idx])
            values_1_0.append(1)
        
        boundary_1_0 = torch.sparse_coo_tensor(
            torch.tensor(indices_1_0).t(),
            torch.tensor(values_1_0, dtype=torch.float32),
            (self.num_vertices, self.num_edges)
        )
        
        # ∂_2: triangles → edges
        # Each triangle (i, j, k) contributes to edges (i,j), (j,k), (k,i)
        edge_to_idx = {(min(e[0], e[1]), max(e[0], e[1])): idx 
                       for idx, e in enumerate(edges.tolist())}
        
        indices_2_1 = []
        values_2_1 = []
        
        for t_idx, (i, j, k) in enumerate(triangles.tolist()):
            # Edge (i, j)
            e1 = edge_to_idx.get((min(i, j), max(i, j)))
            if e1 is not None:
                indices_2_1.append([e1, t_idx])
                values_2_1.append(1)
            
            # Edge (j, k)
            e2 = edge_to_idx.get((min(j, k), max(j, k)))
            if e2 is not None:
                indices_2_1.append([e2, t_idx])
                values_2_1.append(1)
            
            # Edge (k, i)
            e3 = edge_to_idx.get((min(k, i), max(k, i)))
            if e3 is not None:
                indices_2_1.append([e3, t_idx])
                values_2_1.append(1)
        
        boundary_2_1 = torch.sparse_coo_tensor(
            torch.tensor(indices_2_1).t(),
            torch.tensor(values_2_1, dtype=torch.float32),
            (self.num_edges, self.num_triangles)
        )
        
        return boundary_1_0, boundary_2_1
    
    def compute_betti_numbers(
        self,
        boundary_1_0: torch.Tensor,
        boundary_2_1: torch.Tensor
    ) -> Dict[int, int]:
        """Compute Betti numbers (topological invariants).
        
        β_0 = dim(ker ∂_0) - dim(im ∂_1) = num_connected_components
        β_1 = dim(ker ∂_1) - dim(im ∂_2) = num_1d_holes
        β_2 = dim(ker ∂_2) = num_voids
        """
        # Approximate Betti numbers using rank estimation
        # In practice, would use sparse linear algebra
        
        # β_0 ≈ num_vertices - rank(boundary_1_0)
        rank_1_0 = torch.matrix_rank(boundary_1_0.to_dense())
        beta_0 = int(self.num_vertices - rank_1_0.item())
        
        # β_1 ≈ num_edges - rank(boundary_1_0) - rank(boundary_2_1)
        rank_2_1 = torch.matrix_rank(boundary_2_1.to_dense())
        beta_1 = int(self.num_edges - rank_1_0.item() - rank_2_1.item())
        
        # β_2 ≈ num_triangles - rank(boundary_2_1)
        beta_2 = int(self.num_triangles - rank_2_1.item())
        
        return {
            0: max(0, beta_0),
            1: max(0, beta_1),
            2: max(0, beta_2)
        }
    
    def forward(
        self,
        structure: SimplicialStructure
    ) -> SimplicialOutput:
        """Forward pass through simplicial transformer.
        
        Args:
            structure: Simplicial complex structure
        Returns:
            SimplicialOutput with embeddings at all dimensions
        """
        # Get initial embeddings
        vertex_ids = torch.arange(self.num_vertices, device=structure.vertices.device)
        edge_ids = torch.arange(self.num_edges, device=structure.edges.device)
        triangle_ids = torch.arange(self.num_triangles, device=structure.triangles.device)
        
        v_emb, e_emb, t_emb = self.embedding(vertex_ids, edge_ids, triangle_ids)
        
        # Add input features
        v_emb = v_emb + structure.vertices
        if structure.edge_features is not None:
            e_emb = e_emb + structure.edge_features
        if structure.triangle_features is not None:
            t_emb = t_emb + structure.triangle_features
        
        # Build boundary matrices
        b_1_0, b_2_1 = self.build_boundary_matrices(structure.edges, structure.triangles)
        
        # Compute Betti numbers
        betti = self.compute_betti_numbers(b_1_0, b_2_1)
        
        # Store attention weights
        attention_weights = {'vertex': [], 'edge': [], 'triangle': []}
        
        # Process through layers
        for layer_idx, (v_attn, e_attn, t_attn) in enumerate(
            zip(self.vertex_attention, self.edge_attention, self.triangle_attention)
        ):
            # Vertex attention with edge messages
            v_messages = self.boundary_1_0(e_emb, b_1_0)
            v_attn_out = v_attn(v_emb, structure.edges)
            v_emb = self.vertex_fusion(torch.cat([v_attn_out, v_messages], dim=-1))
            
            # Edge attention with vertex and triangle messages
            e_from_v = self.coboundary_0_1(v_emb, b_1_0.t())
            e_from_t = self.boundary_2_1(t_emb, b_2_1)
            e_attn_out = e_attn(e_emb, self._edge_to_edge_graph(structure.edges, structure.triangles))
            e_emb = self.edge_fusion(torch.cat([e_attn_out, e_from_v, e_from_t], dim=-1))
            
            # Triangle attention with edge messages
            t_from_e = self.coboundary_1_2(e_emb, b_2_1.t())
            t_attn_out = t_attn(t_emb, self._triangle_to_triangle_graph(structure.triangles))
            t_emb = t_emb + t_attn_out + t_from_e
            
            # Store attention weights
            attention_weights['vertex'].append(v_attn.attention_weights if hasattr(v_attn, 'attention_weights') else None)
        
        # Output projections
        v_out = self.vertex_head(v_emb)
        e_out = self.edge_head(e_emb)
        t_out = self.triangle_head(t_emb)
        
        return SimplicialOutput(
            vertex_embeddings=v_out,
            edge_embeddings=e_out,
            triangle_embeddings=t_out,
            attention_weights=attention_weights,
            betti_numbers=betti
        )
    
    def _edge_to_edge_graph(
        self,
        edges: torch.Tensor,
        triangles: torch.Tensor
    ) -> torch.Tensor:
        """Build edge-to-edge adjacency via triangles."""
        edge_pairs = []
        
        for tri in triangles.tolist():
            # Edges in same triangle are adjacent
            for i in range(3):
                for j in range(i + 1, 3):
                    edge_pairs.append([tri[i], tri[j]])
                    edge_pairs.append([tri[j], tri[i]])
        
        if edge_pairs:
            return torch.tensor(edge_pairs, dtype=torch.long).t().contiguous()
        else:
            return torch.zeros((2, 0), dtype=torch.long)
    
    def _triangle_to_triangle_graph(
        self,
        triangles: torch.Tensor
    ) -> torch.Tensor:
        """Build triangle-to-triangle adjacency via shared edges."""
        # Simplified: triangles sharing 2 vertices are adjacent
        tri_pairs = []
        
        for i in range(len(triangles)):
            for j in range(i + 1, len(triangles)):
                shared = len(set(triangles[i].tolist()) & set(triangles[j].tolist()))
                if shared >= 2:
                    tri_pairs.append([i, j])
                    tri_pairs.append([j, i])
        
        if tri_pairs:
            return torch.tensor(tri_pairs, dtype=torch.long).t().contiguous()
        else:
            return torch.zeros((2, 0), dtype=torch.long)


def create_simplicial_transformer(
    num_vertices: int = 512,
    num_edges: int = 1024,
    num_triangles: int = 256,
    embed_dim: int = 512,
    num_heads: int = 8,
    num_layers: int = 6
) -> SimplicialAttentionTransformer:
    """Create SimplicialAttentionTransformer."""
    return SimplicialAttentionTransformer(
        num_vertices=num_vertices,
        num_edges=num_edges,
        num_triangles=num_triangles,
        embed_dim=embed_dim,
        num_heads=num_heads,
        num_layers=num_layers
    )
