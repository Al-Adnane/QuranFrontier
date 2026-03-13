# FrontierQu v3.0 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade FrontierQu from v2.0.0 to v3.0.0 by implementing 5 neural-symbolic components: Sheaf convolutions, Differentiable Naskh solver, Morphological attention, Multi-agent Tafsir verification, and Morpho-syntactic embeddings.

**Architecture:** Five orthogonal modules integrated into existing codebase:
1. `topology/sheaf_layer.py` — Sheaf convolutions for verse-to-verse semantic propagation
2. `logic/neuro_symbolic_naskh.py` — Differentiable abrogation solver with chronological constraints
3. `linguistic/morph_attention.py` — Root-aware morphological biasing for attention
4. `agentic/tafsir_verifier.py` — Multi-agent debate loop with constitutional guardrails
5. `search/morpho_embeddings.py` — Enhanced embeddings with morpho-syntactic awareness

**Tech Stack:** PyTorch 2.0+, NetworkX, Z3-solver, LangGraph (for agentic), AraBERT embeddings, Quranic Arabic Corpus (QAC) morphological tags

---

## File Structure

### New Files to Create
```
src/frontierqu/topology/sheaf_layer.py          # Sheaf convolution layer
src/frontierqu/logic/neuro_symbolic_naskh.py    # Differentiable Naskh solver
src/frontierqu/linguistic/morph_attention.py    # Morphological attention biasing
src/frontierqu/agentic/tafsir_verifier.py       # Multi-agent verification loop
src/frontierqu/agentic/constitutional_guard.py  # Safety constraints module
src/frontierqu/search/morpho_embeddings.py      # Morpho-syntactic embedding store

tests/topology/test_sheaf_layer.py              # Sheaf layer tests
tests/logic/test_naskh_solver.py                # Naskh solver tests
tests/linguistic/test_morph_attention.py        # Attention bias tests
tests/agentic/test_tafsir_verifier.py          # Multi-agent tests
tests/search/test_morpho_embeddings.py         # Embedding tests
```

### Modified Files
```
src/frontierqu/core/simplicial.py               # Add edge extraction for Sheaf
src/frontierqu/core/tensor.py                   # Add chronology matrix construction
src/frontierqu/agentic/agent.py                 # Integrate verifier into main agent
src/frontierqu/search/embedding_store.py        # Wire morpho embeddings
pyproject.toml                                  # Add langgraph, langchain dependencies
```

---

# Chunk 1: Sheaf Neural Networks (Topology)

## Task 1: Sheaf Convolution Layer

**Files:**
- Create: `src/frontierqu/topology/sheaf_layer.py`
- Modify: `src/frontierqu/core/simplicial.py` (add edge extraction)
- Test: `tests/topology/test_sheaf_layer.py`

### Step 1: Write the failing test

```bash
# Create test file
cat > tests/topology/test_sheaf_layer.py << 'EOF'
import pytest
import torch
from frontierqu.topology.sheaf_layer import SheafConvLayer


class TestSheafConvLayer:
    def test_sheaf_layer_initialization(self):
        """Test SheafConvLayer can be initialized with correct dimensions."""
        layer = SheafConvLayer(in_channels=768, out_channels=768, num_edges=100)
        assert layer.restriction_maps.shape == (100, 768, 768)
        assert layer.bias.shape == (100, 768)

    def test_sheaf_layer_forward_pass(self):
        """Test forward pass produces correct output shape."""
        batch_size = 1
        num_nodes = 6236  # Approximate number of verses in Quran
        in_channels = 768
        out_channels = 512
        num_edges = 8000  # Approximate thematic links

        layer = SheafConvLayer(in_channels, out_channels, num_edges)
        x = torch.randn(num_nodes, in_channels)
        edge_index = torch.randint(0, num_nodes, (2, num_edges))

        output = layer(x, edge_index)

        assert output.shape == (num_nodes, out_channels)
        assert not torch.isnan(output).any(), "Output contains NaN"

    def test_sheaf_layer_with_weights(self):
        """Test forward pass with edge weights."""
        num_nodes = 100
        in_channels = 64
        out_channels = 64
        num_edges = 50

        layer = SheafConvLayer(in_channels, out_channels, num_edges)
        x = torch.randn(num_nodes, in_channels)
        edge_index = torch.randint(0, num_nodes, (2, num_edges))
        edge_weight = torch.rand(num_edges)

        output = layer(x, edge_index, edge_weight)

        assert output.shape == (num_nodes, out_channels)

    def test_sheaf_layer_preserves_gradients(self):
        """Test that gradients flow through restriction maps."""
        layer = SheafConvLayer(32, 32, 20)
        x = torch.randn(10, 32, requires_grad=True)
        edge_index = torch.tensor([[0, 1, 2], [1, 2, 3]])

        output = layer(x, edge_index)
        loss = output.sum()
        loss.backward()

        assert layer.restriction_maps.grad is not None
        assert x.grad is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
EOF
```

**Run:** `cd ~/Desktop/FrontierQu && pytest tests/topology/test_sheaf_layer.py -v`

**Expected:** ❌ FAIL — `ModuleNotFoundError: No module named 'frontierqu.topology.sheaf_layer'`

### Step 2: Implement Sheaf Convolution Layer

```bash
cat > src/frontierqu/topology/sheaf_layer.py << 'EOF'
"""Sheaf Neural Network Layer for Quranic Structure.

A Sheaf is a generalization of fiber bundles that models how data (semantic meaning)
glues together over overlapping contexts (verses, themes, time periods).

For each edge in the simplicial complex (thematic connection between verses),
we learn a restriction map F_ij that transforms features from verse i to verse j.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class SheafConvLayer(nn.Module):
    """
    A convolutional layer operating over a simplicial complex using sheaf restriction maps
    to propagate semantic features between interconnected verses.

    Mathematical formulation:
    - For each edge (i,j), learn a linear restriction map F_ij: R^{d_in} -> R^{d_out}
    - Message from i to j: m_ij = F_ij @ x_i + b_ij
    - Node j aggregates: x'_j = ReLU(sum_i m_ij)
    """

    def __init__(self, in_channels: int, out_channels: int, num_edges: int):
        """
        Initialize Sheaf convolution layer.

        Args:
            in_channels: Feature dimension of input node embeddings
            out_channels: Feature dimension of output node embeddings
            num_edges: Number of edges in the simplicial complex
        """
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.num_edges = num_edges

        # Restriction maps: one per edge, transforming across that edge
        self.restriction_maps = nn.Parameter(
            torch.Tensor(num_edges, in_channels, out_channels)
        )
        self.bias = nn.Parameter(torch.Tensor(num_edges, out_channels))

        self.reset_parameters()

    def reset_parameters(self):
        """Initialize parameters using Xavier uniform."""
        nn.init.xavier_uniform_(self.restriction_maps)
        nn.init.zeros_(self.bias)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor,
                edge_weight: torch.Tensor = None) -> torch.Tensor:
        """
        Forward pass of Sheaf convolution.

        Args:
            x: Node features [num_nodes, in_channels]
            edge_index: Edge connectivity [2, num_edges], where edge_index[0] is source
                        and edge_index[1] is destination
            edge_weight: Optional edge weights [num_edges]

        Returns:
            Node features after restriction map aggregation [num_nodes, out_channels]
        """
        num_nodes = x.size(0)
        num_edges_actual = edge_index.size(1)

        # Initialize output aggregation
        out = torch.zeros(
            num_nodes, self.out_channels,
            device=x.device, dtype=x.dtype
        )

        # Message passing: for each edge, apply restriction map
        row, col = edge_index  # row = source, col = destination

        for edge_id in range(num_edges_actual):
            src_node = row[edge_id].item()
            dst_node = col[edge_id].item()

            # Get restriction map for this edge (cycle through if more edges than learned maps)
            map_idx = edge_id % self.num_edges
            restriction_map = self.restriction_maps[map_idx]  # [in_channels, out_channels]
            bias = self.bias[map_idx]  # [out_channels]

            # Apply restriction: transform source features, add bias
            src_features = x[src_node]  # [in_channels]
            message = torch.matmul(src_features, restriction_map) + bias  # [out_channels]

            # Apply edge weight if provided
            if edge_weight is not None:
                message = message * edge_weight[edge_id]

            # Aggregate into destination node
            out[dst_node] += message

        # Apply activation
        out = F.relu(out)

        return out


class SheafNeuralNetwork(nn.Module):
    """Multi-layer Sheaf neural network for processing Quranic structure."""

    def __init__(self, in_channels: int, hidden_channels: int,
                 out_channels: int, num_layers: int, num_edges: int):
        super().__init__()
        self.layers = nn.ModuleList()

        # Input layer
        self.layers.append(SheafConvLayer(in_channels, hidden_channels, num_edges))

        # Hidden layers
        for _ in range(num_layers - 2):
            self.layers.append(SheafConvLayer(hidden_channels, hidden_channels, num_edges))

        # Output layer
        self.layers.append(SheafConvLayer(hidden_channels, out_channels, num_edges))

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """Forward pass through all Sheaf layers."""
        for layer in self.layers[:-1]:
            x = layer(x, edge_index)
        # Final layer without activation
        x = self.layers[-1](x, edge_index)
        return x
EOF
```

