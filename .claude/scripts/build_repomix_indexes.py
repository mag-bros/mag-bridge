#!/usr/bin/env python3
"""
build_repomix_indexes.py — Pack venv site-packages into .local-mcp/ indexes.

Usage:
  python .claude/scripts/build_repomix_indexes.py --package PKG[,PKG,...]  [--dry-run]
  python .claude/scripts/build_repomix_indexes.py --build-all              [--dry-run]

Modes (mutually exclusive, one required):
  --package      Build one or more packages by name (comma-separated)
  --build-all    Build all packages in site-packages
"""

import argparse
import glob
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Find project root by searching upward for marker files (case-insensitive)
_markers = {"readme.md", "requirements.txt", "pyproject.toml"}
ROOT = (
    next((p for p in Path(__file__).resolve().parents if any(f.name.lower() in _markers for f in p.iterdir())), None)
    or Path(__file__).parent.parent.parent
)

MANIFEST_PATH = ROOT / ".local-mcp" / "manifest.json"
LOCAL_MCP = ROOT / ".local-mcp"


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------


def read_repomix_version_from_mcp_json(mcp_path: Path) -> str | None:
    """Parse pinned repomix version from .mcp.json args array."""
    try:
        data = json.loads(mcp_path.read_text())
        args = data.get("mcpServers", {}).get("repomix", {}).get("args", [])
        for arg in args:
            if isinstance(arg, str) and arg.startswith("repomix@"):
                return arg.split("@", 1)[1]
    except Exception:
        pass
    return None


