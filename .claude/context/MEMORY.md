# MEMORY

Shared project memory between sessions — the substrate for building a **personal co-work agent**. Organized well, it raises future-session accuracy. Auto-loaded on `/start`. Updated interactively via `/save` (only when context overflow is imminent — otherwise rigid append-only). Keep terse; file is loaded every session. Soft cap ≈ 200 lines.

**Origin:** `.claude2/` is the `mag-bridge/ai-internal` submodule (private). Trust-building phase — "we must first know each other better"; Claude does NOT have repo access yet.

**Context loop:** start-of-session reads this file; end-of-session writes back via `/save`.

---

# Working Principles

- No TDD-driven approach (no TDDA). Smoke tests + smart decisions over exhaustive verification.
- Decompose, don't explore. The plan is already good; refine details rather than re-investigating.
- Eyes on the prize: working dev environment, soon.
- Read user messages holistically first; group logical facts; then act. Don't act on first-pass parse.
- Update this file only with brief rationale; ask permission for non-trivial edits.

---

# TOOL ROUTER

**Rule:** Before each *substantial* request (web/docs/repo/codebase/research), propose a 1-line MCP choice as an A/B/C interactive prompt. Options 2–4 words each. The "Other" slot is the **comment** field — user types custom routing there.

**Example format:**
> For *"find latest FastAPI auth docs"*:
> A) context7  B) exa  C) tavily  *(or comment)*

**Defaults / preferences:**
- Prefer `exa.web_search_exa` over built-in `web_search`
- Prefer `exa.web_fetch_exa` over built-in `web_fetch`
- Prefer `context7` over web search for library/SDK/CLI docs

## MCP Catalog

*Descriptions refined via context7 lookup (Task #2 ✓). exa vs tavily disambiguated: **exa** = semantic neural search + direct-link fetch; **tavily** = real-time crawl/extract/map for site-wide research.*

- **context7** — Up-to-date library/framework/SDK/CLI docs optimized for AI code generation
  - resolve-library-id
  - query-docs
- **github** — GitHub repository, issue, PR, branch, file, and code operations
  - search_repositories
  - search_code
  - search_issues
  - search_users
  - get_file_contents
  - list_commits
  - list_issues
  - get_issue
  - create_issue
  - update_issue
  - add_issue_comment
  - list_pull_requests
  - get_pull_request
  - get_pull_request_comments
  - get_pull_request_files
  - get_pull_request_reviews
  - get_pull_request_status
  - create_pull_request
  - create_pull_request_review
  - merge_pull_request
  - update_pull_request_branch
  - create_branch
  - create_or_update_file
  - push_files
  - create_repository
  - fork_repository
- **repomix** — Pack codebases into AI-optimized single files for cross-file analysis and search
  - pack_codebase
  - pack_remote_repository
  - attach_packed_output
  - read_repomix_output
  - grep_repomix_output
  - file_system_read_file
  - file_system_read_directory
  - generate_skill
- **exa** — AI-powered semantic web search with embeddings, live crawling, and direct answers (needs `EXA_API_KEY`)
  - web_search_exa
  - web_fetch_exa
- **tavily** — Real-time web search plus intelligent extract, map, and systematic crawl tools (needs OAuth)
  - tavily_search
  - tavily_extract
  - tavily_crawl
  - tavily_map
  - tavily_research

---

# SKILL ROUTER

**Rule:** Before a substantial multi-step task, propose a 1-line skill choice as A/B/C interactive prompt. Options 2–4 words. "Other" slot = comment. Same pattern as TOOL ROUTER, but for skills (not MCPs).

**Example format:**
> For *"convert this paper PDF"*:
> A) /convert  B) inline-python  C) /repomix  *(or comment)*

**Defaults / preferences:**
- Prefer a triggering skill over inline reimplementation
- Read each skill's `description` frontmatter when triggering is ambiguous

## Skill Catalog

