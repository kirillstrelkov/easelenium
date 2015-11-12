import os
import inspect
from unittest.case import TestCase

from nose import tools

from easyselenium import browser
from easyselenium.ui.parser.parsed_class import ParsedClass, ParsedBrowserClass, \
    ParsedMouseClass, ParsedPageObjectClass, ParsedModule


class ParsedClassTest(TestCase):
    def test_parsed_py_file_by_class(self):
        classes = ParsedClass.get_parsed_classes(browser.Browser)
        self.assertGreaterEqual(len(classes), 1)

        _class = classes[0]
        self.assertIn('FF', _class.fields)
        self.assertEqual(_class.get_value('FF'), 'ff')
        self.assertEqual(_class.get_code('type'),
                         inspect.getsource(browser.Browser.type))
        self.assertEqual(_class.get_arg_spec('type').args,
                         ['self', 'element', 'text'])

    def test_parsed_py_file_by_module(self):
        classes = ParsedClass.get_parsed_classes(browser)
        self.assertGreaterEqual(len(classes), 1)

        _class = classes[0]
        self.assertIn('FF', _class.fields)
        self.assertEqual(_class.get_value('FF'), 'ff')
        self.assertEqual(_class.get_code('type'),
                         inspect.getsource(browser.Browser.type))
        self.assertEqual(_class.get_arg_spec('type').args,
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
        self.assertEqual(_class.get_arg_spec('type').args,
                         ['self', 'element', 'text'])

        self.assertEqual(path, _class.get_source_file())


class ParsedBrowserClassTest(TestCase):
    def test_parsed_browser_class_contains_only_methods_with_element(self):
        parsed_class = ParsedBrowserClass.get_parsed_classes()[0]
        self.assertNotIn('webdriver_wait', parsed_class.methods)
        self.assertNotIn('execute_js', parsed_class.methods)

        self.assertIn('find_descendant', parsed_class.methods)
        self.assertIn('find_descendants', parsed_class.methods)
        self.assertIn('find_element', parsed_class.methods)
        self.assertIn('find_elements', parsed_class.methods)
        self.assertIn('type', parsed_class.methods)
        self.assertIn('get_attribute', parsed_class.methods)
        self.assertIn('get_text', parsed_class.methods)
        self.assertIn('wait_for_visible', parsed_class.methods)
        self.assertIn('get_title', parsed_class.methods)
        self.assertIn('get_current_url', parsed_class.methods)

        self.assertIn('switch_to_frame', parsed_class.methods)
        self.assertIn('switch_to_default_content', parsed_class.methods)


class ParseNoseToolsModuleTest(TestCase):
    def test_methods_parsed_tools_module(self):
        parsed_module = ParsedModule.get_parsed_module(tools)
        self.assertEqual('nose.tools', parsed_module.name)
        self.assertIs(parsed_module.module_obj, tools)
        good_methods = [
            'assert_almost_equal',
            'assert_almost_equals',
            'assert_dict_contains_subset',
            'assert_dict_equal',
            'assert_equal',
            'assert_equals',
            'assert_false',
            'assert_greater',
            'assert_greater_equal',
            'assert_in',
            'assert_is',
            'assert_is_instance',
            'assert_is_none',
            'assert_is_not',
            'assert_is_not_none',
            'assert_items_equal',
            'assert_less',
            'assert_less_equal',
            'assert_list_equal',
            'assert_multi_line_equal',
            'assert_not_almost_equal',
            'assert_not_almost_equals',
            'assert_not_equal',
            'assert_not_equals',
            'assert_not_in',
            'assert_not_is_instance',
            'assert_not_regexp_matches',
            'assert_raises',
            'assert_raises_regexp',
            'assert_regexp_matches',
            'assert_sequence_equal',
            'assert_set_equal',
            'assert_true',
            'assert_tuple_equal'
        ]

        for m in good_methods:
            self.assertIn(m, parsed_module.methods)


class ParsedMouseClassTest(TestCase):
    def test_parsed_browser_class_contains_only_methods_with_element(self):
        parsed_class = ParsedMouseClass.get_parsed_classes()[0]

        self.assertIn('hover', parsed_class.methods)
        self.assertIn('hover_by_offset', parsed_class.methods)
        self.assertIn('left_click', parsed_class.methods)
        self.assertIn('left_click_by_offset', parsed_class.methods)
        self.assertIn('right_click', parsed_class.methods)
        self.assertIn('right_click_by_offset', parsed_class.methods)


class ParsedPageObjectClassTest(TestCase):
    def test_parsed_page_object_class_contains_methods(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'duckduckgo_class_with_method.py')
        parsed_class = ParsedPageObjectClass.get_parsed_classes(path)[0]

        self.assertIn('search', parsed_class.methods)
