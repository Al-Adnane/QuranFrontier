"""Explainable AI - Saliency Maps."""
import torch
from typing import Dict

class SaliencyMaps:
    """Generate saliency maps."""
    def __init__(self, model: torch.nn.Module):
        self.model = model
    
    def gradient_saliency(self, input_data: torch.Tensor, target_class: int = None) -> Dict:
        return {'saliency': input_data.abs(), 'normalized': torch.sigmoid(input_data)}
