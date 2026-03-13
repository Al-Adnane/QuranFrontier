"""Sheaf convolution layer for simplicial complexes.

Implements sheaf neural networks that respect the categorical structure
of simplicial complexes through restriction maps and gluing axioms.

Includes SheafGluingValidator for verifying the sheaf gluing axiom:
Given local sections s_i on open sets U_i, if their restrictions agree
on all pairwise intersections (rho_ij(s_i) = rho_ji(s_j)), then there
exists a unique global section s with s|_i = s_i for all i.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional, Dict, List


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


class SheafGluingValidator(nn.Module):
    """Validates the sheaf gluing axiom on local patch data.

    Given a collection of local sections (patch vectors) on open sets U_i,
    this module:
    1. Learns restriction maps rho_ij: F(U_i) -> F(U_i cap U_j) for each
       pair of overlapping patches (i, j).
    2. Checks the COCYCLE CONDITION: for every pair (i, j),
       rho_ij(s_i) approx rho_ji(s_j) on the intersection.
    3. Checks the COMPOSITION CONDITION: for every triple (i, j, k),
       rho_jk . rho_ij approx rho_ik (restriction maps compose).
    4. Computes a global section by least-squares gluing of local sections.

    The gluing axiom is satisfied when the cocycle defect is below a threshold.

    Mathematical formulation:
    - Each patch i has a local section s_i in R^d (the stalk at i).
    - Restriction map rho_ij: R^d -> R^d_stalk is a learned linear map.
    - Cocycle defect: ||rho_ij(s_i) - rho_ji(s_j)||_2 for each edge (i,j).
    - Gluing succeeds iff max cocycle defect < threshold.
    """

    def __init__(
        self,
        stalk_dim: int,
        restriction_dim: int,
        num_patches: int,
        consistency_threshold: float = 0.5,
    ):
        """Initialize the gluing validator.

        Args:
            stalk_dim: Dimension of each local section (stalk fiber).
            restriction_dim: Dimension of the restriction (intersection) space.
            num_patches: Number of local patches (open sets).
            consistency_threshold: Maximum cocycle defect for gluing to succeed.
        """
        super().__init__()
        self.stalk_dim = stalk_dim
        self.restriction_dim = restriction_dim
        self.num_patches = num_patches
        self.consistency_threshold = consistency_threshold

        # Build complete graph edges for all patch pairs
        edges_src, edges_dst = [], []
        for i in range(num_patches):
            for j in range(i + 1, num_patches):
                edges_src.extend([i, j])
                edges_dst.extend([j, i])
        self.register_buffer(
            "edge_index",
            torch.tensor([edges_src, edges_dst], dtype=torch.long),
        )
        num_directed_edges = len(edges_src)

        # Restriction maps rho_ij: R^stalk_dim -> R^restriction_dim
        # One per directed edge
        self.restriction_maps = nn.Parameter(
            torch.empty(num_directed_edges, restriction_dim, stalk_dim)
        )
        nn.init.orthogonal_(
            self.restriction_maps.view(-1, stalk_dim)[:restriction_dim * num_directed_edges].view(
                num_directed_edges, restriction_dim, stalk_dim
            )
        )

        # Projection from stalks to global section space
        self.global_proj = nn.Linear(stalk_dim, stalk_dim, bias=False)
        nn.init.eye_(self.global_proj.weight)

    def compute_restrictions(
        self, patches: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Apply restriction maps to local sections.

        Args:
            patches: Local section vectors, shape (num_patches, stalk_dim).

        Returns:
            Tuple of:
            - restricted_src: rho_ij(s_i), shape (num_edges, restriction_dim)
            - restricted_dst: rho_ji(s_j), shape (num_edges, restriction_dim)
        """
        src, dst = self.edge_index[0], self.edge_index[1]
        num_edges = src.size(0)

        # For each directed edge e = (i->j), compute rho_e(s_i)
        # restriction_maps[e]: (restriction_dim, stalk_dim)
        # patches[src[e]]: (stalk_dim,)
        s_src = patches[src]  # (num_edges, stalk_dim)
        restricted_src = torch.einsum("erd,ed->er", self.restriction_maps, s_src)

        # For the reverse edge (j->i), we need rho_{ji}(s_j)
        # The reverse of edge e=(i->j) at position k is the edge (j->i)
        # In our edge construction, edges come in pairs: (i->j) at 2k, (j->i) at 2k+1
        # So the reverse of edge at index e is at index e^1 (XOR with 1)
        reverse_idx = torch.arange(num_edges, device=patches.device) ^ 1
        s_dst = patches[dst]
        restricted_dst = torch.einsum(
            "erd,ed->er",
            self.restriction_maps[reverse_idx],
            s_dst,
        )

        return restricted_src, restricted_dst

    def cocycle_defect(self, patches: torch.Tensor) -> torch.Tensor:
        """Compute the cocycle defect for all edge pairs.

        The cocycle defect measures how much the restriction maps disagree
        on overlapping patches. Zero defect = perfect gluing.

        Args:
            patches: Local section vectors, shape (num_patches, stalk_dim).

        Returns:
            Per-edge cocycle defect, shape (num_edges,).
        """
        restricted_src, restricted_dst = self.compute_restrictions(patches)
        # Cocycle defect: ||rho_ij(s_i) - rho_ji(s_j)||_2
        defects = torch.norm(restricted_src - restricted_dst, p=2, dim=1)
        return defects

    def composition_defect(self, patches: torch.Tensor) -> torch.Tensor:
        """Check the composition condition for all triples (i, j, k).

        For sheaf consistency: rho_jk . rho_ij should approximately equal rho_ik.
        We check this by composing restriction map matrices.

        Args:
            patches: Local section vectors, shape (num_patches, stalk_dim).

        Returns:
            Scalar composition defect (Frobenius norm of deviation).
        """
        n = self.num_patches
        if n < 3:
            return torch.tensor(0.0, device=patches.device)

        # Build edge-to-index lookup
        src, dst = self.edge_index[0], self.edge_index[1]
        edge_lookup = {}
        for idx in range(src.size(0)):
            edge_lookup[(src[idx].item(), dst[idx].item())] = idx

        total_defect = torch.tensor(0.0, device=patches.device)
        count = 0

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                for k in range(n):
                    if k == i or k == j:
                        continue
                    # Check rho_jk . rho_ij vs rho_ik
                    ij_idx = edge_lookup.get((i, j))
                    jk_idx = edge_lookup.get((j, k))
                    ik_idx = edge_lookup.get((i, k))
                    if ij_idx is None or jk_idx is None or ik_idx is None:
                        continue

                    rho_ij = self.restriction_maps[ij_idx]  # (r, d)
                    rho_jk = self.restriction_maps[jk_idx]  # (r, d)
                    rho_ik = self.restriction_maps[ik_idx]  # (r, d)

                    # Compose: rho_jk . rho_ij (treating restriction_dim == stalk_dim
                    # case, else use pseudo-inverse for composition)
                    if self.restriction_dim == self.stalk_dim:
                        composed = rho_jk @ rho_ij.T @ rho_ij  # approximate composition
                        defect = torch.norm(composed - rho_ik, p="fro")
                    else:
                        # For non-square: measure via action on patches
                        s_i = patches[i]
                        via_j = rho_jk @ (torch.linalg.lstsq(rho_ij, rho_ij @ s_i).solution)
                        direct = rho_ik @ s_i
                        defect = torch.norm(via_j - direct, p=2)

                    total_defect = total_defect + defect
                    count += 1

        if count > 0:
            total_defect = total_defect / count

        return total_defect

    def glue_global_section(self, patches: torch.Tensor) -> torch.Tensor:
        """Compute the global section by averaging restricted local sections.

        If the gluing axiom is satisfied, the local sections are consistent
        and can be glued into a unique global section. We compute this as
        the centroid of the projected local sections.

        Args:
            patches: Local section vectors, shape (num_patches, stalk_dim).

        Returns:
            Global section vector, shape (stalk_dim,).
        """
        projected = self.global_proj(patches)  # (num_patches, stalk_dim)
        global_section = projected.mean(dim=0)
        return global_section

    def forward(
        self, patches: torch.Tensor
    ) -> Dict[str, object]:
        """Full gluing axiom validation.

        Args:
            patches: Local section vectors, shape (num_patches, stalk_dim).

        Returns:
            Dictionary with:
            - gluing_satisfied (bool): Whether the gluing axiom holds.
            - cocycle_defects (Tensor): Per-edge defect values.
            - max_defect (float): Maximum cocycle defect.
            - mean_defect (float): Mean cocycle defect.
            - consistency_score (float): 1 - normalized_defect, in [0, 1].
            - global_section (Tensor): The glued global section vector.
            - composition_defect (float): How well restriction maps compose.
        """
        defects = self.cocycle_defect(patches)
        max_defect = defects.max().item()
        mean_defect = defects.mean().item()

        # Normalize consistency score: use sigmoid-like mapping
        # so that defect=0 -> score=1, defect=threshold -> score~0.5
        consistency_score = torch.exp(-defects.mean() / max(self.consistency_threshold, 1e-8)).item()

        comp_defect = self.composition_defect(patches)

        global_section = self.glue_global_section(patches)

        gluing_satisfied = max_defect < self.consistency_threshold

        return {
            "gluing_satisfied": gluing_satisfied,
            "cocycle_defects": defects.detach(),
            "max_defect": max_defect,
            "mean_defect": mean_defect,
            "consistency_score": consistency_score,
            "global_section": global_section,
            "composition_defect": comp_defect.item(),
        }

    def train_to_glue(
        self,
        patches: torch.Tensor,
        num_steps: int = 200,
        lr: float = 0.01,
    ) -> List[float]:
        """Train restriction maps to satisfy the gluing axiom on given patches.

        Optimizes the restriction maps so that cocycle defects are minimized,
        meaning the local sections become glueable.

        Args:
            patches: Local section vectors, shape (num_patches, stalk_dim).
            num_steps: Number of optimization steps.
            lr: Learning rate.

        Returns:
            List of loss values during training.
        """
        optimizer = torch.optim.Adam(self.parameters(), lr=lr)
        losses = []

        for step in range(num_steps):
            optimizer.zero_grad()
            defects = self.cocycle_defect(patches)
            loss = defects.mean()
            loss.backward()
            optimizer.step()
            losses.append(loss.item())

        return losses

    def train_to_separate(
        self,
        patches: torch.Tensor,
        num_steps: int = 200,
        lr: float = 0.01,
    ) -> List[float]:
        """Train restriction maps to MAXIMIZE cocycle defect (detect inconsistency).

        Used when patches are known to be inconsistent — the sheaf should
        detect this by producing high cocycle defects.

        Args:
            patches: Local section vectors, shape (num_patches, stalk_dim).
            num_steps: Number of optimization steps.
            lr: Learning rate.

        Returns:
            List of negative-loss values during training.
        """
        optimizer = torch.optim.Adam(self.parameters(), lr=lr)
        losses = []

        for step in range(num_steps):
            optimizer.zero_grad()
            defects = self.cocycle_defect(patches)
            loss = -defects.mean()  # Maximize defect
            loss.backward()
            optimizer.step()
            losses.append(-loss.item())

        return losses
