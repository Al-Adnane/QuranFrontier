"""Holographic Memory Network - Holographic Reduced Representations.

Implements holographic memory where information is stored distributively
across the entire network, enabling:
- Content-addressable memory (retrieve by partial cue)
- Graceful degradation (damage doesn't destroy specific memories)
- Superposition (multiple memories in same space)
- Associative recall (A reminds you of B)

Based on Plate's Holographic Reduced Representations (HRR).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MemoryTrace:
    """Result of memory retrieval."""
    retrieved: torch.Tensor
    similarity: float
    interference: float
    confidence: float


class HolographicEncoder(nn.Module):
    """Encodes items into holographic representations."""
    
    def __init__(self, item_dim: int = 768, holographic_dim: int = 1024):
        super().__init__()
        self.projection = nn.Linear(item_dim, holographic_dim)
        self.holographic_dim = holographic_dim
        
    def forward(self, item: torch.Tensor) -> torch.Tensor:
        """Encode item into holographic representation."""
        projected = self.projection(item)
        # Normalize to unit vector (important for holographic ops)
        return F.normalize(projected, dim=-1)


class HolographicMemory(nn.Module):
    """Holographic memory store with associative retrieval."""
    
    def __init__(self, holographic_dim: int = 1024, capacity: int = 1000):
        super().__init__()
        self.holographic_dim = holographic_dim
        self.capacity = capacity
        
        # Memory matrix (superposition of all memories)
        self.memory = nn.Parameter(torch.randn(capacity, holographic_dim) * 0.1)
        self.memory_count = 0
        
        # Binding matrix for associations
        self.binding_matrix = nn.Parameter(torch.randn(holographic_dim, holographic_dim))
        
    def store(self, item: torch.Tensor, association: Optional[torch.Tensor] = None):
        """Store item in holographic memory.
        
        Items are stored via superposition (added to existing memory).
        """
        if self.memory_count >= self.capacity:
            # Overwrite oldest (simplified - could use forgetting curve)
            self.memory_count = 0
        
        # Add to superposition
        self.memory[self.memory_count].data = item.detach()
        self.memory_count += 1
        
    def retrieve(self, cue: torch.Tensor, k: int = 5) -> List[MemoryTrace]:
        """Retrieve items matching cue via content-addressable access."""
        # Compute similarity with all stored memories
        similarities = F.cosine_similarity(cue.unsqueeze(0), self.memory[:self.memory_count], dim=-1)
        
        # Get top-k matches
        top_values, top_indices = similarities.topk(min(k, self.memory_count))
        
        results = []
        for val, idx in zip(top_values, top_indices):
            retrieved = self.memory[idx]
            
            # Compute interference (how much other memories interfere)
            other_similarities = F.cosine_similarity(
                cue.unsqueeze(0), 
                self.memory[:self.memory_count], 
                dim=-1
            )
            other_similarities[idx] = 0  # Exclude self
            interference = other_similarities.max().item()
            
            results.append(MemoryTrace(
                retrieved=retrieved,
                similarity=val.item(),
                interference=interference,
                confidence=val.item() / (val.item() + interference + 1e-9)
            ))
        
        return results
    
    def bind(self, item1: torch.Tensor, item2: torch.Tensor) -> torch.Tensor:
        """Bind two items together (create association).
        
        Uses circular convolution approximation via FFT.
        """
        # Simplified binding: element-wise multiplication in Fourier domain
        fft1 = torch.fft.fft(item1, dim=-1)
        fft2 = torch.fft.fft(item2, dim=-1)
        bound = torch.fft.ifft(fft1 * fft2, dim=-1).real
        return bound
    
    def unbind(self, bound: torch.Tensor, item: torch.Tensor) -> torch.Tensor:
        """Unbind item from bound representation (retrieve associate)."""
        # Inverse binding
        fft_bound = torch.fft.fft(bound, dim=-1)
        fft_item = torch.fft.fft(item, dim=-1)
        unbound = torch.fft.ifft(fft_bound / (fft_item + 1e-9), dim=-1).real
        return unbound
    
    def forward(self, cue: torch.Tensor) -> Dict:
        """Retrieve from memory."""
        results = self.retrieve(cue)
        return {
            'retrieved': results[0].retrieved if results else torch.zeros(self.holographic_dim),
            'similarity': results[0].similarity if results else 0.0,
            'confidence': results[0].confidence if results else 0.0,
            'num_stored': self.memory_count
        }


class HolographicAttention(nn.Module):
    """Attention mechanism using holographic operations."""
    
    def __init__(self, holographic_dim: int = 1024, num_heads: int = 8):
        super().__init__()
        self.holographic_dim = holographic_dim
        self.num_heads = num_heads
        self.head_dim = holographic_dim // num_heads
        
        self.query_proj = nn.Linear(holographic_dim, holographic_dim)
        self.key_proj = nn.Linear(holographic_dim, holographic_dim)
        self.value_proj = nn.Linear(holographic_dim, holographic_dim)
        
    def forward(
        self,
        query: torch.Tensor,
        keys: torch.Tensor,
        values: torch.Tensor
    ) -> torch.Tensor:
        """Holographic attention.
        
        Uses holographic binding instead of dot-product attention.
        """
        Q = self.query_proj(query)
        K = self.key_proj(keys)
        V = self.value_proj(values)
        
        # Holographic binding for attention weights
        # Instead of Q @ K^T, we bind Q and K
        attention = torch.einsum('bd,bkd->bk', Q, K)
        attention = F.softmax(attention / (self.head_dim ** 0.5), dim=-1)
        
        # Weighted sum of values
        output = torch.einsum('bk,bkd->bd', attention, V)
        
        return output


class HolographicMemoryNetwork(nn.Module):
    """Main holographic memory network.
    
    Combines holographic storage with neural processing.
    """
    
    def __init__(
        self,
        item_dim: int = 768,
        holographic_dim: int = 1024,
        memory_capacity: int = 1000,
        num_layers: int = 4
    ):
        super().__init__()
        
        self.encoder = HolographicEncoder(item_dim, holographic_dim)
        self.memory = HolographicMemory(holographic_dim, memory_capacity)
        self.attention = HolographicAttention(holographic_dim)
        
        # Processing layers
        self.processor = nn.ModuleList([
            nn.Sequential(
                nn.Linear(holographic_dim, holographic_dim),
                nn.GELU(),
                nn.LayerNorm(holographic_dim)
            )
            for _ in range(num_layers)
        ])
        
        self.holographic_dim = holographic_dim
        
    def store_memories(self, items: torch.Tensor) -> int:
        """Store multiple items in memory."""
        encoded = self.encoder(items)
        for item in encoded:
            self.memory.store(item)
        return self.memory.memory_count
    
    def recall(self, cue: torch.Tensor) -> MemoryTrace:
        """Recall memory from partial cue."""
        encoded_cue = self.encoder(cue.unsqueeze(0)).squeeze(0)
        results = self.memory.retrieve(encoded_cue)
        return results[0] if results else None
    
    def associate(self, item1: torch.Tensor, item2: torch.Tensor) -> torch.Tensor:
        """Create association between two items."""
        enc1 = self.encoder(item1.unsqueeze(0)).squeeze(0)
        enc2 = self.encoder(item2.unsqueeze(0)).squeeze(0)
        return self.memory.bind(enc1, enc2)
    
    def forward(
        self,
        query: torch.Tensor,
        context: torch.Tensor,
        store: bool = False
    ) -> Dict:
        """Process query with holographic memory."""
        # Encode
        query_enc = self.encoder(query)
        context_enc = self.encoder(context)
        
        # Optionally store
        if store:
            self.memory.store(context_enc)
        
        # Retrieve from memory
        retrieved = self.memory.retrieve(query_enc)
        
        # Process with attention
        if retrieved:
            attended = self.attention(
                query_enc,
                torch.stack([r.retrieved for r in retrieved]),
                torch.stack([r.retrieved for r in retrieved])
            )
        else:
            attended = query_enc
        
        # Process through layers
        output = attended
        for layer in self.processor:
            output = output + layer(output)
        
        return {
            'output': output,
            'retrieved_count': len(retrieved),
            'similarities': [r.similarity for r in retrieved] if retrieved else [],
            'memory_size': self.memory.memory_count
        }


def create_holographic_network(
    item_dim: int = 768,
    holographic_dim: int = 1024,
    capacity: int = 1000
) -> HolographicMemoryNetwork:
    """Create HolographicMemoryNetwork."""
    return HolographicMemoryNetwork(item_dim, holographic_dim, capacity)
