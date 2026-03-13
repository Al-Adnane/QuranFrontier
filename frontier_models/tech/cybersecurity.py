"""Cybersecurity Network - Threat Detection.

Inspired by: Cybersecurity
"""

import torch
import torch.nn as nn


class CybersecurityNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256):
        super().__init__()
        # Threat types
        self.malware = nn.Linear(input_dim, embed_dim)
        self.phishing = nn.Linear(input_dim, embed_dim)
        self.ransomware = nn.Linear(input_dim, embed_dim)
        self.ddos = nn.Linear(input_dim, embed_dim)
        # Defense mechanisms
        self.firewall = nn.Linear(input_dim, embed_dim)
        self.ids = nn.Linear(input_dim, embed_dim)  # Intrusion Detection System
        # Security score
        self.security = nn.Linear(embed_dim * 6, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        threats = [self.malware(x), self.phishing(x), self.ransomware(x), self.ddos(x)]
        defense = [self.firewall(x), self.ids(x)]
        return {
            'threats': {
                'malware': self.malware(x),
                'phishing': self.phishing(x),
                'ransomware': self.ransomware(x),
                'ddos': self.ddos(x)
            },
            'defense': {
                'firewall': self.firewall(x),
                'intrusion_detection': self.ids(x)
            },
            'security_score': torch.sigmoid(self.security(torch.cat(threats + defense, -1)))
        }


def create_cybersecurity_network(input_dim: int = 128, embed_dim: int = 256):
    return CybersecurityNetwork(input_dim, embed_dim)
