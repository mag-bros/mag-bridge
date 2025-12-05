#!/usr/bin/env python3
import glob
import os
import sys
from dataclasses import dataclass

from github.scripts.notify import send_discord_message


@dataclass
class JobStatus:
    label: str
    status: str
    duration: int


def read_status_file(path: str) -> JobStatus | None:
    raw = open(path, encoding="utf-8").read().strip()
    if not raw:
        print(f"Empty status file: {path}")
        return None

    parts = raw.split(",", 2)
    if len(parts) != 3:
        print(f"Unexpected format in {path}: {raw!r}")
        return None

    label, status, duration_str = parts
    try:
        duration = int(duration_str)
    except ValueError:
        print(f"Non-integer duration in {path}: {duration_str!r}")
        duration = 0

    return JobStatus(label=label, status=status, duration=duration)


def append_lines(path: str | None, lines: list[str]) -> None:
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(line)
            if not line.endswith("\n"):
                f.write("\n")


def format_summary(success: int, failure: int, total: int, avg_duration: int) -> str:
    return (
        "Matrix build summary\n"
        f"- Total runs: {total}\n"
        f"- Success: {success}\n"
        f"- Failure / cancelled: {failure}\n"
        f"- Average duration (all runs): {avg_duration}s"
    )


def main() -> int:
    files = sorted(glob.glob("build-status-*.txt"))

    github_summary = os.environ.get("GITHUB_STEP_SUMMARY")

    if not files:
        print("No build-status-*.txt artifacts found.")
        summary_text = format_summary(
            success=0,
            failure=0,
            total=0,
            avg_duration=0,
        )
        print(summary_text)
        if github_summary:
            append_lines(
                github_summary,
                [
                    "## Matrix build summary",
                    "",
                    "*No build-status-*.txt artifacts found.*",
                ],
            )
        send_notification(summary_text)
        return 1

    print(f"Collected {len(files)} status files:")
    for path in files:
        print(f" - {path}")

    statuses: list[JobStatus] = []
    for path in files:
        js = read_status_file(path)
        if js is not None:
            statuses.append(js)

    total = len(statuses)
    if total == 0:
        print("No valid status entries parsed.")
        summary_text = format_summary(
            success=0,
            failure=0,
            total=0,
            avg_duration=0,
        )
        print(summary_text)
        if github_summary:
            append_lines(
                github_summary,
                [
                    "## Matrix build summary",
                    "",
                    "*No valid status entries parsed.*",
                ],
            )
        send_notification(summary_text)
        return 1

    success = sum(1 for s in statuses if s.status == "success")
    failure = sum(1 for s in statuses if s.status in ("failure", "cancelled"))
    sum_duration = sum(s.duration for s in statuses)
    avg_duration = sum_duration // total if total > 0 else 0

    print(
        f"Matrix status: {success} success / {total} total "
        f"(failures: {failure}), avg duration: {avg_duration}s"
    )

    summary_text = format_summary(
        success=success,
        failure=failure,
        total=total,
        avg_duration=avg_duration,
    )

    if github_summary:
        append_lines(
            github_summary,
            [
                "## Matrix build summary",
                "",
                f"- Total runs: **{total}**",
                f"- Success: **{success}**",
                f"- Failure / cancelled: **{failure}**",
                f"- Average duration (all runs): **{avg_duration}s**",
                "",
                "Files:",
                "```text",
                *files,
                "```",
            ],
        )

    send_notification(message={})  # TODO::
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
