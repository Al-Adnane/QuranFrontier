"""Comprehensive test suite for all 21 spiritual tradition neural networks.

Tests instantiation, forward pass, and output shape for every model.
Pure PyTorch/numpy - no external dependencies.
"""

import sys
import os
import traceback

import torch

# Add parent paths so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models', 'spiritual_traditions'))


def test_catuskoti_network():
    from models.spiritual_traditions.catuskoti_network import CatuskotiNetwork
    model = CatuskotiNetwork(vocab_size=100, embed_dim=32, hidden_dim=64)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x, num_reasoning_steps=3)
    assert result['output'].shape == (2, 1)
    assert result['final_truth_values'].shape == (2, 4)
    assert not torch.isnan(result['output']).any()
    return True


def test_p_adic_network():
    from models.spiritual_traditions.p_adic_network import PAdicNeuralNetwork
    model = PAdicNeuralNetwork(vocab_size=100, embed_dim=32, hidden_dim=64, num_heads=4, tree_depth=3, p=2)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x)
    assert result['output'].shape == (2, 32)
    assert result['global_repr'].shape == (2, 32)
    assert not torch.isnan(result['output']).any()
    return True


def test_sufi_imaginal_network():
    from models.spiritual_traditions.sufi_imaginal_network import SufiImaginalNetwork
    model = SufiImaginalNetwork(vocab_size=100, embed_dim=64, hidden_dim=128)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x)
    assert result['haqiqa'].shape == (2, 1)
    assert result['imaginal_state'].material.shape == (2, 64)
    assert not torch.isnan(result['haqiqa']).any()
    return True


def test_analects_network():
    from models.spiritual_traditions.analects_network import AnalectsNetwork
    model = AnalectsNetwork(vocab_size=100, embed_dim=64, num_commentators=4)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x)
    assert result['junzi_score'].shape == (2, 1)
    assert result['virtue_state'].ren.shape == (2, 64)
    assert not torch.isnan(result['junzi_score']).any()
    return True


def test_bon_soul_retrieval_network():
    from models.spiritual_traditions.bon_soul_retrieval_network import BonSoulRetrievalNetwork
    model = BonSoulRetrievalNetwork(vocab_size=100, embed_dim=64)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x)
    assert result['wholeness'].shape == (2, 1)
    assert result['fragments']['is_fragmented'].shape == (2, 1)
    assert not torch.isnan(result['wholeness']).any()
    return True


def test_conceptual_blending_network():
    from models.spiritual_traditions.conceptual_blending import ConceptualBlendingNetwork
    model = ConceptualBlendingNetwork(vocab_size=100, element_dim=32, max_elements=5)
    model.eval()
    batch, n_elem = 2, 5
    s1_elem = torch.randint(0, 100, (batch, n_elem))
    s1_rel = torch.randint(0, 20, (batch, n_elem, n_elem))
    s1_frame = torch.randint(0, 100, (batch,))
    s2_elem = torch.randint(0, 100, (batch, n_elem))
    s2_rel = torch.randint(0, 20, (batch, n_elem, n_elem))
    s2_frame = torch.randint(0, 100, (batch,))
    with torch.no_grad():
        result = model(s1_elem, s1_rel, s1_frame, s2_elem, s2_rel, s2_frame, num_elaboration_steps=3)
    assert result['blend_result'].blended_space.elements.shape == (batch, n_elem, 32)
    assert isinstance(result['creativity_score'], float)
    return True


def test_gnostic_aeons_network():
    from models.spiritual_traditions.gnostic_aeons_network import GnosticAeonsNetwork
    model = GnosticAeonsNetwork(vocab_size=100, embed_dim=64)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x)
    assert result['gnosis'].shape == (2, 1)
    assert result['sophia']['wisdom'].shape == (2, 1)
    assert len(result['aeons']) == 4
    assert not torch.isnan(result['gnosis']).any()
    return True


def test_hermetic_correspondence_network():
    from models.spiritual_traditions.hermetic_correspondence_network import HermeticCorrespondenceNetwork
    model = HermeticCorrespondenceNetwork(vocab_size=100, embed_dim=64)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x)
    assert result['wisdom'].shape == (2, 1)
    assert result['correspondence']['correspondence_score'].shape == (2, 1)
    assert not torch.isnan(result['wisdom']).any()
    return True


