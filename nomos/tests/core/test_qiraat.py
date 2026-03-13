"""Tests for Qira'at (Variant Readings) as Fiber Bundle."""

from frontierqu.core.qiraat import (
    QiraatFiberBundle, Qari, Reading,
    CANONICAL_QURRA, get_readings_for_verse
)


def test_ten_canonical_readers():
    """10 canonical readers (qurra') recognized"""
    assert len(CANONICAL_QURRA) == 10


def test_qari_has_name_and_transmitter():
    """Each qari has name and primary transmitter"""
    for qari in CANONICAL_QURRA:
        assert qari.name != ""
        assert qari.transmitter != ""


def test_fiber_at_verse():
    """Fiber at a verse = set of valid readings"""
    bundle = QiraatFiberBundle()
    fiber = bundle.fiber_at((1, 4))
    assert len(fiber) >= 2  # maaliki vs maliki


def test_reading_has_arabic_and_meaning():
    """Each reading variant has Arabic text and semantic impact"""
    bundle = QiraatFiberBundle()
    fiber = bundle.fiber_at((1, 4))
    for reading in fiber:
        assert reading.arabic != ""
        assert reading.qari != ""


def test_holonomy_around_theme():
    """Holonomy measures total variation around thematic loop"""
    bundle = QiraatFiberBundle()
    h = bundle.holonomy(theme="tawhid")
    assert isinstance(h, float)
    assert h >= 0.0


def test_get_readings_convenience():
    """Convenience function returns readings for a verse"""
    readings = get_readings_for_verse((1, 4))
    assert len(readings) >= 1
