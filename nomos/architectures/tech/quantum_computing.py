"""Quantum Computing Network - Qubits and Gates.

Inspired by: Quantum Computing
"""

import torch
import torch.nn as nn


class QuantumComputingNetwork(nn.Module):
    def __init__(self, input_dim: int = 128, embed_dim: int = 256, num_qubits: int = 8):
        super().__init__()
        self.qubits = nn.ModuleList([nn.Linear(input_dim, embed_dim) for _ in range(num_qubits)])
        # Quantum gates
        self.hadamard = nn.Linear(embed_dim, embed_dim)
        self.cnot = nn.Linear(embed_dim * 2, embed_dim)
        self.phase = nn.Linear(embed_dim, embed_dim)
        # Quantum circuit
        self.circuit = nn.Linear(embed_dim * num_qubits, 1)
        
    def forward(self, x: torch.Tensor) -> dict:
        qubit_embs = [q(x) for q in self.qubits]
        return {
            'qubits': qubit_embs,
            'gates': {
                'hadamard': self.hadamard(qubit_embs[0]),
                'cnot': self.cnot(torch.cat(qubit_embs[:2], -1)),
                'phase': self.phase(qubit_embs[0])
            },
            'circuit_output': torch.sigmoid(self.circuit(torch.cat(qubit_embs, -1))),
            'entanglement': torch.sigmoid(torch.stack(qubit_embs).std(dim=0).mean(dim=-1, keepdim=True))
        }


def create_quantum_computing_network(input_dim: int = 128, embed_dim: int = 256):
    return QuantumComputingNetwork(input_dim, embed_dim)
