from pathlib import Path

from rdkit.Chem import Mol, SDMolSupplier

from src import SDF_DIR
from src.core.molecule import MBMolecule


class SDFLoader:
    """Utility for loading and validating SDF molecule files."""

    @staticmethod
    def load(file: str) -> list[MBMolecule]:
        """Load molecules from an SDF file."""
        sdf_path: Path = SDF_DIR.joinpath(file)
        mols: list[MBMolecule] = [MBMolecule(x) for x in SDMolSupplier(sdf_path)]
        SDFLoader._validate(mols, sdf_path)
        return mols

    @staticmethod
    def _validate(mols: list[Mol], path: str) -> None:
        """Validate loaded molecules for completeness and correctness."""
        assert mols, f"No molecules loaded from '{path}' (empty or malformed)."
        assert all(mol is not None for mol in mols), (
            f"Some molecules in '{path}' failed to parse — check syntax or atom types."
        )


mols = SDFLoader.load("As-benzene-arsenic acid.sdf")
