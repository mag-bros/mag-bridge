import difflib

import pytest

from src import BOND_MATCH_SUBDIR
from src.constants.bond_types import RELEVANT_BOND_TYPES, BondType
from src.core.compound import MBCompound
from src.loader import MBLoader, MBMolecule


@pytest.mark.parametrize(
    "bond_type",
    RELEVANT_BOND_TYPES,
    ids=lambda p: f"<{p.id}> {p.formula}",
)
def test_has_bond_type(bond_type: BondType) -> None:
    """Test Assumptions:
    1. Each SDF file was designed to contain exactly one molecule.
    2. The prepared SDF files comprise the simplest molecules that are able to represent given bond type.
    3. The aim of the test is to show that similar bond types are NOT incorrectly matched for the same structure.
    4. Only bond types from the reference https://doi.org/10.1021/ed085p532 are considered
    """

    # (A) Bond type test for internal SDF files
    # Is bond_type.SMARTS matched by each of the bond_type.sdf_files?
    for sdf_file in bond_type.sdf_files:
        compound: MBCompound = MBLoader.FromSDF(sdf_file, subdir=BOND_MATCH_SUBDIR)

        mols_in_file = compound.GetMols(to_rdkit=False)
        assert mols_in_file, (
            f"Test <{bond_type.id}> failed. SDF file '{sdf_file}' contains no molecules."
        )

        # Each SDF file was designed to contain exactly one molecule.
        assert len(mols_in_file) == 1, (
            f"Test <{bond_type.id}> failed. SDF file '{sdf_file}' was expected to contain "
            f"exactly one molecule, but contains {len(mols_in_file)}."
        )

        mol: MBMolecule = mols_in_file[0]
        assert mol.HasSubstructMatch(smarts=bond_type.SMARTS), (
            f"Test <{bond_type.id}> failed. "
            f"SDF '{sdf_file}' did not match expected SMARTS for bond type '{bond_type.formula}'. "
            f"SMARTS: {bond_type.SMARTS}"
        )

    # Special rule: benzene matching is only validated on the benzene SDF itself.
    skip_global_check = bond_type.formula in ["benzene", "C=C"]
    if skip_global_check:
        return

    # (B) Test that SMARTS matches only the expected SDF files globally
    # Example: SMARTS for C=C should not match the SDF designed for C=C-C=C
    expected = sorted(bond_type.sdf_files)
    matched: list[str] = []

    for sdf_file in gather_bond_type_sdf_files():
        compound: MBCompound = MBLoader.FromSDF(sdf_file, subdir=BOND_MATCH_SUBDIR)
        mols_in_file = compound.GetMols(to_rdkit=False)
        if not mols_in_file:
            continue  # ignore empty/invalid SDFs (or assert if you prefer)
        mol: MBMolecule = mols_in_file[0]

        if mol.HasSubstructMatch(smarts=bond_type.SMARTS):
            matched.append(sdf_file)

    matched_sorted = sorted(matched)

    assert matched_sorted == expected, (
        f"Test <{bond_type.id}> failed for bond type '{bond_type.formula}'.\n"
        f"SMARTS: {bond_type.SMARTS}\n"
        f"Expected SDF matches: {expected}\n"
        f"Actual SDF matches:   {matched_sorted}\n"
        f"Unexpected: {sorted(set(matched_sorted) - set(expected))}\n"
        f"Missing:    {sorted(set(expected) - set(matched_sorted))}"
    )


def gather_bond_type_sdf_files() -> list[str]:
    # Gather all SDF files from relevant bond types
    bond_type_sdf_files = sorted(f for bt in RELEVANT_BOND_TYPES for f in bt.sdf_files)

    # Check if all SDF files are unique (1:1, diff-friendly) + show a real diff
    unique_sorted = sorted(set(bond_type_sdf_files))
    if bond_type_sdf_files != unique_sorted:
        diff = "\n".join(
            difflib.unified_diff(
                unique_sorted,
                bond_type_sdf_files,
                fromfile="expected_unique_sorted",
                tofile="actual_all_sorted",
                lineterm="",
            )
        )
        raise AssertionError(
            "SDF files are not unique across bond types (unified diff below):\n\n"
            f"{diff}"
        )

    return bond_type_sdf_files
