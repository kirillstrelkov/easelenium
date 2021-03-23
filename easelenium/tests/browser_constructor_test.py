# coding=utf8
from unittest.case import TestCase
from easelenium.browser import Browser
from selenium import webdriver


# add test skip if browser is not supported
class BrowserConstrutorTest(TestCase):
    def setUp(self):
        self.browser = None

    def test_constructor_no_args(self):
        self.browser = Browser()
        assert self.browser.is_ff()
        assert self.browser.execute_js("return typeof InstallTrigger") == "object"

    def test_constructor_ff(self):
        self.browser = Browser("ff")
        assert self.browser.is_ff()
        assert self.browser.execute_js("return typeof InstallTrigger") == "object"

    def test_constructor_ff_by_name(self):
        self.browser = Browser(name="ff")
        assert self.browser.is_ff()
        assert self.browser.execute_js("return typeof InstallTrigger") == "object"

    def test_constructor_gc(self):
        self.browser = Browser("gc")
        assert self.browser.is_gc()
        assert type(self.browser.execute_js("return window.chrome")) == dict

    def test_constructor_gc_by_name(self):
        self.browser = Browser(name="gc")
        assert self.browser.is_gc()
        assert type(self.browser.execute_js("return window.chrome")) == dict

    def test_constructor_gc_headless(self):
        self.browser = Browser(name="gc", headless=True)
        assert self.browser.is_gc()
        assert self.browser.execute_js("return window.chrome") is None

    def test_constructor_gc_special_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument("window-size=1366,768")

        self.browser = Browser(name="gc", webdriver_kwargs={"options": options})
        assert self.browser.is_gc()
        assert 1350 < self.browser.execute_js("return window.innerWidth") < 1400

    def test_constructor_gc_headless_and_special_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument("window-size=1366,768")

        self.browser = Browser(
            name="gc", headless=True, webdriver_kwargs={"options": options}
        )
        assert self.browser.is_gc()
        assert 1350 < self.browser.execute_js("return window.innerWidth") < 1400

    def tearDown(self):
        if self.browser:
            self.browser.quit()
