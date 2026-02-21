# Cross-Overlap Sorting Design

## Problem

`_FilterCrossOverlaps` in `substruct_matcher.py` sorts candidates using `seniority`, a field that is being phased out. The sort logic is inlined in the caller and uses a 3-tuple `(formula, candidates, max_seniority)` with the third element discarded downstream.

## Solution

Move sorting responsibility entirely to `CrossOverlapComparator.sort_matches`. Sorting is driven exclusively by `CROSS_OVERLAP_RULES` — the single source of truth defined by domain experts.

## Sort Algorithm

Two-stage sort key `(-group_prio, order_index)`:

1. **Group-level** (`-group_prio`): higher `group_prio` is processed first. Current order: BICYCLIC(2) → CARBONYL(1) → DOUBLE_BONDS(0) → DEFAULT(-1).
2. **Intra-group** (`order_index`): position of the formula in `rules[group]["order"]` tuple. Left = highest priority. Exact chemist-defined order is preserved. DEFAULT group formulas (no tuple order) fall back to index `0`.

## Contract Change

Output changes from `list[tuple[str, list, int]]` to `list[tuple[str, list]]`. Caller changes:

```python
# before
for match, candidates, _ in all_matches:

# after
for match, candidates in all_matches:
```

## Files Affected

- `src/core/cross_overlap_comparator.py` — add `sort_matches` static method
- `src/core/substruct_matcher.py` — replace inline sort with `CrossOverlapComparator.sort_matches`, update loop signature, remove TODO comment
- `tests/core/test_cross_overlap_comparator.py` — add `test_sort_matches`
