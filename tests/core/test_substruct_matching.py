from collections import Counter

import pytest

from src.constants.bond_types import RELEVANT_BOND_TYPES
from src.core.substruct_matcher import MBSubstructMatcher
from src.loader import MBLoader
from tests import COVERAGE_REPORTS_DIR
from tests.data.substruct_matching_tests import (
    SUBSTRUCT_MATCH_TESTS,
    SubstructMatchTest,
)


@pytest.mark.parametrize(
    "substruct_match_test",
    SUBSTRUCT_MATCH_TESTS,
    ids=lambda p: f"<{p.id}> {p.SMILES}",
)
def test_substruct_matches(substruct_match_test: SubstructMatchTest) -> None:
    """Test if a molecules matches all expected substructures - Bond Types."""

    if substruct_match_test.skip_test:
        pytest.skip(
            reason="skip this test due to underlying RDKit logical discrepancies"
        )

    mol = MBLoader.MolFromSmiles(smiles=substruct_match_test.SMILES)

    # Actual test: GetMatches()
    result = MBSubstructMatcher.GetMatches(mol=mol)

    def normalize_counter_keys(c: Counter[str]) -> Counter[str]:
        return Counter({k.rstrip(":").strip(): v for k, v in c.items()})

    assert normalize_counter_keys(
        substruct_match_test.expected_matches
    ) == normalize_counter_keys(result.matchesCounter)

    # Internal consistency check: counter must match final hit lists
    assert sum(result.matchesCounter.values()) == sum(
        len(hits) for hits in result.final_hits_by_formula.values()
    )


def test_smiles_uniqueness() -> None:
    counter = Counter([smt.SMILES for smt in SUBSTRUCT_MATCH_TESTS])
    for smiles, count in counter.items():
        assert count == 1, f"SMILES: '{smiles}' not unique"


@pytest.mark.bond_coverage_report
def test_bond_type_coverage(request, bond_coverage_report_publish) -> None:
    covered = Counter()
    for smt in SUBSTRUCT_MATCH_TESTS:
        covered.update(smt.expected_matches.keys())

    expected = {bt.formula for bt in RELEVANT_BOND_TYPES if bt.dummy_ring == False}
    total_usages: int = sum([val for val in covered.values()])
    found_unique = set(covered.keys())

    # Derived metrics
    missing = expected - found_unique
    typos = found_unique - expected  # most likely typos
    intersection = expected.intersection(found_unique)
    presence = {f: (covered.get(f, 0) / total_usages * 100.0) for f in expected}
    ranked = sorted(expected, key=lambda f: (covered.get(f, 0), f))
    total_bond_types = len(expected)  # excluded dummy rings
    total_covered = len(intersection)

    # Markdown generation
    md_path = COVERAGE_REPORTS_DIR.joinpath("bondtype_coverage.md")
    status_ok = not missing and not typos and total_covered == total_bond_types

    md_out: list[str] = [
        "## BondType Substruct Matching Tests Coverage",
        "",
        f"- {'✅' if status_ok else '❌'} Status:  {total_covered}/{total_bond_types}",
    ]
    if missing:
        md_out += [
            f"## Missing Bond Types: {len(missing)}",
            ", ".join(f"`{m}`" for m in sorted(missing)),
        ]
    if typos:
        md_out += [
            f"## Typos Found (most likely): {len(typos)}",
            ", ".join(f"`{m}`" for m in sorted(typos)),
        ]

    md_out += [
        "",
        "| Bond Type Formula | Absolute Usages Count | Weight in usages [%] |",
        "|---|---:|---:|",
    ]
    for f in ranked:
        md_out.append(f"| `{f}` | {covered.get(f, 0)} | {presence[f]:.2f}% |")

    md_text = "\n".join(md_out) + "\n"
    md_path.write_text(md_text, encoding="utf-8")

    # Publish md_out report to pytest
    bond_coverage_report_publish(str(md_path), md_text)

    # actual test
    assert status_ok, f"Missing ({len(missing)}): {sorted(missing)}"
