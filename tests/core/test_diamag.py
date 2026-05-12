import pytest
from src.loader import MBLoader
from tests.data.diamag_tests import CALC_DIAMAG_CONTR_TESTS, DiamagneticContributionTestSDF


def _safe_id(p) -> str:
    try:
        return f"<{p[0]}> {p[1].sdf_file}"
    except Exception:
        return str(p)


@pytest.mark.parametrize(
    "diamag_contr_params",
    list(enumerate(CALC_DIAMAG_CONTR_TESTS)),
    ids=_safe_id,
)
def test_diamag_contr_calc(diamag_contr_params: tuple[int, DiamagneticContributionTestSDF]) -> None:
    """Integration test covering load -> calculate -> assert."""
    idx, test_case = diamag_contr_params
    compound = MBLoader.FromSDF(test_case.sdf_file, subdir="diamag_compound")
    diamag_contr = compound.CalcDiamagContr()

    try:
        assert round(diamag_contr, 2) == test_case.expected_contribution
        print(f'[INF] "{compound.loaded_from}": ✅ Diamag is as expected: {diamag_contr:.4f}')
    except AssertionError as e:
        print(f'[ERR] "{compound.loaded_from}": ❌ result {round(diamag_contr, 2)} is not expected value: {test_case.expected_contribution}')
        raise e
