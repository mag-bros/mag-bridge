import os

from scripts.messages import DiscordMessage

"""Script to notify a Discord channel about the release build summary."""


def send_notification(message: DiscordMessage) -> None:
    """TODO::
    - Include a nice visual summary of the build results
    - Both informational and naming patterns - see our others Discord notifications
    """
    print("Sending release summary notification...")
    ...
