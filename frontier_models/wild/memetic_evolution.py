"""Memetic Evolution Network - Ideas as Replicators.

Models ideas/concepts as memes that evolve, compete, and propagate
through a population using evolutionary dynamics.

Architecture:
    Memes: Self-replicating information units
    Fitness: Based on传播 ability, memorability, utility
    Selection: Memes compete for attention/memory
    Mutation: Ideas transform during transmission
    Recombination: Ideas combine to form new memes

Applications:
- Viral content prediction
- Ideology spread modeling
- Cultural evolution tracking
- Marketing campaign optimization
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class Meme:
    """A meme (idea unit)."""
    id: str
    content: torch.Tensor
    fitness: float
    generation: int
    parent_ids: List[str]
    mutation_rate: float


@dataclass
class PopulationState:
    """State of meme population."""
    memes: List[Meme]
    generation: int
    diversity: float
    dominant_memes: List[str]


class MemeEncoder(nn.Module):
    """Encodes ideas into meme representations."""
    
    def __init__(self, input_dim: int = 768, meme_dim: int = 128):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.GELU(),
            nn.Linear(512, meme_dim * 3)  # content + fitness + mutation
        )
        self.meme_dim = meme_dim
        
    def forward(self, content: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        encoded = self.encoder(content)
        meme_content = encoded[:, :self.meme_dim]
        fitness = torch.sigmoid(encoded[:, self.meme_dim:self.meme_dim+1])
        mutation_rate = torch.sigmoid(encoded[:, self.meme_dim+1:])
        return meme_content, fitness, mutation_rate


class MemeticSelection(nn.Module):
    """Implements selection pressure on memes."""
    
    def __init__(self, selection_strength: float = 1.0):
        super().__init__()
        self.selection_strength = selection_strength
        
    def forward(
        self,
        fitness: torch.Tensor,
        population_size: int
    ) -> torch.Tensor:
        """Select memes based on fitness.
        
        Uses tournament selection with configurable pressure.
        """
        # Softmax selection with temperature
        probs = F.softmax(fitness * self.selection_strength, dim=0)
        return probs


class MemeMutation(nn.Module):
    """Applies mutations to memes during transmission."""
    
    def __init__(self, base_mutation_rate: float = 0.01, meme_dim: int = 128):
        super().__init__()
        self.base_mutation_rate = base_mutation_rate
        self.meme_dim = meme_dim
        self.mutation_net = nn.Sequential(
            nn.Linear(meme_dim, meme_dim // 2),
            nn.ReLU(),
            nn.Linear(meme_dim // 2, meme_dim),
            nn.Tanh()
        )
        
    def forward(
        self,
        meme: torch.Tensor,
        mutation_rate: torch.Tensor
    ) -> torch.Tensor:
        """Apply mutation to meme."""
        # Ensure correct dimension
        if meme.size(-1) != self.meme_dim:
            self.meme_dim = meme.size(-1)
            self.mutation_net = nn.Sequential(
                nn.Linear(self.meme_dim, self.meme_dim // 2),
                nn.ReLU(),
                nn.Linear(self.meme_dim // 2, self.meme_dim),
                nn.Tanh()
            ).to(meme.device)
        
        mutation = self.mutation_net(meme) * mutation_rate
        return meme + mutation


class MemeticRecombination(nn.Module):
    """Recombines memes to create new ideas."""
    
    def __init__(self, meme_dim: int = 128):
        super().__init__()
        self.crossover_net = nn.Linear(meme_dim * 2, meme_dim)
        
    def forward(
        self,
        parent1: torch.Tensor,
        parent2: torch.Tensor
    ) -> torch.Tensor:
        """Create offspring from two parent memes."""
        combined = torch.cat([parent1, parent2], dim=-1)
        offspring = self.crossover_net(combined)
        return (offspring + parent1 + parent2) / 3  # Residual connection


class MemeticEvolutionNetwork(nn.Module):
    """Main memetic evolution simulator.
    
    Simulates how ideas spread, evolve, and compete in a population.
    """
    
    def __init__(
        self,
        input_dim: int = 768,
        meme_dim: int = 128,
        population_size: int = 100,
        selection_strength: float = 1.0
    ):
        super().__init__()
        
        self.encoder = MemeEncoder(input_dim, meme_dim)
        self.selection = MemeticSelection(selection_strength)
        self.mutation = MemeMutation(meme_dim=meme_dim)
        self.recombination = MemeticRecombination(meme_dim)
        
        self.population_size = population_size
        self.meme_dim = meme_dim
        
        # Population memory
        self.register_buffer('population', torch.zeros(population_size, meme_dim))
        self.register_buffer('fitness_history', torch.zeros(population_size, 100))
        
    def initialize_population(self, ideas: torch.Tensor) -> List[Meme]:
        """Initialize population from ideas."""
        memes = []
        content, fitness, mutation_rate = self.encoder(ideas)
        
        for i in range(min(len(ideas), self.population_size)):
            memes.append(Meme(
                id=f"meme_{i}",
                content=content[i],
                fitness=fitness[i].item(),
                generation=0,
                parent_ids=[],
                mutation_rate=mutation_rate[i].mean().item()  # Fixed: average mutation rate
            ))
        
        return memes
    
    def evolve(
        self,
        memes: List[Meme],
        num_generations: int = 10
    ) -> PopulationState:
        """Evolve meme population over generations."""
        if len(memes) < 2:
            return PopulationState(
                memes=memes,
                generation=num_generations,
                diversity=0.0,
                dominant_memes=[m.id for m in memes]
            )
        
        current_memes = memes.copy()
        
        for gen in range(num_generations):
            if len(current_memes) < 2:
                break
                
            # Selection
            fitness_tensor = torch.tensor([m.fitness for m in current_memes])
            selection_probs = self.selection(fitness_tensor, len(current_memes))
            
            # Tournament selection
            selected_indices = torch.multinomial(selection_probs, min(len(current_memes), 10), replacement=True)
            
            if len(selected_indices) < 2:
                break
            
            # Recombination
            new_memes = []
            for i in range(0, len(selected_indices) - 1, 2):
                idx1, idx2 = selected_indices[i], selected_indices[i + 1]
                parent1, parent2 = current_memes[idx1], current_memes[idx2]
                
                # Crossover
                offspring_content = self.recombination(parent1.content, parent2.content)
                
                # Mutation
                mutation_rate = torch.tensor([(parent1.mutation_rate + parent2.mutation_rate) / 2])
                offspring_content = self.mutation(offspring_content.unsqueeze(0), mutation_rate).squeeze(0)
                
                # Evaluate fitness of offspring
                offspring_fitness = self._evaluate_fitness(offspring_content)
                
                new_memes.append(Meme(
                    id=f"meme_gen{gen}_{i}",
                    content=offspring_content,
                    fitness=offspring_fitness.item(),
                    generation=gen + 1,
                    parent_ids=[parent1.id, parent2.id],
                    mutation_rate=mutation_rate.item()
                ))
            
            if new_memes:
                current_memes = new_memes
        
        # Compute population statistics
        fitness_values = [m.fitness for m in current_memes]
        diversity = torch.std(torch.tensor(fitness_values)).item() if len(fitness_values) > 1 else 0.0
        dominant = sorted(current_memes, key=lambda m: -m.fitness)[:5]
        
        return PopulationState(
            memes=current_memes,
            generation=num_generations,
            diversity=diversity,
            dominant_memes=[m.id for m in dominant]
        )
    
    def _evaluate_fitness(self, content: torch.Tensor) -> torch.Tensor:
        """Evaluate meme fitness (传播 ability)."""
        # Fitness based on:
        # 1. Memorability (norm)
        # 2. Simplicity (sparsity)
        # 3. Emotional resonance (learned)
        
        memorability = torch.norm(content, dim=-1)
        simplicity = 1.0 / (torch.norm(content, dim=-1) + 1e-9)
        
        return (memorability * 0.4 + simplicity * 0.3 + 0.3).clamp(0, 1)
    
    def predict_virality(
        self,
        idea: torch.Tensor,
        population_context: Optional[torch.Tensor] = None
    ) -> Dict[str, float]:
        """Predict how viral an idea will become."""
        content, fitness, mutation_rate = self.encoder(idea.unsqueeze(0))
        
        # Virality score
        virality = {
            'fitness': fitness[0].item(),
            'memorability': torch.norm(content, dim=-1)[0].item(),
            'mutability': mutation_rate[0].mean().item(),
            'expected_spread': fitness[0].item() * 100,
            'survival_probability': min(1.0, fitness[0].item() * 2)
        }
        
        return virality
    
    def forward(
        self,
        ideas: torch.Tensor,
        num_generations: int = 10
    ) -> Dict[str, any]:
        """Run memetic evolution on ideas."""
        memes = self.initialize_population(ideas)
        final_state = self.evolve(memes, num_generations)
        
        return {
            'generation': final_state.generation,
            'diversity': final_state.diversity,
            'dominant_memes': final_state.dominant_memes,
            'final_fitness': [m.fitness for m in final_state.memes[:5]]
        }


def create_memetic_network(
    input_dim: int = 768,
    meme_dim: int = 128,
    population_size: int = 100
) -> MemeticEvolutionNetwork:
    """Create MemeticEvolutionNetwork."""
    return MemeticEvolutionNetwork(input_dim, meme_dim, population_size)
