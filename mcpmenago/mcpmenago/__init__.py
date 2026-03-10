"""mcpmenago — MCP Manager. Manages source code indexes for GitHub repositories."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mcpmenago")
except PackageNotFoundError:
    pass  # package is not installed
