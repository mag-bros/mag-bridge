"""Global path constants for mcpmenago.

All paths are anchored to this file's location so they resolve correctly
regardless of the working directory from which mcpmenago is invoked.
"""

from __future__ import annotations

from pathlib import Path

# mcpmenago/mcpmenago/ → mcpmenago/
MCPMENAGO_ROOT = Path(__file__).parent.parent

# mcpmenago/library/
LIBRARY = MCPMENAGO_ROOT.joinpath("library")

# mcpmenago/mcpmenago.json
CONFIG_PATH = MCPMENAGO_ROOT.joinpath("mcpmenago.json")

# host project root (mag-bridge/)
PROJECT_ROOT = MCPMENAGO_ROOT.parent

# host project .gitignore
GITIGNORE = PROJECT_ROOT.joinpath(".gitignore")
