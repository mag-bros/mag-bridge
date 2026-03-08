import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import click


def run_cmd(cmd: List[str], cwd: Path | None = None, env: Dict[str, str] | None = None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True, env=env)
    except subprocess.CalledProcessError as e:
        click.secho(f"\nFATAL: {' '.join(cmd)}\n{e.stderr}", fg="red")
        raise click.Abort()


def get_commit(ref: str, cwd: Path) -> str:
    res = subprocess.run(["git", "rev-parse", "--short", ref], cwd=cwd, text=True, capture_output=True)
    return res.stdout.strip() if res.returncode == 0 else ref


def parse_report(json_path: Path) -> Dict[str, Dict[str, Any]]:
    if not json_path.exists():
        return {}
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = {}
    for test in data.get("tests", []):
        raw_id = test.get("nodeid", "")
        # Extract 'test_func[<ID>]' to handle path migrations
        match = re.search(r"(\w+\[<\d+>)", raw_id)
        nodeid = match.group(1) + "]" if match else raw_id.split("::")[-1]

        outcome = test.get("outcome", "unknown")
        err = ""
        if outcome == "failed":
            crash = test.get("call", {}).get("crash", {})
            err = crash.get("message", "Failure").splitlines()[0]
        results[nodeid] = {"outcome": outcome, "error": err}
    return results


def generate_markdown(target, b_ref, c_ref, b_res, c_res, out_path) -> None:
    # Natural sort fix: sorts numerically by the ID inside the brackets
    all_nodes = sorted(set(b_res.keys()).union(c_res.keys()), key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", x)])
    regressions, fixes, fails, news = [], [], [], []
    s = {"bp": 0, "bf": 0, "bs": 0, "cp": 0, "cf": 0, "cs": 0}

    for n in all_nodes:
        bo, co = b_res.get(n, {}).get("outcome", "missing"), c_res.get(n, {}).get("outcome", "missing")
        if bo == "passed":
            s["bp"] += 1
        elif bo == "failed":
            s["bf"] += 1
        elif bo == "skipped":
            s["bs"] += 1

        if co == "passed":
            s["cp"] += 1
        elif co == "failed":
            s["cf"] += 1
        elif co == "skipped":
            s["cs"] += 1

        if bo == "passed" and co == "failed":
            regressions.append((n, c_res[n]["error"]))
        elif bo == "failed" and co == "passed":
            fixes.append(n)
        elif bo == "failed" and co == "failed":
            fails.append((n, c_res[n]["error"]))
        elif bo == "missing" and co == "failed":
            news.append((n, c_res[n]["error"]))

    def trend(d, inv=False):
        if d == 0:
            return "—"
        icon = "📈" if (d > 0 if not inv else d < 0) else "📉"
        return f"{icon} {d:+d}"

    md = [
        "# TEST_DRIFT Report\n",
        "## ⚙️ Configuration",
        f"- **Target:** `{target}`",
        f"- **Baseline:** branch `{b_ref}`",
        f"- **Current:** local changes ({c_ref})\n",
        "## 📊 Summary\n",
        "| Metric | Baseline | Current | Delta | Trend |",
        "|---|---|---|---|---|",
        f"| **Total** | {len(b_res)} | {len(c_res)} | {len(c_res) - len(b_res):+d} | {trend(len(c_res) - len(b_res))} |",
        f"| **Passed** | **{s['bp']}/{len(b_res)}** | **{s['cp']}/{len(c_res)}** | {s['cp'] - s['bp']:+d} | {trend(s['cp'] - s['bp'])} |",
        f"| **Failed** | {s['bf']} | {s['cf']} | {s['cf'] - s['bf']:+d} | {trend(s['cf'] - s['bf'], True)} |",
        f"| **Skipped** | {s['bs']} | {s['cs']} | {s['cs'] - s['bs']:+d} | — |\n",
        "## 👎 Regressions (Passed → Failed)\n",
    ]

    if regressions:
        md.extend(["| Test Node | Error |", "|---|---|"])
        md.extend([f"| `{n}` | `{e}` |" for n, e in regressions])
    else:
        md.append("There were no tests that transitioned from passed to failed.\n")

    md.append("\n## 👏 Fixes (Failed → Passed)\n")
    if fixes:
        md.extend(["| Test Node | Status |", "|---|---|"])
        md.extend([f"| `{n}` | FIXED |" for n in fixes])
    else:
        md.append("No previously failing tests were fixed.\n")

    if news:
        md.append("\n## 🆕 New Failures\n")
        md.extend(["| Test Node | Error |", "|---|---|"])
        md.extend([f"| `{n}` | `{e}` |" for n, e in news])

    if fails:
        md.append(f"\n## 🔄 Consistently Failing ({len(fails)})\n")
        md.extend(["| Test Node | Error |", "|---|---|"])
        md.extend([f"| `{n}` | `{e}` |" for n, e in fails])

    md.append(f"\n\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(md))


@click.command()
@click.option("--baseline", default="master")
@click.option("--target", default=".")
@click.option("--baseline-target", default=None)
@click.option("--report", default="tests/reports/TEST_DRIFT.md")
def drift(baseline, target, baseline_target, report):
    cwd = Path.cwd()
    report_path = Path(report).resolve()
    bt = baseline_target or target
    ch, bh = get_commit("HEAD", cwd), get_commit(baseline, cwd)

    with tempfile.TemporaryDirectory() as td:
        wt = Path(td) / "wt"
        bj, cj = Path(td) / "b.json", Path(td) / "c.json"

        run_cmd(["git", "worktree", "add", "--detach", str(wt), baseline], cwd=cwd)
        try:
            b_env, c_env = os.environ.copy(), os.environ.copy()
            b_env["PYTHONPATH"], c_env["PYTHONPATH"] = str(wt), str(cwd)

            # Quiet flags: -q (minimal headers), --tb=no (no tracebacks), --no-summary (no footer stats)
            py_cmd = [sys.executable, "-m", "pytest", "-q", "--tb=no", "--no-summary", "--no-header", "--json-report"]

            # --- Phase 1: Baseline ---
            if os.getenv("GITHUB_ACTIONS") == "true":
                print("::group::🔍 Running Baseline Pytest (Branch: " + baseline + ")")

            click.secho("\n--- Running Baseline Pytest ---", fg="yellow")
            subprocess.run(py_cmd + [bt, f"--json-report-file={bj}"], cwd=wt, env=b_env, check=False)

            if os.getenv("GITHUB_ACTIONS") == "true":
                print("::endgroup::")

            # --- Phase 2: Current ---
            if os.getenv("GITHUB_ACTIONS") == "true":
                print("::group::🚀 Running Current Pytest (Local Changes)")

            click.secho("\n--- Running Current Pytest ---", fg="yellow")
            subprocess.run(py_cmd + [target, f"--json-report-file={cj}"], cwd=cwd, env=c_env, check=False)

            if os.getenv("GITHUB_ACTIONS") == "true":
                print("::endgroup::")

            # --- Phase 3: Aggregation ---
            generate_markdown(target, f"branch `{baseline}` ({bh})", f"local changes ({ch})", parse_report(bj), parse_report(cj), report_path)
            click.secho(f"\nDrift report generated: {report_path.relative_to(cwd)}", fg="green", bold=True)

        finally:
            run_cmd(["git", "worktree", "remove", "--force", str(wt)], cwd=cwd)


if __name__ == "__main__":
    drift()
