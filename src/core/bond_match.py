from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from loader import MBMolecule
from src.constants.bond_types import ALWAYS_ACCEPT_PRIO, RELEVANT_BOND_TYPES, BondType


@dataclass(frozen=True, slots=True)
class BondMatchCandidate:
    formula: str
    prio: int
    atoms: tuple[int, ...]


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
                candidates.append(
                    BondMatchCandidate(
                        formula=bt.formula,
                        prio=bt.prio,
                        atoms=tuple(int(x) for x in hit),
                    )
                )

        # --- 2) Resolve overlaps + compute renderer outputs
        return MBSubstructMatcher._Postprocess(candidates=candidates)

    @staticmethod
    def _Postprocess(candidates: list[BondMatchCandidate]) -> SubstructMatchResult:
        """Remove overlapping substructures (same logic as previous version)."""
        if not candidates:
            return SubstructMatchResult.empty()

        # Group candidates by formula (bond type)
        by_formula: dict[str, list[BondMatchCandidate]] = defaultdict(list)
        for c in candidates:
            by_formula[c.formula].append(c)

        final_hits_by_formula = MBSubstructMatcher._RemoveOverlaps(
            by_formula=by_formula
        )

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
        by_formula: dict[str, list[BondMatchCandidate]],
    ) -> dict[str, list[tuple[int, ...]]]:
        # (A) Remove self-overlap within each formula (any shared atom => reject)
        cleaned: dict[str, list[tuple[int, ...]]] = {}

        for formula, lst in by_formula.items():
            used_local: set[int] = set()
            kept: list[tuple[int, ...]] = []

            skip_removal_check = (
                max(c.prio for c in by_formula[formula]) >= ALWAYS_ACCEPT_PRIO
            )

            for c in lst:
                atoms = tuple(sorted(c.atoms))  # normalization (as before)
                if not skip_removal_check:
                    if any(a in used_local for a in atoms):
                        continue
                kept.append(atoms)
                used_local.update(atoms)

            cleaned[formula] = kept

        # (B) Remove cross-formula overlap by priority (shared >1 atom => reject)
        prio_by_f = {f: max(c.prio for c in by_formula[f]) for f in cleaned}
        formulas_sorted = sorted(cleaned, key=lambda f: (-prio_by_f[f], f))

        final_hits_by_formula: dict[str, list[tuple[int, ...]]] = {}
        accepted: list[tuple[int, set[int]]] = []  # (prio, atom_set)

        for formula in formulas_sorted:
            f_prio = prio_by_f[formula]
            skip_removal_check = f_prio >= ALWAYS_ACCEPT_PRIO
            kept: list[tuple[int, ...]] = []

            for atoms in cleaned[formula]:
                atom_set = set(atoms)

                # Reject overlaps only against previously accepted NON-bypass hits
                if (not skip_removal_check) and any(
                    len(atom_set & prev) > 1
                    for p, prev in accepted
                    if p < ALWAYS_ACCEPT_PRIO
                ):
                    continue

                kept.append(atoms)
                accepted.append((f_prio, atom_set))

            final_hits_by_formula[formula] = kept

        return final_hits_by_formula