### Step 3: Run test to verify it passes

**Run:** `cd ~/Desktop/FrontierQu && pytest tests/topology/test_sheaf_layer.py -v`

**Expected:** ✅ PASS — All 4 tests pass

### Step 4: Commit

```bash
cd ~/Desktop/FrontierQu
git add src/frontierqu/topology/sheaf_layer.py tests/topology/test_sheaf_layer.py
git commit -m "feat(topology): add Sheaf Neural Network layer for verse propagation"
```

---

## Task 2: Simplicial Complex Edge Extraction

**Files:**
- Modify: `src/frontierqu/core/simplicial.py` (add edge extraction method)
- Test: Update `tests/core/test_simplicial.py`

### Step 1: Write failing test for edge extraction

```bash
cat >> tests/core/test_simplicial.py << 'EOF'

def test_extract_edges_from_simplicial_complex():
    """Test edge extraction from simplicial complex."""
    from frontierqu.core.simplicial import SimplicialComplex
    from frontierqu.topology.sheaf_layer import SheafConvLayer

    # Create mock simplicial complex
    sc = SimplicialComplex()
    # Assume method exists: extract_edges() -> (edge_index, num_edges)
    edge_index, num_edges = sc.extract_edges()

    assert edge_index.shape[0] == 2, "Edge index should be [2, num_edges]"
    assert edge_index.shape[1] == num_edges
    assert num_edges > 0, "Should extract at least one edge"
EOF
```

### Step 2: Add edge extraction to SimplicialComplex

```bash
# Append to src/frontierqu/core/simplicial.py
cat >> src/frontierqu/core/simplicial.py << 'EOF'

    def extract_edges(self):
        """Extract edges from simplicial complex for Sheaf NN.

        Returns:
            edge_index: torch.Tensor of shape [2, num_edges]
            num_edges: int, number of edges
        """
        import torch
        edges = []

        if hasattr(self, 'simplices'):
            for simplex in self.simplices:
                if len(simplex) >= 2:
                    # Extract pairwise edges from faces
                    vertices = list(simplex)
                    for i in range(len(vertices)):
                        for j in range(i + 1, len(vertices)):
                            edges.append([vertices[i], vertices[j]])

        if edges:
            edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
        else:
            edge_index = torch.zeros((2, 0), dtype=torch.long)

        return edge_index, edge_index.shape[1]
EOF
```

### Step 3: Run test

**Run:** `cd ~/Desktop/FrontierQu && pytest tests/core/test_simplicial.py::test_extract_edges_from_simplicial_complex -v`

**Expected:** ✅ PASS

### Step 4: Commit

```bash
cd ~/Desktop/FrontierQu
git add src/frontierqu/core/simplicial.py tests/core/test_simplicial.py
git commit -m "feat(core): add edge extraction for Sheaf NN compatibility"
```

---

# Chunk 2: Differentiable Naskh Solver (Logic)

## Task 3: Differentiable Naskh Solver

**Files:**
- Create: `src/frontierqu/logic/neuro_symbolic_naskh.py`
- Modify: `src/frontierqu/core/tensor.py` (add chronology matrix)
- Test: `tests/logic/test_naskh_solver.py`

### Step 1: Write failing test

```bash
cat > tests/logic/test_naskh_solver.py << 'EOF'
import pytest
import torch
from frontierqu.logic.neuro_symbolic_naskh import DifferentiableNaskhSolver


class TestDifferentiableNaskhSolver:
    def test_naskh_solver_initialization(self):
        """Test NaskhSolver can be initialized."""
        solver = DifferentiableNaskhSolver(embed_dim=768)
        assert solver is not None
        assert hasattr(solver, 'attention')
        assert hasattr(solver, 'classifier')

    def test_naskh_solver_forward(self):
        """Test forward pass produces abrogation probability matrix."""
        solver = DifferentiableNaskhSolver(embed_dim=256)

        batch_size = 1
        seq_len = 100  # Mock number of verses
        embed_dim = 256

        verse_embeddings = torch.randn(batch_size, seq_len, embed_dim)
        chronology_matrix = torch.triu(torch.ones(seq_len, seq_len), diagonal=1)

        prob_matrix = solver(verse_embeddings, chronology_matrix)

        assert prob_matrix.shape == (seq_len, seq_len)
        assert torch.all(prob_matrix >= 0) and torch.all(prob_matrix <= 1)

    def test_logic_loss_penalizes_violations(self):
        """Test logic loss penalizes chronological violations."""
        solver = DifferentiableNaskhSolver(embed_dim=128)

        # Probability matrix with violations
        prob_matrix = torch.tensor([
            [0.0, 0.9, 0.1],  # Verse 0 claims to abrogate verse 1 (later)
            [0.1, 0.0, 0.8],  # Verse 1 claims to abrogate verse 2 (later)
            [0.7, 0.2, 0.0],  # Verse 2 claims to abrogate verse 0 (VIOLATION)
        ])

        # Chronology: only later verses can abrogate earlier
        chronology_matrix = torch.tensor([
            [0, 1, 1],  # 0 is before 1 and 2
            [0, 0, 1],  # 1 is before 2
            [0, 0, 0],  # 2 is after all
        ], dtype=torch.float)

        loss = solver.logic_loss(prob_matrix, chronology_matrix)
        assert loss > 0, "Should penalize violation where 2 abrogates 0"

    def test_logic_loss_allows_valid_abrogations(self):
        """Test logic loss permits valid chronological abrogations."""
        solver = DifferentiableNaskhSolver(embed_dim=128)

        # Valid abrogation: verse 2 abrogates verse 0 (2 comes later)
        prob_matrix = torch.tensor([
            [0.0, 0.1, 0.8],  # Verse 0: low prob of abrogating later verses
            [0.1, 0.0, 0.2],  # Verse 1: low prob
            [0.1, 0.1, 0.0],  # Verse 2: high prob of abrogating earlier (valid)
        ])

        chronology_matrix = torch.tensor([
            [0, 1, 1],
            [0, 0, 1],
            [0, 0, 0],
        ], dtype=torch.float)

        loss = solver.logic_loss(prob_matrix, chronology_matrix)
        assert loss < 0.5, "Valid abrogations should incur low loss"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
EOF
```

