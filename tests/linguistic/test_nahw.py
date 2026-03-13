"""Tests for Arabic syntax (nahw) as constraint satisfaction."""

from frontierqu.linguistic.nahw import (
    GrammaticalRole, CaseRequirement, IrabConstraint,
    parse_verse, check_constraints, SyntacticTree,
    CASE_ASSIGNMENTS
)


def test_grammatical_roles_exist():
    """Arabic grammar has at least 8 grammatical roles"""
    assert hasattr(GrammaticalRole, 'MUBTADA')
    assert hasattr(GrammaticalRole, 'KHABAR')
    assert hasattr(GrammaticalRole, 'FAIL')
    assert hasattr(GrammaticalRole, 'MAFUL')
    assert hasattr(GrammaticalRole, 'MAJRUR')


def test_case_requirements_exist():
    """Arabic has 4 case markers"""
    assert len(CaseRequirement) == 4


def test_mubtada_requires_raf():
    """Subject (mubtada) requires nominative case (raf')"""
    assert CASE_ASSIGNMENTS[GrammaticalRole.MUBTADA] == CaseRequirement.MARFU


def test_maful_requires_nasb():
    """Object (maf'ul) requires accusative case (nasb)"""
    assert CASE_ASSIGNMENTS[GrammaticalRole.MAFUL] == CaseRequirement.MANSUB


def test_majrur_requires_jarr():
    """Prepositional object requires genitive case (jarr)"""
    assert CASE_ASSIGNMENTS[GrammaticalRole.MAJRUR] == CaseRequirement.MAJRUR


def test_parse_verse_returns_constraints():
    """Parsing a verse returns i'rab constraints"""
    tokens = ["الحمد", "لله", "رب", "العالمين"]
    constraints = parse_verse(tokens)
    assert len(constraints) > 0
    assert all(isinstance(c, IrabConstraint) for c in constraints)


def test_check_constraints_valid():
    """Valid i'rab passes constraint check"""
    constraints = [
        IrabConstraint(word="الحمد", role=GrammaticalRole.MUBTADA,
                       required_case=CaseRequirement.MARFU,
                       actual_case=CaseRequirement.MARFU),
    ]
    assert check_constraints(constraints) is True


def test_check_constraints_invalid():
    """Invalid i'rab fails constraint check"""
    constraints = [
        IrabConstraint(word="الحمد", role=GrammaticalRole.MUBTADA,
                       required_case=CaseRequirement.MARFU,
                       actual_case=CaseRequirement.MANSUB),
    ]
    assert check_constraints(constraints) is False


def test_syntactic_tree_creation():
    """Can create a syntactic dependency tree"""
    tree = SyntacticTree(root_word="الحمد", root_role=GrammaticalRole.MUBTADA)
    tree.add_child("لله", GrammaticalRole.MAJRUR, parent="الحمد")
    assert tree.depth() >= 1
    assert len(tree.nodes) >= 2
