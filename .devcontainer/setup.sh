#!/usr/bin/env bash
# setup.sh — interactive onboarding for a project (fresh or existing). Run once:
#     bash .devcontainer/setup.sh
# It (1) scaffolds .env/.mcp.json/.npmrc, (2) prompts for your READ-ONLY GitHub token
# (hidden — never echoed or in shell history), stores it in .env (0600), and (3) ensures the two
# private submodules (.claude, devcontainers): on a FRESH repo it ADDS them (clone + register +
# .gitmodules); on a repo that already has them it UPDATES. The token reaches git via env config
# only (never argv/URL/.git-config), so it stays out of every log and process listing.
# It reports success or failure honestly and exits non-zero if a submodule can't be set up.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
ROOT="$(dirname "$DIR")"
ENV="$ROOT/.env"

# 1. static config files (idempotent; creates .env from template if absent)
bash "$DIR/scaffold.sh"

# submodules can't exist outside a git repo — fail early and clearly
git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1 || {
  echo "  ✗ $ROOT is not a git repository — run 'git init' (or clone) first, then re-run." >&2
  exit 1
}

# 2. token — reuse .env's GH_TOKEN_RO_INFRA if filled, else prompt (hidden) and persist
read_env_token() { grep -E '^GH_TOKEN_RO_INFRA=' "$ENV" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '"'\''  '; }
tok="$(read_env_token)"
if [ -z "$tok" ]; then
  printf 'Paste your READ-ONLY GitHub token (GH_TOKEN_RO_INFRA) — input hidden: ' >&2
  read -rs tok; echo >&2
  [ -n "$tok" ] || { echo "  ✗ no token entered — aborting" >&2; exit 1; }
  tmp="$(mktemp)"
  if grep -qE '^GH_TOKEN_RO_INFRA=' "$ENV"; then
    sed "s|^GH_TOKEN_RO_INFRA=.*|GH_TOKEN_RO_INFRA=${tok}|" "$ENV" > "$tmp"
  else
    cat "$ENV" > "$tmp"; printf 'GH_TOKEN_RO_INFRA=%s\n' "$tok" >> "$tmp"
  fi
  mv "$tmp" "$ENV"; chmod 600 "$ENV"
  echo "  ✓ token saved to .env (0600)" >&2
else
  echo "  = GH_TOKEN_RO_INFRA already set in .env" >&2
fi

# 3. submodules — ADD on a fresh repo, UPDATE if already present.
#    Token via git ENV config only (inherited by the child clone; never argv/history/.git-config).
b64="$(printf 'x-access-token:%s' "$tok" | base64 | tr -d '\n')"
export GIT_TERMINAL_PROMPT=0 GIT_CONFIG_COUNT=1 \
  GIT_CONFIG_KEY_0=http.extraHeader GIT_CONFIG_VALUE_0="Authorization: Basic ${b64}"

ensure_sub() {          # ensure_sub <path> <url>  → 0 ok, 1 failed
  path="$1"; url="$2"
  if [ -e "$ROOT/$path/.git" ]; then
    git -C "$ROOT" submodule update --init "$path" >/dev/null 2>&1 \
      && { echo "    = $path present — updated" >&2; return 0; }
    echo "    ✗ $path present but update FAILED" >&2; return 1
  fi
  if git -C "$ROOT" submodule add --force "$url" "$path" >/dev/null 2>&1; then
    git config -f "$ROOT/.gitmodules" "submodule.$path.ignore" all >/dev/null 2>&1 || true
    echo "    + $path added (cloned + registered, ignore=all)" >&2; return 0
  fi
  echo "    ✗ $path add FAILED — does GH_TOKEN_RO_INFRA have read access to $url ?" >&2; return 1
}

echo "  → ensuring submodules …" >&2
subs_ok=1
ensure_sub ".claude"       "https://github.com/Sevelantis/.claude.git"       || subs_ok=0
ensure_sub "devcontainers" "https://github.com/Sevelantis/devcontainers.git" || subs_ok=0
unset GIT_CONFIG_COUNT GIT_CONFIG_KEY_0 GIT_CONFIG_VALUE_0

# 4. honest summary — only claim success when the submodules are actually in place
echo >&2
if [ "$subs_ok" = 1 ]; then
  cat >&2 <<'EOF'
  ✅ Onboarding ready — submodules in place (staged for commit).
  Next:
    • set COMPOSE_PROJECT_NAME (unique, lowercase) + DEVCONTAINER_INGRESS_PORT (unique) in .env
    • VS Code → Reopen in Container
EOF
else
  cat >&2 <<'EOF'
  ❌ Setup INCOMPLETE — a submodule could not be set up (see ✗ above).
     Most likely GH_TOKEN_RO_INFRA lacks read access to a Sevelantis repo, or the token expired.
     Fix GH_TOKEN_RO_INFRA in .env, then re-run:  bash .devcontainer/setup.sh
EOF
  exit 1
fi
