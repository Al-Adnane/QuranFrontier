"""Dream Network - Generative Latent Space Exploration.

Implements dream-like generative processes inspired by:
- REM sleep memory consolidation
- Latent space interpolation
- Controlled hallucination
- Novel concept synthesis

Architecture:
    Dream Encoder: Maps concepts to latent space
    Dream Weaver: Generates novel combinations
    Reality Checker: Constrains to plausible outputs
    Memory Consolidator: Integrates new concepts

Applications:
- Creative ideation
- Problem solving during "sleep"
- Memory integration
- Novel concept generation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import random


@dataclass
class DreamContent:
    """Generated dream content."""
    latent_trajectory: torch.Tensor
    synthesized_concepts: List[str]
    novelty_score: float
    coherence_score: float
    emotional_valence: float


@dataclass
class MemoryTrace:
    """Memory being consolidated."""
    content: torch.Tensor
    strength: float
    associations: List[int]
    integrated: bool


class DreamEncoder(nn.Module):
    """Encodes experiences/concepts into dream space."""
    
    def __init__(self, input_dim: int = 512, latent_dim: int = 256):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, latent_dim * 2),
            nn.GELU(),
            nn.Linear(latent_dim * 2, latent_dim * 2)  # mu + logvar
        )
        self.latent_dim = latent_dim
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode to latent distribution (VAE-style)."""
        params = self.encoder(x)
        mu = params[:, :self.latent_dim]
        logvar = params[:, self.latent_dim:]
        return mu, logvar
    
    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """Reparameterization trick."""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std


class DreamWeaver(nn.Module):
    """Weaves together dream elements into novel combinations."""
    
    def __init__(self, latent_dim: int = 256):
        super().__init__()
        self.latent_dim = latent_dim
        
        # Concept mixing
        self.mixer = nn.Linear(latent_dim * 2, latent_dim)
        
        # Novelty generator
        self.novelty_net = nn.Sequential(
            nn.Linear(latent_dim, latent_dim),
            nn.Tanh()
        )
        
        # Trajectory generator (for dream narrative)
        self.trajectory_rnn = nn.LSTM(latent_dim, latent_dim, num_layers=2, batch_first=True)
        
    def mix_concepts(
        self,
        concept1: torch.Tensor,
        concept2: torch.Tensor,
        mix_ratio: float = 0.5
    ) -> torch.Tensor:
        """Blend two concepts."""
        combined = torch.cat([concept1, concept2], dim=-1)
        mixed = self.mixer(combined)
        return (1 - mix_ratio) * concept1 + mix_ratio * concept2 + mixed * 0.1
    
    def generate_novelty(self, base_concept: torch.Tensor) -> torch.Tensor:
        """Generate novel variation of concept."""
        novelty = self.novelty_net(base_concept)
        return base_concept + novelty * 0.3
    
    def generate_trajectory(
        self,
        start: torch.Tensor,
        length: int = 10
    ) -> torch.Tensor:
        """Generate dream narrative trajectory."""
        # Ensure 3D input for LSTM: (batch, seq, dim)
        if start.dim() == 1:
            start = start.unsqueeze(0)  # (1, dim)
        if start.dim() == 2:
            start = start.unsqueeze(1)  # (batch, 1, dim)
        
        batch_size = start.size(0)
        hidden_dim = self.latent_dim
        
        # Initialize RNN with correct dimensions
        h0 = torch.zeros(2, batch_size, hidden_dim, device=start.device)
        c0 = torch.zeros(2, batch_size, hidden_dim, device=start.device)
        
        # Generate sequence
        trajectory = [start]
        current = start.squeeze(1)
        
        for _ in range(length - 1):
            output, (h0, c0) = self.trajectory_rnn(current.unsqueeze(1), (h0, c0))
            current = output.squeeze(1)
            trajectory.append(current.unsqueeze(1))
        
        return torch.cat(trajectory, dim=1)


class RealityChecker(nn.Module):
    """Ensures dreams maintain some connection to reality."""
    
    def __init__(self, latent_dim: int = 256):
        super().__init__()
        self.checker = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.GELU(),
            nn.Linear(128, 1)  # Reality score
        )
        
    def forward(self, dream_content: torch.Tensor) -> torch.Tensor:
        """Score how realistic/plausible content is."""
        return torch.sigmoid(self.checker(dream_content))


