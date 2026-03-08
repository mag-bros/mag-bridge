import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import click


def run_cmd(
    cmd: List[str],
    cwd: Path | None = None,
    capture: bool = True,
    env: Dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            cmd, cwd=cwd, text=True, capture_output=capture, check=True, env=env
        )
    except subprocess.CalledProcessError as e:
        click.secho(f"\nCOMMAND FAILED: {' '.join(cmd)}", fg="red", bold=True)
        if capture:
            click.secho(f"STDOUT: {e.stdout}", fg="yellow")
            click.secho(f"STDERR: {e.stderr}", fg="red")
        raise click.Abort()


def get_commit_hash(ref: str, cwd: Path) -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", ref],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=True,
        )
        return res.stdout.strip()
    except subprocess.CalledProcessError:
        return ref


def parse_report(json_path: Path) -> Dict[str, Dict[str, Any]]:
    if not json_path.exists():
        return {}
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = {}
    for test in data.get("tests", []):
        raw_nodeid = test.get("nodeid", "")
        # Strip file path to make diffing immune to files moving between directories
        nodeid = raw_nodeid.split("::")[-1] if "::" in raw_nodeid else raw_nodeid

        outcome = test.get("outcome", "unknown")
        err_msg = ""
        if outcome == "failed":
            call_info = test.get("call", {})
            crash = call_info.get("crash", {})
            err_msg = (
                crash.get("message", "Unknown error").splitlines()[0]
                if crash
                else "Failure"
            )
        results[nodeid] = {"outcome": outcome, "error": err_msg}
    return results


def generate_markdown(
    target: str,
    baseline_target: str,
    baseline_ref: str,
    current_ref: str,
    baseline_res: Dict[str, Dict[str, Any]],
    current_res: Dict[str, Dict[str, Any]],
    output_path: Path,
) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_nodes = set(baseline_res.keys()).union(current_res.keys())

    regressions, fixes, consistent_fails, new_fails = [], [], [], []
    b_pass = b_fail = b_skip = c_pass = c_fail = c_skip = 0
    b_total = len(baseline_res)
    c_total = len(current_res)

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
            consistent_fails.append((node, current_res[node]["error"]))
        elif b_out == "missing" and c_out == "failed":
            new_fails.append((node, current_res[node]["error"]))

    md = [
        "# TEST_DRIFT Report\n",
        "## Configuration\n",
        "| Parameter | Value |",
        "|---|---|",
        f"| **Timestamp** | `{timestamp}` |",
        f"| **Target** | `{target}` |",
    ]

    if baseline_target and baseline_target != target:
        md.append(f"| **Baseline Target** | `{baseline_target}` |")

    md.extend(
        [
            f"| **Baseline Ref** | `{baseline_ref}` |",
            f"| **Current Ref** | `{current_ref}` |\n",
            "## Summary\n",
            "| Metric | Baseline | Current | Delta |",
            "|---|---|---|---|",
            f"| **Total Tests** | {b_total} | {c_total} | {c_total - b_total:+d} |",
            f"| **Passed** | {b_pass} | {c_pass} | {c_pass - b_pass:+d} |",
            f"| **Failed** | {b_fail} | {c_fail} | {c_fail - b_fail:+d} |",
            f"| **Skipped** | {b_skip} | {c_skip} | {c_skip - b_skip:+d} |\n",
        ]
    )

    if regressions:
        md.extend(
            ["## Regressions (Passed → Failed)\n", "| Test Node | Error |", "|---|---|"]
        )
        for node, err in regressions:
            md.append(f"| `{node}` | `{err}` |")
        md.append("\n")

    if new_fails:
        md.extend(
            [
                "## New Failures (Not in Baseline)\n",
                "| Test Node | Error |",
                "|---|---|",
            ]
        )
        for node, err in new_fails:
            md.append(f"| `{node}` | `{err}` |")
        md.append("\n")

    if fixes:
        md.extend(["## Fixes (Failed → Passed)\n", "| Test Node |", "|---|"])
        for node in fixes:
            md.append(f"| `{node}` |")
        md.append("\n")

    if consistent_fails:
        md.extend(
            [
                f"## Consistently Failing ({len(consistent_fails)} tests)\n",
                "| Test Node | Error |",
                "|---|---|",
            ]
        )
        for node, err in consistent_fails:
            md.append(f"| `{node}` | `{err}` |")
        md.append("\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


@click.command()
@click.option(
    "--baseline", default="master", help="Git branch or commit to use as baseline."
)
@click.option("--target", default=".", help="Directory or file to run pytest against.")
@click.option(
    "--baseline-target",
    default=None,
    help="Fallback path for baseline if file was moved.",
)
@click.option(
    "--report", default="tests/reports/TEST_DRIFT.md", help="Output MD report path."
)
def drift(baseline: str, target: str, baseline_target: str, report: str) -> None:
    cwd = Path.cwd()
    report_path = Path(report).resolve()
    b_target = baseline_target if baseline_target else target

    current_commit = get_commit_hash("HEAD", cwd)
    baseline_commit = get_commit_hash(baseline, cwd)

    click.secho(
        f"Targeting Baseline Commit: {baseline_commit}", fg="magenta", bold=True
    )
    click.secho(f"Targeting Current Commit: {current_commit}", fg="magenta", bold=True)

    if baseline_commit == current_commit:
        click.secho(
            "WARNING: Baseline and Current resolve to the exact same git commit!",
            fg="yellow",
            bold=True,
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        worktree_path = temp_path / "baseline_worktree"
        b_json = temp_path / "baseline.json"
        c_json = temp_path / "current.json"

        b_env = os.environ.copy()
        b_env["PYTHONPATH"] = str(worktree_path)

        c_env = os.environ.copy()
        c_env["PYTHONPATH"] = str(cwd)

        click.secho(
            f"\nCreating isolated worktree for baseline '{baseline}'...", fg="cyan"
        )
        run_cmd(
            ["git", "worktree", "add", "--detach", str(worktree_path), baseline],
            cwd=cwd,
        )

        try:
            click.secho(f"\n--- Running Baseline Pytest ({b_target}) ---", fg="yellow")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    b_target,
                    "--json-report",
                    f"--json-report-file={b_json}",
                ],
                cwd=worktree_path,
                capture_output=False,
                env=b_env,
                check=False,
            )

            click.secho(f"\n--- Running Current Pytest ({target}) ---", fg="yellow")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    target,
                    "--json-report",
                    f"--json-report-file={c_json}",
                ],
                cwd=cwd,
                capture_output=False,
                env=c_env,
                check=False,
            )

            click.secho("\nAggregating results...", fg="cyan")
            b_data = parse_report(b_json)
            c_data = parse_report(c_json)

            generate_markdown(
                target,
                b_target,
                f"{baseline} ({baseline_commit})",
                f"working tree ({current_commit})",
                b_data,
                c_data,
                report_path,
            )
            click.secho(
                f"Drift report generated at: {report_path.relative_to(cwd)}",
                fg="green",
                bold=True,
            )

        finally:
            click.secho("Cleaning up isolated worktree...", fg="cyan")
            run_cmd(
                ["git", "worktree", "remove", "--force", str(worktree_path)], cwd=cwd
            )


if __name__ == "__main__":
    drift()
