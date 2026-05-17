#!/usr/bin/env bash
# cbm-ui.sh — Manually spawn the codebase-memory-mcp graph UI.
#
# Usage:
#   bash .devcontainer/scripts/cbm-ui.sh
#
# Then open http://localhost:9749 in your browser.
# Port 9749 is already forwarded by devcontainer.json.
#
# This process is independent of Claude Code's STDIO MCP session.
# Both can run simultaneously — they share the same CBM_CACHE_DIR database.
set -euo pipefail

exec /usr/local/bin/codebase-memory-mcp \
    --ui=true \
    --host=0.0.0.0 \
    --port=9749
