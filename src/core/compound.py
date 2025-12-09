from typing import TYPE_CHECKING, Literal, overload

from rdkit.Chem import Mol

from core.molecule import MBMolecule


class MBCompound:
    """MBCompound is the representation of all molecules defined by exactly one SDF file."""

    def __init__(self, mols: list[MBMolecule], source_file: str):
        self._mols = mols
        self.source_file = source_file

    def CalcDiamagContr(self, verbose=False):
        """Calculates diamagnetic contribution of a compound."""
        diamag_contr = 0
        for mol in self._mols:
            diamag_contr += mol.CalcDiamagContr(verbose=verbose)

        return diamag_contr

    # --- Overloads visible to callers ---------------------------------
    @overload
    def GetMols(self, to_rdkit: Literal[True] = True) -> list[Mol]: ...
    @overload
    def GetMols(self, to_rdkit: Literal[False]) -> list[MBMolecule]: ...
    def GetMols(self, to_rdkit: bool = True) -> list[MBMolecule] | list[Mol]:
        """Return a list of molecules in this compound. Optional RDKit conversion."""
        if to_rdkit:
            return [mol.ToRDKit() for mol in self._mols]  # list[Mol]

        return self._mols  # list[MBMolecule]
