from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Iterable

from rdkit import Chem

from src.constants.bond_types import (
    AR_NR2,
    CARBON_HALOGEN_BOND,
    DOUBLE_BOND,
    BondType,
    OverlapGroup,
)
from src.core.molecule import MBMolecule


class BondMatchCandidate(BondType):
    """Merges RDKit Substruct Match context with our BondType datasets."""

    __slots__ = ("atoms",)

    def __init__(self, atoms: Iterable[int], **kwargs) -> None:
        super().__init__(**kwargs)
        object.__setattr__(self, "atoms", tuple(int(a) for a in atoms))

    @classmethod
    def from_bt(cls, bt: BondType, atoms: Iterable[int]) -> "BondMatchCandidate":
        return cls(atoms=atoms, **asdict(bt))


@dataclass(frozen=True, slots=True)
class RejectedCandidate:
    candidate: BondMatchCandidate
    reason: str
    conflicting_with: BondMatchCandidate  # 1:1


@dataclass(frozen=True, slots=True)
class InjectedCandidate:
    candidate: BondMatchCandidate
    parent: RejectedCandidate  # 1:1
    rule: str


class SelfOverlapRules:
    """Strategy table mapping each OverlapGroup to its self-overlap classification rule; returns RejectedCandidate or None (accept)."""

    _OverlapRule = Callable[
        [MBMolecule, BondMatchCandidate, set[int], list[BondMatchCandidate]],
        "RejectedCandidate | None",
    ]

    @classmethod
    def check_overlap(
        cls,
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        bmc_atoms: set[int],
        accepted_in_group: list[BondMatchCandidate],
    ) -> RejectedCandidate | None:
        """Check bmc against accepted_in_group using its group rule; returns RejectedCandidate on overlap, None to accept."""
        if bmc.cross_overlap_group is None:
            return None
        group_rules = OVERLAP_RULES_CONFIG.get(bmc.cross_overlap_group)
        if group_rules is None:
            return None
        rule = group_rules.get("self_overlap_rule")
        if rule is None:
            return None
        return rule(mol, bmc, bmc_atoms, accepted_in_group)

    @staticmethod
    def _check_bicyclic(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        bmc_atoms: set[int],
        accepted_in_group: list[BondMatchCandidate],
    ) -> RejectedCandidate | None:
        """Reject bicyclic candidate if it shares 3+ atoms with any already-accepted match of the same group."""
        conflicting = next(
            (acc for acc in accepted_in_group if len(set(acc.atoms) & bmc_atoms) >= 3),
            None,
        )
        if conflicting:
            return RejectedCandidate(candidate=bmc, reason="bicyclic_overlap_3_atoms", conflicting_with=conflicting)
        return None

    @staticmethod
    def _check_double_bonds(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        bmc_atoms: set[int],
        accepted_in_group: list[BondMatchCandidate],
    ) -> RejectedCandidate | None:
        """Reject double-bond candidate if it shares even 1 atom with any already-accepted match of the same group."""
        conflicting = next(
            (acc for acc in accepted_in_group if len(set(acc.atoms) & bmc_atoms) >= 1),
            None,
        )
        if conflicting:
            return RejectedCandidate(candidate=bmc, reason="double_bond_overlap_1_atom", conflicting_with=conflicting)
        return None

    @staticmethod
    def _check_carbonyl(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        bmc_atoms: set[int],
        accepted_in_group: list[BondMatchCandidate],
    ) -> RejectedCandidate | None:
        """Reject carbonyl candidate if it shares 2+ atoms with an accepted match AND both shared atoms are part of the C=O double bond."""
        for acc in accepted_in_group:
            intersection = set(acc.atoms) & bmc_atoms
            if len(intersection) >= 2:
                it = iter(intersection)
                idx1, idx2 = next(it), next(it)
                if all(idx in mol.GetDoubleBondAtomsIndexes() for idx in [idx1, idx2]):
                    return RejectedCandidate(candidate=bmc, reason="carbonyl_double_bond_overlap_2_atoms", conflicting_with=acc)
        return None

    @staticmethod
    def _check_default(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        bmc_atoms: set[int],
        accepted_in_group: list[BondMatchCandidate],
    ) -> RejectedCandidate | None:
        """Reject dihalide (Cl/Br) candidates on 3+ atom ring overlap; all other DEFAULT-group types are unconditionally accepted."""
        if bmc.formula in ["Cl-CR2-CR2-Cl", "R2CCl2", "Br-CR2-CR2-Br"]:
            conflicting = next(
                (acc for acc in accepted_in_group if len(set(acc.atoms) & bmc_atoms) >= 3),
                None,
            )
            if conflicting:
                return RejectedCandidate(candidate=bmc, reason="dihalide_ring_overlap_3_atoms", conflicting_with=conflicting)
        return None


