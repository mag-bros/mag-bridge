import pytest

from src import DIAMAG_COMPOUND_ATOMS_SUBDIR, DIAMAG_COMPOUND_MOLECULES_SUBDIR
from src.core.compound import MBCompound
from src.loader import SDFLoader
from tests.core.test_data import SDF_TEST_COMPOUNDS, DiamagTestCase


@pytest.mark.parametrize(
    "test_compound_params",
    list(enumerate(SDF_TEST_COMPOUNDS)),
    ids=lambda p: f"<test:{p[0]}> {p[1].sdf_file}",
)
def test_calc_diamag_sdf_compounds(
    test_compound_params: tuple[int, DiamagTestCase],
) -> None:
    """Internal Integration Test testing the whole diamag calcs process.
    Logical components:
        1. Load SDF
        2. Calc Diamag Contr
        3. Compare calculated result to expected
    """
    idx, sdf_test_compound = test_compound_params
    # Load all MBMolecule instances from the given SDF file
    compound: MBCompound = SDFLoader.Load(
        sdf_test_compound.sdf_file, subdir=DIAMAG_COMPOUND_ATOMS_SUBDIR
    )

    # Calc Diamag Contr of a Compound defined by a single SDF file
    diamag_contr: float = compound.CalcDiamagContr()

    # Test Result
    try:
        assert round(diamag_contr, 2) == sdf_test_compound.expected_diamag_total
        print(
            f'[INF] "{compound.source_file}": ✅ Diamag is as expected: {diamag_contr:.4f}'
        )
    except AssertionError as e:
        print(
            f'[ERR] "{compound.source_file}": ❌ result {round(diamag_contr, 2)} is not expected value: {sdf_test_compound.expected_diamag_total}'
        )
        raise e
