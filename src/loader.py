import os
from pathlib import Path
from rdkit.Chem import SDMolSupplier

from src import SDF_DIR
from src.core.molecule import MBMolecule, MBMoleculeFactory
from src.utils.exceptions import (
    SDFEmptyFileError,
    SDFFileNotFoundError,
    SDFLoaderError,
    SDFMalformedRecordError,
)


class SDFLoader:
    """Utility for loading and validating SDF molecule files."""

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

        # with open(path, "r", encoding="utf-8", errors="ignore") as f:
        #     content = f.read(2048)
        #     if not ("M  END" in content or "$$$$" in content):
        #         raise SDFLoaderError(
        #             f"File '{path}' does not appear to contain valid SDF records "
        #             "(missing 'M  END' or '$$$$')."
        #         )

    @staticmethod
    def Load(files: str | list[str]) -> list[MBMolecule]:
        """Load one or multiple SDF files and return a flat list of MBMolecule objects."""
        if isinstance(files, str):
            files = [files]

        all_mols: list[MBMolecule] = []

        for file in files:
            sdf_path = SDF_DIR.joinpath(file)
            SDFLoader.CheckFile(sdf_path)

            supplier = SDMolSupplier(str(sdf_path), sanitize=True, removeHs=False)
            raw_mols = list(supplier)

            if not raw_mols:
                raise SDFEmptyFileError(f"No molecules found in file: {sdf_path}")

            failed = sum(1 for mol in raw_mols if mol is None)
            if failed:
                raise SDFMalformedRecordError(
                    f"{failed} molecule(s) failed to parse in file '{sdf_path}'. "
                    "Check the SDF syntax or atom typing."
                )

            mols = [
                MBMoleculeFactory.create(mol, file, i)
                for i, mol in enumerate(raw_mols)
                if mol
            ]
            all_mols.extend(mols)

        if not all_mols:
            raise SDFEmptyFileError("No valid molecules loaded from any file.")

        return all_mols
