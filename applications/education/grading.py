"""Automated Grading System."""
import torch
import torch.nn as nn

class AutomatedGrading(nn.Module):
    """AI-powered automated grading."""
    def __init__(self, embed_dim=256):
        super().__init__()
        self.encoder = nn.Linear(512, embed_dim)
        self.grader = nn.Linear(embed_dim, 1)
    
    def forward(self, submission: torch.Tensor, rubric: torch.Tensor) -> dict:
        encoded = self.encoder(torch.cat([submission, rubric], dim=-1))
        grade = torch.sigmoid(self.grader(encoded))
        return {'grade': grade, 'feedback_embedding': encoded}
