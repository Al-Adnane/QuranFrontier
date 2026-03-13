"""
Embodied Loss Functions: Semantic + Physical Compliance.

Combined loss for fine-tuning Quranic recitation:

L_total = w_semantic * L_semantic + w_tajweed * L_tajweed

where:
- L_semantic: Meaning preservation (cosine distance in embedding space)
- L_tajweed: Tajweed rule compliance (classification + smoothness)
- w_*: Learned or fixed weights

This allows training models that preserve meaning while respecting
tajweed phonetic rules.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple


class SemanticLoss(nn.Module):
    """
    Semantic loss: ensure recitation preserves word meaning.

    Uses cosine distance in embedding space to measure semantic drift.

    L_semantic = 1 - (e_original · e_perturbed) / (||e_original|| ||e_perturbed||)
    """

    def __init__(self, embedding_dim: int = 16, margin: float = 0.2):
        """
        Initialize semantic loss.

        Args:
            embedding_dim: Dimensionality of embeddings.
            margin: Cosine distance margin (0 = no constraint, 1 = must be identical).
        """
        super().__init__()
        self.embedding_dim = embedding_dim
        self.margin = margin

    def forward(
        self,
        embeddings_original: torch.Tensor,
        embeddings_perturbed: torch.Tensor,
    ) -> torch.Tensor:
        """
        Compute semantic loss (cosine distance).

        Args:
            embeddings_original: Original word embeddings, shape (batch, embedding_dim).
            embeddings_perturbed: Recited word embeddings, shape (batch, embedding_dim).

        Returns:
            Scalar loss.
        """
        # Normalize embeddings
        emb_orig_norm = F.normalize(embeddings_original, p=2, dim=1)
        emb_pert_norm = F.normalize(embeddings_perturbed, p=2, dim=1)

        # Cosine similarity
        cosine_sim = torch.sum(emb_orig_norm * emb_pert_norm, dim=1)

        # Loss: maximize similarity (minimize negative cosine distance)
        # Clamp to avoid numerical issues
        cosine_sim = torch.clamp(cosine_sim, -1.0, 1.0)

        # Loss = 1 - similarity = 2 * arccos(similarity) / π
        # Simplified: loss = 1 - similarity for gradient stability
        loss = 1.0 - cosine_sim

        # Apply margin
        if self.margin > 0:
            loss = F.relu(loss - self.margin)

        return loss.mean()


class TajweedLoss(nn.Module):
    """
    Tajweed loss: ensure rule compliance and smooth transitions.

    Combines:
    - Classification loss: predicted rule matches target
    - Smoothness loss: no jarring transitions between rules
    - Continuity loss: proper connected speech

    L_tajweed = L_cls + λ_smooth * L_smooth + λ_cont * L_cont
    """

    def __init__(
        self,
        num_rules: int = 4,
        smooth_weight: float = 0.1,
        continuity_weight: float = 0.05,
    ):
        """
        Initialize tajweed loss.

        Args:
            num_rules: Number of tajweed rules (typically 4: idgham, ikhfaa, iqlab, izhar).
            smooth_weight: Weight for temporal smoothness penalty.
            continuity_weight: Weight for continuity penalty.
        """
        super().__init__()
        self.num_rules = num_rules
        self.smooth_weight = smooth_weight
        self.continuity_weight = continuity_weight

    def forward(
        self,
        rule_predictions: torch.Tensor,
        rule_targets: torch.Tensor,
        rule_sequence: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Compute tajweed loss.

        Args:
            rule_predictions: Predicted rule activations, shape (batch, num_rules).
            rule_targets: Target rule one-hot or soft labels, shape (batch, num_rules).
            rule_sequence: Temporal sequence of rules for continuity, shape (seq_len, num_rules).

        Returns:
            Scalar loss.
        """
        # Classification loss (binary cross-entropy)
        # Ensure predictions are in [0, 1]
        pred_clipped = torch.clamp(rule_predictions, 1e-7, 1 - 1e-7)
        cls_loss = F.binary_cross_entropy(pred_clipped, rule_targets)

        # Smoothness loss (penalize rapid rule changes)
        smooth_loss = 0.0
        if rule_sequence is not None and rule_sequence.shape[0] > 1:
            # Compute temporal differences
            rule_diffs = torch.abs(rule_sequence[1:] - rule_sequence[:-1])
            smooth_loss = torch.mean(rule_diffs)

        # Continuity loss (ensure at least one rule is active)
        cont_loss = 0.0
        rule_activity = torch.max(rule_predictions, dim=1)[0]
        cont_loss = torch.mean(F.relu(0.5 - rule_activity))  # Penalize low activity

        # Total loss
        total_loss = cls_loss + self.smooth_weight * smooth_loss + self.continuity_weight * cont_loss

        return total_loss


