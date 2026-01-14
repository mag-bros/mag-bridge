# from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from src.constants.bond_types import ALWAYS_ACCEPT_PRIO


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
    def GetMatches():
        # TODO: finish this function, we need some serious
        # best practice code cleanup because the  code
        # have gone to an almost unmaintainable state
        ...

    @staticmethod
    def Postprocess(
        candidates: list[BondMatchCandidate],
    ) -> tuple[
        dict[str, list[tuple[int, ...]]],  # final_hits_by_formula
        Counter,  # matches_counter
        dict[str, set[int]],  # groups_atoms
        set[int],  # atoms_to_highlight
    ]:
        """Remove overlapping substructures."""
        # TODO: isolate self overlap code to a separate function -
        #  - not sure if it should be a method of this class or a standalone function, or a separate module
        # - we must tink of different code architectures here
        # - or find a best matching code pattern we could use
        # this code is likely to be changed in the future anyway, scale
        # maters, and naming conenvtions are crucial
        # as you can see we on purpose use non- standard naming pattern - just to match RDKit conventions
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

        # TODO: isolate cross overlap code to a separate function
        # Dont complicate this too much in general, we need a clean solution. Solitude "Ovlerap" like class
        # would probably be an overkill
        # B) cross-formula po priorytecie (większy prio wygrywa)
        formulas_sorted = sorted(
            cleaned.keys(),
            key=lambda f: (-max(c.prio for c in by_formula[f]), f),
        )

        final_hits_by_formula: dict[str, list[tuple[int, ...]]] = {}
        accepted_atom_sets: list[set[int]] = []

        for f in formulas_sorted:
            kept: list[tuple[int, ...]] = []

            # formula-level prio (bo tak sortujesz); jeśli >=100, pomijamy filtrowanie całkowicie
            f_prio = max(c.prio for c in by_formula[f])
            bypass = f_prio >= ALWAYS_ACCEPT_PRIO

            for atoms in cleaned[f]:
                atom_set = set(atoms)

                if not bypass:
                    # odrzuć tylko gdy >1 wspólny atom z którymkolwiek zaakceptowanym
                    if any(len(atom_set & prev) > 1 for prev in accepted_atom_sets):
                        continue

                kept.append(atoms)
                accepted_atom_sets.append(atom_set)

            final_hits_by_formula[f] = kept

        # outputs
        # TODO: consider creating a dataclass for the output, returning a tuple of 4 elements is not very readable
        #  and can lead to confusion
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
