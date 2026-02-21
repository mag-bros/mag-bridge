from src.constants.bond_types import CrossOverlapGroup


class CrossOverlapComparator:
    """Stateless comparator for cross-overlap formula hierarchies using dependency injection."""

    @staticmethod
    def _parse(rule_string: str) -> tuple[str, ...]:
        """Parse quoted formulas from rule string separated by ' > ' delimiters."""
        parts = rule_string.split(" > ")
        return tuple(part.strip().strip('"') for part in parts)

    @staticmethod
    def is_higher_priority(
        formula1: str,
        formula2: str,
        group: CrossOverlapGroup,
        rules: dict[CrossOverlapGroup, str],
    ) -> bool:
        """Check if formula1 has higher priority than formula2 in the hierarchy."""
        hierarchy = CrossOverlapComparator._parse(rules[group])
        try:
            return hierarchy.index(formula1) < hierarchy.index(formula2)
        except ValueError:
            return False
