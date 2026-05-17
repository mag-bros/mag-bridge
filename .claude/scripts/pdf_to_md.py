#!/usr/bin/env python3
"""MinerU PDF to Markdown converter."""

import argparse
import fcntl
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_LOCK_PATH = Path(tempfile.gettempdir()) / "mineru.lock"
_lock_fd = None

# MinerU writes outputs under <stem>/<subdir>/. The subdir name depends on the backend.
BACKEND_OUTPUT_SUBDIR = {
    "hybrid-auto-engine": "hybrid_auto",
    "pipeline": "auto",
    "vlm-http-client": "vlm",
}


def _backend_subdir(backend: str) -> str:
    return BACKEND_OUTPUT_SUBDIR.get(backend, backend.replace("-", "_"))


def _memory_pressure() -> str:
    """macOS memory pressure level via kern.memorystatus_vm_pressure_level.

    Returns 'normal', 'warning', 'critical', or 'unknown'.
    Matches Activity Monitor's green/yellow/red pressure chart on macOS.
    Non-darwin platforms always return 'unknown' (no comparably cheap equivalent).
    """
    if sys.platform != "darwin":
        return "unknown"
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


def cleanup_output(pdf_path: Path, backend_dir: Path, keep_details: bool) -> Path:
    """Post-conversion cleanup. Returns the final MD path.

    Default (keep_details=False): move `<stem>.md` next to the input PDF, delete
        the rest of MinerU's output tree. Result: just `<stem>.pdf` and `<stem>.md`
        in the same directory — clean.
    --details (keep_details=True): leave MinerU's full output intact
        (`<stem>/<backend>/<stem>.md` plus layout.pdf, model.json, images/, …).
    """
    stem_md = backend_dir / f"{pdf_path.stem}.md"

    if keep_details:
        return stem_md

    final_md = pdf_path.parent / f"{pdf_path.stem}.md"
    shutil.move(str(stem_md), str(final_md))
    # backend_dir.parent is `<stem>/` — delete the whole MinerU subtree
    sample_dir = backend_dir.parent
    if sample_dir.exists() and sample_dir.is_dir():
        shutil.rmtree(sample_dir)
    return final_md


_KNOWN_BACKEND_SUBDIRS = set(BACKEND_OUTPUT_SUBDIR.values())


def find_pdfs(input_path: Path) -> list[Path]:
    """Find all PDF files in directory, excluding any backend-output subtrees."""
    if not input_path.is_dir():
        print(f"Error: {input_path} does not exist or is not a directory.")
        sys.exit(1)

    pdfs = []
    for pdf in sorted(input_path.rglob("*.pdf")):
        if _KNOWN_BACKEND_SUBDIRS & set(pdf.parts):
            continue
        pdfs.append(pdf)

    return pdfs


def resolve_output_dir(pdf_path: Path) -> Path:
    """Output goes next to the input PDF — MinerU creates <stem>/<backend>/ inside."""
    return pdf_path.parent


def show_preview_table(pdfs: list[Path], backend: str, keep_details: bool) -> None:
    """Show aligned preview table of input → output mappings."""
    pairs = []
    for pdf in pdfs:
        if keep_details:
            output = resolve_output_dir(pdf) / pdf.stem / _backend_subdir(backend)
        else:
            output = resolve_output_dir(pdf) / f"{pdf.stem}.md"
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


def confirm_conversion(pdfs: list[Path], backend: str, keep_details: bool) -> bool:
    """Show preview table and ask user to confirm."""
    if len(pdfs) <= 1:
        return True

    print(f"[MinerU] Found {len(pdfs)} PDFs to convert:\n")
    show_preview_table(pdfs, backend, keep_details)

    response = input(f"Convert all {len(pdfs)} files? [y/N]: ").strip().lower()
    return response in ("y", "yes")


def convert_pdf(pdf_path: Path, mineru_bin: str, env: dict, backend: str, keep_details: bool) -> None:
    """Convert a single PDF file to markdown using MinerU."""
    output_dir = resolve_output_dir(pdf_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    backend_dir = output_dir / pdf_path.stem / _backend_subdir(backend)
    stem_md = backend_dir / f"{pdf_path.stem}.md"

    print(f"\n[MinerU] Converting: {pdf_path.name}")
    print(f"         Backend:    {backend}")
    print(f"         Mode:       {'--details (full output)' if keep_details else 'clean (just .md)'}")

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

        final_md = cleanup_output(pdf_path, backend_dir, keep_details)
        print(f"[MinerU] ✓ Done: {pdf_path.name} → {final_md}")
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
    parser.add_argument(
        "--details",
        action="store_true",
        help=(
            "Keep MinerU's full output tree: <stem>/<backend>/<stem>.md, layout.pdf, model.json, images/, etc. "
            "Default: discard everything except <stem>.md (moved next to the input PDF)."
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
        print("Install with: uv pip install 'mineru[pipeline]'")
        sys.exit(1)

    env = os.environ.copy()
    config_path = Path(__file__).parent / "mineru.json"

    if config_path.exists():
        env["MINERU_TOOLS_CONFIG_JSON"] = str(config_path)

    env.update(
        {
            "KMP_DUPLICATE_LIB_OK": "TRUE",
            "TOKENIZERS_PARALLELISM": "false",
            # get_vram() in model_utils.py has no MPS branch — falls through to 1GB,
            # giving batch_ratio=1 in hybrid_analyze.py. Setting actual unified memory
            # size fixes this: 16GB → batch_ratio=8 for OCR/formula pipeline stages.
            "MINERU_VIRTUAL_VRAM_SIZE": "16",
        }
    )

    if sys.platform == "darwin":
        # Apple Silicon: use Metal Performance Shaders + CPU fallback for unsupported ops.
        env.update(
            {
                "MINERU_DEVICE_MODE": "mps",
                "PYTORCH_ENABLE_MPS_FALLBACK": "1",
            }
        )
    # Linux/Windows: MinerU auto-detects via torch.cuda.is_available(); falls back to CPU if no GPU.

    # Platform-aware default: hybrid-auto-engine needs mineru[vlm] (~5GB models + accelerate).
    # macOS users typically install mineru[core] for MPS/MLX coverage; Linux installs default to
    # mineru[pipeline] only, so we pick the lighter backend there. --pipeline always wins.
    if args.pipeline:
        backend = "pipeline"
    elif sys.platform == "darwin":
        backend = "hybrid-auto-engine"
    else:
        backend = "pipeline"

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
        input_path = Path(args.dir).resolve()
        pdfs = find_pdfs(input_path)

    if not pdfs:
        print(f"No PDFs found in {input_path}")
        sys.exit(0)

    if not args.yes and not confirm_conversion(pdfs, backend, args.details):
        print("Cancelled.")
        sys.exit(0)

    print(f"\n[MinerU] Starting conversion of {len(pdfs)} file(s)...\n")

    _acquire_lock()
    try:
        failed = []
        for i, pdf in enumerate(pdfs, 1):
            try:
                print(f"[{i}/{len(pdfs)}]", end=" ")
                convert_pdf(pdf, mineru_bin, env, backend, args.details)
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
