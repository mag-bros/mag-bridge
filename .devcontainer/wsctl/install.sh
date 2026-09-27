#!/usr/bin/env bash
# wsctl/install.sh — put `wsctl` on your shell (marker-fenced, idempotent). Ensures target state:
# REPLACES the managed block if present, ADDS it if missing. Paths derive from THIS script's location,
# so they can't drift from where you copied the folder. Mirrors docker-health/install.sh.
#
#   bash install.sh [zsh|bash]     # shell explicit; default: detected from $SHELL
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

sh="${1:-$(basename "${SHELL:-bash}")}"
case "$sh" in
  zsh)  rc="$HOME/.zshrc" ;;
  bash) rc="$HOME/.bashrc" ;;
  *) echo "usage: bash install.sh [zsh|bash]" >&2; exit 2 ;;
esac
touch "$rc"

BEGIN='# >>> wsctl >>>'
END='# <<< wsctl <<<'
# refuse to touch a hand-corrupted rc: an unmatched BEGIN would make the range-delete eat to EOF
nb=$(grep -cxF "$BEGIN" "$rc" || true); ne=$(grep -cxF "$END" "$rc" || true)
[ "$nb" = "$ne" ] || { echo "wsctl: unbalanced markers in $rc ($nb begin / $ne end) — fix manually, then re-run" >&2; exit 3; }

tmp="$(mktemp)"
# clean slate: drop any prior managed block. `|| :` so an all-filtered rc (grep exits 1) doesn't abort under set -e+pipefail.
sed "/$BEGIN/,/$END/d" "$rc" > "$tmp" || :

# `wsctl` = the tool name itself (no cryptic alias). Runs via bash so no exec bit is needed (survives copy on any OS).
cat >> "$tmp" <<BLOCK
$BEGIN
alias wsctl='bash "$DIR/wsctl"'
$END
BLOCK

mv "$tmp" "$rc"
echo "wsctl: wired into $rc"
echo "  usage: wsctl --help   (restart your shell, or:  source $rc)"
