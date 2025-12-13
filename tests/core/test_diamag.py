import pytest

from src import (
    DIAMAG_COMPOUND_ATOMS_SUBDIR,
    DIAMAG_COMPOUND_CONSTITUTIVE_CORR_SUBDIR,
    DIAMAG_COMPOUND_MOLECULES_SUBDIR,
)
from src.core.compound import MBCompound
from src.loader import MBLoader
from tests.core.test_data import (
    CALC_DIAMAG_CONTR_TEST_CASES,
    DiamagneticContributionTestSDF,
)


def _run_diamag_contr_test(
    subdir: str,
    idx: int,
    test_case: DiamagneticContributionTestSDF,
) -> None:
    """Internal Integration Test testing the whole diamag calcs process.
    Logical components:
        1. Load SDF
        2. Calc Diamag Contr
        3. Compare calculated result to expected
    """
    compound: MBCompound = MBLoader.FromSDF(test_case.sdf_file, subdir=subdir)
    diamag_contr: float = compound.CalcDiamagContr()

    try:
        assert round(diamag_contr, 2) == test_case.expected_contribution
        print(
            f'[INF] "{compound.loaded_from}": ✅ Diamag is as expected: {diamag_contr:.4f}'
        )
    except AssertionError as e:
        print(
            f'[ERR] "{compound.loaded_from}": ❌ result {round(diamag_contr, 2)} is not expected value: {test_case.expected_contribution}'
        )
        raise e


def _params_for(subdir: str):
    return pytest.mark.parametrize(
        "diamag_contr_params",
        list(enumerate(CALC_DIAMAG_CONTR_TEST_CASES[subdir])),
        ids=lambda p: f"<test:{p[0]}> {p[1].sdf_file}",
    )


@_params_for(subdir=DIAMAG_COMPOUND_ATOMS_SUBDIR)
def test_diamag_contr_calc_atoms(
    diamag_contr_params: tuple[int, DiamagneticContributionTestSDF],
) -> None:
    idx, test_case = diamag_contr_params
    _run_diamag_contr_test(
        subdir=DIAMAG_COMPOUND_ATOMS_SUBDIR,
        idx=idx,
        test_case=test_case,
    )


@_params_for(subdir=DIAMAG_COMPOUND_MOLECULES_SUBDIR)
def test_diamag_contr_calc_molecules(
    diamag_contr_params: tuple[int, DiamagneticContributionTestSDF],
) -> None:
    idx, test_case = diamag_contr_params
    _run_diamag_contr_test(
        subdir=DIAMAG_COMPOUND_MOLECULES_SUBDIR,
        idx=idx,
        test_case=test_case,
    )


@_params_for(subdir=DIAMAG_COMPOUND_CONSTITUTIVE_CORR_SUBDIR)
def test_diamag_contr_calc_constitutive_corr(
    diamag_contr_params: tuple[int, DiamagneticContributionTestSDF],
) -> None:
    idx, test_case = diamag_contr_params
    _run_diamag_contr_test(
        subdir=DIAMAG_COMPOUND_CONSTITUTIVE_CORR_SUBDIR,
        idx=idx,
        test_case=test_case,
    )
