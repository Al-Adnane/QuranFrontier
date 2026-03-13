#!/usr/bin/env python3
"""FrontierQu Models - Comprehensive Demo.

Demonstrates all 37+ model architectures with example usage.
"""

import torch
import sys
sys.path.insert(0, '/Users/mac/Desktop/FrontierQu')

from frontier_models.api import create_api


def demo_balaghah():
    """Demo: Balaghah Information Bottleneck."""
    print("\n" + "="*60)
    print("MODEL 17: Balaghah Information Bottleneck")
    print("="*60)
    
    api = create_api()
    
    # Example: Compress text while preserving rhetorical devices
    text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    
    print(f"Input: {text}")
    print("Task: Compress while preserving rhetorical beauty")
    
    try:
        model = api.load_model('balaghah_ib', vocab_size=30000)
        print(f"✓ Model loaded: {type(model).__name__}")
        print(f"  - Latent dim: {model.latent_dim}")
        print(f"  - Rhetorical devices tracked: {model.rhetorical_head.num_devices}")
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_nahw():
    """Demo: Nahw Constraint Grammar."""
    print("\n" + "="*60)
    print("MODEL 18: Nahw Constraint Grammar")
    print("="*60)
    
    api = create_api()
    
    # Example: Analyze Arabic syntax
    tokens = ["الكتاب", "على", "الطاولة"]
    
    print(f"Input: {tokens}")
    print("Task: Grammatical analysis (i'rab)")
    
    try:
        model = api.load_model('nahw_constraint', vocab_size=30000)
        print(f"✓ Model loaded: {type(model).__name__}")
        print(f"  - Roles: {len(model.constraint_learner.lstm._parameters) * 2} grammatical roles")
        print(f"  - Cases: 3 (marfu, mansub, majrur)")
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_sarf():
    """Demo: Sarf Group Network."""
    print("\n" + "="*60)
    print("MODEL 19: Sarf Group Network")
    print("="*60)
    
    api = create_api()
    
    # Example: Morphological derivation
    root = "كتب"
    pattern = "فَعَلَ"
    
    print(f"Root: {root}, Pattern: {pattern}")
    print("Task: Generate derived word")
    
    try:
        model = api.load_model('sarf_group', vocab_size=30000)
        print(f"✓ Model loaded: {type(model).__name__}")
        
        # Generate word
        generated = model.generate_word(root, pattern)
        print(f"  - Generated: {generated}")
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_simplicial():
    """Demo: Simplicial Attention Transformer."""
    print("\n" + "="*60)
    print("MODEL 16: Simplicial Attention Transformer")
    print("="*60)
    
    api = create_api()
    
    print("Task: Higher-order attention over simplicial complex")
    
    try:
        model = api.load_model('simplicial_attention', 
                               num_vertices=100, num_edges=200, num_triangles=50)
        print(f"✓ Model loaded: {type(model).__name__}")
        print(f"  - Embed dim: {model.embed_dim}")
        print(f"  - Attention heads: {model.vertex_attention[0].num_heads}")
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_quantum():
    """Demo: Quantum Superposition Embedding."""
    print("\n" + "="*60)
    print("MODEL 26: Quantum Superposition Embedding")
    print("="*60)
    
    api = create_api()
    
    text = "Meaning exists in superposition"
    
    print(f"Input: {text}")
    print("Task: Create quantum superposition of meanings")
    
    try:
        model = api.load_model('quantum_embedding', vocab_size=30000, hilbert_dim=64)
        print(f"✓ Model loaded: {type(model).__name__}")
        
        # Encode as quantum state
        tokens = torch.randint(0, 1000, (1, 32))
        state = model.encode(tokens)
        
        print(f"  - Hilbert dimension: {model.hilbert_dim}")
        print(f"  - State norm: {torch.norm(state.state_vector).item():.4f} (should be ~1.0)")
        print(f"  - Num basis states: {len(state.basis_states)}")
        
        # Measure
        result = model.measurement.measure(state, deterministic=True)
        print(f"  - Measurement outcome: {result.collapsed_state}")
        print(f"  - Outcome probability: {result.probability:.4f}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_deontic():
    """Demo: Deontic Logic Network."""
    print("\n" + "="*60)
    print("MODEL 23: Deontic Logic Network")
    print("="*60)
    
    api = create_api()
    
    print("Task: Classify action into deontic category")
    print("Categories: WAJIB, HARAM, MANDUB, MAKRUH, MUBAH")
    
    try:
        model = api.load_model('deontic_network', input_dim=768)
        print(f"✓ Model loaded: {type(model).__name__}")
        
        # Simulate input
        features = torch.randn(1, 10, 768)
        result = model.classify(features)
        
        print(f"  - Status: {result.status.name}")
        print(f"  - Confidence: {result.confidence:.2%}")
        print(f"  - Constraints satisfied: {result.constraints_satisfied}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_holistic():
    """Demo: Holistic Quranic GNN."""
    print("\n" + "="*60)
    print("MODEL 34: Holistic Quranic GNN")
    print("="*60)
    
    api = create_api()
    
    print("Task: Query entire Quran via graph neural network")
    print("Nodes: 6236 verses, Edges: sequential + thematic + cross-ref")
    
    try:
        model = api.load_model('holistic_gnn', input_dim=128, hidden_dim=256)
        print(f"✓ Model loaded: {type(model).__name__}")
        
        # Simulate verse features
        verse_features = torch.randn(6236, 128)
        query_emb = torch.randn(128)
        
        result = model.query(verse_features, query_emb, k=10)
        
        print(f"  - Top activations: {result.activations[:5].tolist()}")
        print(f"  - Themes detected: {result.themes}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_three_world():
    """Demo: Three-World Fusion."""
    print("\n" + "="*60)
    print("MODEL 35: Three-World Fusion (Neural + Symbolic + Categorical)")
    print("="*60)
    
    api = create_api()
    
    print("Task: Fuse neural, symbolic, and categorical reasoning")
    
    try:
        model = api.load_model('three_world', input_dim=512, hidden_dim=512)
        print(f"✓ Model loaded: {type(model).__name__}")
        
        # Simulate inputs
        x = torch.randn(1, 512)
        rule_ids = torch.randint(0, 100, (1, 5))
        obj_ids = torch.randint(0, 1000, (1, 10))
        
        output = model(x, rule_ids, obj_ids)
        
        print(f"  - Neural output dim: {output.neural_output.shape}")
        print(f"  - Symbolic confidence: {output.symbolic_confidence:.2%}")
        print(f"  - Categorical confidence: {output.categorical_confidence:.2%}")
        print(f"  - Fused output dim: {output.fused_output.shape}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_multi_agent():
    """Demo: Multi-Agent Debate."""
    print("\n" + "="*60)
    print("MODEL 30: Multi-Agent Debate System")
    print("="*60)
    
    api = create_api()
    
    topic = "Is this action permissible?"
    evidence = "Evidence from primary sources"
    
    print(f"Topic: {topic}")
    print("Agents: Proposer, Critic, Verifier")
    
    try:
        model = api.load_model('multi_agent_debate', hidden_dim=512)
        print(f"✓ Model loaded: {type(model).__name__}")
        
        # Simulate debate
        context = torch.randn(1, 512)
        evidence = torch.randn(1, 512)
        
        result = model.debate(context, evidence)
        
        print(f"  - Winner: {result.winner}")
        print(f"  - Consensus: {result.consensus:.2%}")
        print(f"  - Arguments exchanged: {len(result.arguments)}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_all():
    """Run all demos."""
    print("\n" + "#"*60)
    print("# FRONTIERQU MODELS - COMPREHENSIVE DEMO")
    print("# 37+ Novel Architectures from Quranic AI Research")
    print("#"*60)
    
    demo_balaghah()
    demo_nahw()
    demo_sarf()
    demo_simplicial()
    demo_quantum()
    demo_deontic()
    demo_holistic()
    demo_three_world()
    demo_multi_agent()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nTo use these models:")
    print("  from frontier_models.api import create_api")
    print("  api = create_api()")
    print("  model = api.load_model('model_name')")
    print("  result = api.run('model_name', input_data)")
    print("\nAvailable models:")
    
    api = create_api()
    for m in api.list_models():
        print(f"  - {m['name']} ({m['type']})")


if __name__ == '__main__':
    demo_all()
