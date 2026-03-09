# RDKit MCP Server
*Component documentation — shared across agent sessions*

## What
Local FastMCP server (STDIO) giving Claude grounded access to RDKit `2025.09.6` source. Eliminates API hallucinations by pointing at real files on disk.

## File Layout
```
mcp/
├── rdkit_mcp.py           # server — single portable file
├── .module_index.json     # auto-generated on first run (gitignored)
└── (future) pyproject.toml + README.md  — for marketplace extraction
.mcp.json                  # repo root, team-shared Claude Code config
```

## Data Sources
| Source | Path | Default? |
|--------|------|----------|
| Python site-packages | `.venv/lib/python3.13/site-packages/rdkit/` | Yes |
| C++ source | `rdkit/` (git submodule, tag `Release_2025_09_6`) | No — explicit `source="cpp"` |

## Tools
| Tool | Typical token cost | Purpose |
|------|--------------------|---------|
| `get_module_index(min_relevance)` | ~500 | Start here. Returns weighted map of all modules. |
| `search_code(query, source, context_file)` | ~200–3000 | Tiered ripgrep search. |
| `read_file(path, source)` | ~500–15000 | Read one file. Whole file — see known gaps. |
| `inspect_module(name)` | ~300 | C++ signatures from compiled .so via inspect/help. |
| `list_directory(path)` | ~100 | Browse tree, names only. |

## Usage Contract

**Always start with `get_module_index(min_relevance=0.7)`** — 500 tokens to understand what's relevant, then jump directly to the right module.

**Pass `context_file`** — absolute path of the file currently being edited. Server parses its rdkit imports and scopes search to only those modules (Tier 1). Without it, falls back to index relevance (Tier 2), then full search (Tier 3).

**Search before reading** — `search_code` returns match lines with line numbers. Only call `read_file` once you have a specific line target.

**C++ is explicit** — pass `source="cpp"` only when you need implementation details. Python-only (default) is 3-5x cheaper in results volume.

## Tiered Search Routing
```
Tier 1 — CONTEXT (~200 tokens)   parse context_file imports → search only those modules
Tier 2 — INDEX   (~500 tokens)   use relevance scores → search top-N modules
Tier 3 — FULL    (~1000-3000)    ripgrep entire source tree — last resort
```

## Index Schema (Pydantic, MongoDB-ready)
```python
class ModuleEntry(BaseModel):
    name: str              # "Chem.rdmolops"
    python_path: str       # relative to site-packages/rdkit/
    cpp_path: str | None   # relative to rdkit/ submodule
    source_type: str       # "compiled" | "python" | "both"
    description: str
    key_functions: list[str]
    relevance: float       # 0.0-1.0, auto from import freq + manual overrides

class ModuleIndex(BaseModel):
    version: str           # "2025.09.6"
    modules: list[ModuleEntry]
```
Regenerate: delete `mcp/.module_index.json`, restart server. Only needed on RDKit version bump.

## Stack
- `mcp[cli]` (FastMCP) — JSON-RPC, STDIO transport, schema generation
- `rg` (ripgrep) — search backend (~50ms on 100MB)
- `pydantic` — index schema
- `opentelemetry-exporter-otlp-proto-grpc` — Phoenix traces (optional, silent no-op)

## Next: Tree-sitter Symbol Extraction

### Why
`read_file` returns entire files (~2800-13000 tokens). Most queries need one function (~200-500 tokens). 90% token waste. Also: ripgrep text search hits comments, strings, and irrelevant matches.

### What
Add a `get_symbol(name, source)` tool that returns the exact function/class body using tree-sitter AST parsing. Build a symbol index at startup alongside the module index.

### Dependencies (installed)
- `tree-sitter==0.25.2`
- `tree-sitter-cpp==0.23.4`
- `tree-sitter-python==0.25.0`

### Implementation Plan

