"""Meta-Learning - Learning to Learn.

Implements meta-learning algorithms:
- MAML: Model-Agnostic Meta-Learning
- Reptile: First-order meta-learning
- Fast adaptation to new tasks with few samples

Architecture:
    Meta-Learner: Learns good initialization
    Inner Loop: Task-specific adaptation
    Outer Loop: Meta-update across tasks
    Applications: Few-shot learning, rapid adaptation

Based on Finn et al. "Model-Agnostic Meta-Learning" (2017).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
import copy


@dataclass
class MetaOutput:
    """Meta-learning output."""
    adapted_params: Dict[str, torch.Tensor]
    task_loss: float
    adaptation_steps: int


class MetaMLP(nn.Module):
    """Simple MLP for meta-learning."""
    
    def __init__(
        self,
        input_dim: int = 32,
        hidden_dim: int = 64,
        output_dim: int = 1
    ):
        super().__init__()
        
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
    
    def functional_forward(
        self,
        x: torch.Tensor,
        params: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """Forward with explicit parameters (for MAML)."""
        h = x
        h = F.linear(h, params['net.0.weight'], params['net.0.bias'])
        h = F.relu(h)
        h = F.linear(h, params['net.2.weight'], params['net.2.bias'])
        h = F.relu(h)
        h = F.linear(h, params['net.4.weight'], params['net.4.bias'])
        return h


class MAML:
    """Model-Agnostic Meta-Learning algorithm."""
    
    def __init__(
        self,
        model: nn.Module,
        inner_lr: float = 0.01,
        outer_lr: float = 0.001,
        num_adapt_steps: int = 5
    ):
        self.model = model
        self.inner_lr = inner_lr
        self.outer_lr = outer_lr
        self.num_adapt_steps = num_adapt_steps
        
        # Meta-optimizer
        self.meta_optimizer = torch.optim.Adam(model.parameters(), lr=outer_lr)
        
    def adapt(
        self,
        support_x: torch.Tensor,
        support_y: torch.Tensor,
        num_steps: Optional[int] = None
    ) -> MetaOutput:
        """Adapt to new task via gradient descent."""
        if num_steps is None:
            num_steps = self.num_adapt_steps
        
        # Get current parameters
        adapted_params = {
            name: param.clone()
            for name, param in self.model.named_parameters()
        }
        
        # Inner loop: adapt to task
        for _ in range(num_steps):
            # Forward with adapted params
            if hasattr(self.model, 'functional_forward'):
                pred = self.model.functional_forward(support_x, adapted_params)
            else:
                # Temporary parameter update
                pass
            
            # Compute loss
            loss = F.mse_loss(pred, support_y)
            
            # Gradient descent
            grads = torch.autograd.grad(
                loss,
                adapted_params.values(),
                create_graph=True
            )
            
            # Update adapted parameters
            for (name, _), grad in zip(adapted_params.items(), grads):
                adapted_params[name] = adapted_params[name] - self.inner_lr * grad
        
        return MetaOutput(
            adapted_params=adapted_params,
            task_loss=loss.item(),
            adaptation_steps=num_steps
        )
    
    def meta_update(
        self,
        query_x: torch.Tensor,
        query_y: torch.Tensor,
        adapted_params: Dict[str, torch.Tensor]
    ) -> Dict:
        """Meta-update using query set loss."""
        # Forward with adapted params
        if hasattr(self.model, 'functional_forward'):
            pred = self.model.functional_forward(query_x, adapted_params)
        else:
            pred = self.model(query_x)
        
        # Query loss
        query_loss = F.mse_loss(pred, query_y)
        
        # Meta-update
        self.meta_optimizer.zero_grad()
        query_loss.backward()
        self.meta_optimizer.step()
        
        return {
            'query_loss': query_loss.item(),
            'meta_loss': query_loss.item()
        }
    
    def train_step(
        self,
        tasks: List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]]
    ) -> Dict:
        """Meta-training step over batch of tasks.
        
        Each task: (support_x, support_y, query_x, query_y)
        """
        total_loss = 0.0
        
        for support_x, support_y, query_x, query_y in tasks:
            # Adapt to task
            meta_output = self.adapt(support_x, support_y)
            
            # Meta-update
            result = self.meta_update(query_x, query_y, meta_output.adapted_params)
            
            total_loss += result['meta_loss']
        
        return {
            'meta_loss': total_loss / len(tasks),
            'num_tasks': len(tasks)
        }


class Reptile:
    """Reptile: First-order meta-learning."""
    
    def __init__(
        self,
        model: nn.Module,
        inner_lr: float = 0.01,
        meta_lr: float = 0.1,
        num_adapt_steps: int = 5
    ):
        self.model = model
        self.inner_lr = inner_lr
        self.meta_lr = meta_lr
        self.num_adapt_steps = num_adapt_steps
        
        self.optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
    def adapt(
        self,
        support_x: torch.Tensor,
        support_y: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """Adapt to task."""
        # Create temporary model
        adapted = copy.deepcopy(self.model)
        opt = torch.optim.SGD(adapted.parameters(), lr=self.inner_lr)
        
        for _ in range(self.num_adapt_steps):
            opt.zero_grad()
            pred = adapted(support_x)
            loss = F.mse_loss(pred, support_y)
            loss.backward()
            opt.step()
        
        # Return adapted parameters
        return {
            name: param.clone()
            for name, param in adapted.named_parameters()
        }
    
    def meta_update(
        self,
        adapted_params: Dict[str, torch.Tensor]
    ) -> None:
        """Update meta-parameters toward adapted parameters."""
        with torch.no_grad():
            for name, param in self.model.named_parameters():
                adapted = adapted_params[name]
                # Move toward adapted parameters
                param.data = param.data + self.meta_lr * (adapted.data - param.data)
    
    def train_step(
        self,
        tasks: List[Tuple[torch.Tensor, torch.Tensor]]
    ) -> Dict:
        """Meta-training step."""
        total_loss = 0.0
        
        for support_x, support_y in tasks:
            # Adapt
            adapted_params = self.adapt(support_x, support_y)
            
            # Compute loss for logging
            with torch.no_grad():
                pred = self.model(support_x)
                loss = F.mse_loss(pred, support_y)
                total_loss += loss.item()
            
            # Meta-update
            self.meta_update(adapted_params)
        
        self.optimizer.zero_grad()
        
        return {
            'loss': total_loss / len(tasks),
            'num_tasks': len(tasks)
        }


class MetaLearner:
    """Unified meta-learning interface."""
    
    def __init__(
        self,
        input_dim: int = 32,
        hidden_dim: int = 64,
        output_dim: int = 1,
        algorithm: str = 'maml'
    ):
        self.algorithm = algorithm
        
        # Base model
        self.model = MetaMLP(input_dim, hidden_dim, output_dim)
        
        # Initialize algorithm
        if algorithm == 'maml':
            self.algo = MAML(self.model)
        elif algorithm == 'reptile':
            self.algo = Reptile(self.model)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    def train(
        self,
        tasks: List,
        num_iterations: int = 100
    ) -> List[Dict]:
        """Train meta-learner."""
        history = []
        
        for i in range(num_iterations):
            result = self.algo.train_step(tasks)
            result['iteration'] = i
            history.append(result)
        
        return history
    
    def adapt_to_task(
        self,
        support_x: torch.Tensor,
        support_y: torch.Tensor
    ) -> MetaOutput:
        """Adapt to new task."""
        return self.algo.adapt(support_x, support_y)
    
    def evaluate(
        self,
        query_x: torch.Tensor,
        query_y: torch.Tensor,
        adapted_params: Optional[Dict] = None
    ) -> float:
        """Evaluate on query set."""
        self.model.eval()
        with torch.no_grad():
            if adapted_params and hasattr(self.model, 'functional_forward'):
                pred = self.model.functional_forward(query_x, adapted_params)
            else:
                pred = self.model(query_x)
            return F.mse_loss(pred, query_y).item()


def create_meta_learner(
    input_dim: int = 32,
    hidden_dim: int = 64,
    output_dim: int = 1,
    algorithm: str = 'maml'
) -> MetaLearner:
    """Create MetaLearner."""
    return MetaLearner(input_dim, hidden_dim, output_dim, algorithm)
