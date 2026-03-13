"""Training loop for sheaf neural networks on Quranic complex.

Implements supervised and unsupervised loss functions, including:
- Supervised loss (classification/regression)
- Sheaf consistency loss (gluing axiom violations)
- Morphological equivariance loss
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple, Optional
from frontier_neuro_symbolic.sheaf_nn.sheaf_layer import SheafConvLayer, MultiSheafConvLayer
from frontier_neuro_symbolic.sheaf_nn.message_passing import (
    SheafMessagePassing,
    SheafGluingConstraint,
)


class SheafNNTrainer:
    """Training pipeline for sheaf neural networks.

    Combines supervised and unsupervised losses to train sheaf networks
    that respect both task objectives and geometric constraints.
    """

    def __init__(
        self,
        model_in_channels: int,
        model_hidden_channels: List[int],
        model_out_channels: int,
        num_nodes: int,
        num_edges: int,
        lr: float = 0.001,
        weight_decay: float = 1e-5,
        supervised_weight: float = 1.0,
        consistency_weight: float = 0.5,
        device: Optional[str] = None,
    ):
        """Initialize trainer with model and hyperparameters.

        Args:
            model_in_channels: Input feature dimension.
            model_hidden_channels: List of hidden layer dimensions.
            model_out_channels: Output feature dimension.
            num_nodes: Number of nodes.
            num_edges: Number of edges.
            lr: Learning rate for Adam optimizer.
            weight_decay: L2 regularization strength.
            supervised_weight: Weight for supervised loss.
            consistency_weight: Weight for sheaf consistency loss.
            device: Device to use ('cuda' or 'cpu').
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.lr = lr
        self.weight_decay = weight_decay
        self.supervised_weight = supervised_weight
        self.consistency_weight = consistency_weight

        # Build model
        self.model = SheafMessagePassing(
            in_channels=model_in_channels,
            hidden_channels=model_hidden_channels,
            out_channels=model_out_channels,
            num_nodes=num_nodes,
            num_edges=num_edges,
        ).to(self.device)

        # Gluing constraint
        self.gluing_constraint = SheafGluingConstraint(
            num_nodes=num_nodes,
            num_edges=num_edges,
            constraint_strength=consistency_weight,
        ).to(self.device)

        # Optimizer
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=lr,
            weight_decay=weight_decay,
        )

        # Loss functions
        self.ce_loss = nn.CrossEntropyLoss()
        self.mse_loss = nn.MSELoss()

        self.num_nodes = num_nodes
        self.num_edges = num_edges

    def compute_supervised_loss(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        edge_index: torch.Tensor,
        task: str = "classification",
    ) -> torch.Tensor:
        """Compute supervised loss (classification or regression).

        Args:
            x: Node features of shape (num_nodes, in_channels).
            y: Node labels of shape (num_nodes,) for classification
               or (num_nodes, out_channels) for regression.
            edge_index: Edge indices of shape (2, num_edges).
            task: Type of task ('classification' or 'regression').

        Returns:
            Scalar supervised loss.
        """
        # Forward pass
        output = self.model(x, edge_index)

        # Compute loss based on task type
        if task == "classification":
            loss = self.ce_loss(output, y)
        elif task == "regression":
            loss = self.mse_loss(output, y)
        else:
            raise ValueError(f"Unknown task type: {task}")

        return loss

    def compute_sheaf_consistency_loss(
        self,
        output: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        """Compute sheaf consistency loss (gluing axiom violations).

        The gluing axiom states that if a sheaf section agrees on
        the intersection of two open sets, the global section is well-defined.
        We measure this by penalizing inconsistencies along edges.

        Args:
            output: Node features of shape (num_nodes, out_channels).
            edge_index: Edge indices of shape (2, num_edges).

        Returns:
            Scalar consistency loss.
        """
        if edge_index.size(1) == 0:
            return torch.tensor(0.0, device=output.device, dtype=output.dtype)

        # Get source and destination features
        src, dst = edge_index[0], edge_index[1]
        x_src = output[src]  # (num_edges, out_channels)
        x_dst = output[dst]  # (num_edges, out_channels)

        # Consistency loss: minimize difference along edges
        # This encourages the sheaf to be "smooth" and gluing axioms to be satisfied
        edge_differences = torch.norm(x_src - x_dst, p=2, dim=1)
        consistency_loss = edge_differences.mean()

        return consistency_loss

    def compute_loss(
        self,
        output: torch.Tensor,
        y: torch.Tensor,
        edge_index: torch.Tensor,
        task: str = "classification",
    ) -> torch.Tensor:
        """Compute combined supervised + consistency loss.

        Args:
            output: Model output (or use model(x, edge_index)).
            y: Node labels.
            edge_index: Edge indices.
            task: Task type ('classification' or 'regression').

        Returns:
            Weighted sum of losses.
        """
        # Supervised loss
        if task == "classification":
            sup_loss = self.ce_loss(output, y)
        elif task == "regression":
            sup_loss = self.mse_loss(output, y)
        else:
            raise ValueError(f"Unknown task type: {task}")

        # Sheaf consistency loss
        consistency_loss = self.compute_sheaf_consistency_loss(output, edge_index)

        # Combined loss
        total_loss = (
            self.supervised_weight * sup_loss
            + self.consistency_weight * consistency_loss
        )

        return total_loss

    def training_step(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        edge_index: torch.Tensor,
        task: str = "classification",
    ) -> torch.Tensor:
        """Execute a single training step.

        Args:
            x: Node features.
            y: Node labels.
            edge_index: Edge indices.
            task: Task type.

        Returns:
            Loss value.
        """
        # Move to device
        x = x.to(self.device)
        y = y.to(self.device)
        edge_index = edge_index.to(self.device)

        # Zero gradients
        self.optimizer.zero_grad()

        # Forward pass
        output = self.model(x, edge_index)

        # Compute loss
        loss = self.compute_loss(output, y, edge_index, task=task)

        # Backward pass
        loss.backward()

        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

        # Optimizer step
        self.optimizer.step()

        return loss.detach()

    def train(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        edge_index: torch.Tensor,
        num_epochs: int = 100,
        task: str = "classification",
        verbose: bool = False,
    ) -> List[torch.Tensor]:
        """Train the sheaf neural network.

        Args:
            x: Node features of shape (num_nodes, in_channels).
            y: Node labels.
            edge_index: Edge indices of shape (2, num_edges).
            num_epochs: Number of training epochs.
            task: Task type ('classification' or 'regression').
            verbose: Whether to print loss values.

        Returns:
            List of loss values per epoch.
        """
        # Ensure model is in training mode
        self.model.train()

        losses = []

        for epoch in range(num_epochs):
            loss = self.training_step(x, y, edge_index, task=task)
            losses.append(loss)

            if verbose and (epoch + 1) % max(1, num_epochs // 10) == 0:
                print(f"Epoch {epoch+1}/{num_epochs}, Loss: {loss:.6f}")

        return losses

    def evaluate(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        edge_index: torch.Tensor,
        task: str = "classification",
    ) -> dict:
        """Evaluate the model on given data.

        Args:
            x: Node features.
            y: Node labels.
            edge_index: Edge indices.
            task: Task type.

        Returns:
            Dictionary with evaluation metrics.
        """
        self.model.eval()

        with torch.no_grad():
            x = x.to(self.device)
            y = y.to(self.device)
            edge_index = edge_index.to(self.device)

            output = self.model(x, edge_index)
            loss = self.compute_loss(output, y, edge_index, task=task)

            metrics = {"loss": loss.item()}

            if task == "classification":
                predictions = torch.argmax(output, dim=1)
                accuracy = (predictions == y).float().mean()
                metrics["accuracy"] = accuracy.item()

            elif task == "regression":
                mse = ((output - y) ** 2).mean()
                metrics["mse"] = mse.item()

        return metrics

    def inference(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        """Run inference (forward pass without gradients).

        Args:
            x: Node features.
            edge_index: Edge indices.

        Returns:
            Model output.
        """
        self.model.eval()

        with torch.no_grad():
            x = x.to(self.device)
            edge_index = edge_index.to(self.device)
            output = self.model(x, edge_index)

        return output

    def get_model(self) -> nn.Module:
        """Get the underlying sheaf neural network model."""
        return self.model

    def save_checkpoint(self, path: str) -> None:
        """Save model checkpoint.

        Args:
            path: Path to save checkpoint.
        """
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
            },
            path,
        )

    def load_checkpoint(self, path: str) -> None:
        """Load model checkpoint.

        Args:
            path: Path to load checkpoint.
        """
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])


