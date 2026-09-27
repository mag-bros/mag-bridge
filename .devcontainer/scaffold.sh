#!/usr/bin/env bash
# scaffold.sh — drop the standard AI-platform static config into a repo.
#   Creates root .npmrc + .mcp.json (idempotent, never clobbers) and ensures
#   .gitignore hygiene entries. Copy-paste this file into any repo's
#   .devcontainer/ and run it. Portable: bash 3.2+ (macOS default host shell).
#   No secrets: .mcp.json ships ${ENV} placeholders only.
#
# Usage:
#   bash .devcontainer/scaffold.sh           # create missing files (keep existing)
#   bash .devcontainer/scaffold.sh --check   # report only; exit 1 if anything missing
#   bash .devcontainer/scaffold.sh --force   # overwrite .npmrc + .mcp.json with the template
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"   # repo root = parent of .devcontainer/

MODE=create
case "${1:-}" in
  --check)     MODE=check ;;
  --force)     MODE=force ;;
  -h|--help)   sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  "")          ;;
  *)           echo "unknown arg: $1 (try --help)" >&2; exit 2 ;;
esac

GITIGNORE_ENTRIES=(".mcp.idx" ".ai/" "*.env")
MARKER="# --- AI platform scaffold (managed) ---"
MISSING=0

# ---- templates (quoted heredoc → ${ENV} stays literal, never expanded) ----
gen_npmrc() { cat <<'EOF'
# npm settings for installs routed through the pipelock egress proxy.
maxsockets=3        # parallel downloads; 8 (loopback-tuned) overwhelmed the cross-container scan pipeline → cancel/retry churn. Lower = fewer resets; raise if installs are too slow once the gateway response-scan is exempted.
fetch-retries=5     # retry a reset download instead of failing the whole install
fetch-retry-maxtimeout=120000
fetch-timeout=600000
EOF
}

gen_env() { cat <<'EOF'
# Onboarding scaffold — fill in real values, then (re)open the container. NEVER commit real values.
# IMPORTANT: keep every comment on its OWN line. `docker compose --env-file` does NOT strip an inline
# `# ...` from a value — `KEY=val # note` becomes the literal value `val # note`.

# --- Tier-1 per-project tenancy (REQUIRED, unique per repo) ---
# COMPOSE_PROJECT_NAME: DNS/volume-safe (lowercase, digits, underscore). Do NOT change it on an existing
#   repo — it renames the ${project}_claude volume and orphans your auth + Claude Code memory.
COMPOSE_PROJECT_NAME=changeme
# DEVCONTAINER_INGRESS_PORT: a UNIQUE host port per concurrently-run repo (7700, 7701, 7702, …).
#   Left non-numeric on purpose so the platform's initializeCommand guard blocks the rebuild until you set it.
DEVCONTAINER_INGRESS_PORT=CHANGE_ME

# --- Python path (project layout) ---
PYTHONPATH="src:src/converter:tests:devcontainers/workspace/tests:.:./compressor-archive"

# --- GitHub tokens (fine-grained PATs) ---
# GH_TOKEN_RO_INFRA: READ-ONLY, access to the private submodules (Sevelantis/.claude + Sevelantis/devcontainers).
#   This is the onboarding/setup token — used to fetch the submodules.
GH_TOKEN_RO_INFRA=
# GH_TOKEN_RW: read/write — only if you push from inside the container.
GH_TOKEN_RW=

# --- MCP server API keys (blank = that server stays disabled) ---
CONTEXT7_API_KEY=
EXA_API_KEY=
TAVILY_API_KEY=
GEMINI_API_KEY=

# --- App secrets ---
OH_SECRET_KEY=
LOCAL_BACKEND_API_KEY=
EOF
}

gen_mcp() { cat <<'EOF'
{
  "mcpServers": {
    "codebase-memory": {
      "type": "stdio",
      "command": "/usr/local/bin/codebase-memory-mcp",
      "args": []
    },
    "context7": {
      "type": "stdio",
      "command": "context7-mcp",
      "args": [],
      "env": {
        "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
      }
    },
    "github": {
      "type": "stdio",
      "command": "mcp-server-github",
      "args": [],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GH_TOKEN}"
      }
    },
    "repomix": {
      "type": "stdio",
      "command": "repomix",
      "args": ["--mcp"]
    },
    "tavily": {
      "command": "tavily-mcp",
      "args": [],
      "env": {
        "TAVILY_API_KEY": "${TAVILY_API_KEY}"
      }
    },
    "exa": {
      "type": "stdio",
      "command": "exa-mcp-server",
      "args": [],
      "env": {
        "EXA_API_KEY": "${EXA_API_KEY}"
      }
    },
    "pdf-reader": {
      "type": "stdio",
      "command": "pdf-reader-mcp",
      "args": []
    },
    "playwright": {
      "type": "stdio",
      "command": "playwright-mcp",
      "timeout": 30,
      "tools": ["*"],
      "args": [
        "--browser",
        "chromium",
        "--headless",
        "--no-sandbox",
        "--executable-path",
        "/usr/bin/chromium",
        "--viewport-size",
        "720x900",
        "--output-dir",
        ".playwright-mcp"
      ],
      "disabled": false
    },
    "jcodemunch": {
      "type": "stdio",
      "command": "uvx",
      "args": ["jcodemunch-mcp"]
    },
    "yfinance": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "yfmcp", "yfmcp"]
    }
  }
}
EOF
}

# ---- file handling: create if missing, keep unless --force ----
handle_file() {
  name="$1"; gen="$2"; mode="${3:-}"; path="$ROOT/$name"
  if [ -f "$path" ]; then
    case "$MODE" in
      force) "$gen" > "$path"; [ -n "$mode" ] && chmod "$mode" "$path"; echo "  ~ $name  overwritten (--force)" ;;
      check) echo "  = $name  present" ;;
      *)     echo "  = $name  present (kept)" ;;
    esac
  else
    case "$MODE" in
      check) echo "  ✗ $name  MISSING"; MISSING=1 ;;
      *)     "$gen" > "$path"; [ -n "$mode" ] && chmod "$mode" "$path"; echo "  + $name  created" ;;
    esac
  fi
}

# ---- .gitignore: ensure each entry exists (append missing under a marker) ----
ensure_gitignore() {
  gi="$ROOT/.gitignore"
  missing=()
  for entry in "${GITIGNORE_ENTRIES[@]}"; do
    if [ -f "$gi" ] && grep -qxF "$entry" "$gi" 2>/dev/null; then
      [ "$MODE" = check ] && echo "  = .gitignore: $entry"
    elif [ "$MODE" = check ]; then
      echo "  ✗ .gitignore: $entry  MISSING"; MISSING=1
    else
      missing+=("$entry")
    fi
  done
  if [ "${#missing[@]}" -gt 0 ]; then
    {
      [ -f "$gi" ] && [ -s "$gi" ] && printf '\n'
      grep -qxF "$MARKER" "$gi" 2>/dev/null || printf '%s\n' "$MARKER"
      printf '%s\n' "${missing[@]}"
    } >> "$gi"
    echo "  + .gitignore: added ${missing[*]}"
  fi
}

echo "scaffold ($MODE) → $ROOT"
handle_file ".npmrc"    gen_npmrc
handle_file ".mcp.json" gen_mcp
handle_file ".env"      gen_env 600
ensure_gitignore

if [ "$MODE" = check ] && [ "$MISSING" -ne 0 ]; then
  echo "scaffold: incomplete — run 'bash .devcontainer/scaffold.sh' to fix" >&2
  exit 1
fi
echo "scaffold: ok"
