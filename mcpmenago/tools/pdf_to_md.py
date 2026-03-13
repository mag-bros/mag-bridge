#!/usr/bin/env python3
"""MinerU PDF to Markdown converter."""

import argparse
import fcntl
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import MD_DIR, PDF_DIR

_LOCK_PATH = Path(tempfile.gettempdir()) / "mineru.lock"
_lock_fd = None


def _memory_pressure() -> str:
    """macOS memory pressure level via kern.memorystatus_vm_pressure_level.

    Returns 'normal', 'warning', 'critical', or 'unknown'.
    Matches Activity Monitor's green/yellow/red pressure chart.
    Single read-only sysctl call, <1ms.
    """
    try:
        out = subprocess.check_output(
            ["sysctl", "-n", "kern.memorystatus_vm_pressure_level"],
            text=True,
            timeout=3,
        )
        return {1: "normal", 2: "warning", 4: "critical"}.get(int(out.strip()), "unknown")
    except Exception:
        return "unknown"


def _acquire_lock() -> None:
    """Block until this process holds the exclusive MinerU conversion lock."""
    global _lock_fd
    _lock_fd = open(_LOCK_PATH, "w")
    try:
        fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("[MinerU] Another conversion is running — waiting for it to finish...")
        fcntl.flock(_lock_fd, fcntl.LOCK_EX)


def _release_lock() -> None:
    global _lock_fd
    if _lock_fd:
        fcntl.flock(_lock_fd, fcntl.LOCK_UN)
        _lock_fd.close()
        _lock_fd = None


def restructure_directory(directory):
    transforms = {re.compile(r".*_layout\.pdf$"): "index-layout.pdf", re.compile(r".*\.md$"): "index.md"}

    keep_dirs = {"images"}
    valid_targets = set(transforms.values())

    if not os.path.exists(directory):
        return

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isdir(file_path):
            if filename not in keep_dirs:
                pass
            continue

        if filename in valid_targets:
            continue

        target_name = next((name for pat, name in transforms.items() if pat.match(filename)), None)

        if target_name:
            os.rename(file_path, os.path.join(directory, target_name))
        else:
            os.remove(file_path)


def find_pdfs(input_path: Path) -> list[Path]:
    """Find all PDF files in directory, excluding output directories."""
    if not input_path.is_dir():
        print(f"Error: {input_path} does not exist or is not a directory.")
        sys.exit(1)

    pdfs = []
    for pdf in sorted(input_path.rglob("*.pdf")):
        if MD_DIR in pdf.parents:
            continue
        pdfs.append(pdf)

    return pdfs


def resolve_output_dir(pdf_path: Path) -> Path:
    """Map input PDF to its MinerU output parent directory.

    MinerU creates <stem>/hybrid_auto/ inside -o directory, so we return
    the category directory. Final structure:
        research/md/<category>/<stem>/hybrid_auto/<stem>.md
    """
    try:
        rel_path = pdf_path.relative_to(PDF_DIR)
        return MD_DIR / rel_path.parent
    except ValueError:
        return MD_DIR


def show_preview_table(pdfs: list[Path]) -> None:
    """Show aligned preview table of input → output mappings."""
    pairs = []
    for pdf in pdfs:
        output = resolve_output_dir(pdf) / pdf.stem / "hybrid_auto"
        pairs.append((pdf, output))

    all_paths = [p for pair in pairs for p in pair]
    common = Path(os.path.commonpath([str(p) for p in all_paths]))

    print(f"Common Root: {common}/\n")

    inputs = [p[0].relative_to(common) for p in pairs]
    outputs = [p[1].relative_to(common) for p in pairs]

    max_in = max(len(str(p)) for p in inputs)
    max_out = max(len(str(p)) + 1 for p in outputs)
    col_in = max(max_in, 20)
    col_out = max(max_out, 20)

    print(f"{'INPUT':<{col_in}}    {'OUTPUT':<{col_out}}")
    print(f"{'─' * col_in}    {'─' * col_out}")

    for inp, out in zip(inputs, outputs):
        print(f"{str(inp):<{col_in}} →  {out}/")

    print()


def confirm_conversion(pdfs: list[Path]) -> bool:
    """Show preview table and ask user to confirm."""
    if len(pdfs) <= 1:
        return True

    print(f"[MinerU] Found {len(pdfs)} PDFs to convert:\n")
    show_preview_table(pdfs)

    response = input(f"Convert all {len(pdfs)} files? [y/N]: ").strip().lower()
    return response in ("y", "yes")


