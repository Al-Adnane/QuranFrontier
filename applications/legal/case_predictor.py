"""Case Outcome Predictor for Legal."""
import torch
import torch.nn as nn

class CasePredictor(nn.Module):
    """AI-powered legal case outcome prediction."""
    def __init__(self, embed_dim=256):
        super().__init__()
        self.predictor = nn.Linear(512, 3)
    
    def forward(self, case_features: torch.Tensor, precedent: torch.Tensor) -> dict:
        combined = torch.cat([case_features, precedent], dim=-1)
        outcome = torch.softmax(self.predictor(combined), dim=-1)
        return {'outcome': outcome, 'confidence': outcome.max(dim=-1).values}
