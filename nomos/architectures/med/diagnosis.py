"""Diagnosis Network - Medical Diagnosis.

Inspired by: Medical Diagnosis
"""

import torch
import torch.nn as nn


class DiagnosisNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256, num_symptoms: int = 20):
        super().__init__()
        self.symptoms = nn.Linear(input_dim, num_symptoms)
        self.diagnosis = nn.Linear(num_symptoms, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        symptoms = torch.sigmoid(self.symptoms(x))
        return {'symptoms': symptoms, 'diagnosis': torch.sigmoid(self.diagnosis(symptoms))}


def create_diagnosis_network(input_dim: int = 128, embed_dim: int = 256):
    return DiagnosisNetwork(input_dim, embed_dim)
