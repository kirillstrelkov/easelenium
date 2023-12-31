"""Browser API tests."""
import shutil
from pathlib import Path
from tempfile import gettempdir
from unittest.case import TestCase

import pytest
from selenium import webdriver

from easelenium.browser import Browser


# add test skip if browser is not supported
class BrowserConstrutorTest(TestCase):
    """Browser constructor tests."""

    def setUp(self) -> None:
        """Set up."""
        self.browser = None

    def tearDown(self) -> None:
        """Tear down."""
        if self.browser:
            self.browser.quit()


@pytest.mark.skipif(not Browser.supports("ff"), reason="Browser not supported")
class FirefoxTest(BrowserConstrutorTest):
    """Firefox tests."""

    def test_constructor_no_args(self) -> None:
        """Test default constructor."""
        self.browser = Browser()
        assert self.browser.is_ff()
        assert self.browser.execute_js("return typeof InstallTrigger") == "object"

    def test_constructor(self) -> None:
        """Test constructor with arguments."""
        self.browser = Browser("ff", headless=False)
        assert self.browser.is_ff()
        assert self.browser.execute_js("return typeof InstallTrigger") == "object"

    def test_constructor_by_name(self) -> None:
        """Test constructor with arguments."""
        self.browser = Browser(browser_name="ff", headless=False)
        assert self.browser.is_ff()
        assert self.browser.execute_js("return typeof InstallTrigger") == "object"

    def test_constructor_headless(self) -> None:
        """Test constructor with headless True."""
        self.browser = Browser("ff", headless=True)
        assert self.browser.is_ff()
        assert self.browser.execute_js("return typeof InstallTrigger") == "object"
        # TODO: add check if is headless  # noqa: TD003, TD002, FIX002

    def test_constructor_with_executable_path(self) -> None:
        """Test constructor with driver path."""
        new_driver_path = str(Path(gettempdir()) / "geckodriver")
        shutil.copy(
            Browser._find_driver_path("ff"),
            new_driver_path,
        )
        self.browser = Browser(
            webdriver_kwargs={
                "executable_path": new_driver_path,
            },
        )


@pytest.mark.skipif(not Browser.supports("gc"), reason="Browser not supported")
class ChromeTest(BrowserConstrutorTest):
    """Chrome tests."""

    def test_constructor(self) -> None:
        """Test default constructor."""
        self.browser = Browser("gc", headless=False)
        assert self.browser.is_gc()
        assert isinstance(self.browser.execute_js("return window.chrome"), dict)

    def test_constructor_by_name(self) -> None:
        """Test constructor with arguments."""
        self.browser = Browser(browser_name="gc", headless=False)
        assert self.browser.is_gc()
        assert isinstance(self.browser.execute_js("return window.chrome"), dict)

    def test_constructor_headless(self) -> None:
        """Test constructor with headless True."""
        self.browser = Browser(browser_name="gc", headless=True)
        assert self.browser.is_gc()
        assert self.browser.execute_js("return window.chrome") is None

    def test_constructor_special_options(self) -> None:
        """Test constructor with options."""
        options = webdriver.ChromeOptions()
        options.add_argument("window-size=1366,768")

        self.browser = Browser(
            browser_name="gc",
            headless=False,
            maximize=False,
            webdriver_kwargs={"options": options},
        )
        assert self.browser.is_gc()
        assert (
            1300  # noqa: PLR2004
            < self.browser.execute_js("return window.innerWidth")
            < 1400  # noqa: PLR2004
        )

    def test_constructor_headless_and_special_options(self) -> None:
        """Test constructor with headless and options."""
        options = webdriver.ChromeOptions()
        options.add_argument("window-size=1366,768")

        self.browser = Browser(
            browser_name="gc",
            headless=True,
            webdriver_kwargs={"options": options},
        )
        assert self.browser.is_gc()
        assert (
            1350  # noqa: PLR2004
            < self.browser.execute_js("return window.innerWidth")
            < 1400  # noqa: PLR2004
        )
        assert self.browser.execute_js("return window.chrome") is None

    def test_constructor_with_executable_path(self) -> None:
        """Test constructor with driver path."""
        new_driver_path = str(Path(gettempdir()) / "chromedriver")
        shutil.copy(Browser._find_driver_path("gc"), new_driver_path)
        self.browser = Browser(
            browser_name="gc",
            webdriver_kwargs={"executable_path": new_driver_path},
        )
