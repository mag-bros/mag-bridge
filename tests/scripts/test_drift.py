import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import click


def run_cmd(cmd: List[str], cwd: Path | None = None, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=capture, check=False)


def get_current_commit() -> str:
    res = run_cmd(["git", "rev-parse", "--short", "HEAD"])
    return res.stdout.strip()


def parse_report(json_path: Path) -> Dict[str, Dict[str, Any]]:
    if not json_path.exists():
        return {}
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = {}
    for test in data.get("tests", []):
        nodeid = test.get("nodeid", "")
        outcome = test.get("outcome", "unknown")
        err_msg = ""
        if outcome == "failed":
            call_info = test.get("call", {})
            crash = call_info.get("crash", {})
            err_msg = crash.get("message", "Unknown error").splitlines()[0] if crash else "Failure"
        results[nodeid] = {"outcome": outcome, "error": err_msg}
    return results


def generate_markdown(
    target: str,
    baseline_ref: str,
    current_ref: str,
    baseline_res: Dict[str, Dict[str, Any]],
    current_res: Dict[str, Dict[str, Any]],
    output_path: Path,
) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    all_nodes = set(baseline_res.keys()).union(current_res.keys())

    regressions = []
    fixes = []
    consistent_fails = []

    b_pass = b_fail = b_skip = c_pass = c_fail = c_skip = 0

    for node in sorted(all_nodes):
        b_out = baseline_res.get(node, {}).get("outcome", "missing")
        c_out = current_res.get(node, {}).get("outcome", "missing")

        if b_out == "passed":
            b_pass += 1
        elif b_out == "failed":
            b_fail += 1
        elif b_out == "skipped":
            b_skip += 1

        if c_out == "passed":
            c_pass += 1
        elif c_out == "failed":
            c_fail += 1
        elif c_out == "skipped":
            c_skip += 1

        if b_out == "passed" and c_out == "failed":
            regressions.append((node, current_res[node]["error"]))
        elif b_out == "failed" and c_out == "passed":
            fixes.append(node)
        elif b_out == "failed" and c_out == "failed":
            consistent_fails.append(node)

    md = [
        f"# TEST_DRIFT — `{target}`\n",
        f"**Timestamp:** {timestamp}",
        f"**Baseline:** `{baseline_ref}`",
        f"**Current:** `{current_ref}`\n",
        "## Summary\n",
        "| Metric | Baseline | Current | Delta |",
        "|---|---|---|---|",
        f"| Passed | {b_pass} | {c_pass} | {c_pass - b_pass:+d} |",
        f"| Failed | {b_fail} | {c_fail} | {c_fail - b_fail:+d} |",
        f"| Skipped | {b_skip} | {c_skip} | {c_skip - b_skip:+d} |\n",
    ]

    if regressions:
        md.extend(["## Regressions (Passed → Failed)\n", "| Node ID | Error / Assertion | Severity |", "|---|---|---|"])
        for node, err in regressions:
            md.append(f"| `{node}` | `{err}` | HIGH |")
        md.append("\n")

    if fixes:
        md.extend(["## Fixes (Failed → Passed)\n", "| Node ID |", "|---|"])
        for node in fixes:
            md.append(f"| `{node}` |")
        md.append("\n")

    if consistent_fails:
        md.extend([f"## Consistently Failing ({len(consistent_fails)} tests)\n", "| Node ID |", "|---|"])
        for node in consistent_fails:
            md.append(f"| `{node}` |")
        md.append("\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


@click.command()
@click.option("--baseline", default="master", help="Git branch or commit to use as baseline.")
@click.option("--target", default=".", help="Directory or file to run pytest against.")
@click.option("--report", default="tests/reports/TEST_DRIFT.md", help="Output MD report path.")
def drift(baseline: str, target: str, report: str) -> None:
    cwd = Path.cwd()
    current_commit = get_current_commit()
    report_path = Path(report).resolve()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        worktree_path = temp_path / "baseline_worktree"
        b_json = temp_path / "baseline.json"
        c_json = temp_path / "current.json"

        click.secho(f"Creating isolated worktree for baseline '{baseline}'...", fg="cyan")
        run_cmd(["git", "worktree", "add", "--detach", str(worktree_path), baseline], cwd=cwd)

        try:
            click.secho("\n--- Running Baseline Pytest ---", fg="yellow")
            run_cmd(["pytest", target, "--json-report", f"--json-report-file={b_json}"], cwd=worktree_path, capture=False)

            click.secho("\n--- Running Current Pytest ---", fg="yellow")
            run_cmd(["pytest", target, "--json-report", f"--json-report-file={c_json}"], cwd=cwd, capture=False)

            click.secho("\nAggregating results...", fg="cyan")
            b_data = parse_report(b_json)
            c_data = parse_report(c_json)

            generate_markdown(target, baseline, f"working tree ({current_commit})", b_data, c_data, report_path)
            click.secho(f"Drift report generated at: {report_path.relative_to(cwd)}", fg="green", bold=True)

        finally:
            click.secho("Cleaning up isolated worktree...", fg="cyan")
            run_cmd(["git", "worktree", "remove", "--force", str(worktree_path)], cwd=cwd)


if __name__ == "__main__":
    drift()
