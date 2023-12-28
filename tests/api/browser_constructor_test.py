import os
import shutil
from tempfile import gettempdir
from unittest.case import TestCase

from pytest import mark
from selenium import webdriver

from easelenium.browser import Browser


# add test skip if browser is not supported
class BrowserConstrutorTest(TestCase):
    def setUp(self):
        self.browser = None

    def tearDown(self):
        if self.browser:
            self.browser.quit()


@mark.skipif(not Browser.supports("ff"), reason="Browser not supported")
class FirefoxTest(BrowserConstrutorTest):
    DRIVER_IN_HOME_DIR = os.path.join(os.path.expanduser("~"), "geckodriver")

    def test_constructor_no_args(self):
        self.browser = Browser()
        assert self.browser.is_ff()
        assert self.browser.execute_js("return typeof InstallTrigger") == "object"

    def test_constructor(self):
        self.browser = Browser("ff", headless=False)
        assert self.browser.is_ff()
        assert self.browser.execute_js("return typeof InstallTrigger") == "object"

    def test_constructor_by_name(self):
        self.browser = Browser(browser_name="ff", headless=False)
        assert self.browser.is_ff()
        assert self.browser.execute_js("return typeof InstallTrigger") == "object"

    def test_constructor_headless(self):
        self.browser = Browser("ff", headless=True)
        assert self.browser.is_ff()
        assert self.browser.execute_js("return typeof InstallTrigger") == "object"
        # TODO: add check if is headless

    def test_constructor_with_executable_path(self):
        new_driver_path = os.path.join(gettempdir(), "geckodriver")
        shutil.copy(Browser._find_driver_path("ff"), new_driver_path)
        self.browser = Browser(webdriver_kwargs={"executable_path": new_driver_path})


@mark.skipif(not Browser.supports("gc"), reason="Browser not supported")
class ChromeTest(BrowserConstrutorTest):
    DRIVER_IN_HOME_DIR = os.path.join(os.path.expanduser("~"), "chromedriver")

    def test_constructor(self):
        self.browser = Browser("gc", headless=False)
        assert self.browser.is_gc()
        assert type(self.browser.execute_js("return window.chrome")) == dict

    def test_constructor_by_name(self):
        self.browser = Browser(browser_name="gc", headless=False)
        assert self.browser.is_gc()
        assert type(self.browser.execute_js("return window.chrome")) == dict

    def test_constructor_headless(self):
        self.browser = Browser(browser_name="gc", headless=True)
        assert self.browser.is_gc()
        assert self.browser.execute_js("return window.chrome") is None

    def test_constructor_special_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument("window-size=1366,768")

        self.browser = Browser(
            browser_name="gc", headless=False, webdriver_kwargs={"options": options},
        )
        assert self.browser.is_gc()
        assert 1300 < self.browser.execute_js("return window.innerWidth") < 1400

    def test_constructor_headless_and_special_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument("window-size=1366,768")

        self.browser = Browser(
            browser_name="gc", headless=True, webdriver_kwargs={"options": options},
        )
        assert self.browser.is_gc()
        assert 1350 < self.browser.execute_js("return window.innerWidth") < 1400
        assert self.browser.execute_js("return window.chrome") is None

    def test_constructor_with_executable_path(self):
        new_driver_path = os.path.join(gettempdir(), "chromedriver")
        shutil.copy(Browser._find_driver_path("gc"), new_driver_path)
        self.browser = Browser(
            browser_name="gc", webdriver_kwargs={"executable_path": new_driver_path},
        )
