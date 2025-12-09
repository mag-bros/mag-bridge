import pytest

from src import DIAMAG_COMPOUND_CONSTITUTIVE_CORR_SUBDIR
from src.constants.bonds import DIAMAG_RELEVANT_BONDS, DiamagRelevantBond
from src.core.compound import MBCompound
from src.loader import SDFLoader


@pytest.mark.parametrize(
    "diamag_relevant_bond_params",
    list(enumerate(DIAMAG_RELEVANT_BONDS)),
    ids=lambda p: f"<test:{p[0]}> {p[1].formula}",
)
def test_bond_match(
    diamag_relevant_bond_params: tuple[int, DiamagRelevantBond],
) -> None:
    idx, drb = diamag_relevant_bond_params

    if not drb.sdf_file:
        pytest.skip(
            f"test:{idx} SDF file NOT FOUND. "
            f'Please create it for: "{drb.formula}" --- {drb}'
        )

    compound: MBCompound = SDFLoader.Load(
        drb.sdf_file, subdir=DIAMAG_COMPOUND_CONSTITUTIVE_CORR_SUBDIR
    )
    for mol in compound.GetMols(to_rdkit=False):
        expected_smarts = drb.SMARTS
        calculated_mol_smarts = mol.smarts

        assert mol.HasSubstructMatch(smarts=expected_smarts), (
            f"Test <{idx}> Failed: Expected SMARTS '{expected_smarts}' not found in molecule SMARTS '{calculated_mol_smarts}' "
        )
