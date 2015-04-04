from easyselenium.browser import Browser
import imp
import inspect
import os
from pprint import pformat


class ParsedClass(object):
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

    def get_args(self, name_or_method):
        if inspect.ismethod(name_or_method):
            method = name_or_method
        else:
            method = self.get_value(name_or_method)
        arg_spec = inspect.getargspec(method)
        if arg_spec:
            return arg_spec.args
        else:
            return []

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
            return [m for m in members if '__' not in m[0]]

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

    @classmethod
    def get_parsed_classes(cls, module_or_class_or_path=None):
        parsed_classes = ParsedClass.get_parsed_classes(Browser)
        for _class in parsed_classes:
            _class.methods = dict(
                [(n, v) for n, v in _class.methods.items()
                 if cls.__LOCATOR_NAME in _class.get_args(n)]
            )
        return parsed_classes
