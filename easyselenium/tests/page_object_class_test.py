# coding=utf8
import os
import pickle
import codecs

from unittest.case import TestCase

from selenium.webdriver.common.by import By

from easyselenium.utils import is_windows
from easyselenium.ui.file_utils import safe_remove_path, check_if_path_exists,\
    read_file
from easyselenium.ui.generator.page_object_class import get_by_as_code_str,\
    get_by_from_code_str, PageObjectClass


class PageObjectClassTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(PageObjectClassTest, cls).setUpClass()
        cur_path = os.path.dirname(__file__)
        cls.pickled_object_path = os.path.join(
            cur_path, 'data', 'pickled_po_class_object'
        )
        cls.expected_duckduckgo_class_path = os.path.join(
            cur_path, 'data', 'expected_duckduckgo_class.py'
        )
        with codecs.open(cls.pickled_object_path) as f:
            cls.po_class_object = pickle.load(f)
        cls.maxDiff = None

    def test_save_po_object_class(self):
        if is_windows():
            self.skipTest(
                'Unsupported in Windows because temp directory is hardcoded to \'/tmp\' in pickled object.'
            )
        else:
            for path in (self.po_class_object.file_path,
                         self.po_class_object.img_path):
                safe_remove_path(path)

            self.po_class_object.save()

            check_if_path_exists(self.po_class_object.file_path)
            self.assertGreater(
                os.path.getsize(self.po_class_object.file_path), 0
            )
            check_if_path_exists(self.po_class_object.img_path)
            self.assertGreater(
                os.path.getsize(self.po_class_object.img_path), 0
            )

    def test_get_formatted_fields(self):
        if is_windows():
            self.skipTest(
                'Unsupported in Windows because temp directory is hardcoded to \'/tmp\' in pickled object.'
            )
        else:
            expected_fields = u'''
    BAD_NAME = (By.LINK_TEXT, u'⇶') # location: (1261, 23) dimensions: (33, 33)
    LOGO_HOMEPAGE_LINK = (By.ID, u'logo_homepage_link') # location: (526, 117) dimensions: (250, 200)
    SEARCH_FORM_INPUT_HOMEPAGE = (By.ID, u'search_form_input_homepage') # location: (347, 347) dimensions: (562, 46)
    SEARCH_BUTTON_HOMEPAGE = (By.ID, u'search_button_homepage') # location: (912, 350) dimensions: (52, 40)
    TAG_HOME_NAV_TAG_HOME_NAV_ITEM = (By.CSS_SELECTOR, u'.tag-home__nav > .tag-home__nav__item') # location: (625, 458) dimensions: (7, 7)
    TAG_HOME_NAV_ITEM_IS_ACTIVE = (By.CSS_SELECTOR, u'.tag-home__nav__item.is-active') # location: (658, 458) dimensions: (7, 7)
    ADD_TO_BROWSER_BADGE_ICON_BROWSER_FIREFOX = (By.CSS_SELECTOR, u'.add-to-browser-badge__icon.browser--firefox') # location: (518, 521) dimensions: (64, 64)
    ID_FOOTER_HOMEPAGE_DIV_1_SPAN_1_BR_1 = (By.XPATH, u'id("footer_homepage")/DIV[1]/SPAN[1]/BR[1]') # location: (747, 572) dimensions: (0, 20)
    DDGSI_ADD_TO_BROWSER_BADGE_CLOSE_JS_ADD_TO_BROWSER_CLOSE = (By.CSS_SELECTOR, u'.ddgsi.add-to-browser-badge__close.js-add-to-browser-close') # location: (754, 559) dimensions: (30, 38)
'''
            self.assertEqual(
                self.po_class_object._get_fields_as_code().strip(),
                expected_fields.strip()
            )

    def test_get_file_content(self):
        if is_windows():
            self.skipTest(
                'Unsupported in Windows because temp directory is hardcoded to \'/tmp\' in pickled object.'
            )
        else:
            expected_string = read_file(self.expected_duckduckgo_class_path)
            self.assertEqual(
                self.po_class_object._get_file_content().strip(),
                expected_string.strip()
            )

    def test_get_by_as_code_str(self):
        self.assertEqual(u'By.ID',
                         get_by_as_code_str(By.ID))
        self.assertEqual(u'By.CLASS_NAME',
                         get_by_as_code_str(By.CLASS_NAME))
        self.assertEqual(u'By.XPATH',
                         get_by_as_code_str(By.XPATH))
        self.assertEqual(u'By.CSS_SELECTOR',
                         get_by_as_code_str(By.CSS_SELECTOR))
        self.assertEqual(u'By.LINK_TEXT',
                         get_by_as_code_str(By.LINK_TEXT))

    def test_get_by_from_code_str(self):
        self.assertEqual(By.ID,
                         get_by_from_code_str(u'By.ID'))
        self.assertEqual(By.CLASS_NAME,
                         get_by_from_code_str(u'By.CLASS_NAME'))
        self.assertEqual(By.XPATH,
                         get_by_from_code_str(u'By.XPATH'))
        self.assertEqual(By.CSS_SELECTOR,
                         get_by_from_code_str(u'By.CSS_SELECTOR'))
        self.assertEqual(By.LINK_TEXT,
                         get_by_from_code_str(u'By.LINK_TEXT'))

    def test_parse_string_to_po_class(self):
        if is_windows():
            self.skipTest(
                "Unsupported in Windows because temp directory is hardcoded to '/tmp' in pickled object."
            )
        else:
            expected_string = read_file(self.expected_duckduckgo_class_path)
            self.assertEqual(
                self.po_class_object._get_file_content().strip(),
                expected_string.strip()
            )
            po_class = PageObjectClass.parse_string_to_po_class(
                read_file(self.expected_duckduckgo_class_path)
            )

            self.assertEqual(po_class.name, self.po_class_object.name)
            self.assertEqual(po_class.url, self.po_class_object.url)
            self.assertEqual(po_class.fields, self.po_class_object.fields)
            self.assertEqual(po_class.area, self.po_class_object.area)
            self.assertEqual(po_class.file_path,
                             self.po_class_object.file_path)
            self.assertEqual(po_class.img_path, self.po_class_object.img_path)

            self.assertEqual(po_class, self.po_class_object)
