import os
from pathlib import Path

from rdkit.Chem import SDMolSupplier

from src import SDF_DIR
from src.core.molecule import MBMolecule, MBMoleculeFactory
from src.utils.exceptions import SDFEmptyFileError, SDFFileNotFoundError, SDFLoaderError, SDFMalformedRecordError


class SDFLoader:
    """Utility for loading and validating SDF molecule files."""

    @staticmethod
    def load(files: str | list[str]) -> list[MBMolecule]:
        """Load one or multiple SDF files and return a flat list of MBMolecule objects."""
        if isinstance(files, str):
            files = [files]

        all_mols: list[MBMolecule] = []

        for file in files:
            sdf_path: Path = SDF_DIR.joinpath(file)

            if not sdf_path.exists():
                raise SDFFileNotFoundError(f"SDF file not found: {sdf_path}")

            if sdf_path.suffix.lower() != ".sdf":
                raise SDFLoaderError(f"Unsupported file type: {sdf_path.suffix} (expected .sdf)")

            supplier = SDMolSupplier(str(sdf_path), sanitize=True, removeHs=False)
            raw_mols = list(supplier)

            # Case 1: completely empty file
            if not raw_mols:
                raise SDFEmptyFileError(f"No molecules found in file: {sdf_path}")

            # Case 2: partially malformed SDF — RDKit returns some None entries
            failed = sum(1 for mol in raw_mols if mol is None)
            if failed:
                raise SDFMalformedRecordError(
                    f"{failed} molecule(s) failed to parse in file '{sdf_path}'. "
                    "Check the SDF syntax or atom typing."
                )

            mols = [
                MBMoleculeFactory.create(mol, file, i)
                for i, mol in enumerate(raw_mols)
                if mol is not None
            ]

            all_mols.extend(mols)

        if not all_mols:
            raise SDFEmptyFileError("No valid molecules loaded from any file.")

        return all_mols

    @staticmethod
    def PreCheckFileData(path: Path) -> None:
        """Perform pre-validation on the SDF file before parsing."""

        # --- 1️⃣ Path existence ---
        if not path.exists():
            raise SDFFileNotFoundError(f"File not found: {path}")

        # --- 2️⃣ File extension check ---
        if path.suffix.lower() != ".sdf":
            raise SDFLoaderError(f"Invalid file extension '{path.suffix}'. Expected .sdf")

        # --- 3️⃣ File readability ---
        if not path.is_file() or not os.access(path, os.R_OK):
            raise SDFLoaderError(f"File is not readable: {path}")

        # --- 4️⃣ Empty or near-empty file ---
        size = path.stat().st_size
        if size == 0:
            raise SDFEmptyFileError(f"File '{path}' is empty.")

        # --- 5️⃣ Optional: check if content looks like text, not binary ---
        with open(path, "rb") as f:
            header = f.read(256)
            if b"\x00" in header:
                raise SDFLoaderError(f"File '{path}' appears to be binary, not SDF text.")

        # --- 6️⃣ Optional: ensure at least minimal SDF structure marker ---
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(2048)
            if not ("M  END" in content or "$$$$" in content):
                raise SDFLoaderError(
                    f"File '{path}' does not appear to contain valid SDF records (missing 'M  END' or '$$$$')."
                )
