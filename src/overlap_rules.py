from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Iterable

from rdkit import Chem

from src.constants.bond_types import (
    AR_NR2,
    CARBON_BROMINE_BOND,
    CARBON_CHLORINE_BOND,
    CARBON_TRIPLE_BOND,
    CARBONYL_BOND,
    DOUBLE_BOND,
    BondType,
    OverlapGroup,
)
from src.core.cross_overlap_comparator import CrossOverlapComparator
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
        if bmc.overlap_group is None:
            return None
        group_rules = OVERLAP_RULES_CONFIG.get(bmc.overlap_group)
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
            common_atoms = list(bmc_atoms & set(conflicting.atoms))
            if len(common_atoms) == 1:
                has_double_bond_nbrs = True
                conflict_node = common_atoms[0]
                for nbr in mol.GetAtomWithIdx(conflict_node).GetNeighbors():
                    bond = mol.GetBondBetweenAtoms(conflict_node, nbr.GetIdx())
                    if bond.GetBondType() != Chem.BondType.DOUBLE:
                        has_double_bond_nbrs = False
                if has_double_bond_nbrs:
                    return None

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
        if bmc.formula in ["Cl-CR2-CR2-Cl", "Br-CR2-CR2-Br"]:
            conflicting = next(
                (acc for acc in accepted_in_group if len(set(acc.atoms) & bmc_atoms) >= 4),
                None,
            )
            if conflicting:
                return RejectedCandidate(candidate=bmc, reason="dihalide_ring_overlap_4_atoms", conflicting_with=conflicting)
        if bmc.formula in ["RC#C-C(=O)R"]:
            conflicting = next(
                (acc for acc in accepted_in_group if len(set(acc.atoms) & bmc_atoms) >= 3),
                None,
            )
            if conflicting:
                return RejectedCandidate(candidate=bmc, reason="alkynyl_ketone_overlap_3_atoms", conflicting_with=conflicting)

        return None


