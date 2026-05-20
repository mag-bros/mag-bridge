"""MagBridge environment management — internal package.

Import order matters: utils defines `cli`, then command modules decorate it.
"""
from _env.utils import cli  # defines the Click group

# Import command modules to trigger @cli.command() registration
import _env.cmd_dev    # noqa: F401, E402
import _env.cmd_build  # noqa: F401, E402
import _env.cmd_npm    # noqa: F401, E402
import _env.cmd_ops    # noqa: F401, E402

__all__ = ["cli"]
