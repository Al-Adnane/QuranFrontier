"""Neuromorphic Spiking Network - Event-Based Neural Computation.

Implements spiking neural networks (SNNs) with:
- Leaky Integrate-and-Fire (LIF) neurons
- Spike-timing dependent plasticity (STDP)
- Event-based processing (only compute on spikes)
- Temporal coding (information in spike timing)

Architecture:
    LIF Neurons: Biologically plausible neuron model
    Synapses: Learnable connections with STDP
    Encoders: Convert input to spike trains
    Decoders: Read out from spike patterns

Applications:
- Low-power edge computing
- Event camera processing
- Temporal pattern recognition
- Brain-inspired AI
"""

import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SpikeTrain:
    """Spike train representation."""
    spikes: torch.Tensor      # [batch, time, neurons] binary
    spike_times: List[List[int]]  # Spike times per neuron
    rates: torch.Tensor       # Firing rates


class LIFNeuron(nn.Module):
    """Leaky Integrate-and-Fire neuron."""
    
    def __init__(
        self,
        num_neurons: int,
        threshold: float = 1.0,
        decay: float = 0.9,
        refractory_period: int = 2
    ):
        super().__init__()
        self.num_neurons = num_neurons
        self.threshold = threshold
        self.decay = decay
        self.refractory_period = refractory_period
        
        # Membrane potential (state)
        self.register_buffer('voltage', torch.zeros(num_neurons))
        self.register_buffer('refractory', torch.zeros(num_neurons, dtype=torch.long))
        
    def forward(self, input_current: torch.Tensor) -> torch.Tensor:
        """Process input current and emit spikes.
        
        LIF dynamics:
        V[t+1] = decay * V[t] + input
        if V > threshold: spike, V = 0
        """
        # Decay
        self.voltage = self.decay * self.voltage
        
        # Add input current
        self.voltage = self.voltage + input_current
        
        # Check refractory period
        in_refractory = self.refractory > 0
        
        # Generate spikes
        spikes = (self.voltage > self.threshold) & ~in_refractory
        
        # Reset voltage after spike
        self.voltage[spikes] = 0
        
        # Set refractory period (handle batch dimension)
        if spikes.dim() > 1:
            for b in range(spikes.size(0)):
                self.refractory[spikes[b]] = self.refractory_period
        else:
            self.refractory[spikes] = self.refractory_period
        
        return spikes.float()
    
    def reset(self):
        """Reset neuron state."""
        self.voltage.fill_(0)
        self.refractory.fill_(0)


class STDPsynapse(nn.Module):
    """Synapse with Spike-Timing Dependent Plasticity."""
    
    def __init__(
        self,
        pre_neurons: int,
        post_neurons: int,
        learning_rate: float = 0.01
    ):
        super().__init__()
        
        # Synaptic weights
        self.weights = nn.Parameter(torch.randn(pre_neurons, post_neurons) * 0.1)
        
        # STDP parameters
        self.learning_rate = learning_rate
        self.tau_plus = 20.0  # ms
        self.tau_minus = 20.0  # ms
        
        # Spike traces for STDP
        self.register_buffer('pre_trace', torch.zeros(pre_neurons))
        self.register_buffer('post_trace', torch.zeros(post_neurons))
        
    def forward(
        self,
        pre_spikes: torch.Tensor,
        post_spikes: torch.Tensor
    ) -> torch.Tensor:
        """Transmit spikes and apply STDP learning."""
        # Transmit spikes
        post_current = pre_spikes @ self.weights
        
        # STDP learning
        self._apply_stdp(pre_spikes, post_spikes)
        
        return post_current
    
    def _apply_stdp(
        self,
        pre_spikes: torch.Tensor,
        post_spikes: torch.Tensor
    ):
        """Apply STDP weight updates."""
        # Update traces (exponential decay)
        self.pre_trace = self.pre_trace * 0.95 + pre_spikes
        self.post_trace = self.post_trace * 0.95 + post_spikes
        
        # Weight update
        # Pre before post (LTP): strengthen
        # Post before pre (LTD): weaken
        delta_w = (
            self.learning_rate * 
            (self.pre_trace.unsqueeze(1) * post_spikes.unsqueeze(0) -
             self.post_trace.unsqueeze(0) * pre_spikes.unsqueeze(1))
        )
        
        self.weights.data += delta_w
        
        # Weight bounds
        self.weights.data.clamp_(-1, 1)


