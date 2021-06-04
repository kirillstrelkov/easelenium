# coding=utf8
import traceback
from unittest.case import TestCase

from easelenium.browser import Browser
from easelenium.utils import Logger, get_timestamp


class BaseTest(TestCase):
    TC_NAME_WIDTH = 100
    BROWSER_NAME = None
    FAILED_SCREENSHOT_FOLDER = None
    LOGGER = Logger(name="easyselenim.base_test.BaseTest")

    @classmethod
    def setUpClass(cls, **kwargs):
        super(BaseTest, cls).setUpClass()

        kwargs["browser_name"] = kwargs.get("browser_name") or cls.BROWSER_NAME
        kwargs["logger"] = kwargs.get("logger") or cls.LOGGER

        cls.logger = kwargs["logger"]
        cls.browser = Browser(**kwargs)

    @classmethod
    def tearDownClass(cls):
        super(BaseTest, cls).tearDownClass()
        cls.browser.quit()

    def setUp(self):
        TestCase.setUp(self)
        if self.browser.logger:
            name = self.id()
            symbols_before = "-" * int((self.TC_NAME_WIDTH - len(name) - 2) / 2)
            self.browser.logger.info(
                "{} {} {}".format(symbols_before, name, symbols_before)
            )

    def tearDown(self):
        failed = True
        if hasattr(self, "_outcome"):
            # python3
            failed = self._outcome and not self._outcome.success
        elif hasattr(self, "_resultForDoCleanups") and hasattr(
            self._resultForDoCleanups, "result"
        ):
            # nose
            failed = not self._resultForDoCleanups.result.wasSuccessful()
        elif hasattr(self, "_resultForDoCleanups") and hasattr(
            self._resultForDoCleanups, "current_failed"
        ):
            # python2
            failed = self._resultForDoCleanups.current_failed

        if failed:
            name = self.id()
            filename = "_".join(
                [name, self.browser.get_browser_initials(), get_timestamp()]
            )
            try:
                self.browser.save_screenshot(
                    self.FAILED_SCREENSHOT_FOLDER, filename + ".png"
                )
            except Exception:
                formatted_exc = traceback.format_exc()
                self.browser.logger.info(formatted_exc)
        TestCase.tearDown(self)

        if self.browser.logger:
            self.browser.logger.info(u"-" * self.TC_NAME_WIDTH)
