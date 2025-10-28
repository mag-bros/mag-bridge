from typing import Any

from rdkit.Chem import AddHs, Mol
from rdkit.Chem import rdMolDescriptors as rdmd

from src.constants import ConstProvider
from src.core.atom import MBAtom
from PIL import Image
from rdkit.Chem import Draw

class MBMolecule:
    """Wrapper around RDKit Atom providing additional computed attributes."""

    def __init__(self, mol: Mol):
        """Make a molecule object from an RDKit Mol."""
        assert isinstance(mol, Mol), f"Expected rdkit.Chem.rdchem.Mol, got {type(mol)}"
        self._mol: Mol = self._preprocess(mol)  # Actual RDKit object
        self._atoms: list[MBAtom] = [MBAtom(a) for a in self._mol.GetAtoms()]

    def CalcDiamagContr(self, verbose=False) -> float:
        """Calculate the molecule's total diamagnetic contribution.  
        Uses Pascal constants for ring, open-chain, oxidation state, and charge terms."""
        contr = 0
        
        # Iterate over all atoms within this molecule
        for atom in self._atoms:
            if verbose:
                print(atom)
            
            # Retrieve Pascal constant data for this atom
            pascal_values: dict = ConstProvider.GetPascalValues(atom=atom)

            # Add ring constant for N and C atoms located within a ring
            if atom.is_ring_relevant:
                contr += pascal_values.get('ring', 0)
            
            # Add open-chain constant for C or N atoms in chain fragments 
            # or when no ring constant is defined for the atom type
            elif 'ring' not in pascal_values:
                contr += pascal_values.get('open_chain', 0)

            # Add oxidation-state constant when neither ring nor open-chain constants apply
            if (all(key not in pascal_values for key in ["ring", "open_chain"])):
                contr += pascal_values.get('ox_state', 0)

            # Add charge constant for isolated ions (monoatomic species with net charge)
            contr += pascal_values.get('charge', 0)
        
        if verbose:
            print(f"Diamagnetic contribution: {contr:.4f} cm^3 mol^(-1)")
        
        return contr

    def GetImage(self, size=(300, 300)) -> Image:
        """Display 2D depiction of the molecule."""
        from rdkit.Chem.Draw import MolToImage
        from rdkit.Chem.rdDepictor import Compute2DCoords
        
        mol2d = Mol(self._mol)
        Compute2DCoords(mol2d)
        return MolToImage(mol2d, size=size)

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
