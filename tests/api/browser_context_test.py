"""Browser decorator tests."""

from unittest import TestCase

import pytest
from selenium import webdriver

from easelenium.browser import Browser, browser_context
from tests.api import is_headless


def __open_duck_and_assert_title(browser: Browser) -> None:
    browser.get("https://duckduckgo.com/")
    assert "DuckDuckGo" in browser.get_title()


def _make_chrome_options() -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    options.add_argument("window-size=1366,768")
    return options


@pytest.mark.skipif(not Browser.supports("gc"), reason="Browser not supported")
class TestDecoratorChrome(TestCase):
    """Chrome decorator tests."""

    def test_simple_browser_context_gc(self) -> None:
        """Check default decorator."""
        with browser_context(browser_name="gc") as browser:
            assert browser.is_gc()
            __open_duck_and_assert_title(browser)

    def test_browser_context_gc_with_params(self) -> None:
        """Check gc decorator."""
        with browser_context(
            browser_name="gc",
            headless=True,
            webdriver_kwargs={"options": _make_chrome_options()},
        ) as browser:
            assert browser.is_gc()
            assert is_headless(browser), "headless not found"
            # window-size resets to screen size (800px) after any navigation in headless Chrome
            assert browser.execute_js("return window.innerWidth") == 1366  # noqa: PLR2004
            __open_duck_and_assert_title(browser)


@pytest.mark.skipif(not Browser.supports("ff"), reason="Browser not supported")
class TestDecoratorFirefox(TestCase):
    """Firefox decorator tests."""

    def test_simple_browser_context_ff(self) -> None:
        """Check Firefox decorator."""
        with browser_context(browser_name="ff", headless=True) as browser:
            assert browser.is_ff()
            assert is_headless(browser), "headless not found"
            __open_duck_and_assert_title(browser)

    def test_default_browser_context(self) -> None:
        """Check Firefox decorator."""
        with browser_context(browser_name="ff") as browser:
            assert browser.is_ff()
            __open_duck_and_assert_title(browser)
