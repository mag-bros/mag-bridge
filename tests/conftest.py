# conftest.py
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import pytest

MARKER = "counter_metrics"
AGGS = pytest.StashKey[dict[str, "Agg"]]()


@dataclass
class Agg:
    """Aggregates counters across parametrized cases for one logical group."""

    case_ids: set[str] = field(default_factory=set)
    hits: Counter[str] = field(default_factory=Counter)
    cases_with_key: Counter[str] = field(default_factory=Counter)

    def add(self, case_id: str, counter: Counter[str]) -> None:
        """Add metrics for a single case, guarding against double counting."""
        if case_id in self.case_ids:
            raise RuntimeError(
                f"counter_metrics_sink called more than once for: {case_id}"
            )
        self.case_ids.add(case_id)
        self.hits.update(counter)
        self.cases_with_key.update({k: 1 for k in counter.keys()})


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register CLI option for writing derived metrics to JSON."""
    parser.getgroup("counter-metrics").addoption(
        "--counter-metrics-json",
        action="store",
        default=None,
        metavar="PATH",
        help="Write derived counter metrics (JSON) to PATH.",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register marker and initialize stash storage."""
    config.addinivalue_line(
        "markers",
        f"{MARKER}(group=str): aggregate Counter[str] for this marked test group",
    )
    config.stash[AGGS] = {}


@pytest.fixture
def counter_metrics_sink(
    request: pytest.FixtureRequest,
) -> Callable[[Counter[str]], None]:
    """Return a sink function that aggregates a Counter[str] for the marked group."""
    m = request.node.get_closest_marker(MARKER)
    if m is None:
        raise RuntimeError(
            "counter_metrics_sink used without @pytest.mark.counter_metrics(group='...')"
        )

    group = m.kwargs.get("group")
    if not isinstance(group, str) or not group.strip():
        raise RuntimeError(
            "Invalid marker usage; expected @pytest.mark.counter_metrics(group='...')"
        )

    aggs = request.config.stash[AGGS]
    agg = aggs.setdefault(group, Agg())
    case_id = request.node.nodeid  # unique per parametrized instance

    def sink(counter: Counter[str]) -> None:
        """Aggregate metrics for the current test case."""
        agg.add(case_id, counter)

    return sink


def _derive(agg: Agg) -> dict[str, dict[str, float]]:
    """Compute per-key derived percentages from the aggregated counters."""
    total_hits = sum(agg.hits.values())
    total_cases = len(agg.case_ids) or 1
    return {
        k: {
            "hit_share_pct": (cnt / total_hits * 100.0) if total_hits else 0.0,
            "case_presence_pct": (agg.cases_with_key[k] / total_cases * 100.0),
        }
        for k, cnt in agg.hits.items()
    }


def pytest_terminal_summary(
    terminalreporter: pytest.TerminalReporter, exitstatus: int, config: pytest.Config
) -> None:
    """Print a concise derived-metrics summary for marked groups only."""
    aggs = config.stash.get(AGGS, {})
    if not aggs:
        return

    terminalreporter.section("Counter metrics (derived, marked groups only)")
    for group in sorted(aggs):
        agg = aggs[group]
        cases = len(agg.case_ids)
        total_hits = sum(agg.hits.values())
        terminalreporter.write_line(
            f"{group}: cases={cases} distinct_keys={len(agg.hits)} total_hits={total_hits}"
        )

        derived = _derive(agg)
        for key, cnt in agg.hits.most_common(15):
            d = derived[key]
            terminalreporter.write_line(
                f"  {key}: hits={cnt}, hit_share={d['hit_share_pct']:.1f}%, "
                f"case_presence={d['case_presence_pct']:.1f}%"
            )

    out_path = config.getoption("--counter-metrics-json")
    if out_path:
        _write_json(out_path, aggs)


def _write_json(out_path: str, aggs: dict[str, Agg]) -> None:
    """Write derived metrics for all marked groups to a JSON file."""
    payload = {
        group: {
            "cases": len(agg.case_ids),
            "total_hits": sum(agg.hits.values()),
            "derived": _derive(agg),
        }
        for group, agg in aggs.items()
    }
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
