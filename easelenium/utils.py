import logging
import os
import re
import sys
import traceback
from datetime import datetime
from functools import wraps
from random import choice

from selenium import webdriver
from easelenium.browser import Browser


def get_browser(name="gc", headless=True):
    BROWSER_NAME = name

    if name == "gc":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("window-size=1366,768")
        options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2}
        )
    else:
        options = None
    return Browser(BROWSER_NAME, options=options)


def browser_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        browser = None
        return_value = None
        try:
            browser = get_browser()

            kwargs["browser"] = browser
            value = func(*args, **kwargs)
            return_value = value
        except:
            try:
                if browser:
                    browser.save_screenshot()
            except:
                pass
            traceback.print_exc()
        finally:
            if browser:
                browser.quit()

        return return_value

    return wrapper


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
