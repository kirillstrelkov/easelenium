import os
import re
import sys
import logging

from random import choice
from datetime import datetime


def unicode_str(string):
    return u"%s" % string


LINESEP = unicode_str(os.linesep)


def get_match(regexp, string, single_match=True):
    found = re.findall(regexp, string)
    if len(found) > 0:
        return found[0] if single_match else found
    else:
        return None


def is_python2():
    return sys.version_info.major == 2


def is_windows():
    return sys.platform.startswith("win")


def get_timestamp():
    timetuple = datetime.now().timetuple()
    timestamp = "%d%02d%02d%02d%02d%02d" % timetuple[:6]
    return timestamp


def is_string(obj):
    return type(obj) in ((str, unicode) if is_python2() else (str,))


def get_random_value(_list, *val_to_skip):
    _tmp = list(_list)
    for skipped in val_to_skip:
        _tmp.remove(skipped)
    value = choice(_tmp)
    return value


class Logger(object):
    def __init__(self, name=None, log_to_console=True, file_path=None, handler=None):
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(logging.INFO)

        if log_to_console:
            h = logging.StreamHandler(sys.stdout)
            self.__logger.addHandler(h)

        if file_path:
            h = logging.FileHandler(file_path, encoding="utf8")
            self.__logger.addHandler(h)

        if handler:
            self.__logger.addHandler(handler)

    def info(self, msg, *args, **kwargs):
        self.__logger.info(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self.__logger.warn(msg, *args, **kwargs)


def get_class_name_from_file(path):
    filename, _ = os.path.splitext(os.path.basename(path))
    return "".join([w.capitalize() for w in filename.split(u"_")])


def get_py_file_name_from_class_name(class_name):
    words = re.findall("[A-Z]*[a-z0-9]*", class_name)
    words = [w for w in words if len(w) > 0]
    return "_".join(words).lower() + ".py"
