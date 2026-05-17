---
name: convert
description: Convert research-paper PDFs to Markdown then to structural JSON via the `.claude2/scripts/` pipeline. Use whenever the user asks to convert a paper, extract text from a PDF, process a research paper, generate structured JSON from a paper, or has a `.pdf` / `.md` file that needs the standard pipeline applied. Output is always written next to the input file with the new extension — no other location.
---

# /convert

Two-stage deterministic pipeline. No LLM at extraction time.

## Stages

1. **PDF → MD** via `.claude2/scripts/pdf_to_md.py` (MinerU). Preserves layout, equations, tables, figures. Creates a `<stem>/hybrid_auto/index.md` subtree next to the input PDF.
2. **MD → JSON** via `.claude2/scripts/md_to_json.py`. Deterministic structural parser. Output schema: `sections`, `display_equations`, `tables`, `figures`, `references_raw`, `metadata`. Output file is `<input_stem>.json` next to the input MD.

## Input → Output mapping

| Input | Stage 1 output | Stage 2 output |
|---|---|---|
| `paper.pdf` | `paper/hybrid_auto/index.md` (next to PDF) | `paper/hybrid_auto/index.json` (next to MD) |
| `paper.md` | (skipped) | `paper.json` (next to MD) |
| Directory of PDFs | one subtree per PDF | one JSON per `index.md` |

## Usage

### Single PDF (both stages)
```bash
python .claude2/scripts/pdf_to_md.py <path/to/file.pdf>
python .claude2/scripts/md_to_json.py <path/to/file>/hybrid_auto/index.md
```

### Directory (both stages)
```bash
python .claude2/scripts/pdf_to_md.py --dir <path/to/dir>
python .claude2/scripts/md_to_json.py <path/to/dir>
```
`pdf_to_md.py` excludes PDFs inside `hybrid_auto/`. `md_to_json.py` walks for `index.md` files.

### MD only (skip stage 1)
```bash
python .claude2/scripts/md_to_json.py <path/to/file.md>
```

## Routing

When triggered, ask the user once (via interactive prompt) which stage applies:
- **A) PDF→MD→JSON** — full pipeline (most common for fresh papers)
- **B) PDF→MD only** — when JSON not needed yet
- **C) MD→JSON only** — when MinerU output already exists

If a directory is passed, default to A unless the directory already contains `hybrid_auto/` subtrees (then C).

## Prerequisites

- `mineru` binary on PATH (see Setup below if missing).
- `markdown-it-py` and `mdit-py-plugins` installed (already in project venv).
- Stage 1 sets MinerU env vars itself (MPS device, `MINERU_VIRTUAL_VRAM_SIZE=16`, etc.).

## Setup (one-time, only if `mineru` is missing)

Run the checks in order; stop as soon as `mineru` resolves on PATH.

### 1. Detect

```bash
command -v mineru || echo "mineru missing"
```

If present → skip Setup, jump to Usage.

### 2. Ensure `uv` is available

`uv` is the preferred installer (10–100× faster than pip, no env mutation). Bootstrap with plain pip if missing:

```bash
command -v uv || pip install uv
```

### 3. Resolve latest MinerU version

Use the github MCP to fetch the latest tag from `opendatalab/MinerU` rather than guessing:

- `mcp__github__list_commits` on `opendatalab/MinerU` → look at the latest tagged release, OR
- `mcp__github__get_file_contents` on `opendatalab/MinerU` → `pyproject.toml` to read the `version =` line

Pin the resolved version with the `[pipeline]` extras (torch, transformers, onnxruntime — required by `hybrid-auto-engine` AND `pipeline` backends): e.g. `mineru[pipeline]==3.1.14`. The package name is **`mineru`** (legacy alias `magic-pdf` is deprecated; do not use). For all backends including VLM + Gradio, use `mineru[core]` instead (heavier).

### 4. Pin in `requirements-dev.txt`

Read `requirements-dev.txt`. If a line matching `^mineru` already exists, replace it with the new pin; otherwise append `mineru==<version>` at the end. Keep ordering stable — don't reformat other lines.

### 5. Install

```bash
uv pip install -r requirements-dev.txt
```

If `uv` cannot find the project venv, fall back to `uv pip install --system mineru==<version>` or activate the venv first (`source .venv/bin/activate`).

### 6. Verify

```bash
mineru --version
```

If still missing, report exact failure to user — do NOT auto-retry with `pip install magic-pdf` (that's the old name and will misinstall).

## Failure modes

- **macOS memory pressure CRITICAL** → stage 1 aborts pre-flight. Close apps or retry with `--pipeline` (no-VLM fallback, lower accuracy).
- **MinerU exits 0 but output empty** → script catches and raises `RuntimeError`; retry with `--pipeline`.
- **Another MinerU process running** → script blocks on `fcntl` lock until it finishes.

## After conversion

Report the output path(s) so the user can open them. For JSON, mention the top-level keys observed (`sections`, etc.) and the section count — gives a quick quality signal.
