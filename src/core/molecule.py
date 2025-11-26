from typing import Any

from rdkit.Chem import AddHs, Atom, GetMolFrags, Mol, MolToSmiles, RemoveHs, RWMol
from rdkit.Chem import rdMolDescriptors as rdmd

from src.constants import ConstProvider
from src.core.atom import MBAtom


class MBMolecule:
    """Wrapper around RDKit Atom providing additional computed attributes."""

    def __init__(self, mol: Mol, source_file: str, mol_index: int):
        """Make a molecule object from an RDKit Mol."""
        if not isinstance(mol, Mol):
            raise TypeError(f"Expected rdkit.Chem.rdchem.Mol, got {type(mol)}")
        self._mol: Mol = mol
        self._atoms: list[MBAtom] = [MBAtom(a) for a in self._mol.GetAtoms()]
        self.smiles = MolToSmiles(self._mol)
        self.source_file = source_file
        self.mol_index = mol_index

    def CalcDiamagContr(self, verbose=False) -> float:
        """Calculate the chemical compounds's total diamagnetic contribution.
        Uses Pascal constants for ring, open-chain, oxidation state, and charge terms.
        """
        mol_dia_contr = 0

        if verbose:
            print(f"- {repr(self)}")

        # Iterate over all atoms within this molecule
        for atom in self._atoms:
            if verbose:
                print(atom)

            # Retrieve Pascal constant data for this atom
            pascal_values: dict = ConstProvider.GetPascalValues(atom=atom)

            # Add charge constant for isolated ions (monoatomic species with net charge)
            mol_dia_contr += pascal_values.get("charge", 0)

            # Add ox-state constant for covalently bonded atom when neither ring nor open-chain constants apply
            if atom.has_covalent_bond and all(
                key not in pascal_values for key in ["ring", "open_chain"]
            ):
                mol_dia_contr += pascal_values.get("ox_state", 0)

            # Add ring constant for N and C atoms located within a ring
            if atom.is_ring_relevant and atom.ox_state is None and atom.charge is None:
                mol_dia_contr += pascal_values.get("ring", 0)

            # Add open-chain constant for C or N atoms in chain fragments
            # or when no ring constant is defined for the atom type
            if (
                not atom.is_ring_relevant
                and atom.ox_state is None
                and atom.charge is None
            ):
                mol_dia_contr += pascal_values.get("open_chain", 0)

        if verbose:
            print(f"Diamag: {mol_dia_contr:.4f} cm^3 mol^(-1) - {repr(self)}")

        return mol_dia_contr

    def ToRDKit(self) -> Mol:
        """Return the underlying RDKit Mol object."""
        return self._mol

    def ToSmiles(self) -> str:
        """Returns canonical SMILES notation"""
        return MolToSmiles(RemoveHs(self._mol))

    def __str__(self):
        return f"{self.source_file}:{self.mol_index} ({self.smiles})"

    def __getattr__(self, name) -> Any:
        """Delegate unknown attribute access to the wrapped RDKit Molecule."""
        return getattr(self._mol, name)

    def __repr__(self):
        return f"MBMolecule(source_file='{self.source_file}', mol_index={self.mol_index}, smiles='{self.smiles}')"

    """Centralized constructor for MBMolecule objects.
    Takes raw RDKit Mol inputs and returns fully prepared MBMolecule instances."""


class MBMoleculeFactory:
    @staticmethod
    def create(
        mol: Mol,
        source_file: str,
        mol_index: int,
        *,
        add_hydrogens: bool = True,
        set_oxidation_states: bool = True,
        set_props: bool = True,
    ) -> MBMolecule:
        """Create and prepare an MBMolecule with optional preprocessing steps."""

        if add_hydrogens:
            mol = AddHs(mol)  # Adds hydrogens to RDKit object

        if set_props:
            mol.SetProp("_SourceFile", source_file)
            mol.SetProp("_MolIndex", str(mol_index))

        if set_oxidation_states:
            rdmd.CalcOxidationNumbers(mol)

        return MBMolecule(mol=mol, source_file=source_file, mol_index=mol_index)
