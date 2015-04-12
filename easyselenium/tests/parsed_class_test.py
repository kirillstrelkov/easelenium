import os
import inspect

from unittest.case import TestCase

from easyselenium import browser
from easyselenium.ui.parser.parsed_class import ParsedClass, ParsedBrowserClass, \
    ParsedTestCaseClass, ParsedMouseClass, ParsedPageObjectClass


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

        self.assertIn('find_ancestor', parsed_class.methods)
        self.assertIn('find_ancestors', parsed_class.methods)
        self.assertIn('find_element', parsed_class.methods)
        self.assertIn('find_elements', parsed_class.methods)
        self.assertIn('type', parsed_class.methods)
        self.assertIn('wait_for_visible', parsed_class.methods)

        self.assertIn('switch_to_frame', parsed_class.methods)
        self.assertIn('switch_to_default_content', parsed_class.methods)


class ParsedTestCaseClassTest(TestCase):
    def test_methods_parsed_browser_class_with_asserts(self):
        parsed_class = ParsedTestCaseClass.get_parsed_classes()[0]
        good_methods = ['assertAlmostEqual',
                        'assertAlmostEquals',
                        'assertDictContainsSubset',
                        'assertDictEqual',
                        'assertEqual',
                        'assertEquals',
                        'assertFalse',
                        'assertGreater',
                        'assertGreaterEqual',
                        'assertIn',
                        'assertIs',
                        'assertIsInstance',
                        'assertIsNone',
                        'assertIsNot',
                        'assertIsNotNone',
                        'assertItemsEqual',
                        'assertLess',
                        'assertLessEqual',
                        'assertListEqual',
                        'assertMultiLineEqual',
                        'assertNotAlmostEqual',
                        'assertNotAlmostEquals',
                        'assertNotEqual',
                        'assertNotEquals',
                        'assertNotIn',
                        'assertNotIsInstance',
                        'assertNotRegexpMatches',
                        'assertRaises',
                        'assertRaisesRegexp',
                        'assertRegexpMatches',
                        'assertSequenceEqual',
                        'assertSetEqual',
                        'assertTrue',
                        'assertTupleEqual']
        for m in good_methods:
            self.assertIn(m, parsed_class.methods)

        bad_methods = ['_addSkip',
                       '_baseAssertEqual',
                       '_deprecate',
                       '_formatMessage',
                       '_getAssertEqualityFunc',
                       '_truncateMessage',
                       'addCleanup',
                       'addTypeEqualityFunc',
                       'assert_',
                       'countTestCases',
                       'debug',
                       'defaultTestResult',
                       'doCleanups',
                       'fail',
                       'failIf',
                       'failIfAlmostEqual',
                       'failIfEqual',
                       'failUnless',
                       'failUnlessAlmostEqual',
                       'failUnlessEqual',
                       'failUnlessRaises',
                       'id',
                       'run',
                       'setUp',
                       'setUpClass',
                       'shortDescription',
                       'skipTest',
                       'tearDown',
                       'tearDownClass']
        for m in bad_methods:
            self.assertNotIn(m, parsed_class.methods)


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
