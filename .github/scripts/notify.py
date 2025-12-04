import os
from webbrowser import get

"""Script to notify a Discord channel about the release build summary."""


def get_discord_webhook() -> str:
    """Load Discord webhook URL from environment in a safe way."""
    webhook: str | None = os.environ.get("DISCORD_WEBHOOK_URL")

    if not webhook or not webhook.strip():
        raise RuntimeError("DISCORD_WEBHOOK_URL secret is missing or empty")

    return webhook.strip()


def send_discord_message(webhook_url: str, message: str) -> None:
    """TODO::
    - start with creating ReleaseSummary class to hold all data in one place
    - Include a nice visual summary of the build results
    - Both informational and naming patterns - see our others Discord notifications
    """
    print("Sending release summary notification...")
    ...