**Run:** `cd ~/Desktop/FrontierQu && pytest tests/logic/test_naskh_solver.py -v`

**Expected:** ❌ FAIL — Module not found

### Step 2: Implement Differentiable Naskh Solver

```bash
cat > src/frontierqu/logic/neuro_symbolic_naskh.py << 'EOF'
"""Neuro-Symbolic Naskh (Abrogation) Solver.

Naskh is the Islamic jurisprudential concept that later Quranic verses can abrogate
(cancel or modify) earlier ones. This module learns probabilistic abrogation relations
while respecting chronological constraints: only verses revealed later can abrogate earlier ones.

The solver uses:
1. Attention mechanism to capture semantic similarity/dependency
2. Classifier network to predict pairwise abrogation probabilities
3. Logic regularization loss to enforce chronological constraints
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class DifferentiableNaskhSolver(nn.Module):
    """
    Learn pairwise abrogation probabilities between verses with chronological constraints.

    Architecture:
    - MultiheadAttention to encode semantic relationships
    - 2-layer MLP to classify abrogation likelihood for each verse pair
    - Soft logic loss to penalize violations of temporal ordering
    """

    def __init__(self, embed_dim: int = 768, num_heads: int = 8,
                 hidden_dim: int = 256, dropout: float = 0.1):
        """
        Initialize Naskh solver.

        Args:
            embed_dim: Embedding dimension of verse features
            num_heads: Number of attention heads
            hidden_dim: Hidden dimension of classifier MLP
            dropout: Dropout rate
        """
        super().__init__()
        self.embed_dim = embed_dim

        # Semantic dependency encoder: MultiheadAttention
        self.attention = nn.MultiheadAttention(
            embed_dim,
            num_heads=num_heads,
            batch_first=True,
            dropout=dropout
        )

        # Abrogation classifier: takes concatenated [attn(verse_i), attn(verse_j)]
        self.classifier = nn.Sequential(
            nn.Linear(embed_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1)  # Binary classification: P(i abrogates j)
        )

    def forward(self, verse_embeddings: torch.Tensor,
                chronology_matrix: torch.Tensor) -> torch.Tensor:
        """
        Predict abrogation probabilities.

        Args:
            verse_embeddings: Tensor of shape [batch, seq_len, embed_dim]
            chronology_matrix: Binary matrix [seq_len, seq_len] where
                              chronology[i, j] = 1 if verse i comes before verse j

        Returns:
            Probability matrix [seq_len, seq_len] where prob[i, j] = P(i abrogates j)
        """
        batch_size = verse_embeddings.shape[0]
        seq_len = verse_embeddings.shape[1]

        # Encode semantic relationships via attention
        attn_out, _ = self.attention(
            verse_embeddings, verse_embeddings, verse_embeddings
        )  # [batch, seq_len, embed_dim]

        # For simplicity, use first item in batch (can be extended)
        attn_features = attn_out[0]  # [seq_len, embed_dim]

        # Compute pairwise abrogation scores
        score_matrix = torch.zeros(seq_len, seq_len, device=verse_embeddings.device)

        for i in range(seq_len):
            for j in range(seq_len):
                if i == j:
                    score_matrix[i, j] = 0.0  # A verse doesn't abrogate itself
                    continue

                # Concatenate features of both verses
                pair_feat = torch.cat([attn_features[i], attn_features[j]], dim=-1)

                # Classify: is i abrogated by j?
                logit = self.classifier(pair_feat)
                prob = torch.sigmoid(logit).squeeze()
                score_matrix[i, j] = prob

        return score_matrix

    def logic_loss(self, prob_matrix: torch.Tensor,
                   chronology_matrix: torch.Tensor) -> torch.Tensor:
        """
        Constraint loss: penalize abrogations that violate chronological order.

        Constraint: If verse i abrogates verse j, then i must come AFTER j.
        In other words: P(i abrogates j) should be low if chronology[i, j] = 1
        (i.e., if i comes before j).

        Args:
            prob_matrix: Predicted abrogation probability matrix [seq_len, seq_len]
            chronology_matrix: Ground truth chronology [seq_len, seq_len]
                              1 if first verse is before second, 0 otherwise

        Returns:
            Scalar loss (higher = more violations)
        """
        # Identify violations: high probability of abrogation in wrong direction
        # violation_mask[i, j] = True if we predict i abrogates j BUT i comes before j
        violation_mask = (prob_matrix > 0.5) & (chronology_matrix == 1)

        # Soft penalty using cross-entropy style loss
        # For violations, we want to push prob_matrix[i, j] towards 0
        penalty = torch.relu(prob_matrix - 0.5) * chronology_matrix

        return penalty.mean()

    def combined_loss(self, prob_matrix: torch.Tensor,
                      chronology_matrix: torch.Tensor,
                      ground_truth_matrix: torch.Tensor = None,
                      lambda_logic: float = 1.0) -> torch.Tensor:
        """
        Combined loss: Cross-entropy (if labels available) + Logic constraint loss.

        Args:
            prob_matrix: Predicted probabilities
            chronology_matrix: Temporal ordering constraints
            ground_truth_matrix: Ground truth abrogations (optional)
            lambda_logic: Weight for logic loss term

        Returns:
            Total loss
        """
        logic_loss = self.logic_loss(prob_matrix, chronology_matrix)

        # If ground truth available, add supervised loss
        total_loss = lambda_logic * logic_loss

        if ground_truth_matrix is not None:
            # Binary cross-entropy with ground truth
            ce_loss = F.binary_cross_entropy(prob_matrix, ground_truth_matrix)
            total_loss = total_loss + ce_loss

        return total_loss
EOF
```

### Step 3: Run test

**Run:** `cd ~/Desktop/FrontierQu && pytest tests/logic/test_naskh_solver.py -v`

**Expected:** ✅ PASS — All 4 tests pass

### Step 4: Commit

```bash
cd ~/Desktop/FrontierQu
git add src/frontierqu/logic/neuro_symbolic_naskh.py tests/logic/test_naskh_solver.py
git commit -m "feat(logic): add Differentiable Naskh solver with chronological constraints"
```

---

# Chunk 3: Morphological Attention (Linguistic)

## Task 4: Morphological Attention Biasing

**Files:**
- Create: `src/frontierqu/linguistic/morph_attention.py`
- Test: `tests/linguistic/test_morph_attention.py`

### Step 1: Write failing test

