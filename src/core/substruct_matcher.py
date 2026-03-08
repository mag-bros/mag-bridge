from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Iterable, Optional

from src.constants.bond_types import (
    AR_NR2,
    CROSS_OVERLAP_RULES,
    DOUBLE_BOND,
    RELEVANT_BOND_TYPES,
    BondType,
    OverlapGroup,
)
from src.core.cross_overlap_comparator import CrossOverlapComparator
from src.loader import MBMolecule


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
class SubstructMatchResult:
    final_hits_by_formula: dict[str, list[tuple[int, ...]]]

    # Renderer-ready outputs
    matchesCounter: Counter[str]
    highlightAtomGroups: dict[str, list[int]]
    highlightAtomList: list[int]

    @staticmethod
    def empty() -> "SubstructMatchResult":
        return SubstructMatchResult(
            final_hits_by_formula={},
            matchesCounter=Counter(),
            highlightAtomGroups={},
            highlightAtomList=[],
        )


class MBSubstructMatcher:
    @staticmethod
    def GetMatches(mol: MBMolecule) -> SubstructMatchResult:
        """
        Collect candidates from substructure matching and postprocess them
        with overlap removal and renderer output computation.
        """
        # --- 1) Collect match candidates from all relevant bond types
        candidates: list[BondMatchCandidate] = []
        for bt in RELEVANT_BOND_TYPES:
            hits = mol.GetSubstructMatches(smarts=bt.SMARTS)
            if not hits:
                continue

            for hit in hits:
                candidates.append(BondMatchCandidate.from_bt(bt, hit))

        # --- 2) Resolve overlaps + compute renderer outputs
        return MBSubstructMatcher._Postprocess(mol, candidates)

    @staticmethod
    def _Postprocess(mol: MBMolecule, candidates: list[BondMatchCandidate]) -> SubstructMatchResult:
        """Remove overlapping substructures (same logic as previous version)."""
        if not candidates:
            return SubstructMatchResult.empty()

        # Group candidates by formula (bond type)
        grouped_candidates: dict[str, list[BondMatchCandidate]] = defaultdict(list)
        for c in candidates:
            grouped_candidates[c.formula].append(c)

        filtered: dict[str, list[BondMatchCandidate]] = MBSubstructMatcher._FilterSelfOverlaps(mol, grouped_candidates)

        final_candidates_by_formula: dict[str, list[BondMatchCandidate]] = MBSubstructMatcher._FilterCrossOverlaps(mol, filtered)

        final_hits_by_formula: dict[str, list[tuple[int, ...]]] = {
            f: [tuple(sorted(c.atoms)) for c in lst] for f, lst in final_candidates_by_formula.items()
        }

        # Build counters + highlight structures
        matches_counter: Counter[str] = Counter()
        groups_atoms: dict[str, set[int]] = defaultdict(set)
        atoms_to_highlight: set[int] = set()

        # prepare data for renderer
        for formula, hits in final_hits_by_formula.items():
            if not hits:
                continue
            matches_counter[formula] += len(hits)
            for hit in hits:
                groups_atoms[formula].update(hit)
                atoms_to_highlight.update(hit)

        return SubstructMatchResult(
            final_hits_by_formula=final_hits_by_formula,
            matchesCounter=matches_counter,
            highlightAtomGroups={k: sorted(v) for k, v in groups_atoms.items()},
            highlightAtomList=sorted(atoms_to_highlight),
        )

    @staticmethod
    def _FilterSelfOverlaps(
        mol: MBMolecule,
        grouped_candidates: dict[str, list[BondMatchCandidate]],
    ) -> dict[str, list[BondMatchCandidate]]:
        """Filter self overlaps, in complete isolation within Bond Match Candidate groups."""
        filtered = defaultdict(list)

        for _iteration, (cand_key, candidates) in enumerate(grouped_candidates.items()):
            accepted_self_candidates: list[BondMatchCandidate] = []

            for bmc in candidates:
                bmc_atoms = tuple(sorted(bmc.atoms))
                approve_candidate = True

                match bmc.cross_overlap_group:
                    case OverlapGroup.BICYCLIC_STRUCTURES:
                        for acc_cand in accepted_self_candidates:
                            if len(set(acc_cand.atoms) & set(bmc_atoms)) >= 3:  # self overlap check
                                OverlapRules.InjectDerivedMatches(
                                    mol=mol,
                                    rule_key=bmc.formula,
                                    bmc=bmc,
                                    accepted_candidates=accepted_self_candidates,
                                    final_hits_by_formula=filtered,
                                )
                                approve_candidate = False

                    case OverlapGroup.DOUBLE_BONDS:
                        for acc_cand in accepted_self_candidates:
                            if len(set(acc_cand.atoms) & set(bmc_atoms)) >= 1:  # self overlap check
                                approve_candidate = False

                    case OverlapGroup.CARBONYL_BOND_TYPES:
                        for acc_cand in accepted_self_candidates:
                            intersection = set(acc_cand.atoms) & set(bmc_atoms)
                            conflicts = len(intersection)
                            if conflicts >= 2:
                                it = iter(intersection)
                                idx1, idx2 = next(it), next(it)
                                # symbols: list[MBAtom] = (mol.GetAtomInfoByIdx(idx=idx1).symbol, mol.GetAtomInfoByIdx(idx=idx2).symbol)
                                are_carbonyl_bond_atoms = all(idx in mol.GetDoubleBondAtomsIndexes() for idx in [idx1, idx2])
                                if are_carbonyl_bond_atoms:
                                    approve_candidate = False
                            # else: It is not chemically possible to have more than 2 conflicts in this case

                    case OverlapGroup.DEFAULT:

                        def _get_duplicate_bonds(mol) -> list:
                            additional = []
                            aromatic_C_atoms = 0  # Count Aromatic C Atoms for this Candidate
                            for idx in bmc_atoms:
                                candidate = mol.GetAtomInfoByIdx(idx)
                                if candidate.symbol == "C" and candidate.GetIsAromatic():
                                    aromatic_C_atoms += 1

                            for _ in range(aromatic_C_atoms - 1):
                                additional.append(bmc)  # add duplicate identical copy
                            return additional

                        # SelfOverlapRule - adding Ar-OR, Ar-NR2 bonds depending on number of aromatic C atoms
                        internal_conflict = False
                        for acc_cand in accepted_self_candidates:
                            intersection = set(acc_cand.atoms) & set(bmc_atoms)
                            conflicts = len(intersection)
                            if conflicts >= 1:
                                internal_conflict = True

                        if not internal_conflict and bmc.formula in ["Ar-OR", "Ar-NR2"]:
                            for acc_cand in accepted_self_candidates:
                                intersection = set(acc_cand.atoms) & set(bmc_atoms)
                                conflicts = len(intersection)

                                if conflicts == 0:
                                    duplicates = _get_duplicate_bonds(mol)
                                    filtered[cand_key].extend(duplicates)
                            else:
                                duplicates = _get_duplicate_bonds(mol)
                                filtered[cand_key].extend(duplicates)
                    case _:
                        pass

                if approve_candidate:
                    filtered[cand_key].append(bmc)
                    accepted_self_candidates.append(bmc)

        return dict(filtered)

    @staticmethod
    def _FilterCrossOverlaps(
        mol: MBMolecule,
        grouped_candidates: dict[str, list[BondMatchCandidate]],
    ) -> dict[str, list[BondMatchCandidate]]:
        """Filter cross overlaps via specific rules, respecting relations between Bond Match Candidates."""
        filtered = defaultdict(list)
        accepted_candidates: list[BondMatchCandidate] = []
        all_matches = CrossOverlapComparator.sort_matches(grouped_candidates, CROSS_OVERLAP_RULES)

        for _iteration, (cand_key, candidates) in enumerate(all_matches):
            for bmc in candidates:
                bmc_atoms = set(tuple(sorted(bmc.atoms)))
                approve_candidate = True

                match bmc.cross_overlap_group:
                    case OverlapGroup.BICYCLIC_STRUCTURES:
                        if any(len(bmc_atoms & set(acc_can.atoms)) >= 3 for acc_can in accepted_candidates):
                            OverlapRules.InjectDerivedMatches(
                                mol=mol, rule_key=bmc.formula, bmc=bmc, accepted_candidates=accepted_candidates, final_hits_by_formula=filtered
                            )
                            approve_candidate = False

                    case OverlapGroup.DOUBLE_BONDS:
                        if any(
                            acc_can.cross_overlap_group == OverlapGroup.DOUBLE_BONDS and len(bmc_atoms & set(acc_can.atoms)) >= 1
                            for acc_can in accepted_candidates
                        ):
                            approve_candidate = False

                    case OverlapGroup.CARBONYL_BOND_TYPES:
                        for acc_can in accepted_candidates:
                            has_overlapping_2_atoms = len(bmc_atoms & set(acc_can.atoms)) >= 2
                            if acc_can.formula == bmc.formula:
                                continue

                            if has_overlapping_2_atoms and acc_can.cross_overlap_group == OverlapGroup.CARBONYL_BOND_TYPES:
                                if CrossOverlapComparator.is_higher_priority(
                                    formula1=bmc.formula,
                                    formula2=acc_can.formula,
                                    group=OverlapGroup.CARBONYL_BOND_TYPES,
                                    rules=CROSS_OVERLAP_RULES,
                                ):
                                    # candidate is higher prio -> add to result
                                    approve_candidate = True
                                else:
                                    # candidate is lower prio -> reject candidate and skip to next
                                    approve_candidate = False

                    case OverlapGroup.Ar_N_BOND_TYPES:
                        conflicting_ar_ns = []
                        for acc_can in accepted_candidates:
                            is_target_group = acc_can.cross_overlap_group == OverlapGroup.Ar_N_BOND_TYPES
                            common_atoms = bmc_atoms & set(acc_can.atoms)
                            intersection_size = len(common_atoms)

                            if is_target_group and intersection_size >= 3:
                                conflicting_ar_ns.append(acc_can)

                        if conflicting_ar_ns:
                            approve_candidate = False

                    case _:
                        pass

                if approve_candidate:
                    filtered[cand_key].append(bmc)
                    accepted_candidates.append(bmc)

        # Placeholder "dummy" rings must be removed from output - they are temporary objects used only during processing
        filtered_result = {k: [c for c in v if (not c.dummy_ring and not c.dummy_bond_type)] for k, v in dict(filtered).items()}
        return filtered_result