class DerivedInjectRules:
    """Strategy table mapping each OverlapGroup to its inject rule; fires when a rejected candidate can produce a valid alternative match."""

    _Rule = Callable[
        [
            MBMolecule,
            BondMatchCandidate,
            list[BondMatchCandidate],
            dict[str, list[BondMatchCandidate]],
            str,  # trigger: call context for debugger ("on_self_reject" / "on_cross_reject" / "on_accept")
        ],
        bool,
    ]

    @classmethod
    def inject(
        cls,
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        accepted_candidates: list[BondMatchCandidate],
        final_hits_by_formula: dict[str, list[BondMatchCandidate]],
        *,
        trigger: str,
    ) -> None:
        """Dispatch injection rule via trigger context: formula-level for rejections, group-level for on_accept; no-op if no rule is registered."""
        group = bmc.cross_overlap_group if bmc.cross_overlap_group is not None else OverlapGroup.DEFAULT
        group_entry = OVERLAP_RULES_CONFIG.get(group, {})
        if trigger == "on_accept":
            rule = group_entry.get("on_accept")
        else:
            rule = group_entry.get("inject_rules", {}).get(bmc.formula)
        if rule is None:
            return
        rule(mol, bmc, accepted_candidates, final_hits_by_formula, trigger)

    @staticmethod
    def _inject_bicyclic(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        accepted_candidates: list[BondMatchCandidate],
        final_hits_by_formula: dict[str, list[BondMatchCandidate]],
        trigger: str,
    ) -> bool:
        """If cyclohexene is rejected due to bicyclic overlap, add double bond matches instead."""
        if bmc.formula != "cyclohexene":
            return False
        exclude_idx = {i for acc in accepted_candidates for i in acc.atoms}
        double_bond_atoms = mol.GetDoubleBondAtomsIndexes(exclude_idx=exclude_idx)
        if not double_bond_atoms:
            return False
        new_bmc = BondMatchCandidate.from_bt(DOUBLE_BOND, double_bond_atoms)
        accepted_candidates.append(new_bmc)
        final_hits_by_formula.setdefault(DOUBLE_BOND.formula, []).append(new_bmc)
        return True

    @staticmethod
    def _inject_default(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        accepted_candidates: list[BondMatchCandidate],
        final_hits_by_formula: dict[str, list[BondMatchCandidate]],
        trigger: str,
    ) -> bool:
        """If Cl-CR2-CR2-Cl is rejected, inject free C-Cl bonds from atoms not yet occupied by accepted matches."""
        if bmc.formula != "Cl-CR2-CR2-Cl":
            return False
        exclude_idx = {i for acc in accepted_candidates for i in acc.atoms}
        free_nodes = list(set(bmc.atoms) - (exclude_idx & set(bmc.atoms)))
        # # debug variables
        free_nodes_info = {
            idx: {
                "symbol": mol.GetAtomInfoByIdx(idx).symbol,
                "neighbors": [
                    (nbr.GetIdx(), nbr.GetSymbol(), mol.GetBondBetweenAtoms(idx, nbr.GetIdx()).GetBondType())
                    for nbr in mol.GetAtomWithIdx(idx).GetNeighbors()
                ],
            }
            for idx in free_nodes
        }
        # bmc_view = [(idx, mol.GetAtomInfoByIdx(idx).symbol) for idx in bmc.atoms]
        # a1_neighbors = [(nbr.GetIdx(), nbr.GetSymbol()) for nbr in mol.GetAtomWithIdx(a1).GetNeighbors()]
        # a2_neighbors = [(nbr.GetIdx(), nbr.GetSymbol()) for nbr in mol.GetAtomWithIdx(a2).GetNeighbors()]
        # mol_Cl_atoms = {
        #     a.GetIdx(): [(nbr.GetIdx(), nbr.GetSymbol(), mol.GetBondBetweenAtoms(a.GetIdx(), nbr.GetIdx()).GetBondType()) for nbr in a.GetNeighbors()]
        #     for a in mol.GetAtoms()
        #     if a.GetSymbol() == "Cl" and a.GetIdx() not in exclude_idx
        # }

        # Build Injection logic
        free_Cl = [idx for idx in free_nodes if mol.GetAtomInfoByIdx(idx).symbol == "Cl"]
        free_Cl_neighbors = {
            idx: [
                (nbr.GetIdx(), nbr.GetSymbol(), mol.GetBondBetweenAtoms(idx, nbr.GetIdx()).GetBondType())
                for nbr in mol.GetAtomWithIdx(idx).GetNeighbors()
            ]
            for idx in free_Cl
        }
        valid_c_cl_bonds = [
            (next(n[0] for n in neighbors if n[1] == "C" and n[2] == Chem.BondType.SINGLE), cl_idx) for cl_idx, neighbors in free_Cl_neighbors.items()
        ]
        if len(valid_c_cl_bonds) in [1, 2]:  # only one Cl is free here
            for c_idx, cl_idx in valid_c_cl_bonds:
                new_bmc = BondMatchCandidate.from_bt(CARBON_HALOGEN_BOND, [c_idx, cl_idx])
                for _ in range(2):  # Add two times
                    accepted_candidates.append(new_bmc)
                    final_hits_by_formula.setdefault(CARBON_HALOGEN_BOND.formula, []).append(new_bmc)
                return True
        elif len(valid_c_cl_bonds) >= 2:
            raise Exception("more than 2 valid neibhgors")
        return False

    @staticmethod
    def _inject_aromatic(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        accepted_candidates: list[BondMatchCandidate],
        final_hits_by_formula: dict[str, list[BondMatchCandidate]],
        trigger: str,
    ) -> bool:
        """If bmc shares no atom with already-seen candidates, append (aromatic C count − 1) duplicate copies into final_hits_by_formula."""
        if bmc.formula not in {"Ar-OR", "Ar-NR2"}:
            return False
        bmc_atoms = set(bmc.atoms)
        if any(len(set(acc.atoms) & bmc_atoms) >= 1 for acc in accepted_candidates):
            return False
        aromatic_C_atoms = sum(1 for idx in bmc.atoms if mol.GetAtomInfoByIdx(idx).symbol == "C" and mol.GetAtomInfoByIdx(idx).GetIsAromatic())
        extras = [bmc] * (aromatic_C_atoms - 1)
        if not extras:
            return False
        final_hits_by_formula.setdefault(bmc.formula, []).extend(extras)
        return True

    @staticmethod
    def _rule_Ar4_N(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        accepted_candidates: list[BondMatchCandidate],
        final_hits_by_formula: dict[str, list[BondMatchCandidate]],
        conflicts: list[BondMatchCandidate],
    ) -> bool:
        """NOTE: Rule not used. Might be useful in the future.
        Check Check how many Aromatic C Atoms, add this many Ar-NR2 bond types.
        Exception for Ar-NR2 within dummy group of 'Ar-[N+]Ar3'"""

        for conflict in conflicts:
            if conflict.dummy_bond_type:
                new_bmc = BondMatchCandidate.from_bt(AR_NR2, double_bond_atoms)
                for _ in range(4):
                    accepted_candidates.append(new_bmc)
                    final_hits_by_formula.setdefault(DOUBLE_BOND.formula, []).append(new_bmc)
                break  # only first
        return False


