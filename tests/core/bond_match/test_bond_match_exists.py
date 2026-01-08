import pytest

from src import BOND_MATCH_SUBDIR
from src.constants.bond_types import RELEVANT_BOND_TYPES, BondType
from src.core.compound import MBCompound
from src.loader import MBLoader, MBMolecule


@pytest.mark.parametrize(
    "bond_type_params",
    list(enumerate(RELEVANT_BOND_TYPES)),
    ids=lambda p: f"<{p[0]}> {p[1].formula}",
)
def test_bond_match_exists(
    bond_type_params: tuple[int, BondType],
) -> None:
    """Test Assumptions:
    1. Each SDF file was designed to contain exactly one molecule.
    2. The prepared SDF files comprise the simplest molecules that are able to represent given bond type.
    3. The aim of the test is to show that similar bond types are NOT incorrectly matched for the same structure.
    4. Only bond types from the reference https://doi.org/10.1021/ed085p532 are considered
    """

    idx, bond_type = bond_type_params
    substruct_to_match: str = bond_type.SMARTS

    # bond type test for internal SDF files
    # is bond_type.SMARTS substructure matched in each of the bond_type.sdf_files?
    for sdf_file in bond_type.sdf_files:
        compound: MBCompound = MBLoader.FromSDF(sdf_file, subdir=BOND_MATCH_SUBDIR)
        #  Each SDF File was designed to contain exactly one molecule.
        mol: MBMolecule = compound.GetMols(to_rdkit=False)[0]
        assert mol.HasSubstructMatch(smarts=substruct_to_match), (
            f"Test <{idx}> failed. "
            f"SDF file: {sdf_file} was expected to exclusively match SMARTS: {substruct_to_match}, "
            f"but it did not."
        )

    if not bond_type.ignore_benzene_substructure:
        print(
            f"In this test only, the benzene substructure is ignored for all molecules except the benzene molecule itself."
        )
        return

    # Test if SMARTS subsctructure matches only expected SDF files globally
    # The aim of the test is to show that similar bond types are NOT incorrectly matched for the same structure.
    # Example: SMARTS C=C should not match with structure containing C=C-C=C bond type
    matched_sdf_files = []
    for sdf_file in gather_bond_type_sdf_files():
        compound: MBCompound = MBLoader.FromSDF(sdf_file, subdir=BOND_MATCH_SUBDIR)
        #  Each SDF File was designed to contain exactly one molecule.
        mol: MBMolecule = compound.GetMols(to_rdkit=False)[0]
        if mol.HasSubstructMatch(smarts=substruct_to_match):
            matched_sdf_files.append(sdf_file)
    assert sorted(matched_sdf_files) == sorted(bond_type.sdf_files), (
        f"Test <{idx}> failed. "
        f"Expected SDF files: {bond_type.sdf_files}, "
        f"but got: {matched_sdf_files}"
    )


def gather_bond_type_sdf_files() -> list[str]:
    # Gather all SDF files from relevant bond types
    bond_type_sdf_files = []
    for bond_type in RELEVANT_BOND_TYPES:
        bond_type_sdf_files.extend(bond_type.sdf_files)
    # Check if all SDF files are unique
    assert len(bond_type_sdf_files) == len(set(bond_type_sdf_files)), (
        "SDF files are not unique across bond types."
    )

    return bond_type_sdf_files
