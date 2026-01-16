from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass

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

        final_hits_by_formula = MBSubstructMatcher._RemoveOverlaps(grouped_candidates)

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
    def _RemoveOverlaps(
        grouped_candidates: dict[str, list[BondMatchCandidate]],
    ) -> dict[str, list[tuple[int, ...]]]:
        # (A) Remove self-overlap within each formula (any shared atom => reject)
        cleaned: dict[str, list[tuple[int, ...]]] = {}

        for formula, lst in grouped_candidates.items():
            used_local: set[int] = set()
            kept: list[tuple[int, ...]] = []

            skip_removal_check = (
                max(c.seniority for c in grouped_candidates[formula])
                >= SENIORITY_THRESHOLD
            )

            for c in lst:
                atoms = tuple(sorted(c.atoms))  # normalization (as before)
                if not skip_removal_check:
                    if any(a in used_local for a in atoms):
                        continue
                kept.append(atoms)
                used_local.update(atoms)

            cleaned[formula] = kept

        # (B) Remove cross-formula overlap by seniorityrity (shared >1 atom => reject)
        seniority_by_f = {f: max(c.seniority for c in by_formula[f]) for f in cleaned}
        matches = sorted(cleaned, key=lambda f: (-seniority_by_f[f], f))

        final_hits_by_formula: dict[str, list[tuple[int, ...]]] = {}
        accepted: list[tuple[int, set[int]]] = []  # (seniority, atom_set)

        for match in matches:
            f_seniority = seniority_by_f[match]
            skip_removal_check = f_seniority >= SENIORITY_THRESHOLD
            kept: list[tuple[int, ...]] = []

            for atoms in cleaned[match]:
                atom_set = set(atoms)

                # Overlapping rings in bicyclic structure
                # 3 or more shared atoms are considered as an overlap
                is_bicyclic_overlap = any(
                    len(atom_set & prev) >= 3 for p, prev in accepted
                )
                if is_bicyclic_overlap:
                    continue

                # Reject overlaps only against previously accepted NON-bypass hits
                if (not skip_removal_check) and any(
                    len(atom_set & prev) > 1
                    for p, prev in accepted
                    if p < SENIORITY_THRESHOLD
                ):
                    continue

                kept.append(atoms)
                accepted.append((f_seniority, atom_set))

            final_hits_by_formula[match] = kept

        return final_hits_by_formula
