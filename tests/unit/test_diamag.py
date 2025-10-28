import pytest
from core.molecule import MBMolecule
from diamag import calc_diamag_contr
from loader import SDFLoader
from tests.unit.test_data import MOLECULES_DATA_DEPRECATED, SDF_TEST_DATA


@pytest.mark.parametrize("testcase", SDF_TEST_DATA)
def test_calc_diamag_contr(testcase):
    """Verifies diamagnetic calculations are correct using RDKit underneath."""
    mols: list[MBMolecule] = SDFLoader.Load(testcase['sdf_file'])
    for mol in mols:
        result = mol.CalcDiamagContr()
        assert round(result, 2) == testcase["expected_diamag"]

@pytest.mark.skip(reason="deprecation")
def test_calc_diamag_contr_deprecated():
    """Verifies diamag calculations are correct."""

    for molecule in MOLECULES_DATA_DEPRECATED:
        result = calc_diamag_contr(molecule["elements"])
        assert molecule["diamag"] == round(result, 2)
