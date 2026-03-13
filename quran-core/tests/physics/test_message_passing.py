import torch
from frontierqu.physics.message_passing import QuranicGNN

def test_gnn_processes_all_verses():
    """GNN takes entire Quran and outputs verse representations"""
    gnn = QuranicGNN(input_dim=16, hidden_dim=32, num_layers=3)
    x = torch.randn(6236, 16)
    out = gnn(x)
    assert out.shape == (6236, 32)

def test_gnn_respects_edge_types():
    """Different edge types have different weight matrices"""
    gnn = QuranicGNN(input_dim=16, hidden_dim=32, num_layers=3)
    assert len(gnn.edge_type_weights) >= 3

def test_query_produces_subgraph_activation():
    """Query returns activation pattern, not single verse"""
    gnn = QuranicGNN(input_dim=16, hidden_dim=32, num_layers=3)
    x = torch.randn(6236, 16)
    query = torch.randn(32)
    activations = gnn.query(x, query)
    assert activations.shape == (6236,)
    assert (activations >= 0).all()
    assert (activations <= 1).all()

def test_message_passing_is_holistic():
    """Changing one verse's features affects ALL verses"""
    gnn = QuranicGNN(input_dim=16, hidden_dim=32, num_layers=3)
    x = torch.randn(6236, 16)
    out1 = gnn(x).clone()
    x[0] += 10.0
    out2 = gnn(x)
    assert not torch.allclose(out1[-1], out2[-1], atol=1e-4)
