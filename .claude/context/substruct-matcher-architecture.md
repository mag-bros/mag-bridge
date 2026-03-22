# Substruct Matcher Architecture

Reference document for `src/core/substruct_matcher.py` and `src/overlap_rules.py`.

## Core Files

| File | Role |
|---|---|
| `src/core/substruct_matcher.py` | Orchestrator: `GetMatches → _Postprocess → _FilterSelfOverlaps → _FilterCrossOverlaps` |
| `src/overlap_rules.py` | Strategy tables: `SelfOverlapRules`, `OverlapInjector`, `OVERLAP_RULES_CONFIG` |
| `src/constants/bond_types.py` | Bond type definitions, `OverlapGroup` enum — SMARTS patterns are frozen |
| `src/core/cross_overlap_comparator.py` | Priority sorting used by `_FilterCrossOverlaps` |

---

## Data Types

```python
BondMatchCandidate      # BondType + matched atom indices (from RDKit substructure hit)
RejectedCandidate       # candidate + reason str + conflicting_with: BondMatchCandidate (1:1)
InjectedCandidate       # candidate + parent: RejectedCandidate + rule: str (1:1)
```

---

## `_FilterSelfOverlaps` — 3-Phase Pipeline

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
        │  │  Phase 2: InjectDerived                  │
        │  │  OverlapInjector.inject_on_reject(              │
        │  │      trigger="on_self_reject")            │
        │  └──────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 3: on_accept injection                       │
│  OverlapInjector.inject_on_reject(trigger="on_accept")     │
│  (Ar-OR / Ar-NR2 aromatic duplication)              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
            dict(accepted)
```

**Phase 2 isolation:** `working_accepted = list(accepted[cand_key])` — inject rules may append foreign-type entries to this copy (for `exclude_idx` computation), but those writes must not contaminate `accepted[cand_key]`.

**Phase 3 `seen` list:** Each accepted candidate is processed against `seen` (candidates earlier in the same group). `seen` grows per iteration; extras are written directly to `accepted[formula]`.

---

## Strategy Tables

### `SelfOverlapRules` — Phase 1 classifier

Group-level callable per `OverlapGroup`. Returns `RejectedCandidate` on overlap, `None` to accept.

| Method | Group | Threshold | Extra condition |
|---|---|---|---|
| `_check_bicyclic` | BICYCLIC_STRUCTURES | ≥ 3 shared atoms | — |
| `_check_double_bonds` | DOUBLE_BONDS | ≥ 1 shared atom | — |
| `_check_carbonyl` | CARBONYL_BOND_TYPES | ≥ 2 shared atoms | both in C=O double bond |
| `_check_default` | DEFAULT | ≥ 3 shared atoms | only for dihalide formulas (`Cl-CR2-CR2-Cl`, `R2CCl2`, `Br-CR2-CR2-Br`) |

### `OverlapInjector` — Phase 2 + Phase 3 injector

Naming convention mirrors `SelfOverlapRules`: `_inject_{group}`. All rule methods receive `trigger: str` as last parameter — available in debugger, not used by logic.

| Method | Trigger | Condition | Action |
|---|---|---|---|
| `_inject_bicyclic` | `on_cross_reject` | formula == "cyclohexene" | Add C=C double bond matches from free atoms |
| `_inject_default` | `on_self_reject` | formula == "Cl-CR2-CR2-Cl" | Inject free C-Cl bonds from unoccupied atoms |
| `_inject_aromatic` | `on_accept` | formula in `{"Ar-OR", "Ar-NR2"}`, no 1-atom conflict | Append (aromatic C count − 1) duplicate copies |

### `inject()` dispatch

```python
trigger == "on_accept"
    → OVERLAP_RULES_CONFIG[group]["on_accept"]          # group-level callable

trigger == "on_self_reject" | "on_cross_reject"
    → OVERLAP_RULES_CONFIG[group]["inject_rules"][formula]  # formula-level dict
```

---

## `OVERLAP_RULES_CONFIG` Structure

Defined in `overlap_rules.py` after all class definitions (method references resolve at module level).

```python
OverlapGroup.DEFAULT: {
    "group_prio": int,  "order": "IRRELEVANT",
    "self_overlap_rule": SelfOverlapRules._check_default,
    "inject_rules":      {"Cl-CR2-CR2-Cl": OverlapInjector._inject_default},
    "on_accept":         OverlapInjector._inject_aromatic,
},
OverlapGroup.DOUBLE_BONDS: {
    "self_overlap_rule": SelfOverlapRules._check_double_bonds,
    "inject_rules":      {},
    "on_accept":         None,
},
OverlapGroup.BICYCLIC_STRUCTURES: {
    "self_overlap_rule": SelfOverlapRules._check_bicyclic,
    "inject_rules":      {"cyclohexene": OverlapInjector._inject_bicyclic},
    "on_accept":         None,
},
OverlapGroup.CARBONYL_BOND_TYPES: {
    "self_overlap_rule": SelfOverlapRules._check_carbonyl,
    "inject_rules":      {},
    "on_accept":         None,
},
OverlapGroup.Ar_N_BOND_TYPES: {
    "self_overlap_rule": None,
    "inject_rules":      {},
    "on_accept":         OverlapInjector._inject_aromatic,
},
```

**`_inject_aromatic` formula guard:** DEFAULT is a catch-all group. Without an internal formula check, `_inject_aromatic` would fire for `benzene`, `Ar-C(=O)R`, and any other DEFAULT-group formula that has aromatic C atoms in its match. Guard: `if bmc.formula not in {"Ar-OR", "Ar-NR2"}: return False` — follows the same internal-filtering pattern as `_check_default`.

---

## `_FilterCrossOverlaps`

Filters candidates across different formula groups using priority ordering from `OVERLAP_RULES_CONFIG`. `CrossOverlapComparator.sort_matches()` determines processing order (higher priority groups resolved first). Calls `OverlapInjector.inject_on_reject(trigger="on_cross_reject")` for BICYCLIC_STRUCTURES rejections.

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
│  Check bmc against accepted_candidates              │
│  → approve / reject                                 │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
     approve               reject
        │                     │
        ▼                     ▼
  append bmc to      OverlapInjector.inject_on_reject()
  filtered +         trigger="on_cross_reject"
  accepted_candidates  → may append to filtered + accepted_candidates
        │                     │
        └──────────┬──────────┘
                   │  (accepted_candidates updated before next bmc)
                   ▼
         (after all iterations)
┌─────────────────────────────────────────────────────┐
│  Strip dummy rings + dummy bond types               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
            dict(filtered)
```

### Cross Overlap Structural Requirements

- **Candidates must be processed in group priority order** — each decision reads `accepted_candidates` built by all prior iterations; group priority determines which formulas "claim" atoms first.
- **OverlapInjector must fire in the same iteration as the rejection** — injected candidates (e.g. a C=C from a rejected cyclohexene) compute free atoms from the current `accepted_candidates` snapshot; deferring it to after the loop would expand that snapshot and produce wrong or missing injections.
- **Check-overlap methods only return a decision** — writing to `filtered` or `accepted_candidates` always happens at the caller level, keeping rule methods consistent with `SelfOverlapRules`.

---

## Import Chain (no circular imports)

```
bond_types.py          ← stdlib only
    ↑
overlap_rules.py       ← imports bond_types, src.core.molecule
    ↑
substruct_matcher.py   ← imports overlap_rules
```
