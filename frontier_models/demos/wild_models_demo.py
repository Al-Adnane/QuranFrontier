#!/usr/bin/env python3
"""FrontierQu Wild Models Demo - Experimental Architectures."""

import torch
import sys
sys.path.insert(0, '/Users/mac/Desktop/FrontierQu')

from frontier_models.wild import (
    create_memetic_network,
    create_holographic_network,
    create_consciousness_network,
    create_causal_network,
    create_temporal_prediction_network,
    create_fractal_network,
    create_neuromorphic_network,
    create_synesthesia_network,
)


def demo_memetic():
    """Demo: Memetic Evolution Network."""
    print("\n" + "="*60)
    print("WILD MODEL 1: Memetic Evolution Network")
    print("="*60)
    print("Concept: Ideas as replicators that evolve and compete")
    
    model = create_memetic_network(input_dim=128, meme_dim=64, population_size=50)
    
    # Simulate ideas
    ideas = torch.randn(20, 128)
    
    # Initialize and evolve
    memes = model.initialize_population(ideas)
    print(f"  ✓ Initialized {len(memes)} memes")
    
    # Evolve
    result = model.evolve(memes, num_generations=5)
    print(f"  ✓ Evolved {result.generation} generations")
    print(f"  ✓ Population diversity: {result.diversity:.4f}")
    print(f"  ✓ Dominant memes: {result.dominant_memes[:3]}")
    
    # Predict virality
    test_idea = torch.randn(128)
    virality = model.predict_virality(test_idea)
    print(f"  ✓ Virality prediction: {virality['expected_spread']:.2f}")


def demo_holographic():
    """Demo: Holographic Memory Network."""
    print("\n" + "="*60)
    print("WILD MODEL 2: Holographic Memory Network")
    print("="*60)
    print("Concept: Distributed memory with content-addressable retrieval")
    
    model = create_holographic_network(item_dim=128, holographic_dim=256, capacity=100)
    
    # Store memories
    memories = torch.randn(10, 128)
    num_stored = model.store_memories(memories)
    print(f"  ✓ Stored {num_stored} memories in superposition")
    
    # Recall with partial cue
    cue = memories[0] + torch.randn(128) * 0.1
    result = model.recall(cue)
    print(f"  ✓ Recall similarity: {result.similarity:.4f}")
    print(f"  ✓ Recall confidence: {result.confidence:.4f}")
    
    # Create association
    assoc = model.associate(memories[0], memories[1])
    print(f"  ✓ Created association between items 0 and 1")


def demo_consciousness():
    """Demo: Consciousness Integration Network."""
    print("\n" + "="*60)
    print("WILD MODEL 3: Consciousness Integration Network")
    print("="*60)
    print("Concept: Global Workspace Theory implementation")
    
    model = create_consciousness_network(
        input_dims={'vision': 256, 'language': 512, 'memory': 128},
        workspace_dim=256
    )
    
    # Simulate multi-modal input
    inputs = {
        'vision': torch.randn(1, 256),
        'language': torch.randn(1, 512),
        'memory': torch.randn(1, 128)
    }
    
    # Process through consciousness architecture
    result = model.process(inputs)
    print(f"  ✓ Active modules: {result.active_modules}")
    print(f"  ✓ Integration level: {result.integration_level:.2%}")
    print(f"  ✓ Phi (integrated information): {result.phi:.4f}")
    print(f"  ✓ Report: {result.report}")


def demo_causal():
    """Demo: Causal Intervention Network."""
    print("\n" + "="*60)
    print("WILD MODEL 4: Causal Intervention Network")
    print("="*60)
    print("Concept: Do-calculus and counterfactual reasoning")
    
    model = create_causal_network(num_variables=5, hidden_dim=64)
    
    # Simulate observational data
    data = torch.randn(100, 5)
    
    # Intervene
    intervention_var = 0
    intervention_value = torch.ones(100) * 2.0
    result = model.intervene(data, intervention_var, intervention_value, outcome=4)
    print(f"  ✓ Intervention do(X_{intervention_var} = 2.0)")
    print(f"  ✓ Causal effect: {result.causal_effect.mean().item():.4f}")
    
    # Counterfactual
    observed = torch.randn(10, 5)
    cf_result = model.counterfactual_query(
        observed,
        if_x=(0, torch.ones(10) * 3.0),
        then_y=4
    )
    print(f"  ✓ Counterfactual effect: {cf_result.effect.mean().item():.4f}")


