import pytest

from src import DIAMAG_COMPOUND_ATOMS_SUBDIR, DIAMAG_COMPOUND_MOLECULES_SUBDIR
from src.core.compound import MBCompound
from src.loader import SDFLoader
from tests.core.test_data import CALC_DIAMAG_CONTR_TEST_CASES, CalcDiamagContrTestCase


@pytest.mark.parametrize(
    "test_case_params",
    list(enumerate(CALC_DIAMAG_CONTR_TEST_CASES)),
    ids=lambda p: f"<test:{p[0]}> {p[1].sdf_file}",
)
def test_calc_diamag_contr(
    test_case_params: tuple[int, CalcDiamagContrTestCase],
) -> None:
    """Internal Integration Test testing the whole diamag calcs process.
    Logical components:
        1. Load SDF
        2. Calc Diamag Contr
        3. Compare calculated result to expected
    """
    idx, test_case = test_case_params
    # Load all MBMolecule instances from the given SDF file
    compound: MBCompound = SDFLoader.Load(
        test_case.sdf_file, subdir=DIAMAG_COMPOUND_ATOMS_SUBDIR
    )

    # Calc Diamag Contr of a Compound defined by a single SDF file
    diamag_contr: float = compound.CalcDiamagContr()

    # Test Result
    try:
        assert round(diamag_contr, 2) == test_case.expected_contribution
        print(
            f'[INF] "{compound.source_file}": ✅ Diamag is as expected: {diamag_contr:.4f}'
        )
    except AssertionError as e:
        print(
            f'[ERR] "{compound.source_file}": ❌ result {round(diamag_contr, 2)} is not expected value: {test_case.expected_contribution}'
        )
        raise e
