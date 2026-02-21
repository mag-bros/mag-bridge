from src.constants.bond_types import CROSS_OVERLAP_RULES, CrossOverlapGroup
from src.core.cross_overlap_comparator import CrossOverlapComparator


def test_is_higher_priority():
    """Verify correct hierarchy comparison between two bond formulas."""
    assert CrossOverlapComparator.is_higher_priority("Ar-C=C", "C=C", CrossOverlapGroup.DOUBLE_BONDS, CROSS_OVERLAP_RULES)
    assert not CrossOverlapComparator.is_higher_priority("C=C", "Ar-C=C", CrossOverlapGroup.DOUBLE_BONDS, CROSS_OVERLAP_RULES)
    assert CrossOverlapComparator.is_higher_priority("cyclopropane", "cyclopentane", CrossOverlapGroup.BICYCLIC_STRUCTURES, CROSS_OVERLAP_RULES)
    assert not CrossOverlapComparator.is_higher_priority("invalid", "C=C", CrossOverlapGroup.DOUBLE_BONDS, CROSS_OVERLAP_RULES)


def test_get_priority_index():
    """Verify correct priority index retrieval for formulas, returning -1 for missing entries."""
    assert CrossOverlapComparator.get_priority_index("C=C", CrossOverlapGroup.DOUBLE_BONDS, CROSS_OVERLAP_RULES) == 3
    assert CrossOverlapComparator.get_priority_index("CH2=CH-CH2-", CrossOverlapGroup.DOUBLE_BONDS, CROSS_OVERLAP_RULES) == 0
    assert CrossOverlapComparator.get_priority_index("RC(=O)NH2", CrossOverlapGroup.CARBONYL_BOND_TYPES, CROSS_OVERLAP_RULES) == 0
    assert CrossOverlapComparator.get_priority_index("invalid", CrossOverlapGroup.DOUBLE_BONDS, CROSS_OVERLAP_RULES) == -1
