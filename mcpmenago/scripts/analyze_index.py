"""analyze_index.py — Produce metrics JSON from a book's 01_index.json.

Usage:
    uv run --project ./mcpmenago python mcpmenago/scripts/analyze_index.py <book>
    uv run --project ./mcpmenago python mcpmenago/scripts/analyze_index.py <book> --out /path/to/output.json

Output: 01_index_analysis.json written next to 01_index.json (or --out path).
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Allow running from project root without installing
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcpmenago.paths import LIBRARY


_CPP_EXTS = {".h", ".hpp", ".cpp", ".cc", ".cxx", ".c"}
_PY_EXTS = {".py", ".pyi"}


def _lang(file: str) -> str:
    ext = Path(file).suffix.lower()
    if ext in _PY_EXTS:
        return "python"
    if ext in _CPP_EXTS:
        return "cpp"
    return "other"


def _percentile(sorted_vals: list[int], p: float) -> int:
    if not sorted_vals:
        return 0
    idx = int(len(sorted_vals) * p / 100)
    return sorted_vals[min(idx, len(sorted_vals) - 1)]


def analyze(index_path: Path) -> dict:
    raw = json.loads(index_path.read_text())
    symbols: dict[str, list[dict]] = raw.get("symbols", {})

    total_entries = 0
    by_kind: Counter = Counter()
    by_lang: Counter = Counter()
    by_kind_by_lang: dict[str, Counter] = defaultdict(Counter)
    name_entry_counts: list[int] = []
    signature_lengths: list[int] = []
    file_symbol_counts: Counter = Counter()
    duplicate_names: list[tuple[str, int]] = []

    for name, entries in symbols.items():
        count = len(entries)
        total_entries += count
        name_entry_counts.append(count)
        if count > 1:
            duplicate_names.append((name, count))

        for e in entries:
            kind = e.get("kind", "unknown")
            lang = _lang(e.get("file", ""))
            sig = e.get("signature", "")

            by_kind[kind] += 1
            by_lang[lang] += 1
            by_kind_by_lang[lang][kind] += 1
            signature_lengths.append(len(sig))
            file_symbol_counts[e.get("file", "")] += 1

    unique_names = len(symbols)
    sig_sorted = sorted(signature_lengths)
    duplicate_names.sort(key=lambda x: x[1], reverse=True)

    return {
        "source": str(index_path),
        "version": raw.get("version", "unknown"),
        "total_entries": total_entries,
        "unique_names": unique_names,
        "avg_entries_per_name": round(total_entries / unique_names, 2) if unique_names else 0,
        "by_kind": dict(by_kind.most_common()),
        "by_language": dict(by_lang.most_common()),
        "by_kind_by_language": {lang: dict(kinds) for lang, kinds in by_kind_by_lang.items()},
        "top_duplicated_names": [
            {"name": n, "entries": c} for n, c in duplicate_names[:20]
        ],
        "signature_stats": {
            "min": sig_sorted[0] if sig_sorted else 0,
            "max": sig_sorted[-1] if sig_sorted else 0,
            "avg": round(sum(sig_sorted) / len(sig_sorted), 1) if sig_sorted else 0,
            "p50": _percentile(sig_sorted, 50),
            "p90": _percentile(sig_sorted, 90),
        },
        "top_files_by_symbol_count": [
            {"file": f, "count": c} for f, c in file_symbol_counts.most_common(20)
        ],
    }


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("Usage: analyze_index.py <book> [--out <path>]", file=sys.stderr)
        sys.exit(1)

    book = args[0]
    out_path: Path | None = None
    if "--out" in args:
        out_path = Path(args[args.index("--out") + 1])

    index_path = LIBRARY / book / "01_index.json"
    if not index_path.exists():
        print(f"Not found: {index_path}", file=sys.stderr)
        sys.exit(1)

    metrics = analyze(index_path)

    if out_path is None:
        out_path = index_path.parent / "01_index_analysis.json"

    out_path.write_text(json.dumps(metrics, indent=2))
    print(f"Written: {out_path}")
    print(f"  {metrics['total_entries']} total entries, {metrics['unique_names']} unique names")
    print(f"  Languages: {metrics['by_language']}")
    print(f"  Kinds: {metrics['by_kind']}")
    print(f"  Top duplicate: {metrics['top_duplicated_names'][0] if metrics['top_duplicated_names'] else 'none'}")


if __name__ == "__main__":
    main()
