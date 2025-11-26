import os
from pathlib import Path

from rdkit.Chem import SDMolSupplier

from core.compound import MBCompound
from src import SDF_DIR
from src.core.molecule import MBMolecule, MBMoleculeFactory
from src.utils.exceptions import (
    SDFEmptyFileError,
    SDFFileNotFoundError,
    SDFLoaderError,
    SDFMalformedRecordError,
)


class SDFLoader:
    """Utility for loading and validating SDF files."""

    @staticmethod
    def Load(source_file: str, sdf_sub_dir=".") -> MBCompound:
        """Loads an SDF file and return a MBCompound object containing a list of molecules"""

        sdf_path = SDF_DIR.joinpath(sdf_sub_dir).joinpath(source_file)
        SDFLoader.CheckFile(sdf_path)

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
            MBMoleculeFactory.create(mol, source_file, i)
            for i, mol in enumerate(raw_mols)
            if mol
        ]

        if not loaded_mols:
            raise SDFEmptyFileError("No valid molecules loaded from any file.")

        compound = MBCompound(mols=loaded_mols, source_file=source_file)

        return compound

    @staticmethod
    def CheckFile(path: Path) -> None:
        """Perform comprehensive validation on the SDF file before parsing."""
        if not path.exists():
            raise SDFFileNotFoundError(f"File not found: {path}")

        if path.suffix.lower() != ".sdf":
            raise SDFLoaderError(
                f"Invalid file extension '{path.suffix}'. Expected .sdf"
            )

        if not path.is_file() or not os.access(path, os.R_OK):
            raise SDFLoaderError(f"File is not readable: {path}")

        if path.stat().st_size == 0:
            raise SDFEmptyFileError(f"File '{path}' is empty.")

        with open(path, "rb") as f:
            if b"\x00" in f.read(256):
                raise SDFLoaderError(
                    f"File '{path}' appears to be binary, not SDF text."
                )

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if not ("M  END" in content or "$$$$" in content):
                raise SDFLoaderError(
                    f"File '{path}' does not appear to contain valid SDF records "
                    "(missing 'M  END' or '$$$$')."
                )