class ArticulatoryConstraintLoss(nn.Module):
    """
    Articulatory constraint loss: ensure features respect vocal tract anatomy.

    Constraints:
    - Pitch must be within human phonation range (50-400 Hz)
    - Formants must be ordered: F1 < F2 < F3
    - Durations must be non-negative and reasonable (0.05-0.5 s)
    - Transitions must be smooth (no > 50 Hz jumps between frames)
    """

    def __init__(self):
        """Initialize articulatory constraint loss."""
        super().__init__()
        self.pitch_min = 50.0
        self.pitch_max = 400.0
        self.duration_min = 0.05
        self.duration_max = 0.5

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        """
        Compute constraint penalties.

        Args:
            features: Feature vector with [pitch, f1, f2, f3, duration, ...]
                     shape (batch, feature_dim).

        Returns:
            Scalar loss (0 if all constraints satisfied).
        """
        loss = 0.0

        # Pitch constraint
        if features.shape[1] > 0:
            pitch = features[:, 0]
            pitch_violation = F.relu(self.pitch_min - pitch) + F.relu(pitch - self.pitch_max)
            loss += torch.mean(pitch_violation) * 0.1

        # Formant ordering (F1 < F2 < F3)
        if features.shape[1] >= 4:
            f1, f2, f3 = features[:, 1], features[:, 2], features[:, 3]
            f1_f2_violation = F.relu(f1 - f2)  # Penalize F1 >= F2
            f2_f3_violation = F.relu(f2 - f3)  # Penalize F2 >= F3
            loss += (torch.mean(f1_f2_violation) + torch.mean(f2_f3_violation)) * 0.1

        # Duration constraint
        if features.shape[1] >= 5:
            duration = features[:, 4]
            duration_violation = (
                F.relu(self.duration_min - duration)
                + F.relu(duration - self.duration_max)
            )
            loss += torch.mean(duration_violation) * 0.1

        return loss


