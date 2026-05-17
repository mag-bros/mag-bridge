---
name: save
description: Interactively persist the current session's state into `.claude2/context/MEMORY.md` so the next session can pick up cold. Use ONLY when invoked via `/save` OR when the user explicitly says the context window is filling up / nearly overflowing — never proactively at session end. Captures what passed, what changed, what was wrong, what else to update.
---

# /save

End-of-session memory writer. Updates `.claude2/context/MEMORY.md` with whatever from this session matters for next session's cold start.

## When to run

- User explicitly types `/save`.
- User says any of: "context is overflowing", "running out of context", "save before we lose it", "checkpoint", "context window almost full".
- **Do NOT trigger** on normal session-end, completion of a single task, or polite goodbyes. Memory churn = noise.

The overflow constraint exists because once context is truly full the user can no longer answer questions — so save earlier, when the user can still respond.

## Process

### 1. Re-read context

Read `.claude2/context/MEMORY.md` in full. Re-read `.claude2/context/status.md` if relevant. Hold the current state in mind before mutating it.

### 2. Ask 1-2 rigid clarifying questions

Each question: **5–8 words. Numbered. Almost rigid word count.** No prose, no preamble.

Pick the questions from these four categories — choose the 1–2 that matter most for this session:

1. **What passed** — successes, smoke-tests green, tasks closed
2. **What changed** — files touched, decisions made, structures altered
3. **What was wrong** — failures, blockers discovered, dead-ends, misreads
4. **What else to update** — anything the user wants captured that the agent missed

Examples (count the words):
- "Which Phase 1 tasks now complete?" (5)
- "What changed in MEMORY structure today?" (6)
- "Which blockers should next session see?" (6)
- "Anything specific to add to status?" (6)

If only one category obviously matters, ask one question. If two are equally important, ask two. Never more.

### 3. Apply edits

Use `Edit` (not `Write`) to mutate MEMORY.md in place. Targets:
- **Project Status → Last session work** — append/replace the one-sentence summary
- **Project Status → Blockers** — add/remove
- **Tasks** — flip `[ ]` to `[x]`, append new tasks at end of relevant Phase, never reorder past entries
- **Locked-in Decisions** — only on user direction with explicit rationale

Soft cap ≈ 200 lines — if approaching, prune completed tasks rather than archive (they live in git history).

### 4. Report

One short message: "MEMORY updated. Changes: …". Three bullets max. Done.

## What NOT to write

- Conversation transcripts (git log + git diff carry that).
- Generic principles (already in Working Principles section).
- "We did X then Y then Z" narratives — capture the *outcomes*, not the steps.
- File paths the next agent can find by `ls`.

## Output discipline

This skill exists to make next-session start fast. Every line added must be load-bearing for cold-start understanding. If you can't articulate why a future-you needs the line, don't write it.
