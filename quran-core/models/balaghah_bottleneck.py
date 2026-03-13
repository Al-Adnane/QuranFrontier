"""Balaghah Information Bottleneck - Rhetorical Preservation Compression.

This model compresses text while preserving rhetorical devices (jinas, tibaq, 
istiarah, etc.) using information bottleneck principles.

Architecture:
    Encoder: Text → Latent representation (compressed)
    Decoder: Latent → Reconstructed text
    Rhetorical Head: Latent → Rhetorical device predictions
    Loss: Reconstruction + Rhetorical preservation + KL divergence

Based on frontierqu.linguistic.balaghah for rhetorical device detection.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal, kl_divergence
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import math


@dataclass
class RhetoricalDevice:
    """Rhetorical device metadata."""
    device_type: str      # jinas, tibaq, istiarah, tashbih, etc.
    category: str         # maani, bayan, badi
    score: float          # 0-1 strength
    positions: List[int]  # Character/token positions


@dataclass
class BalaghahOutput:
    """Output from BalaghahIB model."""
    compressed: torch.Tensor
    reconstructed: str
    rhetorical_devices: List[RhetoricalDevice]
    compression_ratio: float
    rhetorical_preservation: float
    kl_divergence: float


class RhetoricalEncoder(nn.Module):
    """Encodes text into compressed latent representation."""
    
    def __init__(self, vocab_size: int, embed_dim: int, hidden_dim: int, 
                 latent_dim: int, max_length: int = 512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.positional = nn.Parameter(torch.randn(1, max_length, embed_dim) * 0.1)
        
        self.encoder_layers = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=embed_dim,
                nhead=8,
                dim_feedforward=hidden_dim,
                dropout=0.1,
                batch_first=True
            ) for _ in range(6)
        ])
        
        # Compression: map to latent distribution parameters
        self.mu_head = nn.Linear(embed_dim, latent_dim)
        self.logvar_head = nn.Linear(embed_dim, latent_dim)
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode text to latent distribution parameters.
        
        Args:
            x: Token ids [batch, seq_len]
        Returns:
            mu: Mean [batch, latent_dim]
            logvar: Log variance [batch, latent_dim]
        """
        # Embed + positional
        h = self.embedding(x) + self.positional[:, :x.size(1), :]
        
        # Transformer encoding
        for layer in self.encoder_layers:
            h = layer(h)
        
        # Global pooling (mean over sequence)
        mask = (x != 0).unsqueeze(-1).float()
        h_pooled = (h * mask).sum(dim=1) / (mask.sum(dim=1) + 1e-9)
        
        # Distribution parameters
        mu = self.mu_head(h_pooled)
        logvar = self.logvar_head(h_pooled)
        
        return mu, logvar


class RhetoricalDecoder(nn.Module):
    """Decodes latent representation back to text."""
    
    def __init__(self, vocab_size: int, embed_dim: int, hidden_dim: int,
                 latent_dim: int, max_length: int = 512):
        super().__init__()
        self.latent_proj = nn.Linear(latent_dim, embed_dim)
        self.positional = nn.Parameter(torch.randn(1, max_length, embed_dim) * 0.1)
        
        self.decoder_layers = nn.ModuleList([
            nn.TransformerDecoderLayer(
                d_model=embed_dim,
                nhead=8,
                dim_feedforward=hidden_dim,
                dropout=0.1,
                batch_first=True
            ) for _ in range(6)
        ])
        
        self.output_head = nn.Linear(embed_dim, vocab_size)
        self.max_length = max_length
        
    def forward(self, z: torch.Tensor, memory: torch.Tensor) -> torch.Tensor:
        """Decode latent to token probabilities.
        
        Args:
            z: Latent vector [batch, latent_dim]
            memory: Encoder memory [batch, seq_len, embed_dim]
        Returns:
            logits: Token logits [batch, seq_len, vocab_size]
        """
        # Project latent
        h = self.latent_proj(z).unsqueeze(1)  # [batch, 1, embed_dim]
        
        # Expand to sequence
        seq_len = memory.size(1)
        h = h.expand(-1, seq_len, -1) + self.positional[:, :seq_len, :]
        
        # Transformer decoding
        for layer in self.decoder_layers:
            h = layer(h, memory)
        
        # Output logits
        logits = self.output_head(h)
        return logits


