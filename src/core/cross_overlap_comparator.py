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
            order_index = order.index(formula) if isinstance(order, tuple) and formula in order else len(order) if isinstance(order, tuple) else 0
            return (-group_prio, order_index)

        return sorted(grouped_candidates.items(), key=_sort_key)
