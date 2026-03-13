from frontierqu.logic.isnad import (
    IsnadDAG, Narrator, ReliabilityGrade,
    NarratorRank, evaluate_chain
)

def test_reliability_grades():
    """Four standard hadith reliability grades"""
    assert hasattr(ReliabilityGrade, 'SAHIH')
    assert hasattr(ReliabilityGrade, 'HASAN')
    assert hasattr(ReliabilityGrade, 'DAIF')
    assert hasattr(ReliabilityGrade, 'MAWDU')

def test_narrator_ranks():
    """Narrator hierarchy: sahabah > tabi'in > ...."""
    assert hasattr(NarratorRank, 'SAHABI')
    assert hasattr(NarratorRank, 'TABII')
    assert hasattr(NarratorRank, 'TABA_TABII')

def test_dag_is_acyclic():
    """Isnad graph must be acyclic (no time travel)"""
    dag = IsnadDAG()
    assert dag.is_acyclic()

def test_dag_has_narrators():
    """DAG contains known narrators"""
    dag = IsnadDAG()
    assert len(dag.narrators) > 0

def test_chain_length():
    """Can compute chain length (longest path)"""
    dag = IsnadDAG()
    chain = dag.longest_chain()
    assert chain >= 1

def test_evaluate_chain():
    """Evaluate reliability of a transmission chain"""
    chain = ["Abu Hurayrah", "Ibn Shihab", "Malik", "Al-Bukhari"]
    grade = evaluate_chain(chain)
    assert grade in ReliabilityGrade

def test_weakest_link():
    """Find weakest narrator in a chain"""
    dag = IsnadDAG()
    weak = dag.weakest_link(["Abu Hurayrah", "Ibn Shihab", "Malik"])
    assert weak is not None
