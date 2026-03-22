# Substruct Matcher Architecture

Reference document for `src/core/substruct_matcher.py` and `src/overlap_rules.py`.

## Core Files

| File | Role |
|---|---|
| `src/core/substruct_matcher.py` | Orchestrator: `GetMatches → _Postprocess → _FilterSelfOverlaps → _FilterCrossOverlaps` |
| `src/overlap_rules.py` | Strategy tables: `SelfOverlapRules`, `CrossOverlapRules`, `OverlapInjector`, `OVERLAP_RULES_CONFIG` |
| `src/constants/bond_types.py` | Bond type definitions, `OverlapGroup` enum — SMARTS patterns are frozen |
| `src/core/cross_overlap_comparator.py` | Priority sorting used by `_FilterCrossOverlaps` and `CrossOverlapRules._check_carbonyl` |

---

## Data Types

```python
BondMatchCandidate      # BondType + matched atom indices (from RDKit substructure hit)
RejectedCandidate       # candidate + reason str + conflicting_with: BondMatchCandidate (1:1)
InjectedCandidate       # candidate + parent: RejectedCandidate + rule: str (1:1)
```

---

## Self-Overlaps

### `_FilterSelfOverlaps` — 3-Phase Pipeline

Filters candidates within the same formula group. Input/output: `dict[formula, list[BondMatchCandidate]]`.

```
grouped_candidates
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 1: Classify                                  │
│  SelfOverlapRules.check_overlap()                   │
│  → accepted: dict[str, list[BondMatchCandidate]]    │
│  → rejected: dict[str, list[RejectedCandidate]]     │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   accepted               rejected
        │                     │
        │          ┌──────────┘
        │          ▼
        │  ┌──────────────────────────────────────────┐
        │  │  Phase 2: Inject on rejection            │
        │  │  OverlapInjector.inject_on_reject(       │
        │  │      trigger="on_self_reject")            │
        │  └──────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 3: Inject on accept                          │
│  OverlapInjector.inject_on_reject(trigger="on_accept") │
│  (Ar-OR / Ar-NR2 aromatic duplication)              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
            dict(accepted)
```

**Phase 2 isolation:** `occupied = list(accepted[cand_key])` — inject rules may append foreign-type entries to this copy (for `exclude_idx` computation), but those writes must not contaminate `accepted[cand_key]`.

**Phase 3 `seen` list:** Each accepted candidate is processed against `seen` (candidates earlier in the same group). `seen` grows per iteration; extras are written directly to `accepted[formula]`.

### `SelfOverlapRules` — classifier

Group-level callable per `OverlapGroup`. Returns `RejectedCandidate` on overlap, `None` to accept.

| Method | Group | Threshold | Extra condition |
|---|---|---|---|
| `_check_bicyclic` | BICYCLIC_STRUCTURES | ≥ 3 shared atoms | — |
| `_check_double_bonds` | DOUBLE_BONDS | ≥ 1 shared atom | — |
| `_check_carbonyl` | CARBONYL_BOND_TYPES | ≥ 2 shared atoms | both in C=O double bond |
| `_check_default` | DEFAULT | ≥ 3 shared atoms | only for dihalide formulas (`Cl-CR2-CR2-Cl`, `R2CCl2`, `Br-CR2-CR2-Br`) |

---

## Cross-Overlaps

### `_FilterCrossOverlaps` — Priority-Sorted Pipeline

Filters candidates across different formula groups using priority ordering from `OVERLAP_RULES_CONFIG`.

```
grouped_candidates
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Sort all candidates by group priority              │
│  CrossOverlapComparator.sort_matches()              │
└──────────────────┬──────────────────────────────────┘
                   │
                   │  ↻ one bmc at a time, in sorted order
                   ▼
┌─────────────────────────────────────────────────────┐
│  Check bmc against occupied                         │
│  CrossOverlapRules.check_overlap()                  │
│  → approve / reject                                 │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────────────────────────────────────────┐
        ▼                                                         ▼
┌───────────────────────────────┐  ┌──────────────────────────────────┐
│  approve                      │  │  reject                          │
│                               │  │                                  │
│  bmc → accepted               │  │  OverlapInjector                 │
│  bmc → occupied               │  │  .inject_on_reject(              │
│                               │  │    trigger="on_cross_reject")    │
│                               │  │  → may append to accepted +      │
│                               │  │    occupied                      │
└──────────────┬────────────────┘  └────────────────┬─────────────────┘
               │                                    │
               └─────────────────┬──────────────────┘
                                 │  (occupied updated
                                 │   before next bmc) ↺

         (after all iterations)
┌─────────────────────────────────────────────────────┐
│  Strip dummy rings + dummy bond types               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
            dict(accepted)
```

### Cross-Overlap Structural Requirements

- **Candidates must be processed in group priority order** — each decision reads `occupied` built by all prior iterations; group priority determines which formulas "claim" atoms first.
- **OverlapInjector must fire in the same iteration as the rejection** — injected candidates (e.g. a C=C from a rejected cyclohexene) compute free atoms from the current `occupied` snapshot; deferring it to after the loop would expand that snapshot and produce wrong or missing injections.
- **Check-overlap methods only return a decision** — writing to `accepted` or `occupied` always happens at the caller level, keeping rule methods consistent with `SelfOverlapRules`.

