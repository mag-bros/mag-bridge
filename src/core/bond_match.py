from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Iterable

from loader import MBAtom, MBMolecule
from src.constants.bond_types import (
    DOUBLE_BOND,
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
        return MBSubstructMatcher._Postprocess(mol, candidates)

    @staticmethod
    def _Postprocess(
        mol: MBMolecule, candidates: list[BondMatchCandidate]
    ) -> SubstructMatchResult:
        """Remove overlapping substructures (same logic as previous version)."""
        if not candidates:
            return SubstructMatchResult.empty()

        # Group candidates by formula (bond type)
        grouped_candidates: dict[str, list[BondMatchCandidate]] = defaultdict(list)
        for c in candidates:
            grouped_candidates[c.formula].append(c)

        filtered: dict[str, list[BondMatchCandidate]] = (
            MBSubstructMatcher._FilterSelfOverlaps(grouped_candidates)
        )

        final_candidates_by_formula: dict[str, list[BondMatchCandidate]] = (
            MBSubstructMatcher._FilterCrossOverlaps(mol, filtered)
        )

        final_hits_by_formula: dict[str, list[tuple[int, ...]]] = {
            f: [tuple(sorted(c.atoms)) for c in lst]
            for f, lst in final_candidates_by_formula.items()
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
        grouped_candidates: dict[str, list[BondMatchCandidate]],
    ) -> dict[str, list[BondMatchCandidate]]:
        # (A) Filter self-overlap within each formula (any shared atom => reject)
        filtered = defaultdict(list)

        for match, candidates in grouped_candidates.items():
            used_local: set[int] = set()
            seen: set[tuple[int, ...]] = set()

            max_seniority = max(c.seniority for c in candidates)
            is_ring = any(c.is_ring for c in candidates)

            # if it's a ring => force checking (so: do NOT skip)
            skip_removal_check = (max_seniority >= SENIORITY_THRESHOLD) and (
                not is_ring
            )

            for bmc in candidates:
                atoms = tuple(sorted(bmc.atoms))

                # optional: remove exact duplicates (RDKit symmetry/permutations)
                if atoms in seen:
                    continue
                seen.add(atoms)

                if (not skip_removal_check) and used_local.intersection(atoms):
                    continue

                filtered[match].append(bmc)
                used_local.update(atoms)

        return dict(filtered)

    @staticmethod
    def _FilterCrossOverlaps(
        mol: MBMolecule,
        grouped_candidates: dict[str, list[BondMatchCandidate]],
    ) -> dict[str, list[BondMatchCandidate]]:
        # (B) Remove cross-formula overlap by seniority (shared >1 atom => reject)
        final_by_formula = defaultdict(list)
        accepted_candidates: list[BondMatchCandidate] = []

        all_matches = sorted(
            (
                (f, lst, max(c.seniority for c in lst))
                for f, lst in grouped_candidates.items()
            ),
            key=lambda t: (-t[2], t[0]),
        )

        for match, candidates, seniority in all_matches:
            skip_removal_check = seniority >= SENIORITY_THRESHOLD

            for bmc in candidates:
                atoms = tuple(sorted(bmc.atoms))
                atom_set = set(atoms)

                # Saturated rings in bicyclic structure overlaps with 3 or more shared atoms => reject
                if (seniority > SENIORITY_THRESHOLD) and any(
                    len(atom_set & set(acc_can.atoms)) >= 3
                    for acc_can in accepted_candidates
                ):
                    BicyclicOverlaps.InjectDerivedMatches(
                        mol, bmc, accepted_candidates, final_by_formula
                    )
                    continue

                if (not skip_removal_check) and any(
                    len(atom_set & set(acc_can.atoms)) >= 1
                    for acc_can in accepted_candidates
                    if acc_can.seniority < SENIORITY_THRESHOLD
                ):
                    continue

                # Placeholder rings must be "invisible" for overlap bookkeeping + output
                final_by_formula[match].append(bmc)
                accepted_candidates.append(bmc)

        filtered_result = {
            k: [c for c in v if not c.placeholder_ring]
            for k, v in dict(final_by_formula).items()
        }
        return filtered_result


class BicyclicOverlaps:
    _Rule = Callable[
        [
            MBMolecule,
            BondMatchCandidate,
            list[BondMatchCandidate],
            dict[str, list[BondMatchCandidate]],
        ],
        None,
    ]
    _rules: dict[str, _Rule] | None = None

    @classmethod
    def _get_rules(cls) -> dict[str, _Rule]:
        if cls._rules is None:
            cls._rules = {
                "cyclohexene": cls._rule_cyclohexene,
            }
        return cls._rules

    @classmethod
    def InjectDerivedMatches(
        cls,
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        accepted_candidates: list[BondMatchCandidate],
        final_hits_by_formula: dict[str, list[BondMatchCandidate]],
    ) -> None:
        rule = cls._get_rules().get(bmc.formula)
        if rule is None:
            return
        rule(mol, bmc, accepted_candidates, final_hits_by_formula)

    @staticmethod
    def _rule_cyclohexene(
        mol: MBMolecule,
        bmc: BondMatchCandidate,
        accepted_candidates: list[BondMatchCandidate],
        final_hits_by_formula: dict[str, list[BondMatchCandidate]],
    ) -> None:
        exclude_idx = {i for acc in accepted_candidates for i in acc.atoms}
        double_bond_atoms = mol.GetDoubleBondAtomsIndexes(exclude_idx=exclude_idx)
        if not double_bond_atoms:
            return

        new_bmc = BondMatchCandidate.from_bt(DOUBLE_BOND, double_bond_atoms)
        accepted_candidates.append(new_bmc)
        final_hits_by_formula.setdefault(DOUBLE_BOND.formula, []).append(new_bmc)
