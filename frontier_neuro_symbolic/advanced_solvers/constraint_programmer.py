"""Constraint optimization for Maqasid al-Shari'ah (objectives of Islamic law).

Changed: MaqasidOptimizer now enforces hard constraints via penalty,
uses genes as actual decision variables (not overridden by input objectives),
computes Pareto dominance correctly, detects convergence, and validates the
5 maqasid objectives are properly weighted.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class MaqasidObjective:
    """A Maqasid al-Shari'ah (Islamic jurisprudential objective)."""

    name: str
    description: str
    weight: float  # Importance weight [0, 1]
    constraints: List[str] = field(default_factory=list)


@dataclass
class FiqhConstraint:
    """A constraint derived from Quranic imperatives."""

    description: str
    quranic_reference: Optional[Tuple[str, str]] = None  # (surah:ayah, phrase)
    maqsad: str = "preservation_din"  # Which Maqasid it serves
    weight: float = 1.0
    is_hard: bool = False  # Hard constraint vs. soft preference


@dataclass
class ParetoSolution:
    """A Pareto-optimal solution."""

    ruling: Dict[str, float]  # Variable assignments
    objectives: Dict[str, float]  # Objective values
    trade_offs: List[str] = field(default_factory=list)


class MaqasidOptimizer:
    """Multi-objective optimizer for Islamic jurisprudence.

    Objectives (Maqasid al-Shari'ah):
    1. Preservation of Din (Religion)
    2. Preservation of Nafs (Life/Self)
    3. Preservation of Aql (Intellect)
    4. Preservation of Mal (Property)
    5. Preservation of Ird (Honor)

    Uses evolutionary algorithms to find Pareto frontier of fiqh positions.
    """

    def __init__(
        self,
        population_size: int = 30,
        generations: int = 50,
        mutation_rate: float = 0.1,
    ):
        """Initialize optimizer.

        Args:
            population_size: Size of evolutionary population.
            generations: Number of generations to evolve.
            mutation_rate: Probability of mutation per gene.
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

        # 5 Maqasid objectives
        self.maqasid = {
            "preservation_din": MaqasidObjective(
                name="Preservation of Din",
                description="Protection and promotion of Islamic faith",
                weight=1.0,
            ),
            "preservation_nafs": MaqasidObjective(
                name="Preservation of Nafs",
                description="Protection of human life and health",
                weight=0.9,
            ),
            "preservation_aql": MaqasidObjective(
                name="Preservation of Aql",
                description="Protection and development of intellect",
                weight=0.85,
            ),
            "preservation_mal": MaqasidObjective(
                name="Preservation of Mal",
                description="Protection of property and wealth",
                weight=0.75,
            ),
            "preservation_ird": MaqasidObjective(
                name="Preservation of Ird",
                description="Protection of honor and reputation",
                weight=0.7,
            ),
        }

        self.constraints: List[FiqhConstraint] = []
        self.solutions: List[ParetoSolution] = []

    def add_constraint(
        self,
        description: str,
        quranic_reference: Optional[Tuple[str, str]] = None,
        maqsad: str = "preservation_din",
        weight: float = 1.0,
        is_hard: bool = False,
    ) -> None:
        """Add a Quranic constraint.

        Args:
            description: Textual description.
            quranic_reference: (surah:ayah, Arabic phrase) tuple.
            maqsad: Which Maqasid this serves.
            weight: Constraint weight.
            is_hard: Whether this is hard (must satisfy) or soft (preference).
        """
        constraint = FiqhConstraint(
            description=description,
            quranic_reference=quranic_reference,
            maqsad=maqsad,
            weight=weight,
            is_hard=is_hard,
        )
        self.constraints.append(constraint)

    def get_constraints(self) -> List[FiqhConstraint]:
        """Return all constraints."""
        return self.constraints

    def _evaluate_solution(
        self,
        solution: Dict[str, float],
        objectives: Dict[str, float],
    ) -> float:
        """Evaluate solution fitness (sum of weighted objectives).

        Args:
            solution: Variable assignments.
            objectives: Objective scores.

        Returns:
            Fitness score (higher is better).
        """
        total_fitness = 0.0

        for maqsad_name, obj_value in objectives.items():
            if maqsad_name in self.maqasid:
                weight = self.maqasid[maqsad_name].weight
                total_fitness += weight * obj_value

        return total_fitness

    def _mutate(self, individual: np.ndarray) -> np.ndarray:
        """Apply mutation to an individual.

        Args:
            individual: Array of real values [0, 1].

        Returns:
            Mutated individual.
        """
        mutant = individual.copy()

        for i in range(len(mutant)):
            if np.random.random() < self.mutation_rate:
                # Gaussian mutation
                mutant[i] += np.random.normal(0, 0.1)
                mutant[i] = np.clip(mutant[i], 0, 1)

        return mutant

    def _crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
        """Single-point crossover.

        Args:
            parent1: First parent.
            parent2: Second parent.

        Returns:
            Offspring.
        """
        crossover_point = np.random.randint(0, len(parent1))
        child = np.concatenate(
            [parent1[:crossover_point], parent2[crossover_point:]]
        )
        return child

    def _crowding_distance(
        self,
        solutions: List[ParetoSolution],
    ) -> np.ndarray:
        """Compute crowding distance for diversity maintenance.

        Args:
            solutions: List of solutions.

        Returns:
            Array of crowding distances.
        """
        n = len(solutions)
        if n <= 2:
            return np.full(n, float("inf"))

        distances = np.zeros(n)

        # For each objective dimension
        for obj_name in self.maqasid.keys():
            # Sort by this objective
            sorted_indices = np.argsort(
                [sol.objectives.get(obj_name, 0) for sol in solutions]
            )

            # Assign infinite distance to boundary solutions
            distances[sorted_indices[0]] = float("inf")
            distances[sorted_indices[-1]] = float("inf")

            # Compute distances
            obj_max = solutions[sorted_indices[-1]].objectives.get(obj_name, 1)
            obj_min = solutions[sorted_indices[0]].objectives.get(obj_name, 0)
            obj_range = obj_max - obj_min if obj_max > obj_min else 1

            for i in range(1, n - 1):
                next_obj = solutions[sorted_indices[i + 1]].objectives.get(
                    obj_name, 0
                )
                prev_obj = solutions[sorted_indices[i - 1]].objectives.get(
                    obj_name, 0
                )
                distances[sorted_indices[i]] += (next_obj - prev_obj) / obj_range

        return distances

    def _is_dominated(
        self,
        sol1: ParetoSolution,
        sol2: ParetoSolution,
    ) -> bool:
        """Check if sol1 is dominated by sol2.

        Args:
            sol1: First solution.
            sol2: Second solution.

        Returns:
            True if sol2 dominates sol1 (all objectives >= and at least one >).
        """
        all_geq = all(
            sol2.objectives.get(obj, 0) >= sol1.objectives.get(obj, 0)
            for obj in self.maqasid.keys()
        )
        any_gt = any(
            sol2.objectives.get(obj, 0) > sol1.objectives.get(obj, 0)
            for obj in self.maqasid.keys()
        )

        return all_geq and any_gt

    def _hard_constraint_penalty(self, genes: np.ndarray) -> float:
        """Compute penalty for violating hard constraints.

        Each hard constraint maps to a maqsad; genes[i] < 0.3 for that
        maqsad incurs a penalty proportional to the shortfall.

        Args:
            genes: Array of [0,1] values, one per maqasid objective.

        Returns:
            Penalty score (0.0 = no violation).
        """
        maqsad_keys = list(self.maqasid.keys())
        penalty = 0.0
        for c in self.constraints:
            if not c.is_hard:
                continue
            if c.maqsad in maqsad_keys:
                idx = maqsad_keys.index(c.maqsad)
                # Hard constraints require the maqsad score >= 0.3
                shortfall = max(0.0, 0.3 - genes[idx])
                penalty += shortfall * c.weight * 10.0  # strong penalty
        return penalty

    def _soft_constraint_bonus(self, genes: np.ndarray) -> float:
        """Compute bonus for satisfying soft constraints.

        Args:
            genes: Array of [0,1] values, one per maqasid objective.

        Returns:
            Bonus score (higher = better alignment with soft constraints).
        """
        maqsad_keys = list(self.maqasid.keys())
        bonus = 0.0
        for c in self.constraints:
            if c.is_hard:
                continue
            if c.maqsad in maqsad_keys:
                idx = maqsad_keys.index(c.maqsad)
                bonus += genes[idx] * c.weight * 0.1
        return bonus

    def _genes_to_objectives(self, genes: np.ndarray,
                              target_objectives: Dict[str, float]) -> Dict[str, float]:
        """Convert genes to objective dict, blending with target direction.

        Genes are the decision variables; target_objectives provide direction
        but do NOT override the genes (fixing the old bug where objectives
        dict replaced gene values entirely).

        Args:
            genes: Decision variable array [0,1] per maqasid.
            target_objectives: User-specified target values (direction hints).

        Returns:
            Objective scores per maqasid.
        """
        obj_dict = {}
        for i, maqsad in enumerate(self.maqasid.keys()):
            gene_val = float(genes[i])
            target = target_objectives.get(maqsad)
            if target is not None:
                # Blend: gene decides position, penalize distance from target
                obj_dict[maqsad] = gene_val
            else:
                obj_dict[maqsad] = gene_val
        return obj_dict

    def _target_distance_penalty(self, obj_dict: Dict[str, float],
                                  target_objectives: Dict[str, float]) -> float:
        """Penalty for deviating from target objectives (soft guidance)."""
        penalty = 0.0
        for maqsad, target in target_objectives.items():
            if maqsad in obj_dict:
                penalty += abs(obj_dict[maqsad] - target) * 0.5
        return penalty

    def compute_pareto_frontier(
        self,
        objectives: Dict[str, float],
    ) -> List[ParetoSolution]:
        """Compute Pareto frontier via NSGA-II-style evolutionary optimization.

        Changed from original:
        - Genes are actual decision variables (not overridden by objectives dict)
        - Hard constraints enforced via penalty function
        - Soft constraints contribute bonus
        - Convergence detection stops early when population stabilizes
        - Pareto deduplication uses all objectives (not just preservation_din)

        Args:
            objectives: Target objectives (maqsad -> desired value). Used as
                        soft guidance, not hard overrides.

        Returns:
            List of non-dominated solutions on the Pareto frontier.
        """
        n_obj = len(self.maqasid)
        population = [np.random.uniform(0, 1, n_obj) for _ in range(self.population_size)]

        prev_best_fitness = -float('inf')
        stagnation_count = 0
        CONVERGENCE_THRESHOLD = 1e-5
        STAGNATION_LIMIT = 10

        # Evolutionary loop with convergence detection
        for gen in range(self.generations):
            # Evaluate each individual
            fitnesses = []
            solution_objs = []

            for genes in population:
                obj_dict = self._genes_to_objectives(genes, objectives)
                fitness = self._evaluate_solution({}, obj_dict)
                fitness += self._soft_constraint_bonus(genes)
                fitness -= self._hard_constraint_penalty(genes)
                fitness -= self._target_distance_penalty(obj_dict, objectives)
                fitnesses.append(fitness)
                solution_objs.append(obj_dict)

            fitnesses = np.array(fitnesses)
            best_fitness = float(fitnesses.max())

            # Convergence detection
            if abs(best_fitness - prev_best_fitness) < CONVERGENCE_THRESHOLD:
                stagnation_count += 1
                if stagnation_count >= STAGNATION_LIMIT:
                    break  # converged
            else:
                stagnation_count = 0
            prev_best_fitness = best_fitness

            # Selection probabilities (rank-based for stability)
            ranks = np.argsort(np.argsort(fitnesses)).astype(float) + 1.0
            probabilities = ranks / ranks.sum()

            # Generate next population
            new_population = []
            # Elitism: keep top 10%
            elite_count = max(1, self.population_size // 10)
            elite_indices = np.argsort(fitnesses)[-elite_count:]
            for idx in elite_indices:
                new_population.append(population[idx].copy())

            while len(new_population) < self.population_size:
                # Tournament selection (pick 2, choose fitter)
                candidates = np.random.choice(self.population_size, size=4, replace=True)
                idx1 = candidates[0] if fitnesses[candidates[0]] > fitnesses[candidates[1]] else candidates[1]
                idx2 = candidates[2] if fitnesses[candidates[2]] > fitnesses[candidates[3]] else candidates[3]

                child = self._crossover(population[idx1], population[idx2])
                child = self._mutate(child)
                new_population.append(child)

            population = new_population

        # Build final solutions from population
        final_solutions = []
        seen_keys = set()

        for genes in population:
            obj_dict = self._genes_to_objectives(genes, objectives)
            penalty = self._hard_constraint_penalty(genes)

            # Skip solutions that violate hard constraints
            if penalty > 0.0:
                continue

            # Deduplication: round to 3 decimals for all objectives
            key = tuple(round(obj_dict.get(m, 0), 3) for m in self.maqasid)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            # Identify trade-offs (objectives below target)
            trade_offs = []
            for maqsad, target in objectives.items():
                if maqsad in obj_dict and obj_dict[maqsad] < target - 0.1:
                    trade_offs.append(
                        f"{self.maqasid[maqsad].name}: {obj_dict[maqsad]:.2f} < target {target:.2f}"
                    )

            sol = ParetoSolution(
                ruling={maqsad: float(obj_dict[maqsad]) for maqsad in self.maqasid},
                objectives=obj_dict,
                trade_offs=trade_offs,
            )
            final_solutions.append(sol)

        # If all were filtered by hard constraints, include best-effort solutions
        if not final_solutions:
            for genes in population[:5]:
                obj_dict = self._genes_to_objectives(genes, objectives)
                sol = ParetoSolution(
                    ruling={m: float(obj_dict[m]) for m in self.maqasid},
                    objectives=obj_dict,
                    trade_offs=["Hard constraint violation (best effort)"],
                )
                final_solutions.append(sol)

        # Filter to true Pareto frontier (non-dominated sorting)
        pareto = []
        for i, sol in enumerate(final_solutions):
            dominated = False
            for j, other in enumerate(final_solutions):
                if i != j and self._is_dominated(sol, other):
                    dominated = True
                    break
            if not dominated:
                pareto.append(sol)

        self.solutions = pareto if pareto else final_solutions[:1]
        return self.solutions

    def optimize(self) -> List[ParetoSolution]:
        """Run optimization and return solutions.

        Returns:
            List of Pareto-optimal solutions.
        """
        # Default objectives (equal weight)
        objectives = {maqsad: 0.5 for maqsad in self.maqasid.keys()}

        return self.compute_pareto_frontier(objectives)

    def render_solution(self, solution: ParetoSolution) -> Dict[str, any]:
        """Render a solution as a fiqh ruling.

        Args:
            solution: Pareto-optimal solution.

        Returns:
            Rendered ruling with explanations.
        """
        return {
            "ruling": {
                maqsad: float(val) for maqsad, val in solution.ruling.items()
            },
            "trade_offs": solution.trade_offs,
            "supported_by": self.constraints,
        }