class OverlapInjector:
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
    def inject_on_reject(
        cls,
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        occupied: list[BondMatchCandidate],
        accepted: dict[str, list[BondMatchCandidate]],
        *,
        trigger: str,
    ) -> None:
        """Dispatch injection rule via trigger context: formula-level for rejections, group-level for on_accept; no-op if no rule is registered."""
        group = bmc.overlap_group if bmc.overlap_group is not None else OverlapGroup.DEFAULT
        group_entry = OVERLAP_RULES_CONFIG.get(group, {})
        if trigger == "on_accept":
            rule = group_entry.get("on_accept")
        else:
            rule = group_entry.get("inject_rules", {}).get(bmc.formula)
        if rule is None:
            return
        rule(mol, bmc, occupied, accepted, trigger)

    @staticmethod
    def _inject_bicyclic(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        occupied: list[BondMatchCandidate],
        accepted: dict[str, list[BondMatchCandidate]],
        trigger: str,
    ) -> bool:
        """If cyclohexene is rejected due to bicyclic overlap, add double bond matches instead."""
        if bmc.formula != "cyclohexene":
            return False
        exclude_idx = {i for acc in occupied for i in acc.atoms}
        double_bond_atoms = mol.GetDoubleBondAtomsIndexes(exclude_idx=exclude_idx)
        if not double_bond_atoms:
            return False
        new_bmc = BondMatchCandidate.from_bt(DOUBLE_BOND, double_bond_atoms)
        occupied.append(new_bmc)
        accepted.setdefault(DOUBLE_BOND.formula, []).append(new_bmc)
        return True

    # Maps each formula → list of (seek_symbol, injection_bond, seek_bond_kind) entries.
    # Multiple entries per formula are supported — each injects independently.
    # TODO move to global config
    # TODO:: get bond type from INJECT_MAP instead
    INJECT_MAP: dict[str, list[tuple[str, BondType, Chem.BondType]]] = {
        "Cl-CR2-CR2-Cl": [("Cl", CARBON_CHLORINE_BOND, Chem.BondType.SINGLE)],
        "Br-CR2-CR2-Br": [("Br", CARBON_BROMINE_BOND, Chem.BondType.SINGLE)],
        "RC#C-C(=O)R": [
            ("O", CARBONYL_BOND, Chem.BondType.DOUBLE),
            ("C", CARBON_TRIPLE_BOND, Chem.BondType.TRIPLE),
        ],
    }

    @staticmethod
    def _inject_default(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        occupied: list[BondMatchCandidate],
        accepted: dict[str, list[BondMatchCandidate]],
        trigger: str,
    ) -> bool:
        # TODO refactor this code to be more readable (backward compatibility is crucial)
        """When a dihalide (e.g. Cl-CR2-CR2-Cl) is rejected, inject one C-X BondType per halogen pair in the fragment.

        Skips halogen atoms already claimed by an accepted dihalide or an already-injected C-X bond.
        Atom map of the rejected fragment (for debugging):
            {idx: mol.GetAtomInfoByIdx(idx).symbol for idx in bmc.atoms}
        """
        entries = OverlapInjector.INJECT_MAP.get(bmc.formula)
        if entries is None:
            return False

        # atom_index → symbol map for the fragment
        atom_map: dict[int, str] = {idx: mol.GetAtomInfoByIdx(idx).symbol for idx in bmc.atoms}

        injected = False
        for seek_symbol, injection_bond, seek_bond_kind in entries:
            # For each target atom in the fragment, find its C neighbor via the expected bond kind
            c_x_pairs: list[tuple[int, int]] = []
            for x_idx, sym in atom_map.items():
                if sym != seek_symbol:
                    continue
                # TODO:: get bond type from INJECT_MAP instead
                for nbr in mol.GetAtomWithIdx(x_idx).GetNeighbors():
                    if nbr.GetSymbol() != "C":
                        continue
                    bond = mol.GetBondBetweenAtoms(x_idx, nbr.GetIdx())
                    if bond.GetBondType() == seek_bond_kind and nbr.GetIdx() in atom_map:
                        c_x_pairs.append((nbr.GetIdx(), x_idx))
                        break  # each target atom has exactly one matching C neighbor in the fragment

            if not c_x_pairs:
                continue

            # Target atoms already accounted for — by an injected C-X bond or by an accepted parent
            already_covered: set[int] = set()
            for acc in occupied:
                if acc.formula == injection_bond.formula:
                    for idx in acc.atoms:
                        if mol.GetAtomInfoByIdx(idx).symbol == seek_symbol:
                            already_covered.add(idx)
            for acc_list in accepted.values():
                for acc in acc_list:
                    if acc.formula == bmc.formula:
                        for idx in acc.atoms:
                            if mol.GetAtomInfoByIdx(idx).symbol == seek_symbol:
                                already_covered.add(idx)

            for c_idx, x_idx in c_x_pairs:
                if x_idx in already_covered:
                    continue
                new_bmc = BondMatchCandidate.from_bt(injection_bond, [c_idx, x_idx])
                occupied.append(new_bmc)
                accepted.setdefault(injection_bond.formula, []).append(new_bmc)
                already_covered.add(x_idx)
                injected = True

        return injected

    @staticmethod
    def _inject_aromatic(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        occupied: list[BondMatchCandidate],
        accepted: dict[str, list[BondMatchCandidate]],
        trigger: str,
    ) -> bool:
        """If bmc shares no atom with already-seen candidates, append (aromatic C count - 1) duplicate copies into accepted."""
        if bmc.formula not in {"Ar-OR", "Ar-NR2"}:
            return False
        bmc_atoms = set(bmc.atoms)
        if any(len(set(acc.atoms) & bmc_atoms) >= 1 for acc in occupied):
            return False
        aromatic_C_atoms = sum(1 for idx in bmc.atoms if mol.GetAtomInfoByIdx(idx).symbol == "C" and mol.GetAtomInfoByIdx(idx).GetIsAromatic())
        extras = [bmc] * (aromatic_C_atoms - 1)
        if not extras:
            return False
        accepted.setdefault(bmc.formula, []).extend(extras)
        return True

    @staticmethod
    def _rule_Ar4_N(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        occupied: list[BondMatchCandidate],
        accepted: dict[str, list[BondMatchCandidate]],
        conflicts: list[BondMatchCandidate],
    ) -> bool:
        """NOTE: Rule not used. Might be useful in the future.
        Check Check how many Aromatic C Atoms, add this many Ar-NR2 bond types.
        Exception for Ar-NR2 within dummy group of 'Ar-[N+]Ar3'"""

        for conflict in conflicts:
            if conflict.dummy_bond_type:
                new_bmc = BondMatchCandidate.from_bt(AR_NR2, double_bond_atoms)
                for _ in range(4):
                    occupied.append(new_bmc)
                    accepted.setdefault(DOUBLE_BOND.formula, []).append(new_bmc)
                break  # only first
        return False


