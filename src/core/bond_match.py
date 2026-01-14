from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from src.constants.bond_types import ALWAYS_ACCEPT_PRIO, RELEVANT_BOND_TYPES, BondType


@dataclass(frozen=True, slots=True)
class BondMatchCandidate:
    formula: str
    prio: int
    atoms: tuple[int, ...]

    @property
    def key_self(self) -> tuple[int, tuple[int, ...]]:
        # Longer matches first; tie-break by raw atom tuple (matches previous behavior)
        return (-len(self.atoms), self.atoms)


@dataclass(frozen=True, slots=True)
class SubstructMatchResult:
    # Debuggable / inspectable (kept because it’s valuable for QA and future features)
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
    def GetMatches(*, mol) -> SubstructMatchResult:
        """
        Collect candidates from substructure matching and postprocess them
        into renderer-friendly structures.
        """
        # --- 1) Collect match candidates from all relevant bond types
        candidates: list[BondMatchCandidate] = []
        for bt in RELEVANT_BOND_TYPES:
            hits = mol.GetSubstructMatches(smarts=bt.SMARTS)
            if not hits:
                continue

            prio = int(getattr(bt, "prio", 0))
            for h in hits:
                candidates.append(
                    BondMatchCandidate(
                        formula=bt.formula,
                        prio=prio,
                        atoms=tuple(int(x) for x in h),
                    )
                )

        # --- 2) Resolve overlaps + compute renderer outputs
        return MBSubstructMatcher.Postprocess(candidates=candidates)

    @staticmethod
    def Postprocess(*, candidates: list[BondMatchCandidate]) -> SubstructMatchResult:
        """Remove overlapping substructures (same logic as previous version)."""
        if not candidates:
            return SubstructMatchResult.empty()

        # --- A) Group candidates by formula (bond type)
        by_formula: dict[str, list[BondMatchCandidate]] = defaultdict(list)
        for c in candidates:
            by_formula[c.formula].append(c)

        # --- B) Remove self-overlap within each formula (any shared atom => reject)
        cleaned: dict[str, list[tuple[int, ...]]] = {}
        for formula, lst in by_formula.items():
            used_local: set[int] = set()
            kept: list[tuple[int, ...]] = []

            for c in sorted(lst, key=lambda c: c.key_self):
                atoms = tuple(sorted(c.atoms))  # normalization (as before)
                if any(a in used_local for a in atoms):
                    continue
                kept.append(atoms)
                used_local.update(atoms)

            cleaned[formula] = kept

        # --- C) Remove cross-formula overlap by priority (shared >1 atom => reject)
        formulas_sorted = sorted(
            cleaned.keys(),
            key=lambda f: (-max(c.prio for c in by_formula[f]), f),
        )

        final_hits_by_formula: dict[str, list[tuple[int, ...]]] = {}
        accepted_atom_sets: list[set[int]] = []

        for f in formulas_sorted:
            kept: list[tuple[int, ...]] = []

            f_prio = max(c.prio for c in by_formula[f])
            bypass = f_prio >= ALWAYS_ACCEPT_PRIO

            for atoms in cleaned[f]:
                atom_set = set(atoms)

                if not bypass:
                    # Reject only if it shares >1 atom with any previously accepted hit
                    if any(len(atom_set & prev) > 1 for prev in accepted_atom_sets):
                        continue

                kept.append(atoms)
                accepted_atom_sets.append(atom_set)

            final_hits_by_formula[f] = kept

        # --- D) Build counters + highlight structures
        matches_counter: Counter[str] = Counter()
        groups_atoms: dict[str, set[int]] = defaultdict(set)
        atoms_to_highlight: set[int] = set()

        for f, hits in final_hits_by_formula.items():
            if not hits:
                continue
            matches_counter[f] += len(hits)
            for h in hits:
                groups_atoms[f].update(h)
                atoms_to_highlight.update(h)

        return SubstructMatchResult(
            final_hits_by_formula=final_hits_by_formula,
            matchesCounter=matches_counter,
            highlightAtomGroups={k: sorted(v) for k, v in groups_atoms.items()},
            highlightAtomList=sorted(atoms_to_highlight),
        )

    # Optional: keep legacy 4-tuple return for any older callers
    @staticmethod
    def PostprocessLegacy(
        *, candidates: list[BondMatchCandidate]
    ) -> tuple[
        dict[str, list[tuple[int, ...]]],  # final_hits_by_formula
        Counter[str],  # matches_counter
        dict[str, set[int]],  # groups_atoms
        set[int],  # atoms_to_highlight
    ]:
        res = MBSubstructMatcher.Postprocess(candidates=candidates)

        # reconstruct legacy structures exactly as expected
        groups_atoms: dict[str, set[int]] = {
            k: set(v) for k, v in res.highlightAtomGroups.items()
        }
        atoms_to_highlight = set(res.highlightAtomList)

        return (
            res.final_hits_by_formula,
            res.matchesCounter,
            groups_atoms,
            atoms_to_highlight,
        )