class SheafNNEnsembleTrainer:
    """Trainer for ensemble of sheaf neural networks.

    Trains multiple independent sheaf networks and combines predictions.
    Useful for uncertainty estimation and robustness.
    """

    def __init__(
        self,
        num_models: int,
        model_in_channels: int,
        model_hidden_channels: List[int],
        model_out_channels: int,
        num_nodes: int,
        num_edges: int,
        lr: float = 0.001,
    ):
        """Initialize ensemble trainer.

        Args:
            num_models: Number of models in the ensemble.
            model_in_channels: Input feature dimension.
            model_hidden_channels: Hidden layer dimensions.
            model_out_channels: Output feature dimension.
            num_nodes: Number of nodes.
            num_edges: Number of edges.
            lr: Learning rate.
        """
        self.num_models = num_models
        self.trainers = [
            SheafNNTrainer(
                model_in_channels=model_in_channels,
                model_hidden_channels=model_hidden_channels,
                model_out_channels=model_out_channels,
                num_nodes=num_nodes,
                num_edges=num_edges,
                lr=lr,
            )
            for _ in range(num_models)
        ]

    def train(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        edge_index: torch.Tensor,
        num_epochs: int = 100,
        task: str = "classification",
    ) -> List[List[torch.Tensor]]:
        """Train all models in the ensemble.

        Args:
            x: Node features.
            y: Node labels.
            edge_index: Edge indices.
            num_epochs: Number of epochs.
            task: Task type.

        Returns:
            List of loss histories per model.
        """
        loss_histories = []

        for i, trainer in enumerate(self.trainers):
            print(f"Training model {i+1}/{self.num_models}...")
            losses = trainer.train(x, y, edge_index, num_epochs=num_epochs, task=task)
            loss_histories.append(losses)

        return loss_histories

    def ensemble_inference(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Run inference on all models and combine predictions.

        Args:
            x: Node features.
            edge_index: Edge indices.

        Returns:
            Tuple of (mean predictions, std of predictions).
        """
        predictions = []

        for trainer in self.trainers:
            output = trainer.inference(x, edge_index)
            predictions.append(output)

        predictions = torch.stack(predictions)  # (num_models, num_nodes, out_channels)

        # Compute mean and std
        mean_pred = predictions.mean(dim=0)
        std_pred = predictions.std(dim=0)

        return mean_pred, std_pred