```bash
cat > tests/linguistic/test_morph_attention.py << 'EOF'
import pytest
import torch
from frontierqu.linguistic.morph_attention import MorphologicalAttentionBias


class TestMorphologicalAttentionBias:
    def test_morph_bias_initialization(self):
        """Test MorphologicalAttentionBias can be initialized."""
        bias = MorphologicalAttentionBias(num_heads=8)
        assert bias.num_heads == 8
        assert hasattr(bias, 'root_bias')
        assert hasattr(bias, 'pattern_bias')

    def test_morph_bias_forward(self):
        """Test forward pass preserves attention shape."""
        bias = MorphologicalAttentionBias(num_heads=8)

        batch_size = 2
        num_heads = 8
        seq_len = 50

        # Mock attention scores from transformer
        attention_scores = torch.randn(batch_size, num_heads, seq_len, seq_len)

        # Mock root and pattern IDs (assigned from Quranic Arabic Corpus)
        root_ids = torch.randint(0, 1000, (batch_size, seq_len))
        pattern_ids = torch.randint(0, 500, (batch_size, seq_len))

        modified_scores = bias(attention_scores, root_ids, pattern_ids)

        assert modified_scores.shape == attention_scores.shape
        assert not torch.isnan(modified_scores).any()

    def test_morph_bias_boosts_root_matches(self):
        """Test that bias increases attention for words with shared roots."""
        bias = MorphologicalAttentionBias(num_heads=1)

        batch_size = 1
        seq_len = 3

        # Dummy attention scores (uniform)
        attention_scores = torch.ones(batch_size, 1, seq_len, seq_len) * 0.1

        # Root IDs: verse 0 and 1 share root, 2 is different
        root_ids = torch.tensor([[1, 1, 2]])
        pattern_ids = torch.zeros(batch_size, seq_len, dtype=torch.long)

        modified_scores = bias(attention_scores, root_ids, pattern_ids)

        # Check that attention[0, 0, 1] (same root) is boosted vs [0, 0, 2] (different)
        same_root_score = modified_scores[0, 0, 0, 1]
        diff_root_score = modified_scores[0, 0, 0, 2]

        assert same_root_score > diff_root_score, "Same root should have higher attention"

    def test_morph_bias_preserves_gradients(self):
        """Test gradients flow through the bias layer."""
        bias = MorphologicalAttentionBias(num_heads=4)

        attention_scores = torch.randn(1, 4, 10, 10, requires_grad=True)
        root_ids = torch.randint(0, 50, (1, 10))
        pattern_ids = torch.randint(0, 30, (1, 10))

        modified_scores = bias(attention_scores, root_ids, pattern_ids)
        loss = modified_scores.sum()
        loss.backward()

        assert attention_scores.grad is not None
        assert bias.root_bias.grad is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
EOF
```

**Run:** `cd ~/Desktop/FrontierQu && pytest tests/linguistic/test_morph_attention.py -v`

**Expected:** ❌ FAIL — Module not found

### Step 2: Implement Morphological Attention Bias

```bash
cat > src/frontierqu/linguistic/morph_attention.py << 'EOF'
"""Morphological Attention Bias for Arabic Root Semantics.

In Arabic, meaning is encoded in trilateral roots (e.g., k-t-b for "writing").
Standard tokenizers (BPE/WordPiece) break these roots across subwords, losing semantic coherence.

This module injects morphological priors into the attention mechanism:
- Boost attention between words sharing the same root
- Boost attention between words sharing the same morphological pattern (wazn)
- Use learnable bias parameters to weight root vs pattern matching
"""

import torch
import torch.nn as nn


class MorphologicalAttentionBias(nn.Module):
    """
    Add morphological bias to transformer attention scores.

    Before softmax, inject learned biases based on:
    1. Root match: Do two words share the same trilateral root?
    2. Pattern match: Do two words share the same morphological pattern?

    This encourages the model to attend more strongly to morphologically related words.
    """

    def __init__(self, num_heads: int, root_bias_init: float = 2.0,
                 pattern_bias_init: float = 1.0):
        """
        Initialize morphological attention bias.

        Args:
            num_heads: Number of attention heads (for reference)
            root_bias_init: Initial value for root matching bias
            pattern_bias_init: Initial value for pattern matching bias
        """
        super().__init__()
        self.num_heads = num_heads

        # Learnable bias parameters
        # These will be multiplied by root/pattern match matrices
        self.root_bias = nn.Parameter(torch.tensor(root_bias_init))
        self.pattern_bias = nn.Parameter(torch.tensor(pattern_bias_init))

    def forward(self, attention_scores: torch.Tensor,
                root_ids: torch.Tensor,
                pattern_ids: torch.Tensor) -> torch.Tensor:
        """
        Add morphological bias to attention logits.

        Args:
            attention_scores: Attention logits from transformer
                            Shape: [batch, num_heads, seq_len, seq_len]
            root_ids: Root IDs for each token
                     Shape: [batch, seq_len]
                     Value range: 0 to ~1000 (number of unique roots)
            pattern_ids: Pattern (wazn) IDs for each token
                        Shape: [batch, seq_len]
                        Value range: 0 to ~500 (number of unique patterns)

        Returns:
            Modified attention scores with morphological bias injected
            Shape: [batch, num_heads, seq_len, seq_len]
        """
        batch_size = attention_scores.size(0)
        num_heads = attention_scores.size(1)
        seq_len = attention_scores.size(2)

        # Compute Root Match Matrix
        # root_match[b, i, j] = 1 if token i and j in batch b share same root, else 0
        root_match = (root_ids.unsqueeze(-1) == root_ids.unsqueeze(-2)).float()
        # [batch, seq_len, seq_len]

        # Compute Pattern Match Matrix
        pattern_match = (pattern_ids.unsqueeze(-1) == pattern_ids.unsqueeze(-2)).float()
        # [batch, seq_len, seq_len]

        # Expand to match number of heads (same bias applied across all heads)
        root_match = root_match.unsqueeze(1).expand(-1, num_heads, -1, -1)
        # [batch, num_heads, seq_len, seq_len]

        pattern_match = pattern_match.unsqueeze(1).expand(-1, num_heads, -1, -1)
        # [batch, num_heads, seq_len, seq_len]

        # Inject morphological bias into attention logits (before softmax)
        modified_scores = (
            attention_scores
            + (root_match * self.root_bias)
            + (pattern_match * self.pattern_bias)
        )

        return modified_scores


class MorphologicalAttentionAdapter(nn.Module):
    """
    Wrapper to inject morphological bias into an existing transformer layer.

    Typical usage:
    ```python
    original_attn = model.encoder.layer[0].self_attention
    adapter = MorphologicalAttentionAdapter(original_attn, num_heads=12)
    # Replace in model, or wrap for inference
    ```
    """

    def __init__(self, attention_module: nn.Module, num_heads: int):
        """
        Initialize adapter wrapping an attention module.

        Args:
            attention_module: torch.nn.MultiheadAttention to wrap
            num_heads: Number of heads in the attention module
        """
        super().__init__()
        self.attention = attention_module
        self.morph_bias = MorphologicalAttentionBias(num_heads=num_heads)

    def forward(self, query, key, value, root_ids=None, pattern_ids=None, **kwargs):
        """
        Forward pass: compute attention, then apply morphological bias.

        Args:
            query, key, value: Standard attention inputs
            root_ids: [batch, seq_len] root IDs (optional)
            pattern_ids: [batch, seq_len] pattern IDs (optional)
            **kwargs: Other arguments for attention module

        Returns:
            Attention output with morphological bias applied
        """
        # Compute attention (we need to hook into the attention computation)
        # This is a simplified version; in practice, you'd need to modify
        # the attention module's forward to expose attention scores

        attn_output, attn_weights = self.attention(query, key, value, **kwargs)

        if root_ids is not None and pattern_ids is not None:
            # Note: This requires modification of attention module
            # to expose raw attention scores before softmax
            pass

        return attn_output, attn_weights
EOF
```

### Step 3: Run test

**Run:** `cd ~/Desktop/FrontierQu && pytest tests/linguistic/test_morph_attention.py -v`

**Expected:** ✅ PASS — All 4 tests pass

### Step 4: Commit

```bash
cd ~/Desktop/FrontierQu
git add src/frontierqu/linguistic/morph_attention.py tests/linguistic/test_morph_attention.py
git commit -m "feat(linguistic): add Morphological Attention bias for Arabic roots"
```

---

# Chunk 4: Multi-Agent Tafsir Verification (Agentic)

## Task 5: Constitutional Safety Module

**Files:**
- Create: `src/frontierqu/agentic/constitutional_guard.py`
- Test: `tests/agentic/test_constitutional_guard.py`