def get_repomix_version_info() -> tuple[str, str]:
    """Return (version, git_commit_sha) for the pinned repomix release."""
    version = read_repomix_version_from_mcp_json(ROOT / ".mcp.json") or "unknown"
    try:
        result = subprocess.run(
            ["npm", "show", f"repomix@{version}", "gitHead"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        commit = result.stdout.strip()
        if commit and len(commit) == 40:
            return version, commit
    except Exception:
        pass
    return version, ""


# ---------------------------------------------------------------------------
# Site-packages discovery
# ---------------------------------------------------------------------------


def find_site_packages() -> Path:
    # Linux/macOS: .venv/lib/python3.x/site-packages
    # Windows:     .venv/Lib/site-packages  (capital L, no python* subdir)
    candidates = [
        *[Path(p) for p in glob.glob(str(ROOT / ".venv" / "lib" / "python*" / "site-packages"))],
        ROOT / ".venv" / "Lib" / "site-packages",
    ]
    for path in candidates:
        if path.is_dir():
            return path
    sys.exit("ERROR: .venv site-packages not found — is the venv set up?")


def discover_packages(site_packages: Path) -> list[dict]:
    """Return list of {name, path, version} for top-level package directories."""
    packages = []
    for entry in sorted(site_packages.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        if name == "__pycache__" or name.endswith(".dist-info"):
            continue

        candidates = [name, name.replace("_", "-"), name.replace("-", "_")]
        if name.startswith("_"):
            pub = name.lstrip("_")
            candidates += [pub, pub.replace("_", "-")]
        dist_infos: list[Path] = []
        for cand in candidates:
            dist_infos = list(site_packages.glob(f"{cand}-*.dist-info"))
            if dist_infos:
                break

        version = "unknown"
        if dist_infos:
            metadata = dist_infos[0] / "METADATA"
            if metadata.exists():
                for line in metadata.read_text(errors="replace").splitlines():
                    if line.startswith("Version:"):
                        version = line.split(":", 1)[1].strip()
                        break
            else:
                parts = dist_infos[0].name.rstrip(".dist-info").rsplit("-", 1)
                if len(parts) == 2:
                    version = parts[1]

        packages.append({"name": name.lower().replace("-", "_"), "path": entry, "version": version})
    return packages


# ---------------------------------------------------------------------------
# Package selection
# ---------------------------------------------------------------------------


def resolve_packages_by_name(names: list[str], installed: list[dict]) -> tuple[list[dict], list[str]]:
    """Match requested names against installed packages. Returns (matched, warnings)."""
    index = {p["name"]: p for p in installed}
    matched = []
    warnings = []
    for name in names:
        normalized = name.lower().replace("-", "_")
        if normalized in index:
            matched.append(index[normalized])
        else:
            warnings.append(f"WARNING: '{name}' not found in site-packages — skipping")
    return matched, warnings


# ---------------------------------------------------------------------------
# Packing
# ---------------------------------------------------------------------------


def pack_package(pkg: dict, repomix_version: str, repomix_commit: str) -> dict | None:
    name = pkg["name"]
    src = pkg["path"]
    out_dir = LOCAL_MCP / name
    out_file = out_dir / "index.xml"

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "npx",
        f"repomix@{repomix_version}",
        str(src),
        "--output",
        str(out_file),
        "--compress",
        "--no-gitignore",
        "--style",
        "xml",
    ]

    print(f"  → packing {name} ({pkg['version']}) ...", flush=True)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT packing {name}", file=sys.stderr)
        return None

    if result.returncode != 0:
        print(f"    FAILED {name}:\n{result.stderr[-500:]}", file=sys.stderr)
        return None

    if not out_file.exists():
        print(f"    ERROR: output file missing for {name}", file=sys.stderr)
        return None

    total_files = None
    total_tokens = None
    for line in result.stdout.splitlines():
        lower = line.lower()
        if "files:" in lower or "file processed" in lower:
            for p in line.split():
                if p.isdigit():
                    total_files = int(p)
                    break
        if "token" in lower:
            for p in line.split():
                p_clean = p.replace(",", "")
                if p_clean.isdigit():
                    total_tokens = int(p_clean)
                    break

    return {
        "name": name,
        "version": pkg["version"],
        "source": "venv",
        "packedFile": f".local-mcp/{name}/index.xml",
        "outputId": None,
        "totalFiles": total_files,
        "totalTokens": total_tokens,
        "compressed": True,
        "repomixVersion": repomix_version,
        "repomixCommit": repomix_commit,
        "lastIndexBuild": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def validate_index(pkg_name: str) -> bool:
    out_file = LOCAL_MCP / pkg_name / "index.xml"
    if not out_file.exists():
        return False
    try:
        content = out_file.read_text(errors="replace")
        return "def " in content or "class " in content
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


def load_manifest() -> list:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return []


def save_manifest(entries: list) -> None:
    MANIFEST_PATH.write_text(json.dumps(entries, indent=2) + "\n")


def upsert_entry(manifest: list, new_entry: dict) -> list:
    name = new_entry["name"]
    updated = [e for e in manifest if e.get("name") != name]
    updated.append(new_entry)
    return updated


def check_manifest_integrity(manifest: list, root: Path, current_repomix_version: str) -> tuple[list[str], list[str]]:
    """Check manifest entries against disk. Returns (errors, warnings).

    Errors (hard): missing index, empty index, no def/class in venv index.
    Warnings (soft): repomixVersion mismatch.
    """
    errors: list[str] = []
    warnings: list[str] = []

    for entry in manifest:
        name = entry.get("name", "?")
        packed = entry.get("packedFile", "")
        source = entry.get("source", "")
        index_path = root / packed if packed else None

        if not index_path or not index_path.exists():
            errors.append(f"  MISSING index for '{name}': {packed}")
            continue

        content = index_path.read_text(errors="replace")
        if not content.strip():
            errors.append(f"  EMPTY index for '{name}': {packed}")
            continue

        if source == "venv" and "def " not in content and "class " not in content:
            errors.append(f"  NO CODE in venv index for '{name}' — may be a stub")

        entry_version = entry.get("repomixVersion", "")
        if entry_version and entry_version != current_repomix_version:
            warnings.append(
                f"  WARNING: '{name}' built with repomix@{entry_version}, current pin is @{current_repomix_version} — consider rebuilding"
            )

    return errors, warnings


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def _print_report(manifest: list) -> None:
    venv_entries = sorted(
        [e for e in manifest if e.get("source") == "venv"],
        key=lambda e: e.get("name", ""),
    )
    other_entries = [e for e in manifest if e.get("source") != "venv"]

    W_NAME, W_VER, W_FILES, W_TOK = 20, 9, 6, 9
    rule = f"{'─' * (W_NAME + W_VER + W_FILES + W_TOK + 7)}"

    def row(name: str, ver: str, files: object, tokens: object, path: str = "") -> str:
        tok_str = f"{tokens:,}" if isinstance(tokens, int) else (str(tokens) if tokens else "—")
        files_str = str(files) if files is not None else "—"
        line = f"  {name:<{W_NAME}} {ver:<{W_VER}} {files_str:>{W_FILES}} {tok_str:>{W_TOK}}"
        if path:
            line += f"  {path}"
        return line

    print(f"\n{rule}")
    print(f"  {'Package':<{W_NAME}} {'Version':<{W_VER}} {'Files':>{W_FILES}} {'Tokens':>{W_TOK}}  Location")
    print(rule)

    all_shown = other_entries + venv_entries
    total_files = total_tokens = 0
    for e in all_shown:
        f = e.get("totalFiles")
        t = e.get("totalTokens")
        if isinstance(f, int):
            total_files += f
        if isinstance(t, int):
            total_tokens += t
        print(row(e["name"], e.get("version", "—"), f, t, e.get("packedFile", "")))

    print(rule)
    print(row("TOTAL", f"{len(all_shown)} pkgs", total_files, total_tokens))
    print(rule)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--package", metavar="PKG[,PKG...]", help="Build one or more packages (comma-separated)")
    mode.add_argument("--build-all", action="store_true", help="Build all packages in site-packages")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be built, don't pack")
    args = parser.parse_args()

    repomix_version, repomix_commit = get_repomix_version_info()
    print(f"repomix version: {repomix_version}")
    if repomix_commit:
        print(f"  commit: {repomix_commit}")
    else:
        print("  WARNING: could not resolve commit SHA")

    site_packages = find_site_packages()
    print(f"site-packages: {site_packages}")
    all_packages = discover_packages(site_packages)

    if args.build_all:
        packages = all_packages
    else:
        names = [n.strip() for n in args.package.split(",") if n.strip()]
        packages, pkg_warnings = resolve_packages_by_name(names, all_packages)
        for w in pkg_warnings:
            print(w, file=sys.stderr)
        if not packages:
            sys.exit("ERROR: none of the requested packages found in site-packages")

    print(f"\n{len(packages)} package(s) to build:")
    for p in packages:
        if p["version"] == "unknown":
            print(f"  {p['name']} (version unknown — building anyway)")
        else:
            print(f"  {p['name']} {p['version']}")

    if args.dry_run:
        print("\n--dry-run: exiting without packing.")
        return

    manifest = load_manifest()
    built = 0
    failed = []

    print()
    for pkg in packages:
        entry = pack_package(pkg, repomix_version, repomix_commit)
        if entry is None:
            failed.append(pkg["name"])
            continue

        ok = validate_index(pkg["name"])
        if not ok:
            print(f"    VALIDATION FAILED for {pkg['name']} — skipping manifest update", file=sys.stderr)
            failed.append(pkg["name"])
            continue

        files_str = f"{entry['totalFiles']} files" if entry["totalFiles"] else "? files"
        tokens_str = f"{entry['totalTokens']:,} tokens" if entry["totalTokens"] else "? tokens"
        print(f"    OK  {pkg['name']}  [{files_str}, {tokens_str}]")

        manifest = upsert_entry(manifest, entry)
        manifest = sorted(manifest, key=lambda e: (e.get("source") == "venv", e.get("name", "")))
        save_manifest(manifest)
        built += 1

    print(f"\nBuilt {built}/{len(packages)} package(s).")
    if failed:
        print(f"Failed: {', '.join(failed)}", file=sys.stderr)

    _print_report(manifest)

    # Post-build integrity check
    manifest = load_manifest()
    integrity_errors, integrity_warnings = check_manifest_integrity(manifest, ROOT, repomix_version)
    for w in integrity_warnings:
        print(w)
    if integrity_errors:
        print("\nManifest integrity errors:", file=sys.stderr)
        for e in integrity_errors:
            print(e, file=sys.stderr)
        sys.exit(1)

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
