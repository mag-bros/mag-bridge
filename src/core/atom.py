from typing import Any

from rdkit.Chem import Atom

# TODO move to constants
RELEVANT_OX_STATE_SYMBOLS = [
    "As",
    "Hg",
    "Pb",
]

RELEVANT_RING_ATOMS = [
    "N",
    "C",
]


class MBAtom:
    """Wrapper around RDKit Atom providing additional computed attributes."""

    def __init__(self, atom: Atom) -> None:
        """Initialize from an RDKit Atom and precompute derived fields."""
        if not isinstance(atom, Atom):
            raise TypeError(f"Expected rdkit.Chem.rdchem.Atom, got {type(atom)}")
        self._atom: Atom = atom

        self.in_ring: bool = atom.IsInRing()
        self.self_charge: int = atom.GetFormalCharge()
        self.ox_state: int | None = None
        self.neighbor_symbols: list[str] = [n.GetSymbol() for n in atom.GetNeighbors()]

    def HasCovalentBond(self) -> bool:
        return self._atom.GetTotalDegree() > 0

    def GetCharge(self) -> int | None:
        # Get charge taken from SDF file ONLY for atoms without covalent bonds
        return self._atom.GetFormalCharge() if not self.HasCovalentBond() else None

    def GetOxidationState(self, relevant_symbols: set[str]) -> int | None:
        """Return oxidation number if applicable."""
        if (
            self._atom.HasProp("OxidationNumber")
            and self._atom.GetSymbol() in relevant_symbols
            and self._atom.GetTotalDegree() > 0
        ):
            return self._atom.GetIntProp("OxidationNumber")
        return None

    def GetNeighborSymbols(self, as_string: bool = False) -> str | list[str]:
        """Return neighbor atom symbols as a list or comma-separated string."""
        symbols = [n.GetSymbol() for n in self._atom.GetNeighbors()]
        return ", ".join(symbols) if as_string else symbols

    """Expose key RDKit Atom methods for IDE autocompletion and navigation."""

    def GetSymbol(self) -> str:
        return self._atom.GetSymbol()

    def GetIdx(self) -> int:
        return self._atom.GetIdx()

    def GetFormalCharge(self) -> int:
        return self._atom.GetFormalCharge()

    def GetTotalDegree(self) -> int:
        return self._atom.GetTotalDegree()

    def IsInRing(self) -> bool:
        return self._atom.IsInRing()

    def HasProp(self, key: str):
        return self._atom.HasProp(key=key)

    def GetProp(self, key: str):
        return self._atom.GetProp(key=key)

    def __getattr__(self, name) -> Any:
        """Delegate unknown attribute access to the wrapped RDKit Atom."""
        return getattr(self._atom, name)

    def __str__(self) -> str:
        """Return a human-readable summary of atom properties."""
        return (
            f"Atom: {self.GetSymbol()},\n"
            f"  IsInRing: {self.IsInRing()},\n"
            f"  in_ring: {self.in_ring},\n"
            f"  GetNoBondedAtoms: {self.GetTotalDegree()},\n"
            f"  FormalCharge: {self.GetFormalCharge()},\n"
            f"  self_charge: {self.GetCharge()},\n"
            f"  ox_state: {self.GetOxidationState(relevant_symbols=RELEVANT_OX_STATE_SYMBOLS)},\n"
            f"  id: {self.GetIdx()},\n"
            f"  neighbors: {self.GetNeighborSymbols()}\n"
        )

    def __repr__(self) -> str:
        """Return a concise developer-oriented identifier string."""
        return f"<MyAtom {self.GetSymbol()} idx={self.GetIdx()}>"