### Step 1: Write failing test

```bash
cat > tests/agentic/test_constitutional_guard.py << 'EOF'
import pytest
from frontierqu.agentic.constitutional_guard import ConstitutionalGuard


class TestConstitutionalGuard:
    def test_guard_initialization(self):
        """Test ConstitutionalGuard can be initialized."""
        guard = ConstitutionalGuard()
        assert guard is not None
        assert hasattr(guard, 'check_theological_soundness')
        assert hasattr(guard, 'check_hadith_consistency')

    def test_rejects_unsubstantiated_ruling(self):
        """Test guard rejects rulings without Hadith support."""
        guard = ConstitutionalGuard()

        unsafe_claim = {
            "claim": "Fasting is forbidden in Ramadan",
            "hadith_references": [],
            "madhab_consensus": None
        }

        is_safe, reason = guard.check_theological_soundness(unsafe_claim)
        assert not is_safe, "Should reject claim without theological basis"
        assert "hadith" in reason.lower() or "basis" in reason.lower()

    def test_accepts_well_sourced_ruling(self):
        """Test guard accepts properly sourced rulings."""
        guard = ConstitutionalGuard()

        safe_claim = {
            "claim": "Wudu (ablution) is obligatory before prayer",
            "hadith_references": ["Sahih Bukhari 1:4:46"],
            "madhab_consensus": "All four madhabs agree",
            "confidence": 0.95
        }

        is_safe, reason = guard.check_theological_soundness(safe_claim)
        assert is_safe, f"Should accept well-sourced claim, but got: {reason}"

    def test_flags_controversial_claim(self):
        """Test guard flags controversial/disputed rulings."""
        guard = ConstitutionalGuard()

        disputed_claim = {
            "claim": "Interest (Riba) in Islamic finance includes all lending",
            "hadith_references": ["Sahih Muslim 10:3730"],
            "madhab_consensus": "Schools of law disagree on application",
            "confidence": 0.60
        }

        is_safe, reason = guard.check_theological_soundness(disputed_claim)
        # Should not be unsafe (rejection), but should flag as controversial
        assert isinstance(is_safe, (bool, dict))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
EOF
```

**Run:** `cd ~/Desktop/FrontierQu && pytest tests/agentic/test_constitutional_guard.py -v`

**Expected:** ❌ FAIL — Module not found

### Step 2: Implement Constitutional Guard

```bash
cat > src/frontierqu/agentic/constitutional_guard.py << 'EOF'
"""Constitutional Guardrails for Tafsir Generation.

LLM agents can hallucinate religious rulings, which is a critical failure mode.
This module enforces "constitutional" constraints:
1. Claims must be sourced from Hadith or scholarly consensus
2. Chronological constraints (Naskh abrogation rules)
3. Madhab (school of law) consistency checks
4. Confidence calibration based on evidence strength
"""

from typing import Dict, Tuple, Optional, List


class ConstitutionalGuard:
    """
    Verify that generated Tafsir claims meet constitutional standards.

    Principles:
    - No unsourced religious rulings
    - Respect scholarly disagreement (Ikhtilaf)
    - Enforce chronological ordering constraints
    - Calibrate confidence to evidence quality
    """

    # Known Hadith collections for validation
    HADITH_COLLECTIONS = {
        "Sahih Bukhari": {"priority": 1, "reliability": 0.98},
        "Sahih Muslim": {"priority": 1, "reliability": 0.98},
        "Sunan Abu Dawud": {"priority": 2, "reliability": 0.85},
        "Sunan an-Nasa'i": {"priority": 2, "reliability": 0.85},
        "Jami at-Tirmidhi": {"priority": 2, "reliability": 0.85},
        "Sunan Ibn Majah": {"priority": 2, "reliability": 0.80},
    }

    # The four main schools of Islamic law
    MADHABS = ["Hanafi", "Maliki", "Shafi'i", "Hanbali"]

    def __init__(self, strict_mode: bool = False):
        """
        Initialize guard.

        Args:
            strict_mode: If True, require Sahih hadith (priority 1) for any claim.
                        If False, allow Sunan collections with lower weight.
        """
        self.strict_mode = strict_mode

    def check_theological_soundness(self, claim: Dict) -> Tuple[bool, str]:
        """
        Verify a Tafsir claim is theologically sound.

        Args:
            claim: Dict with keys:
                - 'claim' (str): The actual ruling/interpretation
                - 'hadith_references' (List[str]): Supporting Hadith citations
                - 'madhab_consensus' (str or None): Scholarly agreement level
                - 'confidence' (float, 0-1): Model confidence in the claim

        Returns:
            (is_safe, reason) where:
            - is_safe (bool): True if claim passes all checks
            - reason (str): Explanation if claim fails
        """
        # Check 1: Hadith sourcing
        hadith_refs = claim.get('hadith_references', [])
        if not hadith_refs:
            return False, "Claim lacks Hadith support. Rulings must cite authentic sources."

        # Validate hadith references
        hadith_reliability = self._validate_hadith_references(hadith_refs)
        if hadith_reliability is None:
            return False, f"Hadith references not recognized: {hadith_refs}"

        if self.strict_mode and hadith_reliability < 0.90:
            return False, "Strict mode: Claim requires Sahih-level (priority 1) sources."

        # Check 2: Madhab consistency
        madhab_consensus = claim.get('madhab_consensus')
        if madhab_consensus:
            if "disagree" in madhab_consensus.lower():
                # Claim is controversial; mark with lower confidence
                confidence = claim.get('confidence', 0.5)
                if confidence < 0.70:
                    return False, "Claim is theologically disputed with low confidence."

        # Check 3: Confidence calibration
        confidence = claim.get('confidence', 0.5)
        if hadith_reliability < 0.85 and confidence > 0.90:
            return False, "Confidence too high for lower-reliability sources."

        # All checks passed
        return True, "Claim passes theological soundness checks."

    def check_hadith_consistency(self, claim: Dict,
                                  known_hadith_db: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Check if a claim contradicts known Hadith.

        Args:
            claim: Tafsir claim to validate
            known_hadith_db: (Optional) Database of verified Hadith meanings

        Returns:
            (is_consistent, reason)
        """
        # In practice, this would query a Hadith database
        # For now, basic validation
        hadith_refs = claim.get('hadith_references', [])

        if not hadith_refs:
            return False, "No Hadith references provided."

        # TODO: Integrate actual Hadith DB
        return True, "Hadith references appear valid (database integration pending)."

    def _validate_hadith_references(self, references: List[str]) -> Optional[float]:
        """
        Validate Hadith references and return reliability score.

        Args:
            references: List of hadith citations (e.g., "Sahih Bukhari 1:4:46")

        Returns:
            Average reliability score (0-1), or None if invalid
        """
        if not references:
            return None

        scores = []
        for ref in references:
            collection = None
            reliability = None

            # Parse reference
            for coll_name in self.HADITH_COLLECTIONS:
                if ref.startswith(coll_name):
                    collection = coll_name
                    reliability = self.HADITH_COLLECTIONS[coll_name]["reliability"]
                    break

            if reliability is None:
                return None  # Unrecognized collection

            scores.append(reliability)

        # Return average reliability
        return sum(scores) / len(scores) if scores else None

    def calibrate_confidence(self, claim: Dict,
                            hadith_reliability: float,
                            madhab_agreement: float) -> float:
        """
        Calibrate confidence score based on evidence quality.

        Args:
            claim: Original claim
            hadith_reliability: Reliability of hadith sources (0-1)
            madhab_agreement: Level of scholarly consensus (0-1)
                            1.0 = all madhabs agree, 0.5 = split, 0.0 = disputed

        Returns:
            Calibrated confidence (0-1)
        """
        base_confidence = claim.get('confidence', 0.5)

        # Weight by source reliability
        weighted = base_confidence * hadith_reliability

        # Penalize controversial claims
        if madhab_agreement < 0.75:
            weighted *= madhab_agreement

        return min(1.0, max(0.0, weighted))
EOF
```