**1. Symbol index schema** — extend the existing Pydantic models:
```python
class SymbolEntry(BaseModel):
    name: str              # "GetSubstructMatches"
    kind: str              # "function" | "class" | "method" | "template"
    file: str              # relative path
    start_line: int
    end_line: int
    signature: str         # first line / declaration

class SymbolIndex(BaseModel):
    version: str
    symbols: dict[str, list[SymbolEntry]]  # name → entries (can have overloads)
```

**2. Build symbol index at startup** (~80 lines):
- For **C++ source** (`rdkit/Code/`): parse `.h` and `.cpp` files with `tree-sitter-cpp`
  - Query: `(function_definition)`, `(template_declaration)`, `(class_specifier)`
  - Extract: name, file, start_line, end_line, signature
  - Scope: only `Code/GraphMol/` subtree (where substruct matching lives) — expand later if needed
- For **Python site-packages**: parse `.py` files with `tree-sitter-python`
  - Query: `(function_definition)`, `(class_definition)`
  - Extract: same fields
- Save to `mcp/.symbol_index.json` (gitignored, alongside `.module_index.json`)

**3. New tool: `get_symbol(name, source="python")`**:
- Look up `name` in symbol index
- Read only the lines `start_line:end_line` from the file
- Return: signature + body + file path + line range
- If multiple matches (overloads): return all, sorted by relevance

**4. Update `search_code` tiered routing** — add Tier 0:
```
Tier 0 — SYMBOL (~200 tokens)   exact match in symbol index → return function body
Tier 1 — CONTEXT (~200 tokens)  parse context_file imports → search those modules
Tier 2 — INDEX   (~500 tokens)  relevance scores → search top-N modules
Tier 3 — FULL    (~1000-3000)   ripgrep entire source tree
```

**5. Scope for initial build:**
- C++: parse `rdkit/Code/GraphMol/**/*.{h,cpp}` (~50 files)
- Python: parse `.venv/.../rdkit/Chem/*.py` (~30 files)
- Skip: tests, docs, external, contrib

**6. Token cost after:**
| Operation | Before | After |
|-----------|--------|-------|
| Get one C++ function body | ~2800–13000 (full file) | ~200–500 (exact function) |
| Get one Python function | ~500–2000 (full file) | ~100–300 (exact function) |
| Find + read a symbol | 2-3 hops, ~3000-5000 tokens | 1 hop, ~200-500 tokens |

### Testing approach
Use MCP Inspector to call `get_symbol("GetSubstructMatches", source="cpp")` — should return the exact 16-line template function from `substructmethods.h:98-114`.

### What NOT to do
- Don't parse entire RDKit submodule (~1000+ files). Scope to `Code/GraphMol/`.
- Don't build call graphs. Just symbol → location mapping.
- Don't remove existing tools. `get_symbol` is additive — `search_code` and `read_file` remain as fallbacks.

## Token Cost Reference
| Operation | Approx tokens |
|-----------|--------------|
| `get_module_index(min_relevance=0.7)` | ~500 |
| `search_code` resolves at Tier 1 | ~200 |
| `search_code` falls to Tier 3 | ~1000–3000 |
| `read_file` on a 163-line .h file | ~2800 |
| `read_file` on a 800-line .cpp file | ~13000 |
| `inspect_module("Chem.rdmolops")` | ~300 |

## Marketplace Extraction (future)
**Difficulty: Low.** Steps when ready:
1. Replace hardcoded paths with env vars (`RDKIT_PYTHON_SRC`, `RDKIT_CPP_SRC`)
2. Add `mcp/pyproject.toml` with deps (`mcp[cli]`, `pydantic`, `opentelemetry-*`)
3. Add `mcp/README.md`
4. Move to private org repo, register as marketplace source in `.claude/settings.json`

## Skill (future)
A `.claude/skills/rdkit-lookup.md` skill that encodes the usage contract above — when to call which tool, in what order. The server handles data, the skill handles Claude's reasoning about how to use it.

## Testing
```bash
.venv/bin/mcp dev mcp/rdkit_mcp.py   # MCP Inspector at localhost:6274
```
Test tools here after any change, before using in a Claude session.
