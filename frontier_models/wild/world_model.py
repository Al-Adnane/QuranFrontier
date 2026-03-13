"""World Model - Internal Environment Simulation.

Implements world models for planning and decision making:
- Learn environment dynamics in latent space
- Predict future states and rewards
- Plan by simulating trajectories internally
- Dream to improve policy without real interaction

Architecture:
    VAE: Encode observations to latent
    Dynamics: Predict next latent state
    Reward: Predict reward from latent
    Planner: Optimize actions in latent space

Based on Ha & Schmidhuber "World Models" (2018).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class WorldModelState:
    """State of world model."""
    latent: torch.Tensor
    predicted_next: torch.Tensor
    predicted_reward: torch.Tensor
    prediction_error: float


class WorldVAE(nn.Module):
    """Variational Autoencoder for observations."""
    
    def __init__(self, obs_dim: int = 64, latent_dim: int = 32):
        super().__init__()
        self.latent_dim = latent_dim
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(obs_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU()
        )
        self.mu_head = nn.Linear(64, latent_dim)
        self.logvar_head = nn.Linear(64, latent_dim)
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, obs_dim)
        )
        
    def encode(self, obs: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode observation to latent distribution."""
        h = self.encoder(obs)
        mu = self.mu_head(h)
        logvar = self.logvar_head(h)
        return mu, logvar
    
    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """Reparameterization trick."""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent to observation."""
        return self.decoder(z)
    
    def forward(self, obs: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """VAE forward pass."""
        mu, logvar = self.encode(obs)
        z = self.reparameterize(mu, logvar)
        recon = self.decode(z)
        
        # Compute KL divergence
        kl = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
        
        # Compute reconstruction loss
        recon_loss = F.mse_loss(recon, obs)
        
        return z, recon_loss, kl


class DynamicsModel(nn.Module):
    """Predicts next latent state given current state and action."""
    
    def __init__(self, latent_dim: int = 32, action_dim: int = 4):
        super().__init__()
        
        self.dynamics = nn.Sequential(
            nn.Linear(latent_dim + action_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, latent_dim)
        )
        
    def forward(
        self,
        z: torch.Tensor,
        action: torch.Tensor
    ) -> torch.Tensor:
        """Predict next latent state."""
        combined = torch.cat([z, action], dim=-1)
        return self.dynamics(combined)


class RewardModel(nn.Module):
    """Predicts reward from latent state and action."""
    
    def __init__(self, latent_dim: int = 32, action_dim: int = 4):
        super().__init__()
        
        self.reward_net = nn.Sequential(
            nn.Linear(latent_dim + action_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        
    def forward(self, z: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """Predict reward."""
        combined = torch.cat([z, action], dim=-1)
        return self.reward_net(combined).squeeze(-1)


class LatentPlanner(nn.Module):
    """Plans actions in latent space using world model."""
    
    def __init__(
        self,
        latent_dim: int = 32,
        action_dim: int = 4,
        planning_horizon: int = 10
    ):
        super().__init__()
        self.latent_dim = latent_dim
        self.action_dim = action_dim
        self.planning_horizon = planning_horizon
        
        # Action proposal network
        self.proposer = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim * planning_horizon)
        )
        
    def propose_actions(self, z: torch.Tensor) -> torch.Tensor:
        """Propose action sequence from latent state."""
        actions = self.proposer(z)
        actions = actions.view(-1, self.planning_horizon, self.action_dim)
        return torch.tanh(actions)  # Bound actions
    
    def evaluate_plan(
        self,
        z: torch.Tensor,
        actions: torch.Tensor,
        dynamics: DynamicsModel,
        reward: RewardModel
    ) -> torch.Tensor:
        """Evaluate action sequence using world model."""
        total_reward = 0.0
        current_z = z
        
        for t in range(actions.size(1)):
            action = actions[:, t, :]
            
            # Predict next state
            next_z = dynamics(current_z, action)
            
            # Predict reward
            r = reward(current_z, action)
            total_reward = total_reward + r
            
            current_z = next_z
        
        return total_reward


class WorldModel(nn.Module):
    """Complete World Model for planning and decision making.
    
    Applications:
    - Model-based reinforcement learning
    - Planning in simulated environments
    - Sample-efficient learning
    """
    
    def __init__(
        self,
        obs_dim: int = 64,
        latent_dim: int = 32,
        action_dim: int = 4
    ):
        super().__init__()
        
        self.vae = WorldVAE(obs_dim, latent_dim)
        self.dynamics = DynamicsModel(latent_dim, action_dim)
        self.reward = RewardModel(latent_dim, action_dim)
        self.planner = LatentPlanner(latent_dim, action_dim)
        
        self.latent_dim = latent_dim
        self.action_dim = action_dim
        
    def encode(self, obs: torch.Tensor) -> torch.Tensor:
        """Encode observation to latent."""
        mu, logvar = self.vae.encode(obs)
        return self.vae.reparameterize(mu, logvar)
    
    def predict(
        self,
        z: torch.Tensor,
        action: torch.Tensor
    ) -> WorldModelState:
        """Predict next state and reward."""
        next_z = self.dynamics(z, action)
        reward = self.reward(z, action)
        
        return WorldModelState(
            latent=z,
            predicted_next=next_z,
            predicted_reward=reward,
            prediction_error=0.0
        )
    
    def plan(
        self,
        z: torch.Tensor,
        num_samples: int = 100
    ) -> torch.Tensor:
        """Plan optimal action sequence in latent space."""
        best_actions = None
        best_reward = float('-inf')
        
        for _ in range(num_samples):
            # Propose actions
            actions = self.planner.propose_actions(z)
            
            # Evaluate
            total_reward = self.planner.evaluate_plan(
                z, actions, self.dynamics, self.reward
            )
            
            # Keep best
            if total_reward > best_reward:
                best_reward = total_reward
                best_actions = actions
        
        return best_actions
    
    def train_step(
        self,
        obs: torch.Tensor,
        action: torch.Tensor,
        next_obs: torch.Tensor,
        reward: torch.Tensor,
        optimizer: torch.optim.Optimizer
    ) -> Dict:
        """Training step."""
        self.train()
        
        # Encode observations
        z, vae_recon, vae_kl = self.vae(obs)
        z_next, _, _ = self.vae.encode(next_obs)
        
        # Predict next state
        predicted_z = self.dynamics(z, action)
        dynamics_loss = F.mse_loss(predicted_z, z_next.detach())
        
        # Predict reward
        predicted_reward = self.reward(z, action)
        reward_loss = F.mse_loss(predicted_reward, reward)
        
        # Total loss
        total_loss = (
            vae_recon + 0.001 * vae_kl +
            dynamics_loss + reward_loss
        )
        
        # Optimize
        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()
        
        return {
            'total_loss': total_loss.item(),
            'vae_recon': vae_recon.item(),
            'vae_kl': vae_kl.item(),
            'dynamics_loss': dynamics_loss.item(),
            'reward_loss': reward_loss.item()
        }
    
    def forward(
        self,
        obs: torch.Tensor,
        action: Optional[torch.Tensor] = None,
        plan: bool = False
    ) -> Dict:
        """Forward pass."""
        # Encode
        z = self.encode(obs)
        
        result = {'latent': z}
        
        if action is not None:
            # Predict
            state = self.predict(z, action)
            result['predicted_next'] = state.predicted_next
            result['predicted_reward'] = state.predicted_reward
        
        if plan:
            # Plan optimal actions
            actions = self.plan(z)
            result['planned_actions'] = actions
        
        return result


def create_world_model(
    obs_dim: int = 64,
    latent_dim: int = 32,
    action_dim: int = 4
) -> WorldModel:
    """Create WorldModel."""
    return WorldModel(obs_dim, latent_dim, action_dim)
