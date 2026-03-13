from frontierqu.logic.deontic import (
    DeonticStatus, FiqhRule, derive_ruling,
    Obligatory, Forbidden, Recommended, Discouraged, Permissible
)

def test_five_deontic_categories():
    """Islamic law has exactly 5 deontic categories (al-ahkam al-khamsa)"""
    assert len(DeonticStatus) == 5
    assert DeonticStatus.WAJIB in DeonticStatus
    assert DeonticStatus.HARAM in DeonticStatus
    assert DeonticStatus.MANDUB in DeonticStatus
    assert DeonticStatus.MAKRUH in DeonticStatus
    assert DeonticStatus.MUBAH in DeonticStatus

def test_prayer_is_obligatory():
    """Prayer (salah) is wajib -- derived from imperative in 2:43"""
    rule = derive_ruling(verse=(2, 43), subject="salah")
    assert rule.status == DeonticStatus.WAJIB
    assert rule.evidence_verse == (2, 43)

def test_riba_is_forbidden():
    """Interest (riba) is haram -- derived from prohibition in 2:275"""
    rule = derive_ruling(verse=(2, 275), subject="riba")
    assert rule.status == DeonticStatus.HARAM

def test_naskh_overrides_earlier_ruling():
    """Abrogation: later verse supersedes earlier"""
    from frontierqu.logic.deontic import apply_naskh
    result = apply_naskh(earlier=(2, 240), later=(2, 234), topic="iddah")
    assert result.active_verse == (2, 234)

def test_qiyas_analogical_reasoning():
    """Qiyas: derive ruling for new case by analogy"""
    from frontierqu.logic.deontic import apply_qiyas
    result = apply_qiyas(
        asl_verse=(5, 90),
        asl_ruling=DeonticStatus.HARAM,
        illa="intoxication",
        far_case="beer"
    )
    assert result.status == DeonticStatus.HARAM
    assert result.reasoning_method == "qiyas"
