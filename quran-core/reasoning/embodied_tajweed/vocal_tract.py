"""
Morphogenetic Field PDE Solver for Vocal Tract Activation.

Solves stochastic PDEs on the vocal tract manifold to simulate tajweed dynamics:
    ∂ₜu = D∇²u + f(u; makharij) + ξ(t)

where:
- u(x,t) = activation of articulatory feature at position x and time t
- D = diffusion coefficient (anatomical smoothing)
- f(u; makharij) = Turing reaction term encoding tajweed rules
- ξ(t) = Gaussian noise for stochasticity

This creates Turing patterns that correspond to:
- Idgham (assimilation): confluent activation zones
- Ikhfaa (hiding): weak diffuse activation
- Iqlab (conversion): bifurcation pattern
- Izhar (clarity): isolated peaks
"""

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve
from scipy.integrate import odeint
from typing import Optional, Dict, Tuple, Callable
import warnings


class VocalTractManifold:
    """
    Geometric manifold representing the vocal tract.

    Encodes:
    - Spatial positions along the vocal tract (velum to lips)
    - Makharij (18 tajweed pronunciation points)
    - Laryngeal-supralaryngeal coupling
    - Anatomical constraints
    """

    def __init__(self, grid_size: int = 64):
        """
        Initialize vocal tract manifold.

        Args:
            grid_size: Number of spatial grid points along vocal tract.
        """
        self.grid_size = grid_size
        self.x = np.linspace(0, 1, grid_size)  # Normalized position [0,1]

        # 18 Tajweed makharij points (normalized positions along vocal tract)
        # Reference: Tajweed science encoding makharij from ghunnah (velum) to lips
        self.makharij = np.array([
            0.05,   # 1. Al-Ghunnah (nasal cavity) - خيشوم
            0.10,   # 2. Al-Khay'sh (back of tongue) - خيشوم
            0.15,   # 3. Al-'Aynain (uvula) - الحلق
            0.20,   # 4. Al-Halq al-Wasa (middle pharynx) - الحلق
            0.25,   # 5. Al-Halq al-'Asfal (lower pharynx) - الحلق
            0.30,   # 6. Asl al-Lisan (back of tongue) - اللسان
            0.35,   # 7. Wasat al-Lisan (middle of tongue) - اللسان
            0.40,   # 8. Taraf al-Lisan (tip of tongue) - اللسان
            0.42,   # 9. Al-Jidda (gum ridge above upper teeth) - اللثة
            0.44,   # 10. Al-Adraas al-'Ulya (upper teeth) - الأسنان
            0.46,   # 11. Al-Adraas al-Sufla (lower teeth) - الأسنان
            0.48,   # 12. Al-Shafatain (lips) - الشفتان
            0.50,   # 13. Bayn al-Shafatain (between lips) - الشفتان
            0.55,   # 14. Hard palate region 1 - الحنك الصلب
            0.60,   # 15. Hard palate region 2 - الحنك الصلب
            0.65,   # 16. Soft palate (velum) coupling - الحنك الرخو
            0.70,   # 17. Nasopharyngeal - الأنف
            0.80,   # 18. Laryngeal region - الحنجرة
        ])

        # Anatomical smoothing (diffusion length scale)
        self.smoothing_length = 0.1

    def compute_coupling_strength(self) -> np.ndarray:
        """
        Compute laryngeal-supralaryngeal coupling strength.

        Returns:
            Shape (grid_size,) coupling strength from 0 to 1.
        """
        # Coupling is strongest in the laryngeal region (high x)
        # Decreases toward the lips
        coupling = np.exp(-3 * (self.x - 0.8) ** 2)
        # Normalize
        coupling = coupling / np.max(coupling)
        return coupling


