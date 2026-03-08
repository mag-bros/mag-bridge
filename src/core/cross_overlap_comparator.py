from src.constants.bond_types import OverlapGroup


class CrossOverlapComparator:
    """Stateless comparator for cross-overlap formula hierarchies using dependency injection."""

    @staticmethod
    def is_higher_priority(
        formula1: str,
        formula2: str,
        group: OverlapGroup,
        rules: dict[OverlapGroup, dict],
    ) -> bool:
        """Check if formula1 has higher priority than formula2 in the hierarchy."""
        hierarchy: tuple[str, ...] = rules[group]["order"]
        try:
            is_higher = hierarchy.index(formula1) < hierarchy.index(formula2)
            return is_higher
        except ValueError:
            # handle IRRELEVANT
            return False

    @staticmethod
    def sort_matches(grouped_candidates: dict[str, list], rules: dict) -> list[tuple[str, list]]:
        """Sort grouped candidates by group priority then intra-group order."""

        def _sort_key(item: tuple[str, list]) -> tuple[int, int]:
            formula, cands = item
            group = OverlapGroup.DEFAULT if cands[0].cross_overlap_group is None else cands[0].cross_overlap_group
            rule = rules.get(group, rules[OverlapGroup.DEFAULT])
            order = rule["order"]
            idx = order.index(formula) if isinstance(order, tuple) and formula in order else (len(order) if isinstance(order, tuple) else 0)
            return (-rule["group_prio"], idx)

        return sorted(grouped_candidates.items(), key=_sort_key)
