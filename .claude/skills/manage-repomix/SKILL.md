---
name: manage-repomix
description: Use when indexing codebases or site-packages with Repomix MCP, managing packed indexes in .local-mcp/, or querying indexed modules
---

# Manage Repomix

Manage Repomix MCP indexes — build, query, and maintain packed codebases in `.local-mcp/`.

## Setup

- Check if the Repomix MCP server is connected — if not, offer to add it to `.mcp.json` and tell the user to reload MCP servers before continuing
- The `.mcp.json` entry must pin repomix to an exact npm registry version (not `latest`):
  ```json
  "repomix": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "repomix@<version>", "--mcp"]
  }
  ```
  When first adding, look up the latest published version on `yamadashy/repomix` via GitHub MCP and insert it.
- Ensure `.local-mcp/` is in `.gitignore` (index files are large and regeneratable) — keep `manifest.json` tracked by adding `!.local-mcp/manifest.json` after the ignore
- Do not attempt any other steps until the server is confirmed available

## Build Index

- **Tag clone**: ask user for repo and git tag — if no tag given, ask which version — shallow clone (`--depth 1`) into `.local-mcp/<module>/repo/` — pack into `.local-mcp/<module>/index.xml` filtering to relevant source files — after successful index build, ask the user if `.local-mcp/<module>/repo/` can be removed (default: yes, remove it)
- **Venv scan**: run `.venv/bin/pip list --format=columns` to show installed packages. Present the list to the developer and ask which packages to index. Then run `python .claude/scripts/build_repomix_indexes.py --package PKG1,PKG2,...` with their selection. Do not auto-index everything. If the developer explicitly asks for all packages, use `--build-all`.
- **Self-index**: pack the current working directory into `.local-mcp/self/index.xml` — respects `.gitignore` by default, version is the current git commit hash
- If intent is unclear, ask: "tag clone, .venv scan, or self-index?" — after packing, advise the user which temp directories can be cleaned up — output file is always `index.xml`

## Check for Updates

When asked to check for a new repomix version:
1. Read the current pinned version from `manifest.json` (`repomixVersion`) — this is the ground truth; also confirm it matches what is in `.mcp.json`
2. Fetch the latest release version from `yamadashy/repomix` via the GitHub MCP (`get_file_contents` on `package.json` at `HEAD`)
3. Compare against the pinned version — if newer, show: `repomix X.Y.Z → A.B.C available`
4. Ask for confirmation before writing any changes
5. On confirmation: update `.mcp.json` args to `repomix@A.B.C`, update `repomixVersion` in every manifest entry, and remind the user to reload MCP servers

## Manage

- Maintain `.local-mcp/manifest.json` tracking each module's name, version, output reference, `repomixVersion` (human-readable, e.g. `"1.12.0"`), and `lastIndexBuild` (ISO timestamp) — update all fields on every successful pack
- List or re-pack indexed modules by name
- Search across any indexed module using the Repomix search/grep tools

**Clone cleanup** (distinct from index deletion): after a tag-clone build, ask the user: "Remove the source clone at `.local-mcp/<module>/repo/`? (default: yes, or you can do it yourself)" — removing the clone does NOT remove the index

**Index deletion**: removing a module's index (`.local-mcp/<module>/index.xml`) and manifest entry is a destructive operation — list what will be removed and ask for explicit confirmation before proceeding

## Validate

After every pack, silently validate through the repomix MCP — do NOT use bash grep or file reads:

1. Use the repomix **attach** tool on the new index file
2. Use the repomix **search/grep** tool to query for a symbol known to exist in the package (e.g. main class or top-level function)
3. If matches are found → validation passes silently, proceed to update the manifest
4. If no matches or tool error → report the failure, suggest re-packing, do NOT update the manifest

## Settings

- After first successful pack, discover all available Repomix MCP tools and add only those that read data (query, search, read, grep) to `.claude/settings.json` `permissions.allow` — skip any that write or modify files
- Print which tools were added and which were skipped