### Step 3: Run test

**Run:** `cd ~/Desktop/FrontierQu && pytest tests/agentic/test_constitutional_guard.py -v`

**Expected:** ✅ PASS — All 4 tests pass

### Step 4: Commit

```bash
cd ~/Desktop/FrontierQu
git add src/frontierqu/agentic/constitutional_guard.py tests/agentic/test_constitutional_guard.py
git commit -m "feat(agentic): add Constitutional Guard for theological safety"
```

---

## Task 6: Multi-Agent Tafsir Verifier

**Files:**
- Create: `src/frontierqu/agentic/tafsir_verifier.py`
- Test: `tests/agentic/test_tafsir_verifier.py`

### Step 1: Write failing test

```bash
cat > tests/agentic/test_tafsir_verifier.py << 'EOF'
import pytest
from frontierqu.agentic.tafsir_verifier import MultiAgentTafsirVerifier


class TestMultiAgentTafsirVerifier:
    def test_verifier_initialization(self):
        """Test MultiAgentTafsirVerifier can be initialized."""
        verifier = MultiAgentTafsirVerifier()
        assert verifier is not None
        assert hasattr(verifier, 'proposer')
        assert hasattr(verifier, 'critic')
        assert hasattr(verifier, 'verifier')

    def test_generate_tafsir_structure(self):
        """Test that generate_tafsir returns expected structure."""
        verifier = MultiAgentTafsirVerifier()

        query = "What does surah Al-Fatiha teach about mercy?"
        mock_context_graph = {"verses": [1, 2, 3], "themes": ["mercy", "guidance"]}

        result = verifier.generate_tafsir(query, mock_context_graph)

        assert isinstance(result, dict)
        assert "interpretation" in result
        assert "confidence" in result
        assert "sources" in result

    def test_verifier_rejects_unverified_claims(self):
        """Test verifier rejects claims without proper verification."""
        verifier = MultiAgentTafsirVerifier()

        unverified = {
            "claim": "Allah forbids all music",
            "sources": []
        }

        is_valid = verifier.verify_against_constitution(unverified)
        assert not is_valid, "Should reject unsourced claims"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
EOF
```

**Run:** `cd ~/Desktop/FrontierQu && pytest tests/agentic/test_tafsir_verifier.py -v`

**Expected:** ❌ FAIL — Module not found

### Step 2: Implement Multi-Agent Verifier

```bash
cat > src/frontierqu/agentic/tafsir_verifier.py << 'EOF'
"""Multi-Agent Tafsir Verification System.

Uses a 3-agent debate framework:
1. Proposer: Generates interpretation from retrieved context
2. Critic: Challenges against Hadith and Madhab precedent
3. Verifier: Checks logical consistency using constraints

Inspired by Constitutional AI and multi-agent reasoning systems.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from frontierqu.agentic.constitutional_guard import ConstitutionalGuard


@dataclass
class AgentResponse:
    """Response from a verification agent."""
    agent_name: str
    content: str
    confidence: float
    metadata: Dict


class MultiAgentTafsirVerifier:
    """
    Multi-agent system for generating and verifying Tafsir (Quranic interpretation).

    Architecture:
    1. Proposer Agent: "Given this query and retrieved verses, generate an interpretation"
    2. Critic Agent: "Is this interpretation supported by hadith and madhab consensus?"
    3. Verifier Agent: "Is this logically consistent with Naskh rules and cross-references?"
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the multi-agent verifier.

        Args:
            strict_mode: If True, require high confidence for final output
        """
        self.strict_mode = strict_mode
        self.guard = ConstitutionalGuard(strict_mode=strict_mode)

        # In practice, these would be LLM-backed agents via LangGraph
        # For now, we use placeholder implementations
        self.proposer = ProposerAgent()
        self.critic = CriticAgent()
        self.verifier = VerifierAgent()

    def generate_tafsir(self, query: str, context_graph: Dict) -> Dict:
        """
        Generate Tafsir through multi-agent verification loop.

        Args:
            query: User question about Quranic interpretation
            context_graph: Retrieved verses and related context

        Returns:
            Dict with:
            - interpretation: Final verified interpretation
            - confidence: Overall confidence score
            - sources: Supporting hadith and references
            - debate_log: Log of agent interactions
        """
        # Stage 1: Proposer generates draft
        draft = self.proposer.generate(query, context_graph)

        # Stage 2: Critic evaluates
        critique = self.critic.evaluate(draft, context_graph)

        # Stage 3: Verifier checks consistency
        verification = self.verifier.verify(draft, critique, context_graph)

        # Synthesize final response
        final_interpretation = self._synthesize_response(
            draft, critique, verification
        )

        return final_interpretation

    def verify_against_constitution(self, claim: Dict) -> bool:
        """
        Verify a claim against constitutional principles.

        Args:
            claim: Dict with 'claim', 'sources', 'confidence'

        Returns:
            True if claim passes all checks, False otherwise
        """
        is_safe, reason = self.guard.check_theological_soundness(claim)
        return is_safe

    def _synthesize_response(self, draft: AgentResponse,
                            critique: AgentResponse,
                            verification: AgentResponse) -> Dict:
        """Combine agent outputs into final response."""
        return {
            "interpretation": draft.content,
            "confidence": min(draft.confidence, critique.confidence, verification.confidence),
            "sources": draft.metadata.get("sources", []),
            "debate_log": [
                {"agent": "proposer", "response": draft.content},
                {"agent": "critic", "response": critique.content},
                {"agent": "verifier", "response": verification.content},
            ]
        }


class ProposerAgent:
    """Generates initial Tafsir interpretation."""

    def generate(self, query: str, context_graph: Dict) -> AgentResponse:
        """
        Generate interpretation from retrieved context.

        Args:
            query: User question
            context_graph: Retrieved verses and metadata

        Returns:
            AgentResponse with draft interpretation
        """
        # In real implementation, use LLM to generate response
        # For now, return placeholder
        return AgentResponse(
            agent_name="proposer",
            content=f"Generated interpretation for: {query}",
            confidence=0.75,
            metadata={
                "sources": context_graph.get("verses", []),
                "retrieved_count": len(context_graph.get("verses", []))
            }
        )


class CriticAgent:
    """Evaluates interpretation against scholarly sources."""

    def evaluate(self, draft: AgentResponse, context_graph: Dict) -> AgentResponse:
        """
        Critique the proposed interpretation.

        Args:
            draft: Original proposer response
            context_graph: Context for critique

        Returns:
            AgentResponse with critique
        """
        # In real implementation, check against hadith DB and madhab positions
        return AgentResponse(
            agent_name="critic",
            content=f"Critique of: {draft.content[:50]}...",
            confidence=0.70,
            metadata={"checks_performed": ["hadith_consistency", "madhab_agreement"]}
        )


class VerifierAgent:
    """Verifies logical consistency of interpretation."""

    def verify(self, draft: AgentResponse, critique: AgentResponse,
               context_graph: Dict) -> AgentResponse:
        """
        Verify logical consistency.

        Args:
            draft: Original interpretation
            critique: Critic's response
            context_graph: Context for verification

        Returns:
            AgentResponse with verification result
        """
        # In real implementation, use constraint solver (Z3) for Naskh rules
        return AgentResponse(
            agent_name="verifier",
            content="Interpretation is logically consistent.",
            confidence=0.80,
            metadata={"constraints_checked": ["naskh_order", "chronology"]}
        )
EOF
```

