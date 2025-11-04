from typing import Any

import pytest

from loader import SDFLoader
from src.core.compound import MBCompound
from tests.unit.test_data import SDF_TEST_COMPOUNDS


@pytest.mark.parametrize("testcase", SDF_TEST_COMPOUNDS)
def test_calc_diamag_sdf_compounds(testcase: dict[str, Any]) -> None:
    """Loop through SDF test cases files"""
    for test_case in SDF_TEST_COMPOUNDS:
        # Load all MBMolecule instances from the given SDF file
        compound: MBCompound = SDFLoader.Load(test_case["sdf_file"])

        # Calc Diamag Contr of a Compound defined by a single SDF file
        diamag_contr: float = compound.CalcDiamagContr()

        # Test Result
        try:
            # trunk-ignore(bandit/B101)
            assert round(diamag_contr, 2) == test_case["expected_diamag"]
            print(
                f'[INF] "{compound.source_file}": ✅ Diamag is as expected: {diamag_contr:.4f}'
            )
        except AssertionError:
            print(
                f'[ERR] "{compound.source_file}": ❌ result {round(diamag_contr, 2)} is not expected value: {test_case["expected_diamag"]}'
            )
