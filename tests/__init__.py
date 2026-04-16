from pathlib import Path

from src import ROOT_DIR

COVERAGE_REPORTS_DIR: Path = ROOT_DIR.joinpath("tests/reports")
COVERAGE_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
