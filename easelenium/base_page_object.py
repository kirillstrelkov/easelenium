"""Base page object."""


from easelenium.browser import Browser
from easelenium.utils import Logger


class BasePageObject:
    """Base page object."""

    def __init__(self, browser: Browser, logger: Logger) -> None:
        """Initiliaze."""
        self.browser = browser
        self.logger = logger
