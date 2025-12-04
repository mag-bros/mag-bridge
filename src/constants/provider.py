from tokenize import group
from typing import TYPE_CHECKING

from src.constants.common_molecules import COMMON_MOLECULES, CommonMolecule
from src.constants.misc import (
    METAL_CATIONS,
    RELEVANT_OXIDATION_ATOMS,
    RELEVANT_RING_ATOMS,
)
from src.constants.pascal_atoms import PASCAL_CONST

if TYPE_CHECKING:
    from src.core.atom import MBAtom
    from src.core.molecule import MBMolecule


class ConstProvider:
    @staticmethod
    def GetPascalValues(atom: "MBAtom") -> dict[str, float]:
        """Looks up relevant Pascal Constant data for given atom."""
        covalent = PASCAL_CONST.get(atom.symbol, {}).get("covalent", {})
        ionic = PASCAL_CONST.get(atom.symbol, {}).get("ionic", {})

        values = {
            "open_chain": covalent.get("open_chain"),
            "ring": covalent.get("ring"),
            "ox_state": covalent.get("ox_state", {}).get(atom.ox_state),
            "charge": ionic.get("charge", {}).get(atom.charge),
        }

        # Remove keys that are not present. Missing key means that no data was found for given atom.
        return {k: v for k, v in values.items() if v is not None}

    @staticmethod
    def GetRelevantRingAtoms() -> list[str]:
        return RELEVANT_RING_ATOMS

    @staticmethod
    def GetRelevantOxidationAtoms() -> list[str]:
        return RELEVANT_OXIDATION_ATOMS

    @staticmethod
    def GetCommonMolDiamagContr(mol: "MBMolecule") -> float | None:
        """Returns diamag contribution of common molecules."""
        for group in COMMON_MOLECULES.values():
            for cm in group:
                if mol.smiles in cm.SMILES:
                    return cm.diamag_sus

        return None
