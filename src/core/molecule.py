import math
from typing import Any

from rdkit.Chem import (
    AddHs,
    Atom,
    GetMolFrags,
    Mol,
    MolFromSmarts,
    MolToSmarts,
    MolToSmiles,
    RemoveHs,
    RWMol,
)
from rdkit.Chem import rdMolDescriptors as rdmd

from src.constants.provider import COMMON_DIAMAG_NOT_MATCHED, ConstDB
from src.core.atom import MBAtom


class MBMolecule:
    """Wrapper around RDKit Atom providing additional computed attributes."""

    def __init__(self, mol: Mol, loaded_from: str, mol_index: int):
        """Make a molecule object from an RDKit Mol."""
        self._mol: Mol = mol
        self._atoms: list[MBAtom] = [MBAtom(a) for a in self._mol.GetAtoms()]
        self.loaded_from = loaded_from
        self.mol_index = mol_index
        self.smiles = self.ToSmiles()
        self.smarts = self.ToSmarts()
        self.common_diamag: float = ConstDB.GetCommonMolDiamagContr(smiles=self.smiles)

    def CalcDiamagContr(self, verbose=False) -> float:
        """Calculate the chemical compounds's total diamagnetic contribution.
        Uses Pascal constants for ring, open-chain, oxidation state, and charge terms.
        """

        if verbose:
            print(f"- {repr(self)}")

        if self.common_diamag == COMMON_DIAMAG_NOT_MATCHED:
            contr_all_atoms: float = self.CalcDiamagContrAllAtoms()
            constitutive_corr: float = self.CalcConstitutiveCorrection()
            return contr_all_atoms + constitutive_corr

        return self.common_diamag

    def CalcConstitutiveCorrection(self, verbose=False) -> float:
        # TODO:: finish
        return 0.0

    def CalcDiamagContrAllAtoms(self, verbose=False) -> float:
        """Calculate the chemical compounds's total diamagnetic contribution.
        Uses Pascal constants for ring, open-chain, oxidation state, and charge terms.
        """

        if verbose:
            print(f"- {repr(self)}")

        mol_dia_contr = 0

        # Iterate over all atoms within this molecule
        for atom in self._atoms:
            if verbose:
                print(atom)

            # Add charge constant for isolated ions (monoatomic species with net charge)
            mol_dia_contr += atom.pascal_values.get("charge", 0)

            # Add ox-state constant for covalently bonded atom when neither ring nor open-chain constants apply
            if atom.has_covalent_bond and all(
                key not in atom.pascal_values for key in ["ring", "open_chain"]
            ):
                mol_dia_contr += atom.pascal_values.get("ox_state", 0)

            # Add ring constant for N and C atoms located within a ring
            if atom.is_ring_relevant and atom.ox_state is None and atom.charge is None:
                mol_dia_contr += atom.pascal_values.get("ring", 0)

            # Add open-chain constant for C or N atoms in chain fragments
            # or when no ring constant is defined for the atom type
            if (
                not atom.is_ring_relevant
                and atom.ox_state is None
                and atom.charge is None
            ):
                mol_dia_contr += atom.pascal_values.get("open_chain", 0)

            if verbose:
                print(f"Diamag: {mol_dia_contr:.4f} cm^3 mol^(-1) - {repr(self)}")

        return mol_dia_contr

    def ToRDKit(self) -> Mol:
        """Return the underlying RDKit Mol object."""
        return self._mol

    def ToSmiles(self) -> str:
        """Returns canonical SMILES notation
        NOTE: Our software does not support stereochemical structures."""
        return MolToSmiles(RemoveHs(self._mol), isomericSmiles=False, canonical=True)

    def ToSmarts(self) -> str:
        """Returns canonical SMARTS notation
        NOTE: Our software does not support stereochemical structures."""
        return MolToSmarts(RemoveHs(self._mol), isomericSmiles=True)

    def HasSubstructMatch(self, smarts: str) -> bool:
        """Check if the molecule contains a substructure match for the given SMARTS pattern."""
        return self._mol.HasSubstructMatch(MolFromSmarts(smarts, mergeHs=True))

    def GetSubstructMatches(self, smarts: str) -> tuple[tuple]:
        """Return all substructure matches for the given SMARTS pattern."""
        return self._mol.GetSubstructMatches(MolFromSmarts(smarts, mergeHs=True))

    def GetAtoms(self) -> list[MBAtom]:
        """Return the list of MBAtom objects in this molecule."""
        return self._atoms

    def __str__(self):
        return f"{self.loaded_from}:{self.mol_index} ({self.smiles})"

    def __getattr__(self, name) -> Any:
        """Delegate unknown attribute access to the wrapped RDKit Molecule."""
        return getattr(self._mol, name)

    def __repr__(self):
        return f"MBMolecule(loaded_from='{self.loaded_from}', mol_index={self.mol_index}, smiles='{self.smiles}')"

    """Centralized constructor for MBMolecule objects.
    Takes raw RDKit Mol inputs and returns fully prepared MBMolecule instances."""