OVERLAP_RULES_CONFIG: dict = {
    ## Elements to the left have higher priority!
    OverlapGroup.DEFAULT: {
        "group_prio": int(OverlapGroup.DEFAULT),
        "order": "IRRELEVANT",
        "self_overlap_rule": SelfOverlapRules._check_default,
        "inject_rules": {
            "Cl-CR2-CR2-Cl": DerivedInjectRules._inject_default,
        },
        "on_accept": DerivedInjectRules._inject_aromatic,
    },
    OverlapGroup.DOUBLE_BONDS: {
        "group_prio": int(OverlapGroup.DOUBLE_BONDS),
        "order": ("CH2=CH-CH2-", "Ar-C=C", "C=C-C=C", "C=C"),
        "self_overlap_rule": SelfOverlapRules._check_double_bonds,
        "inject_rules": {},
        "on_accept": None,
    },
    OverlapGroup.BICYCLIC_STRUCTURES: {
        "group_prio": int(OverlapGroup.BICYCLIC_STRUCTURES),
        "order": (
            "cyclopropane",
            "cyclobutane",
            "azacyclopropane",
            "oxacyclopropane",
            "thiacyclopropane",
            "piperazine",
            "cyclohexene",
            "morpholine",
            "dioxane",
            "piperidine",
            "cyclohexane",
            "pyrrolidine",
            "tetrahydrofuran",
            "cyclopentane",
        ),
        "self_overlap_rule": SelfOverlapRules._check_bicyclic,
        "inject_rules": {
            "cyclohexene": DerivedInjectRules._inject_bicyclic,
        },
        "on_accept": None,
    },
    OverlapGroup.CARBONYL_BOND_TYPES: {
        "group_prio": int(OverlapGroup.CARBONYL_BOND_TYPES),
        "order": ("RC(=O)NH2", "Ar-C(=O)NH2", "RCOOR", "Ar-COOR", "RCOOH", "Ar-COOH", "C=O"),
        "self_overlap_rule": SelfOverlapRules._check_carbonyl,
        "inject_rules": {},
        "on_accept": None,
    },
    OverlapGroup.Ar_N_BOND_TYPES: {
        "group_prio": int(OverlapGroup.Ar_N_BOND_TYPES),
        "order": ("Ar-[N+]Ar3", "Ar-NR2"),
        "self_overlap_rule": None,
        "inject_rules": {},
        "on_accept": DerivedInjectRules._inject_aromatic,
    },
}
