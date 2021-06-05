from unittest import TestCase

from easelenium.browser import Browser, browser_decorator
from pytest import mark
from selenium import webdriver


def __open_duck_and_assert_title(browser: Browser):
    browser.get("https://duckduckgo.com/")
    assert "DuckDuckGo" in browser.get_title()
    return True


@browser_decorator(browser_name="gc")
def func_default_decorator_gc(browser: Browser = None):
    return __open_duck_and_assert_title(browser)


__CHROME_OPTIONS = webdriver.ChromeOptions()
__CHROME_OPTIONS.add_argument("window-size=1366,768")


@browser_decorator(
    browser_name="gc", headless=True, webdriver_kwargs={"options": __CHROME_OPTIONS}
)
def func_decorator_gc_with_params(browser: Browser = None):
    result = __open_duck_and_assert_title(browser)
    assert browser.execute_js("return window.chrome") is None
    assert browser.execute_js("return window.screen.height") == 768
    return result


@browser_decorator(browser_name="ff")
def func_default_decorator_ff(browser: Browser = None):
    return __open_duck_and_assert_title(browser)


@browser_decorator(browser_name="ff")
def func_default_decorator(browser: Browser = None):
    return __open_duck_and_assert_title(browser)


@mark.skipif(not Browser.supports("gc"), reason="Browser not supported")
class TestDecoratorChrome(TestCase):
    def test_simple_decorator_gc(self):
        assert func_default_decorator_gc()

    def test_decorator_gc_with_params(self):
        assert func_decorator_gc_with_params()


@mark.skipif(not Browser.supports("ff"), reason="Browser not supported")
class TestDecoratorFirefox(TestCase):
    def test_simple_decorator_ff(self):
        assert func_default_decorator_ff()

    def test_default_decorator(self):
        assert func_default_decorator()
