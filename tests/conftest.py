# conftest.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, cast

import pytest


@dataclass(frozen=True)
class BondCoverageReport:
    """Data needed to print the bond coverage report."""

    md_path: str
    md_content: str


BOND_COVERAGE_REPORT = pytest.StashKey[BondCoverageReport | None]()


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "bond_coverage_report: emit bond coverage report at end"
    )
    config.stash[BOND_COVERAGE_REPORT] = None


@pytest.fixture
def bond_coverage_report_publish(
    request: pytest.FixtureRequest,
) -> Callable[[str, str], None]:
    """Publish the bond coverage report data for end-of-run printing."""

    def publish(md_path: str, md_content: str) -> None:
        request.config.stash[BOND_COVERAGE_REPORT] = BondCoverageReport(
            md_path=md_path,
            md_content=md_content,
        )

    return publish


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config: pytest.Config) -> None:
    tr_plugin = config.pluginmanager.getplugin("terminalreporter")
    if tr_plugin is None:
        return
    tr = cast(pytest.TerminalReporter, tr_plugin)

    report = config.stash.get(BOND_COVERAGE_REPORT, None)
    if report is None:
        return

    # extra summary
    # tr.write_line("=" * 80)
    # tr.write_line("Bond type coverage report")
    # tr.write_line("=" * 80)
    # tr.write_line(f"Markdown report: {report.md_path}")
    # tr.write_line("")
    # tr.write(report.md_content)
    # tr.write_line("")
