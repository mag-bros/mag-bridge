from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from src.constants.bond_types import (
    RELEVANT_BOND_TYPES,
    OverlapGroup,
)
from src.core.cross_overlap_comparator import CrossOverlapComparator
from src.core.molecule import MBMolecule
from src.overlap_rules import (
    CROSS_OVERLAP_RULES,
    BondMatchCandidate,
    DerivedInjectRules,
    RejectedCandidate,
    SelfOverlapRules,
)


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
    def _GetAromaticDuplicates(mol: MBMolecule, bmc: BondMatchCandidate) -> list[BondMatchCandidate]:
        """Return (aromatic C count - 1) duplicate copies of bmc for Ar-OR / Ar-NR2 bond types."""
        aromatic_C_atoms = sum(1 for idx in bmc.atoms if mol.GetAtomInfoByIdx(idx).symbol == "C" and mol.GetAtomInfoByIdx(idx).GetIsAromatic())
        return [bmc] * (aromatic_C_atoms - 1)

    @staticmethod
    def _FilterSelfOverlaps(
        mol: MBMolecule,
        grouped_candidates: dict[str, list[BondMatchCandidate]],
    ) -> dict[str, list[BondMatchCandidate]]:
        """
        Three-phase self-overlap filter, operating in isolation per bond type group.

        Phase 1 — Pure predicate: each candidate is appended to accepted or rejected.
        Phase 2 — Derived injections: rejected candidates may produce new accepted matches.
        Phase 3 — Duplication: Ar-OR / Ar-NR2 add copies based on aromatic C count.
        """
        accepted: dict[str, list[BondMatchCandidate]] = defaultdict(list)
        rejected: dict[str, list[RejectedCandidate]] = defaultdict(list)

        # --- Phase 1: Pure filter ---
        for cand_key, candidates in grouped_candidates.items():
            for bmc in candidates:
                bmc_atoms = set(bmc.atoms)
                rejection = SelfOverlapRules.check_overlap(mol, bmc, bmc_atoms, accepted[cand_key])
                if rejection is not None:
                    rejected[cand_key].append(rejection)
                else:
                    accepted[cand_key].append(bmc)

        # --- Phase 2: Derived injections ---
        # working_accepted is a copy: injection rules may append to it (e.g. to compute exclude_idx
        # for subsequent injections), but those foreign-type appends must not pollute accepted[cand_key].
        for cand_key, rejects in rejected.items():
            working_accepted: list[BondMatchCandidate] = list(accepted[cand_key])
            for rc in rejects:
                DerivedInjectRules.inject(
                    mol=mol,
                    bmc=rc.candidate,
                    accepted_candidates=working_accepted,
                    final_hits_by_formula=accepted,
                )

        # --- Phase 3: Duplicate bond injection for Ar-OR, Ar-NR2 ---
        for cand_key, cands in list(accepted.items()):
            if cand_key not in ["Ar-OR", "Ar-NR2"]:
                continue
            extra: list[BondMatchCandidate] = []
            for i, bmc in enumerate(cands):
                bmc_atoms = set(bmc.atoms)
                internal_conflict = any(len(set(cands[j].atoms) & bmc_atoms) >= 1 for j in range(i))
                if not internal_conflict:
                    extra.extend(MBSubstructMatcher._GetAromaticDuplicates(mol, bmc))
            accepted[cand_key].extend(extra)

        return dict(accepted)

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
                            DerivedInjectRules.inject(mol=mol, bmc=bmc, accepted_candidates=accepted_candidates, final_hits_by_formula=filtered)
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
