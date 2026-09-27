# Quickstart

Get your workspace synced and open in about five minutes. This pulls the two private platform
components (`.claude/` and `devcontainers/`) and opens your dev container.

## Before you start

- **Docker** and **VS Code** with the **Dev Containers** extension.
- **git ≥ 2.31** — check with `git --version`.
- The **read-only access token** you were given (it looks like `github_pat_…`). `wsctl` uses it only
  to pull the two components — it never pushes and never rebuilds.
- This project already cloned and open on your machine.

## 1. Sync the workspace

From the project root:

```bash
bash .devcontainer/wsctl/wsctl setup
```

Paste your token when asked — the input stays hidden.

**You should see:**

```
✓ onboarding ready — submodules in place.
```

## 2. Name your workspace and open it

Set two values in `.env`, then run **Reopen in Container** in VS Code:

| key | value |
| --- | --- |
| `COMPOSE_PROJECT_NAME` | a unique lowercase name, e.g. `dev-jane` |
| `DEVCONTAINER_INGRESS_PORT` | a unique port, e.g. `7700` |

Your container builds and opens. **Your workspace is ready.**

## Keeping it up to date

Pull the latest platform changes anytime:

```bash
bash .devcontainer/wsctl/wsctl update
```

It shows exactly what changed, or `Already up to date.`

## If something goes wrong

| You see | Do this |
| --- | --- |
| `GH_TOKEN_RO_INFRA is not set` | Re-run step 1 and paste your token. |
| `AUTH failed` / `clone FAILED` | Your token is wrong or expired — ask your admin for a fresh one. |

---

**Next:** run your own containers alongside the workspace → [README.md](README.md).
