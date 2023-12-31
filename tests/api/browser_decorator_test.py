"""Browser decorator tests."""
from unittest import TestCase

import pytest
from selenium import webdriver

from easelenium.browser import Browser, browser_decorator


def __open_duck_and_assert_title(browser: Browser) -> bool:
    browser.get("https://duckduckgo.com/")
    return "DuckDuckGo" in browser.get_title()


@browser_decorator(browser_name="gc")
def func_default_decorator_gc(browser: Browser = None) -> bool:
    """Chrome decorator."""
    return __open_duck_and_assert_title(browser)


__CHROME_OPTIONS = webdriver.ChromeOptions()
__CHROME_OPTIONS.add_argument("window-size=1366,768")


@browser_decorator(
    browser_name="gc",
    headless=True,
    webdriver_kwargs={"options": __CHROME_OPTIONS},
)
def func_decorator_gc_with_params(browser: Browser = None) -> bool:
    """Chrome decorator with options."""
    result = __open_duck_and_assert_title(browser)
    assert browser.execute_js("return window.chrome") is None
    assert browser.execute_js("return window.screen.height") == 768  # noqa: PLR2004
    return result


@browser_decorator(browser_name="ff")
def func_decorator_ff(browser: Browser = None) -> bool:
    """Firefox decorator."""
    return __open_duck_and_assert_title(browser)


@browser_decorator()
def func_default_decorator(browser: Browser = None) -> bool:
    """Firefox default decorator."""
    return __open_duck_and_assert_title(browser)


@pytest.mark.skipif(not Browser.supports("gc"), reason="Browser not supported")
class TestDecoratorChrome(TestCase):
    """Chrome decorator tests."""

    def test_simple_decorator_gc(self) -> None:
        """Check default decorator."""
        assert func_default_decorator_gc()

    def test_decorator_gc_with_params(self) -> None:
        """Check gc decorator."""
        assert func_decorator_gc_with_params()


@pytest.mark.skipif(not Browser.supports("ff"), reason="Browser not supported")
class TestDecoratorFirefox(TestCase):
    """Firefox decorator tests."""

    def test_simple_decorator_ff(self) -> None:
        """Check Firefox decorator."""
        assert func_decorator_ff()

    def test_default_decorator(self) -> None:
        """Check Firefox decorator."""
        assert func_default_decorator()
