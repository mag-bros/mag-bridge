import os
from abc import ABC, abstractmethod
from pathlib import Path

from rdkit.Chem import (
    AddHs,
    Atom,
    GetMolFrags,
    Mol,
    MolFromSmarts,
    MolFromSmiles,
    MolToSmarts,
    MolToSmiles,
    RemoveHs,
    RWMol,
    SDMolSupplier,
)
from rdkit.Chem import rdMolDescriptors as rdmd

from core.compound import MBCompound
from src import SDF_DIR
from src.constants.provider import COMMON_DIAMAG_NOT_MATCHED, ConstDB
from src.core.atom import MBAtom
from src.core.molecule import MBMolecule
from src.utils.exceptions import (
    MBLoaderError,
    SDFEmptyFileError,
    SDFFileNotFoundError,
    SDFMalformedRecordError,
)


class MBLoader:
    """Utility for loading and validating SDF files."""

    @staticmethod
    def FromSDF(source_file: str, subdir=".") -> MBCompound:
        """Loads an SDF file and return a MBCompound object containing a list of molecules"""

        sdf_path = SDF_DIR.joinpath(subdir).joinpath(source_file)
        MBLoader.CheckSDF(sdf_path)

        raw_mols = list(SDMolSupplier(str(sdf_path), sanitize=True, removeHs=False))

        if not raw_mols:
            raise SDFEmptyFileError(f"No molecules found in file: {sdf_path}")

        failed = sum(1 for mol in raw_mols if mol is None)
        if failed:
            raise SDFMalformedRecordError(
                f"{failed} molecule(s) failed to parse in file '{sdf_path}'. "
                "Check the SDF syntax or atom typing."
            )

        loaded_mols = [
            MBMoleculeFactory.create(mol=mol, loaded_from=source_file, mol_index=i)
            for i, mol in enumerate(raw_mols)
            if mol
        ]

        if not loaded_mols:
            raise SDFEmptyFileError("No valid molecules loaded from any file.")

        compound = MBCompound(mols=loaded_mols, loaded_from=source_file)

        return compound

    @staticmethod
    def MolFromSmiles(smiles: str) -> MBMolecule:
        loaded_molecule = MBMoleculeFactory.create(
            mol=MolFromSmiles(SMILES=smiles), loaded_from=smiles
        )
        if not loaded_molecule:
            raise MBLoaderError(f"Error loading molecule from smiles: {smiles}")

        return loaded_molecule

    @staticmethod
    def CompoundFromSmiles(smiles: str) -> MBCompound: ...

    @staticmethod
    def CheckSDF(path: Path) -> None:
        """Perform comprehensive validation on the SDF file before parsing."""
        if not path.exists():
            raise SDFFileNotFoundError(f"File not found: {path}")

        if path.suffix.lower() != ".sdf":
            raise MBLoaderError(
                f"Invalid file extension '{path.suffix}'. Expected .sdf"
            )

        if not path.is_file() or not os.access(path, os.R_OK):
            raise MBLoaderError(f"File is not readable: {path}")

        if path.stat().st_size == 0:
            raise SDFEmptyFileError(f"File '{path}' is empty.")

        with open(path, "rb") as f:
            if b"\x00" in f.read(256):
                raise MBLoaderError(
                    f"File '{path}' appears to be binary, not SDF text."
                )

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if not ("M  END" in content or "$$$$" in content):
                raise MBLoaderError(
                    f"File '{path}' does not appear to contain valid SDF records "
                    "(missing 'M  END' or '$$$$')."
                )


class MBMoleculeFactory:
    @staticmethod
    def create(
        mol: Mol,
        loaded_from: str,
        *,
        mol_index: int = 0,
        add_hydrogens: bool = True,
        set_oxidation_states: bool = True,
        set_props: bool = True,
    ) -> MBMolecule:
        """Create and prepare an MBMolecule with optional preprocessing steps."""

        if add_hydrogens:
            mol = AddHs(mol)  # Adds hydrogens to RDKit object

        if set_props:
            mol.SetProp("_SourceFile", loaded_from)
            if mol_index:
                mol.SetProp("_MolIndex", str(mol_index))

        if set_oxidation_states:
            rdmd.CalcOxidationNumbers(mol)

        return MBMolecule(mol=mol, loaded_from=loaded_from, mol_index=mol_index)
