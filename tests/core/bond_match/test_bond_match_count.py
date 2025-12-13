from importlib.abc import Loader

import pytest
from rdkit.Chem import MolFromSmiles, MolToSmiles

from src import BOND_MATCH_SUBDIR, DIAMAG_COMPOUND_CONSTITUTIVE_CORR_SUBDIR
from src.constants.bond_types import RELEVANT_BOND_TYPES, BondType
from src.core.compound import MBCompound
from src.loader import MBLoader, MBMolecule


def test_bond_match_count() -> None:
    all_smiles = ["ClC=CC(Cl)C=CCl"]

    for smiles in all_smiles:
        mol = MBLoader.MolFromSmiles(smiles=smiles)
        matches = []
        for idx, bond_type in enumerate(RELEVANT_BOND_TYPES):
            substruct_to_match: str = bond_type.SMARTS

            how_many_matched = len(mol.GetSubstructMatches(smarts=substruct_to_match))
            if how_many_matched:
                matches.append(
                    {
                        "count": how_many_matched,
                        "constitutive_corr": bond_type.constitutive_corr,
                        "bond_type": bond_type,
                    }
                )
        x = 1


def bond_match_count_pubchem():
    """
    1. Input: list of smiles
    2. Download SMARTS for given smiles, relation: 1 smiles contains a list of SMARTS
    3. Generate config
    4. Copy Paste this config into count_internal test
    """
    return