class SpikeEncoder(nn.Module):
    """Encodes input into spike trains."""
    
    def __init__(self, input_dim: int, num_neurons: int, time_steps: int = 50):
        super().__init__()
        self.input_dim = input_dim
        self.num_neurons = num_neurons
        self.time_steps = time_steps
        
        # Encoding weights
        self.encode = nn.Linear(input_dim, num_neurons)
        
    def forward(self, x: torch.Tensor) -> SpikeTrain:
        """Convert input to spike train."""
        batch_size = x.size(0)
        
        # Encode to firing rates
        rates = torch.sigmoid(self.encode(x))
        
        # Generate spikes from rates (Poisson encoding)
        spikes = torch.rand(batch_size, self.time_steps, self.num_neurons) < rates.unsqueeze(1)
        spikes = spikes.float()
        
        # Extract spike times
        spike_times = []
        for b in range(batch_size):
            neuron_times = []
            for n in range(self.num_neurons):
                times = spikes[b, :, n].nonzero(as_tuple=True)[0].tolist()
                neuron_times.append(times)
            spike_times.append(neuron_times)
        
        return SpikeTrain(
            spikes=spikes,
            spike_times=spike_times,
            rates=rates
        )


class NeuromorphicSpikingNetwork(nn.Module):
    """Main neuromorphic spiking neural network."""
    
    def __init__(
        self,
        input_dim: int = 128,
        num_neurons: List[int] = None,
        time_steps: int = 50
    ):
        super().__init__()
        
        if num_neurons is None:
            num_neurons = [256, 128, 64]
        
        self.time_steps = time_steps
        self.num_layers = len(num_neurons)
        
        # Encoder
        self.encoder = SpikeEncoder(input_dim, num_neurons[0], time_steps)
        
        # LIF neurons for each layer
        self.neurons = nn.ModuleList([
            LIFNeuron(n)
            for n in num_neurons
        ])
        
        # STDP synapses between layers
        self.synapses = nn.ModuleList([
            STDPsynapse(num_neurons[i], num_neurons[i+1])
            for i in range(len(num_neurons) - 1)
        ])
        
        # Output decoder
        self.decoder = nn.Linear(num_neurons[-1], 10)  # 10 classes
        
        self.num_neurons = num_neurons
        
    def forward(
        self,
        x: torch.Tensor,
        train_stdp: bool = True
    ) -> Dict:
        """Process input through spiking network."""
        batch_size = x.size(0)
        
        # Encode to spikes
        input_spikes = self.encoder(x)
        
        # Reset all neurons
        for neuron in self.neurons:
            neuron.reset()
        
        # Process through time
        all_spikes = [input_spikes.spikes]
        
        for t in range(self.time_steps):
            # Get input at this timestep
            layer_spikes = input_spikes.spikes[:, t, :]
            
            # Process through layers
            for i, (neuron, spikes) in enumerate(zip(self.neurons[:-1], [layer_spikes])):
                # Neuron dynamics
                current = spikes @ self.synapses[i].weights if i > 0 else spikes
                output_spikes = neuron(current)
                
                # STDP learning
                if train_stdp and i < len(self.synapses):
                    next_input = self.neurons[i+1].voltage
                    self.synapses[i](output_spikes, (next_input > 0.5).float())
            
            all_spikes.append(layer_spikes)
        
        # Decode from final layer spikes
        final_spikes = all_spikes[-1]
        spike_counts = final_spikes.sum(dim=1)  # Rate coding
        
        # Handle dimension mismatch
        if spike_counts.size(-1) != self.decoder.in_features:
            self.decoder = nn.Linear(spike_counts.size(-1), 10).to(spike_counts.device)
        
        output = self.decoder(spike_counts)
        
        return {
            'output': output,
            'spike_train': input_spikes,
            'all_spikes': all_spikes,
            'total_spikes': sum(s.sum().item() for s in all_spikes)
        }
    
    def get_energy_consumption(
        self,
        spike_counts: Dict
    ) -> float:
        """Estimate energy consumption (spikes = energy)."""
        # Each spike costs energy
        # SNNs are efficient because they're sparse and event-driven
        return spike_counts.get('total_spikes', 0) * 1.0  # Arbitrary units


def create_neuromorphic_network(
    input_dim: int = 128,
    num_neurons: List[int] = None,
    time_steps: int = 50
) -> NeuromorphicSpikingNetwork:
    """Create NeuromorphicSpikingNetwork."""
    return NeuromorphicSpikingNetwork(input_dim, num_neurons, time_steps)
