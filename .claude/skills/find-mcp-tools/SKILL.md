---
name: find-mcp-tools
description: Discovers new MCP code-indexing tools on GitHub and adds them to the research table. Run this when you want to expand the tool list.
---

# find-mcp-tools

Find new MCP code-indexing tools and add them to `results/tools-data.json`.

## Read first (do this before searching)

1. `results/tools-data.json` — extract all `repo` values. These are already known; skip them.
2. `RESEARCH.md` — rules and inclusion criteria are defined there.
3. `scripts/search-queries.txt` — use these queries, in order, for `mcp__github__search_repositories`.

## Loop: for each search query

1. Run `mcp__github__search_repositories` with the query.
2. For each result not already in the exclusion list:
   - Read its README via `mcp__github__get_file_contents`
   - Confirm: has real MCP tools AND indexes local directories AND ≥1 star
   - If yes → append one entry to `results/tools-data.json` (copy schema from any existing entry)
3. Rate limit: sequential calls only, ~100ms apart. Never fire >3 in parallel.

## When done adding entries

```
python scripts/fetch_github_data.py
python scripts/generate_table.py --inject results/research-overview-2026-03-19.html
```

## Rules (short version — full rules in RESEARCH.md)

- No scores, no rankings, no eliminations — flat list only
- `license_warn: true` if license is unclear or non-commercial
- `air_gap_ok: "yes"` only if the README explicitly states offline/no-cloud
- Mark fields `"Not verified"` if you haven't read the README
- Aim for ≥5 new tools per run