def convert_pdf(pdf_path: Path, mineru_bin: str, env: dict, backend: str) -> None:
    """Convert a single PDF file to markdown using MinerU."""
    output_dir = resolve_output_dir(pdf_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[MinerU] Converting: {pdf_path.name}")
    print(f"         Backend:    {backend}")
    print(f"         Output:     {output_dir / pdf_path.stem}/")

    hybrid_dir = output_dir / pdf_path.stem / "hybrid_auto"
    stem_md = hybrid_dir / f"{pdf_path.stem}.md"

    cmd = [
        mineru_bin,
        "-p",
        str(pdf_path),
        "-o",
        str(output_dir),
        "-b",
        backend,
    ]

    try:
        result = subprocess.run(cmd, check=False, env=env)

        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd)

        # MinerU may exit 0 even on internal errors — validate output exists
        if not stem_md.exists() or stem_md.stat().st_size < 100:
            raise RuntimeError(f"output missing or empty (MinerU false positive): {stem_md}")

        restructure_directory(str(hybrid_dir))
        print(f"[MinerU] ✓ Done: {pdf_path.name}")
    except (subprocess.CalledProcessError, RuntimeError) as e:
        print(f"[MinerU] ✗ Failed: {pdf_path.name} — {e}")
        raise subprocess.CalledProcessError(1, cmd) from e


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert PDFs to Markdown using MinerU",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mineru.py paper.pdf                    # Convert single file
  mineru.py --dir research/pdf/core      # Convert directory
  mineru.py --dir research/pdf --yes     # Skip confirmation
  mineru.py paper.pdf --pipeline         # Emergency fallback if hybrid crashes
      """,
    )
    parser.add_argument(
        "pdf_file",
        type=str,
        nargs="?",
        help="Path to single PDF file",
    )
    parser.add_argument(
        "--dir",
        type=str,
        help="Directory to recursively convert all PDFs",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompt",
    )
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help=(
            "Emergency fallback only. No VLM, 6GB VRAM (vs 10GB), accuracy 82+ vs 90+ (OmniDocBench v1.5: "
            "https://github.com/opendatalab/MinerU#local-deployment). Use if hybrid crashes."
        ),
    )
    args = parser.parse_args()

    if args.pdf_file and args.dir:
        print("Error: Cannot specify both pdf_file and --dir")
        sys.exit(1)

    if not args.pdf_file and not args.dir:
        print("Error: Must specify either pdf_file or --dir")
        parser.print_help()
        sys.exit(1)

    mineru_bin = shutil.which("mineru")
    if not mineru_bin:
        print("Error: 'mineru' binary not found in PATH.")
        print("Install with: pip install magic-pdf")
        sys.exit(1)

    env = os.environ.copy()
    config_path = Path(__file__).parent / "mineru.json"

    if config_path.exists():
        env["MINERU_TOOLS_CONFIG_JSON"] = str(config_path)

    env.update(
        {
            "MINERU_DEVICE_MODE": "mps",
            "PYTORCH_ENABLE_MPS_FALLBACK": "1",
            "KMP_DUPLICATE_LIB_OK": "TRUE",
            "TOKENIZERS_PARALLELISM": "false",
            # get_vram() in model_utils.py has no MPS branch — falls through to 1GB,
            # giving batch_ratio=1 in hybrid_analyze.py. Setting actual unified memory
            # size fixes this: 16GB → batch_ratio=8 for OCR/formula pipeline stages.
            "MINERU_VIRTUAL_VRAM_SIZE": "16",
        }
    )

    backend = "pipeline" if args.pipeline else "hybrid-auto-engine"

    # Pre-flight: check macOS memory pressure (green/yellow/red — same as Activity Monitor)
    pressure = _memory_pressure()
    if pressure == "critical":
        print("[MinerU] ✗ Memory pressure is CRITICAL. Aborting to prevent crash.")
        print("           Close background apps or retry with --pipeline.")
        sys.exit(1)
    elif pressure == "warning":
        print("[MinerU] ⚠ Memory pressure is WARNING.")
        if not args.pipeline:
            print("           Consider --pipeline if this conversion fails.")

    if args.pdf_file:
        input_path = Path(args.pdf_file).resolve()

        if not input_path.exists():
            print(f"Error: File {input_path} does not exist.")
            sys.exit(1)

        if input_path.suffix.lower() != ".pdf":
            print(f"Error: {input_path} is not a PDF file.")
            sys.exit(1)

        pdfs = [input_path]
    else:
        input_path = Path(args.dir)

        if not input_path.is_absolute() and not input_path.exists():
            candidate = PDF_DIR / args.dir
            if candidate.exists():
                input_path = candidate

        input_path = input_path.resolve()
        pdfs = find_pdfs(input_path)

    if not pdfs:
        print(f"No PDFs found in {input_path}")
        sys.exit(0)

    if not args.yes and not confirm_conversion(pdfs):
        print("Cancelled.")
        sys.exit(0)

    print(f"\n[MinerU] Starting conversion of {len(pdfs)} file(s)...\n")

    _acquire_lock()
    try:
        failed = []
        for i, pdf in enumerate(pdfs, 1):
            try:
                print(f"[{i}/{len(pdfs)}]", end=" ")
                convert_pdf(pdf, mineru_bin, env, backend)
            except subprocess.CalledProcessError:
                failed.append(pdf.name)
    finally:
        _release_lock()

    print(f"\n{'=' * 60}")
    print("[MinerU] Conversion complete!")
    print(f"  ✓ Success: {len(pdfs) - len(failed)}/{len(pdfs)}")
    if failed:
        print(f"  ✗ Failed: {len(failed)}")
        for name in failed:
            print(f"    - {name}")
    print(f"{'=' * 60}\n")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
