from typing import Any

from rdkit.Chem import AddHs, Mol
from rdkit.Chem import rdMolDescriptors as rdmd

from src.core.atom import MBAtom


class MBMolecule:
    def __init__(self, mol: Mol):
        """Initialize from an RDKit Atom and precompute derived fields."""
        if not isinstance(mol, Mol):
            raise TypeError(f"Expected rdkit.Chem.rdchem.Atom, got {type(mol)}")
        self._mol: Mol = mol
        self._atoms: list[MBAtom] = [MBAtom(a) for a in mol.GetAtoms()]
        self.atom_charge = ...  # TODO::

    def preprocess(self) -> None:
        rdmd.CalcOxidationNumbers(self._mol)
        self._mol = AddHs(self._mol)

    def GetAtoms(self) -> list[MBAtom]:
        return self._atoms

    def __getattr__(self, name) -> Any:
        """Delegate unknown attribute access to the wrapped RDKit Atom."""
        return getattr(self._atom, name)