class CrossOverlapRules:
    """Strategy table mapping each OverlapGroup to its cross-overlap classification rule;
    returns True to approve, False to reject."""

    @classmethod
    def check_overlap(
        cls,
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        bmc_atoms: set[int],
        occupied: list[BondMatchCandidate],
    ) -> bool:
        """Dispatch to the group's cross-overlap rule; returns True (approve) if no rule registered."""
        group = bmc.overlap_group
        if group is None:
            return True
        rule = OVERLAP_RULES_CONFIG.get(group, {}).get("cross_overlap_rule")
        if rule is None:
            return True
        return rule(mol, bmc, bmc_atoms, occupied)

    @staticmethod
    def _check_bicyclic(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        bmc_atoms: set[int],
        occupied: list[BondMatchCandidate],
    ) -> bool:
        """Reject if bmc shares 3+ atoms with any accepted candidate."""
        bicyclic_approved = True
        for acc in occupied:
            shared_atoms = bmc_atoms & set(acc.atoms)
            if len(shared_atoms) >= 3:
                bicyclic_approved = False
        return bicyclic_approved

    @staticmethod
    def _check_double_bonds(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        bmc_atoms: set[int],
        occupied: list[BondMatchCandidate],
    ) -> bool:
        """Reject if bmc shares 1+ atom with any accepted double-bond candidate."""
        double_bond_approved = True
        for acc in occupied:
            is_double_bond_group = acc.overlap_group == OverlapGroup.DOUBLE_BONDS
            shared_atoms = bmc_atoms & set(acc.atoms)
            if is_double_bond_group and len(shared_atoms) >= 1:
                common_atoms = list(shared_atoms)
                if len(common_atoms) == 1:
                    has_double_bond_nbrs = True
                    conflict_node = common_atoms[0]
                    for nbr in mol.GetAtomWithIdx(conflict_node).GetNeighbors():
                        bond = mol.GetBondBetweenAtoms(conflict_node, nbr.GetIdx())
                        if bond.GetBondType() != Chem.BondType.DOUBLE:
                            has_double_bond_nbrs = False
                    if has_double_bond_nbrs:
                        return True

                double_bond_approved = False
        return double_bond_approved

    @staticmethod
    def _check_carbonyl(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        bmc_atoms: set[int],
        occupied: list[BondMatchCandidate],
    ) -> bool:
        """Approve unless a higher-priority accepted carbonyl overlaps by 2+ atoms.

        Last-wins behavior: if multiple accepted carbonyls conflict, the final
        iteration determines the outcome. Currently safe because priority-sorted
        processing guarantees all accepted carbonyls are higher-priority than bmc,
        so is_higher_priority(bmc, acc) is consistently False for all matches.

        Potential fix if last-wins becomes unsafe:
            Collect all conflicts, then reject if ANY accepted carbonyl has higher
            priority than bmc. Replace the loop body with:
                conflicts = [acc for acc in occupied if <conflict_condition>]
                return not any(
                    not CrossOverlapComparator.is_higher_priority(bmc.formula, c.formula, ...)
                    for c in conflicts
                )
            This changes semantics from 'last conflict decides' to 'any conflict can reject'.
        """
        carbonyl_approved = True
        for acc in occupied:
            if acc.formula == bmc.formula:
                continue
            shared_atoms = bmc_atoms & set(acc.atoms)
            if len(shared_atoms) >= 2 and acc.overlap_group == OverlapGroup.CARBONYL_BOND_TYPES:
                carbonyl_approved = CrossOverlapComparator.is_higher_priority(
                    formula1=bmc.formula,
                    formula2=acc.formula,
                    group=OverlapGroup.CARBONYL_BOND_TYPES,
                    rules=OVERLAP_RULES_CONFIG,
                )
        return carbonyl_approved

    @staticmethod
    def _check_ar_n(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        bmc_atoms: set[int],
        occupied: list[BondMatchCandidate],
    ) -> bool:
        """Reject if bmc shares 3+ atoms with any accepted Ar-N candidate."""
        ar_n_approved = True
        for acc in occupied:
            is_ar_n_group = acc.overlap_group == OverlapGroup.Ar_N_BOND_TYPES
            shared_atoms = bmc_atoms & set(acc.atoms)
            if is_ar_n_group and len(shared_atoms) >= 3:
                ar_n_approved = False
        return ar_n_approved

    @staticmethod
    def _check_default(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        bmc_atoms: set[int],
        occupied: list[BondMatchCandidate],
    ) -> bool:
        """Reject dihalide candidates that share 3+ atoms with any accepted ring candidate."""
        if bmc.formula not in ("Cl-CR2-CR2-Cl", "Br-CR2-CR2-Br"):
            return True
        for acc in occupied:
            if acc.overlap_group != OverlapGroup.BICYCLIC_STRUCTURES:
                continue
            shared_atoms = bmc_atoms & set(acc.atoms)
            if len(shared_atoms) >= 4:
                return False
        return True


