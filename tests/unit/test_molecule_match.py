from pathlib import Path
from typing import Any

import pytest
from rdkit import Chem
from rdkit.Chem import MolKey

from src import MOLECULE_MATCH_SUBDIR, SDF_DIR
from src.constants import COMMON_MOLECULES
from src.core.compound import MBCompound
from src.loader import SDFLoader


@pytest.mark.parametrize(
    "common_mol",
    enumerate(COMMON_MOLECULES.items()),
    ids=lambda p: f"<test:{p[0]}> {p[1][0]}"
)
def test_molecule_match(common_mol: tuple[str, dict]) -> None:
    """Unit Test checking molecule substructure match utility done via SMILES format."""
    idx, (mol_key, mol_data) = common_mol
    sdf_file = mol_data['sdf_file']
    expected_smiles: set[str] = mol_data['SMILES']
    
    if sdf_file == '':
        pytest.skip(f'test:{idx} SDF file NOT FOUND. Please create it for: "{mol_key}" --- {mol_data}')
    
    # Load all MBCompound instances from the given SDF file 
    compound: MBCompound = SDFLoader.Load(sdf_file, subdir=MOLECULE_MATCH_SUBDIR)

    # List of SMILES representation for each molecule in given SDF compound
    sdf_compound_smiles: set[str] = { mol.ToSmiles() for mol in compound.GetMols(to_rdkit=False) }

    # Actual test
    # When two sets are compared, the order of their elements doesn't matter
    test_condition: bool = sdf_compound_smiles == expected_smiles
    
    error_msg = f'[ERR]: mol_key: {mol_key}, mol_data: {mol_data}'
    assert test_condition, error_msg