- `/electron-qa` — Visual UI verification via CDP screenshot after Angular edits
- `/find-mcp-tools` — Discover new MCP code-indexing tools on GitHub
- `/repomix` — Manage Repomix indexes in `.local-mcp/`
- `/convert` — Two-stage pipeline: PDF→MD (`pdf_to_md.py`, MinerU) then MD→JSON (`md_to_json.py`). Output next to input. `--details` keeps full MinerU tree.
- `/save` — Interactive MEMORY updater. Triggers ONLY when context overflow is imminent. Asks 1–2 rigid 5–8-word questions covering: passed / changed / wrong / what-else-to-update.
- `/mcp-creator` — Deploy a new MCP server. Spawns 3 sonnet sub-agents (tavily/exa/context7) with "think carefully" preamble; JUDGE merges into one `.mcp.json` stub with `${<SERVICE>_API_KEY}` placeholder. Never prompts for secrets.

---

# Project Status

- **Milestone:** Dev environment scaffolding — essentially done
- **Phase:** All 3 phases complete; only Task 7 (kpwydra real-run) pending — user is executing it
- **Eyes on prize:** Working dev environment, fast — achieved
- **Last session work:** Phase 1 + Phase 2 + Phase 3 finished. Refactored `scripts/pdf_to_md.py` (cross-platform: backend-subdir map, `--details` flag, sys.platform-gated env vars, install hint). Pinned deps in `requirements-dev.txt` (`mineru[pipeline]==3.1.14`, `markdown-it-py==4.2.0`, `mdit-py-plugins==0.6.1`). Stripped macOS-only fields from `mineru.json`. Validated end-to-end pipeline on `sample.pdf` (PDF→MD→JSON). Scaffolded `/convert`, `/save`, `/mcp-creator` skills.
- **Blockers:** exa 401 (deferred). kpwydra run executing on user's machine.
- **Resolved:** All 3 new skills exist. `mag-bros/mag-bridge` parent repo is public — GitHub MCP confirmed access.
- **Issue-naming convention** (from `mag-bros/mag-bridge`): `[<module>] <verb> <subject>` with label = module name. Modules: `core`, `backend`, `frontend`, `tests`, `data`, `notebooks`. Submodule additions: `[mcp]`, `[skill]`, `[ctx]`.

---

# Tasks

Issue-tracker mindset: each item is a discrete unit of work, terse but self-contained. Short tasks ≤10 words; complex ones may go to ~18-20 words when needed. Effort tag: **S**(<15min) / **M**(15-60min) / **L**(1-3h). Align names with `mag-bros/mag-bridge` issue tags once GitHub access is granted.

## Phase 1 — Foundation ✓
- [x] 1. Smoke-test all 5 MCPs (context7/github/repomix ✓; exa 401; tavily OAuth-pending)
- [x] 2. Refined exa/tavily/repomix/context7 descriptions via context7 lookup
- [x] 3. Replaced individual MCP entries with `mcp__<server>__*` wildcards in settings.json
- [x] 4. Audited `commands/start.md` — rewritten to align with new MEMORY.md structure
- [x] 5. Found mag-bridge issue convention: `[<module>] <verb> <subject>` with module-name labels

## Phase 2 — Build skills ✓ (cherry-pie running on user's machine)
- [x] 6. Scaffolded `/convert` skill — two-stage pipeline, routing prompt, failure modes
- [~] 7. /convert on kpwydra PDF — pipeline validated on `sample.pdf`; user running real kpwydra now
- [x] 8. Scaffolded `/save` skill at `.claude2/skills/save/SKILL.md`
- [x] 9. Encoded /save: overflow trigger, 5–8-word rigid questions, 4-category capture

## Phase 3 — Advanced ✓
- [x] 10. Env-var convention: `<SERVICE_UPPER>_API_KEY` (matches existing `EXA_API_KEY`, `TAVILY_API_KEY`, `CONTEXT7_API_KEY`); fall back to `_TOKEN` when official docs say so
- [x] 11. Stub template encoded in `/mcp-creator` SKILL.md (step 4); written on each invocation, not pre-seeded
- [x] 12. Scaffolded `/mcp-creator` at `.claude2/skills/mcp-creator/SKILL.md`
- [x] 13. JUDGE merge logic encoded: per-field reconciliation, authority tiebreaker (library vs hosted), github MCP tiebreaker on version disagreement
- [x] 14. SKILL ROUTER populated above with all 6 skills + A/B/C routing rule

---

# Locked-in Decisions

Reserved for architecture/conceptual tradeoffs. Keep minimal. Updates require user approval with brief rationale.

### [1] (placeholder)
- problem:
- decision:
