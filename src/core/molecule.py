from typing import Any

from rdkit.Chem import AddHs, Mol
from rdkit.Chem import rdMolDescriptors as rdmd

from src.core.atom import MBAtom


class MBMolecule:
    """Wrapper around RDKit Atom providing additional computed attributes."""

    def __init__(self, mol: Mol):
        """Make a molecule object from an RDKit Mol."""
        assert isinstance(mol, Mol), f"Expected rdkit.Chem.rdchem.Mol, got {type(mol)}"
        self._mol: Mol = self._preprocess(mol)  # Actual RDKit object
        self._atoms: list[MBAtom] = [MBAtom(a) for a in self._mol.GetAtoms()]

    def GetAtoms(self) -> list[MBAtom]:
        """Return list of wrapped atom objects."""
        return self._atoms

    def _preprocess(self, mol: Mol) -> None:
        """Adds oxidation numbers from SDF file. Also adds hydrogens to RDKit object """
        mol = AddHs(mol)
        rdmd.CalcOxidationNumbers(mol)
        return mol

    def __getattr__(self, name) -> Any:
        """Pass any unknown function call to the RDKit Mol object."""
        return getattr(self._mol, name)
