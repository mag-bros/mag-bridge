# Cross-Overlap Sorting Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace seniority-based sort in `_FilterCrossOverlaps` with a `CrossOverlapComparator.sort_matches` static method driven entirely by `CROSS_OVERLAP_RULES`.

**Architecture:** Add `sort_matches` to `CrossOverlapComparator` — it receives `grouped_candidates` and `rules`, applies a two-stage sort key `(-group_prio, order_index)`, and returns `list[tuple[str, list]]`. The caller in `substruct_matcher.py` is simplified to a single call with no knowledge of sort logic.

**Tech Stack:** Python 3.13, pytest

---

### Task 1: Add `sort_matches` to `CrossOverlapComparator` (TDD)

**Files:**
- Modify: `src/core/cross_overlap_comparator.py`
- Test: `tests/core/test_cross_overlap_comparator.py`

**Step 1: Write the failing test**

Add to `tests/core/test_cross_overlap_comparator.py`:

```python
def test_sort_matches():
    """Verify group-level and intra-group ordering from CROSS_OVERLAP_RULES."""
    from unittest.mock import MagicMock

    def make_candidates(group):
        c = MagicMock()
        c.cross_overlap_group = group
        return [c]

    grouped = {
        "C=C": make_candidates(CrossOverlapGroup.DOUBLE_BONDS),
        "cyclopropane": make_candidates(CrossOverlapGroup.BICYCLIC_STRUCTURES),
        "C=O": make_candidates(CrossOverlapGroup.CARBONYL_BOND_TYPES),
        "CH2=CH-CH2-": make_candidates(CrossOverlapGroup.DOUBLE_BONDS),
    }
    result = CrossOverlapComparator.sort_matches(grouped, CROSS_OVERLAP_RULES)
    formulas = [f for f, _ in result]

    assert formulas[0] == "cyclopropane"        # BICYCLIC group_prio=2, first
    assert formulas[1] == "C=O"                 # CARBONYL group_prio=1
    assert formulas.index("CH2=CH-CH2-") < formulas.index("C=C")  # intra-group order
```

**Step 2: Run test to verify it fails**

```bash
PYTHONPATH=src pytest tests/core/test_cross_overlap_comparator.py::test_sort_matches -v
```

Expected: `FAILED` — `AttributeError: type object 'CrossOverlapComparator' has no attribute 'sort_matches'`

**Step 3: Implement `sort_matches`**

Replace full content of `src/core/cross_overlap_comparator.py` with:

```python
from src.constants.bond_types import CrossOverlapGroup


class CrossOverlapComparator:
    """Stateless comparator for cross-overlap formula hierarchies using dependency injection."""

    @staticmethod
    def is_higher_priority(
        formula1: str,
        formula2: str,
        group: CrossOverlapGroup,
        rules: dict[CrossOverlapGroup, dict],
    ) -> bool:
        """Check if formula1 has higher priority than formula2 in the hierarchy."""
        hierarchy: tuple[str, ...] = rules[group]["order"]
        try:
            is_higher = hierarchy.index(formula1) < hierarchy.index(formula2)
            return is_higher
        except ValueError:
            return False

    @staticmethod
    def sort_matches(
        grouped_candidates: dict[str, list],
        rules: dict[CrossOverlapGroup, dict],
    ) -> list[tuple[str, list]]:
        """Sort grouped candidates by group priority then intra-group order from rules."""
        def _sort_key(item: tuple[str, list]) -> tuple[int, int]:
            formula, candidates = item
            group = candidates[0].cross_overlap_group or CrossOverlapGroup.DEFAULT
            rule = rules.get(group, rules[CrossOverlapGroup.DEFAULT])
            group_prio = rule["group_prio"]
            order = rule["order"]
            order_index = order.index(formula) if isinstance(order, tuple) and formula in order else 0
            return (-group_prio, order_index)

        return sorted(grouped_candidates.items(), key=_sort_key)
```

**Step 4: Run all comparator tests to verify they pass**

```bash
PYTHONPATH=src pytest tests/core/test_cross_overlap_comparator.py -v
```

Expected: `2 passed`

**Step 5: Commit**

```bash
git add src/core/cross_overlap_comparator.py tests/core/test_cross_overlap_comparator.py
git commit -m "feat: add CrossOverlapComparator.sort_matches driven by CROSS_OVERLAP_RULES"
```

---

### Task 2: Update `substruct_matcher.py` call site

**Files:**
- Modify: `src/core/substruct_matcher.py:152-161`

**Step 1: Replace the inline sort block**

Find this block (around line 152):

```python
        # TODO (NOT FOR NOW) - migrate seniority into cross_overlap_prio isolated field
        def _overlap_sort(t):
            return -t[2], t[0]

        unsorted_matches = []
        for f, lst in grouped_candidates.items():
            max_seniority = max(c.seniority for c in lst)
            unsorted_matches.append((f, lst, max_seniority))
        all_matches = sorted(unsorted_matches, key=lambda t: (-t[2], t[0]))

        for match, candidates, _ in all_matches:
```

Replace with:

```python
        all_matches = CrossOverlapComparator.sort_matches(grouped_candidates, CROSS_OVERLAP_RULES)

        for match, candidates in all_matches:
```

**Step 2: Run the full substruct matching test suite**

```bash
PYTHONPATH=src pytest tests/core/test_substruct_matching.py -q
```

Expected: same pass/fail count as before this change (no regressions introduced by this refactor).

**Step 3: Run all comparator tests**

```bash
PYTHONPATH=src pytest tests/core/test_cross_overlap_comparator.py -v
```

Expected: `2 passed`

**Step 4: Commit**

```bash
git add src/core/substruct_matcher.py
git commit -m "refactor: replace seniority sort with CrossOverlapComparator.sort_matches"
```
