from typing import Any

from rdkit.Chem import Atom

from src.constants import ConstProvider


class MBAtom:
    """Wrapper around RDKit Atom providing additional computed attributes."""

    def __init__(self, atom: Atom) -> None:
        """Initialize from an RDKit Atom and precompute derived fields."""
        if not isinstance(atom, Atom):
            raise TypeError(f"Expected rdkit.Chem.rdchem.Atom, got {type(atom)}")
        self._atom: Atom = atom  # Actual RDKit object
        
        # Pre-compute fields used for diamag calcs, for easy access
        self.symbol: str = self.GetSymbol()
        self.is_ring_relevant: bool = self.IsRingRelevant()
        self.ox_state: int | None = self.GetOxidationState()
        self.has_covalent_bond: bool = self.HasCovalentBond()
        self.total_degree: int = self.GetTotalDegree()
        self.charge: int | None = self.GetCharge()

    def IsRingRelevant(self) -> bool:
        """Return True if atom is part of a ring."""
        if self._atom.GetSymbol() in ConstProvider.GetRelevantRingAtoms():
            return self._atom.IsInRing()
        else:
            return False

    def GetOxidationState(self) -> int | None:
        """Return oxidation number only for relevant atoms"""
        if (
            self._atom.HasProp("OxidationNumber")
            and self._atom.GetSymbol() in ConstProvider.GetRelevantOxidationAtoms()
            and self._atom.GetTotalDegree() > 0
        ):
            return self._atom.GetIntProp("OxidationNumber")
        else:
            return None

    def HasCovalentBond(self) -> bool:
        """Return True if atom has at least one covalent bond."""
        return self._atom.GetTotalDegree() > 0

    def GetCharge(self) -> int | None:
        """Return formal charge only for atoms without covalent bonds.
            @note1: This only refers to single-atom ions (like Na+) but NOT multiatomic ions ( like NO3(-) )
            @note2: The formal charge is taken directly from the SDF file. It is NOT calculated implicitly by RDKit.""" 
        if not self.HasCovalentBond():
            return self._atom.GetFormalCharge()
        else:
            return None

    def GetNeighborSymbols(self, as_string: bool = False) -> str | list[str]:
        """Return neighbor atom symbols as a list or comma-separated string."""
        symbols = [n.GetSymbol() for n in self._atom.GetNeighbors()]
        return ", ".join(symbols) if as_string else symbols

    def __str__(self) -> str:
        """Return a one-line, column-aligned summary of atom properties."""
        return (
            f"Symbol: {self.symbol:<3} | "
            f"IsRingRelevant: {str(self.is_ring_relevant):<5} | "
            f"TotalDegree: {self.total_degree:<2} | "
            f"Charge: {str(self.charge):<5} | "
            f"OxState: {str(self.ox_state):<4} | "
            f"Id: {self.GetIdx():<2} | "
            f"Neighbors: {self.GetNeighborSymbols(as_string=True)}"  # It may be omitted if we will be able to generate image of molecular structure with indexed atoms.
        )

    def __getattr__(self, name) -> Any:
        """Delegate unknown attribute access to the wrapped RDKit Atom."""
        return getattr(self._atom, name)

    def __repr__(self) -> str:
        """Return a concise developer-oriented identifier string."""
        return f"<MBAtom {self.symbol} idx={self.GetIdx()}>"

    # Below section is used for linting purposes only
    # Expose key RDKit Atom methods for IDE autocompletion and navigation.
    def GetSymbol(self) -> str:
        """Return the atom's chemical symbol."""
        return self._atom.GetSymbol()

    def GetIdx(self) -> int:
        """Return the atom index within the molecule."""
        return self._atom.GetIdx()

    def GetFormalCharge(self) -> int:
        """Return the atom's formal charge."""
        return self._atom.GetFormalCharge()

    def GetTotalDegree(self) -> int:
        """Return total number of bonds formed by the given atom, including implicit hydrogens."""
        return self._atom.GetTotalDegree()

    def HasProp(self, key: str) -> bool:
        """Return True if the atom has a property with the given key."""
        return self._atom.HasProp(key=key)

    def GetProp(self, key: str) -> Any:
        """Return property value by key."""
        return self._atom.GetProp(key=key)
