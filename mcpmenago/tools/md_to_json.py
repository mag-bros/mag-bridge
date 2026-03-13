#!/usr/bin/env python3
"""Deterministic MD -> structural.json pre-extractor. No LLM, no interpretation."""

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
from mdit_py_plugins.dollarmath import dollarmath_plugin
from tools import JSON_DIR, MD_DIR

# ── HTML table parser ─────────────────────────────────────────────────────────


class _TableHTMLParser(HTMLParser):
    """Extracts rows from HTML tables. First row treated as headers."""

    def __init__(self) -> None:
        super().__init__()
        self._rows: list[list[str]] = []
        self._current_row: list[str] = []
        self._current_cell: str = ""
        self._in_cell: bool = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "tr":
            self._current_row = []
        elif tag in ("td", "th"):
            self._current_cell = ""
            self._in_cell = True

    def handle_endtag(self, tag: str) -> None:
        if tag in ("td", "th"):
            self._current_row.append(self._current_cell.strip())
            self._in_cell = False
        elif tag == "tr" and self._current_row:
            self._rows.append(self._current_row[:])

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._current_cell += data

    def result(self) -> dict:
        if not self._rows:
            return {"headers": [], "rows": []}
        return {"headers": self._rows[0], "rows": self._rows[1:]}


def _parse_html_table(html: str) -> dict | None:
    if "<table" not in html.lower():
        return None
    parser = _TableHTMLParser()
    parser.feed(html)
    r = parser.result()
    return r if r["headers"] else None


# ── Inline text extraction ────────────────────────────────────────────────────


def _inline_text(node: SyntaxTreeNode) -> str:
    """Collect text from inline node, preserving $math$ in-place."""
    parts = []
    for child in node.children:
        if child.type == "math_inline":
            parts.append(f"${child.content}$")
        elif child.type in ("text", "code_inline"):
            parts.append(child.content)
        elif child.type in ("softbreak", "hardbreak"):
            parts.append("\n")
        elif child.type == "image":
            pass  # catalogued separately
        else:
            parts.append(_inline_text(child))
    return "".join(parts)


# ── GFM table extraction ──────────────────────────────────────────────────────


def _cell_text(cell: SyntaxTreeNode) -> str:
    return _inline_text(cell.children[0]) if cell.children else ""


def _extract_gfm_table(node: SyntaxTreeNode, section_header: str) -> dict:
    headers: list[str] = []
    rows: list[list[str]] = []
    for child in node.children:
        if child.type == "thead":
            for tr in child.children:
                if tr.type == "tr":
                    headers = [_cell_text(th) for th in tr.children if th.type == "th"]
        elif child.type == "tbody":
            for tr in child.children:
                if tr.type == "tr":
                    if row := [_cell_text(td) for td in tr.children if td.type == "td"]:
                        rows.append(row)
    return {"section_header": section_header, "headers": headers, "rows": rows}


# ── Core parser ───────────────────────────────────────────────────────────────


def parse_md(md_text: str) -> dict:
    """Parse markdown into structural JSON. Deterministic — no LLM."""
    md = MarkdownIt("commonmark").use(dollarmath_plugin).enable("table")
    tree = SyntaxTreeNode(md.parse(md_text))

    sections: list[dict] = []
    display_equations: list[dict] = []
    tables: list[dict] = []
    figures: list[dict] = []
    references_raw: list[str] = []

    current: dict | None = None
    in_references: bool = False

    def consume(inline: SyntaxTreeNode, sep: str = "\n\n") -> None:
        """Route inline text to refs or section content; collect figures."""
        if current is not None:
            for child in inline.children:
                if child.type == "image":
                    figures.append({"path": child.attrGet("src") or "", "section_header": current["header"]})
        text = _inline_text(inline).strip()
        if not text:
            return
        if in_references:
            references_raw.append(text)
        elif current is not None:
            current["content"] += text + sep

    for node in tree.children:
        if node.type == "heading":
            if current is not None:
                current["content"] = current["content"].strip()
                sections.append(current)
            header = _inline_text(node.children[0]) if node.children else ""
            in_references = bool(re.search(r"\breferences\b", header, re.I))
            current = {"header": header, "content": ""}

        elif node.type == "paragraph" and current is not None:
            if node.children:
                consume(node.children[0])

        elif node.type in ("ordered_list", "bullet_list"):
            for item in node.children:
                for para in item.children:
                    if para.type == "paragraph" and para.children:
                        consume(para.children[0], "\n")

        elif node.type == "math_block":
            display_equations.append(
                {
                    "section_header": current["header"] if current else "",
                    "latex": f"$${node.content}$$",
                }
            )

        elif node.type == "table":
            tables.append(_extract_gfm_table(node, current["header"] if current else ""))

        elif node.type == "html_block":
            if parsed := _parse_html_table(node.content):
                tables.append({"section_header": current["header"] if current else "", **parsed})

    if current is not None:
        current["content"] = current["content"].strip()
        sections.append(current)

    return {
        "sections": sections,
        "display_equations": display_equations,
        "tables": tables,
        "figures": figures,
        "references_raw": references_raw,
    }


# ── I/O ───────────────────────────────────────────────────────────────────────


def resolve_input_path(arg: str) -> list[Path]:
    """Return list of .md paths to process.

    - Direct .md file              → [that file]
    - Dir + index.md at root       → [dir/index.md]  (root index.md takes priority over subdirs)
    - Dir, no root index.md        → sorted rglob("index.md") across all subdirs
    - Dir with no index.md anywhere → FileNotFoundError
    - Path doesn't exist or is not a file/dir → FileNotFoundError
    """
    p = Path(arg).resolve()
    if p.is_file():
        return [p]
    if p.is_dir():
        direct = p / "index.md"
        if direct.exists():
            return [direct]  # root index.md takes priority; subdirs not scanned
        found = sorted(p.rglob("index.md"))
        if not found:
            raise FileNotFoundError(f"No index.md found under {p}")
        return found
    raise FileNotFoundError(f"Not found: {p}")


def extract_paper(md_path: Path) -> Path:
    """Parse paper index.md -> structural.json. Returns output path."""
    result = parse_md(md_path.read_text(encoding="utf-8"))
    result["metadata"] = {
        "source_file": str(md_path),
        "title_raw": result["sections"][0]["header"] if result["sections"] else "",
    }

    paper_dir = md_path.parent
    try:
        rel = paper_dir.relative_to(MD_DIR)
    except ValueError:
        rel = Path(paper_dir.name)

    out_dir = JSON_DIR / rel
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "structural.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="MD -> structural.json pre-extractor")
    parser.add_argument("input", help="Paper directory, collection directory, or path to .md file")
    args = parser.parse_args()

    paths = resolve_input_path(args.input)
    for md_path in paths:
        try:
            out = extract_paper(md_path)
            print(f"Written: {out}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