def test_i_ching_network():
    from models.spiritual_traditions.i_ching_network import IChingNetwork
    model = IChingNetwork(input_dim=64, hex_dim=64, hidden_dim=128)
    model.eval()
    x = torch.randn(2, 64)
    with torch.no_grad():
        result = model(x)
    assert result['judgment'].shape == (2, 1)
    assert result['hex_state'].lines.shape == (2, 6)
    assert not torch.isnan(result['judgment']).any()
    return True


def test_ifa_divination_network():
    from models.spiritual_traditions.ifa_divination_network import IfaDivinationNetwork
    model = IfaDivinationNetwork(input_dim=64, odu_dim=64, wisdom_dim=128)
    model.eval()
    x = torch.randn(2, 64)
    with torch.no_grad():
        result = model(x)
    assert result['divination_result'].shape == (2, 1)
    assert result['binary_signature'].shape == (2, 8)
    assert not torch.isnan(result['divination_result']).any()
    return True


def test_iit_network():
    from models.spiritual_traditions.iit_network import IntegratedInformationNetwork
    model = IntegratedInformationNetwork(input_dim=32, hidden_dim=64, num_units=16)
    model.eval()
    x = torch.randn(2, 10, 32)
    with torch.no_grad():
        result = model(x, compute_phi=True)
    assert result['final_state'].shape == (2, 16)
    assert result['phi'] is not None
    assert result['phi'].shape == (2,)
    assert not torch.isnan(result['integration_score']).any()
    return True


def test_jain_seven_valued_network():
    from models.spiritual_traditions.jain_seven_valued_network import JainSevenValuedNetwork
    model = JainSevenValuedNetwork(vocab_size=100, embed_dim=64, hidden_dim=128)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x)
    assert result['syadvada'].shape == (2, 7)
    assert result['truth_state'].probabilities.shape == (2, 7)
    assert len(result['truth_values']) == 7
    return True


def test_kabbalah_sefirot_network():
    from models.spiritual_traditions.kabbalah_sefirot_network import KabbalahSefirotNetwork
    model = KabbalahSefirotNetwork(vocab_size=100, embed_dim=64, hidden_dim=128)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x, num_iterations=2)
    assert result['shekhinah'].shape == (2, 1)
    assert len(result['sefirot_states']) == 10
    assert not torch.isnan(result['shekhinah']).any()
    return True


def test_nahuatl_theater_network():
    from models.spiritual_traditions.nahuatl_theater_network import NahuatlTheaterNetwork
    model = NahuatlTheaterNetwork(vocab_size=100, embed_dim=64, hidden_dim=128, num_roles=4)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x)
    assert result['syncretic_understanding'].shape == (2, 1)
    assert result['blend_result']['tension'].shape == (2, 1)
    assert not torch.isnan(result['syncretic_understanding']).any()
    return True


def test_polynesian_wayfinding_network():
    from models.spiritual_traditions.polynesian_wayfinding_network import PolynesianWayfindingNetwork
    model = PolynesianWayfindingNetwork(embed_dim=64)
    model.eval()
    batch = 2
    star_pos = torch.randn(batch, 5, 2)
    wave = torch.randn(batch, 4)
    wind = torch.randn(batch, 3)
    pos = torch.randn(batch, 64)
    with torch.no_grad():
        result = model(star_pos, wave, wind, pos)
    assert result['confidence'].shape == (2, 1)
    assert result['etak']['position'].shape == (2, 2)
    assert not torch.isnan(result['confidence']).any()
    return True


def test_predictive_coding_network():
    from models.spiritual_traditions.predictive_coding import PredictiveCodingNetwork
    model = PredictiveCodingNetwork(input_dim=32, hidden_dims=[64, 32, 16, 8], action_dim=4)
    model.eval()
    x = torch.randn(2, 32)
    with torch.no_grad():
        result = model(x)
    assert result['free_energy'].shape == (2, 1)
    assert len(result['hidden_states']) == 4
    assert not torch.isnan(result['free_energy']).any()
    return True


