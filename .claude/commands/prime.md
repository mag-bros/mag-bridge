# Prime Command: Session Initialization

You are starting a new session on the MagBridge project. You have no memory of previous sessions. All context comes from files.

**Load context in this order:**

1. `MEMORY.md` is already loaded (auto-injected). Read it carefully — it contains the tech stack, architecture, and locked decisions.
2. Read `.claude/context/status.md` — this is the ground truth of what exists on disk RIGHT NOW.
3. Read `.claude/context/PLAN.md` — find the current milestone and phase (first unchecked `[ ]`).
4 Read `.claude/context/substruct-matching.md` — ground truth related to first big project's milestone.

**After loading, confirm:**
- Current milestone and phase
- What exists on disk vs what's planned next
- Any blockers or open questions from the plan

**Then ask the user what they want to work on this session.**
