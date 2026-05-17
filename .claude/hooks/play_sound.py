"""Cross-platform sound player for Claude Code hooks.

macOS:   afplay (built-in)
Linux:   paplay → PulseAudio TCP to host (set PULSE_SERVER env var)
Windows: winsound (stdlib)

Fallback: terminal bell (\a) — always silent-safe, never errors.
"""

import os
import platform
import subprocess
import sys


def play(path: str) -> None:
    system = platform.system()

    if system == "Darwin":
        subprocess.run(["afplay", path], capture_output=True)

    elif system == "Windows":
        import winsound  # type: ignore[import-not-found]

        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)  # type: ignore[reportAttributeAccessIssue]

    else:
        server = os.environ.get("PULSE_SERVER", "tcp:host.docker.internal:4713")
        result = subprocess.run(["paplay", "--server", server, path], capture_output=True)
        if result.returncode != 0:
            print("\a", end="", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        play(sys.argv[1])