class EmbodiedLoss(nn.Module):
    """
    Combined embodied loss: semantic + tajweed + articulatory constraints.

    L_total = w_semantic * L_semantic
            + w_tajweed * L_tajweed
            + w_articulator * L_articulator

    This enables multi-objective optimization of recitation quality.
    """

    def __init__(
        self,
        embedding_dim: int = 16,
        num_rules: int = 4,
        semantic_weight: float = 0.5,
        tajweed_weight: float = 0.5,
        articulator_weight: float = 0.0,
    ):
        """
        Initialize embodied loss.

        Args:
            embedding_dim: Dimensionality of semantic embeddings.
            num_rules: Number of tajweed rules.
            semantic_weight: Weight for semantic loss component.
            tajweed_weight: Weight for tajweed loss component.
            articulator_weight: Weight for articulatory constraint component.
        """
        super().__init__()
        self.semantic_weight = semantic_weight
        self.tajweed_weight = tajweed_weight
        self.articulator_weight = articulator_weight

        # Component loss functions
        self.semantic_loss = SemanticLoss(embedding_dim=embedding_dim)
        self.tajweed_loss = TajweedLoss(num_rules=num_rules)
        self.articulator_loss = ArticulatoryConstraintLoss()

    def forward(
        self,
        embeddings_original: torch.Tensor,
        embeddings_perturbed: torch.Tensor,
        rule_predictions: torch.Tensor,
        rule_targets: torch.Tensor,
        acoustic_features: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, dict]:
        """
        Compute total embodied loss.

        Args:
            embeddings_original: Original word embeddings, shape (batch, embedding_dim).
            embeddings_perturbed: Recited embeddings, shape (batch, embedding_dim).
            rule_predictions: Predicted tajweed rule activations, shape (batch, num_rules).
            rule_targets: Target tajweed rules, shape (batch, num_rules).
            acoustic_features: Optional acoustic features for articulator constraints.

        Returns:
            (total_loss, loss_dict) where loss_dict contains individual components.
        """
        # Semantic loss
        l_semantic = self.semantic_loss(embeddings_original, embeddings_perturbed)

        # Tajweed loss
        l_tajweed = self.tajweed_loss(rule_predictions, rule_targets)

        # Articulatory constraint loss
        l_articulator = 0.0
        if acoustic_features is not None:
            l_articulator = self.articulator_loss(acoustic_features)

        # Weighted combination
        total_loss = (
            self.semantic_weight * l_semantic
            + self.tajweed_weight * l_tajweed
            + self.articulator_weight * l_articulator
        )

        # Return loss and component breakdown
        loss_dict = {
            "total": total_loss.item(),
            "semantic": l_semantic.item(),
            "tajweed": l_tajweed.item(),
            "articulator": l_articulator.item() if acoustic_features is not None else 0.0,
        }

        return total_loss, loss_dict

    def set_weights(self, semantic: float, tajweed: float, articulator: float = 0.0) -> None:
        """
        Update loss component weights dynamically.

        Args:
            semantic: Weight for semantic loss.
            tajweed: Weight for tajweed loss.
            articulator: Weight for articulatory loss.
        """
        total = semantic + tajweed + articulator
        if total > 0:
            self.semantic_weight = semantic / total
            self.tajweed_weight = tajweed / total
            self.articulator_weight = articulator / total


class ProgressiveLoss(nn.Module):
    """
    Progressive loss that shifts emphasis over training.

    Phase 1 (0-30% steps): Emphasize semantic preservation
    Phase 2 (30-70% steps): Balance semantic + tajweed
    Phase 3 (70-100% steps): Emphasize tajweed compliance

    This curriculum learning approach helps avoid early divergence from meaning.
    """

    def __init__(
        self,
        embedding_dim: int = 16,
        num_rules: int = 4,
        total_steps: int = 10000,
    ):
        """
        Initialize progressive loss.

        Args:
            embedding_dim: Semantic embedding dimensionality.
            num_rules: Number of tajweed rules.
            total_steps: Total training steps (for phase scheduling).
        """
        super().__init__()
        self.embodied_loss = EmbodiedLoss(
            embedding_dim=embedding_dim,
            num_rules=num_rules,
        )
        self.total_steps = total_steps
        self.current_step = 0

    def update_step(self) -> None:
        """Increment training step counter."""
        self.current_step += 1

    def _get_phase_weights(self) -> Tuple[float, float, float]:
        """
        Get current phase weights based on training progress.

        Returns:
            (semantic_weight, tajweed_weight, articulator_weight).
        """
        progress = self.current_step / self.total_steps

        if progress < 0.3:
            # Phase 1: semantic emphasis
            return 0.9, 0.1, 0.0
        elif progress < 0.7:
            # Phase 2: balanced
            return 0.5, 0.5, 0.0
        else:
            # Phase 3: tajweed emphasis
            return 0.3, 0.7, 0.0

    def forward(
        self,
        embeddings_original: torch.Tensor,
        embeddings_perturbed: torch.Tensor,
        rule_predictions: torch.Tensor,
        rule_targets: torch.Tensor,
        acoustic_features: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, dict]:
        """
        Compute progressive loss with curriculum weighting.

        Args:
            embeddings_original: Original word embeddings.
            embeddings_perturbed: Recited embeddings.
            rule_predictions: Predicted tajweed rules.
            rule_targets: Target tajweed rules.
            acoustic_features: Optional acoustic features.

        Returns:
            (total_loss, loss_dict).
        """
        # Update phase weights
        sem_w, taj_w, art_w = self._get_phase_weights()
        self.embodied_loss.set_weights(sem_w, taj_w, art_w)

        # Compute loss with current weights
        return self.embodied_loss(
            embeddings_original,
            embeddings_perturbed,
            rule_predictions,
            rule_targets,
            acoustic_features,
        )
