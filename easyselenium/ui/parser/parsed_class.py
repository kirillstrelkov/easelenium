import os
import imp
import inspect
from pprint import pformat
from unittest.case import TestCase

from easyselenium.browser import Browser, Mouse


class ParsedModule(object):
    PROTECTED_PREFIX = '_'
    PRIVATE_PREFIX = '__'

    def __init__(self, name, module_odj, fields, methods):
        self.name = name
        self.module_obj = module_odj
        self.fields = fields
        self.methods = methods

    def get_value(self, name):
        return self.fields.get(name) or self.methods.get(name)

    def get_code(self, name_or_method):
        if inspect.ismethod(name_or_method):
            method = name_or_method
        else:
            method = self.get_value(name_or_method)
        return inspect.getsource(method)

    def get_arg_spec(self, name_or_method):
        if inspect.ismethod(name_or_method):
            method = name_or_method
        else:
            method = self.get_value(name_or_method)
        return inspect.getargspec(method)

    def get_module(self):
        return inspect.getmodule(self.module_obj)

    def get_source_file(self):
        return inspect.getsourcefile(self.module_obj)

    def __str__(self):
        return pformat(self.__dict__)

    def __repr__(self):
        return str(self)

    @classmethod
    def get_parsed_module(cls, module_or_path):
        module_name = None
        module_obj = None

        is_path = type(module_or_path) in (str, unicode)
        if inspect.ismodule(module_or_path) or is_path:
            if is_path:
                module_name = os.path.splitext(
                    os.path.basename(module_or_path)
                )[0]
                module_or_path = imp.load_source(
                    module_name,
                    module_or_path
                )

            module_obj = inspect.getmodule(module_or_path)
            module_name = module_obj.__name__
        else:
            raise NotImplementedError

        def filter_private_members(members):
            return [m for m in members
                    if cls.PROTECTED_PREFIX not in m[0] or
                    cls.PRIVATE_PREFIX not in m[0]]

        methods = inspect.getmembers(module_obj, inspect.ismethod)
        methods = filter_private_members(methods)
        fields = inspect.getmembers(
            module_obj,
            lambda o: not inspect.isroutine(o)
        )
        fields = filter_private_members(fields)

        return ParsedModule(module_name, module_obj, dict(fields), dict(methods))


class ParsedClass(object):
    PROTECTED_PREFIX = '_'
    PRIVATE_PREFIX = '__'

    def __init__(self, name, class_obj, fields, methods):
        self.name = name
        self.class_obj = class_obj
        self.fields = fields
        self.methods = methods

    def get_value(self, name):
        return self.fields.get(name) or self.methods.get(name)

    def get_code(self, name_or_method):
        if inspect.ismethod(name_or_method):
            method = name_or_method
        else:
            method = self.get_value(name_or_method)
        return inspect.getsource(method)

    def get_arg_spec(self, name_or_method):
        if inspect.ismethod(name_or_method):
            method = name_or_method
        else:
            method = self.get_value(name_or_method)
        return inspect.getargspec(method)

    def get_module(self):
        return inspect.getmodule(self.class_obj)

    def get_source_file(self):
        return inspect.getsourcefile(self.class_obj)

    def __str__(self):
        return pformat(self.__dict__)

    def __repr__(self):
        return str(self)

    @classmethod
    def get_parsed_classes(cls, module_or_class_or_path):
        is_path = type(module_or_class_or_path) in (str, unicode)
        if inspect.ismodule(module_or_class_or_path) or is_path:
            if is_path:
                module_name = os.path.splitext(
                    os.path.basename(module_or_class_or_path)
                )[0]
                module_or_class_or_path = imp.load_source(
                    module_name,
                    module_or_class_or_path
                )

            cur_module = inspect.getmodule(module_or_class_or_path)
            classes = inspect.getmembers(
                module_or_class_or_path,
                lambda o: inspect.isclass(o) and inspect.getmodule(o) == cur_module
            )
        elif inspect.isclass(module_or_class_or_path):
            classes = [(module_or_class_or_path.__name__,
                        module_or_class_or_path)]
        else:
            raise NotImplementedError

        def filter_private_members(members):
            return [m for m in members
                    if cls.PROTECTED_PREFIX not in m[0] or
                    cls.PRIVATE_PREFIX not in m[0]]

        parsed_classes = []
        for class_name, _class in classes:
            methods = inspect.getmembers(_class, inspect.ismethod)
            methods = filter_private_members(methods)
            fields = inspect.getmembers(
                _class,
                lambda o: not inspect.isroutine(o)
            )
            fields = filter_private_members(fields)
            parsed_classes.append(ParsedClass(class_name,
                                              _class,
                                              dict(fields),
                                              dict(methods)))

        return parsed_classes


class ParsedBrowserClass(ParsedClass):
    __LOCATOR_NAME = 'element'
    __GOOD_METHODS = ('switch_to_default_content',
                      'get_title',
                      'get_text',
                      'get_attribute',
                      'get_current_url')
    # NOTE: methods which are wrapped(ex. 'stale_exception_wrapper') should be added to __GOOD_METHODS
    # otherwise they won't be added to ParsedClass object

    @classmethod
    def get_parsed_classes(cls, module_or_class_or_path=None):
        parsed_classes = ParsedClass.get_parsed_classes(Browser)
        for _class in parsed_classes:
            _class.methods = dict(
                [(n, v) for n, v in _class.methods.items()
                 if cls.__LOCATOR_NAME in _class.get_arg_spec(n).args or n in cls.__GOOD_METHODS]
            )
        return parsed_classes


class ParsedMouseClass(ParsedClass):
    __LOCATOR_NAME = 'element'

    @classmethod
    def get_parsed_classes(cls, module_or_class_or_path=None):
        parsed_classes = ParsedClass.get_parsed_classes(Mouse)
        for _class in parsed_classes:
            _class.methods = dict(
                [(n, v) for n, v in _class.methods.items()
                 if cls.__LOCATOR_NAME in _class.get_arg_spec(n).args]
            )
        return parsed_classes


class ParsedPageObjectClass(ParsedClass):
    @classmethod
    def get_parsed_classes(cls, module_or_class_or_path):
        parsed_classes = ParsedClass.get_parsed_classes(module_or_class_or_path)
        super_class = ParsedClass.get_parsed_classes(TestCase)[0]

        def filter_class_data(class1, class2, methods_or_fields):
            return dict([(n, v) for n, v in getattr(class1, methods_or_fields).items()
                         if n not in getattr(class2, methods_or_fields)])

        for _class in parsed_classes:
            _class.methods = filter_class_data(_class, super_class, 'methods')
            _class.fields = filter_class_data(_class, super_class, 'fields')

        return parsed_classes
