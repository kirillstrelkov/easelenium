import logging
import os
import re
import sys
from datetime import datetime
from random import choice

from loguru import logger

LINESEP = os.linesep


def get_match(regexp, string, single_match=True):
    found = re.findall(regexp, string)
    if len(found) > 0:
        return found[0] if single_match else found
    else:
        return None


def is_windows():
    return sys.platform.startswith("win")


def get_timestamp():
    timetuple = datetime.now().timetuple()
    timestamp = "%d%02d%02d%02d%02d%02d" % timetuple[:6]
    return timestamp


def is_string(obj):
    return type(obj) == str


def get_random_value(_list, *val_to_skip):
    _tmp = list(_list)
    for skipped in val_to_skip:
        _tmp.remove(skipped)
    value = choice(_tmp)
    return value


class Logger:
    def __init__(
        self,
        name=None,
        log_to_console=True,
        file_path=None,
        handler=None,
        level=logging.INFO,
    ):
        self.__logger = logger

        if log_to_console:
            self.__logger.add(sys.stdout, filter=name, level=level)

        if file_path:
            self.__logger.add(file_path, filter=name, level=level)

        if handler:
            self.__logger.add(handler, filter=name, level=level)

    def debug(self, msg, *args, **kwargs):
        self.__logger.info(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.__logger.info(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self.__logger.warning(msg, *args, **kwargs)


def get_class_name_from_file(path):
    filename, _ = os.path.splitext(os.path.basename(path))
    return "".join([w.capitalize() for w in filename.split("_")])


def get_py_file_name_from_class_name(class_name):
    words = re.findall("[A-Z]*[a-z0-9]*", class_name)
    words = [w for w in words if len(w) > 0]
    return "_".join(words).lower() + ".py"
