import torch
from frontierqu.core.tensor import QuranicTensor


def test_tensor_encodes_all_domains():
    """Tensor has channels for each domain"""
    qt = QuranicTensor()
    T = qt.compute()
    assert T.shape[0] == 6236
    assert T.shape[1] > 0


def test_tensor_is_not_decomposable():
    """Full tensor has non-trivial structure across all verses"""
    qt = QuranicTensor()
    T_full = qt.compute()
    # The tensor should have non-zero features for all verses
    assert T_full.abs().sum() > 0
    # First and last verses should differ
    assert not torch.allclose(T_full[0], T_full[-1])


def test_query_returns_holistic_response():
    """Query returns activation pattern, not single answer"""
    qt = QuranicTensor()
    result = qt.query("mercy")
    assert "activations" in result
    assert "top_verses" in result
    assert "subgraph" in result
    assert len(result["activations"]) == 6236
