"""Browser decorator tests."""

from unittest import TestCase

import pytest
from selenium import webdriver

from easelenium.browser import Browser, browser_decorator
from tests.api import is_headless


def __open_duck_and_assert_title(browser: Browser) -> bool:
    browser.get("https://duckduckgo.com/")
    return "DuckDuckGo" in browser.get_title()


@browser_decorator(browser_name="gc")
def func_default_decorator_gc(browser: Browser) -> bool:
    """Chrome decorator."""
    return __open_duck_and_assert_title(browser)


def _make_chrome_options() -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    options.add_argument("window-size=1366,768")
    return options


@browser_decorator(
    browser_name="gc",
    headless=True,
    webdriver_kwargs={"options": _make_chrome_options()},
)
def func_decorator_gc_with_params(browser: Browser) -> bool:
    """Chrome decorator with options."""
    assert is_headless(browser), "headless not found"
    # window-size resets to screen size (800px) after any navigation in headless Chrome
    assert browser.execute_js("return window.innerWidth") == 1366  # noqa: PLR2004
    return __open_duck_and_assert_title(browser)


@browser_decorator(browser_name="ff")
def func_decorator_ff(browser: Browser) -> bool:
    """Firefox decorator."""
    return __open_duck_and_assert_title(browser)


@browser_decorator()
def func_default_decorator(browser: Browser) -> bool:
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
