from typing import Any

import pytest

from src import DIAMAG_COMPOUND_ATOMS_SUBDIR
from src.core.compound import MBCompound
from src.loader import SDFLoader
from tests.integration.test_data import SDF_TEST_COMPOUNDS


@pytest.mark.parametrize("test_case", SDF_TEST_COMPOUNDS)
def test_calc_diamag_sdf_compounds(test_case: dict[str, Any]) -> None:
    """ Internal Integration Test testing the whole diamag calcs process.
    Logical components:
        1. Load SDF
        2. Calc Diamag Contr
        3. Compare calculated result to expected
    """
    # Load all MBMolecule instances from the given SDF file
    compound: MBCompound = SDFLoader.Load(test_case["sdf_file"], subdir=DIAMAG_COMPOUND_ATOMS_SUBDIR)

    # Calc Diamag Contr of a Compound defined by a single SDF file
    diamag_contr: float = compound.CalcDiamagContr()

    # Test Result
    try:
        # trunk-ignore(bandit/B101)
        assert round(diamag_contr, 2) == test_case["expected_diamag"]
        print(
            f'[INF] "{compound.source_file}": ✅ Diamag is as expected: {diamag_contr:.4f}'
        )
    except AssertionError as e:
        print(
            f'[ERR] "{compound.source_file}": ❌ result {round(diamag_contr, 2)} is not expected value: {test_case["expected_diamag"]}'
        )
        raise e
