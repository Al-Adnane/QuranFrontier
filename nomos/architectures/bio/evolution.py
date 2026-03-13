"""Evolution Network - Natural Selection and Genetic Algorithms.

Inspired by: Biological evolution and natural selection

Architecture:
    Population: Set of candidate solutions
    Fitness: Selection pressure
    Crossover: Genetic recombination
    Mutation: Random variation
    Selection: Survival of the fittest
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple


class EvolutionNetwork(nn.Module):
    """Evolutionary optimization network."""
    
    def __init__(self, input_dim: int = 128, embed_dim: int = 256, population_size: int = 100):
        super().__init__()
        self.population_size = population_size
        self.gene_dim = embed_dim
        
        # Population (chromosomes)
        self.population = nn.Parameter(torch.randn(population_size, embed_dim) * 0.5)
        
        # Fitness function
        self.fitness_fn = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2),
            nn.GELU(),
            nn.Linear(embed_dim // 2, 1)
        )
        
        # Mutation rate (learnable)
        self.mutation_rate = nn.Parameter(torch.tensor(0.1))
        
        # Crossover rate
        self.crossover_rate = nn.Parameter(torch.tensor(0.7))
        
        # Selection pressure
        self.selection_pressure = nn.Parameter(torch.tensor(2.0))
        
    def evaluate_fitness(self, individuals: torch.Tensor) -> torch.Tensor:
        """Evaluate fitness of individuals."""
        return torch.sigmoid(self.fitness_fn(individuals)).squeeze(-1)
    
    def select_parents(self, fitness: torch.Tensor, num_parents: int) -> torch.Tensor:
        """Tournament selection of parents."""
        # Softmax selection based on fitness
        probs = F.softmax(fitness * self.selection_pressure, dim=0)
        indices = torch.multinomial(probs, num_parents, replacement=True)
        return indices
    
    def crossover(self, parent1: torch.Tensor, parent2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Single-point crossover."""
        if torch.rand(1) > self.crossover_rate:
            return parent1.clone(), parent2.clone()
        
        # Random crossover point
        point = torch.randint(1, self.gene_dim - 1, (1,)).item()
        
        child1 = torch.cat([parent1[:point], parent2[point:]])
        child2 = torch.cat([parent2[:point], parent1[point:]])
        
        return child1, child2
    
    def mutate(self, individual: torch.Tensor) -> torch.Tensor:
        """Gaussian mutation."""
        mutation = torch.randn_like(individual) * self.mutation_rate
        return individual + mutation
    
    def evolve(self, generations: int = 10) -> Dict:
        """Run evolutionary optimization."""
        fitness_history = []
        
        for gen in range(generations):
            # Evaluate fitness
            fitness = self.evaluate_fitness(self.population)
            fitness_history.append(fitness.mean().item())
            
            # Select parents
            parent_indices = self.select_parents(fitness, self.population_size)
            parents = self.population[parent_indices]
            
            # Create next generation
            new_population = []
            for i in range(0, self.population_size, 2):
                if i + 1 < len(parents):
                    # Crossover
                    child1, child2 = self.crossover(parents[i], parents[i + 1])
                    # Mutation
                    child1 = self.mutate(child1)
                    child2 = self.mutate(child2)
                    new_population.extend([child1, child2])
                else:
                    new_population.append(parents[i])
            
            # Update population
            self.population = torch.stack(new_population[:self.population_size])
        
        # Get best individual
        final_fitness = self.evaluate_fitness(self.population)
        best_idx = final_fitness.argmax()
        
        return {
            'best_individual': self.population[best_idx],
            'best_fitness': final_fitness[best_idx].item(),
            'fitness_history': fitness_history,
            'final_mean_fitness': final_fitness.mean().item(),
            'mutation_rate': self.mutation_rate.item(),
            'crossover_rate': self.crossover_rate.item()
        }
    
    def forward(self, x: torch.Tensor, generations: int = 10) -> Dict:
        """Forward pass with evolution."""
        # Initialize population from input
        with torch.no_grad():
            self.population.data = x.unsqueeze(0).expand(self.population_size, -1) + \
                                   torch.randn(self.population_size, x.size(1), device=x.device) * 0.1
        
        # Evolve
        return self.evolve(generations)


def create_evolution_network(input_dim: int = 128, embed_dim: int = 256):
    """Create EvolutionNetwork."""
    return EvolutionNetwork(input_dim, embed_dim)