def test_shinto_musubi_network():
    from models.spiritual_traditions.shinto_musubi_network import ShintoMusubiNetwork
    model = ShintoMusubiNetwork(vocab_size=100, embed_dim=64)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x)
    assert result['harmony'].shape == (2, 1)
    assert result['harai']['purity'].shape == (2, 1)
    assert not torch.isnan(result['harmony']).any()
    return True


def test_stoic_lekta_network():
    from models.spiritual_traditions.stoic_lekta_network import StoicLektaNetwork
    model = StoicLektaNetwork(vocab_size=100, embed_dim=64)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x)
    assert result['proposition'].shape == (2, 1)
    assert result['predicate'].shape == (2, 64)
    assert not torch.isnan(result['proposition']).any()
    return True


def test_vedic_network():
    from models.spiritual_traditions.vedic_network import VedicNetwork
    model = VedicNetwork(vocab_size=100, embed_dim=64, hidden_dim=128)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x)
    assert result['brahman_realization'].shape == (2, 1)
    assert result['essence'].shape == (2, 64)
    assert not torch.isnan(result['brahman_realization']).any()
    return True


def test_yogasutra_network():
    from models.spiritual_traditions.yogasutra_network import YogasutraNetwork
    model = YogasutraNetwork(vocab_size=100, sutra_dim=32, hidden_dim=64)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x)
    assert result['kaivalya'].shape == (2, 1)
    assert result['samadhi_result']['samadhi_depth'].shape == (2, 1)
    assert not torch.isnan(result['kaivalya']).any()
    return True


def test_zoroastrian_dualism_network():
    from models.spiritual_traditions.zoroastrian_dualism_network import ZoroastrianDualismNetwork
    model = ZoroastrianDualismNetwork(vocab_size=100, embed_dim=64)
    model.eval()
    x = torch.randint(0, 100, (2, 8))
    with torch.no_grad():
        result = model(x)
    assert result['asha'].shape == (2, 1)
    assert result['battle']['outcome'].shape == (2, 1)
    assert not torch.isnan(result['asha']).any()
    return True


ALL_TESTS = [
    ("CatuskotiNetwork", test_catuskoti_network),
    ("PAdicNeuralNetwork", test_p_adic_network),
    ("SufiImaginalNetwork", test_sufi_imaginal_network),
    ("AnalectsNetwork", test_analects_network),
    ("BonSoulRetrievalNetwork", test_bon_soul_retrieval_network),
    ("ConceptualBlendingNetwork", test_conceptual_blending_network),
    ("GnosticAeonsNetwork", test_gnostic_aeons_network),
    ("HermeticCorrespondenceNetwork", test_hermetic_correspondence_network),
    ("IChingNetwork", test_i_ching_network),
    ("IfaDivinationNetwork", test_ifa_divination_network),
    ("IntegratedInformationNetwork", test_iit_network),
    ("JainSevenValuedNetwork", test_jain_seven_valued_network),
    ("KabbalahSefirotNetwork", test_kabbalah_sefirot_network),
    ("NahuatlTheaterNetwork", test_nahuatl_theater_network),
    ("PolynesianWayfindingNetwork", test_polynesian_wayfinding_network),
    ("PredictiveCodingNetwork", test_predictive_coding_network),
    ("ShintoMusubiNetwork", test_shinto_musubi_network),
    ("StoicLektaNetwork", test_stoic_lekta_network),
    ("VedicNetwork", test_vedic_network),
    ("YogasutraNetwork", test_yogasutra_network),
    ("ZoroastrianDualismNetwork", test_zoroastrian_dualism_network),
]


if __name__ == "__main__":
    passed = 0
    failed = 0
    errors = []

    print(f"Running {len(ALL_TESTS)} spiritual tradition model tests...")
    print("=" * 60)

    for name, test_fn in ALL_TESTS:
        try:
            test_fn()
            passed += 1
            print(f"  PASS  {name}")
        except Exception as e:
            failed += 1
            errors.append((name, str(e)))
            print(f"  FAIL  {name}: {e}")
            traceback.print_exc()

    print("=" * 60)
    print(f"Results: {passed}/{len(ALL_TESTS)} passed, {failed} failed")

    if errors:
        print("\nFailures:")
        for name, err in errors:
            print(f"  - {name}: {err}")
        sys.exit(1)
    else:
        print("\nAll 21 spiritual tradition models PASSED!")
        sys.exit(0)
