/prime

After priming, read these files before doing anything else:
- `.claude/context/substruct-matcher-architecture.md` — full architecture reference
- `.claude/context/substruct-matching.md` — open tasks (find task #2)
- `src/core/substruct_matcher.py` — focus on `_FilterCrossOverlaps` (lines 154–225)
- `src/overlap_rules.py` — existing strategy tables for reference

---

## Task: Extract `CrossOverlapRules` from `_FilterCrossOverlaps`

`_FilterCrossOverlaps` currently uses a `match bmc.cross_overlap_group: case ...` block with
4 branches. Your task is to extract this into a new `CrossOverlapRules` class in
`src/overlap_rules.py`, following the exact same strategy pattern as `SelfOverlapRules`.

### What each branch must become

| Case | New method | Returns |
|---|---|---|
| `BICYCLIC_STRUCTURES` | `_check_bicyclic` | `bool` (approve) |
| `DOUBLE_BONDS` | `_check_double_bonds` | `bool` (approve) |
| `CARBONYL_BOND_TYPES` | `_check_carbonyl` | `bool` (approve) |
| `Ar_N_BOND_TYPES` | `_check_ar_n` | `bool` (approve) |
| `case _` | default → True | — |

### Class contract

```python
class CrossOverlapRules:
    """Strategy table mapping each OverlapGroup to its cross-overlap classification rule;
    returns True to approve, False to reject."""

    @classmethod
    def check_overlap(cls, mol, bmc, bmc_atoms, accepted_candidates, filtered) -> bool:
        """Dispatch to the group's cross-overlap rule; returns True (approve) if no rule registered."""
        ...
```

Static methods follow the naming convention `_check_{group}` — consistent with
`SelfOverlapRules._check_bicyclic`, `_check_double_bonds`, etc.

### Key detail: BICYCLIC_STRUCTURES branch

The BICYCLIC branch calls `OverlapInjector.inject(trigger="on_cross_reject")` before
returning False. This call must be preserved inside `_check_bicyclic` — do not drop it.

### After extraction

`_FilterCrossOverlaps` inner loop becomes:

```python
approve_candidate = CrossOverlapRules.check_overlap(
    mol, bmc, bmc_atoms, accepted_candidates, filtered
)
```

The `match/case` block is removed entirely.

### Rules

- Use `pyright-lsp` plugin for ALL Python file work (required by CLAUDE.md)
- Change scope: `src/overlap_rules.py` and `src/core/substruct_matcher.py` only
- Add `CrossOverlapRules` to `OVERLAP_RULES_CONFIG` dispatch (add `cross_overlap_rule` key per group)
- Docstrings must follow the one-liner style in `SelfOverlapRules` — action verb, condition, effect
- Do NOT run pytest. When the implementation is complete, stop and ask the developer to run tests.
- If you find any inconsistency between the existing code and this brief, stop and report it before proceeding.

### Watch out

Two known asymmetries to flag before implementing — do not silently resolve them:

1. **`check_overlap` signature has an extra `filtered` param** vs `SelfOverlapRules.check_overlap`
   (needed because `_check_bicyclic` must call `OverlapInjector.inject()` into it).
   Propose how to handle this asymmetry and wait for confirmation.

2. **`CARBONYL_BOND_TYPES` branch** calls `CrossOverlapComparator.is_higher_priority()` —
   it references `OVERLAP_RULES_CONFIG` and compares `bmc.formula` vs `acc_can.formula` within
   the loop. Confirm whether this stays fully inline inside `_check_carbonyl` or needs
   further decomposition before proceeding.
