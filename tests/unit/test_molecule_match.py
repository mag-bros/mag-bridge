from pathlib import Path
from typing import Any

import pytest
from rdkit import Chem

from loader import SDFLoader
from src import SDF_TEST_DIR
from src.core.compound import MBCompound


def test_molecule_match() -> None:
    """Loop through SDF test cases files"""

    # Load all MBCompound instances from the given SDF file
    sdf_files = [p.name for p in SDF_TEST_DIR.glob("*.sdf")]
    compounds = [SDFLoader.Load(filename, "tests") for filename in sdf_files]

    EXCEPTION = ["S2O32-.sdf"]

    for compound in compounds:
        group = []
        for mol in compound.GetMols(to_rdkit=False):
            group.append(mol.ToSmiles())

        # Test Results
        try:
            # trunk-ignore(bandit/B101)
            # Exception (thiosulfate anion)
            if compound.source_file in EXCEPTION:
                print(
                    f'[INF] "{compound.source_file}": ⚠ Allowed {set(group)} canonical SMILES case'
                )
                continue

            # Standard assertion
            else:
                assert len(set(group)) == 1
                print(
                    f'[INF] "{compound.source_file}": ✅ One canonical SMILES created: {set(group)}'
                )
        except AssertionError as e:
            print(
                f'[ERR] "{compound.source_file}": ❌ {len(set(group))} canonical SMILES generated: {set(group)}'
            )
            raise e
