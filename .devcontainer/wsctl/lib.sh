#!/usr/bin/env bash
# wsctl/lib.sh — shared helpers for wsctl. Sourced by ./wsctl.
# Standalone by design: the whole wsctl/ dir is copied together (see install.sh).
# No `set -e` here (this file is sourced); the dispatcher owns shell options.
# Portable: bash 3.2+ (macOS), Linux, Windows-via-bash; BSD/GNU differences handled inline.
#
# Requires the caller to export ROOT (repo root).

# --- color: TTY-aware on stderr. COLOR=1 force · COLOR=0 plain · COLOR=auto (default) ---
COLOR="${COLOR:-auto}"
[ "$COLOR" = auto ] && { [ -t 2 ] && COLOR=1 || COLOR=0; }
if [ "$COLOR" = 0 ]; then C_RED=""; C_YEL=""; C_GRN=""; C_DIM=""; C_BLD=""; C_RST=""
else C_RED=$'\033[31m'; C_YEL=$'\033[33m'; C_GRN=$'\033[32m'; C_DIM=$'\033[2m'; C_BLD=$'\033[1m'; C_RST=$'\033[0m'; fi

# --- output: everything to stderr, so stdout stays clean if a verb ever pipes data ---
log()  { printf '%s%s%s\n' "$C_DIM" "$*" "$C_RST" >&2; }
info() { printf '%s\n' "$*" >&2; }
ok()   { printf '%s✓%s %s\n' "$C_GRN" "$C_RST" "$*" >&2; }
warn() { printf '%s⚠%s %s\n' "$C_YEL" "$C_RST" "$*" >&2; }
die()  { printf '%s✗ %s%s\n' "$C_RED$C_BLD" "$*" "$C_RST" >&2; exit "${2:-1}"; }

# --- the two private submodules — single source of truth (space-list; names carry no spaces/globs) ---
SUBMODULES=".claude devcontainers"
url_for() { case "$1" in
  .claude)       printf 'https://github.com/Sevelantis/.claude.git' ;;
  devcontainers) printf 'https://github.com/Sevelantis/devcontainers.git' ;;
  *) return 1 ;;
esac; }
valid_submodule() { local x; for x in $SUBMODULES; do [ "$x" = "$1" ] && return 0; done; return 1; }

GH_MATCH="https://github.com/"   # URL-scope for the token header (never bare — QA hardening)
TOKEN_VAR="GH_TOKEN_RO_INFRA"
GIT_MIN="2.31"                    # GIT_CONFIG_COUNT support floor

# --- git version floor (QA flag: assert, don't assume) ---
git_version() { git --version 2>/dev/null | awk '{print $3}' || true; }   # `|| true`: same pipefail-abort guard as read_token
version_ge() {   # version_ge A B → exit 0 if A >= B. Portable (no `sort -V`, absent on old BSD).
  awk -v a="$1" -v b="$2" 'BEGIN{
    na=split(a,x,"."); nb=split(b,y,"."); n=(na>nb)?na:nb
    for(i=1;i<=n;i++){ ai=(i<=na)?x[i]+0:0; bi=(i<=nb)?y[i]+0:0
      if(ai>bi){exit 0}; if(ai<bi){exit 1} } exit 0 }'
}
require_git_version() {
  local v; v="$(git_version)"; [ -n "$v" ] || die "git not found on PATH"
  version_ge "$v" "$GIT_MIN" || die "git $v is too old — wsctl needs git >= $GIT_MIN (for GIT_CONFIG_COUNT). Please update git."
}

# --- token: read from .env at point-of-use (never an ambient var, never persisted by us elsewhere) ---
read_token() {   # echoes the token, or nothing. MUST return 0 even when absent:
  # under `set -e`+`pipefail` a failing grep here would silently abort the caller before its error message.
  [ -f "$ROOT/.env" ] || return 0
  grep -E "^${TOKEN_VAR}=" "$ROOT/.env" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '"'\'' ' || true
}
persist_token() {   # persist_token <tok> → write into $ROOT/.env (0600). PATs are [A-Za-z0-9_], safe for the | delimiter.
  local tok="$1" tmp; tmp="$(mktemp)"
  if grep -qE "^${TOKEN_VAR}=" "$ROOT/.env" 2>/dev/null; then
    sed "s|^${TOKEN_VAR}=.*|${TOKEN_VAR}=${tok}|" "$ROOT/.env" > "$tmp"
  else
    { [ -f "$ROOT/.env" ] && cat "$ROOT/.env"; printf '%s=%s\n' "$TOKEN_VAR" "$tok"; } > "$tmp"
  fi
  mv "$tmp" "$ROOT/.env"; chmod 600 "$ROOT/.env"
}

# --- run git with the RO token injected ephemerally, SCOPED to github.com only ---
# QA hardening: a URL-scoped `http.https://github.com/.extraHeader` sends the Authorization ONLY to
# github.com; a bare `http.extraHeader` would leak it to any https host git contacts in the invocation.
# The token never touches the URL, argv, .git/config, or logs.
git_ro() {   # git_ro <token> <git args...>
  local tok="$1"; shift
  local b64; b64="$(printf 'x-access-token:%s' "$tok" | base64 | tr -d '\n')"
  GIT_TERMINAL_PROMPT=0 \
  GIT_CONFIG_COUNT=1 \
  GIT_CONFIG_KEY_0="http.${GH_MATCH}.extraHeader" \
  GIT_CONFIG_VALUE_0="Authorization: Basic ${b64}" \
    git "$@"
}

# --- submodule state helpers ---
current_branch() { git -C "$ROOT/$1" symbolic-ref --quiet --short HEAD 2>/dev/null || printf '(detached)'; }
ensure_on_branch() {   # if detached, try to land on master (belt-and-suspenders; `submodule add` usually lands on a branch)
  git -C "$ROOT/$1" symbolic-ref -q HEAD >/dev/null 2>&1 && return 0
  git -C "$ROOT/$1" checkout -q master 2>/dev/null || true
}
diagnose_pull() {   # diagnose_pull <submodule> <git-output> — separate auth failure from dirty/diverged
  local s="$1" out="$2"
  case "$out" in
    *"could not read Username"*|*"Authentication failed"*|*"terminal prompts disabled"*|*"403"*)
      warn "$s: AUTH failed — $TOKEN_VAR is missing/expired/under-scoped (needs Contents:Read on $s), or (in-container) the gateway stripped the auth header." ;;
    *"non-fast-forward"*|*"Not possible to fast-forward"*|*"diverged"*|*"have diverged"*)
      warn "$s: DIVERGED — local commits not on the remote branch. Resolve with git, then re-run." ;;
    *"local changes"*|*"overwritten"*|*"uncommitted"*|*"stash"*)
      warn "$s: DIRTY — uncommitted local changes. Commit or stash them, then re-run." ;;
    *) warn "$s: pull failed — see git output above." ;;
  esac
}
