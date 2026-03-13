"""
Active Inference with Predictive Processing for Embodied Tajweed.

Implements the Free Energy Principle:
    F[q] = E_q[ln q(θ) - ln p(o,θ)] = KL[q||p] - E_q[ln p(o|θ)]

The agent maintains a generative model p(o,θ) encoding:
- Prior beliefs p(θ) from embodied schemata (vocal tract dynamics)
- Likelihood p(o|θ) mapping states to tajweed acoustic features
- Approximate posterior q(θ) minimizing KL divergence

Precision weighting (inverse temperature) determines which errors are minimized:
    F[q] = Σᵢ πᵢ·||oᵢ - μ(θ)||²/2 + KL[q||p]

where πᵢ = precision (higher = lower expected noise).
"""

import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, Tuple, Optional
import numpy as np


class VariationalFreeEnergy(nn.Module):
    """
    Variational Free Energy computation.

    Implements the bound: F[q] = KL[q(θ)||p(θ)] - E_q[ln p(o|θ)]

    Uses neural network parametrization:
    - Prior p(θ) ~ N(μ₀, Σ₀)
    - Posterior q(θ|o) ~ N(μ(o), Σ(o))
    - Likelihood p(o|θ) ~ N(f(θ), σ²)
    """

    def __init__(self, feature_dim: int, latent_dim: int):
        """
        Initialize VFE computation.

        Args:
            feature_dim: Dimensionality of observations (acoustic features).
            latent_dim: Dimensionality of latent states (articulatory).
        """
        super().__init__()
        self.feature_dim = feature_dim
        self.latent_dim = latent_dim

        # Prior parameters (learnable)
        self.register_buffer("mu_prior", torch.zeros(latent_dim))
        self.register_buffer("log_sigma_prior", torch.zeros(latent_dim))

        # Encoder: o → (μ(o), σ(o))
        self.encoder = nn.Sequential(
            nn.Linear(feature_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, latent_dim * 2),
        )

        # Decoder: θ → o_recon
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, feature_dim),
        )

        # Log likelihood variance (learnable)
        self.log_likelihood_var = nn.Parameter(torch.tensor(0.0))

    def encode(self, observations: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Encode observations to latent distribution parameters.

        Args:
            observations: Shape (batch, feature_dim).

        Returns:
            (mu, log_sigma) of posterior q(θ|o).
        """
        params = self.encoder(observations)
        mu = params[:, : self.latent_dim]
        log_sigma = params[:, self.latent_dim :]
        return mu, log_sigma

    def decode(self, latents: torch.Tensor) -> torch.Tensor:
        """
        Decode latents to observation reconstruction.

        Args:
            latents: Shape (batch, latent_dim).

        Returns:
            Reconstructed observations shape (batch, feature_dim).
        """
        return self.decoder(latents)

    def reparameterize(self, mu: torch.Tensor, log_sigma: torch.Tensor) -> torch.Tensor:
        """
        Sample from q(θ|o) using reparameterization trick.

        Args:
            mu: Mean of posterior.
            log_sigma: Log-scale of posterior.

        Returns:
            Sample from q(θ|o).
        """
        sigma = torch.exp(log_sigma)
        epsilon = torch.randn_like(sigma)
        return mu + sigma * epsilon

    def forward(
        self,
        observations: torch.Tensor,
        beliefs: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Compute variational free energy.

        F[q] = KL[q(θ|o)||p(θ)] - E_q[ln p(o|θ)]

        Args:
            observations: Shape (batch, feature_dim).
            beliefs: Optional pre-computed beliefs (batch, latent_dim).

        Returns:
            VFE scalar (summed over batch).
        """
        # Encode observations
        mu_post, log_sigma_post = self.encode(observations)
        sigma_post = torch.exp(log_sigma_post)

        if beliefs is None:
            # Sample from posterior
            beliefs = self.reparameterize(mu_post, log_sigma_post)

        # Reconstruction error (likelihood term)
        recon = self.decode(beliefs)
        likelihood_var = torch.exp(self.log_likelihood_var)
        recon_error = torch.sum((observations - recon) ** 2 / (2 * likelihood_var), dim=1)

        # KL divergence (prior term)
        sigma_prior = torch.exp(self.log_sigma_prior)
        kl_divergence = 0.5 * torch.sum(
            (sigma_post / sigma_prior) ** 2
            + ((mu_post - self.mu_prior) / sigma_prior) ** 2
            - 1.0
            - 2 * (log_sigma_post - self.log_sigma_prior),
            dim=1,
        )

        # Total VFE
        vfe = recon_error + kl_divergence
        return vfe.sum()


class ActiveInference(nn.Module):
    """
    Active inference agent using predictive processing.

    Minimizes variational free energy by:
    1. Updating beliefs q(θ) toward observations
    2. Updating generative model p(o,θ) to explain data
    3. Computing precision weighting for uncertainty
    """

    def __init__(
        self,
        feature_dim: int,
        latent_dim: int,
        learning_rate: float = 0.001,
        update_steps: int = 1,
    ):
        """
        Initialize active inference agent.

        Args:
            feature_dim: Observation dimensionality.
            latent_dim: Latent state dimensionality.
            learning_rate: Optimizer learning rate.
            update_steps: Number of belief update steps per observation.
        """
        super().__init__()
        self.feature_dim = feature_dim
        self.latent_dim = latent_dim
        self.learning_rate = learning_rate
        self.update_steps = update_steps

        # Variational free energy computation
        self.vfe = VariationalFreeEnergy(feature_dim, latent_dim)

        # Belief representation (learnable)
        self.beliefs = nn.Parameter(torch.randn(1, latent_dim) * 0.1)

        # Precision parameters (one per feature dimension)
        self.log_precision = nn.Parameter(torch.zeros(feature_dim))

        # Optimizer for belief updates
        self.optimizer = optim.Adam([self.beliefs], lr=learning_rate)

    def get_precision_weights(self) -> torch.Tensor:
        """
        Get precision weighting for each feature dimension.

        Returns:
            Precision weights shape (feature_dim,).
        """
        return torch.exp(self.log_precision)

    def compute_precision_weight(self, observations: torch.Tensor) -> torch.Tensor:
        """
        Compute expected precision (inverse variance) of observations.

        Uses empirical variance estimation:
            π = 1 / E[||o - E[o]||²]

        Args:
            observations: Shape (batch, feature_dim).

        Returns:
            Scalar precision weight.
        """
        mean = torch.mean(observations, dim=0)
        variance = torch.mean((observations - mean) ** 2)
        precision = 1.0 / (variance + 1e-6)
        return precision

    def update_beliefs(self, observations: torch.Tensor) -> torch.Tensor:
        """
        Update beliefs to minimize prediction error.

        Gradient descent on: L = ||o - μ(θ)||² + λ·KL[q||p]

        Args:
            observations: Shape (batch, feature_dim).

        Returns:
            Updated beliefs shape (1, latent_dim).
        """
        for _ in range(self.update_steps):
            self.optimizer.zero_grad()

            # Reconstruct from current beliefs
            reconstruction = self.vfe.decode(self.beliefs)

            # Prediction error (minimized precision-weighted)
            precision = self.get_precision_weights()
            pred_error = torch.sum(precision * (observations - reconstruction) ** 2)

            # KL regularization (ensure beliefs match prior)
            mu_prior = self.vfe.mu_prior
            sigma_prior = torch.exp(self.vfe.log_sigma_prior)
            kl_reg = 0.5 * torch.sum(
                ((self.beliefs - mu_prior) / sigma_prior) ** 2
            )

            # Total loss
            loss = pred_error + 0.1 * kl_reg
            loss.backward()
            self.optimizer.step()

        return self.beliefs.detach()

    def decode_beliefs(self) -> torch.Tensor:
        """
        Decode beliefs to observation space (prediction).

        Returns:
            Predicted observations shape (1, feature_dim).
        """
        return self.vfe.decode(self.beliefs)

    def get_prior_beliefs(self) -> torch.Tensor:
        """
        Get prior belief distribution p(θ).

        Returns:
            Mean of prior shape (latent_dim,).
        """
        return self.vfe.mu_prior.clone()

    def compute_prediction_error(self, observations: torch.Tensor) -> torch.Tensor:
        """
        Compute weighted prediction error.

        Error = Σᵢ πᵢ·(oᵢ - f_i(θ))²

        Args:
            observations: Shape (batch, feature_dim).

        Returns:
            Prediction error scalar.
        """
        reconstruction = self.decode_beliefs()
        precision = self.get_precision_weights()
        error = torch.sum(precision * (observations - reconstruction) ** 2)
        return error

    def compute_free_energy(self, observations: torch.Tensor) -> torch.Tensor:
        """
        Compute variational free energy.

        Args:
            observations: Shape (batch, feature_dim).

        Returns:
            VFE scalar.
        """
        return self.vfe(observations, self.beliefs)

    def get_uncertainty(self) -> torch.Tensor:
        """
        Get epistemic uncertainty (inverse precision).

        Returns:
            Uncertainty per feature dimension shape (feature_dim,).
        """
        return 1.0 / (self.get_precision_weights() + 1e-6)

    def set_precision(self, precision_values: torch.Tensor) -> None:
        """
        Set precision weights manually (for tajweed rule weighting).

        Args:
            precision_values: Shape (feature_dim,).
        """
        self.log_precision.data = torch.log(precision_values + 1e-6)


class PrecisionWeighting(nn.Module):
    """
    Precision-weighted prediction error for tajweed rules.

    Implements confidence-scaling for different tajweed rule contexts:
    - High precision for critical tajweed rules (e.g., idgham)
    - Low precision for optional embellishments
    """

    def __init__(self, num_rules: int, feature_dim: int):
        """
        Initialize precision weighting module.

        Args:
            num_rules: Number of tajweed rules.
            feature_dim: Feature dimensionality.
        """
        super().__init__()
        self.num_rules = num_rules
        self.feature_dim = feature_dim

        # Learnable precision per rule
        self.rule_precisions = nn.Parameter(torch.ones(num_rules, feature_dim))

    def forward(
        self,
        prediction_error: torch.Tensor,
        rule_activations: torch.Tensor,
    ) -> torch.Tensor:
        """
        Compute rule-weighted prediction error.

        Args:
            prediction_error: Shape (batch, feature_dim).
            rule_activations: Shape (batch, num_rules).

        Returns:
            Weighted error scalar.
        """
        # Average precision over active rules
        active_precisions = torch.einsum("br,rf->bf", rule_activations, self.rule_precisions)

        # Weight prediction error
        weighted_error = torch.sum(active_precisions * prediction_error ** 2)

        return weighted_error
