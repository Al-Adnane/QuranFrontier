"""Consciousness Integration Network - Global Workspace Theory Implementation.

Implements aspects of consciousness based on:
1. Global Workspace Theory (Baars, Dehaene)
2. Integrated Information Theory (Tononi)
3. Predictive Processing (Friston)

Architecture:
    Specialized Modules: Unconscious processors (vision, language, memory)
    Global Workspace: Broadcast medium for conscious access
    Attention Mechanism: Selects what enters consciousness
    Integration: Combines information across modules
    Report: Conscious output

Applications:
- Explainable AI (what the model is "aware" of)
- Attention modeling
- Multi-modal integration
- Cognitive architecture research
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class ConsciousState:
    """State of conscious processing."""
    workspace_content: torch.Tensor
    active_modules: List[str]
    integration_level: float
    phi: float  # Integrated information measure
    report: str


class SpecializedModule(nn.Module):
    """Unconscious specialized processor (e.g., vision, language)."""
    
    def __init__(self, name: str, input_dim: int, hidden_dim: int = 256):
        super().__init__()
        self.name = name
        self.processor = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim)
        )
        self.salience_head = nn.Linear(hidden_dim, 1)  # How important is this?
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Process input and compute salience."""
        processed = self.processor(x)
        salience = torch.sigmoid(self.salience_head(processed))
        return processed, salience


class GlobalWorkspace(nn.Module):
    """Global workspace for conscious broadcasting."""
    
    def __init__(self, workspace_dim: int = 512, capacity: int = 10):
        super().__init__()
        self.workspace_dim = workspace_dim
        self.capacity = capacity
        
        # Workspace state (can hold multiple items)
        self.workspace = nn.Parameter(torch.zeros(capacity, workspace_dim))
        self.workspace_mask = nn.Parameter(torch.zeros(capacity))
        
        # Broadcasting
        self.broadcast_net = nn.Linear(workspace_dim, workspace_dim)
        
    def enter(self, content: torch.Tensor, salience: torch.Tensor) -> bool:
        """Attempt to enter workspace (become conscious).
        
        Returns True if successful.
        """
        # Find available slot
        available = (self.workspace_mask < 0.5).nonzero(as_tuple=True)[0]
        
        if len(available) == 0:
            # Replace lowest salience item
            saliences = self.workspace_mask
            lowest = saliences.argmin()
            idx = lowest
        else:
            idx = available[0]
        
        # Enter workspace
        self.workspace.data[idx] = content.detach()
        self.workspace_mask.data[idx] = salience.detach()
        
        return True
    
    def broadcast(self) -> torch.Tensor:
        """Broadcast workspace content to all modules."""
        # Weighted sum of workspace items
        weights = F.softmax(self.workspace_mask, dim=0)
        broadcast = (self.workspace * weights.unsqueeze(-1)).sum(dim=0)
        return self.broadcast_net(broadcast)
    
    def clear(self):
        """Clear workspace (attention shift)."""
        self.workspace_mask.data.fill_(0)


class IntegrationMeasure(nn.Module):
    """Computes integrated information (Phi-like measure)."""
    
    def __init__(self, workspace_dim: int = 512):
        super().__init__()
        self.projection = nn.Linear(workspace_dim, workspace_dim)
        
    def forward(
        self,
        whole: torch.Tensor,
        parts: List[torch.Tensor]
    ) -> float:
        """Compute integration level.
        
        Phi = Information(whole) - sum(Information(parts))
        """
        # Whole system information
        whole_info = torch.norm(self.projection(whole), dim=-1)
        
        # Sum of part information
        parts_info = sum(torch.norm(self.projection(p), dim=-1) for p in parts)
        
        # Integration (synergy)
        integration = whole_info - parts_info
        
        return max(0, integration.item())


class ConsciousnessIntegrationNetwork(nn.Module):
    """Main consciousness integration network.
    
    Implements global workspace architecture with specialized modules
    and conscious broadcasting.
    """
    
    def __init__(
        self,
        input_dims: Dict[str, int],
        workspace_dim: int = 512,
        hidden_dim: int = 256
    ):
        super().__init__()
        
        # Create specialized modules
        self.proc_modules = nn.ModuleDict({
            name: SpecializedModule(name, dim, hidden_dim)
            for name, dim in input_dims.items()
        })
        
        # Global workspace
        self.workspace = GlobalWorkspace(workspace_dim)
        
        # Integration measure
        self.integration = IntegrationMeasure(workspace_dim)
        
        # Attention selector
        self.attention = nn.MultiheadAttention(workspace_dim, num_heads=8)
        
        # Report generation
        self.report_head = nn.Sequential(
            nn.Linear(workspace_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 100)  # Vocabulary size for report
        )
        
        self.workspace_dim = workspace_dim
        self.input_dims = input_dims
        
    def process(
        self,
        inputs: Dict[str, torch.Tensor],
        report: bool = True
    ) -> ConsciousState:
        """Process inputs through consciousness architecture."""
        
        # Phase 1: Unconscious processing in parallel
        module_outputs = {}
        saliences = {}
        
        for name, input_tensor in inputs.items():
            if name in self.proc_modules:
                output, salience = self.proc_modules[name](input_tensor)
                module_outputs[name] = output
                saliences[name] = salience
        
        # Phase 2: Attention selection (what enters consciousness)
        active_modules = []
        for name, salience in saliences.items():
            if salience > 0.5:  # Threshold for conscious access
                self.workspace.enter(module_outputs[name], salience)
                active_modules.append(name)
        
        # Phase 3: Broadcasting
        broadcast = self.workspace.broadcast()
        
        # Phase 4: Integration
        parts = [module_outputs[name] for name in active_modules]
        phi = self.integration(broadcast, parts) if parts else 0.0
        
        # Phase 5: Report (if requested)
        report_text = ""
        if report:
            report_logits = self.report_head(broadcast)
            report_text = f"Conscious of: {', '.join(active_modules)}"
        
        return ConsciousState(
            workspace_content=broadcast,
            active_modules=active_modules,
            integration_level=len(active_modules) / len(self.proc_modules) if self.proc_modules else 0,
            phi=phi,
            report=report_text
        )
    
    def attend_to(self, module_name: str) -> bool:
        """Shift attention to specific module."""
        if module_name in self.proc_modules:
            self.workspace.clear()
            return True
        return False
    
    def forward(
        self,
        inputs: Dict[str, torch.Tensor]
    ) -> Dict[str, Any]:
        """Forward pass."""
        state = self.process(inputs)
        
        return {
            'workspace': state.workspace_content,
            'active_modules': state.active_modules,
            'integration': state.integration_level,
            'phi': state.phi,
            'report': state.report
        }


def create_consciousness_network(
    input_dims: Dict[str, int] = None,
    workspace_dim: int = 512
) -> ConsciousnessIntegrationNetwork:
    """Create ConsciousnessIntegrationNetwork."""
    if input_dims is None:
        input_dims = {
            'vision': 512,
            'language': 768,
            'memory': 256,
            'emotion': 128
        }
    return ConsciousnessIntegrationNetwork(input_dims, workspace_dim)
