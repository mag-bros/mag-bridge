from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Iterable

from loader import MBAtom, MBMolecule
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
        final_hits_by_formula: dict[str, list[tuple[int, ...]]] = (
            MBSubstructMatcher._FilterCrossOverlaps(mol, filtered)
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
    def _FilterSelfOverlaps(
        grouped_candidates: dict[str, list[BondMatchCandidate]],
    ) -> dict[str, list[BondMatchCandidate]]:
        # (A) Filter self-overlap within each formula (any shared atom => reject)
        filtered: dict[str, list[BondMatchCandidate]] = {}

        for formula, lst in grouped_candidates.items():
            used_local: set[int] = set()
            kept: list[BondMatchCandidate] = []

            skip_removal_check = max(c.seniority for c in lst) >= SENIORITY_THRESHOLD

            for c in lst:
                atoms = tuple(sorted(c.atoms))  # same normalization
                # TODO cyclohexene
                if (not skip_removal_check) and any(a in used_local for a in atoms):
                    continue

                kept.append(c)
                used_local.update(atoms)

            filtered[formula] = kept

        return filtered

    @staticmethod
    def _FilterCrossOverlaps(
        mol: MBMolecule,
        filtered: dict[str, list[BondMatchCandidate]],
    ) -> dict[str, list[tuple[int, ...]]]:
        # (B) Remove cross-formula overlap by seniority (shared >1 atom => reject)
        final_hits_by_formula: dict[str, list[tuple[int, ...]]] = {}
        accepted_candidates: list[BondMatchCandidate] = []

        # sort by (-seniority, formula) while carrying match seniority inline
        matches = sorted(
            ((f, lst, max(c.seniority for c in lst)) for f, lst in filtered.items()),
            key=lambda t: (-t[2], t[0]),
        )

        for match, match_candidates, match_seniority in matches:
            kept_atoms: list[tuple[int, ...]] = []
            skip_removal_check = match_seniority >= SENIORITY_THRESHOLD

            for bmc in match_candidates:
                atoms = tuple(sorted(bmc.atoms))
                atom_set = set(atoms)

                # Saturated rings in bicyclic structure overlaps with 3 or more shared atoms => reject
                is_bicyclic_overlap = (match_seniority > SENIORITY_THRESHOLD) and any(
                    len(atom_set & set(acc_can.atoms)) >= 3
                    for acc_can in accepted_candidates
                )

                if is_bicyclic_overlap:
                    if bmc.formula == "cyclohexene":
                        free_atoms = []
                        for acc_can in accepted_candidates:
                            free_atoms.extend(
                                [
                                    a
                                    for a in mol.GetAtoms()
                                    if a.idx not in acc_can.atoms
                                ]
                            )

                        double_bonds: list[bool] = [
                            a.has_double_bond for a in free_atoms
                        ]
                        indexes: tuple[int, ...] = tuple(a.idx for a in free_atoms)
                        additional_double_bonds = (sum(double_bonds) // 2) % 2
                        cc = BondType(
                            formula="C=C",
                            SMARTS="[C;!$([c]);!$([C]-[c]);!$(C1=CCCCC1)]=[C;!$([c]);!$([C]-[c]);!$(C1=CCCCC1)]",
                            constitutive_corr=5.5,
                            sdf_files=("C2H4.sdf",),
                            seniority=0,
                        )
                        double_bond_atoms = tuple(
                            a for a, m in zip(indexes, double_bonds) if m
                        )

                        accepted_candidates.append(
                            BondMatchCandidate.from_bt(cc, double_bond_atoms)
                        )
                        final_hits_by_formula.setdefault("C=C", []).append(
                            double_bond_atoms
                        )

                    continue

                if (not skip_removal_check) and any(
                    len(atom_set & set(acc_can.atoms)) >= 1
                    for acc_can in accepted_candidates
                    if acc_can.seniority < SENIORITY_THRESHOLD
                ):
                    continue

                # Placeholder rings must be "invisible" for overlap bookkeeping
                accepted_candidates.append(bmc)
                if not bmc.placeholder_ring:
                    kept_atoms.append(atoms)

            final_hits_by_formula[match] = kept_atoms

        return final_hits_by_formula
