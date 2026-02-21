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
