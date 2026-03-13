"""Temporal Prediction Network - Predictive Processing Architecture.

Implements predictive processing / active inference framework:
- Brain as prediction machine
- Minimize prediction error (free energy)
- Hierarchical predictions
- Precision-weighted updates

Architecture:
    Hierarchical Layers: Each level predicts level below
    Prediction Errors: Bottom-up error signals
    Precision Weighting: Attention modulates error signals
    Action: Change world to match predictions

Applications:
- Sequence prediction
- Anomaly detection
- Active learning
- Robot control
"""

import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PredictionState:
    """State of predictive processing."""
    predictions: List[torch.Tensor]
    prediction_errors: List[torch.Tensor]
    free_energy: float
    precision: torch.Tensor


class PredictionLayer(nn.Module):
    """Single layer in predictive hierarchy."""
    
    def __init__(self, input_dim: int, hidden_dim: int = 256):
        super().__init__()
        
        # Top-down prediction generator
        self.predict = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, input_dim)
        )
        
        # Bottom-up error encoder
        self.encode_error = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # Precision estimation (attention)
        self.precision = nn.Sequential(
            nn.Linear(input_dim, 1),
            nn.Sigmoid()
        )
        
    def forward(
        self,
        input_data: torch.Tensor,
        top_prediction: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Process input with prediction.
        
        Returns: prediction, prediction_error, precision
        """
        if top_prediction is not None:
            prediction = self.predict(top_prediction)
        else:
            prediction = torch.zeros_like(input_data)
        
        # Compute prediction error
        error = input_data - prediction
        
        # Encode error
        encoded_error = self.encode_error(error)
        
        # Estimate precision (how much to trust this error)
        prec = self.precision(error)
        
        return prediction, encoded_error, prec


class TemporalPredictionNetwork(nn.Module):
    """Hierarchical temporal prediction network.
    
    Implements predictive processing across time and abstraction levels.
    """
    
    def __init__(
        self,
        input_dim: int = 128,
        hidden_dim: int = 256,
        num_levels: int = 4,
        sequence_length: int = 32
    ):
        super().__init__()
        
        self.num_levels = num_levels
        self.sequence_length = sequence_length
        
        # Hierarchical prediction layers
        self.layers = nn.ModuleList([
            PredictionLayer(input_dim if i == 0 else hidden_dim, hidden_dim)
            for i in range(num_levels)
        ])
        
        # Temporal dynamics (LSTM for each level)
        self.temporal = nn.ModuleList([
            nn.LSTM(hidden_dim, hidden_dim, batch_first=True)
            for _ in range(num_levels)
        ])
        
        # Action generator (active inference)
        self.action_head = nn.Sequential(
            nn.Linear(hidden_dim * num_levels, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, input_dim)
        )
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        
    def predict_sequence(
        self,
        observed: torch.Tensor,
        num_steps: int = 10
    ) -> PredictionState:
        """Predict future sequence.
        
        Args:
            observed: [batch, seq_len, input_dim] observed sequence
            num_steps: Number of steps to predict
        Returns:
            PredictionState with predictions and errors
        """
        batch_size = observed.size(0)
        seq_len = observed.size(1)
        
        # Initialize hidden states at each level
        hidden_states = [
            torch.zeros(batch_size, self.hidden_dim, device=observed.device)
            for _ in range(self.num_levels)
        ]
        
        predictions = []
        prediction_errors = []
        total_free_energy = 0.0
        
        # Process observed sequence
        for t in range(seq_len):
            input_data = observed[:, t, :]
            
            level_predictions = []
            level_errors = []
            
            # Bottom-up pass through hierarchy
            for level in range(self.num_levels):
                # Get top-down prediction
                top_pred = hidden_states[level - 1] if level > 0 else None
                
                # Process at this level
                pred, error, precision = self.layers[level](input_data, top_pred)
                
                # Update hidden state with error (precision-weighted)
                hidden_states[level] = hidden_states[level] + error * precision.squeeze(-1)
                
                # Temporal dynamics
                hidden_states[level], _ = self.temporal[level](
                    hidden_states[level].unsqueeze(1)
                )
                hidden_states[level] = hidden_states[level].squeeze(1)
                
                level_predictions.append(pred)
                level_errors.append(error)
                
                # Free energy (prediction error weighted by precision)
                free_energy = (error ** 2 * precision).sum(dim=-1).mean()
                total_free_energy += free_energy.item()
                
                # Pass encoded error up
                input_data = error
            
            predictions.append(level_predictions)
            prediction_errors.append(level_errors)
        
        # Generate future predictions
        future_predictions = []
        for _ in range(num_steps):
            future = []
            for level in range(self.num_levels):
                top_pred = hidden_states[level - 1] if level > 0 else None
                
                # Create dummy input with correct dimension
                dummy_input = torch.zeros(batch_size, self.input_dim if level == 0 else self.hidden_dim, device=observed.device)
                pred, _, _ = self.layers[level](dummy_input, top_pred)
                future.append(pred)
            future_predictions.append(future)
        
        return PredictionState(
            predictions=predictions,
            prediction_errors=prediction_errors,
            free_energy=total_free_energy,
            precision=torch.tensor(1.0)  # Simplified precision measure
        )
    
    def take_action(
        self,
        hidden_states: List[torch.Tensor],
        target: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Generate action to minimize prediction error (active inference).
        
        Action changes the world to match predictions.
        """
        # Handle dimension mismatch
        if len(hidden_states) > 0:
            combined = torch.cat([h if h.dim() == 2 else h.unsqueeze(0) for h in hidden_states], dim=-1)
            # Resize action head if needed
            if combined.size(-1) != self.action_head[0].in_features:
                self.action_head[0] = nn.Linear(combined.size(-1), self.hidden_dim).to(combined.device)
            action = self.action_head(combined)
        else:
            action = torch.zeros_like(target)
        
        # Action aims to reduce prediction error
        prediction_error = target - action.squeeze(0) if action.dim() > 1 else target - action
        
        return action, prediction_error
    
    def forward(
        self,
        observed: torch.Tensor,
        target: Optional[torch.Tensor] = None
    ) -> Dict:
        """Forward pass."""
        state = self.predict_sequence(observed)
        
        result = {
            'predictions': state.predictions[-1],  # Top level predictions
            'errors': state.prediction_errors[-1],
            'free_energy': state.free_energy,
            'precision': state.precision
        }
        
        if target is not None:
            action, error = self.take_action(
                [state.predictions[-1][-1]],
                target
            )
            result['action'] = action
            result['action_error'] = error
        
        return result


def create_temporal_prediction_network(
    input_dim: int = 128,
    hidden_dim: int = 256,
    num_levels: int = 4
) -> TemporalPredictionNetwork:
    """Create TemporalPredictionNetwork."""
    return TemporalPredictionNetwork(input_dim, hidden_dim, num_levels)
