import pytest

from src.core.bond_match import MBSubstructMatcher
from src.loader import MBLoader
from tests.core.bond_match.bond_match_test_data import (
    BOND_MATCH_TEST_CASES,
    BondMatchTestCase,
)


@pytest.mark.parametrize(
    "bond_type_test_params",
    list(enumerate(BOND_MATCH_TEST_CASES)),
    ids=lambda p: f"<{p[0]}> {p[1].SMILES}",
)
def test_bond_match_count(bond_type_test_params: tuple[int, BondMatchTestCase]) -> None:
    idx, bond_type_test = bond_type_test_params

    mol = MBLoader.MolFromSmiles(smiles=bond_type_test.SMILES)

    # Matching now includes the Postprocess() overlap logic (self + cross-formula)
    result = MBSubstructMatcher.GetMatches(mol=mol)

    assert bond_type_test.expected_matches == result.matchesCounter

    # Internal consistency check: counter must match final hit lists
    assert sum(result.matchesCounter.values()) == sum(
        len(hits) for hits in result.final_hits_by_formula.values()
    )
