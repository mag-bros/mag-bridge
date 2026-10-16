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
def test_compound_molar_mass(diamag_contr_params: tuple[int, DiamagneticContributionTestSDF]) -> None:
    """
    Validates computation of molar mass of the compound.
    Compare calculated molar mass with expected value.
    The tested set of the compound is the same as for diamagnetic contribution tests."""
    idx, test_case = diamag_contr_params
    compound = MBLoader.FromSDF(test_case.sdf_file, subdir="diamag_compound")
    compound_molar_mass = compound.CalcMolarMass()

    reference = test_case.molar_mass_reference
    assert reference is not None, f"no molar_mass_reference set for {test_case.sdf_file}"

    # Note that for tested compounds with heavy elements (As, Pb, Dy, Ag) the expected and reference value differ
    # in their least significant digits, yielding slight discrepancies of ~0.01 g/mol. This suggest that the ChemSketch
    # (reference) and RDKit compute molar mass from different revisions of the IUPAC standard atomic weights.
    TOLERANCE = 0.05  # g/mol

    try:
        assert compound_molar_mass == pytest.approx(reference, abs=TOLERANCE)
        drift = abs(compound_molar_mass - reference)
        if round(drift, 2) > 0:
            print(
                f'[WRN] "{compound.loaded_from}": ⚠ molar mass {compound_molar_mass:.2f} '
                f"drifted {drift:.2f} g/mol from reference {reference} (within ±{TOLERANCE} g/mol)"
            )
        else:
            print(f'[INF] "{compound.loaded_from}": ✅ Molar mass is as expected: {compound_molar_mass:.2f}')
    except AssertionError as e:
        print(
            f'[ERR] "{compound.loaded_from}": ❌ result {round(compound_molar_mass, 2)} '
            f"differs from reference {reference} by more than ±{TOLERANCE} g/mol"
        )
        raise e