OVERLAP_RULES_CONFIG: dict = {
    ## Elements to the left have higher priority!
    OverlapGroup.DEFAULT: {
        "group_prio": int(OverlapGroup.DEFAULT),
        "order": "IRRELEVANT",
        "self_overlap_rule": SelfOverlapRules._check_default,
        "cross_overlap_rule": CrossOverlapRules._check_default,
        "inject_rules": {
            "Cl-CR2-CR2-Cl": OverlapInjector._inject_default,
            "Br-CR2-CR2-Br": OverlapInjector._inject_default,
            "RC#C-C(=O)R": OverlapInjector._inject_default,
        },
        "on_accept": OverlapInjector._inject_aromatic,
    },
    OverlapGroup.DOUBLE_BONDS: {
        "group_prio": int(OverlapGroup.DOUBLE_BONDS),
        "order": ("CH2=CH-CH2-", "Ar-C=C", "C=C-C=C", "C=C"),
        "self_overlap_rule": SelfOverlapRules._check_double_bonds,
        "cross_overlap_rule": CrossOverlapRules._check_double_bonds,
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
        "cross_overlap_rule": CrossOverlapRules._check_bicyclic,
        "inject_rules": {
            "cyclohexene": OverlapInjector._inject_bicyclic,
        },
        "on_accept": None,
    },
    OverlapGroup.CARBONYL_BOND_TYPES: {
        "group_prio": int(OverlapGroup.CARBONYL_BOND_TYPES),
        "order": ("RC(=O)NH2", "Ar-C(=O)NH2", "RCOOR", "Ar-COOR", "RCOOH", "Ar-COOH", "C=O"),
        "self_overlap_rule": SelfOverlapRules._check_carbonyl,
        "cross_overlap_rule": CrossOverlapRules._check_carbonyl,
        "inject_rules": {},
        "on_accept": None,
    },
    OverlapGroup.Ar_N_BOND_TYPES: {
        "group_prio": int(OverlapGroup.Ar_N_BOND_TYPES),
        "order": ("Ar-[N+]Ar3", "Ar-NR2"),
        "self_overlap_rule": None,
        "cross_overlap_rule": CrossOverlapRules._check_ar_n,
        "inject_rules": {},
        "on_accept": OverlapInjector._inject_aromatic,
    },
}
