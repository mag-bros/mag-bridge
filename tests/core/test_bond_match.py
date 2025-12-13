import pytest

from src import DIAMAG_COMPOUND_CONSTITUTIVE_CORR_SUBDIR
from src.constants.bonds import DIAMAG_RELEVANT_BONDS, DiamagRelevantBond
from src.core.compound import MBCompound
from src.loader import SDFFileNotFoundError, SDFLoader


@pytest.mark.parametrize(
    "diamag_relevant_bond_params",
    list(enumerate(DIAMAG_RELEVANT_BONDS)),
    ids=lambda p: f"<test:{p[0]}> {p[1].sdf_file}",
)
def test_bond_match(
    diamag_relevant_bond_params: tuple[int, DiamagRelevantBond],
) -> None:
    """Expected behavior is that each molecule should be matched with exactly one expected SMARTS pattern."""
    idx, drb = diamag_relevant_bond_params
    expected_smarts = drb.SMARTS

    try:
        compound: MBCompound = SDFLoader.Load(
            drb.sdf_file, subdir=DIAMAG_COMPOUND_CONSTITUTIVE_CORR_SUBDIR
        )
    except SDFFileNotFoundError as e:
        pytest.skip(f"test:{idx} SDF file NOT FOUND. {e}")

    matched_bonds = []
    for mol in compound.GetMols(to_rdkit=False):
        if mol.HasSubstructMatch(smarts=expected_smarts):
            matched_bonds.append(mol)

    assert len(matched_bonds) == 1, (
        f"\n[Test {idx} FAILED]\nExpected SMARTS:\n  {expected_smarts}\n\n"
    )
