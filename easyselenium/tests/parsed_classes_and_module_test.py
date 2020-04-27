import os
import inspect

from pytest import mark

from unittest.case import TestCase

from easyselenium import browser
from easyselenium.ui.parser.parsed_class import (
    ParsedClass,
    ParsedBrowserClass,
    ParsedMouseClass,
    ParsedPageObjectClass,
    ParsedModule,
)


class ParsedClassTest(TestCase):
    def test_parsed_py_file_by_class(self):
        classes = ParsedClass.get_parsed_classes(browser.Browser)
        assert len(classes) >= 1

        _class = classes[0]
        assert "FF" in _class.fields
        assert _class.get_value("FF") == "ff"
        assert _class.get_code("type") == inspect.getsource(browser.Browser.type)
        assert _class.get_arg_spec("type").args == ["self", "element", "text"]

    def test_parsed_py_file_by_module(self):
        classes = ParsedClass.get_parsed_classes(browser)
        assert len(classes) > 1

        _class = classes[0]
        assert "FF" in _class.fields
        assert _class.get_value("FF") == "ff"
        assert _class.get_code("type") == inspect.getsource(browser.Browser.type)
        assert _class.get_arg_spec("type").args == ["self", "element", "text"]

    def test_parsed_py_file_by_path(self):
        path = os.path.abspath(os.path.join(__file__, "..", "..", "browser.py"))
        classes = ParsedClass.get_parsed_classes(path)
        assert len(classes) > 1

        _class = classes[0]
        assert "FF" in _class.fields
        assert _class.get_value("FF") == "ff"
        assert _class.get_code("type") == inspect.getsource(browser.Browser.type)
        assert _class.get_arg_spec("type").args == ["self", "element", "text"]

        assert path == _class.get_source_file()


class ParsedBrowserClassTest(TestCase):
    def test_parsed_browser_class_contains_only_methods_with_element(self):
        parsed_class = ParsedBrowserClass.get_parsed_classes()[0]
        assert "webdriver_wait" not in parsed_class.methods
        assert "execute_js" not in parsed_class.methods

        assert "find_descendant" in parsed_class.methods
        assert "find_descendants" in parsed_class.methods
        assert "find_element" in parsed_class.methods
        assert "find_elements" in parsed_class.methods
        assert "type" in parsed_class.methods
        assert "get_attribute" in parsed_class.methods
        assert "get_text" in parsed_class.methods
        assert "wait_for_visible" in parsed_class.methods
        assert "get_title" in parsed_class.methods
        assert "get_current_url" in parsed_class.methods
        assert "switch_to_frame" in parsed_class.methods
        assert "switch_to_default_content" in parsed_class.methods


# TODO: fix me
@mark.skip
class ParseNoseToolsModuleTest(TestCase):
    def test_methods_parsed_tools_module(self):
        # parsed_module = ParsedModule.get_parsed_module(tools)
        # assert "nose.tools" == parsed_module.name
        # assert parsed_module.module_obj is tools
        good_methods = [
            "assert_almost_equal",
            "assert_almost_equals",
            "assert_dict_contains_subset",
            "assert_dict_equal",
            "assert_equal",
            "assert_equals",
            "assert_false",
            "assert_greater",
            "assert_greater_equal",
            "assert_in",
            "assert_is",
            "assert_is_instance",
            "assert_is_none",
            "assert_is_not",
            "assert_is_not_none",
            "assert_less",
            "assert_less_equal",
            "assert_list_equal",
            "assert_multi_line_equal",
            "assert_not_almost_equal",
            "assert_not_almost_equals",
            "assert_not_equal",
            "assert_not_equals",
            "assert_not_in",
            "assert_not_is_instance",
            "assert_not_regexp_matches",
            "assert_raises",
            "assert_raises_regexp",
            "assert_regexp_matches",
            "assert_sequence_equal",
            "assert_set_equal",
            "assert_true",
            "assert_tuple_equal",
        ]

        # for m in good_methods:
        #     assert m in parsed_module.methods


class ParsedMouseClassTest(TestCase):
    def test_parsed_browser_class_contains_only_methods_with_element(self):
        parsed_class = ParsedMouseClass.get_parsed_classes()[0]

        assert "hover" in parsed_class.methods
        assert "hover_by_offset" in parsed_class.methods
        assert "left_click" in parsed_class.methods
        assert "left_click_by_offset" in parsed_class.methods
        assert "right_click" in parsed_class.methods
        assert "right_click_by_offset" in parsed_class.methods


class ParsedPageObjectClassTest(TestCase):
    def test_parsed_page_object_class_contains_methods(self):
        path = os.path.join(
            os.path.dirname(__file__), "data", "duckduckgo_class_with_method.py"
        )
        parsed_class = ParsedPageObjectClass.get_parsed_classes(path)[0]

        assert "search" in parsed_class.methods
