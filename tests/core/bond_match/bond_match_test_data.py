from collections import Counter
from dataclasses import dataclass, field
from typing import Counter, Optional


@dataclass(frozen=True)
class BondMatchTestCase:
    """
    Defines a single bond-matching test case.

    SMILES:
        SMILES string of the test molecule.

    expected_matches:
        Expected number of occurrences for each bond type,
        expressed as a Counter keyed by bond formula.

        Example:
            Counter({
                "C=C": 2,   # two carbon–carbon double bonds
                "C-Cl": 3,  # three carbon–chlorine single bonds
            })

        Each value represents how many substructure matches
        should be found for the given bond type in the molecule.

    description:
        Optional free-text description of the test case
        (e.g. structural features, edge cases, or notes).
    """

    SMILES: str
    expected_matches: Counter[str] = field(default_factory=Counter)
    description: Optional[str] = ""


BOND_MATCH_TEST_CASES: list[BondMatchTestCase] = [
    BondMatchTestCase(
        SMILES="ClC=CC(Cl)C=CCl",
        expected_matches=Counter({"C=C": 2, "C-Cl": 3}),
        description="",
    ),
    BondMatchTestCase(
        SMILES="C=CCC=C",
        expected_matches=Counter({"CH2=CH-CH2-": 2}),
        description="",
    ),
]