### `CrossOverlapRules` — classifier

Group-level callable per `OverlapGroup`. Returns `True` to approve, `False` to reject. Dispatched via `OVERLAP_RULES_CONFIG["cross_overlap_rule"]`. All methods use a `{group}_approved` accumulator — custom logic per group, uniform interface.

| Method | Group | Threshold | Extra condition |
|---|---|---|---|
| `_check_bicyclic` | BICYCLIC_STRUCTURES | ≥ 3 shared atoms with any accepted | — |
| `_check_double_bonds` | DOUBLE_BONDS | ≥ 1 shared atom with any accepted double-bond | — |
| `_check_carbonyl` | CARBONYL_BOND_TYPES | ≥ 2 shared atoms with accepted carbonyl | priority comparison via `CrossOverlapComparator`; last-wins (see docstring) |
| `_check_ar_n` | Ar_N_BOND_TYPES | ≥ 3 shared atoms with any accepted Ar-N | — |

**Return type asymmetry vs `SelfOverlapRules`:** `CrossOverlapRules` returns `bool` rather than `RejectedCandidate | None` because cross-overlap conflicts are many-to-one and relational — the 1:1 `conflicting_with` model of `RejectedCandidate` does not apply.

---

## Overlap Injector

### `OverlapInjector` — side-effect rules

Fires when a rejected candidate can produce a valid alternative match. All rule methods receive `trigger: str` as last parameter — available in debugger, not used by logic.

| Method | Trigger | Condition | Action |
|---|---|---|---|
| `_inject_bicyclic` | `on_cross_reject` | formula == "cyclohexene" | Add C=C double bond matches from free atoms |
| `_inject_default` | `on_self_reject` | formula == "Cl-CR2-CR2-Cl" | Inject free C-Cl bonds for each free Cl from unoccupied atoms |
| `_inject_aromatic` | `on_accept` | formula in `{"Ar-OR", "Ar-NR2"}`, no 1-atom conflict | Append (aromatic C count − 1) duplicate copies |

### `inject_on_reject()` dispatch

```python
trigger == "on_accept"
    → OVERLAP_RULES_CONFIG[group]["on_accept"]              # group-level callable

trigger == "on_self_reject" | "on_cross_reject"
    → OVERLAP_RULES_CONFIG[group]["inject_rules"][formula]  # formula-level dict
```

**`_inject_aromatic` formula guard:** DEFAULT is a catch-all group — without an internal check, `_inject_aromatic` would fire for `benzene` and any DEFAULT formula with aromatic C. Guard: `if bmc.formula not in {"Ar-OR", "Ar-NR2"}: return False`.

---

## `OVERLAP_RULES_CONFIG` Structure

Defined in `overlap_rules.py` after all class definitions (method references resolve at module level). Wires all three domains — self-overlap rule, cross-overlap rule, inject rules, and on-accept hook — into one config per group.

```python
OverlapGroup.DEFAULT: {
    "group_prio": int,  "order": "IRRELEVANT",
    "self_overlap_rule":  SelfOverlapRules._check_default,
    "cross_overlap_rule": None,
    "inject_rules":       {"Cl-CR2-CR2-Cl": OverlapInjector._inject_default},
    "on_accept":          OverlapInjector._inject_aromatic,
},
OverlapGroup.DOUBLE_BONDS: {
    "self_overlap_rule":  SelfOverlapRules._check_double_bonds,
    "cross_overlap_rule": CrossOverlapRules._check_double_bonds,
    "inject_rules":       {},
    "on_accept":          None,
},
OverlapGroup.BICYCLIC_STRUCTURES: {
    "self_overlap_rule":  SelfOverlapRules._check_bicyclic,
    "cross_overlap_rule": CrossOverlapRules._check_bicyclic,
    "inject_rules":       {"cyclohexene": OverlapInjector._inject_bicyclic},
    "on_accept":          None,
},
OverlapGroup.CARBONYL_BOND_TYPES: {
    "self_overlap_rule":  SelfOverlapRules._check_carbonyl,
    "cross_overlap_rule": CrossOverlapRules._check_carbonyl,
    "inject_rules":       {},
    "on_accept":          None,
},
OverlapGroup.Ar_N_BOND_TYPES: {
    "self_overlap_rule":  None,
    "cross_overlap_rule": CrossOverlapRules._check_ar_n,
    "inject_rules":       {},
    "on_accept":          OverlapInjector._inject_aromatic,
},
```

---

## Import Chain (no circular imports)

```
bond_types.py               ← stdlib only
    ↑
cross_overlap_comparator.py ← imports bond_types
    ↑
overlap_rules.py            ← imports bond_types, cross_overlap_comparator, src.core.molecule
    ↑
substruct_matcher.py        ← imports overlap_rules, cross_overlap_comparator
```
