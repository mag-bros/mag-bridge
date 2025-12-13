from importlib.abc import Loader
from typing import Counter

import pytest
from rdkit.Chem import MolFromSmiles, MolToSmiles

from src import BOND_MATCH_SUBDIR, DIAMAG_COMPOUND_CONSTITUTIVE_CORR_SUBDIR
from src.constants.bond_types import RELEVANT_BOND_TYPES, BondType
from src.core.compound import MBCompound
from src.loader import MBLoader, MBMolecule
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
    result_matches = Counter()
    mol = MBLoader.MolFromSmiles(smiles=bond_type_test.SMILES)

    # Find all possible substructure matches for relevant bond types
    for relevant_bond_type in RELEVANT_BOND_TYPES:
        substruct_to_match: str = relevant_bond_type.SMARTS

        match: tuple[tuple[int]] = mol.GetSubstructMatches(smarts=substruct_to_match)
        if match:
            result_matches[relevant_bond_type.formula] += len(match)

    assert bond_type_test.expected_matches == result_matches
