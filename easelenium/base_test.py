"""Base test."""
from __future__ import annotations

import traceback
from typing import Any
from unittest.case import TestCase

from easelenium.browser import Browser
from easelenium.utils import Logger, get_timestamp


class BaseTest(TestCase):
    """Base test."""

    TC_NAME_WIDTH = 100
    BROWSER_NAME = None
    FAILED_SCREENSHOT_FOLDER = None
    LOGGER = Logger(name="easyselenim.base_test.BaseTest")

    @classmethod
    def setUpClass(cls: type[BaseTest], **kwargs: dict[str, Any]) -> None:
        """Set up class."""
        super().setUpClass()

        kwargs["browser_name"] = kwargs.get("browser_name") or cls.BROWSER_NAME
        kwargs["logger"] = kwargs.get("logger") or cls.LOGGER

        cls.logger = kwargs["logger"]
        cls.browser = Browser(**kwargs)

    @classmethod
    def tearDownClass(cls: type[BaseTest]) -> None:
        """Tear down class."""
        super().tearDownClass()
        cls.browser.quit()

    def setUp(self) -> None:
        """Set up."""
        TestCase.setUp(self)
        if self.browser.logger:
            name = self.id()
            symbols_before = "-" * int((self.TC_NAME_WIDTH - len(name) - 2) / 2)
            self.browser.logger.info(  # noqa: PLE1205
                "{} {} {}",
                symbols_before,
                name,
                symbols_before,
            )

    def tearDown(self) -> None:
        """Tear down."""
        failed = True
        if hasattr(self, "_outcome"):
            # python3
            failed = self._outcome and not self._outcome.success
        elif hasattr(self, "_resultForDoCleanups") and hasattr(
            self._resultForDoCleanups,
            "result",
        ):
            # nose
            failed = not self._resultForDoCleanups.result.wasSuccessful()

        if failed:
            name = self.id()
            filename = f"{name}_{self.browser.get_browser_initials()}_{get_timestamp()}"
            try:
                self.browser.save_screenshot(
                    self.FAILED_SCREENSHOT_FOLDER,
                    filename + ".png",
                )
            except Exception:  # noqa: BLE001
                formatted_exc = traceback.format_exc()
                self.browser.logger.info(formatted_exc)
        TestCase.tearDown(self)

        if self.browser.logger:
            self.browser.logger.info("-" * self.TC_NAME_WIDTH)
