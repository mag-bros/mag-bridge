from unittest.mock import MagicMock

from src.constants.bond_types import OverlapGroup
from src.core.cross_overlap_comparator import CrossOverlapComparator
from src.overlap_rules import CROSS_OVERLAP_RULES


def test_is_higher_priority():
    """Verify correct hierarchy comparison between two bond formulas."""
    assert CrossOverlapComparator.is_higher_priority("Ar-C=C", "C=C", OverlapGroup.DOUBLE_BONDS, CROSS_OVERLAP_RULES)
    assert not CrossOverlapComparator.is_higher_priority("C=C", "Ar-C=C", OverlapGroup.DOUBLE_BONDS, CROSS_OVERLAP_RULES)
    assert CrossOverlapComparator.is_higher_priority("cyclopropane", "cyclopentane", OverlapGroup.BICYCLIC_STRUCTURES, CROSS_OVERLAP_RULES)
    assert not CrossOverlapComparator.is_higher_priority("invalid", "C=C", OverlapGroup.DOUBLE_BONDS, CROSS_OVERLAP_RULES)


def test_sort_matches():
    """Verify group-level and intra-group ordering from CROSS_OVERLAP_RULES."""

    def make_candidates(group):
        c = MagicMock()
        c.cross_overlap_group = group
        return [c]

    grouped = {
        "C=C": make_candidates(OverlapGroup.DOUBLE_BONDS),
        "cyclopropane": make_candidates(OverlapGroup.BICYCLIC_STRUCTURES),
        "C=O": make_candidates(OverlapGroup.CARBONYL_BOND_TYPES),
        "CH2=CH-CH2-": make_candidates(OverlapGroup.DOUBLE_BONDS),
    }
    result = CrossOverlapComparator.sort_matches(grouped, CROSS_OVERLAP_RULES)
    formulas = [f for f, _ in result]

    assert formulas[0] == "C=O"
    assert formulas[1] == "cyclopropane"
    assert formulas.index("CH2=CH-CH2-") < formulas.index("C=C")
    assert formulas.index("CH2=CH-CH2-") > formulas.index("C=O")
    assert formulas.index("C=C") > formulas.index("C=O")
