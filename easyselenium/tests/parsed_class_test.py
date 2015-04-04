from easyselenium import browser
import inspect
import os
from unittest.case import TestCase

from easyselenium.parser.parsed_class import ParsedClass, ParsedBrowserClass


class ParsedClassTest(TestCase):
    def test_parsed_py_file_by_class(self):
        classes = ParsedClass.get_parsed_classes(browser.Browser)
        self.assertGreaterEqual(len(classes), 1)

        _class = classes[0]
        self.assertIn('FF', _class.fields)
        self.assertEqual(_class.get_value('FF'), 'ff')
        self.assertEqual(_class.get_code('type'),
                         inspect.getsource(browser.Browser.type))
        self.assertEqual(_class.get_args('type'),
                         ['self', 'element', 'text'])

    def test_parsed_py_file_by_module(self):
        classes = ParsedClass.get_parsed_classes(browser)
        self.assertGreaterEqual(len(classes), 1)

        _class = classes[0]
        self.assertIn('FF', _class.fields)
        self.assertEqual(_class.get_value('FF'), 'ff')
        self.assertEqual(_class.get_code('type'),
                         inspect.getsource(browser.Browser.type))
        self.assertEqual(_class.get_args('type'),
                         ['self', 'element', 'text'])

    def test_parsed_py_file_by_path(self):
        path = os.path.abspath(os.path.join(__file__, '..', '..', 'browser.py'))
        classes = ParsedClass.get_parsed_classes(path)
        self.assertGreaterEqual(len(classes), 1)

        _class = classes[0]
        self.assertIn('FF', _class.fields)
        self.assertEqual(_class.get_value('FF'), 'ff')
        self.assertEqual(_class.get_code('type'),
                         inspect.getsource(browser.Browser.type))
        self.assertEqual(_class.get_args('type'),
                         ['self', 'element', 'text'])

        self.assertEqual(path, _class.get_source_file())


class ParsedBrowserClassTest(TestCase):
    def test_parsed_browser_class_contains_only_methods_with_element(self):
        parsed_class = ParsedBrowserClass.get_parsed_classes()[0]
        self.assertNotIn('webdriver_wait', parsed_class.methods)
        self.assertNotIn('execute_js', parsed_class.methods)

        self.assertIn('find_ancestor', parsed_class.methods)
        self.assertIn('find_ancestors', parsed_class.methods)
        self.assertIn('find_element', parsed_class.methods)
        self.assertIn('find_elements', parsed_class.methods)
        self.assertIn('type', parsed_class.methods)
        self.assertIn('wait_for_visible', parsed_class.methods)

        self.assertIn('switch_to_frame', parsed_class.methods)
        self.assertIn('switch_to_default_content', parsed_class.methods)