class DreamNetwork(nn.Module):
    """Main dream generation and processing network.
    
    Simulates dream-like generative processes for:
    - Creative ideation
    - Memory consolidation
    - Novel concept synthesis
    """
    
    def __init__(
        self,
        input_dim: int = 512,
        latent_dim: int = 256
    ):
        super().__init__()
        
        self.encoder = DreamEncoder(input_dim, latent_dim)
        self.weaver = DreamWeaver(latent_dim)
        self.reality_checker = RealityChecker(latent_dim)
        
        # Memory store for consolidation
        self.memory_capacity = 100
        self.register_buffer('memory_store', torch.zeros(100, latent_dim))
        self.register_buffer('memory_strength', torch.zeros(100))
        self.memory_count = 0
        
        self.latent_dim = latent_dim
        
    def encode_experience(self, experience: torch.Tensor) -> torch.Tensor:
        """Encode experience to latent space."""
        mu, logvar = self.encoder(experience)
        return self.encoder.reparameterize(mu, logvar)
    
    def store_memory(self, experience: torch.Tensor) -> int:
        """Store experience in memory for consolidation."""
        latent = self.encode_experience(experience)
        
        if self.memory_count < self.memory_capacity:
            idx = self.memory_count
            self.memory_count += 1
        else:
            # Overwrite weakest memory
            idx = int(self.memory_strength.argmin().item())
        
        self.memory_store[idx] = latent.detach()
        self.memory_strength[idx] = 1.0
        
        return idx
    
    def consolidate_memories(self, num_cycles: int = 5) -> List[DreamContent]:
        """Consolidate memories through dream-like replay."""
        dreams = []
        
        for cycle in range(num_cycles):
            # Sample memories
            if self.memory_count == 0:
                continue
                
            indices = random.sample(range(self.memory_count), min(5, self.memory_count))
            sampled = self.memory_store[indices]
            
            # Generate dream by mixing memories
            if len(sampled) >= 2:
                mixed = self.weaver.mix_concepts(sampled[0], sampled[1])
            else:
                mixed = sampled[0]
            
            # Add novelty
            novel = self.weaver.generate_novelty(mixed)
            
            # Generate trajectory
            trajectory = self.weaver.generate_trajectory(novel, length=8)
            
            # Check reality
            reality_scores = self.reality_checker(novel)
            
            # Create dream content
            dream = DreamContent(
                latent_trajectory=trajectory,
                synthesized_concepts=[f"concept_{i}" for i in indices],
                novelty_score=torch.norm(novel - mixed).item(),
                coherence_score=reality_scores.mean().item(),
                emotional_valence=random.uniform(-1, 1)
            )
            dreams.append(dream)
            
            # Strengthen memories
            self.memory_strength[indices] *= 0.95
        
        return dreams
    
    def generate_creative_solution(
        self,
        problem: torch.Tensor,
        num_iterations: int = 10
    ) -> DreamContent:
        """Generate creative solution through dream-like processing."""
        # Encode problem
        problem_latent = self.encode_experience(problem)
        
        best_solution = problem_latent
        best_score = 0.0
        
        for _ in range(num_iterations):
            # Mix with random memories
            if self.memory_count > 0:
                random_idx = random.randint(0, self.memory_count - 1)
                memory = self.memory_store[random_idx]
                candidate = self.weaver.mix_concepts(problem_latent, memory)
            else:
                candidate = problem_latent
            
            # Add novelty
            candidate = self.weaver.generate_novelty(candidate)
            
            # Score (novelty + reality balance)
            novelty = torch.norm(candidate - problem_latent).item()
            reality = self.reality_checker(candidate).item()
            score = novelty * reality
            
            if score > best_score:
                best_solution = candidate
                best_score = score
        
        # Generate full trajectory
        trajectory = self.weaver.generate_trajectory(best_solution, length=5)
        
        return DreamContent(
            latent_trajectory=trajectory,
            synthesized_concepts=["solution"],
            novelty_score=best_score,
            coherence_score=self.reality_checker(best_solution).item(),
            emotional_valence=0.5
        )
    
    def forward(
        self,
        experiences: torch.Tensor,
        dream_mode: str = "consolidate"
    ) -> Dict[str, Any]:
        """Process experiences through dream network."""
        
        # Store experiences
        for exp in experiences:
            self.store_memory(exp.unsqueeze(0))
        
        if dream_mode == "consolidate":
            dreams = self.consolidate_memories()
        elif dream_mode == "creative":
            avg_exp = experiences.mean(dim=0, keepdim=True)
            dreams = [self.generate_creative_solution(avg_exp)]
        else:
            dreams = []
        
        return {
            'dreams': dreams,
            'memory_count': self.memory_count,
            'avg_strength': self.memory_strength[:self.memory_count].mean().item()
        }


def create_dream_network(
    input_dim: int = 512,
    latent_dim: int = 256
) -> DreamNetwork:
    """Create DreamNetwork."""
    return DreamNetwork(input_dim, latent_dim)
