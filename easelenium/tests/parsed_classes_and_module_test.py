import inspect
import os
from unittest.case import TestCase

from easelenium import browser
from easelenium.ui.parser.parsed_class import (
    ParsedBrowserClass,
    ParsedClass,
    ParsedMouseClass,
    ParsedPageObjectClass,
)
from pytest import mark


class ParsedClassTest(TestCase):
    def test_parsed_py_file_by_class(self):
        classes = ParsedClass.get_parsed_classes(browser.Browser)
        assert len(classes) >= 1

        _class = classes[0]
        assert "FF" in _class.fields
        assert _class.get_value("FF") == "ff"
        assert _class.get_code("type") == inspect.getsource(browser.Browser.type)
        assert _class.get_arg_spec("type").args[:3] == ["self", "element", "text"]

    def test_parsed_py_file_by_module(self):
        classes = ParsedClass.get_parsed_classes(browser)
        assert len(classes) == 1

        _class = classes[0]
        assert "FF" in _class.fields
        assert _class.get_value("FF") == "ff"
        assert _class.get_code("type") == inspect.getsource(browser.Browser.type)
        assert _class.get_arg_spec("type").args[:3] == ["self", "element", "text"]

    def test_parsed_py_file_by_path(self):
        path = os.path.abspath(os.path.join(__file__, "..", "..", "browser.py"))
        classes = ParsedClass.get_parsed_classes(path)
        assert len(classes) == 1

        _class = classes[0]
        assert "FF" in _class.fields
        assert _class.get_value("FF") == "ff"
        assert _class.get_code("type") == inspect.getsource(browser.Browser.type)
        assert _class.get_arg_spec("type").args[:3] == ["self", "element", "text"]

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
