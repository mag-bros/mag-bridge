from typing import Any

from rdkit.Chem import Atom

# TODO: Not sure if we should move this to constants?
RELEVANT_OX_STATE_CONST = ["As", "Hg", "Pb"]
RELEVANT_RING_ATOMS = ["N", "C"]


class MBAtom:
    """Wrapper around RDKit Atom providing additional computed attributes."""

    def __init__(self, atom: Atom) -> None:
        """Initialize from an RDKit Atom and precompute derived fields."""
        if not isinstance(atom, Atom):
            raise TypeError(f"Expected rdkit.Chem.rdchem.Atom, got {type(atom)}")
        self._atom: Atom = atom  # Actual RDKit object

        # TODO:: Set class fields for other functions
        #       Goal --> easy API user access, e.g. from notebook
        self.symbol: str = self.GetSymbol()  # example
        self.in_ring: bool = self.IsInRing(relevant_ring_atoms=RELEVANT_RING_ATOMS)
        self.ox_state: int | None = ...
        self.charge: int | None = ...
        self.has_covalent_bond: bool = ...

    def IsInRing(self, relevant_ring_atoms: list[str] = None) -> bool | None:
        """Return True if atom is part of a ring."""
        # TODO:: This function is not finished
        # 1. if symbol is NOT ring relevant, then return None object
        # 2. in all other cases, let RDKit decide if it's in ring.
        return self._atom.IsInRing()  # Default to RDKit

    def GetOxidationState(self, relevant_symbols: set[str]) -> int | None:
        """Return oxidation number if applicable."""
        if (
            self._atom.HasProp("OxidationNumber")
            and self._atom.GetSymbol() in relevant_symbols
            and self._atom.GetTotalDegree() > 0
        ):
            return self._atom.GetIntProp("OxidationNumber")
        return None

    def HasCovalentBond(self) -> bool:
        """Return True if atom has at least one covalent bond."""
        return self._atom.GetTotalDegree() > 0

    def GetCharge(self) -> int | None:
        """Return formal charge only for atoms without covalent bonds."""
        if not self.HasCovalentBond:
            self._atom.GetFormalCharge()
        else:
            return None

    def GetNeighborSymbols(self, as_string: bool = False) -> str | list[str]:
        """Return neighbor atom symbols as a list or comma-separated string."""
        symbols = [n.GetSymbol() for n in self._atom.GetNeighbors()]
        return ", ".join(symbols) if as_string else symbols

    def __str__(self) -> str:
        """Return a one-line, column-aligned summary of atom properties."""
        # TODO:: Use constructor fields for all variables instead.
        # TODO:: Filter actually relevant fields - remove these that we don't want to track
        #   Expected: self.symbol
        #   Wrong:    self.GetSymbol()
        return (
            f"Symbol: {self.GetSymbol():<3} | "
            f"Ring: {str(self.IsInRing()):<5} | "
            f"Deg: {self.GetTotalDegree():<2} | "
            f"FChg: {self.GetFormalCharge():<2} | "
            f"SChg: {str(self.GetCharge()):<5} | "
            f"Ox: {str(self.ox_state):<4} | "
            f"id: {self.GetIdx():<2} | "
            f"neighbors: {self.GetNeighborSymbols(as_string=True)}"
        )

    def __getattr__(self, name) -> Any:
        """Delegate unknown attribute access to the wrapped RDKit Atom."""
        return getattr(self._atom, name)

    def __repr__(self) -> str:
        """Return a concise developer-oriented identifier string."""
        return f"<MBAtom {self.GetSymbol()} idx={self.GetIdx()}>"

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
        """Return total number of bonds including implicit hydrogens."""
        return self._atom.GetTotalDegree()

    def HasProp(self, key: str) -> bool:
        """Return True if the atom has a property with the given key."""
        return self._atom.HasProp(key=key)

    def GetProp(self, key: str) -> Any:
        """Return property value by key."""
        return self._atom.GetProp(key=key)
