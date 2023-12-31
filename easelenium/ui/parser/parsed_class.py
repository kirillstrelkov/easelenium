"""Parsed class."""
from __future__ import annotations

import inspect
from importlib.machinery import SourceFileLoader
from pathlib import Path
from pprint import pformat
from typing import TYPE_CHECKING, Any
from unittest.case import TestCase

from easelenium.browser import Browser, Mouse
from easelenium.utils import is_string

if TYPE_CHECKING:
    from types import ModuleType


class ParsedClass:
    """Parsed class."""

    PROTECTED_PREFIX = "_"
    PRIVATE_PREFIX = "__"

    def __init__(
        self,
        name: str,
        class_obj: Any,  # noqa: ANN401
        fields: dict[str, callable],
        methods: dict[str, callable],
    ) -> None:
        """Initialize."""
        self.name = name
        self.class_obj = class_obj
        self.fields = fields
        self.methods = methods

    def get_value(self, name: str) -> callable:
        """Get function or method."""
        return self.fields.get(name) or self.methods.get(name)

    def get_code(self, name_or_method: str | callable) -> str:
        """Get function or method code."""
        if inspect.ismethod(name_or_method) or inspect.isfunction(name_or_method):
            method = name_or_method
        else:
            method = self.get_value(name_or_method)
        return inspect.getsource(method)

    def get_arg_spec(self, name_or_method: str | callable) -> inspect.FullArgSpec:
        """Get function or method argument spec."""
        if inspect.ismethod(name_or_method) or inspect.isfunction(name_or_method):
            method = name_or_method
        else:
            method = self.get_value(name_or_method)
        return inspect.getfullargspec(method)

    def get_module(self) -> ModuleType | None:
        """Get module."""
        return inspect.getmodule(self.class_obj)

    def get_source_file(self) -> str | None:
        """Get source file."""
        return inspect.getsourcefile(self.class_obj)

    def __str__(self) -> str:
        """Get string representation."""
        return pformat(self.__dict__)

    def __repr__(self) -> str:
        """Get string representation."""
        return str(self)

    @classmethod
    def get_parsed_classes(
        cls: type[ParsedClass],
        module_or_class_or_path: Any,  # noqa: ANN401
    ) -> list[ParsedClass]:
        """Return list of ParsedClass objects."""
        is_path = is_string(module_or_class_or_path)
        if inspect.ismodule(module_or_class_or_path) or is_path:
            if is_path:
                module_name = Path(module_or_class_or_path).stem
                module_or_class_or_path = SourceFileLoader(
                    module_name,
                    module_or_class_or_path,
                ).load_module()

            cur_module = inspect.getmodule(module_or_class_or_path)
            classes = inspect.getmembers(
                module_or_class_or_path,
                lambda o: inspect.isclass(o) and inspect.getmodule(o) == cur_module,
            )
        elif inspect.isclass(module_or_class_or_path):
            classes = [(module_or_class_or_path.__name__, module_or_class_or_path)]
        else:
            raise NotImplementedError

        def filter_private_members(members: list[str, callable]) -> list[str, callable]:
            """Filter private and protected methods."""
            return [
                m
                for m in members
                if cls.PROTECTED_PREFIX not in m[0] or cls.PRIVATE_PREFIX not in m[0]
            ]

        parsed_classes = []
        for class_name, _class in classes:
            methods = inspect.getmembers(_class, inspect.ismethod)
            methods += inspect.getmembers(_class, inspect.isfunction)
            methods = filter_private_members(methods)
            fields = inspect.getmembers(_class, lambda o: not inspect.isroutine(o))
            fields = filter_private_members(fields)
            parsed_classes.append(
                ParsedClass(class_name, _class, dict(fields), dict(methods)),
            )

        return parsed_classes


class ParsedBrowserClass(ParsedClass):
    """Parsed class of Browser."""

    _LOCATOR_NAME = "element"
    _GOOD_METHODS = (
        "switch_to_default_content",
        "get_title",
        "get_text",
        "get_attribute",
        "get_current_url",
    )
    # NOTE: methods which are wrapped(ex. 'stale_exception_wrapper')
    # should be added to _GOOD_METHODS
    # otherwise they won't be added to ParsedClass object

    @classmethod
    def get_parsed_classes(
        cls: type[ParsedBrowserClass],
        _module_or_class_or_path: Any = None,  # noqa: ANN401
    ) -> list[ParsedClass]:
        """Return list of ParsedClass objects."""
        parsed_classes = ParsedClass.get_parsed_classes(Browser)
        for _class in parsed_classes:
            _class.methods = {
                n: v
                for n, v in _class.methods.items()
                if not n.startswith("_")
                and (
                    cls._LOCATOR_NAME in _class.get_arg_spec(n).args
                    or n in cls._GOOD_METHODS
                )
            }
        return parsed_classes


class ParsedMouseClass(ParsedClass):
    """ParsedClass of Mouse."""

    _LOCATOR_NAME = "element"

    @classmethod
    def get_parsed_classes(
        cls: type[ParsedClass],
        _module_or_class_or_path: Any = None,  # noqa: ANN401
    ) -> list[ParsedClass]:
        """Return list of ParsedClass objects."""
        parsed_classes = ParsedClass.get_parsed_classes(Mouse)
        for _class in parsed_classes:
            _class.methods = {
                n: v
                for n, v in _class.methods.items()
                if cls._LOCATOR_NAME in _class.get_arg_spec(n).args
            }
        return parsed_classes


class ParsedPageObjectClass(ParsedClass):
    """ParsedClass of PageObject."""

    @classmethod
    def get_parsed_classes(
        cls: type[ParsedClass],
        module_or_class_or_path: Any,  # noqa: ANN401
    ) -> list[ParsedClass]:
        """Return list of ParsedClass objects."""
        parsed_classes = ParsedClass.get_parsed_classes(module_or_class_or_path)
        super_class = ParsedClass.get_parsed_classes(TestCase)[0]

        def filter_class_data(
            class1: ParsedClass,
            class2: ParsedClass,
            methods_or_fields: Any,  # noqa: ANN401
        ) -> dict[str, callable]:
            return {
                n: v
                for n, v in getattr(class1, methods_or_fields).items()
                if n not in getattr(class2, methods_or_fields)
            }

        for _class in parsed_classes:
            _class.methods = filter_class_data(_class, super_class, "methods")
            _class.fields = filter_class_data(_class, super_class, "fields")

        return parsed_classes