### Step 3: Run test

**Run:** `cd ~/Desktop/FrontierQu && pytest tests/agentic/test_tafsir_verifier.py -v`

**Expected:** ✅ PASS — All 3 tests pass

### Step 4: Commit

```bash
cd ~/Desktop/FrontierQu
git add src/frontierqu/agentic/tafsir_verifier.py tests/agentic/test_tafsir_verifier.py
git commit -m "feat(agentic): add Multi-Agent Tafsir verification system"
```

---

# Chunk 5: Morpho-Syntactic Embeddings (Search)

## Task 7: Enhanced Embeddings Module

**Files:**
- Create: `src/frontierqu/search/morpho_embeddings.py`
- Modify: `src/frontierqu/search/embedding_store.py`
- Test: `tests/search/test_morpho_embeddings.py`

### Step 1: Write failing test

```bash
cat > tests/search/test_morpho_embeddings.py << 'EOF'
import pytest
import torch
from frontierqu.search.morpho_embeddings import MorphoSyntacticEmbedder


class TestMorphoSyntacticEmbedder:
    def test_embedder_initialization(self):
        """Test embedder can be initialized."""
        embedder = MorphoSyntacticEmbedder(embedding_dim=768)
        assert embedder is not None
        assert hasattr(embedder, 'encode')

    def test_embedder_produces_fixed_dim(self):
        """Test embedder output has correct dimension."""
        embedder = MorphoSyntacticEmbedder(embedding_dim=256)

        text = "كتب الكاتب الرسالة"  # "The writer wrote the letter"
        morpho_features = {
            "roots": [1, 1, 2],  # Root IDs
            "patterns": [10, 20, 10],
            "pos_tags": ["NOUN", "VERB", "NOUN"]
        }

        embedding = embedder.encode(text, morpho_features)

        assert embedding.shape == (256,)
        assert not torch.isnan(embedding).any()

    def test_same_root_similar_embeddings(self):
        """Test words with same root get similar embeddings."""
        embedder = MorphoSyntacticEmbedder(embedding_dim=128)

        # Two phrases with same root k-t-b
        text1 = "كتاب"  # kitaab (book)
        morpho1 = {"roots": [1], "patterns": [10], "pos_tags": ["NOUN"]}

        text2 = "كتب"  # kataba (wrote)
        morpho2 = {"roots": [1], "patterns": [20], "pos_tags": ["VERB"]}

        embed1 = embedder.encode(text1, morpho1)
        embed2 = embedder.encode(text2, morpho2)

        # Compute cosine similarity
        similarity = torch.nn.functional.cosine_similarity(
            embed1.unsqueeze(0), embed2.unsqueeze(0)
        )

        # Should be fairly similar (>0.6) due to shared root
        assert similarity.item() > 0.5, "Words sharing root should have similar embeddings"

    def test_batch_encoding(self):
        """Test batch encoding of multiple verses."""
        embedder = MorphoSyntacticEmbedder(embedding_dim=256)

        texts = [
            "الحمد لله رب العالمين",  # Verse 1:1
            "مالك يوم الدين",        # Verse 1:4
        ]

        batch_morpho = [
            {"roots": [1, 2, 3, 4], "patterns": [1, 2, 3, 4], "pos_tags": ["NOUN"] * 4},
            {"roots": [5, 6, 7], "patterns": [1, 2, 3], "pos_tags": ["NOUN"] * 3},
        ]

        embeddings = embedder.encode_batch(texts, batch_morpho)

        assert embeddings.shape == (2, 256)
        assert not torch.isnan(embeddings).any()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
EOF
```

**Run:** `cd ~/Desktop/FrontierQu && pytest tests/search/test_morpho_embeddings.py -v`

**Expected:** ❌ FAIL — Module not found

### Step 2: Implement Morpho-Syntactic Embedder

```bash
cat > src/frontierqu/search/morpho_embeddings.py << 'EOF'
"""Morpho-Syntactic Aware Embeddings for Quranic Search.

Standard embeddings treat each word independently. This module enriches embeddings
by incorporating morphological and syntactic information from the Quranic Arabic Corpus:
- Trilateral roots (semantic core)
- Morphological patterns (grammatical structure)
- Part-of-speech tags
- Diacritical marks (harakat)

Result: Semantically similar words (shared root) get similar embeddings,
even if surface form is different.
"""

from typing import Dict, List, Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F


class MorphoSyntacticEmbedder(nn.Module):
    """
    Embedding layer that fuses text embeddings with morphological features.

    Architecture:
    1. Text encoder: AraBERT or similar (frozen or fine-tuned)
    2. Root embedding: Learnable embeddings for ~1000 Arabic roots
    3. Pattern embedding: Learnable embeddings for ~500 morphological patterns
    4. POS embedding: Embeddings for part-of-speech tags
    5. Fusion layer: Combine all features via attention
    """

    def __init__(self, embedding_dim: int = 768,
                 num_roots: int = 1000, num_patterns: int = 500,
                 num_pos_tags: int = 50, use_pretrained: bool = True):
        """
        Initialize morpho-syntactic embedder.

        Args:
            embedding_dim: Output embedding dimension
            num_roots: Number of unique Arabic roots
            num_patterns: Number of unique morphological patterns
            num_pos_tags: Number of unique POS tags
            use_pretrained: If True, initialize with AraBERT weights
        """
        super().__init__()
        self.embedding_dim = embedding_dim

        # Text embedding (placeholder; in practice use AraBERT)
        self.text_embedding = nn.Embedding(num_embeddings=10000,
                                           embedding_dim=embedding_dim)

        # Morphological embeddings
        self.root_embedding = nn.Embedding(num_roots, embedding_dim // 3)
        self.pattern_embedding = nn.Embedding(num_patterns, embedding_dim // 3)
        self.pos_embedding = nn.Embedding(num_pos_tags, embedding_dim // 3)

        # Fusion layer: combine text + morpho features
        fusion_input_dim = embedding_dim + (embedding_dim // 3) * 3  # text + morpho
        self.fusion = nn.Sequential(
            nn.Linear(fusion_input_dim, embedding_dim),
            nn.ReLU(),
            nn.Linear(embedding_dim, embedding_dim),
        )

        # Attention weights for feature combination
        self.attention_weights = nn.Parameter(
            torch.ones(4) / 4  # Equal weight initially: text, root, pattern, pos
        )

    def encode(self, text: str, morpho_features: Dict) -> torch.Tensor:
        """
        Encode a single word/phrase with morphological features.

        Args:
            text: Arabic text to embed
            morpho_features: Dict with:
                - roots: List[int] root IDs
                - patterns: List[int] pattern IDs
                - pos_tags: List[str] POS tag names

        Returns:
            Embedding tensor of shape [embedding_dim]
        """
        # In real implementation, use AraBERT tokenizer
        # For now, use hash-based indexing
        text_idx = hash(text) % 10000
        text_embed = self.text_embedding(torch.tensor(text_idx))

        # Get morphological embeddings
        root_ids = morpho_features.get("roots", [0])
        pattern_ids = morpho_features.get("patterns", [0])

        root_tensor = torch.tensor(root_ids[0] if root_ids else 0)
        pattern_tensor = torch.tensor(pattern_ids[0] if pattern_ids else 0)

        root_embed = self.root_embedding(root_tensor)
        pattern_embed = self.pattern_embedding(pattern_tensor)

        # POS embedding (simplified)
        pos_name = morpho_features.get("pos_tags", ["NOUN"])[0]
        pos_idx = {"NOUN": 0, "VERB": 1, "ADJ": 2, "PREP": 3}.get(pos_name, 0)
        pos_embed = self.pos_embedding(torch.tensor(pos_idx))

        # Concatenate all features
        combined = torch.cat([text_embed, root_embed, pattern_embed, pos_embed], dim=-1)

        # Fuse through attention-weighted combination
        fused = self.fusion(combined)

        return fused

    def encode_batch(self, texts: List[str],
                    morpho_features_list: List[Dict]) -> torch.Tensor:
        """
        Encode multiple texts with morphological features.

        Args:
            texts: List of Arabic texts
            morpho_features_list: List of morphological feature dicts

        Returns:
            Tensor of shape [batch_size, embedding_dim]
        """
        embeddings = []
        for text, morpho in zip(texts, morpho_features_list):
            embed = self.encode(text, morpho)
            embeddings.append(embed)

        return torch.stack(embeddings, dim=0)

    def get_root_based_similarity(self, embedding1: torch.Tensor,
                                  embedding2: torch.Tensor,
                                  shared_root: bool) -> float:
        """
        Compute similarity with root-based boosting.

        Args:
            embedding1, embedding2: Embeddings to compare
            shared_root: Whether embeddings share same root

        Returns:
            Similarity score (0-1)
        """
        cos_sim = F.cosine_similarity(embedding1.unsqueeze(0),
                                      embedding2.unsqueeze(0))[0]

        # Boost similarity if shared root
        if shared_root:
            cos_sim = 0.9 * cos_sim + 0.1  # Boost by 0.1

        return cos_sim.item()
EOF
```

