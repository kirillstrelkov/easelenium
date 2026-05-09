"""Page object generator tests."""

from __future__ import annotations

import tempfile
from time import time
from typing import Any

import pytest
from selenium.webdriver.common.by import By

from tests import EASELENIUM_TEST_URL

try:
    from wx import Point, Rect
except ModuleNotFoundError:
    pytest.skip(allow_module_level=True)

from easelenium.base_test import BaseTest
from easelenium.browser import Browser
from easelenium.ui.generator.page_object_generator import PageObjectGenerator


@pytest.mark.skipif(not Browser.supports("gc"), reason="Browser not supported")
class PageObjectGeneratorTest(BaseTest):
    """PageObjectGenerator tests."""

    BROWSER_NAME = "gc"
    LOGGER = None

    @classmethod
    def setUpClass(cls: type[PageObjectGeneratorTest], **kwargs: Any) -> None:
        """Set up class."""
        super().setUpClass(maximize=False, **kwargs)
        cls.generator = PageObjectGenerator(cls.browser)

    def setUp(self) -> None:
        """Set up."""
        BaseTest.setUp(self)
        self.browser.get("https://duckduckgo.com/")

    def test_get_po_fields_from_page_timed(self) -> None:
        """Check getpage object fields."""
        start_time = time()
        fields = self.generator.get_all_po_fields("https://duckduckgo.com/", None)
        exec_time = time() - start_time
        assert len(fields) > 0
        assert exec_time < 100  # noqa: PLR2004

    def test_get_po_class_from_url(self) -> None:
        """Check get page object class."""
        folder = tempfile.gettempdir()
        name = "DuckDuckGo"
        po_class = self.generator.get_po_class_for_url(
            "https://duckduckgo.com/",
            name,
            folder,
        )
        po_class.save()
        assert len(po_class.fields) > 0

        assert po_class.file_path is not None
        assert po_class.file_path.startswith(folder)
        assert "duck_duck_go" in po_class.file_path

        assert po_class.img_path is not None
        assert po_class.img_path.startswith(folder)
        assert "duck_duck_go" in po_class.img_path

    def test_get_po_class_from_url_with_area(self) -> None:
        """Check get page object class with area."""
        folder = tempfile.gettempdir()
        name = "DuckDuckGo"
        area = (200, 80, 670, 295)
        po_class = self.generator.get_po_class_for_url(
            "https://duckduckgo.com/",
            name,
            folder,
            area,
        )
        po_class.save()
        assert len(po_class.fields) > 0
        assert len(po_class.fields) < 8  # noqa: PLR2004

        assert po_class.file_path is not None
        assert po_class.file_path.startswith(folder)
        assert "duck_duck_go" in po_class.file_path

        assert po_class.img_path is not None
        assert po_class.img_path.startswith(folder)
        assert "duck_duck_go" in po_class.img_path

    def test_get_po_class_fields_from_elements(self) -> None:
        """Check get page object class fields."""
        fields = self.generator.get_all_po_fields("https://duckduckgo.com/", None)
        assert len(fields) >= 7  # noqa: PLR2004

        for field in fields:
            assert len(field.name) > 0
            assert len(field.selector) > 0
            assert field.by in (
                By.ID,
                By.CLASS_NAME,
                By.CSS_SELECTOR,
                By.LINK_TEXT,
                By.XPATH,
            )

    def test_get_id_selector_for_element(self) -> None:
        """Check get id selector for element."""
        by_and_selector = By.ID, "menu-status"
        element = self.browser.find_element(by_and_selector)
        assert by_and_selector == self.generator._get_id_selector(element)
        assert by_and_selector == self.generator._get_selector(element)
        assert self.generator._get_name_for_field(element) == "MENU_STATUS"

    def test_get_class_name_selector_for_element(self) -> None:
        """Check get class name selector for element."""
        self.browser.get(EASELENIUM_TEST_URL)

        by_and_selector = By.CLASS_NAME, "uniq-class-name"
        element = self.browser.find_element(by_and_selector)
        assert by_and_selector == self.generator._get_class_name_selector(element)
        assert self.generator._get_name_for_field(element) == "UNIQ_CLASS_NAME"

    def test_get_link_text_selector_for_element(self) -> None:
        """Check get link text selector for element."""
        by_and_selector = By.LINK_TEXT, "Help"
        element = self.browser.find_element(by_and_selector)
        assert by_and_selector == self.generator._get_link_text_selector(element)
        assert self.generator._get_selector(element) == (By.LINK_TEXT, "Help")
        assert self.generator._get_name_for_field(element) == "HELP"

    def test_get_xpath_selector_for_element(self) -> None:
        """Check get xpath selector for element."""
        by_and_selector = By.XPATH, '//input[contains(@class, "search-input")]'
        element = self.browser.find_element(by_and_selector)
        css_result = self.generator._get_css_selector(element)
        assert css_result is not None
        assert ".search-input_searchInput" in css_result[1]
        sel_result = self.generator._get_selector(element)
        assert sel_result is not None
        assert "search-input_searchInput" in sel_result[1]
        assert "SEARCH_INPUT_SEARCHINPUT" in self.generator._get_name_for_field(element)

    def test_get_css_selector_for_element(self) -> None:
        """Check get css selector for element."""
        by_and_selector = By.CSS_SELECTOR, "input[class*='search-input']"
        element = self.browser.find_element(by_and_selector)
        css_result = self.generator._get_css_selector(element)
        assert css_result is not None
        assert ".search-input_searchInput" in css_result[1]
        sel_result = self.generator._get_selector(element)
        assert sel_result is not None
        assert "search-input_searchInput" in sel_result[1]
        assert "SEARCH_INPUT_SEARCHINPUT" in self.generator._get_name_for_field(element)

    def test_duckduckgo_search_results_area(self) -> None:
        """Check duckduckgo search results area."""
        folder = tempfile.gettempdir()
        name = "DuckDuckGo"
        area = (50, 156, 815, 444)
        po_class = self.generator.get_po_class_for_url(
            "https://duckduckgo.com/?q=selenium+webdriver&ia=web",
            name,
            folder,
            area,
        )
        for f in po_class.fields:
            x, y = f.location
            w, d = f.dimensions
            p = Point(int(x + w / 2), int(y + d / 2))
            assert Rect(*area).Contains(p)

        selectors = [f.selector for f in po_class.fields]
        bys = [f.by for f in po_class.fields]
        assert "link text" in bys
        assert "https://www.selenium.dev" in selectors

    def test_get_po_class_for_url_with_frames(self) -> None:
        """Check get page object class for url with frames."""
        folder = tempfile.gettempdir()
        name = "Iframe"
        area = None
        po_class = self.generator.get_po_class_for_url(
            EASELENIUM_TEST_URL,
            name,
            folder,
            area,
        )

        selectors = [f.selector for f in po_class.fields if "iframe" in f.selector]

        assert len(selectors) == 2  # noqa: PLR2004
