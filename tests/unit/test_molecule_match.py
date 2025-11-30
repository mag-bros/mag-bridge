from pathlib import Path
from typing import Any

import pytest
from rdkit import Chem
from rdkit.Chem import MolKey

from src import MOLECULE_MATCH_SUBDIR, SDF_DIR
from src.constants import COMMON_MOLECULES
from src.core.compound import MBCompound
from src.loader import SDFLoader


def _run_molecule_match(
    group: str,
    idx: int,
    mol_key: str,
    mol_data: dict,
) -> None:
    sdf_file = mol_data["sdf_file"]
    expected_smiles: set[str] = mol_data["SMILES"]

    if not sdf_file:
        pytest.skip(
            f"test:{idx} SDF file NOT FOUND. "
            f'Please create it for: "{group}/{mol_key}" --- {mol_data}'
        )

    compound: MBCompound = SDFLoader.Load(sdf_file, subdir=MOLECULE_MATCH_SUBDIR)

    sdf_compound_smiles: set[str] = {
        mol.ToSmiles() for mol in compound.GetMols(to_rdkit=False)
    }

    # when comparing two sets with "==" the order of elements doesn't matter
    test_condition: bool = sdf_compound_smiles == expected_smiles
    error_msg = (
        f"[ERR]: group={group}, mol_key={mol_key}, "
        f"found={sdf_compound_smiles}, expected={expected_smiles}"
    )
    assert test_condition, error_msg


def _params_for(group: str):
    return pytest.mark.parametrize(
        "common_mol",
        enumerate(COMMON_MOLECULES[group].items()),
        ids=lambda p: f"<test:{p[0]}> {p[1][0]}",
    )


@_params_for("anions")
def test_molecule_match_anions(common_mol: tuple[int, tuple[str, dict]]) -> None:
    idx, (mol_key, mol_data) = common_mol
    _run_molecule_match("anions", idx, mol_key, mol_data)


@_params_for("ligands")
def test_molecule_match_ligands(common_mol: tuple[int, tuple[str, dict]]) -> None:
    idx, (mol_key, mol_data) = common_mol
    _run_molecule_match("ligands", idx, mol_key, mol_data)


@_params_for("organic_solvents")
def test_molecule_match_organic_solvents(
    common_mol: tuple[int, tuple[str, dict]],
) -> None:
    idx, (mol_key, mol_data) = common_mol
    _run_molecule_match("organic_solvents", idx, mol_key, mol_data)