class RhetoricalHead(nn.Module):
    """Predicts rhetorical devices from latent representation."""
    
    def __init__(self, latent_dim: int, num_devices: int = 15):
        super().__init__()
        self.num_devices = num_devices
        
        self.network = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, num_devices * 2)  # score + position for each
        )
        
        # Device types
        self.device_types = [
            'jinas', 'tibaq', 'istiarah', 'tashbih', 'kinayah',
            'tajnid', 'saj', 'tawriyah', 'husn_al-bayan', 'takhyil',
            'mubalaghah', 'tawkid', 'taqdim', 'tikrar', 'tibaq_jinsi'
        ]
        
    def forward(self, z: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Predict rhetorical devices.
        
        Args:
            z: Latent vector [batch, latent_dim]
        Returns:
            Dict with scores and positions for each device type
        """
        output = self.network(z)  # [batch, num_devices * 2]
        output = output.view(-1, self.num_devices, 2)
        
        scores = torch.sigmoid(output[:, :, 0])  # [batch, num_devices]
        positions = torch.sigmoid(output[:, :, 1])  # [batch, num_devices]
        
        return {
            'scores': scores,
            'positions': positions,
            'device_types': self.device_types
        }


class BalaghahInformationBottleneck(nn.Module):
    """Main Balaghah Information Bottleneck model.
    
    Compresses text while preserving rhetorical beauty.
    
    Loss = Reconstruction Loss 
         + λ₁ * Rhetorical Preservation Loss
         + λ₂ * KL Divergence (information bottleneck)
    """
    
    def __init__(
        self,
        vocab_size: int = 30000,
        embed_dim: int = 512,
        hidden_dim: int = 2048,
        latent_dim: int = 128,
        max_length: int = 512,
        rhetorical_weight: float = 1.0,
        kl_weight: float = 0.1,
    ):
        super().__init__()
        
        self.encoder = RhetoricalEncoder(
            vocab_size, embed_dim, hidden_dim, latent_dim, max_length
        )
        self.decoder = RhetoricalDecoder(
            vocab_size, embed_dim, hidden_dim, latent_dim, max_length
        )
        self.rhetorical_head = RhetoricalHead(latent_dim)
        
        self.rhetorical_weight = rhetorical_weight
        self.kl_weight = kl_weight
        self.latent_dim = latent_dim
        
        # Tokenizer placeholder (would be loaded from file)
        self.vocab_size = vocab_size
        
    def encode(self, input_ids: torch.Tensor) -> Tuple[torch.Tensor, Dict]:
        """Encode text to latent representation.
        
        Args:
            input_ids: Token ids [batch, seq_len]
        Returns:
            z: Sampled latent vector [batch, latent_dim]
            encoding: Dict with mu, logvar, rhetorical devices
        """
        mu, logvar = self.encoder(input_ids)
        
        # Reparameterization trick
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        z = mu + eps * std
        
        # Predict rhetorical devices
        rhetorical = self.rhetorical_head(z)
        
        return z, {
            'mu': mu,
            'logvar': logvar,
            'rhetorical': rhetorical
        }
    
    def decode(self, z: torch.Tensor, memory: torch.Tensor) -> torch.Tensor:
        """Decode latent to token logits.
        
        Args:
            z: Latent vector [batch, latent_dim]
            memory: Encoder memory
        Returns:
            logits: Token logits [batch, seq_len, vocab_size]
        """
        return self.decoder(z, memory)
    
    def forward(
        self,
        input_ids: torch.Tensor,
        target_ids: torch.Tensor,
        rhetorical_targets: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """Full forward pass with loss computation.
        
        Args:
            input_ids: Input token ids [batch, seq_len]
            target_ids: Target token ids [batch, seq_len]
            rhetorical_targets: Optional rhetorical device labels [batch, num_devices]
        Returns:
            Dict with losses and outputs
        """
        # Encode
        mu, logvar = self.encoder(input_ids)
        
        # Reparameterization
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        z = mu + eps * std
        
        # Get encoder memory for decoder
        with torch.no_grad():
            memory = self.encoder.embedding(input_ids)
        
        # Decode
        logits = self.decode(z, memory)
        
        # Rhetorical prediction
        rhetorical_pred = self.rhetorical_head(z)
        
        # Compute losses
        recon_loss = F.cross_entropy(
            logits.view(-1, self.vocab_size),
            target_ids.view(-1),
            ignore_index=0,
            reduction='mean'
        )
        
        # KL divergence (information bottleneck)
        kl_loss = kl_divergence(
            Normal(mu, std),
            Normal(torch.zeros_like(mu), torch.ones_like(std))
        ).mean()
        
        # Rhetorical preservation loss
        if rhetorical_targets is not None:
            rhet_loss = F.binary_cross_entropy(
                rhetorical_pred['scores'],
                rhetorical_targets.float()
            )
        else:
            rhet_loss = torch.tensor(0.0, device=z.device)
        
        # Total loss
        total_loss = (
            recon_loss 
            + self.rhetorical_weight * rhet_loss 
            + self.kl_weight * kl_loss
        )
        
        return {
            'loss': total_loss,
            'reconstruction_loss': recon_loss,
            'rhetorical_loss': rhet_loss,
            'kl_loss': kl_loss,
            'logits': logits,
            'rhetorical_scores': rhetorical_pred['scores'],
            'mu': mu,
            'logvar': logvar
        }
    
    def compress(
        self,
        text: str,
        tokenizer: Any,
        compression_ratio: float = 0.1
    ) -> BalaghahOutput:
        """Compress text while preserving rhetorical devices.
        
        Args:
            text: Input text
            tokenizer: Tokenizer with encode/decode methods
            compression_ratio: Target compression (0-1)
        Returns:
            BalaghahOutput with compressed representation
        """
        self.eval()
        
        # Tokenize
        tokens = tokenizer.encode(text)
        input_ids = torch.tensor([tokens], dtype=torch.long)
        
        # Encode
        with torch.no_grad():
            z, encoding = self.encode(input_ids)
        
        # Compute rhetorical preservation
        rhet_scores = encoding['rhetorical']['scores'][0]
        num_devices = (rhet_scores > 0.5).sum().item()
        
        # Simple reconstruction (in practice would use sampling)
        with torch.no_grad():
            memory = self.encoder.embedding(input_ids)
            logits = self.decode(z, memory)
            recon_tokens = logits.argmax(dim=-1)[0].tolist()
        
        reconstructed = tokenizer.decode(recon_tokens)
        
        # Build rhetorical device list
        devices = []
        device_types = encoding['rhetorical']['device_types']
        for i, (score, dtype) in enumerate(zip(rhet_scores, device_types)):
            if score > 0.5:
                devices.append(RhetoricalDevice(
                    device_type=dtype,
                    category='badi',
                    score=score.item(),
                    positions=[int(encoding['rhetorical']['positions'][0, i].item() * len(text))]
                ))
        
        # Compression ratio
        original_size = len(text.encode('utf-8'))
        compressed_size = z.numel() * 4  # float32
        actual_ratio = compressed_size / original_size
        
        # Rhetorical preservation score
        rhet_preservation = rhet_scores.mean().item()
        
        return BalaghahOutput(
            compressed=z,
            reconstructed=reconstructed,
            rhetorical_devices=devices,
            compression_ratio=actual_ratio,
            rhetorical_preservation=rhet_preservation,
            kl_divergence=encoding['kl_loss'].mean().item() if 'kl_loss' in encoding else 0.0
        )
    
    def summarize(
        self,
        text: str,
        tokenizer: Any,
        max_summary_length: int = 50
    ) -> str:
        """Generate rhetorical-preserving summary.
        
        Args:
            text: Input text
            tokenizer: Tokenizer
            max_summary_length: Maximum summary tokens
        Returns:
            Summary text preserving rhetorical devices
        """
        self.eval()
        
        tokens = tokenizer.encode(text)
        input_ids = torch.tensor([tokens], dtype=torch.long)
        
        with torch.no_grad():
            z, _ = self.encode(input_ids)
            memory = self.encoder.embedding(input_ids)
            logits = self.decode(z, memory)
            
            # Greedy decoding with length constraint
            summary_tokens = []
            for i in range(min(max_summary_length, logits.size(1))):
                token = logits[0, i].argmax().item()
                if token == tokenizer.eos_token_id:
                    break
                summary_tokens.append(token)
        
        return tokenizer.decode(summary_tokens)


# Convenience function for quick testing
def create_balaghah_model(
    vocab_size: int = 30000,
    pretrained: bool = False
) -> BalaghahInformationBottleneck:
    """Create BalaghahIB model with optional pretrained weights.
    
    Args:
        vocab_size: Vocabulary size
        pretrained: Whether to load pretrained weights
    Returns:
        Model instance
    """
    model = BalaghahInformationBottleneck(vocab_size=vocab_size)
    
    if pretrained:
        # Would load from checkpoint
        pass
    
    return model
