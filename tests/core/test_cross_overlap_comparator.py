from src.constants.bond_types import CROSS_OVERLAP_RULES, CrossOverlapGroup
from src.core.cross_overlap_comparator import CrossOverlapComparator


def test_is_higher_priority():
    """Verify correct hierarchy comparison between two bond formulas."""
    assert CrossOverlapComparator.is_higher_priority("Ar-C=C", "C=C", CrossOverlapGroup.DOUBLE_BONDS, CROSS_OVERLAP_RULES)
    assert not CrossOverlapComparator.is_higher_priority("C=C", "Ar-C=C", CrossOverlapGroup.DOUBLE_BONDS, CROSS_OVERLAP_RULES)
    assert CrossOverlapComparator.is_higher_priority("cyclopropane", "cyclopentane", CrossOverlapGroup.BICYCLIC_STRUCTURES, CROSS_OVERLAP_RULES)
    assert not CrossOverlapComparator.is_higher_priority("invalid", "C=C", CrossOverlapGroup.DOUBLE_BONDS, CROSS_OVERLAP_RULES)
