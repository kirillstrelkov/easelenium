# coding=utf8
import tempfile
from wx import Rect, Point

from selenium.webdriver.common.by import By

from easyselenium.base_test import BaseTest
from easyselenium.ui.generator.page_object_generator import PageObjectGenerator


class PageObjectGeneratorTest(BaseTest):
    BROWSER_NAME = 'gc'
    logger = False

    @classmethod
    def setUpClass(cls):
        super(PageObjectGeneratorTest, cls).setUpClass()
        cls.generator = PageObjectGenerator(cls.browser)

    def setUp(self):
        BaseTest.setUp(self)
        self.browser.get('https://duckduckgo.com/')

    def test_get_po_fields_from_page(self):
        fields = self.generator.get_all_po_fields('https://duckduckgo.com/', None)
        self.assertGreaterEqual(len(fields), 7)

    def test_get_po_class_from_url(self):
        folder = tempfile.gettempdir()
        name = 'DuckDuckGo'
        po_class = self.generator.get_po_class_for_url(
            'https://duckduckgo.com/', name, folder
        )
        po_class.save()
        self.assertGreater(len(po_class.fields), 0)
        self.assertTrue(po_class.file_path.startswith(folder))
        self.assertIn('duck_duck_go', po_class.file_path)
        self.assertTrue(po_class.img_path.startswith(folder))
        self.assertIn('duck_duck_go', po_class.img_path)

    def test_get_po_class_from_url_with_area(self):
        folder = tempfile.gettempdir()
        name = 'DuckDuckGo'
        area = (200, 80, 670, 295)
        po_class = self.generator.get_po_class_for_url(
            'https://duckduckgo.com/', name, folder, area
        )
        po_class.save()
        self.assertGreater(len(po_class.fields), 0)
        self.assertLess(len(po_class.fields), 8)
        self.assertTrue(po_class.file_path.startswith(folder))
        self.assertIn('duck_duck_go', po_class.file_path)
        self.assertTrue(po_class.img_path.startswith(folder))
        self.assertIn('duck_duck_go', po_class.img_path)

    def test_get_po_class_fields_from_elements(self):
        fields = self.generator.get_all_po_fields(
            'https://duckduckgo.com/',
            None
        )
        self.assertGreaterEqual(len(fields), 7)

        for field in fields:
            self.assertGreater(len(field.name), 0)
            self.assertGreater(len(field.selector), 0)
            self.assertIn(field.by, (By.ID, By.CLASS_NAME,
                                     By.CSS_SELECTOR, By.LINK_TEXT,
                                     By.XPATH))
            self.assertNotEqual(field.location, (0, 0))
            self.assertNotEqual(field.dimensions, (0, 0))

    def test_get_id_selector_for_element(self):
        by_and_selector = By.ID, u'search_form_input_homepage'
        element = self.browser.find_element(by_and_selector)
        self.assertEqual(by_and_selector,
                         self.generator._get_id_selector(element))
        self.assertEqual(by_and_selector,
                         self.generator._get_selector(element))
        self.assertEqual(u'SEARCH_FORM_INPUT_HOMEPAGE',
                         self.generator._get_name_for_field(element))

    def test_get_class_name_selector_for_element(self):
        by_and_selector = By.CLASS_NAME, u'logo-wrap--home'
        element = self.browser.find_element(by_and_selector)
        self.assertEqual(by_and_selector,
                         self.generator._get_class_name_selector(element))
        self.assertEqual((By.LINK_TEXT, u'About DuckDuckGo'),
                         self.generator._get_selector(element))
        self.assertEqual(u'ABOUT_DUCKDUCKGO',
                         self.generator._get_name_for_field(element))

    def test_get_link_text_selector_for_element(self):
        by_and_selector = By.LINK_TEXT, u'About DuckDuckGo'
        element = self.browser.find_element(by_and_selector)
        self.assertEqual(by_and_selector,
                         self.generator._get_link_text_selector(element))
        self.assertEqual((By.ID, u'logo_homepage_link'),
                         self.generator._get_selector(element))
        self.assertEqual(u'LOGO_HOMEPAGE_LINK',
                         self.generator._get_name_for_field(element))

    def test_get_xpath_selector_for_element(self):
        by_and_selector = By.XPATH, u'//*[@id="search_form_input_homepage"]'
        element = self.browser.find_element(by_and_selector)
        self.assertEqual(by_and_selector,
                         self.generator._get_xpath_selector(element))
        self.assertEqual((By.ID, u'search_form_input_homepage'),
                         self.generator._get_selector(element))
        self.assertEqual(u'SEARCH_FORM_INPUT_HOMEPAGE',
                         self.generator._get_name_for_field(element))

    def test_get_css_selector_for_element(self):
        by_and_selector = By.CSS_SELECTOR, u'#logo_homepage_link'
        element = self.browser.find_element(by_and_selector)
        self.assertEqual(by_and_selector,
                         self.generator._get_css_selector(element))
        self.assertEqual((By.ID, u'logo_homepage_link'),
                         self.generator._get_selector(element))
        self.assertEqual(u'LOGO_HOMEPAGE_LINK',
                         self.generator._get_name_for_field(element))

        by_and_selector = By.CSS_SELECTOR, u'.logo-wrap--home'
        element = self.browser.find_element(by_and_selector)
        self.assertEqual(by_and_selector,
                         self.generator._get_css_selector(element))
        self.assertEqual((By.LINK_TEXT, u'About DuckDuckGo'),
                         self.generator._get_selector(element))
        self.assertEqual(u'ABOUT_DUCKDUCKGO',
                         self.generator._get_name_for_field(element))

    def test_duckduckgo_search_results_area(self):
        folder = tempfile.gettempdir()
        name = 'DuckDuckGo'
        area = (50, 156, 615, 244)
        po_class = self.generator.get_po_class_for_url(
            u'https://duckduckgo.com/?q=selenium&ia=about',
            name,
            folder,
            area
        )
        for f in po_class.fields:
            x, y = f.location
            w, d = f.dimensions
            p = Point(x + w / 2, y + d / 2)
            self.assertTrue(Rect(*area).Contains(p), f)

        selectors = [f.selector for f in po_class.fields]
        bys = [f.by for f in po_class.fields]
        self.assertIn('link text', bys)
        self.assertIn(u'Selenium - Web Browser Automation', selectors)

    def test_get_po_class_for_url_with_frames(self):
        folder = tempfile.gettempdir()
        name = 'Quackit'
        area = None
        po_class = self.generator.get_po_class_for_url(
            u'http://www.quackit.com/html/templates/frames/frames_example_6.html',
            name, folder, area
        )

        selectors = [f.selector for f in po_class.fields]

        self.assertGreaterEqual(len(selectors), 5)
        self.assertIn(u'/html/frameset/frame', selectors)
        self.assertIn(u'/html/frameset/frame[2]', selectors)
