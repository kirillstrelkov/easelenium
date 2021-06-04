# coding=utf8
import tempfile

from easelenium.base_test import BaseTest
from easelenium.ui.generator.page_object_generator import PageObjectGenerator
from selenium.webdriver.common.by import By
from wx import Point, Rect


class PageObjectGeneratorTest(BaseTest):
    BROWSER_NAME = "gc"
    LOGGER = None

    @classmethod
    def setUpClass(cls):
        super(PageObjectGeneratorTest, cls).setUpClass()
        cls.generator = PageObjectGenerator(cls.browser)

    def setUp(self):
        BaseTest.setUp(self)
        self.browser.get("https://duckduckgo.com/")

    def test_get_po_fields_from_page(self):
        fields = self.generator.get_all_po_fields("https://duckduckgo.com/", None)
        assert len(fields) > 7

    def test_get_po_class_from_url(self):
        folder = tempfile.gettempdir()
        name = "DuckDuckGo"
        po_class = self.generator.get_po_class_for_url(
            "https://duckduckgo.com/", name, folder
        )
        po_class.save()
        assert len(po_class.fields) > 0
        assert po_class.file_path.startswith(folder)
        assert "duck_duck_go" in po_class.file_path
        assert po_class.img_path.startswith(folder)
        assert "duck_duck_go" in po_class.img_path

    def test_get_po_class_from_url_with_area(self):
        folder = tempfile.gettempdir()
        name = "DuckDuckGo"
        area = (200, 80, 670, 295)
        po_class = self.generator.get_po_class_for_url(
            "https://duckduckgo.com/", name, folder, area
        )
        po_class.save()
        assert len(po_class.fields) > 0
        assert len(po_class.fields) < 8
        assert po_class.file_path.startswith(folder)
        assert "duck_duck_go" in po_class.file_path
        assert po_class.img_path.startswith(folder)
        assert "duck_duck_go" in po_class.img_path

    def test_get_po_class_fields_from_elements(self):
        fields = self.generator.get_all_po_fields("https://duckduckgo.com/", None)
        assert len(fields) >= 7

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
            assert field.location != (0, 0)
            assert field.dimensions != (0, 0)

    def test_get_id_selector_for_element(self):
        by_and_selector = By.ID, "search_form_input_homepage"
        element = self.browser.find_element(by_and_selector)
        assert by_and_selector == self.generator._get_id_selector(element)
        assert by_and_selector == self.generator._get_selector(element)
        assert "SEARCH_FORM_INPUT_HOMEPAGE" == self.generator._get_name_for_field(
            element
        )

    def test_get_class_name_selector_for_element(self):
        by_and_selector = By.CLASS_NAME, "logo-wrap--home"
        element = self.browser.find_element(by_and_selector)
        assert by_and_selector == self.generator._get_class_name_selector(element)
        assert (By.LINK_TEXT, "About DuckDuckGo") == self.generator._get_selector(
            element
        )
        assert "ABOUT_DUCKDUCKGO" == self.generator._get_name_for_field(element)

    def test_get_link_text_selector_for_element(self):
        by_and_selector = By.LINK_TEXT, "About DuckDuckGo"
        element = self.browser.find_element(by_and_selector)
        assert by_and_selector == self.generator._get_link_text_selector(element)
        assert (By.ID, "logo_homepage_link") == self.generator._get_selector(element)
        assert "LOGO_HOMEPAGE_LINK" == self.generator._get_name_for_field(element)

    def test_get_xpath_selector_for_element(self):
        by_and_selector = By.XPATH, u'//*[@id="search_form_input_homepage"]'
        element = self.browser.find_element(by_and_selector)
        assert by_and_selector, self.generator._get_xpath_selector(element)
        assert (By.ID, "search_form_input_homepage") == self.generator._get_selector(
            element
        )
        assert "SEARCH_FORM_INPUT_HOMEPAGE" == self.generator._get_name_for_field(
            element
        )

    def test_get_css_selector_for_element(self):
        by_and_selector = By.CSS_SELECTOR, "#logo_homepage_link"
        element = self.browser.find_element(by_and_selector)
        assert by_and_selector, self.generator._get_css_selector(element)
        assert (By.ID, "logo_homepage_link") == self.generator._get_selector(element)
        assert "LOGO_HOMEPAGE_LINK" == self.generator._get_name_for_field(element)

        by_and_selector = By.CSS_SELECTOR, ".logo-wrap--home"
        element = self.browser.find_element(by_and_selector)
        assert by_and_selector, self.generator._get_css_selector(element)
        assert (By.LINK_TEXT, "About DuckDuckGo") == self.generator._get_selector(
            element
        )
        assert "ABOUT_DUCKDUCKGO", self.generator._get_name_for_field(element)

    def test_duckduckgo_search_results_area(self):
        folder = tempfile.gettempdir()
        name = "DuckDuckGo"
        area = (50, 156, 815, 444)
        po_class = self.generator.get_po_class_for_url(
            "https://duckduckgo.com/?q=selenium+webdriver&ia=web", name, folder, area
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

    def test_get_po_class_for_url_with_frames(self):
        folder = tempfile.gettempdir()
        name = "Iframe"
        area = None
        po_class = self.generator.get_po_class_for_url(
            "https://yari-demos.prod.mdn.mozit.cloud/en-US/docs/Web/HTML/Element/iframe/_sample_.Example1.html",
            name,
            folder,
            area,
        )

        selectors = [f.selector for f in po_class.fields]

        assert len(selectors) >= 2
        assert "/html/body/iframe" in selectors
