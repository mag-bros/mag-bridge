import json
from collections import Counter
from pathlib import Path

import pytest

from src.constants.bond_types import RELEVANT_BOND_TYPES
from src.core.substruct_matcher import MBSubstructMatcher
from src.loader import MBLoader
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
    counts = Counter()
    for smt in SUBSTRUCT_MATCH_TESTS:
        counts.update(smt.expected_matches.keys())

    expected_formulas = {bt.formula for bt in RELEVANT_BOND_TYPES}
    found_formulas = set(counts.keys())

    missing = expected_formulas - found_formulas
    # assert not missing, f"Missing ({len(missing)}): {sorted(missing)}"

    total_tests = len(SUBSTRUCT_MATCH_TESTS)

    # Presence-per-test percentage (used only for the table)
    tests_with_formula_pct = {
        f: (counts.get(f, 0) / total_tests * 100.0) for f in expected_formulas
    }

    # Sort from least present -> most present
    ranked = sorted(expected_formulas, key=lambda f: (counts.get(f, 0), f))

    report_dir = Path(str(request.config.rootpath)) / "tests" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = report_dir / "bondtype_coverage.json"
    md_path = report_dir / "bondtype_coverage.md"

    # Global coverage numbers (as requested)
    all_relevant = len(RELEVANT_BOND_TYPES)
    discovered_unique = len(
        counts
    )  # <-- "count is len(count)" (distinct formulas in tests)

    payload = {
        "metric": "tests_with_formula_pct",
        "coverage": {
            "discovered_unique_formulas": discovered_unique,
            "relevant_bond_types_total": all_relevant,
            "missing_relevant_formulas": sorted(missing),
        },
        "items": [
            {
                "formula": f,
                "tests_count": int(counts.get(f, 0)),
                "tests_pct": round(tests_with_formula_pct[f], 3),
            }
            for f in ranked
        ],
    }
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )

    ok = not missing and discovered_unique == all_relevant

    lines = [
        "# BondType Substruct Matching Tests Coverage",
        "",
        f"- Status {'✅' if ok else '❌'} [{discovered_unique}/{all_relevant}]",
    ]
    if missing:
        lines += [
            f"## Missing [{len(missing)}]",
            ", ".join(f"`{m}`" for m in sorted(missing)),
        ]

    lines += [
        "",
        "| formula | tests_count | tests_pct |",
        "|---|---:|---:|",
    ]
    for f in ranked:
        lines.append(
            f"| `{f}` | {counts.get(f, 0)} | {tests_with_formula_pct[f]:.2f}% |"
        )

    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")

    bond_coverage_report_publish(str(md_path), md_text)
