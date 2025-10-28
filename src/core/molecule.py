from typing import Any

from rdkit.Chem import AddHs, Mol
from rdkit.Chem import rdMolDescriptors as rdmd

from src.core.atom import MBAtom


class MBMolecule:
    """Wrapper around RDKit Atom providing additional computed attributes."""

    def __init__(self, mol: Mol):
        """Make a molecule object from an RDKit Mol."""
        if not isinstance(mol, Mol):
            raise TypeError(f"Expected rdkit.Chem.rdchem.Mol, got {type(mol)}")
        self._mol: Mol = mol  # Actual RDKit object
        self._atoms: list[MBAtom] = [MBAtom(a) for a in mol.GetAtoms()]

    def preprocess(self) -> None:
        """Modify this molecule in place (adds oxidation numbers and hydrogens)."""
        self._mol = AddHs(self._mol)
        rdmd.CalcOxidationNumbers(self._mol)
        self._atoms: list[MBAtom] = [MBAtom(a) for a in self._mol.GetAtoms()]

    def GetAtoms(self) -> list[MBAtom]:
        """Return list of wrapped atom objects."""
        return self._atoms

    def __getattr__(self, name) -> Any:
        """Pass any unknown function call to the RDKit Mol object."""
        return getattr(self._mol, name)