class MorphogeneticField:
    """
    Turing-pattern based morphogenetic field solver.

    Solves the stochastic PDE:
        ∂ₜu = D·∂²ₓu + f(u; makharij, tajweed_rule) + σ·ξ(t)

    Using an implicit Euler scheme for stability:
        u^{n+1} = u^n + Δt·(L·u^{n+1} + f(u^n) + noise)
    """

    def __init__(
        self,
        grid_size: int = 64,
        diffusion_coeff: float = 0.01,
        reaction_strength: float = 1.0,
        time_step: float = 0.001,
        noise_level: float = 0.01,
        tajweed_rule: str = "idgham",
    ):
        """
        Initialize morphogenetic field.

        Args:
            grid_size: Spatial grid size.
            diffusion_coeff: Diffusion coefficient D.
            reaction_strength: Turing reaction strength.
            time_step: Numerical time step.
            noise_level: Gaussian noise standard deviation.
            tajweed_rule: Which tajweed rule to encode ("idgham", "ikhfaa", "iqlab", "izhar").
        """
        self.grid_size = grid_size
        self.diffusion_coeff = diffusion_coeff
        self.reaction_strength = reaction_strength
        self.time_step = time_step
        self.noise_level = noise_level
        self.tajweed_rule = tajweed_rule

        # Vocal tract manifold
        self.manifold = VocalTractManifold(grid_size)

        # Build Laplacian matrix (second derivative, Dirichlet boundary)
        dx = 1.0 / (grid_size - 1)
        diag_main = np.ones(grid_size) * (-2.0 / (dx ** 2))
        diag_off = np.ones(grid_size - 1) * (1.0 / (dx ** 2))
        self.laplacian = diags([diag_main, diag_off, diag_off], [0, 1, -1]).tocsr()

        # Identity matrix for implicit scheme
        self.identity = np.eye(grid_size, dtype=np.float32)

        # Build system matrix: (I - Δt·D·L)
        self.system_matrix = self.identity - self.time_step * self.diffusion_coeff * self.laplacian.toarray()

        # Rule parameters (Turing instability region)
        self.rule_parameters = self._get_rule_parameters()

    def _get_rule_parameters(self) -> Dict[str, float]:
        """
        Get Turing instability parameters for specific tajweed rules.

        Returns:
            Dictionary of parameters (activation_threshold, inhibition_range, bifurcation_strength).
        """
        params = {
            "idgham": {
                "activation_threshold": 0.3,
                "inhibition_range": 0.05,
                "bifurcation_strength": 2.5,
            },
            "ikhfaa": {
                "activation_threshold": 0.1,
                "inhibition_range": 0.15,
                "bifurcation_strength": 1.2,
            },
            "iqlab": {
                "activation_threshold": 0.4,
                "inhibition_range": 0.08,
                "bifurcation_strength": 2.0,
            },
            "izhar": {
                "activation_threshold": 0.5,
                "inhibition_range": 0.02,
                "bifurcation_strength": 3.0,
            },
        }
        return params.get(self.tajweed_rule, params["idgham"])

    def _reaction_term(self, u: np.ndarray) -> np.ndarray:
        """
        Turing reaction function encoding tajweed rules.

        Implements: f(u; makharij) = λ·u·(1 - u²) - γ·coupling(x)·u

        where:
        - First term: cubic autocatalysis (bistable)
        - Second term: lateralized inhibition (position-dependent)

        Args:
            u: Activation field shape (grid_size,).

        Returns:
            Reaction term f(u) shape (grid_size,).
        """
        params = self.rule_parameters

        # Bistable autocatalysis with Turing instability
        lambda_react = self.reaction_strength * params["bifurcation_strength"]
        reaction = lambda_react * u * (1.0 - u ** 2)

        # Inhibition kernel (Gaussian, position-dependent)
        coupling = self.manifold.compute_coupling_strength()
        gamma_inhib = params["inhibition_range"] / self.manifold.smoothing_length
        inhibition = -gamma_inhib * coupling * u

        # Makharij-weighted modulation
        makharij_mod = self._makharij_modulation(u)

        return reaction + inhibition + makharij_mod

    def _makharij_modulation(self, u: np.ndarray) -> np.ndarray:
        """
        Modulate reaction based on makharij localization.

        Args:
            u: Activation field.

        Returns:
            Modulation term.
        """
        # Gaussian bumps at makharij points
        modulation = np.zeros_like(u)
        sigma_makharij = 0.03

        for makharij_pos in self.manifold.makharij:
            bump = np.exp(-((self.manifold.x - makharij_pos) ** 2) / (2 * sigma_makharij ** 2))
            modulation += 0.05 * bump * u

        return modulation

    def solve_step(self, u: np.ndarray) -> np.ndarray:
        """
        Advance PDE by one time step using implicit Euler.

        Args:
            u: Current activation field, shape (grid_size,).

        Returns:
            Updated activation field u^{n+1}.
        """
        # Reaction term (explicit)
        reaction = self._reaction_term(u)

        # Noise
        noise = np.random.randn(self.grid_size) * self.noise_level

        # Right-hand side: u^n + Δt·(f(u^n) + noise)
        rhs = u + self.time_step * (reaction + noise)

        # Implicit solve: (I - Δt·D·L)·u^{n+1} = rhs
        try:
            u_next = spsolve(self.system_matrix, rhs).astype(np.float32)
        except Exception:
            # Fallback to explicit Euler if solver fails
            u_next = u + self.time_step * (self.diffusion_coeff * self.laplacian.toarray() @ u + reaction + noise)

        # Boundary conditions (Dirichlet: u=0 at edges)
        u_next[0] = 0.0
        u_next[-1] = 0.0

        # Clip to valid range
        u_next = np.clip(u_next, -1.0, 1.0)

        return u_next

    def compute_bifurcation_point(self) -> float:
        """
        Compute bifurcation parameter for current tajweed rule.

        Returns:
            Critical bifurcation strength where Turing instability begins.
        """
        # Analytical estimate: λ_c ~ 1 + sqrt(2)·γ·diffusion_coeff
        gamma = self.rule_parameters["inhibition_range"]
        return 1.0 + np.sqrt(2) * gamma * self.diffusion_coeff

    def evolve_to_pattern(
        self,
        u_init: np.ndarray,
        num_steps: int = 200,
        record_every: int = 10,
    ) -> Dict[str, np.ndarray]:
        """
        Evolve the field until a stable pattern emerges.

        Args:
            u_init: Initial activation.
            num_steps: Number of time steps.
            record_every: Record field every N steps.

        Returns:
            Dictionary with:
            - 'field': Final field
            - 'trajectory': List of intermediate fields
            - 'rule': tajweed rule name
        """
        u = u_init.copy()
        trajectory = [u.copy()]

        for step in range(num_steps):
            u = self.solve_step(u)
            if step % record_every == 0:
                trajectory.append(u.copy())

        return {
            "field": u,
            "trajectory": trajectory,
            "rule": self.tajweed_rule,
            "grid_size": self.grid_size,
        }

    def compute_pattern_energy(self, u: np.ndarray) -> float:
        """
        Compute Lyapunov energy of the field.

        E[u] = ∫ [D/2·|∇u|² + U(u)]

        Args:
            u: Activation field.

        Returns:
            Energy scalar.
        """
        # Gradient energy (discretized)
        grad_u = np.gradient(u)
        grad_energy = 0.5 * self.diffusion_coeff * np.sum(grad_u ** 2)

        # Potential energy U(u) = -λ/2·u² + λ/4·u⁴
        lambda_pot = self.reaction_strength * self.rule_parameters["bifurcation_strength"]
        potential = np.sum(-lambda_pot / 2 * u ** 2 + lambda_pot / 4 * u ** 4)

        return grad_energy + potential

    def compute_order_parameter(self, u: np.ndarray) -> float:
        """
        Compute order parameter measuring pattern formation.

        ψ = sqrt(1/N · Σᵢ |uᵢ|²)

        Args:
            u: Activation field.

        Returns:
            Order parameter in [0, 1].
        """
        return np.sqrt(np.mean(u ** 2))
