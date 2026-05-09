import pytest
from src.loader import MBLoader
from tests.data.data_quality_tests import CALC_DIAMAG_QUALITY_TESTS, DataQualityDiamagContrTestsSDF


def _safe_id(p) -> str:
    try:
        return f"<{p[0]}> {p[1].sdf_file}"
    except Exception:
        return str(p)


@pytest.mark.parametrize(
    "diamag_contr_params",
    list(enumerate(CALC_DIAMAG_QUALITY_TESTS)),
    ids=_safe_id,
)
def test_diamag_contr_quality(diamag_contr_params: tuple[int, DataQualityDiamagContrTestsSDF]) -> None:
    """Validation test comparing calculated and measured diamagnetic susceptibility for a chemical compound."""

    idx, test_case = diamag_contr_params
    compound = MBLoader.FromSDF(test_case.sdf_file, subdir="diamag_compound")
    calculated_diamag_sus = compound.CalcDiamagContr()
    diamag_sus_precent_error = abs(round(((calculated_diamag_sus - test_case.measured_diamag_sus) / test_case.measured_diamag_sus * 100), 2))
    percent_error_limit = 5.0

    if diamag_sus_precent_error < percent_error_limit:
        print(f'[INF] "{compound.loaded_from}": ✅ Percent error {diamag_sus_precent_error:.1f}% within acceptable deviation')
    else:
        print(f'[INF] "{compound.loaded_from}": ⚠️ Percent error {diamag_sus_precent_error:.1f}% HIGHER than acceptable deviation')
