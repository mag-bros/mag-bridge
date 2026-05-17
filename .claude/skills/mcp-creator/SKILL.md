---
name: mcp-creator
description: Deploy a new MCP server fast and accurately. Use whenever the user asks to add, install, register, or set up an MCP server — e.g., "add a Linear MCP", "I need an MCP for Notion", "set up the Postgres MCP". Spawns 3 parallel sub-agents (one per docs-MCP: tavily, exa, context7), then merges findings into a single `.mcp.json` stub. Never prompts for credentials — emits a placeholder and tells the user where to add the token.
---

# /mcp-creator

Add a new MCP server entry to `.mcp.json` with the correct package name, version pin, and an `${ENV_VAR}` placeholder for the secret. The user fills in the token after.

## Trigger

User asks to add / install / register / set-up an MCP server — by name ("Linear MCP", "Slack MCP") or by need ("I want Claude to read my calendar"). Both trigger.

If the requested MCP already exists in `.mcp.json`, **skip research** → tell the user it's already configured and offer to refresh the version pin instead. Cheap to detect, expensive to repeat the JUDGE pattern unnecessarily.

## Process

### 1. Identify target

Extract from the user's message:
- **Service name** (e.g. "Linear", "Notion", "Postgres")
- **Transport hint**, if any ("HTTP", "stdio", "remote")

If ambiguous, ask one focused question, ≤ 8 words. Example: *"Which MCP server? (e.g. Linear, Slack)"*

### 2. Spawn 3 research sub-agents in parallel

In a single turn, fire 3 `general-purpose` sub-agents. Each uses **exactly one** docs MCP — splitting the search surface across complementary sources is the whole point. Use `model: sonnet` (current latest = sonnet 4.6) and prepend each prompt with **"Think carefully and verify your findings before reporting."** to approximate medium-thinking budget.

| Agent | MCP | Strength | Best for |
|---|---|---|---|
| A | `tavily` | HTML crawl, TOC scraping, repetitive-page traversal | Project README + docs sites with many install variants |
| B | `exa` | Direct-link fetch + semantic web search | Authoritative install instructions, env-var names, version |
| C | `context7` | Deepest detail for library/SDK docs | Library-style MCPs (npm packages, Python packages) |

**Prompt template for each sub-agent:**

> Think carefully and verify your findings before reporting.
> Find install instructions for the `<SERVICE>` MCP server. Return JSON only:
> ```
> {
>   "name": "<service-lowercase>",
>   "transport": "stdio" | "http",
>   "command": "...",
>   "args": [...],
>   "env_vars": {"VAR_NAME": "purpose"},
>   "latest_version": "x.y.z",
>   "source_url": "https://...",
>   "notes": "any caveat"
> }
> ```
> Use **only** the `<MCP>` MCP tools. Do not use web_search/web_fetch. If you can't find authoritative info, return `null` and explain why.

Tell the user once that research is in flight; don't poll the agents — wait for completion notifications.

### 3. JUDGE — merge into one stub

When all 3 reports return:

- **Field-by-field reconciliation:**
  - `command`, `args`, `latest_version`: pick the most-frequent value, or the one from the most-authoritative source
  - **Authority tiebreaker — depends on MCP type:**
    - Library-style (npm/pip package): `context7 > exa > tavily`
    - Hosted-service-style (Slack, Notion, Linear): `tavily > exa > context7`
- `env_vars`: union (never drop a needed secret)
- `source_url`: prefer `github.com/<org>/<repo>` over wrappers/aggregators
- **Version tiebreaker (last resort):** use `mcp__github__get_file_contents` on the source repo's `pyproject.toml` or `package.json` to read the ground-truth version

If reports disagree significantly (different package names, different transports), **surface the disagreement to the user** before writing — better to ask than to commit a wrong entry.

### 4. Generate the `.mcp.json` stub

Append (or replace if upgrading) the entry. Read `.mcp.json` first; insert into the `mcpServers` object alphabetically; preserve trailing newline.

**Template:**

```json
"<service-lc>": {
  "type": "<stdio|http>",
  "command": "npx",
  "args": ["-y", "<package-name>@<version>"],
  "env": {
    "<SERVICE>_API_KEY": "${<SERVICE>_API_KEY}"
  }
}
```

**For HTTP transport:**

```json
"<service-lc>": {
  "type": "http",
  "url": "https://<endpoint>"
}
```

**Env-var convention:** `<SERVICE_UPPER>_API_KEY` matches what's already in this project (`EXA_API_KEY`, `TAVILY_API_KEY`, `CONTEXT7_API_KEY`, `GITHUB_TOKEN`). Use `_TOKEN` instead if the official docs say so. **One env var per credential** — never reuse another service's variable.

### 5. Tell the user where the token goes (verbatim)

> Added `<service>` to `.mcp.json`. You now can add the token:
> 1. Edit `.env` and set `<SERVICE>_API_KEY=<your-token>`
> 2. Reload MCPs (`/mcp` slash command, or restart Claude Code)
> 3. Verify with a smoke-test tool call

**Never prompt** the user to paste the secret into the chat — secrets in chat history are a leak vector.

## Don'ts

- Don't write the token into `.mcp.json` directly — only `${...}` references
- Don't restart Claude Code or modify the shell env yourself
- Don't add the new entry to MEMORY.md's `TOOL ROUTER` catalog automatically — that's `/save`'s job, after the user verifies the MCP works
- Don't spawn the 3 research sub-agents if the MCP is already configured (check `.mcp.json` first)
- Don't fabricate an MCP entry when the requested service doesn't actually have one — say so plainly

## Failure modes

- **All 3 agents fail** (no internet, all MCPs rate-limited, etc.) → report which agents failed and ask the user for the install command directly. Don't guess.
- **2 of 3 disagree on version** → fall back to `mcp__github__get_file_contents` on the source repo for ground truth
- **Service isn't actually an MCP** (only a regular API) → tell the user honestly; offer to scaffold a custom wrapper if they want
- **JUDGE finds the MCP needs OAuth, not a static token** → emit the HTTP transport stub and note: "auth is OAuth — first call will trigger the flow"

## After-action

Report concisely: which agents agreed, which disagreed, the final stub, and the next user action. Three bullets max.
