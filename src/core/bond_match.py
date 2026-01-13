from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class BondMatchCandidate:
    formula: str
    prio: int
    atoms: tuple[int, ...]

    @property
    def key_self(self) -> tuple[int, tuple[int, ...]]:
        return (-len(self.atoms), self.atoms)


class MBSubstructMatcher:
    @staticmethod
    def Postprocess(
        candidates: list[BondMatchCandidate],
    ) -> tuple[
        dict[str, list[tuple[int, ...]]],  # final_hits_by_formula
        Counter,  # matches_counter
        dict[str, set[int]],  # groups_atoms
        set[int],  # atoms_to_highlight
    ]:
        # A) self-overlap w obrębie formuły
        by_formula: dict[str, list[BondMatchCandidate]] = defaultdict(list)
        for c in candidates:
            by_formula[c.formula].append(c)

        cleaned: dict[str, list[tuple[int, ...]]] = {}
        for formula, lst in by_formula.items():
            used_local: set[int] = set()
            kept: list[tuple[int, ...]] = []

            for c in sorted(lst, key=lambda c: c.key_self):
                atoms = tuple(sorted(c.atoms))  # normalizacja
                if any(a in used_local for a in atoms):  # overlap? usuń
                    continue
                kept.append(atoms)
                used_local.update(atoms)

            cleaned[formula] = kept

        # B) cross-formula po priorytecie (większy prio wygrywa)
        formulas_sorted = sorted(
            cleaned.keys(),
            key=lambda f: (-max(c.prio for c in by_formula[f]), f),
        )

        final_hits_by_formula: dict[str, list[tuple[int, ...]]] = {}

        # trzymamy listę już zaakceptowanych dopasowań jako zbiory atomów
        accepted_atom_sets: list[set[int]] = []

        for f in formulas_sorted:
            kept: list[tuple[int, ...]] = []
            for atoms in cleaned[f]:
                atom_set = set(atoms)

                # reguła: z KAŻDYM wcześniej zaakceptowanym dopasowaniem
                # można współdzielić maksymalnie 1 atom
                ok = True
                for prev in accepted_atom_sets:
                    if len(atom_set & prev) > 1:
                        ok = False
                        break

                if not ok:
                    continue

                kept.append(atoms)
                accepted_atom_sets.append(atom_set)

            final_hits_by_formula[f] = kept

        # outputs
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

        return final_hits_by_formula, matches_counter, groups_atoms, atoms_to_highlight
