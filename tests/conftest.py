# conftest.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pytest


@dataclass(frozen=True)
class BondCoverageReport:
    """Bond coverage report payload produced by a single test."""

    md_path: str
    md_content: str


BOND_COVERAGE_REPORT = pytest.StashKey[BondCoverageReport | None]()


def pytest_configure(config: pytest.Config) -> None:
    """Register marker and initialize stash slot."""
    config.addinivalue_line(
        "markers", "bond_coverage_report: produces bond coverage report artifacts"
    )
    config.stash[BOND_COVERAGE_REPORT] = None


@pytest.fixture
def bond_coverage_report_publish(
    request: pytest.FixtureRequest,
) -> Callable[[str, str], None]:
    """Store report metadata in the pytest stash (no terminal output)."""

    def publish(md_path: str, md_content: str) -> None:
        request.config.stash[BOND_COVERAGE_REPORT] = BondCoverageReport(
            md_path=md_path,
            md_content=md_content,
        )

    return publish
