# coding=utf8
import tempfile

from selenium.webdriver.common.by import By

from easyselenium.generator.page_object_generator import PageObjectGenerator
from easyselenium.base_test import BaseTest


class PageObjectGeneratorTest(BaseTest):
    LOGGER = False

    @classmethod
    def setUpClass(cls):
        super(PageObjectGeneratorTest, cls).setUpClass()
        cls.generator = PageObjectGenerator(cls.browser)

    def setUp(self):
        BaseTest.setUp(self)
        self.browser.get('https://duckduckgo.com/')

    def test_get_elements_from_page(self):
        elements = self.generator.get_elements_from_url(
            'https://duckduckgo.com/')
        self.assertGreaterEqual(len(elements), 98)
        elements = self.generator._filter_elements(elements)
        self.assertGreaterEqual(len(elements), 10)

    def test_get_po_class_from_url(self):
        folder = tempfile.gettempdir()
        name = 'DuckDuckGo'
        po_class = self.generator._get_po_class_for_url(
            'https://duckduckgo.com/', name, folder
        )
        self.assertGreater(po_class.fields, 0)
        self.assertTrue(po_class.file_path.startswith(folder))
        self.assertIn(name, po_class.file_path)
        self.assertTrue(po_class.img_path.startswith(folder))
        self.assertIn(name, po_class.img_path)

    def test_get_po_class_fields_from_elements(self):
        elements = self.generator.get_elements_from_url(
            'https://duckduckgo.com/'
        )
        self.assertGreaterEqual(len(elements), 98)
        elements = self.generator._filter_elements(elements)
        self.assertGreaterEqual(len(elements), 10)

        fields = self.generator._get_po_class_fields_from_elements(elements)
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
        by_and_selector = By.CLASS_NAME, u'logo_homepage'
        element = self.browser.find_element(by_and_selector)
        self.assertEqual(by_and_selector,
                         self.generator._get_class_name_selector(element))
        self.assertEqual((By.ID, u'logo_homepage_link'),
                         self.generator._get_selector(element))
        self.assertEqual(u'LOGO_HOMEPAGE_LINK',
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
        by_and_selector = By.XPATH, u'id("search_form_input_homepage")'
        element = self.browser.find_element(by_and_selector)
        self.assertEqual(by_and_selector,
                         self.generator._get_xpath_selector(element))
        self.assertEqual((By.ID, u'search_form_input_homepage'),
                         self.generator._get_selector(element))
        self.assertEqual(u'SEARCH_FORM_INPUT_HOMEPAGE',
                         self.generator._get_name_for_field(element))

        by_and_selector = By.XPATH, u'id("content_homepage")/DIV[1]/DIV[1]'
        element = self.browser.find_element(by_and_selector)
        self.assertEqual(by_and_selector,
                         self.generator._get_xpath_selector(element))
        self.assertEqual((By.LINK_TEXT, u'About DuckDuckGo'),
                         self.generator._get_selector(element))
        self.assertEqual(u'ABOUT_DUCKDUCKGO',
                         self.generator._get_name_for_field(element))

        by_and_selector = By.XPATH, u'id("content_homepage")/DIV[1]/DIV[3]/DIV[1]/UL[1]/LI[1]'
        element = self.browser.find_element(by_and_selector)
        self.assertEqual(by_and_selector,
                         self.generator._get_xpath_selector(element))
        self.assertEqual((By.CSS_SELECTOR, u'.tag-home__nav__item.is-active'),
                         self.generator._get_selector(element))
        self.assertEqual(u'TAG_HOME_NAV_ITEM_IS_ACTIVE',
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