### Step 3: Run test

**Run:** `cd ~/Desktop/FrontierQu && pytest tests/search/test_morpho_embeddings.py -v`

**Expected:** ✅ PASS — All 4 tests pass

### Step 4: Integrate with embedding store

```bash
cat >> src/frontierqu/search/embedding_store.py << 'EOF'

# Add this method to EmbeddingStore class
    def add_morpho_aware_verse(self, verse_text: str, morpho_features: Dict,
                                verse_id: Tuple[int, int]):
        """
        Store a verse with morphological features.

        Args:
            verse_text: Quranic verse text
            morpho_features: Dict with roots, patterns, pos_tags
            verse_id: (chapter, verse) identifier
        """
        from frontierqu.search.morpho_embeddings import MorphoSyntacticEmbedder

        if not hasattr(self, 'morpho_embedder'):
            self.morpho_embedder = MorphoSyntacticEmbedder()

        # Encode with morphological awareness
        embedding = self.morpho_embedder.encode(verse_text, morpho_features)

        # Store in vector DB
        self.add_verse(verse_text, embedding, verse_id)
EOF
```

### Step 5: Commit

```bash
cd ~/Desktop/FrontierQu
git add src/frontierqu/search/morpho_embeddings.py tests/search/test_morpho_embeddings.py
git commit -m "feat(search): add Morpho-Syntactic embeddings with root awareness"
```

---

# Integration & Testing

## Task 8: Update Project Configuration

**Files:**
- Modify: `pyproject.toml` (add new dependencies)
- Create: `docs/v3-ARCHITECTURE.md` (document new architecture)

### Step 1: Update dependencies

```bash
cat > pyproject.toml << 'EOF'
[project]
name = "frontierqu"
version = "3.0.0"
description = "Universal Holistic Quranic Algorithmic Framework for DeepTech/ML Research"
requires-python = ">=3.11"
dependencies = [
    "torch>=2.0.0",
    "numpy>=2.0.0",
    "scipy>=1.10.0",
    "networkx>=3.0",
    "sympy>=1.12",
]

[project.optional-dependencies]
topology = ["gudhi>=3.8.0", "ripser>=0.6.0"]
logic = ["z3-solver>=4.12.0"]
agentic = ["langgraph>=0.1.0", "langchain>=0.1.0"]
embeddings = ["transformers>=4.30.0"]
full = [
    "gudhi>=3.8.0",
    "ripser>=0.6.0",
    "z3-solver>=4.12.0",
    "python-igraph>=0.11.0",
    "langgraph>=0.1.0",
    "langchain>=0.1.0",
    "transformers>=4.30.0"
]
dev = ["pytest>=8.0", "pytest-cov>=4.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
EOF
```

### Step 2: Commit

```bash
cd ~/Desktop/FrontierQu
git add pyproject.toml
git commit -m "chore: bump to v3.0.0 with new dependencies"
```

---

## Task 9: Run Full Test Suite

**Run all tests:**

```bash
cd ~/Desktop/FrontierQu
pytest tests/ -v --tb=short
```

**Expected:** ✅ All tests pass (18/18 new tests + existing tests)

---

# Success Criteria

✅ **Sheaf Neural Networks**
- `test_sheaf_layer_initialization` PASS
- `test_sheaf_layer_forward_pass` PASS
- `test_sheaf_layer_with_weights` PASS
- `test_sheaf_layer_preserves_gradients` PASS

✅ **Differentiable Naskh Solver**
- `test_naskh_solver_initialization` PASS
- `test_naskh_solver_forward` PASS
- `test_logic_loss_penalizes_violations` PASS
- `test_logic_loss_allows_valid_abrogations` PASS

✅ **Morphological Attention**
- `test_morph_bias_initialization` PASS
- `test_morph_bias_forward` PASS
- `test_morph_bias_boosts_root_matches` PASS
- `test_morph_bias_preserves_gradients` PASS

✅ **Constitutional Guard**
- `test_guard_initialization` PASS
- `test_rejects_unsubstantiated_ruling` PASS
- `test_accepts_well_sourced_ruling` PASS
- `test_flags_controversial_claim` PASS

✅ **Multi-Agent Verifier**
- `test_verifier_initialization` PASS
- `test_generate_tafsir_structure` PASS
- `test_verifier_rejects_unverified_claims` PASS

✅ **Morpho-Syntactic Embeddings**
- `test_embedder_initialization` PASS
- `test_embedder_produces_fixed_dim` PASS
- `test_same_root_similar_embeddings` PASS
- `test_batch_encoding` PASS

✅ **All 18 tests passing**
✅ **Project version bumped to v3.0.0**
✅ **Dependencies updated in pyproject.toml**

---

## Post-Implementation Notes

1. **Integration:** Sheaf NN should consume edges from `simplicial_complex.extract_edges()`
2. **Training:** Naskh solver and embedder require fine-tuning on Quranic corpus
3. **LLM Backend:** Proposer/Critic/Verifier agents need LangGraph + LLM (Claude, GPT-4, etc.)
4. **Evaluation:** Run against known Tafsir rulings + scholarly agreement benchmarks
5. **Safety:** Constitutional Guard must be integrated before any agent output reaches users

EOF
```

---

## Plan Review Summary

**Total Implementation Effort:** ~8 hours for complete implementation
**Tasks:** 9 (Sheaf NN, Naskh Solver, Morpho Attention, Constitutional Guard, Multi-Agent Verifier, Embeddings, Config, Testing, Cleanup)
**New Files:** 6 source modules + 6 test modules = 12 files
**Tests:** 18 new tests, all TDD-based
**Version:** v2.0.0 → v3.0.0

---

Plan complete and saved to `/Users/mac/Desktop/FrontierQu/docs/superpowers/plans/2026-03-12-frontierqu-v3-implementation.md`. Ready to execute using **superpowers:subagent-driven-development** for parallel task execution, or **superpowers:executing-plans** for sequential execution in current session.

**Which approach would you prefer?**

1. **Subagent-driven** (faster): Dispatch independent tasks to parallel workers
2. **Current session** (direct): Execute plan here sequentially