def demo_temporal():
    """Demo: Temporal Prediction Network."""
    print("\n" + "="*60)
    print("WILD MODEL 5: Temporal Prediction Network")
    print("="*60)
    print("Concept: Predictive processing / active inference")
    
    model = create_temporal_prediction_network(
        input_dim=64, hidden_dim=128, num_levels=3
    )
    
    # Simulate observed sequence - use fewer steps than sequence_length
    observed = torch.randn(1, 10, 64)
    
    # Predict
    state = model.predict_sequence(observed, num_steps=5)
    print(f"  ✓ Free energy (prediction error): {state.free_energy:.4f}")
    print(f"  ✓ Predicted {len(state.predictions)} time steps")
    
    # Action for active inference
    target = torch.randn(64)
    action, error = model.take_action([state.predictions[-1][-1]], target)
    print(f"  ✓ Action generated, error: {error.norm().item():.4f}")


def demo_fractal():
    """Demo: Fractal Neural Network."""
    print("\n" + "="*60)
    print("WILD MODEL 6: Fractal Neural Network")
    print("="*60)
    print("Concept: Self-similar hierarchical architecture")
    
    model = create_fractal_network(
        input_dim=128, hidden_dim=256, num_layers=3
    )
    
    # Process input
    x = torch.randn(4, 128)
    result = model(x, return_all_scales=True)
    
    print(f"  ✓ Output shape: {result['output'].shape}")
    print(f"  ✓ Fractal dimension: {model.compute_fractal_dimension(x):.4f}")
    print(f"  ✓ Scales processed: {len(result['all_scales'][0])}")


def demo_neuromorphic():
    """Demo: Neuromorphic Spiking Network."""
    print("\n" + "="*60)
    print("WILD MODEL 7: Neuromorphic Spiking Network")
    print("="*60)
    print("Concept: Event-based spiking computation (LIF + STDP)")
    
    model = create_neuromorphic_network(
        input_dim=64, num_neurons=[128, 64], time_steps=30
    )
    
    # Process input
    x = torch.randn(4, 64)
    result = model(x, train_stdp=False)
    
    print(f"  ✓ Total spikes: {result['total_spikes']}")
    print(f"  ✓ Output shape: {result['output'].shape}")
    print(f"  ✓ Energy (spike count): {model.get_energy_consumption(result):.2f}")


def demo_synesthesia():
    """Demo: Cross-Modal Synesthesia Network."""
    print("\n" + "="*60)
    print("WILD MODEL 8: Cross-Modal Synesthesia Network")
    print("="*60)
    print("Concept: Multi-sensory blending and cross-modal mapping")
    
    model = create_synesthesia_network(
        modality_dims={'visual': 256, 'auditory': 128, 'textual': 512},
        shared_dim=256
    )
    
    # Multi-modal input
    inputs = {
        'visual': torch.randn(2, 256),
        'auditory': torch.randn(2, 128),
        'textual': torch.randn(2, 512)
    }
    
    # Process
    result = model(inputs, primary_modality='textual')
    
    print(f"  ✓ Modalities encoded: {list(result['representations'].keys())}")
    print(f"  ✓ Blended shape: {result['blended'].shape}")
    
    # Induce synesthesia
    synesthesia = result['synesthesia']
    if synesthesia:
        print(f"  ✓ Induced modalities: {list(synesthesia.induced_modalities.keys())}")
        print(f"  ✓ Consistency: {synesthesia.consistency_score:.4f}")


def run_all_demos():
    """Run all wild model demos."""
    print("\n" + "#"*60)
    print("# FRONTIERQU WILD MODELS DEMO")
    print("# 8 Cutting-Edge Experimental Architectures")
    print("#"*60)
    
    demo_memetic()
    demo_holographic()
    demo_consciousness()
    demo_causal()
    demo_temporal()
    demo_fractal()
    demo_neuromorphic()
    demo_synesthesia()
    
    print("\n" + "="*60)
    print("ALL WILD MODEL DEMOS COMPLETE")
    print("="*60)
    print("\nWild models implemented:")
    print("  1. Memetic Evolution - Ideas as replicators")
    print("  2. Holographic Memory - Content-addressable storage")
    print("  3. Consciousness Network - Global Workspace Theory")
    print("  4. Causal Intervention - Do-calculus reasoning")
    print("  5. Temporal Prediction - Predictive processing")
    print("  6. Fractal Network - Self-similar architecture")
    print("  7. Neuromorphic Spiking - Event-based computation")
    print("  8. Synesthesia Network - Cross-modal blending")
    print("\nUsage:")
    print("  from frontier_models.wild import *")
    print("  model = create_memetic_network()")
    print("  model = create_holographic_network()")
    print("  # ... etc")


if __name__ == '__main__':
    run_all_demos()