class OverlapRules:
    _Rule = Callable[
        [
            MBMolecule,
            BondMatchCandidate,
            list[BondMatchCandidate],
            dict[str, list[BondMatchCandidate]],
            list[BondMatchCandidate],
        ],
        None,
    ]
    _rules: dict[str, _Rule] | None = None

    @classmethod
    def _get_rules(cls) -> dict[str, _Rule]:
        if cls._rules is None:
            cls._rules = {
                "cyclohexene": cls._rule_cyclohexene,
                "Ar-NR2": cls._rule_Ar4_N,
                # "Ar-[N+]Ar3": cls._rule_Ar4_N,
            }
        return cls._rules

    @classmethod
    def InjectDerivedMatches(
        cls,
        mol: MBMolecule,
        rule_key,
        bmc: BondMatchCandidate,
        accepted_candidates: list[BondMatchCandidate],
        final_hits_by_formula: dict[str, list[BondMatchCandidate]],
        conflicts: Optional[list[BondMatchCandidate]] = None,
    ) -> None:
        conflicts = conflicts if conflicts else []
        rule = cls._get_rules().get(bmc.formula)
        if rule is None:
            return
        rule(mol, bmc, accepted_candidates, final_hits_by_formula, conflicts)

    @staticmethod
    def _rule_Ar4_N(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        accepted_candidates: list[BondMatchCandidate],
        final_hits_by_formula: dict[str, list[BondMatchCandidate]],
        conflicts: list[BondMatchCandidate],
    ) -> None:
        """Check Check how many Aromatic C Atoms, add this many Ar-NR2 bond types.
        Exception for Ar-NR2 within dummy group of 'Ar-[N+]Ar3'"""

        for conflict in conflicts:
            if conflict.dummy_bond_type:
                new_bmc = BondMatchCandidate.from_bt(AR_NR2, double_bond_atoms)
                for _ in range(4):
                    accepted_candidates.append(new_bmc)
                    final_hits_by_formula.setdefault(DOUBLE_BOND.formula, []).append(new_bmc)
                break  # only first

    @staticmethod
    def _rule_cyclohexene(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        accepted_candidates: list[BondMatchCandidate],
        final_hits_by_formula: dict[str, list[BondMatchCandidate]],
        conflicts: list[BondMatchCandidate],
    ) -> None:
        """If cyclohexene is rejected due to bicyclic overlap, add double bond matches instead."""
        exclude_idx = {i for acc in accepted_candidates for i in acc.atoms}
        double_bond_atoms = mol.GetDoubleBondAtomsIndexes(exclude_idx=exclude_idx)
        if not double_bond_atoms:
            return

        new_bmc = BondMatchCandidate.from_bt(DOUBLE_BOND, double_bond_atoms)
        accepted_candidates.append(new_bmc)
        final_hits_by_formula.setdefault(DOUBLE_BOND.formula, []).append(new_bmc)
