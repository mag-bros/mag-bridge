class DiscordMessage:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url


class ReleaseSummaryMessage(DiscordMessage):
    """Contains a release summary message information."""

    # TODO::
    ...
