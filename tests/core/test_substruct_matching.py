from collections import Counter
from typing import Counter

import pytest

from src.core.substruct_matcher import MBSubstructMatcher
from src.loader import MBLoader
from tests.data.substruct_matching_tests import (
    SUBSTRUCT_MATCH_TESTS,
    SubstructMatchTest,
)


@pytest.mark.parametrize(
    "substruct_match_test",
    SUBSTRUCT_MATCH_TESTS,
    ids=lambda p: f"<{p.id}> {p.SMILES}",
)
def test_substruct_matches(substruct_match_test: SubstructMatchTest) -> None:
    """Test if a molecules matches all expected substructures - Bond Types."""

    mol = MBLoader.MolFromSmiles(smiles=substruct_match_test.SMILES)

    # Matching now includes the Postprocess() overlap logic (self + cross-formula)
    result = MBSubstructMatcher.GetMatches(mol=mol)

    def normalize_counter_keys(c: Counter[str]) -> Counter[str]:
        return Counter({k.rstrip(":").strip(): v for k, v in c.items()})

    assert normalize_counter_keys(
        substruct_match_test.expected_matches
    ) == normalize_counter_keys(result.matchesCounter)

    # Internal consistency check: counter must match final hit lists
    assert sum(result.matchesCounter.values()) == sum(
        len(hits) for hits in result.final_hits_by_formula.values()
    )
