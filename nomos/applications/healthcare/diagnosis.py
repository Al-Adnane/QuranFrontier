"""Medical Diagnosis System."""
import torch
import torch.nn as nn
from typing import Dict, List

class MedicalDiagnosis(nn.Module):
    """AI-powered medical diagnosis assistant."""
    def __init__(self, input_dim: int = 512, num_conditions: int = 100):
        super().__init__()
        self.symptom_encoder = nn.Embedding(200, 128)
        self.diagnosis_network = nn.Sequential(nn.Linear(128, 256), nn.ReLU(), nn.Linear(256, num_conditions))
    
    def forward(self, symptoms: torch.Tensor) -> Dict:
        symptom_emb = self.symptom_encoder(symptoms).mean(dim=1)
        logits = self.diagnosis_network(symptom_emb)
        return {'diagnoses': logits.argmax(dim=-1), 'confidence': torch.sigmoid(logits).max(dim=-1).values}
