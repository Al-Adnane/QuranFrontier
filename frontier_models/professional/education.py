"""Education Pedagogy Network - Learning Methods.

Inspired by: Education Theory
"""

import torch
import torch.nn as nn


class EducationPedagogyNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Learning styles
        self.visual = nn.Linear(input_dim, embed_dim)
        self.auditory = nn.Linear(input_dim, embed_dim)
        self.kinesthetic = nn.Linear(input_dim, embed_dim)
        # Teaching methods
        self.lecture = nn.Linear(input_dim, embed_dim)
        self.discussion = nn.Linear(input_dim, embed_dim)
        self.hands_on = nn.Linear(input_dim, embed_dim)
        # Learning outcome
        self.outcome = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        styles = [self.visual(x), self.auditory(x), self.kinesthetic(x)]
        methods = [self.lecture(x), self.discussion(x), self.hands_on(x)]
        return {
            'learning_styles': {
                'visual': self.visual(x),
                'auditory': self.auditory(x),
                'kinesthetic': self.kinesthetic(x)
            },
            'teaching_methods': {
                'lecture': self.lecture(x),
                'discussion': self.discussion(x),
                'hands_on': self.hands_on(x)
            },
            'learning_outcome': torch.sigmoid(self.outcome(torch.cat(styles + methods, -1)))
        }


def create_education_pedagogy_network(input_dim: int = 128, embed_dim: int = 256):
    return EducationPedagogyNetwork(input_dim, embed_dim)
