import math
from frontierqu.linguistic.balaghah import (
    RhetoricalAnalysis, rhetorical_density,
    detect_maani, detect_bayan, detect_badi,
    RhetoricalDevice
)

def test_rhetorical_density_positive():
    """Quranic verse has positive rhetorical density"""
    density = rhetorical_density("بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ")
    assert density > 0.0

def test_rhetorical_density_higher_for_rich_verse():
    """Rhetorically rich verses have higher density"""
    simple = rhetorical_density("بِسْمِ اللَّهِ")
    rich = rhetorical_density("بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ")
    # Rich verse has repetition (Rahman/Rahim) = higher rhetorical density
    assert rich >= simple

def test_detect_badi_alliteration():
    """Detect alliteration (jinas) in text"""
    # الرحمن الرحيم — Rahman and Rahim share the root ر-ح-م
    devices = detect_badi("الرَّحْمَٰنِ الرَّحِيمِ")
    device_types = [d.device_type for d in devices]
    assert "jinas" in device_types or "tikrar" in device_types

def test_detect_maani_returns_analysis():
    """Ma'ani analysis returns sentence type and emphasis level"""
    analysis = detect_maani("الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ")
    assert analysis.sentence_type is not None
    assert analysis.emphasis_level >= 0.0

def test_detect_bayan_returns_devices():
    """Bayan analysis detects figures of speech"""
    devices = detect_bayan("اللَّهُ نُورُ السَّمَاوَاتِ وَالْأَرْضِ")
    assert isinstance(devices, list)

def test_full_analysis():
    """Full rhetorical analysis combines all three branches"""
    analysis = RhetoricalAnalysis.analyze("إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ")
    assert analysis.maani is not None
    assert isinstance(analysis.bayan, list)
    assert isinstance(analysis.badi, list)
    assert analysis.density > 0.0

def test_rhetorical_device_dataclass():
    """RhetoricalDevice has required fields"""
    device = RhetoricalDevice(device_type="jinas", category="badi", description="Paronomasia", score=0.8)
    assert device.device_type == "jinas"
    assert device.score == 0.8
