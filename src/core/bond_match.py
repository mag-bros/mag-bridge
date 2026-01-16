from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Iterable

from loader import MBMolecule
from src.constants.bond_types import (
    RELEVANT_BOND_TYPES,
    SENIORITY_THRESHOLD,
    BondType,
)


class BondMatchCandidate(BondType):
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
        return MBSubstructMatcher._Postprocess(candidates)

    @staticmethod
    def _Postprocess(candidates: list[BondMatchCandidate]) -> SubstructMatchResult:
        """Remove overlapping substructures (same logic as previous version)."""
        if not candidates:
            return SubstructMatchResult.empty()

        # Group candidates by formula (bond type)
        grouped_candidates: dict[str, list[BondMatchCandidate]] = defaultdict(list)
        for c in candidates:
            grouped_candidates[c.formula].append(c)

        final_hits_by_formula = MBSubstructMatcher._FilterOverlaps(grouped_candidates)

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
    def _FilterOverlaps(
        grouped_candidates: dict[str, list[BondMatchCandidate]],
    ) -> dict[str, list[tuple[int, ...]]]:
        # (A) Filter self-overlap within each formula (any shared atom => reject)
        filtered: dict[str, list[BondMatchCandidate]] = {}

        for formula, lst in grouped_candidates.items():
            used_local: set[int] = set()
            kept: list[BondMatchCandidate] = []

            skip_removal_check = max(c.seniority for c in lst) >= SENIORITY_THRESHOLD

            for c in lst:
                atoms = tuple(sorted(c.atoms))  # same normalization
                if (not skip_removal_check) and any(a in used_local for a in atoms):
                    continue

                kept.append(c)
                used_local.update(atoms)

            filtered[formula] = kept

        # (B) Remove cross-formula overlap by seniority (shared >1 atom => reject)
        seniority_by_f = {f: max(c.seniority for c in filtered[f]) for f in filtered}
        matches = sorted(filtered, key=lambda f: (-seniority_by_f[f], f))

        final_hits_by_formula: dict[str, list[tuple[int, ...]]] = {}

        accepted_candidates: list[BondMatchCandidate] = []

        for match in matches:
            f_seniority = seniority_by_f[match]
            skip_removal_check = f_seniority >= SENIORITY_THRESHOLD
            kept_atoms: list[tuple[int, ...]] = []

            for bmc in filtered[match]:
                atoms = tuple(sorted(bmc.atoms))
                atom_set = set(atoms)

                is_bicyclic_overlap = any(
                    len(atom_set & set(acc_can.atoms)) >= 3
                    for acc_can in accepted_candidates
                )
                if is_bicyclic_overlap:
                    continue

                if (not skip_removal_check) and any(
                    len(atom_set & set(acc_can.atoms)) >= 1
                    for acc_can in accepted_candidates
                    if acc_can.seniority < SENIORITY_THRESHOLD
                ):
                    continue

                kept_atoms.append(atoms)

                # Placeholder rings must be "invisible" for overlap bookkeeping
                if not bmc.placeholder_ring:
                    accepted_candidates.append(bmc)

            final_hits_by_formula[match] = kept_atoms

        return final_hits_by_formula
