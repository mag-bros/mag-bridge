# Refactor Plan: `_FilterSelfOverlaps`

**Scope:** `src/core/substruct_matcher.py` — only this file changes.

**Status:** Phase 1-3 refactor applied. Next step: extract `SelfOverlapRules` class.

## Problem

`_FilterSelfOverlaps` manages three entangled state containers (`filtered`, `accepted_self_candidates`, `approve_candidate` flag) that diverge silently. Injection and duplication happen mid-iteration, breaking the isolation contract. Debugging is blind — rejections leave no trail.

## New Aggregates

Add two dataclasses to `substruct_matcher.py`:

```python
@dataclass
class RejectedCandidate:
    candidate: BondMatchCandidate
    reason: str
    conflicting_with: BondMatchCandidate  # 1:1

@dataclass
class InjectedCandidate:
    candidate: BondMatchCandidate
    parent: RejectedCandidate  # 1:1
    rule: str
```

## `_FilterSelfOverlaps()`

- **Three phases, each with a single responsibility:**
```
grouped_candidates
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 1: Classify                                  │
│  SelfOverlapRules.classify() → accepted / rejected  │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   accepted               rejected
        │                     │
        │          ┌──────────┘
        │          ▼
        │  ┌──────────────────────────────────────────┐
        │  │  Phase 2: InjectDerived                  │
        │  │  OverlapRules.InjectDerivedMatches()      │
        │  └──────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 3: InjectDuplicates  (Ar-OR / Ar-NR2 only)  │
│  _GetAromaticDuplicates()                           │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
            dict(accepted)
```

- **Two typed aggregates replace three entangled state variables:**
```python
# Before
filtered                  # dict  — output, mutated by filter + injection + duplication
accepted_self_candidates  # list  — comparison set, contaminated by injected foreign types
approve_candidate         # bool  — flipped back and forth across loop iterations

# After
accepted: dict[str, list[BondMatchCandidate]]  # output + comparison set (unified)
rejected: dict[str, list[RejectedCandidate]]   # explicit rejection record with reason + conflict
```

- **Each `match/case` branch is now a pure predicate — accept or reject, nothing else:**
```python
# Before: branch mutates output mid-loop
OverlapRules.InjectDerivedMatches(..., final_hits_by_formula=filtered)
approve_candidate = False

# After: branch only classifies
rejected[cand_key].append(RejectedCandidate(candidate=bmc, reason="...", conflicting_with=acc))
```

## Next: `SelfOverlapRules` class

Extract Phase 1 classification logic into a new class. Each `match/case` branch becomes a static method with a shared contract:

```python
class SelfOverlapRules:
    """Per-OverlapGroup classification rules for self-overlap filtering."""

    _ClassifyRule = Callable[
        [MBMolecule, BondMatchCandidate, set[int], list[BondMatchCandidate]],
        RejectedCandidate | None,  # None = accept
    ]

    _rules: dict[OverlapGroup, _ClassifyRule] = {
        OverlapGroup.BICYCLIC_STRUCTURES: _classify_bicyclic,
        OverlapGroup.DOUBLE_BONDS:        _classify_double_bonds,
        OverlapGroup.CARBONYL_BOND_TYPES: _classify_carbonyl,
        OverlapGroup.DEFAULT:             _classify_default,
    }
```

**Per-group rule summary:**

| OverlapGroup | Threshold | Extra check | Reason string |
|---|---|---|---|
| BICYCLIC_STRUCTURES | `>= 3` atoms | — | `bicyclic_overlap_3_atoms` |
| DOUBLE_BONDS | `>= 1` atom | — | `double_bond_overlap_1_atom` |
| CARBONYL_BOND_TYPES | `>= 2` atoms | both in double bond | `carbonyl_double_bond_overlap_2_atoms` |
| DEFAULT (Cl/Br) | `>= 3` atoms | — | `dihalide_ring_overlap_3_atoms` |
| DEFAULT (other) | — | always accept | — |

**Naming rationale:** `SelfOverlapRules` parallels existing `OverlapRules`. Future merge path: both become one `OverlapRules` with classify + inject capabilities.

## Tradeoffs

- **Injection timing shifted post-loop** — functionally equivalent (injected matches have ≤2 atoms, never reach any overlap threshold).
- **DEFAULT Cl/Br simplified to `>= 3`** — explicit `approve=True` for 1/2 conflicts were no-ops. Removed misleading branches.
- **Ar-OR/Ar-NR2 duplication adds 1x per non-conflicting candidate** — corrects original `for/else` double-count. No test impact.

## Constraints
- SMARTS patterns must not change
- No changes outside `src/core/substruct_matcher.py`
- All existing tests must pass without modification
- `_FilterCrossOverlaps` input/output contract unchanged
