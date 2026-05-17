# /start

You are starting a new session on **MagBridge AI** — the `.claude2/` submodule of `mag-bros/mag-bridge`. You have no memory of prior sessions; everything comes from the files below.

## Read in order
1. **`context/MEMORY.md`** (auto-loaded) — internalize, in this order:
   - **Working Principles** — how we work (no TDDA, decompose-don't-explore, eyes on the prize)
   - **TOOL ROUTER** — *mandatory*: before each substantial request, propose A/B/C MCP choice via interactive prompt (Other-slot = comment)
   - **SKILL ROUTER** — same pattern, applied to skills
   - **Project Status** — milestone, phase, blockers, **Last session work**
   - **Tasks** — current Phase, what's done, what's next
   - **Locked-in Decisions** — architecture tradeoffs (rarely changes; ask before edits)
2. **`context/status.md`** — long-running overview ("where are we?")
3. **`CLAUDE.md`** — MagBridge project rules (already loaded)

## Confirm to the user (briefly)
- Current Phase + next 1–3 unchecked tasks
- What changed since last session (read `Last session work` in MEMORY)
- Any open blockers worth raising now

## Naming convention
Issues, tasks, PRs follow `[<module>] <verb> <subject>`. Modules: `core`, `backend`, `frontend`, `tests`, `data`, `notebooks`, `mcp`, `skill`, `ctx`.

## Then ask
"What do you want to work on this session?"
