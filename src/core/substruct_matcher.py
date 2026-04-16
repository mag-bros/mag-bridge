from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from src.constants.bond_types import RELEVANT_BOND_TYPES
from src.core.cross_overlap_comparator import CrossOverlapComparator
from src.core.molecule import MBMolecule
from src.overlap_rules import (
    OVERLAP_RULES_CONFIG,
    BondMatchCandidate,
    CrossOverlapRules,
    OverlapInjector,
    RejectedCandidate,
    SelfOverlapRules,
)


@dataclass(frozen=True, slots=True)
class SubstructMatchResult:
    hits_by_formula: dict[str, list[tuple[int, ...]]]

    # Renderer-ready outputs
    matchesCounter: Counter[str]
    highlightAtomGroups: dict[str, list[int]]
    highlightAtomList: list[int]

    @staticmethod
    def empty() -> "SubstructMatchResult":
        return SubstructMatchResult(
            hits_by_formula={},
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

        self_filtered: dict[str, list[BondMatchCandidate]] = MBSubstructMatcher._FilterSelfOverlaps(mol, grouped_candidates)

        cross_filtered: dict[str, list[BondMatchCandidate]] = MBSubstructMatcher._FilterCrossOverlaps(mol, self_filtered)

        hits_by_formula: dict[str, list[tuple[int, ...]]] = {f: [tuple(sorted(bmc.atoms)) for bmc in lst] for f, lst in cross_filtered.items()}

        # Build counters + highlight structures
        matches_counter: Counter[str] = Counter()
        highlight_groups: dict[str, set[int]] = defaultdict(set)
        atoms_to_highlight: set[int] = set()

        for formula, hits in hits_by_formula.items():
            if not hits:
                continue
            matches_counter[formula] += len(hits)
            for hit in hits:
                highlight_groups[formula].update(hit)
                atoms_to_highlight.update(hit)

        return SubstructMatchResult(
            hits_by_formula=hits_by_formula,
            matchesCounter=matches_counter,
            highlightAtomGroups={k: sorted(v) for k, v in highlight_groups.items()},
            highlightAtomList=sorted(atoms_to_highlight),
        )

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
        for cand_key, rejects in rejected.items():
            # Snapshot of group's accepted — injectors may append but must not pollute accepted[cand_key]
            occupied: list[BondMatchCandidate] = list(accepted[cand_key])
            for rc in rejects:
                OverlapInjector.inject_on_reject(
                    mol=mol,
                    bmc=rc.candidate,
                    occupied=occupied,
                    accepted=accepted,
                    trigger="on_self_reject",
                )

        return dict(accepted)

    @staticmethod
    def _FilterCrossOverlaps(
        mol: MBMolecule,
        grouped_candidates: dict[str, list[BondMatchCandidate]],
    ) -> dict[str, list[BondMatchCandidate]]:
        """Filter cross overlaps via specific rules, respecting relations between Bond Match Candidates."""
        accepted: dict[str, list[BondMatchCandidate]] = defaultdict(list)
        # Flat list of all accepted candidates across all groups — tracks which atoms are occupied globally
        occupied: list[BondMatchCandidate] = []
        all_matches = CrossOverlapComparator.sort_matches(grouped_candidates, OVERLAP_RULES_CONFIG)

        for _iteration, (cand_key, candidates) in enumerate(all_matches):
            for bmc in candidates:
                bmc_atoms = set(tuple(sorted(bmc.atoms)))

                approve_candidate = CrossOverlapRules.check_overlap(mol, bmc, bmc_atoms, occupied)
                if not approve_candidate:
                    OverlapInjector.inject_on_reject(mol=mol, bmc=bmc, occupied=occupied, accepted=accepted, trigger="on_cross_reject")
                if approve_candidate:
                    accepted[cand_key].append(bmc)
                    occupied.append(bmc)

        # Placeholder "dummy" rings must be removed from output - they are temporary objects used only during processing
        filtered_result = {k: [c for c in v if (not c.dummy_ring and not c.dummy_bond_type)] for k, v in dict(accepted).items()}
        return filtered_result
